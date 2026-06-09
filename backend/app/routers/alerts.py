"""
告警 API 路由
提供告警记录列表查询和确认操作接口。
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import func as sa_func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert import AlertLog
from app.models.user import User
from app.services.auth_service import get_current_user, require_admin
from app.services.audit_service import log_action

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class AlertItem(BaseModel):
    """告警记录单项"""

    id: int
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """告警记录分页响应"""

    items: List[AlertItem]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=AlertListResponse,
    summary="获取告警记录列表",
)
async def get_alerts(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    severity: Optional[str] = Query(None, description="严重级别筛选：low / medium / high / critical"),
    acknowledged: Optional[bool] = Query(None, description="是否已确认"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AlertListResponse:
    """分页查询告警记录，支持按时间范围、严重级别和确认状态筛选。"""
    conditions = []

    if start_time:
        conditions.append(AlertLog.triggered_at >= start_time)
    if end_time:
        conditions.append(AlertLog.triggered_at <= end_time)
    if severity:
        conditions.append(AlertLog.severity == severity)
    if acknowledged is not None:
        conditions.append(AlertLog.acknowledged == acknowledged)

    # 查询总数
    count_stmt = select(sa_func.count(AlertLog.id)).where(*conditions)
    try:
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询告警总数失败: {str(e)}"
        )

    # 查询分页数据
    offset = (page - 1) * page_size
    query_stmt = (
        select(AlertLog)
        .where(*conditions)
        .order_by(AlertLog.triggered_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    try:
        result = await db.execute(query_stmt)
        alerts = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询告警列表失败: {str(e)}"
        )

    items = [
        AlertItem(
            id=alert.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            message=alert.message,
            triggered_at=alert.triggered_at,
            acknowledged=alert.acknowledged,
            acknowledged_at=alert.acknowledged_at,
        )
        for alert in alerts
    ]

    return AlertListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.put(
    "/{alert_id}/acknowledge",
    summary="确认告警",
)
async def acknowledge_alert(
    alert_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """将指定告警标记为已确认，记录确认时间。"""
    # 先检查告警是否存在
    check_stmt = select(AlertLog).where(AlertLog.id == alert_id)
    try:
        check_result = await db.execute(check_stmt)
        alert = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询告警记录失败: {str(e)}"
        )

    if alert is None:
        raise HTTPException(
            status_code=404, detail=f"告警记录不存在: alert_id={alert_id}"
        )

    # 如果已确认，直接返回
    if alert.acknowledged:
        return {
            "message": "告警已确认",
            "alert_id": alert_id,
            "acknowledged": True,
            "acknowledged_at": alert.acknowledged_at,
        }

    # 更新确认状态
    now = datetime.now(timezone.utc)
    update_stmt = (
        update(AlertLog)
        .where(AlertLog.id == alert_id)
        .values(acknowledged=True, acknowledged_at=now)
    )

    try:
        await db.execute(update_stmt)
        await db.flush()  # 确保更新刷入数据库，commit 由 get_db 生命周期管理
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"确认告警失败: {str(e)}"
        )

    # 记录审计日志
    client_ip = request.client.host if request.client else ""
    await log_action(
        db, current_user.username, "UPDATE", "Alert",
        f"确认告警: alert_id={alert_id}, type={alert.alert_type}", client_ip,
    )

    return {
        "message": "告警已确认",
        "alert_id": alert_id,
        "acknowledged": True,
        "acknowledged_at": now,
    }
