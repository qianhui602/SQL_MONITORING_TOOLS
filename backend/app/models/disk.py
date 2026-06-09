from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DiskSpaceRecord(Base):
    __tablename__ = "disk_space_records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    database_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="数据库名称"
    )
    data_file_mb: Mapped[float] = mapped_column(
        Float, nullable=False, comment="数据文件大小(MB)"
    )
    log_file_mb: Mapped[float] = mapped_column(
        Float, nullable=False, comment="日志文件大小(MB)"
    )
    total_mb: Mapped[float] = mapped_column(
        Float, nullable=False, comment="总大小(MB)"
    )
    used_mb: Mapped[float] = mapped_column(
        Float, nullable=False, comment="已用空间(MB)"
    )
    free_mb: Mapped[float] = mapped_column(
        Float, nullable=False, comment="可用空间(MB)"
    )
    usage_pct: Mapped[float] = mapped_column(
        Float, nullable=False, comment="使用率(%)"
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, comment="采集时间"
    )
    server_address: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="服务器地址"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="记录创建时间"
    )

    def __repr__(self) -> str:
        return (
            f"<DiskSpaceRecord id={self.id} db={self.database_name} "
            f"total={self.total_mb}MB usage={self.usage_pct}% "
            f"server={self.server_address}>"
        )
