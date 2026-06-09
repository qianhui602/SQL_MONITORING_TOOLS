"""
告警模型
存储系统自动触发的各类告警记录，包括告警类型、严重级别和处理状态。
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AlertLog(Base):
    """告警日志

    记录系统触发的告警信息，支持分级告警和确认/通知状态跟踪。
    """

    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="告警类型：cpu_high / deadlock / connection_exceed 等"
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        comment="严重级别：low / medium / high / critical",
    )
    message: Mapped[str] = mapped_column(
        Text, nullable=False, comment="告警消息正文"
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="告警触发时间"
    )
    acknowledged: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否已确认"
    )
    acknowledged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="确认时间"
    )
    notification_sent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="通知是否已发送"
    )

    # ---------- 审计字段 ----------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )

    def __repr__(self) -> str:
        return (
            f"<AlertLog id={self.id} type={self.alert_type} "
            f"severity={self.severity} acknowledged={self.acknowledged}>"
        )
