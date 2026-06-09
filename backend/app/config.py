"""
配置管理模块
从环境变量 / .env 文件中读取所有配置
"""

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
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

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
    # 为了灵活性，支持多个 SQL Server 实例，这里定义默认连接
    MSSQL_HOST: str = "127.0.0.1"
    MSSQL_PORT: int = 1433
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""
    MSSQL_DATABASE: str = "master"

    # ---------- 定时任务 ----------
    SCHEDULER_INTERVAL_SECONDS: int = 60  # 采集间隔，默认 60 秒

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
    JWT_SECRET_KEY: str = "sql-monitor-secret-key-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # 默认超级管理员账号（首次启动时自动创建）
    DEFAULT_ADMIN_USERNAME: str = "Admin"
    DEFAULT_ADMIN_PASSWORD: str = "Chuz0001"


settings = Settings()
