"""
系统安装配置路由
提供首次安装时设置管理员和系统配置的接口。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.config import SystemConfig
from app.models.user import User, UserRole
from app.services.auth_service import hash_password

router = APIRouter()


# ===== 数据模型 =====


class SetupAdminRequest(BaseModel):
    """创建管理员请求"""

    username: str = Field(..., min_length=1, description="管理员用户名")
    password: str = Field(..., min_length=1, description="管理员密码")
    full_name: str = Field(default="", description="管理员姓名")


class SetupConfigRequest(BaseModel):
    """保存系统配置请求"""

    timezone: str = Field(default="Asia/Shanghai", description="系统时区")
    data_retention_days: int = Field(default=90, description="数据保留天数")


# ===== 接口定义 =====


@router.get("/status", summary="检查系统初始化状态")
async def get_setup_status(db: AsyncSession = Depends(get_db)) -> dict:
    """检查系统是否已完成初始化（是否存在超级管理员账号）"""
    stmt = select(User).where(User.role == UserRole.SUPER_ADMIN.value).limit(1)
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()
    has_admin = admin is not None
    return {"initialized": has_admin, "has_admin": has_admin}


@router.post("/admin", summary="创建初始超级管理员")
async def create_setup_admin(
    body: SetupAdminRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """创建第一个超级管理员账号

    仅在系统中尚无管理员时可用。
    """
    # 检查是否已有管理员
    stmt = select(User).where(User.role == UserRole.SUPER_ADMIN.value).limit(1)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员已存在",
        )

    # 创建新管理员
    admin = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=UserRole.SUPER_ADMIN.value,
        full_name=body.full_name or None,
        is_active=True,
    )
    db.add(admin)
    await db.flush()

    return {"success": True, "message": "超级管理员创建成功"}


@router.post("/config", summary="保存基础系统配置")
async def save_setup_config(
    body: SetupConfigRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """保存系统基本配置项（时区、数据保留天数等）"""
    configs_to_save = [
        ("timezone", body.timezone, "系统时区"),
        ("data_retention_days", str(body.data_retention_days), "数据保留天数"),
    ]

    for key, value, desc in configs_to_save:
        # 查询现有配置
        stmt = select(SystemConfig).where(SystemConfig.config_key == key)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if config:
            # 更新现有配置
            config.config_value = value
        else:
            # 插入新配置
            new_config = SystemConfig(
                config_key=key,
                config_value=value,
                description=desc,
            )
            db.add(new_config)

    await db.flush()

    return {"success": True, "message": "系统配置保存成功"}
