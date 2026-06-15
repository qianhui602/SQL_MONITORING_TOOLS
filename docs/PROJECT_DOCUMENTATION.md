# SQL 监控平台 — 项目文档

## 一、项目概述

### 1.1 项目简介

SQL 监控平台是一套基于 **FastAPI + Vue 3 + PostgreSQL** 的 **MS SQL Server 性能监控与告警平台**。该平台提供实时指标监控、历史趋势分析、死锁检测、慢查询分析、阻塞链追踪、磁盘空间监控、索引分析、告警管理与系统报告等功能，帮助 DBA 和开发人员全面掌握 SQL Server 的运行状态。

### 1.2 项目目标

- 实时监控 SQL Server 的关键性能指标（CPU、内存、连接数、IO 等 28 项指标）
- 自动检测并分析死锁事件，支持 AI 智能分析
- 识别和分析 TOP 20 慢查询，记录执行统计
- 提供灵活的告警规则配置与多渠道通知（邮件 / 钉钉 / 企业微信）
- 支持多 SQL Server 实例统一监控
- 提供直观的数据可视化和报告功能（含 PDF 导出）
- 支持在线一键升级

### 1.3 主要功能模块

| 模块 | 功能描述 | 核心路由 |
|------|---------|---------|
| **仪表盘** | 实时关键指标卡片 + 关键趋势图 | `Dashboard.vue` |
| **性能趋势** | 按分类查看 7 大类历史指标曲线，支持对比 | `Trends.vue` |
| **死锁监控** | 死锁事件列表 + 详情 + 一键 AI 分析 | `Deadlocks.vue` |
| **慢查询分析** | TOP 20 慢查询及执行统计、SQL 文本 | `SlowQueries.vue` |
| **阻塞进程** | 实时阻塞链 + 历史阻塞记录 | `Blocking.vue` |
| **磁盘空间** | 数据库文件空间使用情况与历史趋势 | `Disk.vue` |
| **索引分析** | 缺失索引建议 + 索引碎片化分析 | `Indexes.vue` |
| **告警管理** | 告警事件查看、确认、通知状态 | `Alerts.vue` |
| **告警规则** | 内置规则 + 自定义规则管理、静默时段 | `AlertRules.vue` |
| **实例管理** | 多 SQL Server 实例配置与连接测试 | `Instances.vue` |
| **用户管理** | 角色与账号管理（超级管理员 / 管理员 / 只读用户） | `Users.vue` |
| **审计日志** | 记录用户关键操作，支持按条件筛选 | `AuditLogs.vue` |
| **系统设置** | SQL Server 连接、采集间隔、通知渠道配置 | `Settings.vue` |
| **系统报告** | 基于监控数据的性能分析报告，支持 AI 分析与 PDF 导出 | `Report.vue` |
| **在线升级** | 检查 GitHub 新版本并执行一键升级 | `Upgrade.vue` |

### 1.4 用户角色与权限

| 角色 | 说明 | 权限 |
|------|------|------|
| `super_admin`（超级管理员） | 拥有系统最高权限，不可删除 | 全部操作 + 用户管理 + 系统设置 + 在线升级 |
| `admin`（管理员） | 业务管理员 | 数据查看、告警/规则/实例配置、报告生成 |
| `viewer`（只读用户） | 只读访问 | 查看监控数据、告警、报告 |

### 1.5 系统架构总览

```
┌──────────────────────────────┐
│   Vue 3 前端 (Nginx 托管)    │
│  ┌──────────────────────────┐│
│  │ Dashboard / Trends / ... ││
│  └──────────────────────────┘│
└──────────────┬───────────────┘
               │ HTTP/HTTPS (Axios)
               ▼
┌──────────────────────────────┐
│     FastAPI 后端服务          │
│  ┌─────────────────────────┐ │
│  │  Routers (API 路由层)    │ │
│  │  Services (业务逻辑层)   │ │
│  │  Collectors (数据采集层) │ │
│  │  Models (数据模型层)     │ │
│  │  Scheduler (定时调度)    │ │
│  └─────────────────────────┘ │
└──────────────┬───────────────┘
               │
        ┌──────┴───────┐
        ▼              ▼
┌────────────┐  ┌──────────────┐
│ PostgreSQL │  │  SQL Server  │
│ (监控存储) │  │ (被监控目标) │
└────────────┘  └──────────────┘
```

