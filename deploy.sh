#!/bin/bash
# ============================================
# SQL 监控平台 - Docker 一键部署脚本
# ============================================

set -e

echo "=========================================="
echo "  SQL 监控平台 - Docker 部署"
echo "=========================================="

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "[INFO] 未找到 .env 文件，正在从模板创建..."
    cp .env.example .env
    echo "[WARN] 请编辑 .env 文件，填写实际的数据库密码等配置"
    echo "[WARN] 然后重新运行此脚本"
    exit 1
fi

# 构建并启动
echo "[1/3] 构建 Docker 镜像..."
docker-compose build --no-cache

echo "[2/3] 启动服务..."
docker-compose up -d

echo "[3/3] 等待服务就绪..."
sleep 10

# 检查服务状态
echo ""
echo "=========================================="
echo "  服务状态"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo "  前端界面:  http://localhost:3000"
echo "  后端 API:  http://localhost:8000"
echo "  API 文档:  http://localhost:8000/docs"
echo "  默认账号:  Admin / Chuz0001"
echo "=========================================="
echo ""
echo "常用命令："
echo "  查看日志:  docker-compose logs -f"
echo "  停止服务:  docker-compose down"
echo "  重启服务:  docker-compose restart"
echo "  更新部署:  docker-compose up -d --build"
