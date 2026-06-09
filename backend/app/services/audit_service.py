"""
审计日志服务
提供统一的审计日志写入接口，供所有路由层调用。
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    username: str,
    action: str,
    resource: str,
    detail: str = "",
    ip_address: str = "",
) -> Optional[AuditLog]:
    """写入审计日志

    将用户操作记录写入 audit_logs 表。
    写入失败仅记录错误日志，不影响主业务流程。

    Args:
        db: 数据库 session
        username: 操作用户名
        action: 操作类型（如 CREATE / UPDATE / DELETE）
        resource: 操作资源（如 User / Config / AlertRule）
        detail: 操作详情（可选）
        ip_address: 客户端 IP（可选）

    Returns:
        AuditLog or None: 成功返回对象，失败返回 None
    """
    log_entry = AuditLog(
        username=username,
        action=action,
        resource=resource,
        detail=detail,
        ip_address=ip_address,
    )
    try:
        db.add(log_entry)
        # 不在此 commit，依赖 get_db 的生命周期统一 commit
        logger.debug(
            "Audit log queued: user=%s action=%s resource=%s",
            username,
            action,
            resource,
        )
        return log_entry
    except Exception as e:
        logger.error("Failed to create audit log: %s", e)
        return None
