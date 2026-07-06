# SQL 监控平台 - 项目文档

## 1. 项目概述

### 1.1 项目简介
SQL 监控平台是一个基于 FastAPI + Vue.js + PostgreSQL 的 MS SQL Server 性能监控与告警平台。该平台提供实时监控、历史趋势分析、告警管理、死锁检测、慢查询分析等功能，帮助数据库管理员和开发人员全面掌握 SQL Server 的运行状态。

### 1.2 项目目标
- 实时监控 SQL Server 的关键性能指标（CPU、内存、连接数、IO 等）
- 自动检测并分析死锁事件
- 识别和分析慢查询
- 提供灵活的告警规则配置和多渠道通知
- 支持多 SQL Server 实例的统一监控
- 提供直观的数据可视化和报告功能

### 1.3 主要功能

#### 1.3.1 性能监控
- **实时指标监控**：CPU 使用率、内存使用量、活跃连接数、缓存命中率、页生命周期等
- **历史趋势分析**：支持按时间范围查询历史指标数据，提供对比分析功能
- **概览仪表盘**：展示关键性能指标的汇总信息

#### 1.3.2 死锁监控
- **自动检测**：通过 SQL Server 系统健康会话自动捕获死锁事件
- **详细分析**：记录死锁 XML、受害者会话、涉及的 SQL 语句和对象
- **AI 分析**：集成 DeepSeek AI 进行智能死锁分析，提供优化建议

#### 1.3.3 慢查询分析
- **自动采集**：基于 DMV 自动识别执行时间过长的查询
- **统计分析**：提供慢查询的执行次数、CPU 消耗、逻辑读等统计信息
- **SQL 文本记录**：完整记录慢查询的 SQL 语句

#### 1.3.4 告警管理
- **内置规则**：内存使用率过高、死锁检测、采集任务中断等
- **自定义规则**：支持用户自定义告警规则，包括指标、阈值、操作符等
- **冷却期控制**：避免相同告警在短时间内重复触发
- **静默时段**：支持设置告警的静默时段

#### 1.3.5 通知服务
- **邮件通知**：通过 SMTP 发送告警邮件
- **钉钉通知**：支持钉钉机器人 Webhook 通知
- **企业微信通知**：支持企业微信群机器人 Webhook 通知
- **多渠道组合**：支持同时发送多种渠道的通知

#### 1.3.6 阻塞进程监控
- **实时阻塞检测**：检测当前被阻塞的进程
- **历史记录**：记录阻塞事件的历史数据

#### 1.3.7 磁盘空间监控
- **空间使用率**：监控数据库文件的磁盘空间使用情况
- **历史趋势**：提供磁盘空间使用的历史趋势

#### 1.3.8 索引分析
- **缺失索引检测**：识别 SQL Server 建议的缺失索引
- **索引碎片分析**：分析索引的碎片化程度
- **优化建议**：提供索引优化建议

#### 1.3.9 实例管理
- **多实例支持**：支持同时监控多个 SQL Server 实例
- **独立配置**：每个实例可独立配置连接信息
- **连接测试**：支持测试实例连接是否正常

#### 1.3.10 用户与权限管理
- **角色权限**：超级管理员、管理员、只读用户三种角色
- **用户管理**：支持用户的增删改查
- **密码管理**：支持修改密码，使用 bcrypt 加密存储
- **密码找回**：通过邮箱验证码方式重置密码，无需管理员介入
- **个人设置**：普通用户可自行修改姓名、邮箱等个人信息

#### 1.3.11 审计日志
- **操作记录**：记录用户的关键操作
- **日志查询**：支持按时间、用户、操作类型查询审计日志

#### 1.3.12 报告功能
- **报告生成**：基于监控数据生成性能分析报告
- **AI 分析**：集成 DeepSeek AI 提供智能化的报告分析
- **历史报告**：支持保存和查看历史报告

#### 1.3.13 数据导出
- **多格式支持**：支持导出为 CSV、Excel 等格式
- **多类型数据**：支持导出指标、告警、死锁、慢查询等数据

### 1.4 用户角色

| 角色 | 权限说明 |
|------|----------|
| **超级管理员 (super_admin)** | 拥有全部权限，不可删除，拥有系统最高权限 |
| **管理员 (admin)** | 可管理用户、修改配置、查看所有数据 |
| **只读用户 (viewer)** | 仅可查看数据，无法修改配置或管理用户 |

