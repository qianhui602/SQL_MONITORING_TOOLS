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
