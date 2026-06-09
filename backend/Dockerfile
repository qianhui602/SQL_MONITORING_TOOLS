# ============================================
# SQL 监控平台 - 后端 Dockerfile
# ============================================
# 多阶段构建：先安装依赖，再运行应用
# ============================================

# ---------- 第一阶段：依赖安装 ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装系统依赖（asyncpg 和 pymssql 需要编译依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    freetds-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- 第二阶段：运行阶段 ----------
FROM python:3.12-slim

WORKDIR /app

# 仅安装运行时所需的系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libct4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制第一阶段安装的 Python 包
COPY --from=builder /root/.local /root/.local

# 确保 PATH 包含用户安装的包
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
