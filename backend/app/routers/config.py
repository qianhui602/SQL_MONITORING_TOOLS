"""
系统配置 API 路由
提供系统配置项的读取和更新接口。
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.config import SystemConfig
from app.models.user import User
from app.collectors.sqlserver import MSSQLConnectionManager
from app.services.auth_service import get_current_user, require_admin
from app.services.deepseek import AI_PROVIDERS
from app.services.audit_service import log_action

router = APIRouter()


class ConfigItem(BaseModel):
    """系统配置项"""

    config_key: str
    config_value: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class ConfigUpdateRequest(BaseModel):
    """更新配置请求体"""

    config_value: str


class TestMSSQLRequest(BaseModel):
    """测试 SQL Server 连接请求体"""

    host: str
    port: int = 1433
    user: str
    password: str
    database: str = "master"


@router.get(
    "",
    response_model=List[ConfigItem],
    summary="获取所有系统配置",
)
async def get_all_configs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> List[ConfigItem]:
    """查询所有系统配置项。"""
    stmt = select(SystemConfig).order_by(SystemConfig.config_key)

    try:
        result = await db.execute(stmt)
        configs = result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询系统配置失败: {str(e)}"
        )

    return [
        ConfigItem(
            config_key=cfg.config_key,
            config_value=cfg.config_value,
            description=cfg.description,
        )
        for cfg in configs
    ]


@router.get(
    "/{key}",
    response_model=ConfigItem,
    summary="获取单个系统配置",
)
async def get_config_by_key(
    key: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ConfigItem:
    """根据配置键名获取系统配置详情。"""
    stmt = select(SystemConfig).where(SystemConfig.config_key == key)

    try:
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询配置项失败: {str(e)}"
        )

    if config is None:
        raise HTTPException(
            status_code=404, detail=f"配置项不存在: config_key={key}"
        )

    return ConfigItem(
        config_key=config.config_key,
        config_value=config.config_value,
        description=config.description,
    )


@router.put(
    "/{key}",
    response_model=ConfigItem,
    summary="更新系统配置",
)
async def update_config(
    key: str,
    body: ConfigUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ConfigItem:
    """更新指定配置项的值。"""
    check_stmt = select(SystemConfig).where(SystemConfig.config_key == key)

    try:
        check_result = await db.execute(check_stmt)
        config = check_result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"查询配置项失败: {str(e)}"
        )

    if config is None:
        raise HTTPException(
            status_code=404, detail=f"配置项不存在: config_key={key}"
        )

    old_value = config.config_value
    update_stmt = (
        update(SystemConfig)
        .where(SystemConfig.config_key == key)
        .values(config_value=body.config_value)
    )

    try:
        await db.execute(update_stmt)
        await db.flush()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"更新配置项失败: {str(e)}"
        )

    result = await db.execute(check_stmt)
    updated_config = result.scalar_one()

    # 记录审计日志
    client_ip = request.client.host if request.client else ""
    await log_action(
        db, current_user.username, "UPDATE", "Config",
        f"更新配置: {key}, 旧值: {old_value}, 新值: {body.config_value}", client_ip,
    )

    return ConfigItem(
        config_key=updated_config.config_key,
        config_value=updated_config.config_value,
        description=updated_config.description,
    )


@router.post(
    "/test_mssql",
    summary="测试 SQL Server 连接",
)
async def test_mssql_connection(
    body: TestMSSQLRequest,
    _: User = Depends(require_admin),
) -> dict:
    """测试指定的 SQL Server 连接参数。"""
    try:
        mgr = MSSQLConnectionManager(
            host=body.host,
            port=body.port,
            user=body.user,
            password=body.password,
            database=body.database,
        )
        ok = mgr.test_connection()
        mgr.close()
        if ok:
            return {"success": True}
        return {"success": False, "error": "连接测试未通过"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get(
    "/ai_providers",
    summary="获取可用的 AI 提供商列表",
)
async def get_ai_providers(
    _: User = Depends(get_current_user),
) -> dict:
    """返回所有可用的 AI 提供商及其模型列表。"""
    return {"providers": AI_PROVIDERS}
