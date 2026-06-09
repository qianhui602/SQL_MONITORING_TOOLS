"""
索引分析采集模块
从 SQL Server 采集缺失索引建议和索引碎片信息。
"""

import logging
from typing import Any, Dict, List

import pymssql

logger = logging.getLogger(__name__)


class IndexAnalyzer:
    """SQL Server 索引分析器

    从目标 SQL Server 实例采集缺失索引建议和索引碎片信息，
    每个采集方法独立，单个失败不影响其他指标采集。
    """

    def collect_missing_indexes(
        self, connection: pymssql.Connection
    ) -> List[Dict[str, Any]]:
        """从 sys.dm_db_missing_index_* 采集缺失索引建议

        Args:
            connection: pymssql 数据库连接

        Returns:
            list: 缺失索引建议列表
        """
        results: List[Dict[str, Any]] = []
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    DB_NAME(mid.database_id) AS database_name,
                    SCHEMA_NAME(o.schema_id) AS schema_name,
                    OBJECT_NAME(mid.object_id) AS table_name,
                    mid.equality_columns,
                    mid.inequality_columns,
                    mid.included_columns,
                    migs.avg_user_impact,
                    migs.user_seeks,
                    migs.user_scans
                FROM sys.dm_db_missing_index_details AS mid
                INNER JOIN sys.dm_db_missing_index_groups AS mig
                    ON mid.index_handle = mig.index_handle
                INNER JOIN sys.dm_db_missing_index_group_stats AS migs
                    ON mig.index_group_handle = migs.group_handle
                INNER JOIN sys.objects AS o
                    ON mid.object_id = o.object_id
                WHERE mid.database_id = DB_ID()
                ORDER BY migs.avg_user_impact DESC;
            """)
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                results.append({
                    "database_name": row[0],
                    "schema_name": row[1],
                    "table_name": row[2],
                    "equality_columns": row[3],
                    "inequality_columns": row[4],
                    "included_columns": row[5],
                    "avg_user_impact": float(row[6]) if row[6] is not None else 0.0,
                    "user_seeks": int(row[7]) if row[7] is not None else 0,
                    "user_scans": int(row[8]) if row[8] is not None else 0,
                })
        except pymssql.Error as e:
            logger.error("Failed to collect missing indexes: %s", e)
        return results

    def collect_fragmented_indexes(
        self, connection: pymssql.Connection
    ) -> List[Dict[str, Any]]:
        """从 sys.dm_db_index_physical_stats 采集索引碎片信息

        Args:
            connection: pymssql 数据库连接

        Returns:
            list: 碎片索引列表
        """
        results: List[Dict[str, Any]] = []
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    DB_NAME(ips.database_id) AS database_name,
                    SCHEMA_NAME(o.schema_id) AS schema_name,
                    OBJECT_NAME(ips.object_id) AS table_name,
                    i.name AS index_name,
                    ips.avg_fragmentation_in_percent,
                    ips.page_count,
                    CASE i.type_desc
                        WHEN 'CLUSTERED' THEN 'CLUSTERED'
                        ELSE 'NONCLUSTERED'
                    END AS index_type
                FROM sys.dm_db_index_physical_stats(
                    DB_ID(), NULL, NULL, NULL, 'LIMITED'
                ) AS ips
                INNER JOIN sys.indexes AS i
                    ON ips.object_id = i.object_id
                    AND ips.index_id = i.index_id
                INNER JOIN sys.objects AS o
                    ON ips.object_id = o.object_id
                WHERE ips.avg_fragmentation_in_percent > 5
                  AND ips.page_count > 100
                  AND o.is_ms_shipped = 0
                ORDER BY ips.avg_fragmentation_in_percent DESC;
            """)
            rows = cursor.fetchall()
            cursor.close()
            for row in rows:
                results.append({
                    "database_name": row[0],
                    "schema_name": row[1],
                    "table_name": row[2],
                    "index_name": row[3],
                    "avg_fragmentation_pct": float(row[4]) if row[4] is not None else 0.0,
                    "page_count": int(row[5]) if row[5] is not None else 0,
                    "index_type": row[6],
                })
        except pymssql.Error as e:
            logger.error("Failed to collect fragmented indexes: %s", e)
        return results

    def collect_all(
        self, connection: pymssql.Connection
    ) -> Dict[str, Any]:
        """采集所有索引分析数据

        Args:
            connection: pymssql 数据库连接

        Returns:
            dict: 包含 missing_indexes 和 fragmented_indexes 的汇总字典
        """
        result: Dict[str, Any] = {
            "missing_indexes": [],
            "fragmented_indexes": [],
            "error": "",
        }
        try:
            result["missing_indexes"] = self.collect_missing_indexes(connection)
        except Exception as e:
            logger.error("Error collecting missing indexes: %s", e)
            result["error"] += f"missing_indexes: {e}; "

        try:
            result["fragmented_indexes"] = self.collect_fragmented_indexes(connection)
        except Exception as e:
            logger.error("Error collecting fragmented indexes: %s", e)
            result["error"] += f"fragmented_indexes: {e}; "

        return result
