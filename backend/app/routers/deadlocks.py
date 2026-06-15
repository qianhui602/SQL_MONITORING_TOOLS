"""死锁事件 API 路由
提供死锁事件列表查询、详情查看和 AI 分析接口。
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.deadlock import DeadlockEvent, DeadlockSql
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.deepseek import analyze_deadlock, get_deepseek_config

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------


class DeadlockSqlItem(BaseModel):
    """死锁关联 SQL 单项"""

    session_id: int
    sql_text: Optional[str] = None
    isolation_level: Optional[str] = None
    involved_objects: Optional[str] = None
    login_name: Optional[str] = None
    host_name: Optional[str] = None
    client_app: Optional[str] = None

    model_config = {"from_attributes": True}


class DeadlockEventListItem(BaseModel):
    """死锁事件列表单项"""

    id: int
    occur_at: datetime
    victim_session_id: Optional[int] = None
    server_address: str
    login_name: Optional[str] = None
    host_name: Optional[str] = None
    client_app: Optional[str] = None

    model_config = {"from_attributes": True}


class DeadlockEventListResponse(BaseModel):
    """死锁事件列表分页响应"""

    items: List[DeadlockEventListItem]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}


class DeadlockEventDetailResponse(BaseModel):
    """死锁事件详情响应"""

    id: int
    occur_at: datetime
    deadlock_xml: Optional[str] = None
    victim_session_id: Optional[int] = None
    server_address: str
    analysis_result: Optional[str] = None
    sql_statements: List[DeadlockSqlItem] = []
    involved_objects: List[str] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=DeadlockEventListResponse,
    summary="获取死锁事件列表",
)
async def get_deadlock_events(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(
        None, description="按实例筛选（server_address），如 生产环境(10.0.0.1:1433)"
    ),
    login_name: Optional[str] = Query(None, description="按用户名筛选（模糊匹配）"),
    host_name: Optional[str] = Query(None, description="按主机名筛选（模糊匹配）"),
    client_app: Optional[str] = Query(None, description="按应用程序筛选（模糊匹配）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DeadlockEventListResponse:
    """分页查询死锁事件列表，支持按时间范围、实例、用户、主机、应用筛选。"""
    conditions = []

    if start_time:
        conditions.append(DeadlockEvent.occur_at >= start_time)
    if end_time:
        conditions.append(DeadlockEvent.occur_at <= end_time)
    if server_address:
        conditions.append(DeadlockEvent.server_address == server_address)
    if login_name:
        conditions.append(DeadlockEvent.login_name.ilike(f"%{login_name}%"))
    if host_name:
        conditions.append(DeadlockEvent.host_name.ilike(f"%{host_name}%"))
    if client_app:
        conditions.append(DeadlockEvent.client_app.ilike(f"%{client_app}%"))

    # 查询总数
    count_stmt = select(sa_func.count(DeadlockEvent.id)).where(*conditions)
    try:
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁事件总数失败: {str(e)}"
        )

    # 查询分页数据
    offset = (page - 1) * page_size
    query_stmt = (
        select(DeadlockEvent)
        .where(*conditions)
        .order_by(DeadlockEvent.occur_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    try:
        result = await db.execute(query_stmt)
        events = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁事件列表失败: {str(e)}"
        )

    items = [
        DeadlockEventListItem(
            id=event.id,
            occur_at=event.occur_at,
            victim_session_id=event.victim_session_id,
            server_address=event.server_address,
            login_name=event.login_name,
            host_name=event.host_name,
            client_app=event.client_app,
        )
        for event in events
    ]

    return DeadlockEventListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{event_id}",
    response_model=DeadlockEventDetailResponse,
    summary="获取死锁事件详情",
)
async def get_deadlock_event_detail(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DeadlockEventDetailResponse:
    """获取指定死锁事件的完整详情，包括关联的 SQL 语句列表。"""
    stmt = (
        select(DeadlockEvent)
        .where(DeadlockEvent.id == event_id)
        .options(selectinload(DeadlockEvent.deadlock_sqls))
    )

    try:
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁事件详情失败: {str(e)}"
        )

    if event is None:
        raise HTTPException(
            status_code=404, detail=f"死锁事件不存在: event_id={event_id}"
        )

    # 构建 SQL 语句列表
    sql_statements = [
        DeadlockSqlItem(
            session_id=sql.session_id,
            sql_text=sql.sql_text,
            isolation_level=sql.isolation_level,
            involved_objects=sql.involved_objects,
            login_name=sql.login_name,
            host_name=sql.host_name,
            client_app=sql.client_app,
        )
        for sql in (event.deadlock_sqls or [])
    ]

    # 收集所有涉及的对象（去重）
    involved_objects: List[str] = []
    seen_objects: set = set()
    for sql in event.deadlock_sqls or []:
        if sql.involved_objects:
            for obj in sql.involved_objects.split(","):
                obj = obj.strip()
                if obj and obj not in seen_objects:
                    seen_objects.add(obj)
                    involved_objects.append(obj)

    return DeadlockEventDetailResponse(
        id=event.id,
        occur_at=event.occur_at,
        deadlock_xml=event.deadlock_xml,
        victim_session_id=event.victim_session_id,
        server_address=event.server_address,
        analysis_result=event.analysis_result,
        sql_statements=sql_statements,
        involved_objects=involved_objects,
    )


@router.post(
    "/{event_id}/analyze",
    summary="DeepSeek AI 分析死锁事件",
)
async def analyze_deadlock_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """调用 DeepSeek 大模型分析死锁事件的原因、影响和优化建议。"""
    stmt = (
        select(DeadlockEvent)
        .where(DeadlockEvent.id == event_id)
        .options(selectinload(DeadlockEvent.deadlock_sqls))
    )
    try:
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁事件失败: {str(e)}"
        )

    if event is None:
        raise HTTPException(
            status_code=404, detail=f"死锁事件不存在: event_id={event_id}"
        )

    deadlock_info = {
        "occur_at": str(event.occur_at),
        "victim_session_id": event.victim_session_id,
        "server_address": event.server_address,
        "sql_statements": [
            {
                "session_id": sql.session_id,
                "sql_text": sql.sql_text,
                "isolation_level": sql.isolation_level,
                "involved_objects": sql.involved_objects,
            }
            for sql in (event.deadlock_sqls or [])
        ],
    }

    analysis = await analyze_deadlock(deadlock_info, **await get_deepseek_config(db))

    event.analysis_result = analysis
    try:
        await db.commit()
    except Exception as e:
        logger.error(f"保存 AI 分析结果失败: {e}")
        await db.rollback()

    return {"event_id": event_id, "analysis": analysis}
