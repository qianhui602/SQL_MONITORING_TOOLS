# SQL 监控平台

基于 FastAPI + Vue.js + PostgreSQL 的 MS SQL Server 性能监控与告警平台。

## 功能特性

### 核心监控
- **性能监控**：CPU、内存、连接数、I/O、锁等待、批处理请求等 28 项指标
- **SQL 断联监控**：主动检测 SQL Server 连接状态，断开/恢复时自动告警
- **死锁检测**：自动捕获死锁事件，支持 DeepSeek AI 分析
- **慢查询分析**：TOP 20 慢查询识别与统计
- **阻塞链追踪**：实时监控 SQL Server 阻塞进程
- **磁盘空间监控**：数据库文件空间使用情况
- **索引分析**：缺失索引建议与碎片分析
- **多实例支持**：同时监控多个 SQL Server 实例

### 告警与通知
- **告警系统**：自定义告警规则，支持企业微信通知
- **声音提醒**：新告警声音通知，支持静音开关
- **连接状态告警**：实例离线/恢复自动触发告警

### 用户与权限
- **角色权限**：超级管理员、管理员、只读用户三种角色
- **密码找回**：通过邮箱验证码重置密码
- **个人设置**：用户可修改姓名、邮箱等个人信息

### 系统功能
- **在线升级**：支持通过管理后台一键升级
- **安装引导**：首次部署提供可视化引导流程
- **品牌定制**：支持自定义系统标题和 Logo
- **深色模式**：支持深色/浅色主题切换

### UI 特性
- **现代化设计**：玻璃拟态风格、渐变装饰、微交互动画
- **响应式布局**：适配桌面端和平板设备
- **实时数据刷新**：可配置自动刷新间隔（5秒/10秒/30秒/60秒）
- **自定义仪表盘**：统计卡片和图表支持显示/隐藏和排序

## 快速开始

### 环境要求

- **Docker** >= 20.10（推荐 Docker Desktop 4.x+）
- **Docker Compose** >= 2.0（Docker Desktop 已内置）
- **Python** >= 3.12（本地开发模式）
- **Node.js** >= 20（本地开发模式）

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd SQL监控平台

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库连接信息

# 3. 启动服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 本地开发

**后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | 监控平台 Web UI |
| API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 后端 API | http://localhost:8000 | RESTful API 端点 |

## 项目结构

```
.
├── backend/              # FastAPI 后端服务
│   ├── app/              # 应用代码
│   │   ├── collectors/   # 指标采集器
│   │   ├── models/       # 数据模型
│   │   ├── routers/      # API 路由
│   │   └── services/     # 业务服务
│   ├── Dockerfile        # 后端 Docker 构建文件
│   └── requirements.txt  # Python 依赖
├── frontend/             # Vue.js 前端
│   ├── src/              # 前端源码
│   │   ├── views/        # 页面组件
│   │   │   ├── ForgotPassword.vue  # 找回密码
│   │   │   ├── ResetPassword.vue   # 重置密码
│   │   │   ├── Profile.vue         # 个人设置
│   │   │   └── Setup.vue           # 安装引导
│   │   ├── components/   # 公共组件
│   │   └── api/          # API 接口
│   ├── Dockerfile        # 前端 Docker 构建文件
│   └── package.json      # Node.js 依赖
├── Docs/                 # 项目文档
│   ├── PROJECT_DOCUMENTATION.md    # 项目文档
│   ├── TECHNICAL_DOCUMENTATION.md  # 技术文档
│   └── 指标监控说明文档.md          # 指标监控说明
├── docker-compose.yml    # Docker Compose 编排文件
└── .env                  # 环境变量配置
```

## 文档

详细文档请参阅 [Docs](./Docs/) 目录：

- [项目文档](./Docs/PROJECT_DOCUMENTATION.md) - 项目概述、功能模块、使用说明
- [技术文档](./Docs/TECHNICAL_DOCUMENTATION.md) - 技术架构、API 设计、部署架构
- [用户手册](./Docs/USER_MANUAL.md) - 系统操作指南、功能使用说明
- [指标监控说明](./Docs/指标监控说明文档.md) - 监控指标详解、采集机制、数据存储

