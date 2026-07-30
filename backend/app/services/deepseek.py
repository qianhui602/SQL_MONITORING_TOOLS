"""AI 分析服务

支持多种 AI 提供商（DeepSeek、OpenAI、Xiaomi MiMo、自定义），
所有提供商均使用 OpenAI 兼容的 /v1/chat/completions 接口。
支持从数据库配置中读取 API Key、模型和 Base URL。
"""

import logging
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import SystemConfig

logger = logging.getLogger(__name__)

# AI 提供商预设配置
AI_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "models": [
            {"id": "deepseek-v4-flash", "name": "DeepSeek-V4-Flash（快速）"},
            {"id": "deepseek-v4-pro", "name": "DeepSeek-V4-Pro（增强）"},
        ],
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com",
        "models": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini（快速）"},
            {"id": "gpt-4o", "name": "GPT-4o（增强）"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo（经济）"},
        ],
    },
    "xiaomi": {
        "name": "Xiaomi MiMo",
        "base_url": "https://api.xiaomi.com",
        "models": [
            {"id": "mimo-7b", "name": "MiMo-7B（轻量）"},
            {"id": "mimo-13b", "name": "MiMo-13B（标准）"},
        ],
    },
    "custom": {
        "name": "自定义（OpenAI 兼容）",
        "base_url": "",
        "models": [],
    },
}


async def get_ai_config(db: AsyncSession) -> dict:
    """从数据库读取 AI 配置（兼容旧的 deepseek_ 前缀配置）"""
    keys = [
        "ai_provider", "ai_api_key", "ai_model", "ai_base_url",
        "deepseek_api_key", "deepseek_model",
    ]
    config = {
        "provider": "deepseek",
        "api_key": "",
        "model": "deepseek-v4-flash",
        "base_url": "",
    }

    try:
        stmt = select(SystemConfig).where(
            SystemConfig.config_key.in_(keys)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()
        for row in rows:
            if row.config_key == "ai_provider":
                config["provider"] = row.config_value or "deepseek"
            elif row.config_key == "ai_api_key":
                config["api_key"] = row.config_value
            elif row.config_key == "ai_model":
                config["model"] = row.config_value
            elif row.config_key == "ai_base_url":
                config["base_url"] = row.config_value
            # 兼容旧配置
            elif row.config_key == "deepseek_api_key" and not config["api_key"]:
                config["api_key"] = row.config_value
            elif row.config_key == "deepseek_model" and not config["model"]:
                config["model"] = row.config_value

    except Exception as e:
        logger.warning("读取 AI 配置失败，使用默认值: %s", e)

    return config


def _get_base_url(provider: str, custom_base_url: str = "") -> str:
    """获取提供商的 API Base URL"""
    if provider == "custom":
        return custom_base_url.rstrip("/")
    preset = AI_PROVIDERS.get(provider, {})
    return preset.get("base_url", "https://api.deepseek.com")


def get_base_url(provider: str, custom_base_url: str = "") -> str:
    """获取提供商的 API Base URL（公共接口）"""
    return _get_base_url(provider, custom_base_url)


def _build_prompt(deadlock_info: dict) -> str:
    involve_parts = []
    for s in deadlock_info.get("sql_statements", []):
        sql = s.get("sql_text", "")[:500]
        obj = s.get("involved_objects", "")
        sess = s.get("session_id", "?")
        iso = s.get("isolation_level", "未知")
        line = f"【会话 {sess}】"
        if iso != "未知":
            line += f" 隔离级别: {iso}"
        if sql:
            line += f"\nSQL: {sql}"
        if obj:
            line += f"\n涉及对象: {obj}"
        involve_parts.append(line)

    prompt = f"""你是一个 SQL Server 数据库死锁分析专家。请分析以下死锁事件，给出专业、简洁的分析结果。

## 死锁事件信息
- 发生时间: {deadlock_info.get('occur_at', '未知')}
- 受害会话 ID: {deadlock_info.get('victim_session_id', '未知')}
- 服务器: {deadlock_info.get('server_address', '未知')}

## 参与的会话及 SQL
{chr(10).join(involve_parts) if involve_parts else "无详细会话信息"}

## 分析要求
请按以下格式输出分析结果（请使用中文）：

**死锁原因分析：** 分析导致死锁的根本原因，说明资源竞争的具体对象和锁模式。

**涉及资源：** 列出死锁涉及的具体表、索引等资源对象。

**优化建议：** 给出具体的优化建议来避免类似死锁再次发生，包括但不限于索引优化、SQL改写、事务调整等。

**影响评估：** 评估该死锁对业务的可能影响程度（高/中/低）并说明理由。"""
    return prompt


async def _call_ai_api(
    base_url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: float = 60.0,
) -> Optional[str]:
    """调用 OpenAI 兼容的 Chat Completions API"""
    if not api_key:
        return None

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
        )
        if resp.status_code != 200:
            logger.error("AI API error: %s %s", resp.status_code, resp.text)
            return None

        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return content.strip() if content else None


