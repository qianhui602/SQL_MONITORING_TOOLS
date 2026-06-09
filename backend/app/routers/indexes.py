"""
索引分析 API 路由
提供缺失索引建议和索引碎片列表查询，按 SQL Server 实例和时间范围筛选。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.index_analysis import IndexFragmentation, MissingIndex
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class MissingIndexItem(BaseModel):
    """缺失索引建议单项"""

    id: int
    database_name: str
    schema_name: str
    table_name: str
    equality_columns: Optional[str] = None
    inequality_columns: Optional[str] = None
    included_columns: Optional[str] = None
    avg_user_impact: float
    user_seeks: int
    user_scans: int
    collected_at: datetime
    server_address: str

    model_config = {"from_attributes": True}


class IndexFragmentationItem(BaseModel):
    """索引碎片记录单项"""

    id: int
    database_name: str
    schema_name: str
    table_name: str
    index_name: str
    avg_fragmentation_pct: float
    page_count: int
    index_type: str
    collected_at: datetime
    server_address: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/missing",
    response_model=List[MissingIndexItem],
    summary="获取缺失索引建议列表",
)
async def get_missing_indexes(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
    limit: int = Query(200, ge=1, le=5000, description="返回记录数上限"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[MissingIndexItem]:
    """查询缺失索引建议，支持按时间范围和实例筛选。"""
    conditions = []

    if start_time:
        conditions.append(MissingIndex.collected_at >= start_time)
    if end_time:
        conditions.append(MissingIndex.collected_at <= end_time)
    if server_address:
        conditions.append(MissingIndex.server_address == server_address)

    stmt = (
        select(MissingIndex)
        .where(*conditions)
        .order_by(MissingIndex.avg_user_impact.desc(), MissingIndex.collected_at.desc())
        .limit(limit)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询缺失索引建议失败: {str(e)}"
        )

    return [
        MissingIndexItem.model_validate(rec) for rec in records
    ]


@router.get(
    "/fragmentation",
    response_model=List[IndexFragmentationItem],
    summary="获取索引碎片列表",
)
async def get_index_fragmentation(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
    limit: int = Query(200, ge=1, le=5000, description="返回记录数上限"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[IndexFragmentationItem]:
    """查询索引碎片信息，支持按时间范围和实例筛选。"""
    conditions = []

    if start_time:
        conditions.append(IndexFragmentation.collected_at >= start_time)
    if end_time:
        conditions.append(IndexFragmentation.collected_at <= end_time)
    if server_address:
        conditions.append(IndexFragmentation.server_address == server_address)

    stmt = (
        select(IndexFragmentation)
        .where(*conditions)
        .order_by(IndexFragmentation.avg_fragmentation_pct.desc(), IndexFragmentation.collected_at.desc())
        .limit(limit)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询索引碎片信息失败: {str(e)}"
        )

    return [
        IndexFragmentationItem.model_validate(rec) for rec in records
    ]
