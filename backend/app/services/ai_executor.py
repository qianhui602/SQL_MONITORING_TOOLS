"""AI 任务执行引擎

实现完整的"用户提问 → AI 拆解 → 调用工具 → 分析数据 → 给出结果"工作流。
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_task import AiTask, AiTaskStep
from app.services.ai_tools import execute_tool, format_tool_result_for_ai
from app.services.ai_context import build_monitoring_context, format_context_for_ai
from app.services.deepseek import get_ai_config, plan_task, execute_step, chat_completion, get_base_url

logger = logging.getLogger(__name__)

# 聚合所有步骤的工具执行结果，供 summary 步骤使用
_all_tool_results: list[str] = []


def _clean_tool_results() -> None:
    global _all_tool_results
    _all_tool_results = []


def _record_tool_result(text: str) -> None:
    global _all_tool_results
    _all_tool_results.append(text)


def _get_accumulated_tool_results() -> str:
    if not _all_tool_results:
        return ""
    return "\n\n".join(_all_tool_results)


async def create_task(db: AsyncSession, user_id: int, query: str) -> dict:
    """创建 AI 诊断任务：查询上下文 → AI 规划 → 保存步骤"""
    _clean_tool_results()

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


async def execute_followup(
    db: AsyncSession,
    task_id: int,
    step_id: int,
    original_query: str,
    existing_steps: list,
    followup_query: str,
) -> None:
    """执行追问：基于任务历史上下文，回答用户的后续问题

    Args:
        db: 数据库会话
        task_id: 任务 ID
        step_id: 追问步骤 ID
        original_query: 原始任务查询
        existing_steps: 已有步骤列表
        followup_query: 追问内容
    """
    # 获取 AI 配置
    ai_config = await get_ai_config(db)
    if not ai_config.get("api_key"):
        step = await db.get(AiTaskStep, step_id)
        if step:
            step.status = "failed"
            step.error = "未配置 AI API Key"
            await db.commit()
        return

    # 构建对话历史
    messages = []

    # System prompt
    messages.append({
        "role": "system",
        "content": (
            "你是一位资深的 SQL Server 数据库性能优化专家。"
            "用户之前发起了一个数据库诊断任务，你已经给出了分析结果。"
            "现在用户有后续问题，请基于之前的分析上下文进行回答。"
            "请用中文回答，输出格式清晰，重点突出。"
        ),
    })

    # 原始任务
    messages.append({
        "role": "user",
        "content": f"我的原始需求：{original_query}",
    })

    # 历史步骤结果作为 assistant 回复
    for s in existing_steps:
        if s.status == "completed" and s.result:
            messages.append({
                "role": "assistant",
                "content": f"**{s.title}** 分析结果：\n\n{s.result}",
            })

    # 追问内容
    messages.append({
        "role": "user",
        "content": followup_query,
    })

    # 调用 AI
    url = ai_config.get("base_url", "") or get_base_url(ai_config.get("provider", "deepseek"))
    ai_result = await chat_completion(
        base_url=url,
        api_key=ai_config["api_key"],
        model=ai_config["model"],
        messages=messages,
    )

    # 更新步骤
    step = await db.get(AiTaskStep, step_id)
    if step:
        step.result = ai_result or "AI 未能生成回复"
        step.status = "completed"
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
    """逐步执行任务的所有步骤

    每个步骤的执行流程：
    1. 执行对应的数据查询工具 → 获取真实监控数据
    2. 将工具执行结果传递给 AI 进行分析
    3. 保存分析结果
    """
    _clean_tool_results()

    # 更新任务状态
    task = await db.get(AiTask, task_id)
    if not task:
        return

    task.status = "running"
    await db.commit()

    # 查询系统上下文（概览信息）
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
                # === 关键流程：先执行工具，再交给 AI ===

                # 1. 执行工具 → 获取真实监控数据
                tool_output = await execute_tool(db, step.step_type)

                # 2. 如果是 summary 类型，附加上所有之前步骤的结果
                step_tool_text = tool_output or ""
                if step.step_type == "summary":
                    accumulated = _get_accumulated_tool_results()
                    if accumulated:
                        step_tool_text = accumulated

                # 3. 格式化工具结果供 AI 使用
                tool_result_formatted = format_tool_result_for_ai(
                    step_type=step.step_type,
                    step_title=step.title,
                    tool_output=step_tool_text,
                )

                # 4. 调用 AI 分析（传入工具执行结果 + 系统上下文）
                ai_result = await execute_step(
                    step_type=step.step_type,
                    step_data={"title": step.title, "description": step.description},
                    context_text=context_text,
                    tool_result_text=tool_result_formatted,
                    api_key=ai_config["api_key"],
                    model=ai_config["model"],
                    base_url=ai_config.get("base_url", ""),
                    provider=ai_config["provider"],
                )

                # 5. 保存结果
                step.result = ai_result
                step.status = "completed"

                # 6. 记录工具执行结果供后续步骤使用
                if step.step_type != "summary" and tool_output:
                    _record_tool_result(
                        f"### 步骤 {step.step_order}: {step.title}\n"
                        f"工具执行结果:\n{tool_output}\n"
                        f"AI 分析结论:\n{ai_result or '无'}"
                    )

            except Exception as e:
                step.error = str(e)
                step.status = "failed"

            await db.commit()

        task.status = "completed"
    except Exception as e:
        logger.error("任务执行异常: %s", e)
        task.status = "failed"

    await db.commit()
