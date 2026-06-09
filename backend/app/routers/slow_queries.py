"""
慢查询监控 API 路由
提供慢查询记录列表查询，支持分页和时间范围筛选。
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
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SlowQueryResponse:
    """查询慢查询记录，支持分页和时间范围筛选。"""
    filters = []

    if start_time:
        filters.append(SlowQueryRecord.collected_at >= start_time)
    if end_time:
        filters.append(SlowQueryRecord.collected_at <= end_time)
    if server_address:
        filters.append(SlowQueryRecord.server_address == server_address)

    try:
        count_stmt = select(func.count(SlowQueryRecord.id)).where(*filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(SlowQueryRecord)
            .where(*filters)
            .order_by(SlowQueryRecord.total_elapsed_ms.desc())
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
