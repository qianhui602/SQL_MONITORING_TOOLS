# ============================================
# SQL 监控平台 - Docker 一键部署脚本 (Windows)
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SQL 监控平台 - Docker 部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "[INFO] 未找到 .env 文件，正在从模板创建..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[WARN] 请编辑 .env 文件，填写实际的数据库密码等配置" -ForegroundColor Yellow
    Write-Host "[WARN] 然后重新运行此脚本" -ForegroundColor Yellow
    exit 1
}

# 构建并启动
Write-Host "[1/3] 构建 Docker 镜像..." -ForegroundColor Green
docker-compose build --no-cache

Write-Host "[2/3] 启动服务..." -ForegroundColor Green
docker-compose up -d

Write-Host "[3/3] 等待服务就绪..." -ForegroundColor Green
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  服务状态" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  前端界面:  http://localhost:3000"
Write-Host "  后端 API:  http://localhost:8000"
Write-Host "  API 文档:  http://localhost:8000/docs"
Write-Host "  默认账号:  Admin / Chuz0001"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "常用命令：" -ForegroundColor Yellow
Write-Host "  查看日志:  docker-compose logs -f"
Write-Host "  停止服务:  docker-compose down"
Write-Host "  重启服务:  docker-compose restart"
Write-Host "  更新部署:  docker-compose up -d --build"