---

## 二、快速开始

### 2.1 环境要求

| 组件 | 版本要求 |
|------|---------|
| Docker | ≥ 20.10（推荐 Docker Desktop 4.x+） |
| Docker Compose | ≥ 2.0 |
| Python（本地开发） | ≥ 3.12 |
| Node.js（本地开发） | ≥ 20 |
| PostgreSQL | 16（容器内自动部署） |
| SQL Server（被监控） | 2008 R2 及以上（推荐 2016+） |

### 2.2 Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd sql-monitor-platform

# 2. 复制并修改环境变量
cp .env.example .env
# 编辑 .env 文件，填写 PostgreSQL 与 SQL Server 连接信息

# 3. 启动服务（首次会自动构建镜像）
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

### 2.3 本地开发模式

**后端启动：**

```bash
cd backend
pip install -r requirements.txt
# 复制并修改 .env，将 PG_HOST 改为 127.0.0.1
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端启动：**

```bash
cd frontend
npm install
npm run dev
```

### 2.4 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | 监控平台 Web UI |
| API 文档 | http://localhost:8000/docs | Swagger UI 交互式文档 |
| 后端 API | http://localhost:8000 | RESTful API 端点（统一前缀 `/api`） |
| 健康检查 | http://localhost:8000/health | `{"status": "ok", ...}` |

### 2.5 默认账号

- **用户名**：`Admin`
- **密码**：`Chuz0001`

> ⚠️ 请在首次登录后立即修改默认密码。

---

## 三、功能模块详细说明

### 3.1 仪表盘（Dashboard）

- **关键指标卡片**：CPU 使用率、SQL Server 内存、活跃连接数、缓存命中率、页预期生存时间、锁等待数
- **死锁/告警统计**：死锁事件计数、最新告警摘要
- **性能趋势图表**：支持按时间范围查看，支持与昨日/上周/上月对比
- **自定义排序**：支持调整卡片展示顺序

### 3.2 性能趋势（Trends）

- **按分类查看**：CPU、内存、连接、IO、OS 内存、锁等待、批处理请求 7 大类
- **自定义时间范围**：支持任意时间窗口选择
- **多指标对比**：支持在同一图表中叠加多个指标曲线

### 3.3 死锁监控（Deadlocks）

- **死锁事件列表**：死锁发生时间、受害者会话、涉及对象、server_address
- **死锁详情**：完整 deadlock XML、参与会话的 SQL 语句、事务隔离级别
- **AI 分析**：一键调用 DeepSeek LLM 分析死锁原因，给出优化建议

### 3.4 慢查询分析（SlowQueries）

- **TOP 20 慢查询**：基于 `total_elapsed_ms` 排序
- **SQL 文本去重**：MD5 哈希聚合相同语句
- **执行统计**：执行次数、总 CPU 时间、总逻辑读、平均耗时、最后执行时间

### 3.5 阻塞进程（Blocking）

- **实时阻塞**：当前阻塞链，显示阻塞源会话与被阻塞会话
- **关键信息**：`blocking_session_id`、`blocked_session_id`、`wait_type`、`wait_time_ms`、阻塞/被阻塞 SQL
- **历史记录**：保留历史阻塞事件快照

### 3.6 磁盘空间（Disk）

- **数据库文件使用率**：ROWS / LOG 文件大小、已用空间、可用空间、使用率%
- **历史趋势**：查看磁盘空间使用变化

### 3.7 索引分析（Indexes）

- **缺失索引建议**：SQL Server DMV 自动建议，按 `avg_user_impact` 排序
- **索引碎片化**：显示索引碎片率 > 5% 且页数 > 100 的索引，提示重建/重组

### 3.8 告警管理（Alerts）

- **告警列表**：告警类型、严重级别（low / medium / high / critical）、触发时间、消息正文
- **告警确认**：支持手动确认告警
- **通知状态**：显示通知是否已成功发送

### 3.9 告警规则（AlertRules）

- **内置规则**：
  - 内存使用率过高（critical，冷却 10 分钟）
  - 死锁检测（high，冷却 5 分钟）
  - 采集中断（high，冷却 15 分钟）
- **自定义规则**：
  - 指标选择（分类 + 指标名）
  - 条件运算符：`>` / `<` / `>=` / `<=` / `=`
  - 阈值设置
  - 严重级别设置
  - 静默时段（指定时间段内不触发告警）
- **启用/禁用**：每条规则可独立开关

### 3.10 实例管理（Instances）

- **多实例支持**：同时监控多台 SQL Server
- **实例配置**：名称、主机、端口、用户名、密码、默认数据库、描述
- **连接测试**：保存前可测试连接
- **独立采集**：每个活跃实例使用独立连接采集

### 3.11 用户管理（Users）

- 用户列表、创建、编辑、删除
- 角色分配（super_admin / admin / viewer）
- 密码修改（bcrypt 加密存储）

### 3.12 审计日志（AuditLogs）

- 记录用户登录、配置变更、规则变更等关键操作
- 支持按时间范围、用户、操作类型筛选

### 3.13 系统设置（Settings）

- SQL Server 连接配置（单实例模式）
- 采集间隔（秒）
- 通知渠道：SMTP 邮件 / 钉钉 Webhook / 企业微信 Webhook

### 3.14 系统报告（Report）

- 基于监控数据生成的完整性能分析报告
- AI 智能分析（DeepSeek）
- 报告历史保存
- PDF 导出

---

## 四、技术栈

### 4.1 后端

| 类别 | 技术 | 版本 |
|------|------|------|
| 编程语言 | Python | 3.12+ |
| Web 框架 | FastAPI | 0.115+ |
| ASGI 服务器 | Uvicorn | 最新 |
| ORM | SQLAlchemy | 2.0+ |
| PostgreSQL 异步驱动 | asyncpg | 最新 |
| SQL Server 驱动 | pymssql | 最新 |
| 数据库迁移 | Alembic | 最新 |
| 定时任务 | APScheduler | 3.10+ |
| 配置管理 | pydantic-settings | 2.0+ |
| 密码哈希 | bcrypt | 最新 |
| JWT 认证 | PyJWT | 2.8+ |
| HTTP 客户端 | httpx | 最新 |

### 4.2 前端

| 类别 | 技术 |
|------|------|
| 前端框架 | Vue 3（Composition API） |
| 路由 | Vue Router 4 |
| 构建工具 | Vite 5 |
| HTTP 客户端 | Axios |
| 图表库 | Apache ECharts 5 |
| 组件库 | Element Plus（或同类 UI） |
| PDF 导出 | html2canvas + jsPDF |

### 4.3 数据库

- **PostgreSQL 16**：主数据库，存储监控数据、告警、用户、配置
- **SQL Server**：被监控的目标数据库（通过 DMV 读取，无写入操作）

### 4.4 部署

- **Docker** 容器化
- **Docker Compose** 多容器编排（backend + frontend + postgres）
- **Nginx**：前端静态文件服务 + 反向代理
- 版本号：`1.0.11`（`backend/app/config.py` 中 `VERSION`）

---

## 五、环境变量配置（.env）

完整配置清单（见 `backend/app/config.py`）：

```dotenv
# ========== 项目基础信息 ==========
PROJECT_NAME=SQL 监控平台
DEBUG=false
CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_URL=

