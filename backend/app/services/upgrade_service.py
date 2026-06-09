"""
在线升级服务

提供版本检测、Git 拉取、Docker 构建与重启等功能。
仅在 Docker 部署模式下生效（检测到 /app/.docker 标记）。
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# 项目配置
CURRENT_VERSION = "0.1.0"
GITHUB_API = "https://api.github.com/repos"
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCKER_COMPOSE_FILE = os.path.join(PROJECT_DIR, "..", "docker-compose.yml")

# 运行模式检测
IS_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"


def _run_cmd(cmd: list[str], cwd: str = PROJECT_DIR, timeout: int = 120) -> tuple[int, str, str]:
    """执行 shell 命令并返回 (返回码, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "命令执行超时"
    except FileNotFoundError:
        return -1, "", f"命令未找到: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


async def check_version() -> dict:
    """检查 GitHub 上是否有新版本"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{GITHUB_API}/sunvalley-sql-monitor/sql-monitor/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
            )

            if resp.status_code != 200:
                return {
                    "current_version": CURRENT_VERSION,
                    "latest_version": CURRENT_VERSION,
                    "has_update": False,
                    "release_url": "",
                    "error": f"GitHub API 返回 {resp.status_code}",
                }

            data = resp.json()
            latest_tag = data.get("tag_name", "").lstrip("v")
            release_url = data.get("html_url", "")

            # 简单版本比较
            has_update = _compare_versions(latest_tag, CURRENT_VERSION) > 0

            return {
                "current_version": CURRENT_VERSION,
                "latest_version": latest_tag or CURRENT_VERSION,
                "has_update": has_update,
                "release_url": release_url,
                "release_notes": data.get("body", "")[:500] if data.get("body") else "",
                "published_at": data.get("published_at", ""),
            }

    except httpx.TimeoutException:
        return {
            "current_version": CURRENT_VERSION,
            "latest_version": CURRENT_VERSION,
            "has_update": False,
            "error": "GitHub API 请求超时",
        }
    except Exception as e:
        logger.exception("版本检测失败")
        return {
            "current_version": CURRENT_VERSION,
            "latest_version": CURRENT_VERSION,
            "has_update": False,
            "error": str(e),
        }


def _compare_versions(v1: str, v2: str) -> int:
    """比较版本号，v1 > v2 返回 1，相等返回 0，小于返回 -1"""
    try:
        parts1 = [int(x) for x in v1.split(".")]
        parts2 = [int(x) for x in v2.split(".")]
        # 补齐位数
        max_len = max(len(parts1), len(parts2))
        parts1 += [0] * (max_len - len(parts1))
        parts2 += [0] * (max_len - len(parts2))

        for a, b in zip(parts1, parts2):
            if a > b:
                return 1
            if a < b:
                return -1
        return 0
    except (ValueError, AttributeError):
        return 0


async def get_git_status() -> dict:
    """获取当前 Git 仓库状态"""
    # 检查是否是 git 仓库
    code, _, _ = _run_cmd(["git", "rev-parse", "--git-dir"])
    if code != 0:
        return {"is_git_repo": False, "error": "不是 Git 仓库"}

    # 获取远程仓库地址
    _, remote_url, _ = _run_cmd(["git", "remote", "get-url", "origin"])
    # 获取当前分支
    _, branch, _ = _run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    # 获取最近提交
    _, last_commit, _ = _run_cmd(["git", "log", "-1", "--format=%H %s"])
    # 检查是否有未提交的更改
    _, has_changes, _ = _run_cmd(["git", "status", "--porcelain"])
    # 检查与远程的差异
    _, behind_count, _ = _run_cmd(
        ["git", "rev-list", "--count", f"HEAD..origin/{branch}"]
    ) if branch else ("0", "0", "")

    return {
        "is_git_repo": True,
        "remote_url": remote_url or "",
        "branch": branch or "",
        "last_commit": last_commit or "",
        "has_uncommitted": bool(has_changes),
        "behind_remote": int(behind_count) if behind_count.isdigit() else 0,
    }


async def apply_upgrade() -> dict:
    """执行升级：拉取代码 + 构建 Docker 镜像 + 重启"""
    start_time = datetime.now(timezone.utc)
    logs: list[str] = []

    def log(msg: str):
        logger.info("[UPGRADE] %s", msg)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    try:
        log("开始升级流程...")

        # 1. 检查 Git 仓库
        log("步骤 1/4: 检查 Git 仓库...")
        code, _, err = _run_cmd(["git", "rev-parse", "--git-dir"])
        if code != 0:
            return {
                "success": False,
                "error": "不是 Git 仓库，无法在线升级",
                "logs": logs,
            }
        log("✓ Git 仓库正常")

        # 2. 拉取最新代码
        log("步骤 2/4: 拉取最新代码...")
        code, out, err = _run_cmd(["git", "pull", "--ff-only"])
        if code != 0:
            return {
                "success": False,
                "error": f"Git pull 失败: {err or out}",
                "logs": logs,
            }
        log(f"✓ 代码已更新到最新: {out[:200] if out else ''}")

        # 3. 构建 Docker 镜像
        log("步骤 3/4: 构建 Docker 镜像...")
        compose_file = os.path.join(PROJECT_DIR, "..", "docker-compose.yml")
        if os.path.exists(compose_file):
            code, out, err = _run_cmd(
                ["docker-compose", "build", "--no-cache"],
                cwd=os.path.dirname(compose_file),
                timeout=300,
            )
            if code != 0:
                return {
                    "success": False,
                    "error": f"Docker 构建失败: {err[:300] if err else out[:300]}",
                    "logs": logs,
                }
            log("✓ Docker 镜像构建完成")

            # 4. 重启服务
            log("步骤 4/4: 重启服务...")
            code, out, err = _run_cmd(
                ["docker-compose", "up", "-d"],
                cwd=os.path.dirname(compose_file),
                timeout=120,
            )
            if code != 0:
                return {
                    "success": False,
                    "error": f"重启服务失败: {err or out}",
                    "logs": logs,
                }
            log("✓ 服务已重启")
        else:
            log("未检测到 docker-compose.yml，跳过 Docker 构建步骤")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        log(f"✓ 升级完成！耗时: {elapsed:.0f} 秒")

        return {
            "success": True,
            "error": "",
            "logs": logs,
        }

    except Exception as e:
        logger.exception("升级过程异常")
        return {
            "success": False,
            "error": f"升级异常: {str(e)}",
            "logs": logs,
        }
