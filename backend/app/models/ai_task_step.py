"""
AI 诊断任务步骤模型
存储任务的执行步骤及每个步骤的结果。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AiTaskStep(Base):
    """AI 诊断任务步骤"""
    __tablename__ = "ai_task_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False, index=True, comment="关联任务 ID"
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="步骤顺序号")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="步骤标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", comment="步骤描述")
    step_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="步骤类型: metrics / deadlock / slow_query / disk / index / summary"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="步骤状态: pending / running / completed / failed"
    )
    result: Mapped[str] = mapped_column(Text, nullable=True, default=None, comment="AI 分析结果")
    error: Mapped[str] = mapped_column(Text, nullable=True, default=None, comment="错误信息")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<AiTaskStep id={self.id} order={self.step_order} status={self.status}>"
