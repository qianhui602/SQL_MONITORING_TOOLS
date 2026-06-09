"""
死锁模型
存储从 SQL Server 捕获的死锁事件信息和相关会话 SQL 详情。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeadlockEvent(Base):
    """死锁事件

    记录一次死锁发生的时间、死锁 XML 内容、受害会话等信息。
    """

    __tablename__ = "deadlocks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    occur_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="死锁发生时间"
    )
    deadlock_xml: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="死锁图形 XML（系统_health 会话捕获的 xml_deadlock_report）"
    )
    victim_session_id: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None, comment="死锁受害者会话 ID"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="被监控的 SQL Server 地址"
    )
    analysis_result: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="DeepSeek AI 分析结果"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )

    # 关联的死锁 SQL 详情
    deadlock_sqls: Mapped[list["DeadlockSql"]] = relationship(
        "DeadlockSql",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<DeadlockEvent id={self.id} occur_at={self.occur_at} "
            f"victim={self.victim_session_id} server={self.server_address}>"
        )


class DeadlockSql(Base):
    """死锁涉及的 SQL 详情

    记录死锁事件中每个参与会话执行的 SQL 语句及相关上下文信息。
    """

    __tablename__ = "deadlock_sqls"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("deadlocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的死锁事件 ID",
    )
    session_id: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="参与死锁的会话 ID"
    )
    sql_text: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="会话当前执行的 SQL 语句"
    )
    isolation_level: Mapped[str] = mapped_column(
        String(50), nullable=True, default=None, comment="事务隔离级别"
    )
    involved_objects: Mapped[str] = mapped_column(
        String(500), nullable=True, default=None, comment="涉及的对象（表/索引等），逗号分隔"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )

    # 关联的死锁事件
    event: Mapped["DeadlockEvent"] = relationship(
        "DeadlockEvent", back_populates="deadlock_sqls"
    )

    def __repr__(self) -> str:
        return (
            f"<DeadlockSql id={self.id} event_id={self.event_id} "
            f"session_id={self.session_id}>"
        )
