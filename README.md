# MS SQL Server 监控平台部署说明

基于 FastAPI + Vue.js + PostgreSQL 的 MS SQL Server 性能监控与告警平台。

## 环境要求

- **Docker** >= 20.10（推荐 Docker Desktop 4.x+）
- **Docker Compose** >= 2.0（Docker Desktop 已内置）
- **Python** >= 3.12（本地开发模式）
- **Node.js** >= 20（本地开发模式）

## 目录结构

```
.
├── backend/              # FastAPI 后端服务
│   ├── app/              # 应用代码
│   ├── Dockerfile        # 后端 Docker 构建文件
│   ├── .env.example      # 后端环境变量模板
│   └── requirements.txt  # Python 依赖
├── frontend/             # Vue.js 前端
│   ├── src/              # 前端源码
│   ├── Dockerfile        # 前端 Docker 构建文件
│   └── package.json      # Node.js 依赖
├── docker-compose.yml    # Docker Compose 编排文件
├── .env.example          # 环境变量模板（项目根目录）
└── .env                  # 环境变量配置（需自行创建）
```

## 配置说明

### 1. 创建环境变量文件

复制项目根目录的 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

### 2. 配置项说明

| 配置项 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| **项目基础信息** | | | |
| `PROJECT_NAME` | 项目名称 | SQL 监控平台 | |
| `DEBUG` | 调试模式开关 | false | 生产环境设为 false |
| `CORS_ORIGINS` | 允许的跨域来源 | ["http://localhost:3000"] | JSON 数组格式 |
| **PostgreSQL 配置** | | | |
| `PG_HOST` | 数据库主机地址 | postgres | Docker 部署使用服务名；外部 PG 改为实际 IP |
| `PG_PORT` | 数据库端口 | 5432 | |
| `PG_USER` | 数据库用户 | postgres | |
| `PG_PASSWORD` | 数据库密码 | （必填） | 请设置为强密码 |
| `PG_DATABASE` | 数据库名称 | sql_monitor | |
| **SQL Server 配置** | | | |
| `MSSQL_HOST` | SQL Server 主机地址 | 127.0.0.1 | 被监控的目标数据库 |
| `MSSQL_PORT` | SQL Server 端口 | 1433 | |
| `MSSQL_USER` | SQL Server 用户 | sa | |
| `MSSQL_PASSWORD` | SQL Server 密码 | （必填） | |
| `MSSQL_DATABASE` | 默认监控数据库 | master | |
| **定时任务** | | | |
| `SCHEDULER_INTERVAL_SECONDS` | 采集间隔（秒） | 60 | |
| **邮件通知（SMTP）** | | | |
| `SMTP_SERVER` | SMTP 服务器地址 | smtp.example.com | |
| `SMTP_PORT` | SMTP 端口 | 587 | 使用 TLS |
| `SMTP_USER` | SMTP 用户名 | （可选） | |
| `SMTP_PASSWORD` | SMTP 密码 | （可选） | |
| `ALERT_EMAILS` | 告警接收邮箱列表 | [] | JSON 数组格式 |
| **钉钉通知** | | | |
| `DINGTALK_WEBHOOK_URL` | 钉钉机器人 Webhook 地址 | （可选） | 为空则不启用 |
| **日志** | | | |
| `LOG_LEVEL` | 日志级别 | INFO | DEBUG / INFO / WARNING / ERROR |

## 本地开发启动

### 后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建并配置环境变量
cp .env.example .env
# 编辑 .env，将 PG_HOST 改为 127.0.0.1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动开发服务器（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器（热重载）
npm run dev
```

## Docker 部署

### 1. 准备环境变量

```bash
# 从模板创建环境变量文件
cp .env.example .env
```

编辑 `.env` 文件，填写实际的数据库连接信息。

### 2. 启动服务

```bash
# 构建并启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 单独查看某服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 3. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（会清空 PostgreSQL 数据）
docker-compose down -v
```

### 4. 重新构建

```bash
# 更新代码后重新构建镜像
docker-compose build

# 或查看构建缓存重新构建
docker-compose build --no-cache
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端界面** | http://localhost:3000 | 监控平台 Web UI |
| **API 文档** | http://localhost:8000/docs | Swagger UI 交互式文档 |
| **API 文档（备选）** | http://localhost:8000/redoc | ReDoc 格式文档 |
| **API 基础地址** | http://localhost:8000 | RESTful API 端点 |
| **PostgreSQL** | localhost:5432 | 数据库直连（仅限宿主机） |

## 注意事项

1. **首次启动**：PostgreSQL 首次启动需要初始化数据，大约需要 10-20 秒，后端服务会自动等待数据库就绪。
2. **密码安全**：请务必修改 `.env` 中的默认密码，尤其是 `PG_PASSWORD` 和 `MSSQL_PASSWORD`。
3. **数据持久化**：PostgreSQL 数据存储在 Docker 数据卷 `sql-monitor-pgdata` 中，`docker-compose down` 不会删除数据；使用 `docker-compose down -v` 会清空所有数据。
4. **日志查看**：生产环境建议配置日志收集（如 ELK / Loki）以便集中管理日志。
5. **健康检查**：后端服务依赖 PostgreSQL 的健康检查，确保数据库就绪后才启动。
