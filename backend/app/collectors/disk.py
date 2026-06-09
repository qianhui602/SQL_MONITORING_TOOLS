import logging
from typing import Any, Dict, List

import pymssql

logger = logging.getLogger(__name__)


class DiskCollector:
    def collect_disk_space(self, connection: pymssql.Connection) -> Dict[str, Any]:
        result: Dict[str, Any] = {"disk_info": [], "error": ""}
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT
                    DB_NAME(mf.database_id) AS database_name,
                    SUM(CASE WHEN mf.type_desc = 'ROWS' THEN mf.size * 8 / 1024.0 ELSE 0 END) AS data_file_mb,
                    SUM(CASE WHEN mf.type_desc = 'LOG' THEN mf.size * 8 / 1024.0 ELSE 0 END) AS log_file_mb,
                    SUM(mf.size * 8 / 1024.0) AS total_mb,
                    SUM(CASE WHEN mf.type_desc = 'ROWS' THEN FILEPROPERTY(mf.name, 'SpaceUsed') * 8 / 1024.0 ELSE 0 END) AS used_mb
                FROM sys.master_files mf
                WHERE mf.database_id > 4
                GROUP BY mf.database_id
                ORDER BY total_mb DESC
            """)
            rows: List = cursor.fetchall()
            cursor.close()

            for row in rows:
                db_name = str(row[0]) if row[0] else "unknown"
                data_mb = float(row[1]) if row[1] else 0.0
                log_mb = float(row[2]) if row[2] else 0.0
                total_mb = float(row[3]) if row[3] else 0.0
                used_mb = float(row[4]) if row[4] else 0.0
                free_mb = total_mb - used_mb
                usage_pct = round((used_mb / total_mb * 100), 2) if total_mb > 0 else 0.0

                result["disk_info"].append({
                    "database_name": db_name,
                    "data_file_mb": round(data_mb, 2),
                    "log_file_mb": round(log_mb, 2),
                    "total_mb": round(total_mb, 2),
                    "used_mb": round(used_mb, 2),
                    "free_mb": round(free_mb, 2),
                    "usage_pct": usage_pct,
                })
        except pymssql.Error as e:
            logger.error("Failed to collect disk space metrics: %s", e)
            result["error"] = str(e)
        return result
