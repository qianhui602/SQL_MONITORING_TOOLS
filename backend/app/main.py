"""
FastAPI 应用启动入口
SQL 监控平台后端服务
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# CORS 中间件配置（限制 methods 和 headers）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    max_age=86400,
)


# 安全 HTTP 头中间件
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# 注册 API 路由（所有接口挂载在 /api 前缀下）
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": settings.PROJECT_NAME}


# ===== 全局异常处理器（错误信息脱敏）=====

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("请求参数校验失败: %s", exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "请求参数格式错误"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("服务器内部错误: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误，请稍后重试"},
    )