async def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    timeout: float = 120.0,
) -> Optional[str]:
    """调用 OpenAI 兼容的 Chat Completions API（多轮对话）

    Args:
        base_url: API 基础地址
        api_key: API 密钥
        model: 模型名称
        messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
        timeout: 超时时间（秒）
    """
    if not api_key or not messages:
        return None

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 2048,
            },
        )
        if resp.status_code != 200:
            logger.error("AI API error: %s %s", resp.status_code, resp.text)
            return None

        data = resp.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return content.strip() if content else None


async def analyze_deadlock(
    deadlock_info: dict,
    api_key: str = "",
    model: str = "deepseek-v4-flash",
    base_url: str = "",
    provider: str = "deepseek",
) -> Optional[str]:
    """分析死锁事件"""
    if not api_key:
        provider_name = AI_PROVIDERS.get(provider, {}).get("name", provider)
        return f"AI 分析失败：{provider_name} API Key 未配置，请在系统设置中填写。"

    url = base_url or _get_base_url(provider)
    try:
        prompt = _build_prompt(deadlock_info)
        result = await _call_ai_api(
            base_url=url,
            api_key=api_key,
            model=model,
            system_prompt="你是一位资深的 SQL Server 数据库性能优化专家，精通死锁分析、索引优化和事务调优。",
            user_prompt=prompt,
        )
        return result or "AI 分析返回为空"

    except httpx.TimeoutException:
        logger.error("AI API 请求超时")
        return "AI 分析请求超时，请稍后重试"
    except Exception as e:
        logger.exception("AI API 调用异常: %s", e)
        return f"AI 分析异常: {str(e)}"


def _build_report_prompt(report_data: dict) -> str:
    summary = report_data.get("summary", {})
    deadlocks = report_data.get("deadlocks", {})
    slow_queries = report_data.get("slow_queries", {})
    blocking = report_data.get("blocking", {})
    disk = report_data.get("disk", {})
    indexes = report_data.get("indexes", {})

    prompt = f"""你是一个 SQL Server 数据库性能优化专家。请根据以下监控数据，生成一份专业的性能分析报告。

## 系统概览
- CPU 使用率: {summary.get('cpu_usage', 'N/A')}%
- 内存使用量: {summary.get('sql_server_memory_mb', 'N/A')} MB
- 活跃连接数: {summary.get('active_sessions', 'N/A')}
- 缓存命中率: {summary.get('buffer_cache_hit_ratio', 'N/A')}%
- 页生命周期: {summary.get('page_life_expectancy', 'N/A')} 秒
- 锁等待数: {summary.get('lock_waits', 'N/A')}

## 死锁分析
- 死锁次数: {deadlocks.get('count', 0)}
- 最新死锁: {deadlocks.get('latest_time', '无')}

## 慢查询分析
- 慢查询数量: {slow_queries.get('count', 0)}
- 平均耗时: {slow_queries.get('avg_duration_ms', 0)} ms
- TOP 慢查询: {slow_queries.get('top_queries', '无数据')}

## 阻塞分析
- 阻塞事件数: {blocking.get('count', 0)}

## 磁盘状态
- 磁盘使用率: {disk.get('usage_pct', 'N/A')}%

## 索引分析
- 缺失索引数: {indexes.get('missing_count', 0)}
- 高碎片索引数: {indexes.get('high_fragmentation_count', 0)}

## 分析要求（请使用中文回答）
请按以下格式输出分析报告：

### 一、总体评估
对当前数据库的整体运行状况进行评估（健康/亚健康/需要关注）。

### 二、性能瓶颈分析
分析当前存在的性能瓶颈，分别从 CPU、内存、I/O、锁等方面说明。

### 三、存在的主要问题
指出需要重点关注的问题，如死锁、慢查询、索引缺失等。

### 四、优化建议
给出具体的可操作的优化建议，按优先级排序。

### 五、风险提示
指出可能影响业务稳定性的风险点。"""
    return prompt


