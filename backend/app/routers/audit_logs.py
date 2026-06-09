"""
审计日志 API 路由
提供审计日志的分页查询接口，支持按用户、操作类型、时间范围筛选。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.auth_service import get_current_user, require_admin

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class AuditLogItem(BaseModel):
    """审计日志单项"""

    id: int
    username: str
    action: str
    resource: str
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """审计日志分页响应"""

    items: List[AuditLogItem]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="查询审计日志",
)
async def get_audit_logs(
    username: Optional[str] = Query(None, description="用户名筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选：CREATE / UPDATE / DELETE"),
    start_time: Optional[datetime] = Query(None, description="操作起始时间"),
    end_time: Optional[datetime] = Query(None, description="操作结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AuditLogListResponse:
    """分页查询审计日志，支持按用户名、操作类型和时间范围筛选。
    仅管理员可访问。
    """
    conditions = []

    if username:
        conditions.append(AuditLog.username == username)
    if action:
        conditions.append(AuditLog.action == action)
    if start_time:
        conditions.append(AuditLog.created_at >= start_time)
    if end_time:
        conditions.append(AuditLog.created_at <= end_time)

    # 查询总数
    count_stmt = select(sa_func.count(AuditLog.id)).where(*conditions)
    try:
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询审计日志总数失败: {str(e)}"
        )

    # 查询分页数据
    offset = (page - 1) * page_size
    query_stmt = (
        select(AuditLog)
        .where(*conditions)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    try:
        result = await db.execute(query_stmt)
        logs = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询审计日志列表失败: {str(e)}"
        )

    items = [
        AuditLogItem(
            id=log.id,
            username=log.username,
            action=log.action,
            resource=log.resource,
            detail=log.detail,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return AuditLogListResponse(
        items=items, total=total, page=page, page_size=page_size
    )
