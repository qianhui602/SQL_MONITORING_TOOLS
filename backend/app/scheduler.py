"""
APScheduler 定时任务管理
负责定时采集 SQL Server 指标并写入 PostgreSQL
支持单实例（兼容旧模式）和多实例模式。
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

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

logger = logging.getLogger(__name__)

_CONFIG_KEY_MAP = {
    "mssql_host": "MSSQL_HOST",
    "mssql_port": "MSSQL_PORT",
    "mssql_user": "MSSQL_USER",
    "mssql_password": "MSSQL_PASSWORD",
    "mssql_database": "MSSQL_DATABASE",
    "scheduler_interval_seconds": "SCHEDULER_INTERVAL_SECONDS",
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
        )
        logger.info("Collect job added with interval=%ds", interval_seconds)

    async def _load_runtime_config(self) -> Optional[Dict[str, str]]:
        """从数据库加载运行时配置（SQL Server 连接信息等）"""
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
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(MonitoredInstance).where(
                        MonitoredInstance.is_active == True
                    ).order_by(MonitoredInstance.id)
                )
                instances = result.scalars().all()
                logger.info("Loaded %d active monitored instance(s)", len(instances))
                return list(instances)
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

        try:
            data = self._collector.collect_all_metrics()
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

        await self._run_alert_checks(data)

    async def _collect_multi_instance(self, runtime_config: Dict[str, str]) -> None:
        """多实例采集模式：遍历所有活跃实例逐个采集"""
        instances = await self._load_active_instances()

        if not instances:
            logger.warning("No active instances found, skipping multi-instance collection")
            return

        all_metrics: List[Dict[str, Any]] = []
        all_deadlocks: List[Dict[str, Any]] = []
        success_count = 0
        fail_count = 0

        for instance in instances:
            server_address = f"{instance.name}({instance.host}:{instance.port})"
            logger.info(
                "Collecting metrics from instance: %s (host=%s:%s db=%s)",
                server_address, instance.host, instance.port, instance.database_name,
            )

            try:
                # 为每个实例创建独立的连接管理器
                conn_mgr = MSSQLConnectionManager.get_connection_for_instance(
                    host=instance.host,
                    port=instance.port,
                    user=instance.username,
                    password=instance.password,
                    database=instance.database_name,
                )
                collector = MetricsCollector(connection_manager=conn_mgr)
                data = collector.collect_all_metrics()

                # 为该实例的指标打上 server_address
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

                # 关闭该实例的连接
                try:
                    conn_mgr.close()
                except Exception:
                    pass

            except Exception as e:
                fail_count += 1
                logger.error(
                    "Failed to collect metrics from instance %s: %s",
                    server_address, e, exc_info=True,
                )

        logger.info(
            "Multi-instance collection cycle completed: %d success, %d failed, "
            "%d total metrics, %d total deadlocks",
            success_count, fail_count, len(all_metrics), len(all_deadlocks),
        )

        # 汇总所有实例的数据执行告警检查
        if all_metrics or all_deadlocks:
            aggregated_data = {
                "metrics": all_metrics,
                "deadlocks": all_deadlocks,
            }
            await self._run_alert_checks(aggregated_data)

    async def _store_slow_queries(
        self, session, slow_queries: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将慢查询数据写入 PostgreSQL"""
        now = datetime.now(timezone.utc)
        for sq in slow_queries:
            try:
                last_exec = sq.get("last_execution_time")
                if isinstance(last_exec, str):
                    last_exec = datetime.fromisoformat(last_exec)

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
                await session.execute(
                    stmt,
                    {
                        "sql_hash": sq.get("sql_hash", ""),
                        "sql_text": sq.get("sql_text", ""),
                        "execution_count": sq.get("execution_count", 0),
                        "total_cpu_ms": sq.get("total_cpu_ms", 0.0),
                        "total_logical_reads": sq.get("total_logical_reads", 0),
                        "total_elapsed_ms": sq.get("total_elapsed_ms", 0.0),
                        "avg_elapsed_ms": sq.get("avg_elapsed_ms", 0.0),
                        "last_execution_time": last_exec,
                        "collected_at": now,
                        "server_address": server_address,
                    },
                )
            except Exception as e:
                logger.warning("Failed to store slow query record: %s", e)

    async def _store_disk_space(
        self, session, disk_space: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将磁盘空间数据写入 PostgreSQL"""
        now = datetime.now(timezone.utc)
        for disk in disk_space:
            try:
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
                await session.execute(
                    stmt,
                    {
                        "database_name": disk.get("database_name", ""),
                        "data_file_mb": disk.get("data_file_mb", 0.0),
                        "log_file_mb": disk.get("log_file_mb", 0.0),
                        "total_mb": disk.get("total_mb", 0.0),
                        "used_mb": disk.get("used_mb", 0.0),
                        "free_mb": disk.get("free_mb", 0.0),
                        "usage_pct": disk.get("usage_pct", 0.0),
                        "collected_at": now,
                        "server_address": server_address,
                    },
                )
            except Exception as e:
                logger.warning("Failed to store disk space record: %s", e)

    async def _store_blocking_events(
        self, session, blocking_events: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将阻塞事件数据写入 PostgreSQL"""
        now = datetime.now(timezone.utc)
        for event in blocking_events:
            try:
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
                await session.execute(
                    stmt,
                    {
                        "blocked_spid": event.get("blocked_spid", 0),
                        "blocking_spid": event.get("blocking_spid", 0),
                        "wait_type": event.get("wait_type", ""),
                        "wait_time_ms": event.get("wait_time_ms", 0),
                        "blocked_sql": event.get("blocked_sql"),
                        "blocking_sql": event.get("blocking_sql"),
                        "blocked_db": event.get("blocked_db"),
                        "collected_at": now,
                        "server_address": server_address,
                    },
                )
            except Exception as e:
                logger.warning("Failed to store blocking event: %s", e)

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
        """将指标数据写入 PostgreSQL"""
        for metric in metrics:
            category = metric["category"]
            timestamp = metric["timestamp"]
            values = metric["values"]

            # Parse ISO format timestamp to datetime
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            for key, value in values.items():
                if value is None:
                    continue
                try:
                    stmt = text("""
                        INSERT INTO metrics (category, metric_name, metric_value, collected_at, server_address)
                        VALUES (:category, :metric_name, :metric_value, :collected_at, :server_address)
                    """)
                    await session.execute(
                        stmt,
                        {
                            "category": category,
                            "metric_name": key,
                            "metric_value": float(value),
                            "collected_at": timestamp,
                            "server_address": server_address,
                        },
                    )
                except (TypeError, ValueError) as e:
                    logger.warning(
                        "Skip metric %s/%s: invalid value %r - %s",
                        category, key, value, e,
                    )

    async def _store_deadlocks(
        self, session, deadlocks: list[Dict[str, Any]], server_address: str
    ) -> None:
        """将死锁事件写入 PostgreSQL"""
        for dl in deadlocks:
            stmt = text("""
                INSERT INTO deadlocks (
                    occur_at, victim_session_id, deadlock_xml, server_address
                ) VALUES (
                    :occur_at, :victim_session_id, :deadlock_xml, :server_address
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
                        event_id, session_id, sql_text, isolation_level, involved_objects
                    ) VALUES (
                        :event_id, :session_id, :sql_text, :isolation_level, :involved_objects
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
        """清理超过保留天数的旧监控数据"""
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
                    "metrics",
                    "slow_queries",
                    "disk_space_records",
                    "blocking_events",
                ]
                total_deleted = 0
                for table in tables:
                    try:
                        result = await session.execute(
                            text(f"DELETE FROM {table} WHERE collected_at < :cutoff"),
                            {"cutoff": cutoff},
                        )
                        deleted = result.rowcount
                        total_deleted += deleted
                        if deleted > 0:
                            logger.info("Cleanup %s: deleted %d rows older than %d days", table, deleted, retention_days)
                    except Exception as e:
                        logger.warning("Failed to clean table %s: %s", table, e)

                # 清理旧的告警日志（保留 180 天）
                alert_cutoff = datetime.now(timezone.utc) - timedelta(days=180)
                try:
                    result = await session.execute(
                        text("DELETE FROM alert_logs WHERE triggered_at < :cutoff"),
                        {"cutoff": alert_cutoff},
                    )
                    if result.rowcount > 0:
                        total_deleted += result.rowcount
                        logger.info("Cleanup alert_logs: deleted %d rows", result.rowcount)
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
