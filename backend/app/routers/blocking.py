"""
阻塞进程实时监控 API 路由
提供当前阻塞链信息和历史查询。
数据来源：blocking_events 表。
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.blocking import BlockingEvent
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


class BlockingChainItem(BaseModel):
    """阻塞链记录单项（与前端 Blocking.vue 字段匹配）"""

    database_name: Optional[str] = None
    blocking_spid: int
    blocked_spid: int
    blocking_wait_type: Optional[str] = None
    blocking_wait_time: Optional[int] = None
    blocking_host_name: Optional[str] = None
    blocking_login_name: Optional[str] = None
    host_name: Optional[str] = None
    login_name: Optional[str] = None
    blocking_sql: Optional[str] = None
    blocked_sql: Optional[str] = None
    wait_type: str
    wait_time: int
    collected_at: datetime
    server_address: str

    model_config = {"from_attributes": True}


@router.get(
    "/realtime",
    response_model=List[BlockingChainItem],
    summary="获取实时阻塞进程数据",
)
async def get_blocking_realtime(
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[BlockingChainItem]:
    """查询当前阻塞链信息（返回最近一次采集的快照）。"""
    try:
        latest_time_subq = (
            select(func.max(BlockingEvent.collected_at))
            .select_from(BlockingEvent)
            .scalar_subquery()
        )
        stmt = select(BlockingEvent).where(
            BlockingEvent.collected_at == latest_time_subq
        )
        if server_address:
            stmt = stmt.where(BlockingEvent.server_address == server_address)

        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询阻塞进程记录失败: {str(e)}"
        )

    return [
        BlockingChainItem(
            database_name=r.blocked_db,
            blocking_spid=r.blocking_spid,
            blocked_spid=r.blocked_spid,
            blocking_sql=r.blocking_sql,
            blocked_sql=r.blocked_sql,
            wait_type=r.wait_type,
            wait_time=r.wait_time_ms,
            collected_at=r.collected_at,
            server_address=r.server_address,
        )
        for r in records
    ]


class BlockingHistoryResponse(BaseModel):
    """阻塞历史响应"""

    items: List[BlockingChainItem]
    total: int


@router.get(
    "/history",
    response_model=BlockingHistoryResponse,
    summary="获取阻塞历史记录（分页）",
)
async def get_blocking_history(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BlockingHistoryResponse:
    """查询阻塞历史记录，支持分页和时间范围筛选。"""
    filters = []

    if start_time:
        filters.append(BlockingEvent.collected_at >= start_time)
    if end_time:
        filters.append(BlockingEvent.collected_at <= end_time)
    if server_address:
        filters.append(BlockingEvent.server_address == server_address)

    try:
        # 获取总数
        count_stmt = select(func.count(BlockingEvent.id)).where(*filters)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 获取分页数据
        stmt = (
            select(BlockingEvent)
            .where(*filters)
            .order_by(BlockingEvent.collected_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询阻塞历史记录失败: {str(e)}"
        )

    items = [
        BlockingChainItem(
            database_name=r.blocked_db,
            blocking_spid=r.blocking_spid,
            blocked_spid=r.blocked_spid,
            blocking_sql=r.blocking_sql,
            blocked_sql=r.blocked_sql,
            wait_type=r.wait_type,
            wait_time=r.wait_time_ms,
            collected_at=r.collected_at,
            server_address=r.server_address,
        )
        for r in records
    ]

    return BlockingHistoryResponse(items=items, total=total)
