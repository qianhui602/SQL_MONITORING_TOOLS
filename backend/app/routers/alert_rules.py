"""
自定义告警规则 API 路由
提供告警规则的 CRUD 和启用/禁用操作接口。
"""

import logging
from datetime import datetime, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func as sa_func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.alert_rule import AlertRule
from app.models.user import User
from app.services.auth_service import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class AlertRuleCreate(BaseModel):
    """创建告警规则请求"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    enabled: bool = True
    metric_category: str = Field(..., max_length=50)
    metric_name: str = Field(..., max_length=100)
    operator: str = Field(..., pattern=r"^(gt|lt|gte|lte|eq)$")
    threshold: float
    severity: str = Field(..., pattern=r"^(critical|high|medium|low)$")
    cooldown_minutes: int = Field(default=30, ge=1, le=1440)
    notification_channels: str = Field(default="email", max_length=200)
    silence_start: Optional[str] = Field(default=None, description="HH:MM 格式")
    silence_end: Optional[str] = Field(default=None, description="HH:MM 格式")


class AlertRuleUpdate(BaseModel):
    """更新告警规则请求"""

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    enabled: Optional[bool] = None
    metric_category: Optional[str] = Field(default=None, max_length=50)
    metric_name: Optional[str] = Field(default=None, max_length=100)
    operator: Optional[str] = Field(default=None, pattern=r"^(gt|lt|gte|lte|eq)$")
    threshold: Optional[float] = None
    severity: Optional[str] = Field(default=None, pattern=r"^(critical|high|medium|low)$")
    cooldown_minutes: Optional[int] = Field(default=None, ge=1, le=1440)
    notification_channels: Optional[str] = Field(default=None, max_length=200)
    silence_start: Optional[str] = Field(default=None, description="HH:MM 格式，传空字符串可清除")
    silence_end: Optional[str] = Field(default=None, description="HH:MM 格式，传空字符串可清除")


class ToggleRequest(BaseModel):
    """启用/禁用规则请求"""

    enabled: bool


class AlertRuleResponse(BaseModel):
    """告警规则响应"""

    id: int
    name: str
    description: Optional[str] = None
    enabled: bool
    metric_category: str
    metric_name: str
    operator: str
    threshold: float
    severity: str
    cooldown_minutes: int
    notification_channels: str
    silence_start: Optional[str] = None
    silence_end: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _parse_time(value: Optional[str]) -> Optional[time]:
    """将 HH:MM 字符串解析为 time 对象，失败返回 None"""
    if not value:
        return None
    try:
        parts = value.strip().split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=List[AlertRuleResponse],
    summary="获取告警规则列表",
)
async def list_alert_rules(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[AlertRuleResponse]:
    """获取所有自定义告警规则列表，按创建时间升序排列。"""
    stmt = select(AlertRule).order_by(AlertRule.created_at.asc())
    try:
        result = await db.execute(stmt)
        rules = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询告警规则失败: {str(e)}"
        )

    def _fmt(t: Optional[time]) -> Optional[str]:
        if t is None:
            return None
        return t.strftime("%H:%M")

    return [
        AlertRuleResponse(
            id=r.id,
            name=r.name,
            description=r.description,
            enabled=r.enabled,
            metric_category=r.metric_category,
            metric_name=r.metric_name,
            operator=r.operator,
            threshold=r.threshold,
            severity=r.severity,
            cooldown_minutes=r.cooldown_minutes,
            notification_channels=r.notification_channels,
            silence_start=_fmt(r.silence_start),
            silence_end=_fmt(r.silence_end),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rules
    ]


@router.post(
    "",
    response_model=AlertRuleResponse,
    summary="创建告警规则",
)
async def create_alert_rule(
    payload: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AlertRuleResponse:
    """创建新的自定义告警规则。"""
    rule = AlertRule(
        name=payload.name,
        description=payload.description,
        enabled=payload.enabled,
        metric_category=payload.metric_category,
        metric_name=payload.metric_name,
        operator=payload.operator,
        threshold=payload.threshold,
        severity=payload.severity,
        cooldown_minutes=payload.cooldown_minutes,
        notification_channels=payload.notification_channels,
        silence_start=_parse_time(payload.silence_start),
        silence_end=_parse_time(payload.silence_end),
    )
    db.add(rule)
    try:
        await db.commit()
        await db.refresh(rule)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"创建告警规则失败: {str(e)}"
        )

    def _fmt(t: Optional[time]) -> Optional[str]:
        if t is None:
            return None
        return t.strftime("%H:%M")

    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        enabled=rule.enabled,
        metric_category=rule.metric_category,
        metric_name=rule.metric_name,
        operator=rule.operator,
        threshold=rule.threshold,
        severity=rule.severity,
        cooldown_minutes=rule.cooldown_minutes,
        notification_channels=rule.notification_channels,
        silence_start=_fmt(rule.silence_start),
        silence_end=_fmt(rule.silence_end),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.put(
    "/{rule_id}",
    response_model=AlertRuleResponse,
    summary="更新告警规则",
)
async def update_alert_rule(
    rule_id: int,
    payload: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AlertRuleResponse:
    """更新指定告警规则的配置。"""
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")

    update_values = {}
    if payload.name is not None:
        update_values["name"] = payload.name
    if payload.description is not None:
        update_values["description"] = payload.description
    if payload.enabled is not None:
        update_values["enabled"] = payload.enabled
    if payload.metric_category is not None:
        update_values["metric_category"] = payload.metric_category
    if payload.metric_name is not None:
        update_values["metric_name"] = payload.metric_name
    if payload.operator is not None:
        update_values["operator"] = payload.operator
    if payload.threshold is not None:
        update_values["threshold"] = payload.threshold
    if payload.severity is not None:
        update_values["severity"] = payload.severity
    if payload.cooldown_minutes is not None:
        update_values["cooldown_minutes"] = payload.cooldown_minutes
    if payload.notification_channels is not None:
        update_values["notification_channels"] = payload.notification_channels
    if payload.silence_start is not None:
        update_values["silence_start"] = _parse_time(payload.silence_start) if payload.silence_start else None
    if payload.silence_end is not None:
        update_values["silence_end"] = _parse_time(payload.silence_end) if payload.silence_end else None

    if update_values:
        stmt = (
            update(AlertRule)
            .where(AlertRule.id == rule_id)
            .values(**update_values)
        )
        try:
            await db.execute(stmt)
            await db.flush()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"更新告警规则失败: {str(e)}"
            )

    await db.refresh(rule)

    def _fmt(t: Optional[time]) -> Optional[str]:
        if t is None:
            return None
        return t.strftime("%H:%M")

    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        enabled=rule.enabled,
        metric_category=rule.metric_category,
        metric_name=rule.metric_name,
        operator=rule.operator,
        threshold=rule.threshold,
        severity=rule.severity,
        cooldown_minutes=rule.cooldown_minutes,
        notification_channels=rule.notification_channels,
        silence_start=_fmt(rule.silence_start),
        silence_end=_fmt(rule.silence_end),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.delete(
    "/{rule_id}",
    summary="删除告警规则",
)
async def delete_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """删除指定的告警规则。"""
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")

    try:
        await db.delete(rule)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"删除告警规则失败: {str(e)}"
        )

    return {"message": "告警规则已删除", "rule_id": rule_id}


@router.put(
    "/{rule_id}/toggle",
    response_model=AlertRuleResponse,
    summary="启用/禁用告警规则",
)
async def toggle_alert_rule(
    rule_id: int,
    payload: ToggleRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AlertRuleResponse:
    """切换告警规则的启用/禁用状态。"""
    rule = await db.get(AlertRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="告警规则不存在")

    stmt = (
        update(AlertRule)
        .where(AlertRule.id == rule_id)
        .values(enabled=payload.enabled)
    )
    try:
        await db.execute(stmt)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"切换告警规则状态失败: {str(e)}"
        )

    await db.refresh(rule)

    def _fmt(t: Optional[time]) -> Optional[str]:
        if t is None:
            return None
        return t.strftime("%H:%M")

    return AlertRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        enabled=rule.enabled,
        metric_category=rule.metric_category,
        metric_name=rule.metric_name,
        operator=rule.operator,
        threshold=rule.threshold,
        severity=rule.severity,
        cooldown_minutes=rule.cooldown_minutes,
        notification_channels=rule.notification_channels,
        silence_start=_fmt(rule.silence_start),
        silence_end=_fmt(rule.silence_end),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )
