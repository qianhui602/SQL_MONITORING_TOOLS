"""
通知 API 路由
基于告警日志提供通知功能：未读通知列表、标记已读、删除、全部已读。
使用 notification_reads 表实现按用户过滤已读状态。
"""

import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func as sa_func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import AlertLog
from app.models.notification_read import NotificationRead
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


def _user_read_subq(user_id: int):
    """构建当前用户已读通知的子查询"""
    return (
        select(NotificationRead.alert_id)
        .where(NotificationRead.user_id == user_id)
        .scalar_subquery()
    )


@router.get(
    "/unread-count",
    summary="获取未读通知数量",
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """仅返回当前用户的未读通知数量，用于轻量级轮询。"""
    read_subq = _user_read_subq(user.id)
    stmt = select(sa_func.count(AlertLog.id)).where(
        ~AlertLog.id.in_(read_subq)
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
    user: User = Depends(get_current_user),
) -> NotificationsResponse:
    """获取当前用户的通知列表，按时间倒序，包含用户级别的已读状态。"""
    read_subq = _user_read_subq(user.id)

    unread_stmt = select(sa_func.count(AlertLog.id)).where(
        ~AlertLog.id.in_(read_subq)
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

        # 批量查询当前用户对这些告警的已读状态
        alert_ids = [a.id for a in alerts]
        if alert_ids:
            read_ids_stmt = select(NotificationRead.alert_id).where(
                NotificationRead.user_id == user.id,
                NotificationRead.alert_id.in_(alert_ids),
            )
            read_ids_result = await db.execute(read_ids_stmt)
            read_ids = set(read_ids_result.scalars().all())
        else:
            read_ids = set()
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
            read=alert.id in read_ids,
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
    user: User = Depends(get_current_user),
) -> dict:
    """将指定通知标记为当前用户已读。"""
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

    # 检查是否已读
    exists_stmt = select(NotificationRead).where(
        NotificationRead.user_id == user.id,
        NotificationRead.alert_id == notification_id,
    )
    exists_result = await db.execute(exists_stmt)
    if exists_result.scalar_one_or_none() is not None:
        return {"message": "已标记为已读", "id": notification_id}

    record = NotificationRead(user_id=user.id, alert_id=notification_id)
    try:
        db.add(record)
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
    """删除指定告警通知（同时清理所有用户的已读记录）。"""
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

    # 先删除已读记录，再删除告警
    try:
        await db.execute(
            delete(NotificationRead).where(
                NotificationRead.alert_id == notification_id
            )
        )
        await db.execute(
            delete(AlertLog).where(AlertLog.id == notification_id)
        )
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"删除通知失败: {str(e)}"
        )

    return {"message": "已删除", "id": notification_id}


@router.post("/read-all", summary="全部标记已读")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """将当前用户的所有未读通知标记为已读。"""
    # 查询所有未读告警 ID
    read_subq = _user_read_subq(user.id)
    stmt = select(AlertLog.id).where(~AlertLog.id.in_(read_subq))
    try:
        result = await db.execute(stmt)
        unread_ids = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询未读通知失败: {str(e)}"
        )

    if not unread_ids:
        return {"message": "没有未读通知", "count": 0}

    # 批量插入已读记录
    now = datetime.now(timezone.utc)
    records = [
        NotificationRead(user_id=user.id, alert_id=aid, read_at=now)
        for aid in unread_ids
    ]
    try:
        db.add_all(records)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"全部标记已读失败: {str(e)}"
        )

    return {"message": f"已将 {len(records)} 条通知标记为已读", "count": len(records)}
