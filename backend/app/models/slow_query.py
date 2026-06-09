"""
慢查询模型
存储从 SQL Server 采集的慢查询记录（TOP 20 按总耗时排序）。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SlowQueryRecord(Base):
    """慢查询记录

    记录单次采集的慢查询信息，包含 SQL 文本、执行统计和耗时数据。
    """

    __tablename__ = "slow_queries"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    sql_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="SQL 文本 MD5 哈希，用于聚合去重"
    )
    sql_text: Mapped[str] = mapped_column(
        Text, nullable=False, comment="慢查询 SQL 文本"
    )
    execution_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="执行次数"
    )
    total_cpu_ms: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="总 CPU 时间（毫秒）"
    )
    total_logical_reads: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="总逻辑读取次数"
    )
    total_elapsed_ms: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="总耗时（毫秒）"
    )
    avg_elapsed_ms: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="平均耗时（毫秒）"
    )
    last_execution_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="最后执行时间"
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
            f"<SlowQueryRecord id={self.id} hash={self.sql_hash[:8]} "
            f"total_elapsed={self.total_elapsed_ms}ms "
            f"server={self.server_address} at={self.collected_at}>"
        )