## 默认账号

- 用户名：`Admin`
- 密码：`Chuz0001`

> 请在首次登录后修改默认密码。

## 功能说明

- **密码找回**：在登录页点击"忘记密码"，输入注册邮箱获取验证码，凭验证码设置新密码
- **个人设置**：点击右上角用户菜单 → "个人设置"，可修改姓名和邮箱
- **安装引导**：首次部署访问时自动进入安装向导，引导完成数据库初始化和管理员账号创建
- **声音提醒**：顶部栏铃铛图标可查看通知，支持开启/关闭声音提醒

## 升级指南

系统会自动检测是否有新版本可用。当发现新版本时，侧边栏底部版本号会显示黄色圆点提示，页面底部也会弹出升级通知横幅。

### 手动升级步骤

#### Docker 部署升级（推荐）

```bash
# 1. 进入项目目录
cd SQL_MONITORING_TOOLS

# 2. 拉取最新代码
git pull origin master

# 3. 重新构建并启动容器（数据自动保留）
docker-compose up -d --build

# 4. 验证服务状态
docker-compose ps
```

#### 本地开发环境升级

```bash
# 1. 进入项目目录
cd SQL_MONITORING_TOOLS

# 2. 拉取最新代码
git pull origin master

# 3. 升级后端依赖
cd backend
pip install -r requirements.txt

# 4. 升级前端依赖
cd ../frontend
npm install

# 5. 重启后端服务
cd ../backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. 重启前端开发服务器（另一个终端）
cd frontend
npm run dev
```

### 升级注意事项

| 项目 | 说明 |
|------|------|
| 数据库 | 升级会自动执行数据库迁移，无需手动操作 |
| 配置文件 | 已有的系统配置（品牌、告警规则等）会保留 |
| 用户数据 | 所有用户账号、审计日志不会丢失 |
| Docker 卷 | 使用 Docker 部署时数据存储在卷中，容器重建不会丢失 |

### 升级脚本

可以将以下脚本保存为 `upgrade.sh`（Linux/Mac）或 `upgrade.bat`（Windows）快速升级：

**Linux/Mac (`upgrade.sh`)**

```bash
#!/bin/bash
echo "=== SQL 监控平台升级脚本 ==="
echo ""

# 拉取最新代码
echo "[1/4] 拉取最新代码..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ 代码拉取失败，请检查网络连接"
    exit 1
fi

# 检测部署方式
if [ -f "docker-compose.yml" ] && command -v docker &> /dev/null; then
    echo "[2/4] 检测到 Docker 部署，重新构建..."
    docker-compose up -d --build
    echo "[3/4] 清理旧镜像..."
    docker image prune -f
    echo "[4/4] 验证服务状态..."
    docker-compose ps
else
    echo "[2/4] 检测到本地部署，安装依赖..."
    cd backend && pip install -r requirements.txt
    cd ../frontend && npm install
    echo "[3/4] 依赖安装完成"
    echo "[4/4] 请手动重启后端和前端服务"
fi

echo ""
echo "✅ 升级完成！"
```

**Windows (`upgrade.bat`)**

```bat
@echo off
echo === SQL 监控平台升级脚本 ===
echo.

echo [1/4] 拉取最新代码...
git pull origin master
if %errorlevel% neq 0 (
    echo ❌ 代码拉取失败，请检查网络连接
    pause
    exit /b 1
)

echo [2/4] 检测部署方式...
if exist "docker-compose.yml" (
    echo 检测到 Docker 部署，重新构建...
    docker-compose up -d --build
    echo [3/4] 清理旧镜像...
    docker image prune -f
    echo [4/4] 验证服务状态...
    docker-compose ps
) else (
    echo 检测到本地部署，安装依赖...
    cd backend && pip install -r requirements.txt
    cd ../frontend && npm install
    echo [3/4] 依赖安装完成
    echo [4/4] 请手动重启后端和前端服务
)

echo.
echo ✅ 升级完成！
pause
```

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重新构建
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

## 许可证

MIT License
