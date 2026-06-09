"""
SQL Server 性能指标采集模块
采集 CPU、内存、连接、I/O、OS 内存、锁等待、批处理请求等性能指标
"""

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict

import pymssql

logger = logging.getLogger(__name__)


def _handle_collection_error(metric_name: str):
    """采集方法错误处理装饰器

    统一处理 pymssql 异常和错误日志，
    消除各个采集方法中重复的 try-catch 代码。

    Args:
        metric_name: 指标名称，用于错误日志
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, connection: pymssql.Connection) -> Dict[str, Any]:
            try:
                return func(self, connection)
            except pymssql.Error as e:
                logger.error("Failed to collect %s metrics: %s", metric_name, e)
                return {"error": str(e)}
        return wrapper
    return decorator


class PerformanceCollector:
    """SQL Server 性能指标采集器

    从目标 SQL Server 实例采集各项性能指标。
    每个采集方法独立，单个失败不影响其他指标采集。
    """

    @contextmanager
    def _cursor_context(self, connection: pymssql.Connection):
        """游标上下文管理器，确保游标正确关闭

        消除游标泄漏风险，简化游标创建和关闭的样板代码。

        Args:
            connection: pymssql 数据库连接
        """
        cursor = None
        try:
            cursor = connection.cursor()
            yield cursor
        finally:
            if cursor is not None:
                cursor.close()

    @_handle_collection_error("CPU")
    def collect_cpu(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集 CPU 使用率"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT 
                    cpu_count,
                    hyperthread_ratio,
                    (SELECT TOP 1 
                        CAST(record AS XML).value('(Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int')
                     FROM sys.dm_os_ring_buffers 
                     WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
                     ORDER BY timestamp DESC) AS process_utilization
                FROM sys.dm_os_sys_info;
            """)
            row = cursor.fetchone()
            if row and row[2] is not None:
                return {"cpu_usage": row[2], "sql_cpu": row[2]}

        # 回退查询：当 ring_buffer 不可用时
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT cntr_value 
                FROM sys.dm_os_performance_counters 
                WHERE object_name LIKE '%SQLServer:SQL Statistics%' 
                  AND counter_name = 'SQL Compilations/sec';
            """)
            row = cursor.fetchone()
            if row:
                return {"cpu_usage": 0, "sql_cpu": row[0]}

        return {}

    @_handle_collection_error("memory")
    def collect_memory(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集内存使用量"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT
                    (SELECT cntr_value/1024
                     FROM sys.dm_os_performance_counters
                     WHERE counter_name = 'Total Server Memory (KB)') AS sql_server_memory_mb,
                    (SELECT CAST(cntr_value * 1.0 / NULLIF(
                        (SELECT cntr_value
                         FROM sys.dm_os_performance_counters
                         WHERE counter_name = 'Buffer cache hit ratio base'
                           AND object_name LIKE '%Buffer Manager%'), 0) * 100 AS DECIMAL(5,2))
                     FROM sys.dm_os_performance_counters
                     WHERE counter_name = 'Buffer cache hit ratio'
                       AND object_name LIKE '%Buffer Manager%') AS buffer_cache_hit_ratio,
                    (SELECT cntr_value/1024
                     FROM sys.dm_os_performance_counters
                     WHERE counter_name = 'Target Server Memory (KB)') AS target_memory_mb,
                    (SELECT cntr_value
                     FROM sys.dm_os_performance_counters
                     WHERE counter_name = 'Page life expectancy'
                       AND object_name LIKE '%Buffer Manager%') AS page_life_expectancy;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "sql_server_memory_mb": row[0],
                    "buffer_cache_hit_ratio": row[1],
                    "target_memory_mb": row[2],
                    "page_life_expectancy": row[3],
                }
        return {}

    @_handle_collection_error("connection")
    def collect_connections(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集连接信息"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM sys.dm_exec_connections) AS total_connections,
                    (SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE status = 'running') AS active_sessions,
                    (SELECT cntr_value
                     FROM sys.dm_os_performance_counters
                     WHERE counter_name = 'User Connections') AS user_connections,
                    (SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE is_user_process = 1) AS user_processes;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "total_connections": row[0],
                    "active_sessions": row[1],
                    "user_connections": row[2],
                    "user_processes": row[3],
                }
        return {}

    @_handle_collection_error("IO")
    def collect_io(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集 I/O 指标"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT 
                    AVG(io_stall_read_ms) AS avg_read_latency_ms,
                    AVG(io_stall_write_ms) AS avg_write_latency_ms,
                    SUM(num_of_reads) AS total_reads,
                    SUM(num_of_writes) AS total_writes,
                    SUM(num_of_bytes_read / 1024.0 / 1024.0) AS read_mb,
                    SUM(num_of_bytes_written / 1024.0 / 1024.0) AS write_mb
                FROM sys.dm_io_virtual_file_stats(NULL, NULL);
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "avg_read_latency_ms": row[0],
                    "avg_write_latency_ms": row[1],
                    "total_reads": row[2],
                    "total_writes": row[3],
                    "read_mb": row[4],
                    "write_mb": row[5],
                }
        return {}

    @_handle_collection_error("OS memory")
    def collect_os_memory(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集 OS 内存"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT
                    total_physical_memory_kb/1024/1024 AS total_physical_memory_gb,
                    available_physical_memory_kb/1024/1024 AS available_physical_memory_gb,
                    (total_physical_memory_kb - available_physical_memory_kb) * 100.0 / total_physical_memory_kb AS memory_usage_pct
                FROM sys.dm_os_sys_info
                CROSS JOIN sys.dm_os_sys_memory;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "total_physical_memory_gb": row[0],
                    "available_physical_memory_gb": row[1],
                    "memory_usage_pct": row[2],
                }
        return {}

    @_handle_collection_error("lock")
    def collect_locks(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集锁等待指标"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM sys.dm_tran_locks WHERE request_status = 'WAIT') AS waiting_locks,
                    (SELECT COUNT(*) FROM sys.dm_os_waiting_tasks WHERE wait_type LIKE 'LCK%') AS lock_waits,
                    (SELECT AVG(wait_duration_ms) FROM sys.dm_os_waiting_tasks WHERE wait_type LIKE 'LCK%') AS avg_lock_wait_ms;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "waiting_locks": row[0],
                    "lock_waits": row[1],
                    "avg_lock_wait_ms": row[2] if row[2] is not None else 0,
                }
        return {}

    @_handle_collection_error("batch request")
    def collect_batch_requests(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """采集批处理请求和编译指标"""
        with self._cursor_context(connection) as cursor:
            cursor.execute("""
                SELECT
                    (SELECT cntr_value 
                     FROM sys.dm_os_performance_counters 
                     WHERE counter_name = 'Batch Requests/sec'
                       AND object_name LIKE '%SQL Statistics%') AS batch_requests_sec,
                    (SELECT cntr_value 
                     FROM sys.dm_os_performance_counters 
                     WHERE counter_name = 'SQL Compilations/sec'
                       AND object_name LIKE '%SQL Statistics%') AS sql_compilations_sec,
                    (SELECT cntr_value 
                     FROM sys.dm_os_performance_counters 
                     WHERE counter_name = 'SQL Re-Compilations/sec'
                       AND object_name LIKE '%SQL Statistics%') AS sql_recompilations_sec;
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "batch_requests_sec": row[0],
                    "sql_compilations_sec": row[1],
                    "sql_recompilations_sec": row[2],
                }
        return {}

    def collect_all(self, connection: pymssql.Connection) -> Dict[str, Any]:
        """调用所有采集方法，返回汇总字典

        单个指标采集失败不影响其他指标。

        Args:
            connection: pymssql 数据库连接

        Returns:
            dict: 包含所有采集指标的汇总字典
        """
        metrics: Dict[str, Any] = {
            "cpu": self.collect_cpu(connection),
            "memory": self.collect_memory(connection),
            "connections": self.collect_connections(connection),
            "io": self.collect_io(connection),
            "os_memory": self.collect_os_memory(connection),
            "locks": self.collect_locks(connection),
            "batch_requests": self.collect_batch_requests(connection),
        }
        return metrics
