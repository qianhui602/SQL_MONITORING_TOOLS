"""
PostgreSQL 异步数据库连接管理

使用 SQLAlchemy 2.0 异步引擎 + asyncpg 驱动
提供 session 工厂和依赖注入函数
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步引擎
async_engine = create_async_engine(
    settings.PG_DSN,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=10,
)

# 异步 session 工厂
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基类，所有模型继承此类"""
    pass


async def get_db(read_only: bool = False) -> AsyncSession:
    """FastAPI 依赖注入：获取数据库 session

    使用 async generator 确保请求结束后正确归还 session 到连接池。

    Args:
        read_only: 是否为只读请求，只读请求不执行 commit
    """
    async with async_session_factory() as session:
        try:
            yield session
            if not read_only:
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_readonly_db() -> AsyncSession:
    """FastAPI 依赖注入：获取只读数据库 session

    只读请求不执行 commit，减少不必要的数据库交互开销。
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
