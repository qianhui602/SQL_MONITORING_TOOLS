"""
SQL Server 死锁检测模块
使用扩展事件 (system_health) 检测和解析死锁事件
"""

import logging
from typing import Any, Dict, List

import pymssql

logger = logging.getLogger(__name__)


class DeadlockDetector:
    """SQL Server 死锁检测器

    通过 system_health 扩展事件会话检测死锁事件，
    并解析死锁 XML 提取关键信息。
    """

    def check_deadlocks(self, connection: pymssql.Connection) -> List[Dict[str, Any]]:
        """从 system_health 会话中读取死锁事件

        Args:
            connection: pymssql 数据库连接

        Returns:
            list[dict]: 原始死锁事件列表，每个包含 occur_at 和 deadlock_xml
        """
        results: List[Dict[str, Any]] = []
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    xed.value('@timestamp', 'datetime2') AS occur_at,
                    xed.query('.') AS deadlock_xml
                FROM
                (
                    SELECT CAST(st.target_data AS XML) AS target_data
                    FROM sys.dm_xe_session_targets st
                    JOIN sys.dm_xe_sessions s
                        ON s.address = st.event_session_address
                    WHERE s.name = 'system_health'
                      AND st.target_name = 'ring_buffer'
                ) AS data
                CROSS APPLY target_data.nodes('/RingBufferTarget/event[@name="xml_deadlock_report"]') AS xe(xed);
            """)
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                results.append({
                    "occur_at": row[0],
                    "deadlock_xml": row[1],
                })
            if results:
                logger.info("Detected %d deadlock event(s) from system_health", len(results))
        except pymssql.Error as e:
            logger.error("Failed to check deadlocks from system_health: %s", e)
        return results

    def parse_deadlock_xml(self, xml_str: str) -> Dict[str, Any]:
        """解析死锁 XML，提取关键信息

        Args:
            xml_str: 死锁事件的 XML 字符串

        Returns:
            dict: 解析后的死锁信息，包含：
                - victim_session_id: 受害会话ID
                - processes: 参与死锁的进程列表
                - sql_statements: 每个进程对应的 SQL 语句列表
                - involved_objects: 涉及的对象（表/索引）
        """
        import xml.etree.ElementTree as ET

        result: Dict[str, Any] = {
            "victim_session_id": None,
            "processes": [],
            "sql_statements": [],
            "involved_objects": [],
        }

        try:
            root = ET.fromstring(xml_str)

            # 使用命名空间处理或直接搜索
            namespace = ""
            deadlock_element = root.find(".//deadlock")
            if deadlock_element is None:
                deadlock_element = root.find(".//{http://schemas.microsoft.com/sqlserver}deadlock")
                if deadlock_element is not None:
                    namespace = "{http://schemas.microsoft.com/sqlserver}"

            if deadlock_element is None:
                # 尝试直接在根元素下找
                for child in root.iter():
                    if "deadlock" in child.tag:
                        deadlock_element = child
                        break

            if deadlock_element is None:
                logger.warning("Could not find deadlock element in XML")
                return result

            # 先处理 process-list，建立 id → spid 映射
            process_id_to_spid = {}
            process_list = deadlock_element.find(f"{namespace}process-list")
            if process_list is not None:
                for process in process_list.findall(f"{namespace}process"):
                    proc_info: Dict[str, Any] = {
                        "session_id": None,
                        "transaction_name": None,
                        "isolation_level": None,
                    }
                    proc_id = process.get("id", "")
                    spid = process.get("spid")
                    if spid is not None:
                        proc_info["session_id"] = int(spid)
                    else:
                        proc_info["session_id"] = self._parse_process_id(proc_id)
                    if proc_id:
                        process_id_to_spid[proc_id] = proc_info["session_id"]
                    proc_info["transaction_name"] = process.get("transactionname")
                    proc_info["isolation_level"] = process.get("isolationlevel")
                    result["processes"].append(proc_info)

                    # 提取 SQL 语句
                    inputbuf = process.find(f"{namespace}inputbuf")
                    if inputbuf is not None and inputbuf.text:
                        result["sql_statements"].append(inputbuf.text.strip())

            # 处理 victim-list（用进程地址映射查找实际 session_id）
            victim_list = deadlock_element.find(f"{namespace}victim-list")
            if victim_list is not None:
                victim_process = victim_list.find(f"{namespace}victimProcess")
                if victim_process is not None:
                    victim_id = victim_process.get("id", "")
                    if victim_id in process_id_to_spid:
                        result["victim_session_id"] = process_id_to_spid[victim_id]
                    else:
                        spid = victim_process.get("spid")
                        if spid is not None:
                            result["victim_session_id"] = int(spid)
                        else:
                            result["victim_session_id"] = self._parse_process_id(victim_id)

            # 处理 resource-list 提取涉及的对象
            resource_list = deadlock_element.find(f"{namespace}resource-list")
            if resource_list is not None:
                for resource in resource_list:
                    obj_name = None
                    if resource.tag.endswith("objectlock") or "objectlock" in resource.tag:
                        obj_name = resource.get("objectname")
                    elif resource.tag.endswith("pagelock") or "pagelock" in resource.tag:
                        obj_name = resource.get("objectname")
                    elif resource.tag.endswith("keylock") or "keylock" in resource.tag:
                        obj_name = resource.get("objectname")
                    elif resource.tag.endswith("ridlock") or "ridlock" in resource.tag:
                        obj_name = resource.get("objectname")
                    if obj_name and obj_name not in result["involved_objects"]:
                        result["involved_objects"].append(obj_name)

        except ET.ParseError as e:
            logger.error("Failed to parse deadlock XML: %s", e)

        return result

    @staticmethod
    def _parse_process_id(raw_id: str):
        """解析死锁XML中的进程ID（可能是十进制或十六进制格式）

        SQL Server 2019 的 system_health 会话中进程ID格式为 process1ca4bbfa4e8，
        其中 1ca4bbfa4e8 是十六进制表示的 session_id。
        """
        if not raw_id:
            return None
        stripped = raw_id.replace("process", "", 1) if raw_id.startswith("process") else raw_id
        try:
            return int(stripped)
        except ValueError:
            try:
                return int(stripped, 16)
            except ValueError:
                logger.warning("Could not parse process ID: %r", raw_id)
                return None

    def detect(self, connection: pymssql.Connection) -> List[Dict[str, Any]]:
        """整合检查与解析，返回解析后的死锁事件列表

        Args:
            connection: pymssql 数据库连接

        Returns:
            list[dict]: 解析后的死锁事件列表，每个包含：
                - occur_at: 发生时间
                - deadlock_xml: 原始 XML
                - parsed: 解析后的死锁详细信息
        """
        raw_events = self.check_deadlocks(connection)
        parsed_events: List[Dict[str, Any]] = []
        for event in raw_events:
            xml_str = str(event["deadlock_xml"])
            parsed = self.parse_deadlock_xml(xml_str)
            parsed_events.append({
                "occur_at": event["occur_at"],
                "deadlock_xml": xml_str,
                "parsed": parsed,
            })
        return parsed_events