### 1.5 系统架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue.js 前端   │────▶│  FastAPI 后端   │────▶│   PostgreSQL    │
│   (Nginx)       │     │   (Uvicorn)     │     │   (数据存储)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   SQL Server    │
                        │   (被监控目标)  │
                        └─────────────────┘
```

## 2. 功能模块详细说明

### 2.1 仪表盘 (Dashboard)
仪表盘是系统的首页，提供以下功能：
- **关键指标卡片**：CPU 使用率、内存使用量、活跃连接数、缓存命中率、页生命周期、锁等待数
- **死锁事件统计**：死锁事件计数和最新死锁时间
- **性能趋势图表**：支持按时间范围查看历史趋势，支持对比模式（昨天、上周、上月）
- **自定义图表**：支持自定义显示的图表和排序

### 2.2 性能趋势 (Trends)
提供详细的性能指标历史趋势分析：
- 支持按指标分类（CPU、内存、连接、IO）查看趋势
- 支持自定义时间范围
- 支持多指标对比分析

### 2.3 死锁监控 (Deadlocks)
死锁事件的详细查看和分析：
- 死锁事件列表：显示死锁发生时间、受害者会话、涉及对象
- 死锁详情：查看死锁 XML、参与会话的 SQL 语句
- AI 分析：一键触发 DeepSeek AI 分析，获取优化建议

### 2.4 慢查询分析 (SlowQueries)
慢查询的识别和分析：
- 慢查询列表：显示 SQL 哈希、执行次数、总 CPU 时间、平均耗时等
- 统计分析：提供慢查询的汇总统计信息
- SQL 文本查看：查看完整的 SQL 语句

### 2.5 阻塞进程 (Blocking)
阻塞进程的实时和历史监控：
- 实时阻塞：显示当前被阻塞的进程
- 历史记录：查看历史阻塞事件

### 2.6 磁盘空间 (Disk)
磁盘空间使用情况监控：
- 空间使用率：显示数据库文件的磁盘使用率
- 历史趋势：查看磁盘空间使用的历史变化

### 2.7 索引分析 (Indexes)
索引优化建议：
- 缺失索引：显示 SQL Server 建议的缺失索引
- 索引碎片：分析索引的碎片化程度

### 2.8 告警管理 (Alerts)
告警事件的查看和处理：
- 告警列表：显示告警类型、严重级别、触发时间、消息内容
- 告警确认：支持确认告警事件
- 通知状态：显示通知是否已发送

### 2.9 告警规则 (AlertRules)
告警规则的配置管理：
- 规则列表：显示所有告警规则
- 规则创建：支持创建自定义告警规则
- 规则编辑：支持编辑现有规则
- 规则启用/禁用：支持启用或禁用规则
- 静默时段：支持设置规则的静默时段

### 2.10 实例管理 (Instances)
SQL Server 实例的管理：
- 实例列表：显示所有监控实例
- 实例创建：支持添加新的监控实例
- 实例编辑：支持编辑实例配置
- 连接测试：支持测试实例连接

### 2.11 用户管理 (Users)
系统用户的管理：
- 用户列表：显示所有用户
- 用户创建：支持创建新用户
- 用户编辑：支持编辑用户信息
- 用户删除：支持删除用户（超级管理员不可删除）
- **个人设置**：用户可修改自己的姓名和邮箱（无需管理员权限）

### 2.12 审计日志 (AuditLogs)
系统操作日志的查看：
- 日志列表：显示操作时间、用户、操作类型、详情
- 日志查询：支持按条件筛选日志

### 2.13 系统设置 (Settings)
系统配置的管理：
- 数据库连接配置
- 采集间隔配置
- 告警阈值配置
- 通知渠道配置
- 前端访问地址配置（用于密码重置邮件等链接生成）
- 品牌定制（系统标题、Logo 自定义）
- 声音提醒开关

### 2.14 系统报告 (Report)
性能分析报告的生成和查看：
- 报告生成：基于当前监控数据生成报告
- AI 分析：集成 DeepSeek AI 提供智能化分析
- 报告历史：支持保存和查看历史报告
- 报告导出：支持导出为 PDF 格式

### 2.15 密码找回 (ForgotPassword)
密码重置流程：
- **发送验证码**：用户输入注册邮箱，系统发送 6 位数字验证码（30 分钟有效）
- **重置密码**：用户输入验证码和新密码完成重置
- **安全机制**：验证码与邮箱双向校验，防止越权重置

### 2.16 个人设置 (Profile)
用户个人信息管理：
- **基本信息**：查看用户名、角色（只读）
- **编辑信息**：修改姓名、邮箱
- **修改密码**：通过当前密码验证后设置新密码

## 3. 技术栈

### 3.1 后端技术
- **Python 3.12+**：主要编程语言
- **FastAPI**：Web 框架，提供高性能的异步 API
- **Uvicorn**：ASGI 服务器
- **SQLAlchemy 2.0**：ORM 框架，支持异步操作
- **asyncpg**：PostgreSQL 异步驱动
- **pymssql**：SQL Server 连接驱动
- **Alembic**：数据库迁移工具
- **APScheduler**：定时任务调度
- **Pydantic**：数据验证和配置管理
- **bcrypt**：密码哈希加密
- **PyJWT**：JWT 令牌生成和验证
- **httpx**：异步 HTTP 客户端（用于通知和 AI 调用）

### 3.2 前端技术
- **Vue.js 3**：前端框架
- **Vue Router 4**：路由管理
- **Vite 5**：构建工具
- **Axios**：HTTP 客户端
- **ECharts 5**：数据可视化图表库
- **vue-echarts**：Vue.js 的 ECharts 组件
- **html2canvas**：HTML 转图片
- **jsPDF**：PDF 生成

### 3.3 数据库
- **PostgreSQL 16**：主数据库，存储监控数据和配置
- **SQL Server**：被监控的目标数据库

### 3.4 部署技术
- **Docker**：容器化部署
- **Docker Compose**：多容器编排
- **Nginx**：前端静态文件服务和反向代理

### 3.5 AI 集成
- **DeepSeek AI**：用于死锁分析和报告生成的 AI 服务

## 4. 系统配置

### 4.1 环境变量配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| **项目基础信息** | | |
| `PROJECT_NAME` | 项目名称 | SQL 监控平台 |
| `DEBUG` | 调试模式开关 | false |
| `CORS_ORIGINS` | 允许的跨域来源 | ["http://localhost:3000"] |
| **PostgreSQL 配置** | | |
| `PG_HOST` | 数据库主机地址 | postgres |
| `PG_PORT` | 数据库端口 | 5432 |
| `PG_USER` | 数据库用户 | postgres |
| `PG_PASSWORD` | 数据库密码 | （必填） |
| `PG_DATABASE` | 数据库名称 | sql_monitor |
| **SQL Server 配置** | | |
| `MSSQL_HOST` | SQL Server 主机地址 | 127.0.0.1 |
| `MSSQL_PORT` | SQL Server 端口 | 1433 |
| `MSSQL_USER` | SQL Server 用户 | sa |
| `MSSQL_PASSWORD` | SQL Server 密码 | （必填） |
| `MSSQL_DATABASE` | 默认监控数据库 | master |
| **定时任务** | | |
| `SCHEDULER_INTERVAL_SECONDS` | 采集间隔（秒） | 60 |
| **邮件通知（SMTP）** | | |
| `SMTP_SERVER` | SMTP 服务器地址 | smtp.example.com |
| `SMTP_PORT` | SMTP 端口 | 587 |
| `SMTP_USER` | SMTP 用户名 | （可选） |
| `SMTP_PASSWORD` | SMTP 密码 | （可选） |
| `ALERT_EMAILS` | 告警接收邮箱列表 | [] |
| **钉钉通知** | | |
| `DINGTALK_WEBHOOK_URL` | 钉钉机器人 Webhook 地址 | （可选） |
| **日志** | | |
| `LOG_LEVEL` | 日志级别 | INFO |
| **认证 / JWT** | | |
| `JWT_SECRET_KEY` | JWT 密钥 | sql-monitor-secret-key-change-me-in-production |
| `JWT_ALGORITHM` | JWT 算法 | HS256 |
| `JWT_EXPIRE_HOURS` | JWT 过期时间（小时） | 24 |
| **默认管理员** | | |
| `DEFAULT_ADMIN_USERNAME` | 默认管理员用户名 | Admin |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码 | Chuz0001 |

### 4.2 运行时配置（数据库存储）

系统还支持通过数据库 `system_configs` 表存储运行时配置，包括：
- SQL Server 连接配置
- 采集与告警配置
- Webhook 通知配置
- 多实例模式配置
- 前端访问地址（frontend_url）
- 品牌标题（brand_title）

## 5. 部署指南

### 5.1 环境要求
- **Docker** >= 20.10（推荐 Docker Desktop 4.x+）
- **Docker Compose** >= 2.0
- **Python** >= 3.12（本地开发模式）
- **Node.js** >= 20（本地开发模式）

### 5.2 Docker 部署

#### 5.2.1 准备环境变量
```bash
# 从模板创建环境变量文件
cp .env.example .env

