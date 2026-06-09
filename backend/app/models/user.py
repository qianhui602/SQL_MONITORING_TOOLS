"""
用户模型
存储系统用户及其角色权限信息。
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, Enum):
    """用户角色枚举

    - SUPER_ADMIN: 超级管理员（不可删除，拥有全部权限）
    - ADMIN: 管理员（可管理用户、修改配置）
    - VIEWER: 只读用户（仅可查看数据）
    """

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """系统用户

    存储登录用户、密码哈希、角色权限和账号状态。
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主键 ID"
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="登录用户名"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希（bcrypt）"
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.VIEWER.value,
        comment="角色: super_admin / admin / viewer",
    )
    full_name: Mapped[str] = mapped_column(
        String(100), nullable=True, default=None, comment="姓名"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="是否启用"
    )
    last_login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="最后登录时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="最后更新时间",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