# ========== PostgreSQL（存储监控数据和配置） ==========
PG_HOST=postgres
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=your_password_here
PG_DATABASE=sql_monitor

# ========== SQL Server（被监控的目标数据库） ==========
MSSQL_HOST=127.0.0.1
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=your_password_here
MSSQL_DATABASE=master

# ========== 定时任务 ==========
SCHEDULER_INTERVAL_SECONDS=60

# ========== 告警通知 ==========
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
ALERT_EMAILS=[]

DINGTALK_WEBHOOK_URL=
FEISHU_WEBHOOK_URL=

# ========== GitHub 升级 ==========
GITHUB_TOKEN=

# ========== 日志 ==========
LOG_LEVEL=INFO

# ========== 认证 / JWT ==========
JWT_SECRET_KEY=sql-monitor-secret-key-change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# ========== 默认管理员 ==========
DEFAULT_ADMIN_USERNAME=Admin
DEFAULT_ADMIN_PASSWORD=Chuz0001
```

---

## 六、运行时配置（system_configs 表）

系统还支持通过数据库 `system_configs` 表存储**运行时配置**，包括：

| 配置键 | 含义 | 对应 env 变量 |
|--------|------|--------------|
| `mssql_host` | SQL Server 主机 | MSSQL_HOST |
| `mssql_port` | SQL Server 端口 | MSSQL_PORT |
| `mssql_user` | SQL Server 用户名 | MSSQL_USER |
| `mssql_password` | SQL Server 密码 | MSSQL_PASSWORD |
| `mssql_database` | 默认数据库 | MSSQL_DATABASE |
| `scheduler_interval_seconds` | 采集间隔 | SCHEDULER_INTERVAL_SECONDS |
| `mssql_instances_enabled` | 是否启用多实例模式 | — |

> 优先级：运行时配置（数据库） > 环境变量 > 默认值。启动调度器时会先从 `system_configs` 表加载，若存在则覆盖环境变量。

---

## 七、API 接口总览

所有接口统一前缀：`/api`

### 7.1 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/login` | 用户登录，获取 JWT token |
| `GET` | `/api/auth/me` | 获取当前登录用户信息 |
| `POST` | `/api/auth/change_password` | 修改当前用户密码 |