# 编辑 .env 文件，填写实际的数据库连接信息
```

#### 5.2.2 启动服务
```bash
# 构建并启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f
```

#### 5.2.3 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（会清空 PostgreSQL 数据）
docker-compose down -v
```

### 5.3 本地开发

#### 5.3.1 后端开发
```bash
# 进入后端目录
cd backend

# 创建并配置环境变量
cp .env.example .env
# 编辑 .env，将 PG_HOST 改为 127.0.0.1

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5.3.2 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器（热重载）
npm run dev
```

### 5.4 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端界面** | http://localhost:3000 | 监控平台 Web UI |
| **API 文档** | http://localhost:8000/docs | Swagger UI 交互式文档 |
| **API 文档（备选）** | http://localhost:8000/redoc | ReDoc 格式文档 |
| **API 基础地址** | http://localhost:8000 | RESTful API 端点 |
| **PostgreSQL** | localhost:5432 | 数据库直连（仅限宿主机） |

## 6. 使用说明

### 6.1 首次登录
1. 访问 http://localhost:3000
2. 使用默认管理员账号登录：
   - 用户名：Admin
   - 密码：Chuz0001
3. 首次登录后请立即修改默认密码

### 6.2 配置监控实例
1. 进入"实例管理"页面
2. 点击"添加实例"按钮
3. 填写 SQL Server 连接信息
4. 点击"测试连接"验证配置
5. 保存配置

