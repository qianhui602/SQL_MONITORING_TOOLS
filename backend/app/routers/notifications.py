"""
通知 API 路由
基于告警日志提供通知功能：未读通知列表、标记已读、删除、全部已读。
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func as sa_func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import AlertLog
from app.models.user import User
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class NotificationItem(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime
    read: bool

    model_config = {"from_attributes": True}


class NotificationsResponse(BaseModel):
    items: List[NotificationItem]
    total: int
    unread_count: int

    model_config = {"from_attributes": True}


@router.get(
    "/unread-count",
    summary="获取未读通知数量",
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """仅返回未读通知数量，用于轻量级轮询。"""
    stmt = select(sa_func.count(AlertLog.id)).where(
        AlertLog.acknowledged == False
    )
    try:
        result = await db.execute(stmt)
        count = result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询未读数失败: {str(e)}"
        )
    return {"unread_count": count}


@router.get(
    "",
    response_model=NotificationsResponse,
    summary="获取通知列表",
)
async def get_notifications(
    limit: int = Query(20, ge=1, le=100, description="返回条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> NotificationsResponse:
    """获取通知列表，按时间倒序，包含未读数量。"""
    unread_stmt = select(sa_func.count(AlertLog.id)).where(
        AlertLog.acknowledged == False
    )
    count_stmt = select(sa_func.count(AlertLog.id))

    try:
        unread_result = await db.execute(unread_stmt)
        unread_count = unread_result.scalar() or 0

        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0

        query_stmt = (
            select(AlertLog)
            .order_by(AlertLog.triggered_at.desc())
            .limit(limit)
        )
        result = await db.execute(query_stmt)
        alerts = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询通知失败: {str(e)}"
        )

    items = [
        NotificationItem(
            id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            triggered_at=alert.triggered_at,
            read=alert.acknowledged,
        )
        for alert in alerts
    ]

    return NotificationsResponse(
        items=items, total=total, unread_count=unread_count
    )


@router.put("/{notification_id}/read", summary="标记通知为已读")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """将指定通知标记为已读。"""
    check_stmt = select(AlertLog).where(AlertLog.id == notification_id)
    try:
        check_result = await db.execute(check_stmt)
        alert = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询通知失败: {str(e)}"
        )

    if alert is None:
        raise HTTPException(
            status_code=404, detail=f"通知不存在: id={notification_id}"
        )

    if alert.acknowledged:
        return {"message": "已标记为已读", "id": notification_id}

    now = datetime.now(timezone.utc)
    update_stmt = (
        update(AlertLog)
        .where(AlertLog.id == notification_id)
        .values(acknowledged=True, acknowledged_at=now)
    )
    try:
        await db.execute(update_stmt)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"标记已读失败: {str(e)}"
        )

    return {"message": "已标记为已读", "id": notification_id}


@router.delete("/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """删除指定通知。"""
    check_stmt = select(AlertLog).where(AlertLog.id == notification_id)
    try:
        check_result = await db.execute(check_stmt)
        alert = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询通知失败: {str(e)}"
        )

    if alert is None:
        raise HTTPException(
            status_code=404, detail=f"通知不存在: id={notification_id}"
        )

    delete_stmt = delete(AlertLog).where(AlertLog.id == notification_id)
    try:
        await db.execute(delete_stmt)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"删除通知失败: {str(e)}"
        )

    return {"message": "已删除", "id": notification_id}


@router.post("/read-all", summary="全部标记已读")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """将所有未读通知标记为已读。"""
    now = datetime.now(timezone.utc)
    update_stmt = (
        update(AlertLog)
        .where(AlertLog.acknowledged == False)
        .values(acknowledged=True, acknowledged_at=now)
    )
    try:
        result = await db.execute(update_stmt)
        await db.flush()
        affected = result.rowcount
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"全部标记已读失败: {str(e)}"
        )

    return {"message": f"已将 {affected} 条通知标记为已读", "count": affected}
