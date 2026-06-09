"""
慢查询采集模块
从 sys.dm_exec_query_stats 和 sys.dm_exec_sql_text 采集 TOP 20 慢查询。
"""

import hashlib
import logging
from typing import Any, Dict

import pymssql

logger = logging.getLogger(__name__)


class SlowQueryCollector:
    """SQL Server 慢查询采集器

    采集执行计划缓存中按总耗时排序的 TOP 20 慢查询语句。
    """

    def collect_slow_queries(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集 TOP 20 慢查询

        从 sys.dm_exec_query_stats 获取查询统计信息，
        通过 sys.dm_exec_sql_text 获取查询文本，
        按总耗时 DESC 排序取前 20 条。

        Args:
            connection: pymssql 数据库连接

        Returns:
            dict: {"slow_queries": [dict, ...], "error": ""}
        """
        result: Dict[str, Any] = {"slow_queries": [], "error": ""}
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT TOP 20
                    qt.text                                          AS sql_text,
                    qs.execution_count                               AS execution_count,
                    qs.total_worker_time / 1000.0                    AS total_cpu_ms,
                    qs.total_logical_reads                           AS total_logical_reads,
                    qs.total_elapsed_time / 1000.0                   AS total_elapsed_ms,
                    qs.total_elapsed_time / 1000.0
                        / NULLIF(qs.execution_count, 0)              AS avg_elapsed_ms,
                    qs.last_execution_time                           AS last_execution_time
                FROM sys.dm_exec_query_stats qs
                CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
                ORDER BY qs.total_elapsed_time DESC
            """)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                # 计算 SQL 哈希值，用于后续聚合去重
                item["sql_hash"] = hashlib.md5(
                    (item["sql_text"] or "").encode("utf-8")
                ).hexdigest()
                # 将 datetime 转为 ISO 字符串便于序列化
                if item.get("last_execution_time"):
                    item["last_execution_time"] = (
                        item["last_execution_time"].isoformat()
                    )
                result["slow_queries"].append(item)
            cursor.close()
        except pymssql.Error as e:
            logger.error("Failed to collect slow queries: %s", e)
            result["error"] = str(e)
        except Exception as e:
            logger.error("Unexpected error collecting slow queries: %s", e)
            result["error"] = str(e)
        return result
