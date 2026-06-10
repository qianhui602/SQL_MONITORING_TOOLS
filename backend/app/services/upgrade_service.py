"""
在线升级服务

提供版本检测、Git 拉取、Docker 构建与重启等功能。
仅在 Docker 部署模式下生效（检测到 /app/.docker 标记或 DOCKER_CONTAINER 环境变量）。
"""

import asyncio
import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# 项目路径 - 从 backend/app/services/ 向上三级到项目根目录
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # backend/
PROJECT_DIR = os.path.dirname(_backend_dir)  # 项目根目录
DOCKER_COMPOSE_FILE = os.path.join(PROJECT_DIR, "docker-compose.yml")
VERSION_FILE = os.path.join(_backend_dir, "VERSION")

logger.info("Upgrade service initialized: PROJECT_DIR=%s, VERSION_FILE=%s", PROJECT_DIR, VERSION_FILE)

# 运行模式检测
IS_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"

# 默认 GitHub 仓库，可通过环境变量 UPGRADE_GITHUB_REPO 覆盖
GITHUB_REPO = os.environ.get("UPGRADE_GITHUB_REPO", "qianhui602/SQL_MONITORING_TOOLS")
GITHUB_URL = f"https://github.com/{GITHUB_REPO}.git"

# 是否检查 git 命令可用
GIT_AVAILABLE = shutil.which("git") is not None


