"""
FastAPI 应用启动入口
SQL 监控平台后端服务
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import api_router
from app.init_db import init_db
from app.scheduler import SchedulerManager

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
scheduler = SchedulerManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化资源，关闭时清理"""
    await init_db()
    scheduler.setup(app, settings)
    scheduler.start()
    logger.info("应用启动完成，调度器已启动")
    yield
    scheduler.stop()
    logger.info("应用关闭，调度器已停止")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SQL 监控平台 - 数据库查询性能监控与分析",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册 API 路由（所有接口挂载在 /api 前缀下）
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": settings.PROJECT_NAME}
