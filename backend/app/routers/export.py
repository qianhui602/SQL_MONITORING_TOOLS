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

    使用 StringIO 缓冲区逐批写入 CSV 数据并 yield，
    实现低内存占用的流式导出。

    Args:
        headers: CSV 列标题列表
        rows_generator: 异步生成器，yield 每行数据（tuple）

    Yields:
        bytes: CSV 数据块
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入 BOM 确保 Excel 正确识别 UTF-8
    yield io.BytesIO(b"\xef\xbb\xbf").read()
    # 写入表头
    output.write(",".join(f'"{h}"' for h in headers) + "\n")

    batch_size = 500
    batch = []

    async for row in rows_generator:
        batch.append(row)
        if len(batch) >= batch_size:
            for r in batch:
                output.write(",".join(f'"{v}"' if v is not None else "" for v in r) + "\n")
            data = output.getvalue()
            output.seek(0)
            output.truncate()
            yield data.encode("utf-8")
            batch = []

    # 写入剩余批次
    for r in batch:
        output.write(",".join(f'"{v}"' if v is not None else "" for v in r) + "\n")
    data = output.getvalue()
    if data:
        yield data.encode("utf-8")


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
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出死锁事件为 CSV 文件。"""
    conditions = []
    if start_time:
        conditions.append(DeadlockEvent.occur_at >= start_time)
    if end_time:
        conditions.append(DeadlockEvent.occur_at <= end_time)

    stmt = (
        select(DeadlockEvent)
        .where(*conditions)
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
            yield (
                rec.id,
                rec.occur_at.isoformat() if rec.occur_at else "",
                rec.victim_session_id or "",
                rec.server_address,
            )

    headers = ["ID", "发生时间", "受害者会话ID", "服务器地址"]
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
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """导出慢查询数据为 CSV 文件。"""
    headers = [
        "ID", "SQL哈希", "SQL文本", "执行次数", "CPU时间(ms)",
        "逻辑读", "总耗时(ms)", "平均耗时(ms)", "最后执行时间", "采集时间",
    ]

    async def row_generator():
        filters = []
        if start_time:
            filters.append(SlowQueryRecord.collected_at >= start_time)
        if end_time:
            filters.append(SlowQueryRecord.collected_at <= end_time)

        stmt = (
            select(SlowQueryRecord)
            .where(*filters) if filters else select(SlowQueryRecord)
        )
        stmt = stmt.order_by(SlowQueryRecord.collected_at.desc())

        result = await db.execute(stmt)
        records = result.scalars().all()

        for r in records:
            yield (
                r.id,
                r.sql_hash,
                r.sql_text[:200] if r.sql_text else "",
                r.execution_count,
                round(r.total_cpu_ms, 2),
                r.total_logical_reads,
                round(r.total_elapsed_ms, 2),
                round(r.avg_elapsed_ms, 2),
                r.last_execution_time.isoformat() if r.last_execution_time else "",
                r.collected_at.isoformat(),
            )

    filename = f"slow_queries_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        _stream_csv(headers, row_generator()),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
