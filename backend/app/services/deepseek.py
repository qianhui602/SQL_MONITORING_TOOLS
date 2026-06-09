"""DeepSeek AI 分析服务

支持从数据库配置中读取 API Key 和模型名称，
实现在系统设置界面动态修改。
"""

import json
import logging
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import SystemConfig

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


async def get_deepseek_config(db: AsyncSession) -> dict:
    """从数据库读取 DeepSeek 配置"""
    keys = ["deepseek_api_key", "deepseek_model"]
    config = {"api_key": "", "model": "deepseek-v4-flash"}

    try:
        stmt = select(SystemConfig).where(
            SystemConfig.config_key.in_(keys)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()
        for row in rows:
            if row.config_key == "deepseek_api_key":
                config["api_key"] = row.config_value
            elif row.config_key == "deepseek_model":
                config["model"] = row.config_value
    except Exception as e:
        logger.warning("读取 DeepSeek 配置失败，使用默认值: %s", e)

    return config


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


async def analyze_deadlock(
    deadlock_info: dict,
    api_key: str = "",
    model: str = "deepseek-v4-flash",
) -> Optional[str]:
    if not api_key:
        logger.error("DeepSeek API Key 未配置")
        return "AI 分析失败：DeepSeek API Key 未配置，请在系统设置中填写。"

    try:
        prompt = _build_prompt(deadlock_info)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位资深的 SQL Server 数据库性能优化专家，精通死锁分析、索引优化和事务调优。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048,
                },
            )
            if resp.status_code != 200:
                logger.error(
                    f"DeepSeek API error: {resp.status_code} {resp.text}"
                )
                return f"AI 分析调用失败 (HTTP {resp.status_code})"

            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return content.strip() if content else "AI 分析返回为空"

    except httpx.TimeoutException:
        logger.error("DeepSeek API 请求超时")
        return "AI 分析请求超时，请稍后重试"
    except Exception as e:
        logger.exception(f"DeepSeek API 调用异常: {e}")
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
) -> Optional[str]:
    """使用 DeepSeek AI 生成报告分析建议"""
    if not api_key:
        logger.error("DeepSeek API Key 未配置")
        return "AI 分析失败：DeepSeek API Key 未配置，请在系统设置中填写。"

    try:
        prompt = _build_report_prompt(report_data)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一位资深的 SQL Server 数据库性能优化专家，精通性能分析、索引优化和系统调优。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2048,
                },
            )
            if resp.status_code != 200:
                logger.error(f"DeepSeek API error: {resp.status_code} {resp.text}")
                return f"报告分析调用失败 (HTTP {resp.status_code})"

            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return content.strip() if content else "报告分析返回为空"

    except httpx.TimeoutException:
        logger.error("DeepSeek 报告分析 API 请求超时")
        return "报告分析请求超时，请稍后重试"
    except Exception as e:
        logger.exception(f"DeepSeek 报告分析 API 调用异常: {e}")
        return f"报告分析异常: {str(e)}"