def _get_current_version() -> str:
    """从 VERSION 文件读取当前版本，失败则回退到 settings.VERSION"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, encoding="utf-8") as f:
                version = f.read().strip()
                if version:
                    return version
    except Exception as e:
        logger.warning("读取 VERSION 文件失败: %s", e)
    return settings.VERSION


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
    current = _get_current_version()
    env_name = os.environ.get("UPGRADE_ENV", "production")

    # 如果未配置有效的 GitHub 仓库，返回提示
    if not GITHUB_REPO or GITHUB_REPO.count("/") != 1:
        return {
            "current_version": current,
            "latest_version": current,
            "has_update": False,
            "release_url": "",
            "error": f"GitHub 仓库未配置（当前: {GITHUB_REPO or '空'}），请在 .env 中设置 UPGRADE_GITHUB_REPO",
            "upgrade_enabled": False,
        }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            resp = await client.get(
                url,
                headers={"Accept": "application/vnd.github.v3+json"},
            )

            if resp.status_code == 404:
                return {
                    "current_version": current,
                    "latest_version": current,
                    "has_update": False,
                    "release_url": f"https://github.com/{GITHUB_REPO}/releases",
                    "error": f"GitHub 仓库 {GITHUB_REPO} 不存在或没有公开的 Release",
                    "upgrade_enabled": True,
                }
            elif resp.status_code == 403:
                # API 限流
                return {
                    "current_version": current,
                    "latest_version": current,
                    "has_update": False,
                    "release_url": f"https://github.com/{GITHUB_REPO}/releases",
                    "error": "GitHub API 请求频率限制，请稍后再试",
                    "upgrade_enabled": True,
                }
            elif resp.status_code != 200:
                return {
                    "current_version": current,
                    "latest_version": current,
                    "has_update": False,
                    "release_url": f"https://github.com/{GITHUB_REPO}/releases",
                    "error": f"GitHub API 返回 {resp.status_code}",
                    "upgrade_enabled": True,
                }

            data = resp.json()
            latest_tag = data.get("tag_name", "").lstrip("v")
            release_url = data.get("html_url", "")

            has_update = _compare_versions(latest_tag, current) > 0

            return {
                "current_version": current,
                "latest_version": latest_tag or current,
                "has_update": has_update,
                "release_url": release_url,
                "release_notes": (data.get("body", "")[:1000] if data.get("body") else ""),
                "published_at": data.get("published_at", ""),
                "upgrade_enabled": True,
            }

    except httpx.TimeoutException:
        return {
            "current_version": current,
            "latest_version": current,
            "has_update": False,
            "release_url": f"https://github.com/{GITHUB_REPO}/releases",
            "error": "GitHub API 请求超时，请检查服务器网络",
            "upgrade_enabled": True,
        }
    except Exception as e:
        logger.exception("版本检测失败")
        return {
            "current_version": current,
            "latest_version": current,
            "has_update": False,
            "release_url": "",
            "error": f"版本检测异常: {str(e)}",
            "upgrade_enabled": True,
        }


def _compare_versions(v1: str, v2: str) -> int:
    """比较版本号，v1 > v2 返回 1，相等返回 0，小于返回 -1"""
    try:
        parts1 = [int(x) for x in v1.split(".")]
        parts2 = [int(x) for x in v2.split(".")]
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
    """获取当前项目状态"""
    # 检查关键文件是否存在
    has_backend = os.path.isdir(os.path.join(PROJECT_DIR, "backend"))
    has_frontend = os.path.isdir(os.path.join(PROJECT_DIR, "frontend"))
    has_compose = os.path.exists(DOCKER_COMPOSE_FILE)
    has_version = os.path.exists(VERSION_FILE)

    # 如果有 Git 命令，尝试获取更多信息
    if GIT_AVAILABLE:
        code, _, _ = _run_cmd(["git", "rev-parse", "--git-dir"])
        if code == 0:
            # 有 Git 仓库
            _, remote_url, _ = _run_cmd(["git", "remote", "get-url", "origin"])
            _, branch, _ = _run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            _, last_commit, _ = _run_cmd(["git", "log", "-1", "--format=%H %s"])
            return {
                "is_git_repo": True,
                "remote_url": remote_url or "",
                "branch": branch or "",
                "last_commit": last_commit or "",
                "current_version": _get_current_version(),
                "project_ready": has_backend and has_frontend,
            }

    # 无 Git 环境（如 Docker 容器内），显示项目状态
    return {
        "is_git_repo": False,
        "current_version": _get_current_version(),
        "project_ready": has_backend and has_frontend,
        "has_backend": has_backend,
        "has_frontend": has_frontend,
        "has_docker_compose": has_compose,
        "hint": "在线升级将通过下载 Release ZIP 方式更新代码",
    }


async def apply_upgrade() -> dict:
    """执行升级：下载 Release zip + 解压 + 构建 Docker 镜像 + 重启"""
    start_time = datetime.now(timezone.utc)
    logs: list[str] = []

    def log(msg: str):
        logger.info("[UPGRADE] %s", msg)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    try:
        log("开始升级流程...")
        log(f"当前版本: v{_get_current_version()}")

        # 1. 获取最新版本信息
        log("步骤 1/4: 获取最新版本...")
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"获取版本信息失败: HTTP {resp.status_code}",
                    "logs": logs,
                }
            release_data = resp.json()
            latest_tag = release_data.get("tag_name", "").lstrip("v")
            zipball_url = release_data.get("zipball_url", "")

        log(f"✓ 最新版本: v{latest_tag}")

        # 2. 下载并解压代码
        log("步骤 2/4: 下载最新代码...")
        if not zipball_url:
            return {
                "success": False,
                "error": "未找到下载链接",
                "logs": logs,
            }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(zipball_url)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"下载代码失败: HTTP {resp.status_code}",
                    "logs": logs,
                }

        # 保存到临时文件并解压
        import io
        import zipfile

        zip_bytes = io.BytesIO(resp.content)
        if not zipfile.is_zipfile(zip_bytes):
            return {
                "success": False,
                "error": "下载的文件不是有效的 ZIP 格式",
                "logs": logs,
            }

        zip_bytes.seek(0)
        with zipfile.ZipFile(zip_bytes) as zf:
            # 获取顶层目录名
            top_dirs = set()
            for name in zf.namelist():
                parts = name.split("/")
                if len(parts) > 1:
                    top_dirs.add(parts[0])

            if not top_dirs:
                return {
                    "success": False,
                    "error": "ZIP 文件格式异常",
                    "logs": logs,
                }

            # 解压到临时目录
            temp_dir = os.path.join(PROJECT_DIR, "_upgrade_temp")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            zf.extractall(temp_dir)

        # 找到解压后的目录
        extracted_dir = os.path.join(temp_dir, list(top_dirs)[0])

        # 备份当前版本
        log("备份当前版本...")
        backup_dir = os.path.join(PROJECT_DIR, f"_backup_{_get_current_version()}")
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

        # 复制关键文件到临时目录
        log("✓ 代码下载完成")

        # 3. 更新代码
        log("步骤 3/4: 更新代码文件...")
        # 需要更新的目录和文件
        update_dirs = ["backend", "frontend", "Docs"]
        update_files = ["docker-compose.yml", "README.md", ".env.example", "deploy.sh", "deploy.ps1"]

        for d in update_dirs:
            src = os.path.join(extracted_dir, d)
            dst = os.path.join(PROJECT_DIR, d)
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                log(f"✓ 更新目录: {d}")

        for f in update_files:
            src = os.path.join(extracted_dir, f)
            dst = os.path.join(PROJECT_DIR, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                log(f"✓ 更新文件: {f}")

        # 更新 VERSION 文件
        version_file = os.path.join(extracted_dir, "backend", "VERSION")
        if os.path.exists(version_file):
            shutil.copy2(version_file, os.path.join(PROJECT_DIR, "backend", "VERSION"))
            log(f"✓ 版本更新为 v{latest_tag}")

        # 清理临时文件
        shutil.rmtree(temp_dir)

        # 4. 构建 Docker 镜像
        log("步骤 4/4: 构建 Docker 镜像...")
        compose_file = DOCKER_COMPOSE_FILE
        if os.path.exists(compose_file):
            compose_dir = os.path.dirname(compose_file)
            code, out, err = _run_cmd(
                ["docker-compose", "build", "--no-cache"],
                cwd=compose_dir,
                timeout=600,
            )
            if code != 0:
                return {
                    "success": False,
                    "error": f"Docker 构建失败: {err[:300] if err else out[:300]}",
                    "logs": logs,
                }
            log("✓ Docker 镜像构建完成")

            # 5. 重启服务
            log("重启服务...")
            code, out, err = _run_cmd(
                ["docker-compose", "up", "-d"],
                cwd=compose_dir,
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
            log("! 未检测到 docker-compose.yml，跳过 Docker 构建步骤")

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        log(f"✓ 升级完成！耗时: {elapsed:.0f} 秒")

        return {
            "success": True,
            "message": f"升级到 v{latest_tag} 成功",
            "elapsed_seconds": elapsed,
            "logs": logs,
        }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "下载超时，请检查网络连接",
            "logs": logs,
        }
    except Exception as e:
        logger.exception("升级失败")
        return {
            "success": False,
            "error": f"升级异常: {str(e)}",
            "logs": logs,
        }