### 6.3 配置告警规则
1. 进入"告警规则"页面
2. 点击"添加规则"按钮
3. 配置告警条件：
   - 选择指标类型
   - 设置比较操作符
   - 设置阈值
   - 选择严重级别
4. 可选：设置静默时段
5. 保存规则

### 6.4 查看监控数据
1. **仪表盘**：查看实时关键指标
2. **性能趋势**：查看历史趋势图表
3. **死锁监控**：查看死锁事件详情
4. **慢查询分析**：查看慢查询统计

### 6.5 生成报告
1. 进入"系统报告"页面
2. 选择报告时间范围
3. 点击"生成报告"
4. 查看 AI 分析建议
5. 可选：导出为 PDF

## 7. API 接口说明

### 7.1 认证接口
- `POST /api/auth/login`：用户登录，获取 JWT 令牌
- `GET /api/auth/me`：获取当前用户信息
- `POST /api/auth/change_password`：修改密码
- `POST /api/auth/forgot_password`：请求密码重置验证码（发送到邮箱）
- `POST /api/auth/reset_password`：通过验证码重置密码
- `PUT /api/auth/me`：更新当前用户个人信息（姓名、邮箱）

### 7.2 用户管理接口
- `GET /api/users`：获取用户列表
- `POST /api/users`：创建用户
- `PUT /api/users/{id}`：更新用户
- `DELETE /api/users/{id}`：删除用户

### 7.3 监控数据接口
- `GET /api/metrics/realtime`：获取实时指标
- `GET /api/metrics/history`：获取历史指标
- `GET /api/metrics/summary`：获取指标摘要

### 7.4 死锁接口
- `GET /api/deadlocks`：获取死锁列表
- `GET /api/deadlocks/{id}`：获取死锁详情
- `POST /api/deadlocks/{id}/analyze`：AI 分析死锁

### 7.5 告警接口
- `GET /api/alerts`：获取告警列表
- `PUT /api/alerts/{id}/acknowledge`：确认告警

### 7.6 告警规则接口
- `GET /api/alert-rules`：获取告警规则列表
- `POST /api/alert-rules`：创建告警规则
- `PUT /api/alert-rules/{id}`：更新告警规则
- `DELETE /api/alert-rules/{id}`：删除告警规则
- `PUT /api/alert-rules/{id}/toggle`：启用/禁用告警规则

### 7.7 实例管理接口
- `GET /api/instances`：获取实例列表
- `POST /api/instances`：创建实例
- `PUT /api/instances/{id}`：更新实例
- `DELETE /api/instances/{id}`：删除实例
- `POST /api/instances/{id}/test`：测试实例连接

### 7.8 慢查询接口
- `GET /api/slow-queries`：获取慢查询列表
- `GET /api/slow-queries/stats`：获取慢查询统计

