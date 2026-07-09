"""
APScheduler 定时任务管理
负责定时采集 SQL Server 指标并写入 PostgreSQL
支持单实例（兼容旧模式）和多实例模式。
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.collector import MetricsCollector
from app.collectors.sqlserver import MSSQLConnectionManager
from app.config import Settings
from app.database import async_session_factory
from app.models.instance import MonitoredInstance
from app.models.slow_query import SlowQueryRecord
from app.services.alert_service import AlertEngine
from app.services.cache import cache_configs, get_cached_configs, cache_instances, get_cached_instances

logger = logging.getLogger(__name__)

_CONFIG_KEY_MAP = {
    "mssql_host": "MSSQL_HOST",
    "mssql_port": "MSSQL_PORT",
    "mssql_user": "MSSQL_USER",
    "mssql_password": "MSSQL_PASSWORD",
    "mssql_database": "MSSQL_DATABASE",
    "scheduler_interval_seconds": "SCHEDULER_INTERVAL_SECONDS",
}


# ---------------------------------------------------------------------------
# 通用批量存储工具
# ---------------------------------------------------------------------------

def batch_store_handler(table_name: str):
    """批量数据存储的异常处理装饰器

    统一处理批量数据存储的异常处理和日志记录，
    消除各个存储方法中重复的 try-catch 代码。

    Args:
        table_name: 表名，用于错误日志
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            self, session, data_list: list[Dict[str, Any]], server_address: str
        ) -> None:
            if not data_list:
                return

            now = datetime.now(timezone.utc)
            success_count = 0
            error_count = 0

            for item in data_list:
                try:
                    await func(self, session, item, server_address, now)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    logger.warning("Failed to store %s record: %s", table_name, e)

            if error_count > 0:
                logger.info(
                    "Stored %s: %d success, %d failed",
                    table_name, success_count, error_count
                )
        return wrapper
    return decorator