async def analyze_report(
    report_data: dict,
    api_key: str = "",
    model: str = "deepseek-v4-flash",
    base_url: str = "",
    provider: str = "deepseek",
) -> Optional[str]:
    """使用 AI 生成报告分析建议"""
    if not api_key:
        provider_name = AI_PROVIDERS.get(provider, {}).get("name", provider)
        return f"AI 分析失败：{provider_name} API Key 未配置，请在系统设置中填写。"

    url = base_url or _get_base_url(provider)
    try:
        prompt = _build_report_prompt(report_data)
        result = await _call_ai_api(
            base_url=url,
            api_key=api_key,
            model=model,
            system_prompt="你是一位资深的 SQL Server 数据库性能优化专家，精通性能分析、索引优化和系统调优。",
            user_prompt=prompt,
        )
        return result or "报告分析返回为空"

    except httpx.TimeoutException:
        logger.error("AI 报告分析 API 请求超时")
        return "报告分析请求超时，请稍后重试"
    except Exception as e:
        logger.exception("AI 报告分析 API 调用异常: %s", e)
        return f"报告分析异常: {str(e)}"


async def plan_task(
    user_query: str,
    context_text: str,
    api_key: str = "",
    model: str = "deepseek-v4-flash",
    base_url: str = "",
    provider: str = "deepseek",
) -> Optional[list]:
    """根据用户需求和监控上下文，生成诊断任务执行计划（步骤列表）"""
    if not api_key:
        return None

    url = base_url or _get_base_url(provider)

    system_prompt = """你是一个 SQL Server 数据库诊断专家。根据用户的诊断需求和当前系统状态，生成一个诊断任务执行计划。

请以 JSON 数组格式返回执行计划，每个步骤包含以下字段：
- title: 步骤标题（简短描述）
- description: 步骤详细描述
- step_type: 步骤类型，必须是以下之一：metrics, deadlock, slow_query, disk, index, summary

示例格式：
[
  {"title": "检查性能指标", "description": "查询 CPU、内存、连接数等核心指标", "step_type": "metrics"},
  {"title": "分析死锁事件", "description": "查询近期死锁事件并分析原因", "step_type": "deadlock"},
  {"title": "综合分析报告", "description": "基于所有检查结果生成综合诊断报告", "step_type": "summary"}
]

注意：
1. 只返回 JSON 数组，不要包含其他文字
2. 根据用户需求选择相关的检查步骤
3. 最后一步通常是 summary（综合分析）
4. 步骤数量控制在 3-6 个"""

    try:
        result = await _call_ai_api(
            base_url=url,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt=f"{context_text}\n\n## 用户需求\n{user_query}",
            timeout=30.0,
        )
        if not result:
            return None

        # 解析 JSON 步骤列表
        import json
        import re

        # 尝试提取 JSON 数组
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            steps = json.loads(json_match.group())
            # 验证步骤格式
            valid_steps = []
            valid_types = {"metrics", "deadlock", "slow_query", "disk", "index", "summary"}
            for i, step in enumerate(steps):
                if isinstance(step, dict) and "title" in step and "step_type" in step:
                    if step["step_type"] in valid_types:
                        step["step_order"] = i + 1
                        step.setdefault("description", "")
                        valid_steps.append(step)
            return valid_steps if valid_steps else None

        return None
    except Exception as e:
        logger.error("AI 任务规划异常: %s", e)
        return None


