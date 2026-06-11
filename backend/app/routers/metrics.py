"""
性能指标 API 路由
提供实时指标、历史趋势和概览摘要接口。
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func as sa_func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.performance import MetricRecord
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class MetricHistoryItem(BaseModel):
    """历史趋势数据单项"""

    collected_at: datetime
    metric_value: float
    metric_name: str

    model_config = {"from_attributes": True}


class RealtimeMetricsResponse(BaseModel):
    """实时指标数据响应"""

    cpu: Dict[str, float] = {}
    memory: Dict[str, float] = {}
    connection: Dict[str, float] = {}
    io: Dict[str, float] = {}
    server_address: str = ""

    model_config = {"from_attributes": True}


class SummaryMetricsResponse(BaseModel):
    """概览摘要响应"""

    cpu_usage: Optional[float] = None
    sql_server_memory_mb: Optional[float] = None
    active_sessions: Optional[int] = None
    buffer_cache_hit_ratio: Optional[float] = None
    memory_usage_pct: Optional[float] = None
    server_address: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/realtime",
    response_model=RealtimeMetricsResponse,
    summary="获取最新一批采集的指标数据",
)
async def get_realtime_metrics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
) -> RealtimeMetricsResponse:
    """查询最近 60 秒内的采集指标数据，按 category 分组返回。"""
    cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=60)

    conditions = [MetricRecord.collected_at >= cutoff_time]
    if server_address:
        conditions.append(MetricRecord.server_address == server_address)

    stmt = (
        select(MetricRecord)
        .where(*conditions)
        .order_by(MetricRecord.collected_at.desc())
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询实时指标数据失败: {str(e)}"
        )

    if not records:
        return RealtimeMetricsResponse()

    # 取最新一条记录的 server_address
    server_address = records[0].server_address

    # 按 category 分组，取每个 metric_name 的最新值
    grouped: Dict[str, Dict[str, float]] = {}
    latest: Dict[str, Dict[str, float]] = {}

    for record in records:
        cat = record.category
        if cat not in grouped:
            grouped[cat] = {}
        if record.metric_name not in grouped[cat]:
            grouped[cat][record.metric_name] = record.metric_value

    # 将分组结果映射到标准字段
    cpu_metrics = grouped.get("cpu", {})
    memory_metrics = grouped.get("memory", {})
    connection_metrics = grouped.get("connection", {})
    io_metrics = grouped.get("io", {})

    return RealtimeMetricsResponse(
        cpu=cpu_metrics,
        memory=memory_metrics,
        connection=connection_metrics,
        io=io_metrics,
        server_address=server_address,
    )


@router.get(
    "/history",
    response_model=List[MetricHistoryItem],
    summary="获取历史趋势数据",
)
async def get_metric_history(
    category: str = Query(..., description="指标分类，如 cpu / memory / connection / io"),
    metric_name: Optional[str] = Query(None, description="指标名称，可选筛选"),
    start_time: datetime = Query(..., description="起始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    limit: int = Query(1000, ge=1, le=10000, description="返回记录数上限"),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[MetricHistoryItem]:
    """按时间范围和分类查询历史指标数据，大数据范围自动均匀采样。"""
    from sqlalchemy import text

    base_conditions = [
        "category = :category",
        "collected_at >= :start_time",
        "collected_at <= :end_time",
    ]
    params: Dict[str, Any] = {
        "category": category,
        "start_time": start_time,
        "end_time": end_time,
        "limit": limit,
    }

    if metric_name:
        base_conditions.append("metric_name = :metric_name")
        params["metric_name"] = metric_name
    if server_address:
        base_conditions.append("server_address = :server_address")
        params["server_address"] = server_address

    where_clause = " AND ".join(base_conditions)

    stmt = text(f"""
        WITH base AS (
            SELECT collected_at, metric_value, metric_name,
                   ROW_NUMBER() OVER (ORDER BY collected_at ASC) AS rn,
                   COUNT(*) OVER () AS total
            FROM metrics
            WHERE {where_clause}
        )
        SELECT collected_at, metric_value, metric_name
        FROM base
        WHERE rn = 1 OR rn % GREATEST(CEIL(total::numeric / :limit), 1) = 1
        ORDER BY collected_at ASC
        LIMIT :limit
    """)

    try:
        result = await db.execute(stmt, params)
        rows = result.fetchall()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询历史指标数据失败: {str(e)}"
        )

    return [
        MetricHistoryItem(
            collected_at=row[0],
            metric_value=float(row[1]),
            metric_name=row[2],
        )
        for row in rows
    ]


@router.get(
    "/summary",
    response_model=SummaryMetricsResponse,
    summary="获取概览摘要",
)
async def get_metrics_summary(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
) -> SummaryMetricsResponse:
    """获取最近的关键性能指标汇总：CPU、内存、连接数、缓存命中率。"""
    # 使用子查询获取每个 metric_name 的最新记录
    subquery = (
        select(
            MetricRecord.metric_name,
            sa_func.max(MetricRecord.collected_at).label("max_collected_at"),
        )
        .group_by(MetricRecord.metric_name)
        .subquery()
    )

    where_conditions = [
        MetricRecord.metric_name.in_(
            [
                "cpu_usage",
                "sql_server_memory_mb",
                "buffer_cache_hit_ratio",
                "active_sessions",
                "memory_usage_pct",
            ]
        )
    ]
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
            status_code=500, detail=f"查询概览摘要数据失败: {str(e)}"
        )

    # 提取各指标值
    summary: Dict[str, Any] = {}
    server_address = None

    for record in records:
        summary[record.metric_name] = record.metric_value
        if server_address is None:
            server_address = record.server_address

    return SummaryMetricsResponse(
        cpu_usage=summary.get("cpu_usage"),
        sql_server_memory_mb=summary.get("sql_server_memory_mb"),
        active_sessions=int(summary["active_sessions"])
        if summary.get("active_sessions") is not None
        else None,
        buffer_cache_hit_ratio=summary.get("buffer_cache_hit_ratio"),
        memory_usage_pct=summary.get("memory_usage_pct"),
        server_address=server_address,
    )
