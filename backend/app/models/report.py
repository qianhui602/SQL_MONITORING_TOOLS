"""
报表记录模型
存储生成的报表元数据和 JSON 摘要数据。
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReportRecord(Base):
    """报表记录

    记录已生成的报表标题、时间范围、摘要数据及创建人等信息。
    """

    __tablename__ = "report_records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="报表标题"
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="报表开始时间"
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="报表结束时间"
    )
    summary_data: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="JSON 格式的摘要数据"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )
    created_by: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None, comment="创建人用户 ID"
    )

    def __repr__(self) -> str:
        return (
            f"<ReportRecord id={self.id} title={self.title!r} "
            f"start_time={self.start_time} end_time={self.end_time}>"
        )