### 7.9 阻塞接口
- `GET /api/blocking/realtime`：获取实时阻塞
- `GET /api/blocking/history`：获取阻塞历史

### 7.10 磁盘接口
- `GET /api/disk/space`：获取磁盘空间
- `GET /api/disk/history`：获取磁盘历史

### 7.11 索引接口
- `GET /api/indexes/missing`：获取缺失索引
- `GET /api/indexes/fragmentation`：获取索引碎片

### 7.12 审计日志接口
- `GET /api/audit-logs`：获取审计日志

### 7.13 数据导出接口
- `GET /api/export/metrics`：导出指标数据
- `GET /api/export/alerts`：导出告警数据
- `GET /api/export/deadlocks`：导出死锁数据
- `GET /api/export/slow-queries`：导出慢查询数据

### 7.14 通知接口
- `GET /api/notifications`：获取通知列表
- `PUT /api/notifications/{id}/read`：标记通知已读
- `DELETE /api/notifications/{id}`：删除通知
- `POST /api/notifications/read-all`：标记所有通知已读

### 7.15 报告接口
- `GET /api/reports/summary`：获取报告摘要
- `POST /api/reports/save`：保存报告
- `GET /api/reports/history`：获取报告历史
- `DELETE /api/reports/history/{id}`：删除报告

### 7.16 配置接口
- `GET /api/config`：获取所有配置
- `GET /api/config/{key}`：获取单个配置
- `PUT /api/config/{key}`：更新配置
- `POST /api/config/test_mssql`：测试 SQL Server 连接

### 7.17 在线升级接口
- `GET /api/upgrade/check`：检查 GitHub 新版本
- `GET /api/upgrade/git-status`：查看 Git 仓库状态
- `POST /api/upgrade/apply`：执行在线升级（git pull + Docker 构建）

## 8. 数据库设计

### 8.1 核心表结构

