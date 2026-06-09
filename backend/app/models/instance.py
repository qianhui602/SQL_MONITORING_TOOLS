"""
被监控 SQL Server 实例模型
支持多个 SQL Server 实例的独立监控配置。
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MonitoredInstance(Base):
    """被监控的 SQL Server 实例

    每个实例存储独立的连接信息，调度器根据 is_active 决定是否采集。
    """

    __tablename__ = "monitored_instances"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="实例名称，如生产环境"
    )
    host: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="SQL Server 主机地址"
    )
    port: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1433, comment="SQL Server 端口"
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="登录用户名"
    )
    password: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="登录密码"
    )
    database_name: Mapped[str] = mapped_column(
        String(100), nullable=False, default="master", comment="默认连接的数据库名"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用采集"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="实例描述/备注"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    def __repr__(self) -> str:
        return (
            f"<MonitoredInstance id={self.id} name={self.name!r} "
            f"host={self.host}:{self.port} active={self.is_active}>"
        )