def build_field_params(
    data: Dict[str, Any],
    field_map: Dict[str, Tuple[str, Any]],
    extra_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """根据字段映射构建参数字典

    Args:
        data: 原始数据字典
        field_map: 字段映射配置 {source_field: (db_field, default_value)}
        extra_params: 额外的参数（如时间戳、服务器地址等）

    Returns:
        构建好的参数字典
    """
    params = extra_params.copy() if extra_params else {}
    for source_field, (db_field, default_value) in field_map.items():
        params[db_field] = data.get(source_field, default_value)
    return params


# 字段映射配置
SLOW_QUERY_FIELD_MAP: Dict[str, Tuple[str, Any]] = {
    "sql_hash": ("sql_hash", ""),
    "sql_text": ("sql_text", ""),
    "execution_count": ("execution_count", 0),
    "total_cpu_ms": ("total_cpu_ms", 0.0),
    "total_logical_reads": ("total_logical_reads", 0),
    "total_elapsed_ms": ("total_elapsed_ms", 0.0),
    "avg_elapsed_ms": ("avg_elapsed_ms", 0.0),
}

DISK_SPACE_FIELD_MAP: Dict[str, Tuple[str, Any]] = {
    "database_name": ("database_name", ""),
    "data_file_mb": ("data_file_mb", 0.0),
    "log_file_mb": ("log_file_mb", 0.0),
    "total_mb": ("total_mb", 0.0),
    "used_mb": ("used_mb", 0.0),
    "free_mb": ("free_mb", 0.0),
    "usage_pct": ("usage_pct", 0.0),
}

BLOCKING_EVENT_FIELD_MAP: Dict[str, Tuple[str, Any]] = {
    "blocked_spid": ("blocked_spid", 0),
    "blocking_spid": ("blocking_spid", 0),
    "wait_type": ("wait_type", ""),
    "wait_time_ms": ("wait_time_ms", 0),
    "blocked_sql": ("blocked_sql", None),
    "blocking_sql": ("blocking_sql", None),
    "blocked_db": ("blocked_db", None),
}


class SchedulerManager:
    """APScheduler 调度器管理器"""

    def __init__(self) -> None:
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._collector: Optional[MetricsCollector] = None
        self._alert_engine: Optional[AlertEngine] = None

    def setup(self, app, settings: Settings) -> None:
        """配置调度器"""
        self.scheduler = AsyncIOScheduler()
        self._alert_engine = AlertEngine(db_session_factory=async_session_factory)

        interval = settings.SCHEDULER_INTERVAL_SECONDS
        self.add_collect_job(interval_seconds=interval)
        # 添加数据清理定时任务（每天凌晨 3 点执行）
        self.add_cleanup_job()
        logger.info("Scheduler configured with interval=%ds", interval)

    def add_collect_job(self, interval_seconds: int = 60) -> None:
        """添加定时采集任务"""
        if self.scheduler is None:
            raise RuntimeError("Scheduler not initialized. Call setup() first.")

        self.scheduler.add_job(
            func=self._collect_and_store,
            trigger="interval",
            seconds=interval_seconds,
            id="collect_metrics",
            name="Collect SQL Server metrics",
            replace_existing=True,
            misfire_grace_time=30,
            max_instances=1,
            coalesce=True,
        )
        logger.info("Collect job added with interval=%ds", interval_seconds)

    async def _load_runtime_config(self) -> Optional[Dict[str, str]]:
        """从数据库加载运行时配置（SQL Server 连接信息等）"""
        cached = get_cached_configs()
        if cached:
            return cached
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    text(
                        "SELECT config_key, config_value FROM system_configs"
                    )
                )
                config = {}
                for row in result:
                    config[row[0]] = row[1]
                cache_configs(config)
                return config
        except Exception as e:
            logger.error("Failed to load runtime config: %s", e)
            return None

    def _apply_runtime_config(self, runtime_config: Dict[str, str]) -> None:
        """应用运行时配置到采集器（单实例兼容模式）"""
        if self._collector is None:
            host = runtime_config.get("mssql_host", "")
            port = int(runtime_config.get("mssql_port", 1433))
            user = runtime_config.get("mssql_user", "")
            password = runtime_config.get("mssql_password", "")
            database = runtime_config.get("mssql_database", "master")

            self._collector = MetricsCollector()
            self._collector.connection_manager = self._collector.connection_manager.__class__(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
            )
            logger.info(
                "Runtime config applied: SQL Server %s:%s user=%s db=%s",
                host, port, user, database,
            )

    async def _load_active_instances(self) -> List[MonitoredInstance]:
        """加载所有启用的监控实例"""
        cached = get_cached_instances()
        if cached:
            return cached
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(MonitoredInstance).where(
                        MonitoredInstance.is_active == True
                    ).order_by(MonitoredInstance.id)
                )
                instances = result.scalars().all()
                instances_list = list(instances)
                cache_instances(instances_list)
                logger.info("Loaded %d active monitored instance(s)", len(instances_list))
                return instances_list
        except Exception as e:
            logger.error("Failed to load active instances: %s", e)
            return []

    async def _collect_and_store(self) -> None:
        """采集任务：遍历所有活跃实例采集指标并写入 PostgreSQL，完成后执行告警检查"""
        logger.info("Starting metrics collection cycle")

        runtime_config = await self._load_runtime_config()
        if runtime_config is None:
            logger.error("Failed to load runtime config, skipping collection cycle")
            return

        # 判断是否启用多实例模式
        instances_enabled = runtime_config.get(
            "mssql_instances_enabled", "false"
        ).lower() == "true"

        if instances_enabled:
            await self._collect_multi_instance(runtime_config)
        else:
            await self._collect_single_instance(runtime_config)

    async def _collect_single_instance(self, runtime_config: Dict[str, str]) -> None:
        """单实例采集模式（向后兼容旧配置）"""
        self._apply_runtime_config(runtime_config)

        if self._collector is None:
            logger.error("MetricsCollector not initialized")
            return

        server_address = runtime_config.get("mssql_host", "unknown")
        connection_status_list: List[Dict[str, Any]] = []

        # 连接预检
        if self._collector.connection_manager:
            is_connected = self._collector.connection_manager.ping()
            if is_connected:
                conn_status = {
                    "server_address": server_address,
                    "is_connected": True,
                    "connection_error": None,
                    "previous_was_disconnected": False,
                    "last_connected_at": "无记录",
                }
                # 单实例模式无法跟踪前次状态，仅当采集失败时会触发 collection_interrupted
            else:
                logger.warning(
                    "Single-instance connection check failed for %s, skipping collection",
                    server_address,
                )
                conn_status = {
                    "server_address": server_address,
                    "is_connected": False,
                    "connection_error": f"Connection failed: {server_address}",
                    "previous_was_disconnected": False,
                    "last_connected_at": "无记录",
                }
                connection_status_list.append(conn_status)
                aggregated_data: Dict[str, Any] = {
                    "metrics": [],
                    "deadlocks": [],
                    "connection_status": connection_status_list,
                }
                await self._run_alert_checks(aggregated_data)
                return

        try:
            data = await asyncio.to_thread(self._collector.collect_all_metrics)
        except Exception as e:
            logger.error("Metrics collection failed: %s", e)
            return

        if not data.get("metrics") and not data.get("deadlocks") and not data.get("slow_queries"):
            logger.warning("No metrics, deadlocks, or slow queries collected")

        async with async_session_factory() as session:
            try:
                await self._store_metrics(session, data["metrics"], server_address)
                await self._store_deadlocks(session, data["deadlocks"], server_address)
                await self._store_slow_queries(session, data["slow_queries"], server_address)
                await self._store_disk_space(session, data["disk_space"], server_address)
                await self._store_blocking_events(session, data.get("blocking_events", []), server_address)
                await self._store_missing_indexes(session, data.get("missing_indexes", []), server_address)
                await self._store_index_fragmentation(session, data.get("fragmented_indexes", []), server_address)
                await session.commit()
                logger.info(
                    "Single-instance collection completed: %d metrics, %d deadlocks, %d slow queries, %d disk records, %d blocking events, %d missing indexes, %d fragmented indexes",
                    len(data["metrics"]),
                    len(data["deadlocks"]),
                    len(data["slow_queries"]),
                    len(data["disk_space"]),
                    len(data.get("blocking_events", [])),
                    len(data.get("missing_indexes", [])),
                    len(data.get("fragmented_indexes", [])),
                )
            except Exception as e:
                await session.rollback()
                logger.error("Failed to store collected data: %s", e)
                return

        data["connection_status"] = connection_status_list if connection_status_list else []
        await self._run_alert_checks(data)

    async def _update_instance_connection(
        self, instance: MonitoredInstance, is_connected: bool,
        server_address: str, error_message: Optional[str] = None,
    ) -> None:
        """更新实例连接状态到数据库"""
        now = datetime.now(timezone.utc)
        async with async_session_factory() as session:
            try:
                stmt = (
                    select(MonitoredInstance)
                    .where(MonitoredInstance.id == instance.id)
                )
                result = await session.execute(stmt)
                db_instance = result.scalar_one_or_none()
                if db_instance is None:
                    return

                db_instance.is_connected = is_connected
                if is_connected:
                    db_instance.last_connected_at = now
                    db_instance.connection_error = None
                else:
                    db_instance.last_disconnected_at = now
                    db_instance.connection_error = error_message
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.warning(
                    "Failed to update connection status for %s: %s",
                    server_address, e,
                )

    async def _collect_multi_instance(self, runtime_config: Dict[str, str]) -> None:
        """多实例采集模式：遍历所有活跃实例逐个采集"""
        instances = await self._load_active_instances()

        if not instances:
            logger.warning("No active instances found, skipping multi-instance collection")
            return

        all_metrics: List[Dict[str, Any]] = []
        all_deadlocks: List[Dict[str, Any]] = []
        connection_status_list: List[Dict[str, Any]] = []
        success_count = 0
        fail_count = 0

        now = datetime.now(timezone.utc)

        for instance in instances:
            server_address = f"{instance.name}({instance.host}:{instance.port})"
            logger.info(
                "Checking connection for instance: %s (host=%s:%s db=%s)",
                server_address, instance.host, instance.port, instance.database_name,
            )

            conn_mgr = MSSQLConnectionManager.get_connection_for_instance(
                host=instance.host,
                port=instance.port,
                user=instance.username,
                password=instance.password,
                database=instance.database_name,
            )

            # 连接预检
            previous_was_disconnected = not instance.is_connected
            is_connected = conn_mgr.ping()

            # 记录连接状态
            conn_status = {
                "server_address": server_address,
                "is_connected": is_connected,
                "connection_error": None,
                "previous_was_disconnected": previous_was_disconnected,
                "last_connected_at": str(instance.last_connected_at) if instance.last_connected_at else "无记录",
            }

            # 更新实例连接状态到数据库
            if is_connected:
                await self._update_instance_connection(
                    instance, True, server_address,
                )
                conn_status["connection_error"] = None

                # 检测连接恢复
                if previous_was_disconnected:
                    conn_status["previous_was_disconnected"] = True
                    conn_status["down_duration"] = "未知"
                    connection_status_list.append(conn_status)
            else:
                error_msg = f"Connection failed: {instance.host}:{instance.port}"
                await self._update_instance_connection(
                    instance, False, server_address, error_msg,
                )
                conn_status["connection_error"] = error_msg
                connection_status_list.append(conn_status)
                fail_count += 1
                logger.warning(
                    "Instance %s is offline, skipping data collection",
                    server_address,
                )
                conn_mgr.close()
                continue

            # 连接成功，执行采集
            logger.info(
                "Collecting metrics from instance: %s",
                server_address,
            )

            try:
                collector = MetricsCollector(connection_manager=conn_mgr)
                data = await asyncio.to_thread(collector.collect_all_metrics)

                instance_metrics = data.get("metrics", [])
                instance_deadlocks = data.get("deadlocks", [])

                async with async_session_factory() as session:
                    try:
                        await self._store_metrics(
                            session, instance_metrics, server_address
                        )
                        await self._store_deadlocks(
                            session, instance_deadlocks, server_address
                        )
                        await self._store_slow_queries(
                            session, data.get("slow_queries", []), server_address
                        )
                        await self._store_disk_space(
                            session, data.get("disk_space", []), server_address
                        )
                        await self._store_blocking_events(
                            session, data.get("blocking_events", []), server_address
                        )
                        await self._store_missing_indexes(
                            session, data.get("missing_indexes", []), server_address
                        )
                        await self._store_index_fragmentation(
                            session, data.get("fragmented_indexes", []), server_address
                        )
                        await session.commit()
                        logger.info(
                            "Instance %s: stored %d metrics, %d deadlocks, %d slow queries, %d disk records, %d blocking events, %d missing indexes, %d fragmented indexes",
                            server_address,
                            len(instance_metrics),
                            len(instance_deadlocks),
                            len(data.get("slow_queries", [])),
                            len(data.get("disk_space", [])),
                            len(data.get("blocking_events", [])),
                            len(data.get("missing_indexes", [])),
                            len(data.get("fragmented_indexes", [])),
                        )
                    except Exception as e:
                        await session.rollback()
                        logger.error(
                            "Failed to store data for instance %s: %s",
                            server_address, e,
                        )

                all_metrics.extend(instance_metrics)
                all_deadlocks.extend(instance_deadlocks)
                success_count += 1

            except Exception as e:
                fail_count += 1
                logger.error(
                    "Failed to collect metrics from instance %s: %s",
                    server_address, e, exc_info=True,
                )
            finally:
                try:
                    conn_mgr.close()
                except Exception:
                    pass

        logger.info(
            "Multi-instance collection cycle completed: %d success, %d failed, "
            "%d total metrics, %d total deadlocks",
            success_count, fail_count, len(all_metrics), len(all_deadlocks),
        )

        # 汇总所有实例的数据和连接状态执行告警检查
        aggregated_data: Dict[str, Any] = {
            "metrics": all_metrics,
            "deadlocks": all_deadlocks,
        }
        if connection_status_list:
            aggregated_data["connection_status"] = connection_status_list
        await self._run_alert_checks(aggregated_data)

    @batch_store_handler("slow_query")
    async def _store_slow_queries(
        self, session, sq: Dict[str, Any], server_address: str, now: datetime
    ) -> None:
        """存储单条慢查询记录"""
        last_exec = sq.get("last_execution_time")
        if isinstance(last_exec, str):
            last_exec = datetime.fromisoformat(last_exec)

        params = build_field_params(sq, SLOW_QUERY_FIELD_MAP, {
            "last_execution_time": last_exec,
            "collected_at": now,
            "server_address": server_address,
        })

        stmt = text("""
            INSERT INTO slow_queries (
                sql_hash, sql_text, execution_count,
                total_cpu_ms, total_logical_reads, total_elapsed_ms,
                avg_elapsed_ms, last_execution_time, collected_at, server_address
            ) VALUES (
                :sql_hash, :sql_text, :execution_count,
                :total_cpu_ms, :total_logical_reads, :total_elapsed_ms,
                :avg_elapsed_ms, :last_execution_time, :collected_at, :server_address
            )
        """)
        await session.execute(stmt, params)

    @batch_store_handler("disk_space")
    async def _store_disk_space(
        self, session, disk: Dict[str, Any], server_address: str, now: datetime
    ) -> None:
        """存储单条磁盘空间记录"""
        params = build_field_params(disk, DISK_SPACE_FIELD_MAP, {
            "collected_at": now,
            "server_address": server_address,
        })

        stmt = text("""
            INSERT INTO disk_space_records (
                database_name, data_file_mb, log_file_mb,
                total_mb, used_mb, free_mb, usage_pct,
                collected_at, server_address
            ) VALUES (
                :database_name, :data_file_mb, :log_file_mb,
                :total_mb, :used_mb, :free_mb, :usage_pct,
                :collected_at, :server_address
            )
        """)
        await session.execute(stmt, params)

    @batch_store_handler("blocking_event")
    async def _store_blocking_events(
        self, session, event: Dict[str, Any], server_address: str, now: datetime
    ) -> None:
        """存储单条阻塞事件记录"""
        params = build_field_params(event, BLOCKING_EVENT_FIELD_MAP, {
            "collected_at": now,
            "server_address": server_address,
        })

        stmt = text("""
            INSERT INTO blocking_events (
                blocked_spid, blocking_spid, wait_type, wait_time_ms,
                blocked_sql, blocking_sql, blocked_db,
                collected_at, server_address
            ) VALUES (
                :blocked_spid, :blocking_spid, :wait_type, :wait_time_ms,
                :blocked_sql, :blocking_sql, :blocked_db,
                :collected_at, :server_address
            )
        """)
        await session.execute(stmt, params)

    async def _store_missing_indexes(
        self, session: AsyncSession, data: List[Dict[str, Any]], server_address: str
    ) -> None:
        """将缺失索引数据写入数据库"""
        from app.models.index_analysis import MissingIndex

        for item in data:
            record = MissingIndex(
                database_name=item.get("database_name", "unknown"),
                schema_name=item.get("schema_name", ""),
                table_name=item.get("table_name", ""),
                equality_columns=item.get("equality_columns"),
                inequality_columns=item.get("inequality_columns"),
                included_columns=item.get("included_columns"),
                avg_user_impact=item.get("avg_user_impact", 0.0),
                user_seeks=item.get("user_seeks", 0),
                user_scans=item.get("user_scans", 0),
                collected_at=datetime.now(timezone.utc),
                server_address=server_address,
            )
            session.add(record)

    async def _store_index_fragmentation(
        self, session: AsyncSession, data: List[Dict[str, Any]], server_address: str
    ) -> None:
        """将索引碎片数据写入数据库"""
        from app.models.index_analysis import IndexFragmentation

        for item in data:
            record = IndexFragmentation(
                database_name=item.get("database_name", "unknown"),
                schema_name=item.get("schema_name", ""),
                table_name=item.get("table_name", ""),
                index_name=item.get("index_name", ""),
                avg_fragmentation_pct=item.get("avg_fragmentation_pct", 0.0),
                page_count=item.get("page_count", 0),
                index_type=item.get("index_type", "NONCLUSTERED"),
                collected_at=datetime.now(timezone.utc),
                server_address=server_address,
            )
            session.add(record)

    async def _run_alert_checks(self, metrics_data: Dict[str, Any]) -> None:
        """执行告警规则检查"""
        if self._alert_engine is None:
            logger.warning("AlertEngine not initialized, skipping alert checks")
            return

        try:
            alerts = await self._alert_engine.process_metrics(metrics_data)
            if alerts:
                logger.info(
                    "Alert checks completed: %d new alert(s) created",
                    len(alerts),
                )
            else:
                logger.debug("Alert checks completed: no new alerts")
        except Exception as e:
            logger.error("Alert check failed: %s", e, exc_info=True)

    async def _store_metrics(
        self, session, metrics: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将指标数据批量写入 PostgreSQL"""
        all_params = []
        for metric in metrics:
            category = metric["category"]
            timestamp = metric["timestamp"]
            values = metric["values"]

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            for key, value in values.items():
                if value is None:
                    continue
                try:
                    all_params.append({
                        "category": category,
                        "metric_name": key,
                        "metric_value": float(value),
                        "collected_at": timestamp,
                        "server_address": server_address,
                    })
                except (TypeError, ValueError) as e:
                    logger.warning(
                        "Skip metric %s/%s: invalid value %r - %s",
                        category, key, value, e,
                    )

        if not all_params:
            return

        stmt = text("""
            INSERT INTO metrics (category, metric_name, metric_value, collected_at, server_address)
            VALUES (:category, :metric_name, :metric_value, :collected_at, :server_address)
        """)
        await session.execute(stmt, all_params)

    async def _store_deadlocks(
        self, session, deadlocks: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将死锁事件写入 PostgreSQL"""
        for dl in deadlocks:
            # 从进程列表中提取主要用户的上下文信息
            processes = dl.get("processes", []) or []
            primary_login = None
            primary_host = None
            primary_app = None
            for p in processes:
                if p.get("login_name"):
                    primary_login = p["login_name"]
                if p.get("hostname"):
                    primary_host = p["hostname"]
                if p.get("clientapp"):
                    primary_app = p["clientapp"]
                if primary_login and primary_host and primary_app:
                    break

            stmt = text("""
                INSERT INTO deadlocks (
                    occur_at, victim_session_id, deadlock_xml, server_address,
                    login_name, host_name, client_app
                ) VALUES (
                    :occur_at, :victim_session_id, :deadlock_xml, :server_address,
                    :login_name, :host_name, :client_app
                )
                RETURNING id
            """)
            result = await session.execute(
                stmt,
                {
                    "occur_at": dl.get("occur_at"),
                    "victim_session_id": dl.get("victim_session_id"),
                    "deadlock_xml": dl.get("deadlock_xml", ""),
                    "server_address": server_address,
                    "login_name": primary_login,
                    "host_name": primary_host,
                    "client_app": primary_app,
                },
            )
            event_id = result.scalar_one()

            processes = dl.get("processes", []) or []
            sql_statements = dl.get("sql_statements", []) or []
            involved_objects = dl.get("involved_objects", []) or []

            for i, proc in enumerate(processes):
                sql_text = sql_statements[i] if i < len(sql_statements) else None
                stmt_sql = text("""
                    INSERT INTO deadlock_sqls (
                        event_id, session_id, sql_text, isolation_level, involved_objects,
                        login_name, host_name, client_app
                    ) VALUES (
                        :event_id, :session_id, :sql_text, :isolation_level, :involved_objects,
                        :login_name, :host_name, :client_app
                    )
                """)
                await session.execute(
                    stmt_sql,
                    {
                        "event_id": event_id,
                        "session_id": proc.get("session_id"),
                        "sql_text": sql_text,
                        "isolation_level": proc.get("isolation_level"),
                        "involved_objects": ",".join(involved_objects) if involved_objects else None,
                        "login_name": proc.get("login_name"),
                        "host_name": proc.get("hostname"),
                        "client_app": proc.get("clientapp"),
                    },
                )

    def add_cleanup_job(self) -> None:
        """添加定时数据清理任务（每天凌晨 3 点执行）"""
        if self.scheduler is None:
            raise RuntimeError("Scheduler not initialized. Call setup() first.")

        self.scheduler.add_job(
            func=self._cleanup_old_data,
            trigger="cron",
            hour=3,
            minute=0,
            id="cleanup_old_data",
            name="Cleanup old monitoring data",
            replace_existing=True,
        )
        logger.info("Cleanup job added: daily at 03:00")

    async def _cleanup_old_data(self) -> None:
        """清理超过保留天数的旧监控数据（分批删除，避免锁表）"""
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    text("SELECT config_value FROM system_configs WHERE config_key = 'data_retention_days'")
                )
                row = result.fetchone()
                retention_days = int(row[0]) if row and row[0] else 90

                if retention_days <= 0:
                    return

                cutoff = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) - timedelta(days=retention_days)

                tables = [
                    ("metrics", "collected_at"),
                    ("slow_queries", "collected_at"),
                    ("disk_space_records", "collected_at"),
                    ("blocking_events", "collected_at"),
                    ("deadlocks", "occur_at"),
                    ("deadlock_sqls", "event_id"),
                    ("missing_indexes", "collected_at"),
                    ("index_fragmentation", "collected_at"),
                ]
                batch_size = 1000
                total_deleted = 0

                for table, date_column in tables:
                    try:
                        if table == "deadlock_sqls":
                            result = await session.execute(
                                text("SELECT id FROM deadlocks WHERE occur_at < :cutoff"),
                                {"cutoff": cutoff},
                            )
                            deadlock_ids = [row[0] for row in result]
                            if deadlock_ids:
                                deleted = 0
                                while deadlock_ids:
                                    batch_ids = deadlock_ids[:batch_size]
                                    deadlock_ids = deadlock_ids[batch_size:]
                                    result = await session.execute(
                                        text(f"DELETE FROM {table} WHERE event_id IN ({','.join([':id_%d' % i for i in range(len(batch_ids))])})"),
                                        {f"id_{i}": id_val for i, id_val in enumerate(batch_ids)},
                                    )
                                    deleted += result.rowcount
                                total_deleted += deleted
                                if deleted > 0:
                                    logger.info("Cleanup %s: deleted %d rows", table, deleted)
                        else:
                            deleted = 0
                            while True:
                                result = await session.execute(
                                    text(f"DELETE FROM {table} WHERE {date_column} < :cutoff LIMIT :batch_size"),
                                    {"cutoff": cutoff, "batch_size": batch_size},
                                )
                                batch_deleted = result.rowcount
                                if batch_deleted == 0:
                                    break
                                deleted += batch_deleted
                                await session.commit()
                            total_deleted += deleted
                            if deleted > 0:
                                logger.info("Cleanup %s: deleted %d rows older than %d days", table, deleted, retention_days)
                    except Exception as e:
                        logger.warning("Failed to clean table %s: %s", table, e)

                alert_cutoff = datetime.now(timezone.utc) - timedelta(days=180)
                try:
                    deleted = 0
                    while True:
                        result = await session.execute(
                            text("DELETE FROM alert_logs WHERE triggered_at < :cutoff LIMIT :batch_size"),
                            {"cutoff": alert_cutoff, "batch_size": batch_size},
                        )
                        batch_deleted = result.rowcount
                        if batch_deleted == 0:
                            break
                        deleted += batch_deleted
                        await session.commit()
                    total_deleted += deleted
                    if deleted > 0:
                        logger.info("Cleanup alert_logs: deleted %d rows", deleted)
                except Exception as e:
                    logger.warning("Failed to clean alert_logs: %s", e)

                await session.commit()
                if total_deleted > 0:
                    logger.info("Data cleanup completed: total %d rows deleted", total_deleted)
                else:
                    logger.debug("Data cleanup completed: no expired data found")

        except Exception as e:
            logger.error("Data cleanup job failed: %s", e, exc_info=True)

    def start(self) -> None:
        """启动调度器"""
        if self.scheduler is None:
            raise RuntimeError("Scheduler not initialized. Call setup() first.")
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self) -> None:
        """停止调度器"""
        if self.scheduler is not None and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
