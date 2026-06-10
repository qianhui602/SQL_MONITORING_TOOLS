"""
APScheduler 定时任务管理
负责定时采集 SQL Server 指标并写入 PostgreSQL
支持单实例（兼容旧模式）和多实例模式。
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, text

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
                await session.commit()
                logger.info(
                    "Single-instance collection completed: %d metrics, %d deadlocks, %d slow queries, %d disk records",
                    len(data["metrics"]),
                    len(data["deadlocks"]),
                    len(data["slow_queries"]),
                    len(data["disk_space"]),
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
                        await session.commit()
                        logger.info(
                            "Instance %s: stored %d metrics, %d deadlocks, %d slow queries, %d disk records",
                            server_address,
                            len(instance_metrics),
                            len(instance_deadlocks),
                            len(data.get("slow_queries", [])),
                            len(data.get("disk_space", [])),
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
