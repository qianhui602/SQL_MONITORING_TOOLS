"""AI 任务执行引擎

按计划逐步执行诊断任务，更新步骤状态。
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_task import AiTask, AiTaskStep
from app.services.ai_context import build_monitoring_context, format_context_for_ai
from app.services.deepseek import get_ai_config, plan_task, execute_step

logger = logging.getLogger(__name__)


async def create_task(db: AsyncSession, user_id: int, query: str) -> dict:
    """创建 AI 诊断任务：查询上下文 → AI 规划 → 保存步骤"""
    # 1. 构建监控上下文
    context = await build_monitoring_context(db)
    context_text = format_context_for_ai(context)

    # 2. 获取 AI 配置
    ai_config = await get_ai_config(db)

    # 3. AI 生成执行计划
    steps = await plan_task(
        user_query=query,
        context_text=context_text,
        api_key=ai_config["api_key"],
        model=ai_config["model"],
        base_url=ai_config.get("base_url", ""),
        provider=ai_config["provider"],
    )

    if not steps:
        # 如果 AI 规划失败，使用默认计划
        steps = [
            {"title": "检查性能指标", "description": "查询 CPU、内存、连接数等核心指标", "step_type": "metrics", "step_order": 1},
            {"title": "分析死锁事件", "description": "查询近期死锁事件", "step_type": "deadlock", "step_order": 2},
            {"title": "检查慢查询", "description": "分析慢查询趋势", "step_type": "slow_query", "step_order": 3},
            {"title": "检查磁盘空间", "description": "评估存储健康状况", "step_type": "disk", "step_order": 4},
            {"title": "综合分析报告", "description": "生成诊断报告", "step_type": "summary", "step_order": 5},
        ]

    # 4. 创建任务记录
    task = AiTask(user_id=user_id, query=query, status="planning")
    db.add(task)
    await db.flush()

    # 5. 创建步骤记录
    for step_data in steps:
        step = AiTaskStep(
            task_id=task.id,
            step_order=step_data["step_order"],
            title=step_data["title"],
            description=step_data.get("description", ""),
            step_type=step_data["step_type"],
            status="pending",
        )
        db.add(step)

    await db.commit()
    await db.refresh(task)

    return {
        "task_id": task.id,
        "status": task.status,
        "steps": [
            {
                "id": s.id,
                "step_order": s.step_order,
                "title": s.title,
                "description": s.description,
                "step_type": s.step_type,
                "status": s.status,
            }
            for s in (await db.execute(
                select(AiTaskStep).where(AiTaskStep.task_id == task.id).order_by(AiTaskStep.step_order)
            )).scalars().all()
        ],
    }


async def execute_task(db: AsyncSession, task_id: int) -> None:
    """逐步执行任务的所有步骤"""
    # 更新任务状态
    task = await db.get(AiTask, task_id)
    if not task:
        return

    task.status = "running"
    await db.commit()

    # 查询上下文
    context = await build_monitoring_context(db)
    context_text = format_context_for_ai(context)

    # 获取 AI 配置
    ai_config = await get_ai_config(db)

    # 查询步骤
    stmt = (
        select(AiTaskStep)
        .where(AiTaskStep.task_id == task_id)
        .order_by(AiTaskStep.step_order)
    )
    result = await db.execute(stmt)
    steps = result.scalars().all()

    try:
        for step in steps:
            step.status = "running"
            await db.commit()

            try:
                result = await execute_step(
                    step_type=step.step_type,
                    step_data={"title": step.title, "description": step.description},
                    context_text=context_text,
                    api_key=ai_config["api_key"],
                    model=ai_config["model"],
                    base_url=ai_config.get("base_url", ""),
                    provider=ai_config["provider"],
                )
                step.result = result
                step.status = "completed"
            except Exception as e:
                step.error = str(e)
                step.status = "failed"

            await db.commit()

        task.status = "completed"
    except Exception as e:
        logger.error("任务执行异常: %s", e)
        task.status = "failed"

    await db.commit()
