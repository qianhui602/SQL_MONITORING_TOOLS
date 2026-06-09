"""
系统配置模型
存储系统的 key-value 配置项，支持运行时动态读取和修改。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemConfig(Base):
    """系统配置

    使用键值对方式存储系统配置项，config_key 为唯一键。
    """

    __tablename__ = "system_configs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    config_key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True, comment="配置键名"
    )
    config_value: Mapped[str] = mapped_column(
        Text, nullable=False, comment="配置值"
    )
    description: Mapped[str] = mapped_column(
        String(500), nullable=True, default=None, comment="配置项说明"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最后更新时间",
    )

    def __repr__(self) -> str:
        return f"<SystemConfig id={self.id} key={self.config_key}>"
