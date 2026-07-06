"""
报表 API 路由
提供报表数据聚合、保存、历史查询和删除接口。
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func as sa_func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, get_db
from app.models.performance import MetricRecord
from app.models.deadlock import DeadlockEvent
from app.models.slow_query import SlowQueryRecord
from app.models.blocking import BlockingEvent
from app.models.disk import DiskSpaceRecord
from app.models.index_analysis import MissingIndex, IndexFragmentation
from app.models.report import ReportRecord
from app.models.instance import MonitoredInstance
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.deepseek import analyze_report, get_deepseek_config


logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class SummarySection(BaseModel):
    """概览摘要"""

    cpu_usage: Optional[float] = None
    sql_server_memory_mb: Optional[float] = None
    active_sessions: Optional[int] = None
    buffer_cache_hit_ratio: Optional[float] = None
    page_life_expectancy: Optional[float] = None
    lock_waits: Optional[float] = None

    model_config = {"from_attributes": True}


class TrendItem(BaseModel):
    """趋势数据单项"""

    collected_at: datetime
    metric_value: float
    metric_name: str

    model_config = {"from_attributes": True}


class DeadlockInfo(BaseModel):
    """死锁信息"""

    total_count: int = 0
    latest_events: List[Dict[str, Any]] = []


class SlowQueryInfo(BaseModel):
    """慢查询信息"""

    total_count: int = 0
    avg_duration: float = 0.0
    top_queries: List[Dict[str, Any]] = []


class BlockingInfo(BaseModel):
    """阻塞信息"""

    total_count: int = 0


class IndexInfo(BaseModel):
    """索引信息"""

    missing_index_count: int = 0
    high_fragmentation_count: int = 0


class ReportSummaryResponse(BaseModel):
    """报表汇总响应"""

    summary: SummarySection = SummarySection()
    trends: Dict[str, List[TrendItem]] = {}
    deadlocks: DeadlockInfo = DeadlockInfo()
    slow_queries: SlowQueryInfo = SlowQueryInfo()
    blocking: BlockingInfo = BlockingInfo()
    disk: Optional[Dict[str, Any]] = None
    indexes: IndexInfo = IndexInfo()
    ai_analysis: str = ""


class SaveReportRequest(BaseModel):
    """保存报表请求"""

    title: str
    start_time: str
    end_time: str
    summary_data: str


class ReportRecordResponse(BaseModel):
    """报表记录响应"""

    id: int
    title: str
    start_time: datetime
    end_time: datetime
    summary_data: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DeleteReportResponse(BaseModel):
    """删除报表响应"""

    message: str


class ReportHistoryItem(BaseModel):
    """报表历史列表项（不含 summary_data 大字段）"""

    id: int
    title: str
    start_time: datetime
    end_time: datetime
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    model_config = {"from_attributes": True}


class PaginatedReportHistoryResponse(BaseModel):
    """分页报表历史响应"""

    items: List[ReportHistoryItem]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _parse_datetime(dt_str: str, field_name: str) -> datetime:
    """将 ISO 格式字符串解析为带 UTC 时区的 datetime 对象。"""
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} 格式无效: {str(e)}",
        )


async def _resolve_server_address(
    db: AsyncSession, instance_id: Optional[int]
) -> Optional[str]:
    """如果提供了 instance_id，则从 MonitoredInstance 中解析 server_address。"""
    if instance_id is None:
        return None
    stmt = select(MonitoredInstance).where(MonitoredInstance.id == instance_id)
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance is None:
        raise HTTPException(
            status_code=404, detail=f"实例 id={instance_id} 不存在"
        )
    return f"{instance.host}:{instance.port}"


async def _query_summary(
    db: AsyncSession, server_address: Optional[str]
) -> SummarySection:
    """查询最新关键性能指标。"""
    metric_names = [
        "cpu_usage",
        "sql_server_memory_mb",
        "active_sessions",
        "buffer_cache_hit_ratio",
        "page_life_expectancy",
        "lock_waits",
    ]

    subquery = (
        select(
            MetricRecord.metric_name,
            sa_func.max(MetricRecord.collected_at).label("max_collected_at"),
        )
        .where(MetricRecord.metric_name.in_(metric_names))
        .group_by(MetricRecord.metric_name)
        .subquery()
    )

    where_conditions = [MetricRecord.metric_name.in_(metric_names)]
    if server_address:
        where_conditions.append(MetricRecord.server_address == server_address)

    stmt = (
        select(MetricRecord)
        .join(
            subquery,
            and_(
                MetricRecord.metric_name == subquery.c.metric_name,
                MetricRecord.collected_at == subquery.c.max_collected_at,
            ),
        )
        .where(*where_conditions)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询概览摘要失败: {str(e)}"
        )

    summary: Dict[str, Any] = {}
    for record in records:
        summary[record.metric_name] = record.metric_value

    return SummarySection(
        cpu_usage=summary.get("cpu_usage"),
        sql_server_memory_mb=summary.get("sql_server_memory_mb"),
        active_sessions=int(summary["active_sessions"])
        if summary.get("active_sessions") is not None
        else None,
        buffer_cache_hit_ratio=summary.get("buffer_cache_hit_ratio"),
        page_life_expectancy=summary.get("page_life_expectancy"),
        lock_waits=summary.get("lock_waits"),
    )


async def _query_trends(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    server_address: Optional[str],
) -> Dict[str, List[TrendItem]]:
    """按分类查询历史趋势数据。"""
    categories = ["cpu", "memory", "connections", "io"]
    trends: Dict[str, List[TrendItem]] = {}

    for cat in categories:
        conditions = [
            MetricRecord.category == cat,
            MetricRecord.collected_at >= start_time,
            MetricRecord.collected_at <= end_time,
        ]
        if server_address:
            conditions.append(MetricRecord.server_address == server_address)

        stmt = (
            select(MetricRecord)
            .where(*conditions)
            .order_by(MetricRecord.collected_at.asc())
            .limit(2000)
        )

        try:
            result = await db.execute(stmt)
            records = result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"查询趋势数据({cat})失败: {str(e)}"
            )

        trends[cat] = [
            TrendItem(
                collected_at=record.collected_at,
                metric_value=record.metric_value,
                metric_name=record.metric_name,
            )
            for record in records
        ]

    return trends


async def _query_deadlocks(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    server_address: Optional[str],
) -> DeadlockInfo:
    """查询死锁统计和最新事件。"""
    conditions = [
        DeadlockEvent.occur_at >= start_time,
        DeadlockEvent.occur_at <= end_time,
    ]
    if server_address:
        conditions.append(DeadlockEvent.server_address == server_address)

    try:
        count_stmt = select(sa_func.count(DeadlockEvent.id)).where(*conditions)
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        latest_stmt = (
            select(DeadlockEvent)
            .where(*conditions)
            .order_by(DeadlockEvent.occur_at.desc())
            .limit(10)
        )
        latest_result = await db.execute(latest_stmt)
        latest_events = latest_result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁数据失败: {str(e)}"
        )

    return DeadlockInfo(
        total_count=total_count,
        latest_events=[
            {
                "id": ev.id,
                "occur_at": ev.occur_at.isoformat() if ev.occur_at else None,
                "victim_session_id": ev.victim_session_id,
                "server_address": ev.server_address,
            }
            for ev in latest_events
        ],
    )


async def _query_slow_queries(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    server_address: Optional[str],
) -> SlowQueryInfo:
    """查询慢查询统计和 TOP 10。"""
    conditions = [
        SlowQueryRecord.collected_at >= start_time,
        SlowQueryRecord.collected_at <= end_time,
    ]
    if server_address:
        conditions.append(SlowQueryRecord.server_address == server_address)

    try:
        count_stmt = select(sa_func.count(SlowQueryRecord.id)).where(*conditions)
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        avg_stmt = select(sa_func.avg(SlowQueryRecord.avg_elapsed_ms)).where(
            *conditions
        )
        avg_result = await db.execute(avg_stmt)
        avg_duration = avg_result.scalar() or 0.0

        top_stmt = (
            select(SlowQueryRecord)
            .where(*conditions)
            .order_by(SlowQueryRecord.avg_elapsed_ms.desc())
            .limit(10)
        )
        top_result = await db.execute(top_stmt)
        top_queries = top_result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询慢查询数据失败: {str(e)}"
        )

    return SlowQueryInfo(
        total_count=total_count,
        avg_duration=float(avg_duration),
        top_queries=[
            {
                "id": q.id,
                "sql_hash": q.sql_hash,
                "sql_text": q.sql_text[:500] if q.sql_text else "",
                "execution_count": q.execution_count,
                "avg_elapsed_ms": q.avg_elapsed_ms,
                "total_elapsed_ms": q.total_elapsed_ms,
                "collected_at": q.collected_at.isoformat()
                if q.collected_at
                else None,
            }
            for q in top_queries
        ],
    )


async def _query_blocking(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    server_address: Optional[str],
) -> BlockingInfo:
    """查询阻塞事件统计。"""
    conditions = [
        BlockingEvent.collected_at >= start_time,
        BlockingEvent.collected_at <= end_time,
    ]
    if server_address:
        conditions.append(BlockingEvent.server_address == server_address)

    try:
        count_stmt = select(sa_func.count(BlockingEvent.id)).where(*conditions)
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询阻塞数据失败: {str(e)}"
        )

    return BlockingInfo(total_count=total_count)


async def _query_disk(
    db: AsyncSession, server_address: Optional[str]
) -> Optional[Dict[str, Any]]:
    """查询最新的磁盘空间记录。"""
    conditions = []
    if server_address:
        conditions.append(DiskSpaceRecord.server_address == server_address)

    try:
        stmt = (
            select(DiskSpaceRecord)
            .where(*conditions)
            .order_by(DiskSpaceRecord.collected_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询磁盘数据失败: {str(e)}"
        )

    if record is None:
        return None

    return {
        "id": record.id,
        "database_name": record.database_name,
        "total_mb": record.total_mb,
        "used_mb": record.used_mb,
        "free_mb": record.free_mb,
        "usage_pct": record.usage_pct,
        "collected_at": record.collected_at.isoformat()
        if record.collected_at
        else None,
        "server_address": record.server_address,
    }


async def _query_indexes(
    db: AsyncSession, server_address: Optional[str]
) -> IndexInfo:
    """查询缺失索引数量和碎片率 > 30% 的索引数量。"""
    missing_conditions = []
    frag_conditions = [IndexFragmentation.avg_fragmentation_pct > 30]

    if server_address:
        missing_conditions.append(MissingIndex.server_address == server_address)
        frag_conditions.append(
            IndexFragmentation.server_address == server_address
        )

    try:
        missing_stmt = select(sa_func.count(MissingIndex.id)).where(
            *missing_conditions
        )
        missing_result = await db.execute(missing_stmt)
        missing_count = missing_result.scalar() or 0

        frag_stmt = select(sa_func.count(IndexFragmentation.id)).where(
            *frag_conditions
        )
        frag_result = await db.execute(frag_stmt)
        frag_count = frag_result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询索引数据失败: {str(e)}"
        )

    return IndexInfo(
        missing_index_count=missing_count,
        high_fragmentation_count=frag_count,
    )


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/summary",
    response_model=ReportSummaryResponse,
    summary="获取报表汇总数据",
)
async def get_report_summary(
    start_time: str = Query(..., description="起始时间（ISO 格式，如 2025-01-01T00:00:00）"),
    end_time: str = Query(..., description="结束时间（ISO 格式，如 2025-01-01T23:59:59）"),
    instance_id: Optional[int] = Query(None, description="实例 ID，可选筛选"),
    _: User = Depends(get_current_user),
) -> ReportSummaryResponse:
    """聚合多个模块的数据，生成指定时间范围内的报表汇总。"""
    start_dt = _parse_datetime(start_time, "start_time")
    end_dt = _parse_datetime(end_time, "end_time")

    # 使用独立 session 完成所有数据查询，查询结束后立即释放连接，
    # 避免 AI 分析期间长时间持有数据库连接。
    async with async_session_factory() as query_session:
        server_address = await _resolve_server_address(query_session, instance_id)
        summary = await _query_summary(query_session, server_address)
        trends = await _query_trends(query_session, start_dt, end_dt, server_address)
        deadlocks = await _query_deadlocks(query_session, start_dt, end_dt, server_address)
        slow_queries = await _query_slow_queries(
            query_session, start_dt, end_dt, server_address
        )
        blocking = await _query_blocking(query_session, start_dt, end_dt, server_address)
        disk = await _query_disk(query_session, server_address)
        indexes = await _query_indexes(query_session, server_address)
        # deepseek 配置也需要 db session，在查询阶段一并获取
        deepseek_config = await get_deepseek_config(query_session)

    # 数据查询完成后 session 已关闭，再调用 AI 分析（耗时操作不占用 db 连接）
    report_data_for_ai = {
        "summary": summary.model_dump(),
        "deadlocks": {
            "count": deadlocks.total_count,
            "latest_time": (
                deadlocks.latest_events[0]["occur_at"]
                if deadlocks.latest_events
                else None
            ),
        },
        "slow_queries": {
            "count": slow_queries.total_count,
            "avg_duration_ms": slow_queries.avg_duration,
            "top_queries": (
                [q["sql_text"][:200] for q in slow_queries.top_queries[:3]]
                if slow_queries.top_queries
                else []
            ),
        },
        "blocking": {"count": blocking.total_count},
        "disk": disk or {},
        "indexes": {
            "missing_count": indexes.missing_index_count,
            "high_fragmentation_count": indexes.high_fragmentation_count,
        },
    }

    ai_analysis = ""
    try:
        ai_result = await analyze_report(report_data_for_ai, **deepseek_config)
        if ai_result:
            ai_analysis = ai_result
    except Exception:
        logger.exception("AI report analysis failed")
        ai_analysis = "AI 分析暂时不可用"

    return ReportSummaryResponse(
        summary=summary,
        trends=trends,
        deadlocks=deadlocks,
        slow_queries=slow_queries,
        blocking=blocking,
        disk=disk,
        indexes=indexes,
        ai_analysis=ai_analysis,
    )


@router.post(
    "/save",
    response_model=ReportRecordResponse,
    summary="保存报表记录",
)
async def save_report(
    body: SaveReportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportRecordResponse:
    """保存一条报表记录到数据库。"""
    start_dt = _parse_datetime(body.start_time, "start_time")
    end_dt = _parse_datetime(body.end_time, "end_time")

    record = ReportRecord(
        title=body.title,
        start_time=start_dt,
        end_time=end_dt,
        summary_data=body.summary_data,
        created_by=user.id,
    )
    db.add(record)
    try:
        await db.commit()
        await db.refresh(record)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"保存报表失败: {str(e)}"
        )

    return ReportRecordResponse(
        id=record.id,
        title=record.title,
        start_time=record.start_time,
        end_time=record.end_time,
        summary_data=record.summary_data,
        created_at=record.created_at,
    )


@router.get(
    "/history",
    response_model=PaginatedReportHistoryResponse,
    summary="获取报表历史列表",
)
async def get_report_history(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大 100"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> PaginatedReportHistoryResponse:
    """分页获取已保存的报表记录列表（不返回 summary_data 大字段）。"""
    offset = (page - 1) * page_size

    try:
        # 查询总数
        count_stmt = select(sa_func.count()).select_from(ReportRecord)
        total = (await db.execute(count_stmt)).scalar() or 0

        # 查询列表（不加载 summary_data 大字段）
        stmt = (
            select(
                ReportRecord.id,
                ReportRecord.title,
                ReportRecord.start_time,
                ReportRecord.end_time,
                ReportRecord.created_at,
                ReportRecord.created_by,
            )
            .order_by(ReportRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        rows = result.all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询报表历史失败: {str(e)}"
        )

    items = [
        ReportHistoryItem(
            id=row.id,
            title=row.title,
            start_time=row.start_time,
            end_time=row.end_time,
            created_at=row.created_at,
            created_by=row.created_by,
        )
        for row in rows
    ]

    return PaginatedReportHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/history/{record_id}",
    response_model=DeleteReportResponse,
    summary="删除报表记录",
)
async def delete_report(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DeleteReportResponse:
    """根据 ID 删除一条报表记录。"""
    stmt = select(ReportRecord).where(ReportRecord.id == record_id)
    try:
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询报表记录失败: {str(e)}"
        )

    if record is None:
        raise HTTPException(
            status_code=404, detail=f"报表记录 id={record_id} 不存在"
        )

    try:
        await db.delete(record)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"删除报表记录失败: {str(e)}"
        )

    return DeleteReportResponse(message=f"报表记录 id={record_id} 已成功删除")
