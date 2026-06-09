"""
自定义告警规则模型
支持用户自定义告警规则，包括阈值、操作符、严重级别、冷却期等配置。
"""

from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AlertRule(Base):
    """自定义告警规则

    用户可以定义针对特定性能指标的告警规则，
    支持多种比较操作符和通知渠道配置。
    """

    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="规则名称"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="规则描述"
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用"
    )
    metric_category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="指标分类，如 cpu / memory / connection"
    )
    metric_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="指标名称，如 cpu_usage / memory_usage_pct"
    )
    operator: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="比较操作符：gt / lt / gte / lte / eq"
    )
    threshold: Mapped[float] = mapped_column(
        Float, nullable=False, comment="告警阈值"
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", comment="严重级别：critical / high / medium / low"
    )
    cooldown_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, comment="冷却时间（分钟）"
    )
    notification_channels: Mapped[str] = mapped_column(
        String(200), nullable=True, default="email", comment="通知渠道：email,dingtalk,wecom，逗号分隔"
    )
    silence_start: Mapped[time] = mapped_column(
        Time, nullable=True, default=None, comment="静默开始时间"
    )
    silence_end: Mapped[time] = mapped_column(
        Time, nullable=True, default=None, comment="静默结束时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最后更新时间",
    )

    def __repr__(self) -> str:
        return (
            f"<AlertRule id={self.id} name={self.name} "
            f"metric={self.metric_name} operator={self.operator} "
            f"threshold={self.threshold} enabled={self.enabled}>"
        )
