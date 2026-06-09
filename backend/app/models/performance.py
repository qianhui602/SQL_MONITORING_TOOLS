"""
性能指标模型
存储从 SQL Server 采集的各类性能指标数据（CPU、内存、连接数、IO 等）。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MetricRecord(Base):
    """性能指标记录

    记录单次采集的性能指标数据，包含指标分类、名称、值和采集时间等信息。
    """

    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="指标分类：cpu / memory / connection / io"
    )
    metric_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="指标名称，如 cpu_usage_percent"
    )
    metric_value: Mapped[float] = mapped_column(
        Float, nullable=False, comment="指标数值"
    )
    unit: Mapped[str] = mapped_column(
        String(30), nullable=True, default=None, comment="单位，如 %、MB、count/s"
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="指标采集时间"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="被监控的 SQL Server 地址（IP 或主机名）"
    )

    # ---------- 审计字段 ----------
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )

    def __repr__(self) -> str:
        return (
            f"<MetricRecord id={self.id} category={self.category} "
            f"name={self.metric_name} value={self.metric_value} "
            f"server={self.server_address} at={self.collected_at}>"
        )
