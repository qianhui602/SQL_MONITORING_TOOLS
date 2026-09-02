"""
数据导出 API 路由
提供性能指标、告警记录、死锁事件、慢查询的 CSV 导出接口。
使用 StreamingResponse 实现流式输出，适合大量数据导出。
"""

import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.alert import AlertLog
from app.models.deadlock import DeadlockEvent
from app.models.performance import MetricRecord
from app.models.slow_query import SlowQueryRecord
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()


async def _stream_csv(headers: list, rows_generator):
    """生成 CSV 流

    使用 csv.writer 正确转义逗号、引号、换行等特殊字符，
    逐行产出数据块，实现低内存占用的流式导出。

    Args:
        headers: CSV 列标题列表
        rows_generator: 异步生成器，yield 每行数据（tuple）

    Yields:
        bytes: CSV 数据块
    """
    output = io.StringIO()
    writer = csv.writer(output)

    yield b"\xef\xbb\xbf"
    writer.writerow(headers)
    yield output.getvalue().encode("utf-8")
    output.seek(0)
    output.truncate()

    async for row in rows_generator:
        writer.writerow(row)
        yield output.getvalue().encode("utf-8")
        output.seek(0)
        output.truncate()


@router.get(
    "/metrics",
    summary="导出性能指标 CSV",
)
async def export_metrics(
    category: Optional[str] = Query(None, description="指标分类筛选"),
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出性能指标数据为 CSV 文件。"""
    conditions = []
    if category:
        conditions.append(MetricRecord.category == category)
    if start_time:
        conditions.append(MetricRecord.collected_at >= start_time)
    if end_time:
        conditions.append(MetricRecord.collected_at <= end_time)

    stmt = (
        select(MetricRecord)
        .where(*conditions)
        .order_by(MetricRecord.collected_at.desc())
        .limit(50000)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询性能指标失败: {str(e)}"
        )

    async def row_generator():
        for rec in records:
            yield (
                rec.id,
                rec.category,
                rec.metric_name,
                rec.metric_value,
                rec.unit or "",
                rec.collected_at.isoformat() if rec.collected_at else "",
                rec.server_address,
            )

    headers = ["ID", "分类", "指标名称", "指标值", "单位", "采集时间", "服务器地址"]
    filename = f"metrics_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        _stream_csv(headers, row_generator()),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get(
    "/alerts",
    summary="导出告警记录 CSV",
)
async def export_alerts(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出告警记录为 CSV 文件。"""
    conditions = []
    if start_time:
        conditions.append(AlertLog.triggered_at >= start_time)
    if end_time:
        conditions.append(AlertLog.triggered_at <= end_time)

    stmt = (
        select(AlertLog)
        .where(*conditions)
        .order_by(AlertLog.triggered_at.desc())
        .limit(50000)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询告警记录失败: {str(e)}"
        )

    async def row_generator():
        for rec in records:
            yield (
                rec.id,
                rec.alert_type,
                rec.severity,
                rec.message,
                rec.triggered_at.isoformat() if rec.triggered_at else "",
                "是" if rec.acknowledged else "否",
                rec.acknowledged_at.isoformat() if rec.acknowledged_at else "",
                "是" if rec.notification_sent else "否",
            )

    headers = ["ID", "告警类型", "严重级别", "消息", "触发时间", "已确认", "确认时间", "通知已发送"]
    filename = f"alerts_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        _stream_csv(headers, row_generator()),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get(
    "/deadlocks",
    summary="导出死锁事件 CSV",
)
async def export_deadlocks(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    login_name: Optional[str] = Query(None, description="按用户名筛选（模糊匹配）"),
    host_name: Optional[str] = Query(None, description="按主机名筛选（模糊匹配）"),
    client_app: Optional[str] = Query(None, description="按应用程序筛选（模糊匹配）"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出死锁事件为 CSV 文件，列与死锁监控页面一致，筛选条件与列表接口一致。"""
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

    stmt = (
        select(DeadlockEvent)
        .where(*conditions)
        .options(selectinload(DeadlockEvent.deadlock_sqls))
        .order_by(DeadlockEvent.occur_at.desc())
        .limit(50000)
    )

    try:
        result = await db.execute(stmt)
        records = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询死锁事件失败: {str(e)}"
        )

    async def row_generator():
        for rec in records:
            sqls = sorted(
                rec.deadlock_sqls or [],
                key=lambda s: (s.session_id is not None, s.session_id),
            )
            sql_parts = []
            for sql in sqls:
                sql_text = (sql.sql_text or "").strip()
                if not sql_text:
                    continue
                prefix = (
                    f"[会话 {sql.session_id}]\n"
                    if sql.session_id is not None
                    else ""
                )
                sql_parts.append(f"{prefix}{sql_text}")
            yield (
                rec.occur_at.isoformat() if rec.occur_at else "",
                rec.victim_session_id if rec.victim_session_id is not None else "",
                rec.server_address,
                rec.login_name or "",
                rec.host_name or "",
                rec.client_app or "",
                "\n\n".join(sql_parts),
            )

    headers = [
        "发生时间", "受害会话ID", "SQL Server地址", "用户",
        "主机（设备）", "应用程序", "关联SQL语句",
    ]
    filename = f"deadlocks_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        _stream_csv(headers, row_generator()),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get(
    "/slow-queries",
    summary="导出慢查询 CSV",
)
async def export_slow_queries(
    start_time: Optional[datetime] = Query(None, description="起始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    server_address: Optional[str] = Query(None, description="按实例筛选"),
    sort_by: str = Query("total_elapsed_ms", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向 asc/desc"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出慢查询数据为 CSV 文件，列与慢查询分析页面一致，筛选和排序与列表接口一致。"""
    filters = []
    if start_time:
        filters.append(SlowQueryRecord.collected_at >= start_time)
    if end_time:
        filters.append(SlowQueryRecord.collected_at <= end_time)
    if server_address:
        filters.append(SlowQueryRecord.server_address == server_address)

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
    order_clause = sort_col.asc() if sort_order == "asc" else sort_col.desc()

    stmt = (
        select(SlowQueryRecord)
        .where(*filters)
        .order_by(order_clause)
        .limit(50000)
    )

    try:
        result = await db.stream(stmt.execution_options(yield_per=1000))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询慢查询记录失败: {str(e)}"
        )

    async def row_generator():
        async for r in result.scalars():
            yield (
                r.sql_text or "",
                r.execution_count,
                r.total_cpu_ms,
                r.total_logical_reads,
                r.avg_elapsed_ms,
                r.last_execution_time.isoformat() if r.last_execution_time else "",
                r.collected_at.isoformat() if r.collected_at else "",
                r.server_address,
            )

    headers = [
        "查询文本", "执行次数", "总CPU时间(ms)", "总逻辑读",
        "平均耗时(ms)", "最后执行时间", "采集时间", "实例地址",
    ]
    filename = f"slow_queries_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        _stream_csv(headers, row_generator()),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
