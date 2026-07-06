"""
配置管理模块
从环境变量 / .env 文件中读取所有配置
"""

import base64
import os
import secrets
import warnings
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，优先级：环境变量 > .env 文件"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---------- 项目基础信息 ----------
    PROJECT_NAME: str = "SQL 监控平台"
    VERSION: str = "1.0.11"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    FRONTEND_URL: str = ""

    # ---------- PostgreSQL（存储监控数据和配置） ----------
    PG_HOST: str = "127.0.0.1"
    PG_PORT: int = 5432
    PG_USER: str = "postgres"
    PG_PASSWORD: str = ""
    PG_DATABASE: str = "sql_monitor"

    @property
    def PG_DSN(self) -> str:
        return (
            f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
        )

    @property
    def PG_SYNC_DSN(self) -> str:
        """同步 DSN，用于 Alembic 迁移"""
        return (
            f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
        )

    # ---------- SQL Server（被监控的目标数据库） ----------
    MSSQL_HOST: str = "127.0.0.1"
    MSSQL_PORT: int = 1433
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""
    MSSQL_DATABASE: str = "master"

    # ---------- 定时任务 ----------
    SCHEDULER_INTERVAL_SECONDS: int = 60

    # ---------- 告警通知配置 ----------
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAILS: List[str] = []

    DINGTALK_WEBHOOK_URL: str = ""
    FEISHU_WEBHOOK_URL: str = ""

    # ---------- 日志 ----------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )

    # ---------- 认证 / JWT ----------
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    DEFAULT_ADMIN_USERNAME: str = os.environ.get("DEFAULT_ADMIN_USERNAME", "Admin")
    DEFAULT_ADMIN_PASSWORD: str = os.environ.get("DEFAULT_ADMIN_PASSWORD", "")

    # ---------- 密码加密 ----------
    # 用于加密/解密 SQL Server 密码的密钥（Fernet 对称加密）
    # 生产环境务必通过环境变量配置固定值，否则重启后无法解密已有密码
    ENCRYPTION_KEY: str = os.environ.get("ENCRYPTION_KEY", "")


settings = Settings()

# 确保 JWT 密钥存在：未配置时生成随机密钥并警告
if not settings.JWT_SECRET_KEY:
    settings.JWT_SECRET_KEY = secrets.token_urlsafe(32)
    warnings.warn(
        "JWT_SECRET_KEY 未设置，已生成随机密钥。"
        "请在 .env 中配置固定值以保证重启后 token 仍有效。"
    )

# 确保加密密钥存在：未配置时生成随机密钥并强烈警告
# 注意：随机密钥会导致重启后无法解密已有密码，生产环境务必配置固定值
if not settings.ENCRYPTION_KEY:
    settings.ENCRYPTION_KEY = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode()
    warnings.warn(
        "ENCRYPTION_KEY 未设置，已生成随机密钥。"
        "重启后将无法解密已加密存储的 SQL Server 密码，"
        "请在 .env 中配置固定值。"
    )