"""
用户通知已读记录模型
记录每个用户对哪些告警通知已读，实现按用户过滤未读通知。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotificationRead(Base):
    """用户通知已读记录

    记录用户已确认/阅读过的告警通知，
    与 AlertLog 和 User 通过外键关联。
    """

    __tablename__ = "notification_reads"
    __table_args__ = (
        UniqueConstraint("user_id", "alert_id", name="uq_user_alert_read"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("alert_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<NotificationRead user_id={self.user_id} alert_id={self.alert_id}>"
