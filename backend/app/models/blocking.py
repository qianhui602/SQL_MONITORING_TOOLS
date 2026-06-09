"""
阻塞事件模型
存储从 SQL Server 采集的阻塞链事件记录。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BlockingEvent(Base):
    """阻塞事件记录

    记录单次采集的阻塞链信息，包括被阻塞会话、阻塞源会话、
    等待类型、等待时间以及双方的 SQL 文本。
    """

    __tablename__ = "blocking_events"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    blocked_spid: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="被阻塞的会话 SPID"
    )
    blocking_spid: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="阻塞源会话 SPID"
    )
    wait_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="", comment="等待类型"
    )
    wait_time_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="等待时间（毫秒）"
    )
    blocked_sql: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="被阻塞会话当前执行的 SQL"
    )
    blocking_sql: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="阻塞源会话当前执行的 SQL"
    )
    blocked_db: Mapped[str] = mapped_column(
        String(100), nullable=True, default=None, comment="被阻塞会话所在的数据库"
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="采集时间"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="被监控的 SQL Server 地址"
    )

    # ---------- 审计字段 ----------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )

    def __repr__(self) -> str:
        return (
            f"<BlockingEvent id={self.id} blocked={self.blocked_spid} "
            f"blocking={self.blocking_spid} wait_type={self.wait_type} "
            f"server={self.server_address} at={self.collected_at}>"
        )
