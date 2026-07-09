"""
被监控 SQL Server 实例管理 API 路由
提供实例的 CRUD 和连接测试接口。
"""

from datetime import datetime, timezone
from typing import List, Optional

import pymssql
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.instance import MonitoredInstance
from app.models.user import User
from app.services.auth_service import get_current_user, require_admin
from app.services.crypto import decrypt_password, encrypt_password

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class InstanceCreateRequest(BaseModel):
    """添加实例请求体"""

    name: str = Field(..., min_length=1, max_length=100, description="实例名称")
    host: str = Field(..., min_length=1, max_length=255, description="主机地址")
    port: int = Field(1433, ge=1, le=65535, description="端口号")
    username: str = Field(..., min_length=1, max_length=100, description="用户名")
    password: str = Field(..., min_length=1, max_length=200, description="密码")
    database_name: str = Field("master", max_length=100, description="数据库名")
    is_active: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class InstanceUpdateRequest(BaseModel):
    """更新实例请求体（所有字段可选）"""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="实例名称")
    host: Optional[str] = Field(None, min_length=1, max_length=255, description="主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="端口号")
    username: Optional[str] = Field(None, min_length=1, max_length=100, description="用户名")
    password: Optional[str] = Field(None, min_length=1, max_length=200, description="密码")
    database_name: Optional[str] = Field(None, max_length=100, description="数据库名")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述")


class InstanceResponse(BaseModel):
    """实例响应体"""

    id: int
    name: str
    host: str
    port: int
    username: str
    database_name: str
    is_active: bool
    is_connected: bool = True
    last_connected_at: Optional[datetime] = None
    last_disconnected_at: Optional[datetime] = None
    connection_error: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestConnectionRequest(BaseModel):
    """测试连接请求体"""

    host: str
    port: int = 1433
    username: str
    password: str
    database_name: str = "master"


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=List[InstanceResponse],
    summary="获取所有实例列表",
)
async def list_instances(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[InstanceResponse]:
    """查询所有被监控的 SQL Server 实例。"""
    stmt = select(MonitoredInstance).order_by(MonitoredInstance.created_at.desc())

    try:
        result = await db.execute(stmt)
        instances = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询实例列表失败: {str(e)}"
        )

    return [
        InstanceResponse.model_validate(inst) for inst in instances
    ]


@router.post(
    "",
    response_model=InstanceResponse,
    status_code=201,
    summary="添加实例",
)
async def create_instance(
    body: InstanceCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> InstanceResponse:
    """添加一个新的被监控 SQL Server 实例。"""
    instance = MonitoredInstance(
        name=body.name,
        host=body.host,
        port=body.port,
        username=body.username,
        password=encrypt_password(body.password),
        database_name=body.database_name,
        is_active=body.is_active,
        description=body.description,
    )

    try:
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"添加实例失败: {str(e)}"
        )

    return InstanceResponse.model_validate(instance)


@router.put(
    "/{instance_id}",
    response_model=InstanceResponse,
    summary="更新实例",
)
async def update_instance(
    instance_id: int,
    body: InstanceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> InstanceResponse:
    """更新指定实例的配置信息。"""
    check_stmt = select(MonitoredInstance).where(
        MonitoredInstance.id == instance_id
    )

    try:
        check_result = await db.execute(check_stmt)
        instance = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询实例失败: {str(e)}"
        )

    if instance is None:
        raise HTTPException(
            status_code=404, detail=f"实例不存在: instance_id={instance_id}"
        )

    # 只更新传入了的字段
    update_data = body.model_dump(exclude_unset=True)
    # 如果包含密码字段，加密后存储
    if "password" in update_data and update_data["password"]:
        update_data["password"] = encrypt_password(update_data["password"])
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_stmt = (
            update(MonitoredInstance)
            .where(MonitoredInstance.id == instance_id)
            .values(**update_data)
        )
        try:
            await db.execute(update_stmt)
            await db.flush()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"更新实例失败: {str(e)}"
            )

    # 重新载入以获取最新数据
    result = await db.execute(check_stmt)
    updated_instance = result.scalar_one()
    return InstanceResponse.model_validate(updated_instance)


@router.delete(
    "/{instance_id}",
    summary="删除实例",
)
async def delete_instance(
    instance_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """删除指定的被监控实例。"""
    check_stmt = select(MonitoredInstance).where(
        MonitoredInstance.id == instance_id
    )

    try:
        check_result = await db.execute(check_stmt)
        instance = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询实例失败: {str(e)}"
        )

    if instance is None:
        raise HTTPException(
            status_code=404, detail=f"实例不存在: instance_id={instance_id}"
        )

    try:
        await db.delete(instance)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"删除实例失败: {str(e)}"
        )

    return {"message": "实例已删除", "instance_id": instance_id}


@router.post(
    "/{instance_id}/test",
    summary="测试实例连接",
)
async def test_instance_connection(
    instance_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    """使用实例配置的连接信息测试 SQL Server 连接是否正常。"""
    check_stmt = select(MonitoredInstance).where(
        MonitoredInstance.id == instance_id
    )

    try:
        check_result = await db.execute(check_stmt)
        instance = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询实例失败: {str(e)}"
        )

    if instance is None:
        raise HTTPException(
            status_code=404, detail=f"实例不存在: instance_id={instance_id}"
        )

    try:
        conn = pymssql.connect(
            server=instance.host,
            port=instance.port,
            user=instance.username,
            password=decrypt_password(instance.password),
            database=instance.database_name,
            timeout=10,
            login_timeout=10,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return {"success": True}
    except pymssql.Error as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}