### 7.2 用户管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/users` | 获取用户列表 |
| `POST` | `/api/users` | 创建用户 |
| `PUT` | `/api/users/{id}` | 更新用户信息 |
| `DELETE` | `/api/users/{id}` | 删除用户 |

### 7.3 监控数据接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/metrics/realtime` | 实时指标（仪表盘用） |
| `GET` | `/api/metrics/history` | 历史指标（趋势图用） |
| `GET` | `/api/metrics/summary` | 指标摘要卡片 |

### 7.4 死锁接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/deadlocks` | 死锁事件列表 |
| `GET` | `/api/deadlocks/{id}` | 死锁详情（含 SQL 明细） |
| `POST` | `/api/deadlocks/{id}/analyze` | AI 分析死锁 |

### 7.5 告警接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/alerts` | 告警列表 |
| `PUT` | `/api/alerts/{id}/acknowledge` | 确认告警 |

### 7.6 告警规则接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/alert-rules` | 规则列表 |
| `POST` | `/api/alert-rules` | 创建规则 |
| `PUT` | `/api/alert-rules/{id}` | 更新规则 |
| `DELETE` | `/api/alert-rules/{id}` | 删除规则 |
| `PUT` | `/api/alert-rules/{id}/toggle` | 启用/禁用规则 |

### 7.7 实例管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/instances` | 实例列表 |
| `POST` | `/api/instances` | 创建实例 |
| `PUT` | `/api/instances/{id}` | 更新实例 |
| `DELETE` | `/api/instances/{id}` | 删除实例 |
| `POST` | `/api/instances/{id}/test` | 测试实例连接 |

### 7.8 慢查询接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/slow-queries` | 慢查询列表 |
| `GET` | `/api/slow-queries/stats` | 慢查询统计摘要 |

### 7.9 阻塞接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/blocking/realtime` | 实时阻塞链 |
| `GET` | `/api/blocking/history` | 阻塞历史记录 |

### 7.10 磁盘接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/disk/space` | 当前磁盘空间使用 |
| `GET` | `/api/disk/history` | 磁盘空间历史 |

### 7.11 索引接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/indexes/missing` | 缺失索引建议 |
| `GET` | `/api/indexes/fragmentation` | 索引碎片分析 |

### 7.12 审计日志接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/audit-logs` | 审计日志列表 |

### 7.13 数据导出接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/export/metrics` | 导出指标数据（CSV/Excel） |
| `GET` | `/api/export/alerts` | 导出告警数据 |
| `GET` | `/api/export/deadlocks` | 导出死锁数据 |
| `GET` | `/api/export/slow-queries` | 导出慢查询数据 |

