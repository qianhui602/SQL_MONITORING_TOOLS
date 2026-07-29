"""AI 任务工具模块

提供真实数据查询工具，每个步骤先执行工具获取实际监控数据，
再交给 AI 分析，实现"用户提问 → AI 拆解 → 调用工具 → 分析数据 → 给出结果"。
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.performance import MetricRecord
from app.models.deadlock import DeadlockEvent, DeadlockSql
from app.models.slow_query import SlowQueryRecord
from app.models.blocking import BlockingEvent
from app.models.disk import DiskSpaceRecord
from app.models.index_analysis import MissingIndex, IndexFragmentation

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 工具注册表
# ---------------------------------------------------------------------------

TOOL_REGISTRY: Dict[str, str] = {
    "metrics": "查询最新性能指标（CPU、内存、连接数、缓存命中率等）",
    "deadlock": "查询近期死锁事件详情",
    "slow_query": "查询最新慢查询记录",
    "disk": "查询磁盘空间使用情况",
    "index": "查询索引缺失与碎片分析",
    "blocking": "查询当前阻塞链事件",
    "summary": "综合所有检查结果生成报告",
}


async def execute_tool(db: AsyncSession, step_type: str) -> Optional[str]:
    """根据步骤类型执行对应的数据查询工具，返回格式化文本"""
    tool_map = {
        "metrics": _query_metrics,
        "deadlock": _query_deadlocks,
        "slow_query": _query_slow_queries,
        "disk": _query_disk,
        "index": _query_indexes,
        "blocking": _query_blocking,
    }
    fn = tool_map.get(step_type)
    if not fn:
        return None
    try:
        return await fn(db)
    except Exception as e:
        logger.warning("工具执行失败 [%s]: %s", step_type, e)
        return f"[工具执行异常: {str(e)}]"


# ---------------------------------------------------------------------------
# 工具实现
# ---------------------------------------------------------------------------


async def _query_metrics(db: AsyncSession) -> str:
    """工具: 查询最新性能指标"""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
    stmt = (
        select(MetricRecord)
        .where(MetricRecord.collected_at >= cutoff)
        .order_by(desc(MetricRecord.collected_at))
        .limit(200)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return "【性能指标】最近 5 分钟内无采集数据。"

    # 按 metric_name 取最新值
    latest: Dict[str, float] = {}
    server_address = ""
    for r in records:
        if r.metric_name not in latest:
            latest[r.metric_name] = r.metric_value
        if not server_address:
            server_address = r.server_address

    lines = [f"【性能指标】服务器: {server_address}"]
    metric_labels = {
        "cpu_usage": "CPU 使用率",
        "sql_server_memory_mb": "SQL Server 内存 (MB)",
        "active_sessions": "活跃会话数",
        "buffer_cache_hit_ratio": "缓存命中率",
        "lock_waits": "锁等待数",
        "batch_requests_sec": "批处理请求/秒",
        "memory_usage_pct": "内存使用率",
        "page_life_expectancy": "页预期寿命 (秒)",
        "sql_compilations_sec": "SQL 编译数/秒",
        "sql_recompilations_sec": "SQL 重编译数/秒",
    }
    for key, label in metric_labels.items():
        if key in latest:
            val = latest[key]
            if isinstance(val, float):
                lines.append(f"  - {label}: {val:.2f}")
            else:
                lines.append(f"  - {label}: {val}")

    return "\n".join(lines)


async def _query_deadlocks(db: AsyncSession) -> str:
    """工具: 查询近期死锁事件"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    stmt = (
        select(DeadlockEvent)
        .where(DeadlockEvent.occur_at >= cutoff)
        .order_by(desc(DeadlockEvent.occur_at))
        .limit(10)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    if not events:
        return "【死锁事件】过去 24 小时内无死锁记录。"

    lines = [f"【死锁事件】过去 24 小时共 {len(events)} 次:"]
    for ev in events:
        lines.append(f"  - 时间: {ev.occur_at}")
        lines.append(f"    受害会话: {ev.victim_session_id}")
        lines.append(f"    服务器: {ev.server_address}")
        if ev.login_name:
            lines.append(f"    登录名: {ev.login_name}")
        if ev.host_name:
            lines.append(f"    主机名: {ev.host_name}")

        # 查询关联 SQL
        sql_stmt = select(DeadlockSql).where(
            DeadlockSql.deadlock_id == ev.id
        )
        sql_result = await db.execute(sql_stmt)
        sqls = sql_result.scalars().all()
        for s in sqls[:3]:  # 最多展示 3 条
            if s.sql_text:
                lines.append(f"    SQL[{s.session_id}]: {s.sql_text[:200]}")

    return "\n".join(lines)


