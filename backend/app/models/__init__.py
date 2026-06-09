"""
模型导入模块
将所有 ORM 模型集中导入，便于 Alembic 迁移脚本和应用启动时自动建表时引用。
"""

from app.models.performance import MetricRecord
from app.models.deadlock import DeadlockEvent, DeadlockSql
from app.models.alert import AlertLog
from app.models.config import SystemConfig
from app.models.user import User, UserRole
from app.models.instance import MonitoredInstance
from app.models.slow_query import SlowQueryRecord
from app.models.blocking import BlockingEvent
from app.models.disk import DiskSpaceRecord
from app.models.index_analysis import MissingIndex, IndexFragmentation
from app.models.alert_rule import AlertRule as AlertRuleModel
from app.models.audit_log import AuditLog
from app.models.report import ReportRecord

__all__ = [
    "MetricRecord",
    "DeadlockEvent",
    "DeadlockSql",
    "AlertLog",
    "SystemConfig",
    "User",
    "UserRole",
    "MonitoredInstance",
    "SlowQueryRecord",
    "BlockingEvent",
    "DiskSpaceRecord",
    "MissingIndex",
    "IndexFragmentation",
    "AlertRuleModel",
    "AuditLog",
    "ReportRecord",
]
