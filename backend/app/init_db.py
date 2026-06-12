"""
数据库初始化辅助函数

提供应用启动时自动建表的能力，适用于开发环境快速启动。
生产环境建议使用 Alembic 迁移脚本管理 schema 变更。
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, text

from app.config import settings
from app.database import Base, async_engine

logger = logging.getLogger(__name__)


_DEFAULT_CONFIGS = [
    # ========== SQL Server 连接配置 ==========
    {
        "key": "mssql_host",
        "value": "10.239.253.3",
        "desc": "SQL Server 服务器地址",
    },
    {
        "key": "mssql_port",
        "value": "1433",
        "desc": "SQL Server 端口",
    },
    {
        "key": "mssql_user",
        "value": "PowerBI",
        "desc": "SQL Server 账号",
    },
    {
        "key": "mssql_password",
        "value": "PowerBI",
        "desc": "SQL Server 密码",
    },
    {
        "key": "mssql_database",
        "value": "master",
        "desc": "SQL Server 数据库",
    },
    # ========== PostgreSQL 连接配置 ==========
    {
        "key": "pg_host",
        "value": "10.239.254.14",
        "desc": "PostgreSQL 服务器地址",
    },
    {
        "key": "pg_port",
        "value": "5432",
        "desc": "PostgreSQL 端口",
    },
    {
        "key": "pg_database",
        "value": "sv_test_db",
        "desc": "PostgreSQL 数据库名",
    },
    {
        "key": "pg_user",
        "value": "u_sv_mgt",
        "desc": "PostgreSQL 账号",
    },
    {
        "key": "pg_password",
        "value": "Sunvalleyco.com",
        "desc": "PostgreSQL 密码",
    },
    # ========== 采集与告警配置 ==========
    {
        "key": "scheduler_interval_seconds",
        "value": "60",
        "desc": "数据采集间隔（秒）",
    },
    {
        "key": "memory_alert_threshold_pct",
        "value": "85",
        "desc": "内存告警阈值（%）",
    },
    {
        "key": "memory_alert_duration_minutes",
        "value": "5",
        "desc": "内存持续超过阈值时长（分钟）后触发告警",
    },
    {
        "key": "deadlock_alert_enabled",
        "value": "true",
        "desc": "死锁告警开关",
    },
    {
        "key": "collection_interrupt_threshold",
        "value": "3",
        "desc": "连续几次采集失败后触发中断告警",
    },
    {
        "key": "alert_cooldown_minutes",
        "value": "30",
        "desc": "告警冷却期（分钟），相同告警在此期间不重复发送",
    },
    # ========== Webhook 通知配置 ==========
    {
        "key": "wecom_webhook_url",
        "value": "",
        "desc": "企业微信机器人 Webhook URL",
    },
    {
        "key": "wecom_enabled",
        "value": "false",
        "desc": "企业微信通知开关",
    },
    # ========== 多实例模式配置 ==========
    {
        "key": "mssql_instances_enabled",
        "value": "false",
        "desc": "是否启用多 SQL Server 实例监控模式（true 时从 monitored_instances 表读取实例列表）",
    },
    # ========== DeepSeek AI 配置 ==========
    {
        "key": "deepseek_api_key",
        "value": "sk-40bd88a5422c4db1acf7f566e8acd88a",
        "desc": "DeepSeek API 密钥",
    },
    {
        "key": "deepseek_model",
        "value": "deepseek-v4-flash",
        "desc": "DeepSeek 模型（deepseek-v4-flash / deepseek-v4-pro）",
    },
    # ========== SMTP 邮件配置 ==========
    {
        "key": "smtp_server",
        "value": "",
        "desc": "SMTP 邮件服务器地址",
    },
    {
        "key": "smtp_port",
        "value": "587",
        "desc": "SMTP 端口（默认 587）",
    },
    {
        "key": "smtp_user",
        "value": "",
        "desc": "SMTP 发件人账号",
    },
    {
        "key": "smtp_password",
        "value": "",
        "desc": "SMTP 发件人密码",
    },
    {
        "key": "smtp_recipients",
        "value": "",
        "desc": "告警邮件接收人（多个用逗号分隔）",
    },
    {
        "key": "smtp_enabled",
        "value": "false",
        "desc": "邮件告警开关",
    },
    # ========== 数据保留策略 ==========
    {
        "key": "data_retention_days",
        "value": "90",
        "desc": "数据保留天数（超过此天数的监控数据将被自动清理）",
    },
    # ========== 系统设置 ==========
    {
        "key": "timezone",
        "value": "Asia/Shanghai",
        "desc": "系统时区（用于日志和报表时间显示）",
    },
]


async def init_db() -> None:
    """创建所有未存在的表，并插入默认配置项"""
    try:
        from app.models import (  # noqa: F401
            AlertLog,
            DeadlockEvent,
            DeadlockSql,
            MetricRecord,
            SystemConfig,
            User,
            MonitoredInstance,
            MissingIndex,
            IndexFragmentation,
            AlertRuleModel,
            AuditLog,
            ReportRecord,
        )

        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info(
            "数据库初始化完成 - 已确保所有表存在 "
            "(tables: %s)",
            ", ".join(sorted(Base.metadata.tables.keys())),
        )

        # 执行 schema 迁移（新加字段在老表上补充）
        await _run_migrations()

        await _seed_default_configs()
        await _seed_default_admin()

    except Exception:
        logger.exception("数据库初始化失败")
        raise


async def _run_migrations() -> None:
    """执行数据库 schema 迁移"""
    try:
        async with async_engine.begin() as conn:
            # 检查 deadlocks 表是否有 analysis_result 列
            result = await conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'deadlocks' AND column_name = 'analysis_result'"
                )
            )
            if not result.first():
                await conn.execute(
                    text(
                        "ALTER TABLE deadlocks "
                        "ADD COLUMN analysis_result TEXT"
                    )
                )
                logger.info("迁移: deadlocks 表添加 analysis_result 列")
    except Exception:
        logger.exception("数据库迁移失败")


async def _seed_default_configs() -> None:
    """向 system_configs 表中插入默认配置项（若不存在则插入）"""
    try:
        async with async_engine.begin() as conn:
            for cfg in _DEFAULT_CONFIGS:
                exists = await conn.execute(
                    text(
                        "SELECT 1 FROM system_configs WHERE config_key = :key"
                    ),
                    {"key": cfg["key"]},
                )
                if not exists.first():
                    await conn.execute(
                        text(
                            "INSERT INTO system_configs "
                            "(config_key, config_value, description) "
                            "VALUES (:key, :value, :desc)"
                        ),
                        {
                            "key": cfg["key"],
                            "value": cfg["value"],
                            "desc": cfg["desc"],
                        },
                    )
                    logger.info("插入默认配置: %s = %s", cfg["key"], cfg["value"])

        logger.info("系统配置默认值初始化完成")
    except Exception:
        logger.exception("插入系统配置默认值失败")


async def _seed_default_admin() -> None:
    """创建默认超级管理员账号（若不存在）

    用户名/密码取自配置：DEFAULT_ADMIN_USERNAME / DEFAULT_ADMIN_PASSWORD
    """
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.models import User, UserRole
        from app.services.auth_service import hash_password

        username = settings.DEFAULT_ADMIN_USERNAME
        password = settings.DEFAULT_ADMIN_PASSWORD

        async with AsyncSession(async_engine) as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                admin = User(
                    username=username,
                    password_hash=hash_password(password),
                    role=UserRole.SUPER_ADMIN.value,
                    full_name="超级管理员",
                    is_active=True,
                )
                session.add(admin)
                await session.commit()
                logger.info(
                    "已创建默认超级管理员账号: %s（请尽快修改默认密码）",
                    username,
                )
            else:
                # 确保超级管理员角色不变
                if existing.role != UserRole.SUPER_ADMIN.value:
                    existing.role = UserRole.SUPER_ADMIN.value
                    await session.commit()
                    logger.info("已修复账号 %s 的超级管理员角色", username)
                else:
                    logger.info("超级管理员账号 %s 已存在，跳过创建", username)
    except Exception:
        logger.exception("创建默认超级管理员账号失败")


async def drop_all_tables() -> None:
    """删除所有表（危险操作！）

    仅用于测试环境清理，生产环境禁止调用。
    """
    logger.warning("⚠️  正在删除所有数据库表 - 此操作不可逆！")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("所有表已删除")
