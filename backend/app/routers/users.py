"""
用户管理路由
仅管理员可访问（超级管理员有最高权限）。
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import (
    get_current_user,
    hash_password,
    require_admin,
    require_super_admin,
)
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default=UserRole.VIEWER.value)
    full_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=200)


class UpdateUserRequest(BaseModel):
    role: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = Field(default=None, max_length=200)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=100)


def _validate_role(role: str) -> None:
    if role not in {r.value for r in UserRole}:
        raise HTTPException(status_code=400, detail=f"无效的角色: {role}")


@router.get("", response_model=List[UserResponse], summary="用户列表")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.id.asc()))
    return result.scalars().all()


@router.post("", response_model=UserResponse, summary="创建用户")
async def create_user(
    payload: CreateUserRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    _validate_role(payload.role)

    # 仅超级管理员可创建管理员/超级管理员
    if payload.role in (UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value):
        if current_user.role != UserRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=403, detail="只有超级管理员可以创建管理员账号"
            )

    # 用户名唯一性（不区分大小写）
    existing = await db.execute(
        select(User).where(func.lower(User.username) == payload.username.lower())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在（不区分大小写）")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        full_name=payload.full_name,
        email=payload.email,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 记录审计日志
    client_ip = request.client.host if request.client else ""
    await log_action(
        db, current_user.username, "CREATE", "User",
        f"创建用户: {user.username}, 角色: {user.role}", client_ip,
    )

    # 发送欢迎邮件（发送到用户邮箱）
    if payload.email:
        try:
            from app.services.notification import NotificationService
            ns = NotificationService()
            await ns.email_notifier.send_welcome_email(
                username=payload.username,
                password=payload.password,
                full_name=payload.full_name or "",
                to_email=payload.email,
            )
        except Exception as e:
            logger.debug("Welcome email not sent: %s", e)

    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 超级管理员账号不可被任何人禁用或降级
    if user.role == UserRole.SUPER_ADMIN.value:
        if payload.role is not None and payload.role != UserRole.SUPER_ADMIN.value:
            raise HTTPException(status_code=403, detail="超级管理员角色不可修改")
        if payload.is_active is False:
            raise HTTPException(status_code=403, detail="超级管理员账号不可禁用")

    if payload.role is not None:
        _validate_role(payload.role)
        # 仅超级管理员可设置 admin/super_admin
        if payload.role in (UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value):
            if current_user.role != UserRole.SUPER_ADMIN.value:
                raise HTTPException(status_code=403, detail="只有超级管理员可以授予管理员权限")
        user.role = payload.role

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        user.email = payload.email
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password:
        user.password_hash = hash_password(payload.password)

    await db.commit()
    await db.refresh(user)

    # 记录审计日志
    client_ip = request.client.host if request.client else ""
    detail_parts = []
    if payload.role:
        detail_parts.append(f"角色: {payload.role}")
    if payload.is_active is not None:
        detail_parts.append(f"启用: {payload.is_active}")
    if payload.password:
        detail_parts.append("重置密码")
    await log_action(
        db, current_user.username, "UPDATE", "User",
        f"更新用户: {user.username}, {'; '.join(detail_parts)}", client_ip,
    )

    return user


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == UserRole.SUPER_ADMIN.value:
        raise HTTPException(status_code=403, detail="超级管理员账号不可删除")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="不能删除自己")

    username = user.username
    await db.delete(user)
    await db.commit()

    # 记录审计日志
    client_ip = request.client.host if request.client else ""
    await log_action(
        db, current_user.username, "DELETE", "User",
        f"删除用户: {username}", client_ip,
    )

    return {"message": "用户已删除"}