### 7.14 通知接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/notifications` | 通知列表 |
| `PUT` | `/api/notifications/{id}/read` | 标记已读 |
| `DELETE` | `/api/notifications/{id}` | 删除通知 |
| `POST` | `/api/notifications/read-all` | 标记全部已读 |

### 7.15 报告接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/reports/summary` | 获取报告摘要数据 |
| `POST` | `/api/reports/save` | 保存报告 |
| `GET` | `/api/reports/history` | 报告历史列表 |
| `DELETE` | `/api/reports/history/{id}` | 删除报告 |

### 7.16 系统配置接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/config` | 获取所有配置键值 |
| `GET` | `/api/config/{key}` | 获取单个配置 |
| `PUT` | `/api/config/{key}` | 更新配置 |
| `POST` | `/api/config/test_mssql` | 测试 SQL Server 连接 |
| `POST` | `/api/config/test_smtp` | 测试 SMTP 邮件发送 |
| `POST` | `/api/config/test_notification` | 测试通知 Webhook |

### 7.17 在线升级接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/upgrade/check` | 检查 GitHub 新版本 |
| `GET` | `/api/upgrade/git-status` | 查看本地 Git 仓库状态 |
| `POST` | `/api/upgrade/apply` | 执行在线升级（git pull + 构建） |

---

## 八、数据库设计

### 8.1 核心数据表清单

| 表名 | 用途 | 数据量级 | 说明 |
|------|------|---------|------|
| `metrics` | 通用性能指标（7 大类 28 项） | 大 | 每实例每 60 秒写入 28 条记录 |
| `slow_queries` | 慢查询记录 | 大 | 每实例每 60 秒写入 TOP 20 条 |
| `deadlocks` | 死锁事件主表 | 中 | 仅在检测到死锁时写入 |
| `deadlock_sqls` | 死锁关联 SQL 明细表 | 中 | 与 `deadlocks` 一对多 |
| `blocking_events` | 阻塞事件历史 | 大 | 每次采集检测到阻塞时写入 |
| `disk_space_records` | 磁盘空间历史记录 | 中 | 每实例每 60 秒 |
| `missing_indexes` | 缺失索引建议 | 中 | 按采集周期 |
| `index_fragmentation` | 索引碎片记录 | 中 | 按采集周期 |
| `alert_logs` | 告警日志 | 中 | 告警引擎触发 |
| `alert_rules` | 告警规则配置 | 小 | 自定义规则 |
| `users` | 用户账号 | 小 | 含角色、密码哈希 |
| `monitored_instances` | 监控实例配置 | 小 | 多实例模式配置 |
| `audit_logs` | 审计日志 | 中 | 关键操作记录 |
| `system_configs` | 系统运行时配置 | 小 | SQL Server 连接等 |
| `report_records` | 系统报告记录 | 中 | 保存用户生成的报告 |

### 8.2 关键表结构

#### metrics（性能指标表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PK | 主键 |
| `category` | VARCHAR(50) | 指标分类 |
| `metric_name` | VARCHAR(100) | 指标名称 |
| `metric_value` | DOUBLE | 指标数值 |
| `unit` | VARCHAR(30) | 单位 |
| `collected_at` | TIMESTAMPTZ | 采集时间 |
| `server_address` | VARCHAR(255) | 被监控的 SQL Server 地址标识 |
| `created_at` | TIMESTAMPTZ | 记录创建时间 |

#### deadlocks（死锁事件表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PK | 主键 |
| `occur_at` | TIMESTAMPTZ | 死锁发生时间 |
| `deadlock_xml` | TEXT | 死锁图形 XML |
| `victim_session_id` | INTEGER | 死锁受害者会话 ID |
| `server_address` | VARCHAR(255) | 实例标识 |
| `analysis_result` | TEXT | DeepSeek AI 分析结果 |
| `created_at` | TIMESTAMPTZ | 创建时间 |

