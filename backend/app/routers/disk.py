"""
磁盘空间监控 API 路由
提供各数据库磁盘空间使用情况查询。
数据来源：disk_space_records 表。
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.disk import DiskSpaceRecord
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


class DiskSpaceItem(BaseModel):
    """磁盘空间记录单项（与前端 Disk.vue 字段匹配）"""

    database_name: str
    data_file_mb: float
    log_file_mb: float
    total_size_mb: float
    used_mb: float
    free_mb: float
    usage_pct: float
    collected_at: datetime
    server_address: str

    model_config = {"from_attributes": True}


class DiskSpaceResponse(BaseModel):
    """磁盘空间响应（包含采集时间）"""

    items: List[DiskSpaceItem]
    collected_at: Optional[datetime] = None


@router.get(
    "/space",
    response_model=DiskSpaceResponse,
    summary="获取磁盘空间使用情况",
)
async def get_disk_space(
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DiskSpaceResponse:
    """查询各数据库的磁盘空间使用情况（返回最近一次采集的快照）。"""
    try:
        latest_time_subq = (
            select(func.max(DiskSpaceRecord.collected_at))
            .select_from(DiskSpaceRecord)
            .scalar_subquery()
        )
        stmt = select(DiskSpaceRecord).where(
            DiskSpaceRecord.collected_at == latest_time_subq
        )
        if server_address:
            stmt = stmt.where(DiskSpaceRecord.server_address == server_address)

        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询磁盘空间记录失败: {str(e)}"
        )

    if not records:
        return DiskSpaceResponse(items=[], collected_at=None)

    collected_at = records[0].collected_at
    items = [
        DiskSpaceItem(
            database_name=r.database_name,
            data_file_mb=r.data_file_mb,
            log_file_mb=r.log_file_mb,
            total_size_mb=r.total_mb,
            used_mb=r.used_mb,
            free_mb=r.free_mb,
            usage_pct=r.usage_pct,
            collected_at=r.collected_at,
            server_address=r.server_address,
        )
        for r in records
    ]
    return DiskSpaceResponse(items=items, collected_at=collected_at)
