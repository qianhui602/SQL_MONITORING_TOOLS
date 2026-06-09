"""
阻塞/等待链采集模块
从 sys.dm_exec_requests 采集当前阻塞链信息。
"""

import logging
from typing import Any, Dict

import pymssql

logger = logging.getLogger(__name__)


class BlockingCollector:
    """SQL Server 阻塞链采集器

    采集当前实例中所有活跃的阻塞链关系，
    包括被阻塞和阻塞源会话的 SPID、等待类型、等待时间、SQL 文本等。
    """

    def collect_blocking(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集当前阻塞链

        通过 sys.dm_exec_requests 查找被阻塞的请求，
        同时通过子查询获取阻塞源的 SQL 文本。

        Args:
            connection: pymssql 数据库连接

        Returns:
            dict: {"blocking_chains": [dict, ...], "error": ""}
        """
        result: Dict[str, Any] = {"blocking_chains": [], "error": ""}
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    r.session_id                                     AS blocked_spid,
                    r.blocking_session_id                            AS blocking_spid,
                    r.wait_type                                      AS wait_type,
                    r.wait_time                                      AS wait_time_ms,
                    t1.text                                          AS blocked_sql,
                    (SELECT TOP 1 t.text
                     FROM sys.dm_exec_requests r2
                     CROSS APPLY sys.dm_exec_sql_text(r2.sql_handle) t
                     WHERE r2.session_id = r.blocking_session_id)    AS blocking_sql,
                    DB_NAME(r.database_id)                           AS blocked_db
                FROM sys.dm_exec_requests r
                CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t1
                WHERE r.blocking_session_id > 0
                ORDER BY r.wait_time DESC
            """)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                result["blocking_chains"].append(item)
            cursor.close()
        except pymssql.Error as e:
            logger.error("Failed to collect blocking chains: %s", e)
            result["error"] = str(e)
        except Exception as e:
            logger.error("Unexpected error collecting blocking chains: %s", e)
            result["error"] = str(e)
        return result
