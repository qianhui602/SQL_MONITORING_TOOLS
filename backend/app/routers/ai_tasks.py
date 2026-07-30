"""
AI 诊断任务路由
提供任务创建、查询、删除接口。
"""

import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, get_db
from app.models.ai_task import AiTask, AiTaskStep
from app.models.user import User
from app.services.ai_executor import create_task, execute_task, execute_followup
from app.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class TaskCreateRequest(BaseModel):
    """创建任务请求体"""

    query: str


class FollowUpRequest(BaseModel):
    """追加追问请求体"""

    query: str


class TaskStepResponse(BaseModel):
    """任务步骤响应"""

    id: int
    step_order: int
    title: str
    description: str
    step_type: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

    model_config = {"from_attributes": True}


class TaskCreateResponse(BaseModel):
    """任务创建响应"""

    task_id: int
    status: str
    steps: list


class TaskResponse(BaseModel):
    """任务详情响应"""

    id: int
    query: str
    status: str
    created_at: str
    steps: List[TaskStepResponse] = []


class TaskListItem(BaseModel):
    """任务列表项"""

    id: int
    query: str
    status: str
    created_at: str


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.post("/tasks", response_model=TaskCreateResponse, summary="创建 AI 诊断任务")
async def create_ai_task(
    req: TaskCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """创建 AI 诊断任务并异步执行"""
    result = await create_task(db, _.id, req.query)

    # 异步执行任务（不阻塞响应）
    asyncio.create_task(_run_task(result["task_id"]))

    return result


async def _run_task(task_id: int) -> None:
    """后台执行任务（使用独立的数据库会话）"""
    async with async_session_factory() as db:
        try:
            await execute_task(db, task_id)
        except Exception as e:
            logger.error("后台任务执行失败: task_id=%s, error=%s", task_id, e)


@router.get("/tasks", response_model=List[TaskListItem], summary="获取任务列表")
async def list_ai_tasks(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取当前用户的任务列表（最近 50 条）"""
    stmt = (
        select(AiTask)
        .where(AiTask.user_id == _.id)
        .order_by(desc(AiTask.created_at))
        .limit(50)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return [
        TaskListItem(
            id=t.id,
            query=t.query[:100],
            status=t.status,
            created_at=t.created_at.isoformat() if t.created_at else "",
        )
        for t in tasks
    ]


@router.get("/tasks/{task_id}", response_model=TaskResponse, summary="获取任务详情")
async def get_ai_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取任务详情（含执行步骤）"""
    task = await db.get(AiTask, task_id)
    if not task or task.user_id != _.id:
        raise HTTPException(status_code=404, detail="任务不存在")

    stmt = (
        select(AiTaskStep)
        .where(AiTaskStep.task_id == task_id)
        .order_by(AiTaskStep.step_order)
    )
    result = await db.execute(stmt)
    steps = result.scalars().all()

    return TaskResponse(
        id=task.id,
        query=task.query,
        status=task.status,
        created_at=task.created_at.isoformat() if task.created_at else "",
        steps=[
            TaskStepResponse(
                id=s.id,
                step_order=s.step_order,
                title=s.title,
                description=s.description,
                step_type=s.step_type,
                status=s.status,
                result=s.result,
                error=s.error,
            )
            for s in steps
        ],
    )


@router.post("/tasks/{task_id}/followup", response_model=TaskStepResponse, summary="追问")
async def followup_ai_task(
    task_id: int,
    req: FollowUpRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """在已完成的任务上追加追问，AI 基于上下文回答"""
    task = await db.get(AiTask, task_id)
    if not task or task.user_id != _.id:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取已有步骤（用于上下文）
    stmt = (
        select(AiTaskStep)
        .where(AiTaskStep.task_id == task_id)
        .order_by(AiTaskStep.step_order)
    )
    result = await db.execute(stmt)
    existing_steps = result.scalars().all()

    step_order = max((s.step_order for s in existing_steps), default=0) + 1

    # 创建 followup 步骤（先设为 running，异步执行）
    step = AiTaskStep(
        task_id=task_id,
        step_order=step_order,
        title=req.query[:200],
        description="",
        step_type="followup",
        status="running",
    )
    db.add(step)
    await db.commit()
    await db.refresh(step)

    # 异步执行
    asyncio.create_task(_run_followup(task_id, step.id, task.query, existing_steps, req.query))

    return TaskStepResponse(
        id=step.id,
        step_order=step.step_order,
        title=step.title,
        description=step.description or "",
        step_type=step.step_type,
        status=step.status,
        result=step.result,
        error=step.error,
    )


async def _run_followup(
    task_id: int,
    step_id: int,
    original_query: str,
    existing_steps: list,
    followup_query: str,
) -> None:
    """后台执行追问（使用独立的数据库会话）"""
    async with async_session_factory() as db:
        try:
            await execute_followup(db, task_id, step_id, original_query, existing_steps, followup_query)
        except Exception as e:
            logger.error("追问执行失败: task_id=%s, error=%s", task_id, e)
            # 标记步骤失败
            step = await db.get(AiTaskStep, step_id)
            if step:
                step.status = "failed"
                step.error = str(e)
                await db.commit()


@router.delete("/tasks/{task_id}", summary="删除任务")
async def delete_ai_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除任务及其所有步骤"""
    task = await db.get(AiTask, task_id)
    if not task or task.user_id != _.id:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 先删除关联步骤，再删除任务
    await db.execute(delete(AiTaskStep).where(AiTaskStep.task_id == task_id))
    await db.delete(task)
    await db.flush()

    return {"success": True}
