# SQL 监控平台

基于 **FastAPI + Vue 3 + PostgreSQL** 的 **MS SQL Server 性能监控与告警平台**，帮助 DBA 和开发人员实时掌握 SQL Server 的运行状态。

---

## 功能特性

| 模块 | 功能 |
|------|-----|
| **性能监控** | 实时采集 CPU / 内存 / 连接 / IO / 锁等待 / 批处理请求（7 大类 28 项指标） |
| **死锁检测** | 自动捕获死锁事件，支持 DeepSeek AI 分析获取优化建议 |
| **慢查询分析** | TOP 20 慢查询识别，支持 MD5 哈希去重聚合 |
| **阻塞链追踪** | 实时监控 SQL Server 阻塞进程链，记录阻塞历史 |
| **磁盘空间监控** | 数据库文件空间使用情况与历史趋势 |
| **索引分析** | 缺失索引建议 + 索引碎片分析 |
| **多实例支持** | 同时监控多个 SQL Server 实例，数据隔离 |
| **告警系统** | 自定义告警规则 + 邮件 / 钉钉 / 企业微信通知 |
| **系统报告** | 基于监控数据生成性能分析报告，支持 AI 摘要 + PDF 导出 |
| **在线升级** | 一键从 GitHub 更新代码 |

---

## 快速开始

### 环境要求

| 组件 | 版本要求 |
|------|---------|
| Docker | ≥ 20.10（推荐 Docker Desktop 4.x+） |
| Docker Compose | ≥ 2.0 |
| Python（本地开发） | ≥ 3.12 |
| Node.js（本地开发） | ≥ 20 |

### Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd sql-monitor-platform

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写数据库连接信息

# 3. 启动服务（首次会自动构建镜像）
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

### 本地开发模式

**后端：**
```bash
cd backend
pip install -r requirements.txt
# 复制 .env 并将 PG_HOST 改为 127.0.0.1
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | 监控平台 Web UI |
| API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 后端 API | http://localhost:8000 | RESTful API 端点 |

### 默认账号

- **用户名**：`Admin`
- **密码**：`Chuz0001`

> ⚠️ 请在首次登录后立即修改默认密码。

---

## 项目结构

```
.
├── backend/                # FastAPI 后端服务
│   ├── app/
│   │   ├── collectors/     # 数据采集器（7 大类指标 + 慢查询 + 死锁 + 阻塞）
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── routers/        # API 路由（17 个模块）
│   │   ├── services/       # 业务服务（告警/认证/通知/AI）
│   │   ├── config.py       # 配置管理（Settings）
│   │   ├── main.py         # 应用入口
│   │   └── scheduler.py    # APScheduler 定时任务
│   ├── alembic/            # 数据库迁移脚本
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # Axios API 封装
│   │   ├── components/     # 公共组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理（Pinia）
│   │   ├── styles/         # 全局样式
│   │   ├── utils/          # 工具函数
│   │   ├── views/          # 页面组件（Dashboard/Trends/...）
│   │   ├── App.vue
│   │   └── main.js
│   ├── Dockerfile
│   ├── index.html
│   └── vite.config.js
├── Docs/                   # 项目文档
│   ├── PROJECT_DOCUMENTATION.md   # 项目概览与部署指南
│   ├── TECHNICAL_DOCUMENTATION.md # 技术架构与实现细节
│   └── 指标监控说明文档.md         # 指标详解与告警体系
├── docker-compose.yml      # Docker Compose 编排
├── .env.example            # 环境变量模板
├── deploy.sh               # 部署脚本（Linux/Mac）
└── deploy.ps1              # 部署脚本（Windows）
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | FastAPI（Python 3.12+） |
| **ASGI 服务器** | Uvicorn |
| **ORM** | SQLAlchemy 2.0 |
| **数据库** | PostgreSQL 16 |
| **目标数据库** | MS SQL Server（2008 R2+，建议 2016+） |
| **定时任务** | APScheduler（默认 60 秒采集一次） |
| **前端框架** | Vue 3（Composition API） |
| **构建工具** | Vite 5 |
| **图表库** | Apache ECharts 5 |
| **容器化** | Docker + Docker Compose |
| **反向代理** | Nginx |
| **通知渠道** | SMTP 邮件 / 钉钉 Webhook / 企业微信 Webhook |
| **AI 分析** | DeepSeek LLM（可选） |

---

## 文档

完整文档请参阅 [Docs](./Docs/) 目录：

- **[项目文档](./Docs/PROJECT_DOCUMENTATION.md)** — 项目概述、部署指南、API 接口说明、数据库设计
- **[技术文档](./Docs/TECHNICAL_DOCUMENTATION.md)** — 架构分层、核心模块实现、API 设计规范、运维安全、故障排查
- **[指标监控说明](./Docs/指标监控说明文档.md)** — 28 项性能指标详解、专项监控、告警体系、诊断与问题排查

---

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除数据卷（⚠️ 会清空 PostgreSQL 数据，请谨慎）
docker-compose down -v

# 查看实时日志
docker-compose logs -f

# 仅查看后端日志
docker-compose logs -f backend

# 重新构建并启动
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 进入后端容器
docker-compose exec backend bash

# 查看 PostgreSQL 表
docker-compose exec postgres psql -U postgres -d sql_monitor
```

---

## 安全注意事项

1. **默认密码**：务必在首次登录后修改 `Admin` 账号的默认密码 `Chuz0001`
2. **环境变量**：`.env` 文件包含敏感信息，权限应设置为 `600`，切勿提交到版本控制
3. **生产环境**：务必修改 `JWT_SECRET_KEY` 为随机字符串（建议 ≥ 32 字符）
4. **HTTPS**：生产环境前端建议使用 HTTPS（通过 Nginx 配置 SSL 证书）
5. **SQL Server 监控账号**：建议使用最小权限原则（`VIEW SERVER STATE`），不要使用 sa

---

## 版本

当前版本：**v1.0.11**

---

## 许可证

MIT License