async def execute_step(
    step_type: str,
    step_data: dict,
    context_text: str,
    tool_result_text: str = "",
    api_key: str = "",
    model: str = "deepseek-v4-flash",
    base_url: str = "",
    provider: str = "deepseek",
) -> Optional[str]:
    """执行单个诊断步骤，生成分析结果

    Args:
        step_type: 步骤类型
        step_data: 步骤元数据（标题、描述等）
        context_text: 系统上下文（概览信息）
        tool_result_text: 工具执行结果（真实监控数据）
        api_key: AI API 密钥
        model: AI 模型名称
        base_url: API 地址
        provider: 提供商名称
    """
    if not api_key:
        return None

    url = base_url or _get_base_url(provider)

    step_prompts = {
        "metrics": "你正在执行「性能指标检查」工具，已获取到最新的数据库性能指标数据。请根据这些实际数据进行分析：评估 CPU、内存、连接等关键指标的健康状况，指出异常项并给出优化建议。",
        "deadlock": "你正在执行「死锁分析」工具，已获取到近期死锁事件的详细记录。请分析死锁原因、涉及资源，给出具体的优化建议来避免类似死锁再次发生。",
        "slow_query": "你正在执行「慢查询分析」工具，已获取到 TOP 慢查询记录。请分析每条慢查询的性能瓶颈，给出索引优化、SQL 改写或结构调整建议。",
        "disk": "你正在执行「磁盘空间检查」工具，已获取到各数据库磁盘使用数据。请评估存储健康状况，对使用率高的数据库给出扩容或清理建议。",
        "index": "你正在执行「索引分析」工具，已获取到缺失索引建议和索引碎片数据。请分析索引策略，给出创建或维护索引的具体建议。",
        "blocking": "你正在执行「阻塞链分析」工具，已获取到实时阻塞事件数据。请分析阻塞原因和影响，给出优化建议来解决阻塞问题。",
        "summary": "请基于前面所有步骤的执行结果，生成一份完整的数据库健康诊断报告。包括总体评估、主要发现的问题、优化建议（按优先级排序）。",
    }

    system_prompt = f"""你是一位资深的 SQL Server 数据库性能优化专家。
{step_prompts.get(step_type, '请分析以下数据并给出专业建议。')}

请用中文回答，输出格式清晰，重点突出。"""

    # 构建用户提示词，优先使用工具执行结果
    user_prompt_parts = []
    if tool_result_text:
        user_prompt_parts.append(f"## 工具执行结果\n{tool_result_text}")
    if context_text:
        user_prompt_parts.append(f"## 系统概览\n{context_text}")
    user_prompt_parts.append(
        f"## 步骤详情\n标题: {step_data.get('title', '')}\n描述: {step_data.get('description', '')}"
    )

    try:
        result = await _call_ai_api(
            base_url=url,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt="\n\n".join(user_prompt_parts),
            timeout=120.0,
        )
        return result or "分析结果为空"
    except Exception as e:
        logger.error("步骤执行异常: %s", e)
        return f"执行异常: {str(e)}"


# 向后兼容：旧函数名映射
async def get_deepseek_config(db: AsyncSession) -> dict:
    """向后兼容：返回旧格式配置"""
    config = await get_ai_config(db)
    return {
        "api_key": config["api_key"],
        "model": config["model"],
        "base_url": config["base_url"],
        "provider": config["provider"],
    }
