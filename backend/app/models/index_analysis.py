"""
索引分析模型
存储从 SQL Server 采集的缺失索引建议和索引碎片信息。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MissingIndex(Base):
    """缺失索引建议

    记录 SQL Server 自动检测到的缺失索引建议，
    包含建议列信息和预估影响，用于指导索引优化。
    """

    __tablename__ = "missing_indexes"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    database_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="数据库名称"
    )
    schema_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="架构名称"
    )
    table_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="表名称"
    )
    equality_columns: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="等值查询列"
    )
    inequality_columns: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="不等值查询列"
    )
    included_columns: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="包含列"
    )
    avg_user_impact: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="预估用户影响百分比"
    )
    user_seeks: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="用户查找次数"
    )
    user_scans: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="用户扫描次数"
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="采集时间"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="被监控的 SQL Server 地址"
    )

    def __repr__(self) -> str:
        return (
            f"<MissingIndex id={self.id} table={self.schema_name}.{self.table_name} "
            f"impact={self.avg_user_impact}>"
        )


class IndexFragmentation(Base):
    """索引碎片信息

    记录索引碎片率、页数等指标，用于监控索引健康状况。
    碎片率过高 (>30%) 通常需要重建索引。
    """

    __tablename__ = "index_fragmentation"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    database_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="数据库名称"
    )
    schema_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="架构名称"
    )
    table_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="表名称"
    )
    index_name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="索引名称"
    )
    avg_fragmentation_pct: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="平均碎片率百分比"
    )
    page_count: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="索引页数"
    )
    index_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="索引类型：CLUSTERED / NONCLUSTERED"
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="采集时间"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="被监控的 SQL Server 地址"
    )

    def __repr__(self) -> str:
        return (
            f"<IndexFragmentation id={self.id} "
            f"index={self.index_name} frag={self.avg_fragmentation_pct}%>"
        )
