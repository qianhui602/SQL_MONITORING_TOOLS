"""
路由模块导入
将所有子路由聚合到 api_router，供 main.py 注册。
"""

from fastapi import APIRouter

from app.routers.metrics import router as metrics_router
from app.routers.deadlocks import router as deadlocks_router
from app.routers.alerts import router as alerts_router
from app.routers.config import router as config_router
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.instances import router as instances_router
from app.routers.slow_queries import router as slow_queries_router
from app.routers.blocking import router as blocking_router
from app.routers.disk import router as disk_router
from app.routers.indexes import router as indexes_router
from app.routers.alert_rules import router as alert_rules_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.export import router as export_router
from app.routers.notifications import router as notifications_router
from app.routers.reports import router as reports_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["性能指标"])
api_router.include_router(deadlocks_router, prefix="/deadlocks", tags=["死锁事件"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["告警管理"])
api_router.include_router(config_router, prefix="/config", tags=["系统配置"])
api_router.include_router(instances_router, prefix="/instances", tags=["实例管理"])
api_router.include_router(slow_queries_router, prefix="/slow-queries", tags=["慢查询"])
api_router.include_router(blocking_router, prefix="/blocking", tags=["阻塞进程"])
api_router.include_router(disk_router, prefix="/disk", tags=["磁盘IO"])
api_router.include_router(indexes_router, prefix="/indexes", tags=["索引分析"])
api_router.include_router(alert_rules_router, prefix="/alert-rules", tags=["告警规则"])
api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["审计日志"])
api_router.include_router(export_router, prefix="/export", tags=["数据导出"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["通知"])
api_router.include_router(reports_router, prefix="/reports", tags=["报告"])
api_router.include_router(upgrade_router, prefix="/upgrade", tags=["在线升级"])

__all__ = ["api_router"]
