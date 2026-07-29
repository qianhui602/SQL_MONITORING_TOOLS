"""AI 上下文构建服务

自动查询最新监控数据，为 AI 任务规划提供上下文。
"""

import logging

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.performance import MetricRecord
from app.models.deadlock import DeadlockEvent
from app.models.slow_query import SlowQueryRecord
from app.models.blocking import BlockingEvent
from app.models.disk import DiskSpaceRecord
from app.models.index_analysis import MissingIndex, IndexFragmentation

logger = logging.getLogger(__name__)


async def build_monitoring_context(db: AsyncSession) -> dict:
    """查询最新监控数据，构建系统上下文"""
    context = {}

    # 查询最新性能指标
    try:
        stmt = (
            select(MetricRecord)
            .order_by(desc(MetricRecord.collected_at))
            .limit(50)
        )
        result = await db.execute(stmt)
        metrics = result.scalars().all()

        # 按指标名分组，取最新值
        latest_metrics = {}
        for m in metrics:
            if m.metric_name not in latest_metrics:
                latest_metrics[m.metric_name] = m.metric_value

        context["metrics"] = latest_metrics
    except Exception as e:
        logger.warning("查询性能指标失败: %s", e)
        context["metrics"] = {}

    # 查询死锁统计
    try:
        stmt = select(func.count(DeadlockEvent.id))
        result = await db.execute(stmt)
        deadlock_count = result.scalar() or 0
        context["deadlock_count"] = deadlock_count
    except Exception as e:
        logger.warning("查询死锁统计失败: %s", e)
        context["deadlock_count"] = 0

    # 查询慢查询统计
    try:
        stmt = select(func.count(SlowQueryRecord.id))
        result = await db.execute(stmt)
        slow_query_count = result.scalar() or 0
        context["slow_query_count"] = slow_query_count
    except Exception as e:
        logger.warning("查询慢查询统计失败: %s", e)
        context["slow_query_count"] = 0

    # 查询阻塞事件统计
    try:
        stmt = select(func.count(BlockingEvent.id))
        result = await db.execute(stmt)
        blocking_count = result.scalar() or 0
        context["blocking_count"] = blocking_count
    except Exception as e:
        logger.warning("查询阻塞统计失败: %s", e)
        context["blocking_count"] = 0

    # 查询磁盘使用率
    try:
        stmt = (
            select(DiskSpaceRecord)
            .order_by(desc(DiskSpaceRecord.collected_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        disk = result.scalar_one_or_none()
        if disk:
            context["disk_usage_pct"] = disk.usage_pct
            context["disk_total_mb"] = disk.total_mb
            context["disk_used_mb"] = disk.used_mb
        else:
            context["disk_usage_pct"] = 0
    except Exception as e:
        logger.warning("查询磁盘数据失败: %s", e)
        context["disk_usage_pct"] = 0

    # 查询缺失索引统计
    try:
        stmt = select(func.count(MissingIndex.id))
        result = await db.execute(stmt)
        missing_index_count = result.scalar() or 0
        context["missing_index_count"] = missing_index_count
    except Exception as e:
        logger.warning("查询缺失索引失败: %s", e)
        context["missing_index_count"] = 0

    # 查询高碎片索引统计
    try:
        stmt = select(func.count(IndexFragmentation.id)).where(
            IndexFragmentation.avg_fragmentation_pct > 30
        )
        result = await db.execute(stmt)
        high_frag_count = result.scalar() or 0
        context["high_fragmentation_count"] = high_frag_count
    except Exception as e:
        logger.warning("查询索引碎片失败: %s", e)
        context["high_fragmentation_count"] = 0

    return context


def format_context_for_ai(context: dict) -> str:
    """将上下文格式化为 AI 可读的文本"""
    lines = ["## 当前系统状态"]

    metrics = context.get("metrics", {})
    if metrics:
        lines.append("### 性能指标")
        metric_names = {
            "cpu_usage": "CPU 使用率",
            "sql_server_memory_mb": "SQL Server 内存",
            "active_sessions": "活跃会话数",
            "buffer_cache_hit_ratio": "缓存命中率",
            "lock_waits": "锁等待数",
            "batch_requests_sec": "批处理请求/秒",
        }
        for key, label in metric_names.items():
            if key in metrics:
                lines.append(f"- {label}: {metrics[key]}")

    lines.append(f"\n### 告警与异常")
    lines.append(f"- 死锁事件数: {context.get('deadlock_count', 0)}")
    lines.append(f"- 慢查询数量: {context.get('slow_query_count', 0)}")
    lines.append(f"- 阻塞事件数: {context.get('blocking_count', 0)}")
    lines.append(f"- 缺失索引数: {context.get('missing_index_count', 0)}")
    lines.append(f"- 高碎片索引数: {context.get('high_fragmentation_count', 0)}")

    lines.append(f"\n### 磁盘状态")
    lines.append(f"- 使用率: {context.get('disk_usage_pct', 0)}%")
    if context.get("disk_total_mb"):
        lines.append(f"- 总大小: {context['disk_total_mb']} MB")
        lines.append(f"- 已用: {context.get('disk_used_mb', 0)} MB")

    return "\n".join(lines)
