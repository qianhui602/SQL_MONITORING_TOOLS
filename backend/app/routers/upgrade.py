"""
在线升级 API 路由

提供版本检查、Git 仓库状态查看、执行升级等接口。
仅管理员可操作。
"""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.user import User
from app.services.auth_service import get_current_user, require_admin
from app.services.upgrade_service import (
    apply_upgrade,
    check_version,
    get_git_status,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class VersionCheckResponse(BaseModel):
    """版本检查响应"""

    current_version: str
    latest_version: str
    has_update: bool
    release_url: str = ""
    release_notes: str = ""
    published_at: str = ""
    error: str = ""


class GitStatusResponse(BaseModel):
    """Git 仓库状态响应"""

    is_git_repo: bool
    remote_url: str = ""
    branch: str = ""
    last_commit: str = ""
    has_uncommitted: bool = False
    behind_remote: int = 0
    error: str = ""


class UpgradeApplyResponse(BaseModel):
    """升级结果响应"""

    success: bool
    error: str = ""
    logs: list[str] = []


@router.get(
    "/check",
    response_model=VersionCheckResponse,
    summary="检查 GitHub 新版本",
)
async def check_new_version(
    _: User = Depends(require_admin),
):
    """检查 GitHub Releases 是否有比当前更新的版本。"""
    return await check_version()


@router.get(
    "/git-status",
    response_model=GitStatusResponse,
    summary="查看 Git 仓库状态",
)
async def get_repo_status(
    _: User = Depends(require_admin),
):
    """查看当前 Git 仓库的远程地址、分支、未提交变更等信息。"""
    return await get_git_status()


@router.post(
    "/apply",
    response_model=UpgradeApplyResponse,
    summary="执行在线升级",
)
async def perform_upgrade(
    _: User = Depends(require_admin),
):
    """执行完整升级流程：git pull → docker-compose build → docker-compose up -d

    **注意**:
    - 升级期间服务可能短暂不可用
    - 需要服务器上已配置好 Git 远程仓库
    """
    return await apply_upgrade()
