"""
Alembic 异步迁移环境配置

使用 SQLAlchemy 2.0 异步引擎 + asyncpg 驱动。
所有 ORM 模型已通过 app.models 导入，
alembic 通过 Base.metadata 自动识别需要追踪的表。
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------- 加载 Alembic 配置 ----------
config = context.config

# 如果存在日志配置文件，则使用它
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ========== 重要：导入所有模型，确保 Base.metadata 包含所有表 ==========
from app.database import Base
from app.models import (  # noqa: F401  -- 确保模型被注册到 Base.metadata
    AlertLog,
    DeadlockEvent,
    DeadlockSql,
    MetricRecord,
    SystemConfig,
)

# ---------- 设置目标元数据 ----------
target_metadata = Base.metadata


def get_url() -> str:
    """从 app.config 获取 PostgreSQL DSN

    优先使用 Alembic .ini 中的配置作为备选。
    生产环境下强烈建议通过环境变量配置。
    """
    try:
        from app.config import settings

        return settings.PG_DSN.replace("+asyncpg", "")
    except Exception:
        # 备选：从 alembic.ini 读取
        return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """离线模式执行迁移

    仅生成 SQL 脚本而不连接数据库，适用于审查或 DBA 手动执行。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 表名使用小写蛇形命名
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """在同步连接上执行迁移"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """异步模式执行迁移

    使用 async engine 连接到 PostgreSQL，在线执行迁移。
    """
    # 构建异步配置
    config_section = config.get_section(config.config_ini_section)
    url = get_url()
    config_section["sqlalchemy.url"] = url.replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    connectable = async_engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """在线模式入口

    根据配置决定使用异步还是同步引擎。
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
