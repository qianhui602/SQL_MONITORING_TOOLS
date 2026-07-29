"""
AI 诊断任务模型
存储用户发起的 AI 诊断任务及其状态信息。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AiTask(Base):
    """AI 诊断任务

    记录一次 AI 诊断任务的发起、执行和完成状态。
    """

    __tablename__ = "ai_tasks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="发起用户 ID",
    )
    query: Mapped[str] = mapped_column(
        Text, nullable=False, comment="用户诊断需求描述"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="任务状态：pending / planning / running / completed / failed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="任务创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最后更新时间",
    )

    # 关联的步骤
    steps: Mapped[list["AiTaskStep"]] = relationship(
        "AiTaskStep",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<AiTask id={self.id} user_id={self.user_id} "
            f"status={self.status} at={self.created_at}>"
        )


class AiTaskStep(Base):
    """AI 诊断任务步骤

    记录任务执行计划中的每个步骤及其执行状态和结果。
    """

    __tablename__ = "ai_task_steps"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的任务 ID",
    )
    step_order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="步骤执行顺序"
    )
    title: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="步骤标题"
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="步骤详细描述"
    )
    step_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="步骤类型：metrics / deadlock / slow_query / disk / index / summary",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="步骤状态：pending / running / completed / failed",
    )
    result: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="AI 分析结果"
    )
    error: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="错误信息"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="记录创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最后更新时间",
    )

    # 关联的任务
    task: Mapped["AiTask"] = relationship("AiTask", back_populates="steps")

    def __repr__(self) -> str:
        return (
            f"<AiTaskStep id={self.id} task_id={self.task_id} "
            f"order={self.step_order} type={self.step_type} "
            f"status={self.status}>"
        )