async def _query_slow_queries(db: AsyncSession) -> str:
    """工具: 查询慢查询记录"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    stmt = (
        select(SlowQueryRecord)
        .where(SlowQueryRecord.collected_at >= cutoff)
        .order_by(desc(SlowQueryRecord.total_elapsed_ms))
        .limit(10)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    if not records:
        return "【慢查询】过去 24 小时内无慢查询记录。"

    lines = [f"【慢查询】TOP {len(records)}（按总耗时排序）:"]
    for r in records:
        lines.append(f"  - 执行次数: {r.execution_count}")
        lines.append(f"    总耗时: {r.total_elapsed_ms:.0f} ms")
        lines.append(f"    平均耗时: {r.avg_elapsed_ms:.0f} ms")
        lines.append(f"    总 CPU: {r.total_cpu_ms:.0f} ms")
        lines.append(f"    逻辑读: {r.total_logical_reads}")
        lines.append(f"    SQL: {r.sql_text[:300]}")
        lines.append("")

    return "\n".join(lines)


async def _query_disk(db: AsyncSession) -> str:
    """工具: 查询磁盘空间使用情况"""
    # 获取最近一次采集时间
    max_time_stmt = select(func.max(DiskSpaceRecord.collected_at))
    max_result = await db.execute(max_time_stmt)
    max_time = max_result.scalar()
    if not max_time:
        return "【磁盘空间】无磁盘数据。"

    stmt = (
        select(DiskSpaceRecord)
        .where(DiskSpaceRecord.collected_at == max_time)
        .order_by(desc(DiskSpaceRecord.usage_pct))
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    lines = [f"【磁盘空间】采集时间: {max_time}，共 {len(records)} 个数据库:"]
    for r in records:
        lines.append(
            f"  - {r.database_name}: "
            f"总 {r.total_mb:.0f} MB, "
            f"已用 {r.used_mb:.0f} MB, "
            f"空闲 {r.free_mb:.0f} MB, "
            f"使用率 {r.usage_pct:.1f}%"
        )

    return "\n".join(lines)


async def _query_indexes(db: AsyncSession) -> str:
    """工具: 查询索引缺失和碎片分析"""
    parts = []

    # 缺失索引
    try:
        stmt = (
            select(MissingIndex)
            .order_by(desc(MissingIndex.estimated_impact))
            .limit(10)
        )
        result = await db.execute(stmt)
        missing = result.scalars().all()
        if missing:
            parts.append(f"【缺失索引】共 {len(missing)} 条建议:")
            for m in missing:
                parts.append(
                    f"  - 表: {m.table_name}, "
                    f"影响: {m.estimated_impact:.0f}, "
                    f"列: {m.missing_columns or 'N/A'}"
                )
        else:
            parts.append("【缺失索引】无缺失索引建议。")
    except Exception as e:
        parts.append(f"【缺失索引】查询异常: {e}")

    # 高碎片索引
    try:
        stmt = (
            select(IndexFragmentation)
            .where(IndexFragmentation.avg_fragmentation_pct > 30)
            .order_by(desc(IndexFragmentation.avg_fragmentation_pct))
            .limit(10)
        )
        result = await db.execute(stmt)
        frag = result.scalars().all()
        if frag:
            parts.append(f"【索引碎片】碎片率 > 30% 的索引共 {len(frag)} 个:")
            for f in frag:
                parts.append(
                    f"  - 表: {f.table_name}, 索引: {f.index_name}, "
                    f"碎片率: {f.avg_fragmentation_pct:.1f}%"
                )
        else:
            parts.append("【索引碎片】无高碎片索引。")
    except Exception as e:
        parts.append(f"【索引碎片】查询异常: {e}")

    return "\n".join(parts) if parts else "【索引分析】无可用数据。"


async def _query_blocking(db: AsyncSession) -> str:
    """工具: 查询当前阻塞链事件"""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    stmt = (
        select(BlockingEvent)
        .where(BlockingEvent.collected_at >= cutoff)
        .order_by(desc(BlockingEvent.wait_time_ms))
        .limit(20)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    if not events:
        return "【阻塞事件】最近 30 分钟内无阻塞记录。"

    lines = [f"【阻塞事件】最近 30 分钟共 {len(events)} 条（按等待时间降序）:"]
    for ev in events[:10]:
        lines.append(
            f"  - 被阻塞 SPID: {ev.blocked_spid}, "
            f"阻塞源 SPID: {ev.blocking_spid}, "
            f"等待类型: {ev.wait_type}, "
            f"等待时间: {ev.wait_time_ms} ms"
        )
        if ev.blocked_sql:
            lines.append(f"    被阻塞 SQL: {ev.blocked_sql[:200]}")
        if ev.blocking_sql:
            lines.append(f"    阻塞源 SQL: {ev.blocking_sql[:200]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 格式化工具结果供 AI 使用
# ---------------------------------------------------------------------------


def format_tool_result_for_ai(
    step_type: str, step_title: str, tool_output: str
) -> str:
    """将工具执行结果格式化为 AI 可理解的上下文"""
    if not tool_output:
        return ""
    return (
        f"## 工具执行结果: {step_title}\n"
        f"工具类型: {step_type}\n"
        f"{tool_output}\n"
    )
