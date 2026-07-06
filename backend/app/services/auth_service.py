"""
认证服务
封装密码哈希、JWT 编码/解码、当前用户依赖注入等工具。
"""

import logging
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

_PASSWORD_RESET_CODES = {}  # code -> {"user_id": int, "expires_at": datetime}
_RESET_CODE_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        logger.info("JWT token expired")
        return None
    except jwt.PyJWTError as e:
        logger.warning("JWT decode error: %s", e)
        return None


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    if not username:
        return None
    stmt = select(User).where(func.lower(User.username) == username.lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        verify_password(password, "fake_hash_for_timing_attack_prevention_0123456789")
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(func.lower(User.email) == email.lower())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def generate_reset_code(user_id: int) -> str:
    """生成 6 位数字验证码，关联用户 ID，有效期 30 分钟"""
    now = datetime.now(timezone.utc)
    # 清理过期验证码
    expired = [k for k, v in _PASSWORD_RESET_CODES.items() if v["expires_at"] < now]
    for k in expired:
        del _PASSWORD_RESET_CODES[k]
    # 移除该用户之前的验证码
    to_remove = [k for k, v in _PASSWORD_RESET_CODES.items() if v["user_id"] == user_id]
    for k in to_remove:
        del _PASSWORD_RESET_CODES[k]
    # 生成 6 位数字验证码
    code = "".join(random.choices(string.digits, k=6))
    _PASSWORD_RESET_CODES[code] = {
        "user_id": user_id,
        "expires_at": now + timedelta(minutes=_RESET_CODE_EXPIRE_MINUTES),
    }
    return code


def verify_reset_code(code: str) -> Optional[int]:
    """验证验证码，返回 user_id 或 None"""
    data = _PASSWORD_RESET_CODES.get(code)
    if not data:
        return None
    if datetime.now(timezone.utc) > data["expires_at"]:
        del _PASSWORD_RESET_CODES[code]
        return None
    return data["user_id"]


def invalidate_reset_code(code: str) -> None:
    _PASSWORD_RESET_CODES.pop(code, None)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或 token 无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="token 缺少用户信息")

    user = await get_user_by_id(db, int(user_id_str))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )
    return current_user
