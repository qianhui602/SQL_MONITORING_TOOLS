"""
慢查询监控 API 路由
提供慢查询记录列表查询和统计信息，支持分页和时间范围筛选。
数据来源：slow_queries 表。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.slow_query import SlowQueryRecord
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


class SlowQueryItem(BaseModel):
    """慢查询记录单项（与前端 SlowQueries.vue 字段匹配）"""

    id: int
    query_text: str
    execution_count: int
    total_cpu_time_ms: float
    total_logical_reads: int
    avg_duration_ms: float
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    last_execution_time: Optional[datetime] = None
    collected_at: datetime
    database_name: Optional[str] = None

    model_config = {"from_attributes": True}


class SlowQueryResponse(BaseModel):
    """慢查询分页响应"""

    items: List[SlowQueryItem]
    total: int


@router.get(
    "",
    response_model=SlowQueryResponse,
    summary="获取慢查询记录列表（分页）",
)
async def get_slow_queries(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(
        None, description="按实例筛选"
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort_by: str = Query("total_elapsed_ms", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 asc/desc"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SlowQueryResponse:
    """查询慢查询记录，支持分页、时间范围筛选和排序。"""
    filters = []

    if start_time:
        filters.append(SlowQueryRecord.collected_at >= start_time)
    if end_time:
        filters.append(SlowQueryRecord.collected_at <= end_time)
    if server_address:
        filters.append(SlowQueryRecord.server_address == server_address)

    # 排序字段映射
    sort_field_map = {
        "execution_count": SlowQueryRecord.execution_count,
        "total_cpu_time_ms": SlowQueryRecord.total_cpu_ms,
        "total_logical_reads": SlowQueryRecord.total_logical_reads,
        "avg_duration_ms": SlowQueryRecord.avg_elapsed_ms,
        "last_execution_time": SlowQueryRecord.last_execution_time,
        "collected_at": SlowQueryRecord.collected_at,
        "total_elapsed_ms": SlowQueryRecord.total_elapsed_ms,
    }
    sort_col = sort_field_map.get(sort_by, SlowQueryRecord.total_elapsed_ms)
    if sort_order == "asc":
        order_clause = sort_col.asc()
    else:
        order_clause = sort_col.desc()

    try:
        count_stmt = select(func.count(SlowQueryRecord.id)).where(*filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SlowQueryRecord)
            .where(*filters)
            .order_by(order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询慢查询记录失败: {str(e)}"
        )

    items = [
        SlowQueryItem(
            id=r.id,
            query_text=r.sql_text,
            execution_count=r.execution_count,
            total_cpu_time_ms=r.total_cpu_ms,
            total_logical_reads=r.total_logical_reads,
            avg_duration_ms=r.avg_elapsed_ms,
            collected_at=r.collected_at,
            last_execution_time=r.last_execution_time,
        )
        for r in records
    ]

    return SlowQueryResponse(items=items, total=total)


class SlowQueryStats(BaseModel):
    """慢查询统计信息"""

    total_count: int
    total_cpu_time_ms: float
    avg_cpu_time_ms: float
    max_cpu_time_ms: float
    total_logical_reads: int
    avg_logical_reads: float
    avg_duration_ms: float
    max_duration_ms: float
    total_executions: int
    unique_queries: int


@router.get(
    "/stats",
    response_model=SlowQueryStats,
    summary="获取慢查询统计信息",
)
async def get_slow_query_stats(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SlowQueryStats:
    """获取慢查询的统计信息，包括总CPU时间、平均逻辑读等。"""
    filters = []

    if start_time:
        filters.append(SlowQueryRecord.collected_at >= start_time)
    if end_time:
        filters.append(SlowQueryRecord.collected_at <= end_time)
    if server_address:
        filters.append(SlowQueryRecord.server_address == server_address)

    try:
        stmt = select(
            func.count(SlowQueryRecord.id).label("total_count"),
            func.sum(SlowQueryRecord.total_cpu_ms).label("total_cpu_time_ms"),
            func.avg(SlowQueryRecord.total_cpu_ms).label("avg_cpu_time_ms"),
            func.max(SlowQueryRecord.total_cpu_ms).label("max_cpu_time_ms"),
            func.sum(SlowQueryRecord.total_logical_reads).label("total_logical_reads"),
            func.avg(SlowQueryRecord.total_logical_reads).label("avg_logical_reads"),
            func.avg(SlowQueryRecord.avg_elapsed_ms).label("avg_duration_ms"),
            func.max(SlowQueryRecord.avg_elapsed_ms).label("max_duration_ms"),
            func.sum(SlowQueryRecord.execution_count).label("total_executions"),
            func.count(func.distinct(SlowQueryRecord.sql_hash)).label("unique_queries"),
        ).where(*filters)

        result = await db.execute(stmt)
        row = result.one()

        return SlowQueryStats(
            total_count=row.total_count or 0,
            total_cpu_time_ms=float(row.total_cpu_time_ms or 0),
            avg_cpu_time_ms=float(row.avg_cpu_time_ms or 0),
            max_cpu_time_ms=float(row.max_cpu_time_ms or 0),
            total_logical_reads=row.total_logical_reads or 0,
            avg_logical_reads=float(row.avg_logical_reads or 0),
            avg_duration_ms=float(row.avg_duration_ms or 0),
            max_duration_ms=float(row.max_duration_ms or 0),
            total_executions=row.total_executions or 0,
            unique_queries=row.unique_queries or 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询慢查询统计信息失败: {str(e)}"
        )
