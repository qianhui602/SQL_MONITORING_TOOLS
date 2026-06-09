"""
审计日志模型
记录用户的关键操作，支持追溯和合规审计。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    """操作审计日志

    记录系统中所有写操作（创建、更新、删除）的详细信息，
    包括操作人、操作类型、资源、详情和 IP 地址。
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="操作用户名"
    )
    action: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="操作类型，如 CREATE / UPDATE / DELETE"
    )
    resource: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="操作资源，如 User / Config / AlertRule"
    )
    detail: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="操作详情"
    )
    ip_address: Mapped[str] = mapped_column(
        String(50), nullable=True, default=None, comment="客户端 IP 地址"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        comment="操作时间",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} user={self.username} "
            f"action={self.action} resource={self.resource}>"
        )
