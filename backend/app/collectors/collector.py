"""
SQL Server 指标采集协调器
整合连接管理、性能采集和死锁检测
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from app.collectors.deadlock import DeadlockDetector
from app.collectors.performance import PerformanceCollector
from app.collectors.slow_query import SlowQueryCollector
from app.collectors.sqlserver import MSSQLConnectionManager

logger = logging.getLogger(__name__)


class MetricsCollector:
    """指标采集协调器

    整合 MSSQLConnectionManager、PerformanceCollector、DeadlockDetector，
    对外提供统一的指标采集入口。
    """

    def __init__(self, connection_manager: MSSQLConnectionManager = None) -> None:
        self.connection_manager = connection_manager or MSSQLConnectionManager()
        self.performance_collector = PerformanceCollector()
        self.deadlock_detector = DeadlockDetector()
        self.slow_query_collector = SlowQueryCollector()

    def collect_all_metrics(self) -> Dict[str, Any]:
        """执行一次完整的采集

        采集性能指标和死锁事件，整理成统一格式返回。
        所有异常在内部消化，确保调用方总能拿到结构化数据。

        Returns:
            dict: 采集结果，格式:
                {
                    "metrics": [...],
                    "deadlocks": [...]
                }
        """
        result: Dict[str, Any] = {
            "metrics": [],
            "deadlocks": [],
            "slow_queries": [],
        }

        try:
            connection = self.connection_manager.get_connection()
        except Exception as e:
            logger.error("Failed to get MSSQL connection for metrics collection: %s", e)
            return result

        # 采集性能指标
        try:
            perf_metrics = self.performance_collector.collect_all(connection)
            now = datetime.now(timezone.utc)
            for category, data in perf_metrics.items():
                if "error" not in data and data:
                    metric_entry = {
                        "category": category,
                        "timestamp": now.isoformat(),
                        "values": data,
                    }
                    result["metrics"].append(metric_entry)
        except Exception as e:
            logger.error("Unexpected error during performance metrics collection: %s", e)

        # 采集死锁事件
        try:
            deadlock_events = self.deadlock_detector.detect(connection)
            for event in deadlock_events:
                result["deadlocks"].append({
                    "occur_at": event["occur_at"],
                    "victim_session_id": event["parsed"]["victim_session_id"],
                    "processes": event["parsed"]["processes"],
                    "sql_statements": event["parsed"]["sql_statements"],
                    "involved_objects": event["parsed"]["involved_objects"],
                    "deadlock_xml": event["deadlock_xml"],
                })
        except Exception as e:
            logger.error("Unexpected error during deadlock detection: %s", e)

        # 采集慢查询
        try:
            slow_query_data = self.slow_query_collector.collect_slow_queries(connection)
            result["slow_queries"] = slow_query_data.get("slow_queries", [])
            if slow_query_data.get("error"):
                logger.error("Slow query collection error: %s", slow_query_data["error"])
        except Exception as e:
            logger.error("Unexpected error during slow query collection: %s", e)

        return result
