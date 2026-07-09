"""
版本检查路由
对比本地版本与 GitHub 最新版本，提示用户是否需要升级。
"""

import logging
import re
import urllib.request
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _parse_version(version_str: str) -> tuple:
    """将版本号字符串解析为可比较的元组，如 '1.0.11' -> (1, 0, 11)"""
    match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)', version_str.strip())
    if match:
        return tuple(int(x) for x in match.groups())
    return (0, 0, 0)


def _fetch_github_latest_tag() -> Optional[str]:
    """从 GitHub API 获取最新 release/tag 版本号"""
    try:
        url = "https://api.github.com/repos/qianhui602/SQL_MONITORING_TOOLS/releases/latest"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SQL-Monitor-App"
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("tag_name", "")
    except Exception as e:
        logger.warning("获取 GitHub 版本失败: %s", e)
        return None


def _fetch_github_tags() -> Optional[str]:
    """从 GitHub API 获取最新 tag（如果没有 release）"""
    try:
        url = "https://api.github.com/repos/qianhui602/SQL_MONITORING_TOOLS/tags?per_page=1"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SQL-Monitor-App"
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                return data[0].get("name", "")
    except Exception as e:
        logger.warning("获取 GitHub tags 失败: %s", e)
        return None


class VersionCheckResponse(BaseModel):
    current_version: str
    latest_version: Optional[str] = None
    has_update: bool = False
    github_url: str = "https://github.com/qianhui602/SQL_MONITORING_TOOLS"
    message: str = ""


@router.get("/check", response_model=VersionCheckResponse)
async def check_version():
    """检查是否有新版本可用"""
    current_version = settings.VERSION

    # 尝试从 GitHub 获取最新版本
    latest_tag = _fetch_github_latest_tag()
    if not latest_tag:
        latest_tag = _fetch_github_tags()

    if not latest_tag:
        return VersionCheckResponse(
            current_version=current_version,
            latest_version=None,
            has_update=False,
            message="无法获取远程版本信息，请检查网络连接"
        )

    latest_clean = latest_tag.lstrip("v")
    current_tuple = _parse_version(current_version)
    latest_tuple = _parse_version(latest_clean)

    has_update = latest_tuple > current_tuple

    message = ""
    if has_update:
        message = f"发现新版本 {latest_tag}，当前版本 v{current_version}，建议升级以获取最新功能和安全修复。"
    else:
        message = f"当前已是最新版本 v{current_version}"

    return VersionCheckResponse(
        current_version=current_version,
        latest_version=latest_clean,
        has_update=has_update,
        message=message
    )