#### 8.1.1 metrics (性能指标表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| category | String(50) | 指标分类：cpu / memory / connection / io |
| metric_name | String(100) | 指标名称 |
| metric_value | Float | 指标数值 |
| unit | String(30) | 单位 |
| collected_at | DateTime | 采集时间 |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.2 deadlocks (死锁事件表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| occur_at | DateTime | 死锁发生时间 |
| deadlock_xml | Text | 死锁图形 XML |
| victim_session_id | Integer | 死锁受害者会话 ID |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| analysis_result | Text | DeepSeek AI 分析结果 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.3 deadlock_sqls (死锁 SQL 详情表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| event_id | Integer | 关联的死锁事件 ID |
| session_id | Integer | 参与死锁的会话 ID |
| sql_text | Text | 会话当前执行的 SQL 语句 |
| isolation_level | String(50) | 事务隔离级别 |
| involved_objects | String(500) | 涉及的对象 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.4 alert_logs (告警日志表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| alert_type | String(50) | 告警类型 |
| severity | String(20) | 严重级别：low / medium / high / critical |
| message | Text | 告警消息正文 |
| triggered_at | DateTime | 告警触发时间 |
| acknowledged | Boolean | 是否已确认 |
| acknowledged_at | DateTime | 确认时间 |
| notification_sent | Boolean | 通知是否已发送 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.5 alert_rules (告警规则表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| name | String(100) | 规则名称 |
| description | Text | 规则描述 |
| metric_category | String(50) | 指标分类 |
| metric_name | String(100) | 指标名称 |
| operator | String(10) | 比较操作符 |
| threshold | Float | 告警阈值 |
| severity | String(20) | 严重级别 |
| enabled | Boolean | 是否启用 |
| silence_start | Time | 静默开始时间 |
| silence_end | Time | 静默结束时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 8.1.6 users (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| username | String(50) | 登录用户名 |
| password_hash | String(255) | 密码哈希 |
| role | String(20) | 角色 |
| full_name | String(100) | 姓名 |
| email | String(200) | 邮箱地址 |
| is_active | Boolean | 是否启用 |
| last_login_at | DateTime | 最后登录时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 8.1.7 monitored_instances (监控实例表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| name | String(100) | 实例名称 |
| host | String(255) | SQL Server 主机地址 |
| port | Integer | SQL Server 端口 |
| username | String(100) | 登录用户名 |
| password | String(200) | 登录密码 |
| database_name | String(100) | 默认连接的数据库名 |
| is_active | Boolean | 是否启用采集 |
| description | Text | 实例描述/备注 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 8.1.8 slow_queries (慢查询表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| sql_hash | String(100) | SQL 哈希值 |
| sql_text | Text | SQL 语句 |
| execution_count | Integer | 执行次数 |
| total_cpu_ms | Float | 总 CPU 时间（毫秒） |
| total_logical_reads | Integer | 总逻辑读 |
| total_elapsed_ms | Float | 总耗时（毫秒） |
| avg_elapsed_ms | Float | 平均耗时（毫秒） |
| last_execution_time | DateTime | 最后执行时间 |
| collected_at | DateTime | 采集时间 |
| server_address | String(255) | 被监控的 SQL Server 地址 |

#### 8.1.9 blocking_events (阻塞事件表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| blocking_session_id | Integer | 阻塞会话 ID |
| blocked_session_id | Integer | 被阻塞会话 ID |
| blocking_sql_text | Text | 阻塞会话的 SQL 语句 |
| blocked_sql_text | Text | 被阻塞会话的 SQL 语句 |
| wait_time_seconds | Float | 等待时间（秒） |
| wait_type | String(100) | 等待类型 |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| collected_at | DateTime | 采集时间 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.10 disk_space_records (磁盘空间记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| database_name | String(100) | 数据库名称 |
| file_type | String(50) | 文件类型：ROWS / LOG |
| file_name | String(255) | 文件名 |
| physical_name | String(500) | 物理路径 |
| size_mb | Float | 文件大小（MB） |
| used_mb | Float | 已使用空间（MB） |
| free_mb | Float | 可用空间（MB） |
| usage_pct | Float | 使用率（%） |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| collected_at | DateTime | 采集时间 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.11 missing_indexes (缺失索引表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| database_name | String(100) | 数据库名称 |
| table_name | String(255) | 表名 |
| equality_columns | String(500) | 等式查询列 |
| inequality_columns | String(500) | 不等式查询列 |
| included_columns | String(500) | 包含列 |
| avg_total_user_cost | Float | 平均总用户成本 |
| avg_user_impact | Float | 平均用户影响 |
| user_seeks | Integer | 用户查找次数 |
| user_scans | Integer | 用户扫描次数 |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| collected_at | DateTime | 采集时间 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.12 index_fragmentation (索引碎片表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| database_name | String(100) | 数据库名称 |
| table_name | String(255) | 表名 |
| index_name | String(255) | 索引名称 |
| index_type | String(100) | 索引类型 |
| avg_fragmentation_pct | Float | 平均碎片率（%） |
| page_count | Integer | 页数 |
| server_address | String(255) | 被监控的 SQL Server 地址 |
| collected_at | DateTime | 采集时间 |
| created_at | DateTime | 记录创建时间 |

#### 8.1.13 audit_logs (审计日志表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| user_id | Integer | 操作用户 ID |
| username | String(50) | 操作用户名 |
| action | String(100) | 操作类型 |
| detail | Text | 操作详情 |
| ip_address | String(50) | IP 地址 |
| created_at | DateTime | 操作时间 |

#### 8.1.14 system_configs (系统配置表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| config_key | String(100) | 配置键 |
| config_value | Text | 配置值 |
| description | String(500) | 配置描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 8.1.15 report_records (报告记录表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 ID |
| title | String(200) | 报告标题 |
| content | Text | 报告内容 |
| report_data | Text | 报告数据（JSON 格式） |
| ai_analysis | Text | AI 分析结果 |
| created_at | DateTime | 创建时间 |

## 9. 注意事项

### 9.1 安全注意事项
1. **密码安全**：请务必修改 `.env` 中的默认密码，尤其是 `PG_PASSWORD` 和 `MSSQL_PASSWORD`
2. **JWT 密钥**：生产环境请修改 `JWT_SECRET_KEY` 为强随机字符串
3. **HTTPS**：生产环境建议使用 HTTPS
4. **防火墙**：限制数据库端口的访问

### 9.2 性能注意事项
1. **采集间隔**：根据实际需求调整 `SCHEDULER_INTERVAL_SECONDS`
2. **数据清理**：定期清理历史数据，避免数据库过大
3. **索引优化**：确保 PostgreSQL 表有适当的索引

### 9.3 备份注意事项
1. **数据库备份**：定期备份 PostgreSQL 数据
2. **配置备份**：备份 `.env` 文件和数据库配置
3. **日志备份**：定期备份应用日志

### 9.4 监控注意事项
1. **健康检查**：定期检查服务健康状态
2. **日志监控**：监控应用日志，及时发现异常
3. **资源监控**：监控服务器资源使用情况