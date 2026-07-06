"""
认证路由
登录、获取当前用户信息、修改密码等接口。
"""

import logging
from datetime import datetime, timezone
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
    hash_password,
    generate_reset_token,
    verify_reset_token,
    invalidate_reset_token,
    verify_password,
)
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

router = APIRouter()

_LOGIN_ATTEMPTS = defaultdict(list)
_MAX_LOGIN_ATTEMPTS = 5
_LOGIN_WINDOW_SECONDS = 60


def _check_login_rate_limit(ip: str) -> bool:
    now = datetime.now().timestamp()
    _LOGIN_ATTEMPTS[ip] = [t for t in _LOGIN_ATTEMPTS[ip] if now - t < _LOGIN_WINDOW_SECONDS]
    if len(_LOGIN_ATTEMPTS[ip]) >= _MAX_LOGIN_ATTEMPTS:
        return False
    _LOGIN_ATTEMPTS[ip].append(now)
    return True


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=200)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    role: str
    full_name: str | None = None
    is_active: bool
    last_login_at: datetime | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)


@router.post("/login", response_model=LoginResponse, summary="登录")
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    client_ip = request.client.host if request.client else ""
    if not _check_login_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录尝试过于频繁，请稍后再试",
        )

    user = await authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    # 更新最后登录时间
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(user.id, user.username, user.role)

    # 记录登录审计
    client_ip = request.client.host if request.client else ""
    await log_action(db, user.username, "LOGIN", "Auth", f"{user.username} 登录成功", client_ip)

    return LoginResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
        },
    )


@router.get("/me", response_model=CurrentUserResponse, summary="获取当前登录用户信息")
async def get_me(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        last_login_at=current_user.last_login_at,
    )


@router.post("/change_password", summary="修改自己的密码")
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码不正确")

    current_user.password_hash = hash_password(payload.new_password)
    await db.commit()

    # 记录密码修改审计
    client_ip = request.client.host if request.client else ""
    await log_action(db, current_user.username, "UPDATE", "Auth", f"{current_user.username} 修改了密码", client_ip)

    return {"message": "密码修改成功"}


class ResetPasswordRequest(BaseModel):
    email: str = Field(..., max_length=200)


class ResetPasswordConfirmRequest(BaseModel):
    token: str = Field(...)
    new_password: str = Field(..., min_length=6, max_length=100)


@router.post("/forgot_password", summary="请求密码重置")
async def forgot_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_email(db, payload.email)
    if not user or not user.is_active:
        return {"message": "如果该邮箱已注册，将收到重置链接"}

    token = generate_reset_token(user.id)

    try:
        from app.services.notification import NotificationService
        ns = NotificationService()
        await ns.email_notifier.send_password_reset_email(
            username=user.username,
            email=user.email,
            token=token,
            full_name=user.full_name or "",
        )
    except Exception as e:
        logger.error("Failed to send password reset email: %s", e)

    return {"message": "如果该邮箱已注册，将收到重置链接"}


@router.post("/reset_password", summary="重置密码")
async def reset_password(
    payload: ResetPasswordConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    user_id = verify_reset_token(payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="重置链接无效或已过期")

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="用户不存在或已禁用")

    user.password_hash = hash_password(payload.new_password)
    await db.commit()

    invalidate_reset_token(payload.token)

    logger.info("Password reset for user: %s", user.username)

    return {"message": "密码重置成功"}