#### slow_queries（慢查询表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PK | 主键 |
| `sql_hash` | VARCHAR(100) | SQL MD5 哈希值（去重用） |
| `sql_text` | TEXT | SQL 文本 |
| `execution_count` | INTEGER | 累计执行次数 |
| `total_cpu_ms` | FLOAT | 累计 CPU 时间（毫秒） |
| `total_logical_reads` | BIGINT | 累计逻辑读次数 |
| `total_elapsed_ms` | FLOAT | 累计耗时（毫秒） |
| `avg_elapsed_ms` | FLOAT | 平均单次耗时（毫秒） |
| `last_execution_time` | DATETIME | 最后执行时间 |
| `collected_at` | TIMESTAMPTZ | 采集时间 |
| `server_address` | VARCHAR(255) | 实例标识 |

#### alert_logs（告警日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PK | 主键 |
| `alert_type` | VARCHAR(50) | 告警类型 |
| `severity` | VARCHAR(20) | 严重级别（low/medium/high/critical） |
| `message` | TEXT | 告警消息正文 |
| `triggered_at` | TIMESTAMPTZ | 触发时间 |
| `acknowledged` | BOOLEAN | 是否已确认 |
| `acknowledged_at` | TIMESTAMPTZ | 确认时间 |
| `notification_sent` | BOOLEAN | 通知是否已发送 |
| `created_at` | TIMESTAMPTZ | 创建时间 |

#### users（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PK | 主键 |
| `username` | VARCHAR(50) UNIQUE | 登录用户名 |
| `password_hash` | VARCHAR(255) | bcrypt 密码哈希 |
| `role` | VARCHAR(20) | 角色 |
| `full_name` | VARCHAR(100) | 姓名 |
| `is_active` | BOOLEAN | 是否启用 |
| `last_login_at` | TIMESTAMPTZ | 最后登录时间 |
| `created_at` | TIMESTAMPTZ | 创建时间 |
| `updated_at` | TIMESTAMPTZ | 更新时间 |

---

## 九、常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 停止并删除数据卷（会清空 PostgreSQL 数据，请谨慎）
docker-compose down -v

# 查看实时日志
docker-compose logs -f

# 只查看后端日志
docker-compose logs -f backend

# 重新构建镜像
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 进入后端容器执行 Alembic 迁移
docker-compose exec backend alembic upgrade head
```

---

## 十、注意事项

### 10.1 安全

1. **密码安全**：请务必修改 `.env` 中的 `PG_PASSWORD`、`MSSQL_PASSWORD` 与默认管理员密码
2. **JWT 密钥**：生产环境请修改 `JWT_SECRET_KEY` 为强随机字符串（建议 ≥ 32 字符）
3. **HTTPS**：生产环境前端/后端建议使用 HTTPS（可在 Nginx 层配置 SSL 证书）
4. **防火墙**：限制数据库端口的公开访问，仅允许受信任来源
5. **最小权限原则**：SQL Server 监控账号仅需授予 `VIEW SERVER STATE` + `VIEW DATABASE STATE` 权限即可完成所有采集任务

### 10.2 性能

1. **采集间隔**：根据实际需要调整 `SCHEDULER_INTERVAL_SECONDS`（默认 60 秒）。建议在大型 SQL Server 上提高到 120~300 秒以降低压力
2. **数据清理**：`metrics`、`slow_queries`、`blocking_events` 等大表建议按时间分区并定期清理（调度器内置每日凌晨 3 点的数据清理任务）
3. **索引优化**：为 PostgreSQL 的 `metrics(metric_name, collected_at)`、`slow_queries(collected_at)`、`deadlocks(occur_at)` 等查询频繁字段建立合适索引

### 10.3 备份

1. **PostgreSQL 备份**：定期使用 `pg_dump` 备份监控数据库
2. **配置备份**：备份 `.env` 文件
3. **日志备份**：定期归档容器/应用日志

### 10.4 监控建议

1. **健康检查**：定期调用 `/health` 接口确认服务运行状态
2. **告警复盘**：每周复盘告警记录，识别趋势性问题
3. **资源监控**：监控容器资源使用，若后端容器内存/CPU 持续偏高，可降低采集频率或增加实例资源
