# SQL 监控平台 — 技术文档

## 一、整体架构

### 1.1 架构分层

```
┌──────────────────────────────────────────────────────────────────────┐
│                       客户端层（Client）                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    Vue 3 前端应用（Nginx 托管）                 │  │
│  │   Dashboard / Trends / Deadlocks / Alerts / Users / ...        │  │
│  └────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTP/HTTPS + Axios
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       应用层（FastAPI）                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI ASGI 应用                          │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │  │
│  │  │   Routers（路由）│  │  Services（服务）│  │ Collectors   │  │  │
│  │  │  17 个模块      │  │  认证/告警/审计  │  │ 7 类采集器   │  │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘  │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │  │
│  │  │   Models（模型）│  │  Scheduler（调度）│  │ Config（配置）│  │  │
│  │  │  15 个数据模型  │  │ APScheduler 定时  │  │ pydantic     │  │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────┘  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│   PostgreSQL 16（数据存储）  │  │   SQL Server（被监控目标）    │
│  metrics / deadlocks / ...   │  │  DMV / 扩展事件 / 系统表      │
└──────────────────────────────┘  └──────────────────────────────┘
```

### 1.2 数据流（典型采集周期）

```
APScheduler（每 60 秒触发一次）
          │
          ▼
SchedulerManager._collect_and_store()
          │
  ┌───────┴──────────────────────┐
  ▼                              ▼
加载 system_configs 配置      判断单/多实例模式
  │                              │
  │                              ▼
  │                     遍历 monitored_instances 表
  │                              │
  │                              ▼
  │               每个实例创建 MSSQLConnectionManager
  │                              │
  │                              ▼
  │                    MetricsCollector.collect_all()
  │                       ├── PerformanceCollector ─▶ 28 项指标
  │                       ├── SlowQueryCollector   ─▶ TOP 20
  │                       ├── DeadlockDetector     ─▶ 死锁事件
  │                       ├── BlockingCollector    ─▶ 阻塞链
  │                       ├── DiskSpaceCollector   ─▶ 磁盘空间
  │                       └── IndexAnalyzer        ─▶ 索引分析
  │                              │
  │                              ▼
  │                       asyncpg 批量写入 PostgreSQL
  │                              │
  └──────────────────────────────┘
                                 │
                                 ▼
                        AlertEngine.process_metrics()
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      内存过高检测         死锁事件检测       采集中断检测
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                        NotificationService.notify_all()
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        SMTP 邮件           钉钉 Webhook      企业微信 Webhook
```

### 1.3 技术选型说明

| 组件 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| Web 框架 | FastAPI | 0.115+ | 高性能异步、自动生成 Swagger、类型安全 |
| ASGI 服务器 | Uvicorn | 最新 | 官方推荐 ASGI 服务器，支持 HTTP/2 |
| ORM | SQLAlchemy | 2.0+ | 成熟稳定，原生支持异步会话（AsyncSession） |
| PostgreSQL 驱动 | asyncpg | 最新 | 最快的异步 PostgreSQL 驱动 |
| SQL Server 驱动 | pymssql | 最新 | Python 生态中最稳定的 SQL Server 驱动，支持 TDS 协议 |
| 数据库迁移 | Alembic | 最新 | SQLAlchemy 官方迁移工具 |
| 定时任务 | APScheduler | 3.10+ | 轻量、支持多种触发器（Interval/Cron/Date） |
| 配置管理 | pydantic-settings | 2.0+ | 类型安全，支持 .env 文件加载 |
| 密码哈希 | bcrypt | 最新 | 自适应哈希算法，抗暴力破解 |
| JWT 认证 | PyJWT | 2.8+ | 简单易用的 JWT 库 |
| HTTP 客户端 | httpx | 最新 | 异步 HTTP 客户端，用于通知 & AI 调用 |
| 前端框架 | Vue 3 | 3.x | Composition API + 响应式，学习曲线平缓 |
| 前端路由 | Vue Router | 4.x | 官方路由，支持懒加载 |
| 构建工具 | Vite | 5.x | 极速冷启动 & HMR |
| 图表 | Apache ECharts | 5.x | 功能丰富、性能好、中文社区活跃 |
| 数据库 | PostgreSQL | 16 | 支持 JSONB、分区表、丰富索引类型 |
| 反向代理 | Nginx | 1.26+ | 前端静态文件服务 + API 反向代理 |

---

## 二、项目目录结构

### 2.1 后端结构

```
backend/
├── alembic/                          # 数据库迁移脚本目录
│   ├── versions/                     # 迁移版本（001_add_user_email.py 等）
│   ├── env.py                        # Alembic 环境配置
│   └── script.py.mako                # 迁移脚本模板
├── app/
│   ├── collectors/                   # 数据采集层（核心模块）
│   │   ├── __init__.py
│   │   ├── collector.py              # 采集协调器 MetricsCollector
│   │   ├── sqlserver.py              # SQL Server 连接管理 MSSQLConnectionManager
│   │   ├── performance.py            # 28 项性能指标采集 PerformanceCollector
│   │   ├── deadlock.py               # 死锁检测 DeadlockDetector
│   │   ├── slow_query.py             # 慢查询采集 SlowQueryCollector
│   │   ├── blocking.py               # 阻塞链采集 BlockingCollector
│   │   ├── disk.py                   # 磁盘空间采集 DiskSpaceCollector
│   │   └── index_analyzer.py         # 索引分析 IndexAnalyzer
│   ├── models/                       # 数据模型层（SQLAlchemy ORM）
│   │   ├── __init__.py
│   │   ├── performance.py            # metrics 表模型
│   │   ├── deadlock.py               # deadlocks / deadlock_sqls 模型
│   │   ├── alert.py                  # alert_logs 模型
│   │   ├── alert_rule.py             # alert_rules 模型
│   │   ├── user.py                   # users 模型
│   │   ├── instance.py               # monitored_instances 模型
│   │   ├── slow_query.py             # slow_queries 模型
│   │   ├── blocking.py               # blocking_events 模型
│   │   ├── disk.py                   # disk_space_records 模型
│   │   ├── index_analysis.py         # missing_indexes / index_fragmentation 模型
│   │   ├── audit_log.py              # audit_logs 模型
│   │   ├── config.py                 # system_configs 模型
│   │   └── report.py                 # report_records 模型
│   ├── routers/                      # API 路由层（共 17 个模块）
│   │   ├── __init__.py               # 路由聚合（挂载到 /api）
│   │   ├── auth.py                   # 认证相关接口
│   │   ├── users.py                  # 用户管理接口
│   │   ├── metrics.py                # 性能指标接口
│   │   ├── deadlocks.py              # 死锁监控接口
│   │   ├── alerts.py                 # 告警管理接口
│   │   ├── alert_rules.py            # 告警规则接口
│   │   ├── instances.py              # 实例管理接口
│   │   ├── slow_queries.py           # 慢查询接口
│   │   ├── blocking.py               # 阻塞链接口
│   │   ├── disk.py                   # 磁盘接口
│   │   ├── indexes.py                # 索引接口
│   │   ├── audit_logs.py             # 审计日志接口
│   │   ├── config.py                 # 系统配置接口
│   │   ├── export.py                 # 数据导出接口
│   │   ├── notifications.py          # 通知接口
│   │   ├── reports.py                # 报告接口
│   │   ├── setup.py                  # 初始化接口
│   │   ├── smtp_test.py              # SMTP 测试接口
│   │   └── upgrade.py                # 在线升级接口
│   ├── services/                     # 业务服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py           # 认证服务（登录/密码哈希/JWT）
│   │   ├── alert_service.py          # 告警引擎（内置规则 + 自定义规则）
│   │   ├── audit_service.py          # 审计日志服务
│   │   ├── notification.py           # 通知服务（SMTP/钉钉/企业微信）
│   │   ├── deepseek.py               # DeepSeek AI 集成（死锁/报告分析）
│   │   └── upgrade_service.py        # 在线升级服务（git pull + docker build）
│   ├── __init__.py
│   ├── config.py                     # 全局配置管理（Settings 类）
│   ├── database.py                   # 数据库连接（AsyncSession 工厂）
│   ├── init_db.py                    # 数据库初始化（建表/插入默认管理员）
│   ├── main.py                       # FastAPI 应用入口（lifespan 生命周期）
│   └── scheduler.py                  # APScheduler 定时任务调度器
├── .env.example                      # 环境变量模板
├── Dockerfile                        # 后端容器镜像构建
├── alembic.ini                       # Alembic 配置
├── requirements.txt                  # Python 依赖列表
└── VERSION                           # 版本号文件（当前 1.0.11）
```

### 2.2 前端结构

```
frontend/
├── src/
│   ├── api/                          # API 客户端封装
│   │   └── index.js                  # Axios 实例 & API 请求封装
│   ├── components/                   # 公共组件
│   │   └── Layout.vue                # 全局布局（侧边栏 + 顶部导航）
│   ├── router/                       # 路由管理
│   │   └── index.js                  # 路由定义（所有页面路由配置）
│   ├── stores/                       # 状态管理（Pinia/Vuex）
│   │   ├── auth.js                   # 认证状态（token/当前用户）
│   │   └── theme.js                  # 主题状态（深色/浅色）
│   ├── styles/                       # 全局样式
│   │   └── theme.css                 # 主题 CSS 变量
│   ├── utils/                        # 工具函数
│   │   └── datetime.js               # 日期/时间格式化工具
│   ├── views/                        # 页面组件
│   │   ├── Login.vue                 # 登录页面
│   │   ├── Dashboard.vue             # 仪表盘（实时指标卡片 + 图表）
│   │   ├── Trends.vue                # 性能趋势（28 项指标趋势图）
│   │   ├── Deadlocks.vue             # 死锁列表 + 详情 + AI 分析
│   │   ├── Alerts.vue                # 告警事件管理
│   │   ├── AlertRules.vue            # 告警规则配置
│   │   ├── SlowQueries.vue           # 慢查询分析
│   │   ├── Blocking.vue              # 阻塞链监控
│   │   ├── Disk.vue                  # 磁盘空间监控
│   │   ├── Indexes.vue               # 索引分析
│   │   ├── Instances.vue             # 多实例管理
│   │   ├── Users.vue                 # 用户管理
│   │   ├── AuditLogs.vue             # 审计日志
│   │   ├── Settings.vue              # 系统设置
│   │   ├── Report.vue                # 系统报告（AI 分析 + PDF 导出）
│   │   └── Upgrade.vue               # 在线升级页面
│   ├── App.vue                       # 根组件
│   └── main.js                       # Vue 应用入口
├── .dockerignore
├── Dockerfile                        # 前端容器镜像构建（多阶段 Nginx）
├── index.html                        # Vite 入口 HTML
├── nginx.conf                        # Nginx 配置（静态文件 + 反向代理 /api）
├── package.json                      # Node.js 依赖（含 Vue/Router/ECharts 等）
└── vite.config.js                    # Vite 构建配置
```

### 2.3 项目根目录

```
.
├── Docs/                             # 项目文档（本目录）
│   ├── PROJECT_DOCUMENTATION.md      # 项目文档（概述/部署/API）
│   ├── TECHNICAL_DOCUMENTATION.md    # 技术文档（架构/实现/设计）
│   └── 指标监控说明文档.md             # 指标监控详解（28 项指标说明）
├── backend/                          # 后端代码
├── frontend/                         # 前端代码
├── docker-compose.yml                # 容器编排（3 个服务：postgres/backend/frontend）
├── .env.example                      # 根目录环境变量模板
├── .gitignore                        # Git 忽略规则
├── README.md                         # 项目概览（快速开始）
├── deploy.sh                         # Linux/Mac 部署脚本
├── deploy.ps1                        # Windows PowerShell 部署脚本
├── _fix_ui.py                        # UI 修复辅助脚本
├── _upload.py                        # 上传辅助脚本
└── _upload_all.py                    # 全量上传辅助脚本
```

---

## 三、核心模块实现详解

### 3.1 数据采集层（Collectors）

#### 3.1.1 采集协调器（collector.py）

`MetricsCollector` 是采集层的统一入口，负责协调多个专项采集器，并将结果汇总为结构化数据供上层写入。

**核心职责：**
- 维护各专项采集器实例
- 提供 `collect_all()` 方法触发完整采集流程
- 统一错误处理与日志记录
- 支持按实例粒度独立采集（配合多实例模式）

**工作流程：**
```
1. 创建/复用 MSSQLConnectionManager 建立到目标 SQL Server 的连接
2. 调用 PerformanceCollector 采集 28 项性能指标
3. 调用 SlowQueryCollector 采集 TOP 20 慢查询
4. 调用 DeadlockDetector 检测最新死锁事件
5. 调用 BlockingCollector 采集阻塞链
6. 调用 DiskSpaceCollector 采集数据库文件空间
7. 调用 IndexAnalyzer 分析缺失索引 + 索引碎片
8. 返回结构化结果 dict：{metrics:[], deadlocks:[], slow_queries:[], ...}
```

#### 3.1.2 SQL Server 连接管理（sqlserver.py）

`MSSQLConnectionManager` 负责管理到 SQL Server 的 TDS 协议连接，实现连接复用、自动重试与健康检查。

**关键特性：**
- 支持 `host:port` 多种连接配置（实例名模式、端口模式）
- 内置连接保活机制，避免频繁建立/释放连接
- 自动重试：连接失败最多重试 N 次（指数退避）
- 连接超时控制（login timeout + query timeout）
- 多实例模式下按实例 ID 独立管理连接池

#### 3.1.3 性能指标采集（performance.py）

`PerformanceCollector` 是最核心的采集器，通过 DMV 和性能计数器采集 7 大类 28 项指标：

| 分类 | 关键 SQL 语句/视图 | 指标数量 |
|------|-------------------|---------|
| CPU | `sys.dm_os_ring_buffers`（RING_BUFFER_SCHEDULER_MONITOR） + `sys.dm_os_sys_info` | 2 |
| 内存 | `sys.dm_os_performance_counters`（Buffer cache hit ratio / Target Server Memory / Page life expectancy） | 4 |
| 连接 | `sys.dm_exec_sessions` + `sys.dm_exec_connections` + 性能计数器 User Connections | 4 |
| IO | `sys.dm_io_virtual_file_stats` 聚合 | 4 |
| OS 内存 | `sys.dm_os_sys_memory` + `sys.dm_os_sys_info` | 3 |
| 锁等待 | `sys.dm_tran_locks` + `sys.dm_os_waiting_tasks` | 3 |
| 批处理请求 | `sys.dm_os_performance_counters`（Batch Requests/sec、SQL Compilations/sec、SQL Re-Compilations/sec） | 3 |

**设计要点：**
- 所有查询均为只读，不锁定用户表
- 使用 `collected_at` 时间戳对齐同一次采集的所有指标
- 按 `category / metric_name / value / unit` 的统一结构输出

#### 3.1.4 死锁检测（deadlock.py）

`DeadlockDetector` 通过 SQL Server 扩展事件（Extended Events）的 system_health 会话捕获死锁 XML 报告。

**工作机制：**
1. 查询 `sys.dm_xe_session_targets` 中 `system_health` 会话的 `event_file` 目标
2. 使用 `sys.fn_xe_file_target_read_file()` 解析 XML 事件流
3. 过滤出 `xml_deadlock_report` 事件
4. 解析 XML：提取 `victim`、`process-list`、`resource-list`
5. 对比已记录死锁时间，避免重复记录
6. 记录到 `deadlocks` 主表 + `deadlock_sqls` 明细表

**注意事项：**
- system_health 会话默认启用，但部分老版本 SQL Server 可能需要手动启用
- 死锁 XML 可能较大，使用 TEXT 类型存储
- 支持 DeepSeek AI 分析，将死锁 XML + SQL 文本发送给 LLM 获取优化建议

#### 3.1.5 慢查询采集（slow_query.py）

`SlowQueryCollector` 基于 `sys.dm_exec_query_stats` DMV 采集 TOP 20 耗时查询：

```sql
SELECT TOP 20
    qs.execution_count,
    qs.total_worker_time / 1000 AS total_cpu_ms,
    qs.total_logical_reads,
    qs.total_elapsed_time / 1000 AS total_elapsed_ms,
    qs.total_elapsed_time / 1000 / CASE WHEN qs.execution_count = 0 THEN 1 ELSE qs.execution_count END AS avg_elapsed_ms,
    qs.last_execution_time,
    st.text AS sql_text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_elapsed_time DESC
```

**去重机制：**
- 对 `sql_text` 计算 MD5 哈希作为 `sql_hash`
- 前端通过 `sql_hash` 聚合展示同一 SQL 的历史执行次数

**注意事项：**
- `dm_exec_query_stats` 是自 SQL Server 启动以来的累积统计
- 仅反映计划缓存中的查询（计划被清出后无法再追踪）
- 如需更精确的慢查询追踪，可在 SQL Server 配置 Query Store

### 3.2 定时任务调度（scheduler.py）

`SchedulerManager` 基于 APScheduler 的 `AsyncIOScheduler` 实现定时任务。

**核心任务：**

| 任务 | 触发器 | 说明 |
|------|--------|------|
| 指标采集 | Interval（默认 60 秒） | `_collect_and_store()` 核心采集流程 |
| 数据清理 | Cron（每天 03:00） | `_cleanup_old_data()` 清理过期指标、慢查询等历史数据 |

**单实例 vs 多实例模式：**
- `mssql_instances_enabled = false`（默认）：使用 `system_configs` 中配置的单一 SQL Server 连接
- `mssql_instances_enabled = true`：遍历 `monitored_instances` 表中的活跃实例（`is_active=true`），为每个实例独立采集

**`_collect_and_store()` 执行流程：**
```
1. 从 system_configs 表加载运行时配置
2. 加载告警规则
3. 判断单实例/多实例模式
4. 对每个目标执行：
   a. 获取/创建 MSSQLConnectionManager
   b. 调用 MetricsCollector.collect_all() 采集
   c. 批量写入 PostgreSQL（metrics / slow_queries / deadlocks / ...）
5. 触发 AlertEngine.process_metrics() 检查告警
6. 若有新告警，触发通知服务
```

**misfire 处理：**
- 设置 `misfire_grace_time=30`，允许采集任务最多延迟 30 秒执行
- 防止因数据库暂时不可用导致任务永久跳过

### 3.3 告警引擎（alert_service.py）

`AlertEngine` 整合了内置告警规则和用户自定义规则。

**内置规则（硬编码）：**

| 规则名 | 触发条件 | 严重级别 | 冷却期 |
|--------|---------|---------|-------|
| `memory_high` | OS 内存使用率 > 85% 且持续 ≥ 5 分钟 | critical | 10 分钟 |
| `deadlock_detected` | 本次采集发现新死锁事件 | high | 5 分钟 |
| `collection_interrupted` | 连续 3 个采集周期无新指标写入 | high | 15 分钟 |

**自定义规则（来自 alert_rules 表）：**
- 按 `category + metric_name` 匹配
- 支持操作符：`>`、`<`、`>=`、`<=`、`=`
- 支持 `severity` 级别设置
- 支持 `silence_start / silence_end` 指定静默时间段

**告警生命周期：**
```
1. 采集完成 → AlertEngine.process_metrics(aggregated_data)
2. 检查每条内置规则和自定义规则的条件
3. 若触发：
   - 检查冷却期（cooldown）
   - 检查静默时段（silence window）
   - 写入 alert_logs 表
   - 调用 NotificationService.notify_all()
4. 用户前端确认 → PUT /api/alerts/{id}/acknowledge
5. 告警状态变为已确认
```

### 3.4 通知服务（notification.py）

`NotificationService` 聚合了 3 类通知渠道：

| 渠道 | 实现方式 | 依赖 |
|------|---------|------|
| SMTP 邮件 | Python `smtplib` + `email` 模块 | 需配置 SMTP_SERVER/PORT/USER/PASSWORD |
| 钉钉机器人 | HTTP POST Webhook | `DINGTALK_WEBHOOK_URL` 环境变量 |
| 企业微信机器人 | HTTP POST Webhook | `FEISHU_WEBHOOK_URL` 环境变量 |

**消息格式：**
- 邮件：标准 HTML 邮件
- 钉钉/企业微信：Markdown 消息卡片

**失败处理：**
- 单渠道失败不影响其他渠道发送
- 每次发送结果记录到日志

### 3.5 认证服务（auth_service.py）

`AuthService` 实现了完整的身份验证和鉴权逻辑。

**核心流程：**
```
用户登录请求（username + password）
          │
          ▼
1. 查询 users 表中 username 匹配的记录
2. 使用 bcrypt.checkpw() 校验密码
3. 生成 JWT token
   ├── header: { alg: HS256, typ: JWT }
   ├── payload: { sub: user_id, username, role, iat, exp }
   ├── signature: HMAC-SHA256(JWT_SECRET_KEY)
4. 返回 { access_token, token_type: "bearer", user }
          │
          ▼
后续请求携带：Authorization: Bearer <token>
          │
          ▼
FastAPI Depends(get_current_user) 解码 JWT 校验
```

**密码安全：**
- 使用 `bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))`
- 密码哈希存储在 `password_hash` 字段，从不返回给前端
- `rounds=12` 平衡了安全性与计算速度

**JWT 安全：**
- `JWT_SECRET_KEY` 生产环境建议修改为 32+ 字符的强随机字符串
- 默认过期时间 24 小时
- 校验失败返回 401 Unauthorized

**角色权限：**
- `super_admin`：全部权限，不可删除
- `admin`：用户管理/配置管理/告警规则/报告生成
- `viewer`：只读访问

### 3.6 AI 分析集成（deepseek.py）

集成 DeepSeek LLM 为死锁分析和报告生成提供智能建议。

**典型调用流程：**
```
1. 用户点击 "AI 分析" 按钮
2. 前端发起 POST /api/deadlocks/{id}/analyze
3. 后端从数据库加载死锁 XML + 关联 SQL
4. 构建 Prompt：
   ├── System prompt: "你是一位资深 SQL Server 数据库性能优化专家..."
   ├── User prompt: "请分析以下死锁事件，指出原因并给出 3 条优化建议..."
5. 异步调用 DeepSeek API（httpx.AsyncClient，超时 60s）
6. 解析 JSON 响应，提取 message.content
7. 将分析结果写入 deadlocks.analysis_result 字段
8. 返回给前端展示
```

**注意事项：**
- 需要 DeepSeek API Key（或可替换为 OpenAI 兼容的其他 LLM）
- API 调用为异步阻塞式，大死锁 XML 可能触发上下文窗口限制
- 建议为 API 调用添加速率限制和缓存

### 3.7 数据库初始化（init_db.py）

`init_db()` 在应用 `lifespan` 启动阶段执行，完成：

1. 通过 SQLAlchemy `metadata.create_all()` 创建所有数据表
2. 插入默认管理员账号（`Admin` / `Chuz0001`），若已存在则跳过
3. 插入部分默认告警规则（可选）
4. 记录启动日志

**注意事项：**
- `create_all()` 是幂等的，已存在的表不会重建
- 但新增/修改的表结构需通过 Alembic 迁移来执行（以避免数据丢失）

### 3.8 在线升级（upgrade_service.py）

支持通过管理后台一键执行：

1. `git pull` 拉取最新代码
2. `docker-compose up -d --build` 重建并重启容器

**安全约束：**
- 仅 `super_admin` 角色可访问升级接口
- 需正确配置 `GITHUB_TOKEN` 才能拉取私有仓库
- 升级操作记录到审计日志

---

## 四、API 设计规范

### 4.1 RESTful 设计原则

- 所有 API 统一挂载在 `/api` 前缀下
- 使用标准 HTTP 方法：`GET`（查询）、`POST`（创建）、`PUT`（更新）、`DELETE`（删除）
- 使用 HTTP 状态码表达请求结果：200、201、400、401、403、404、422、500
- 使用 JSON 格式进行数据交换
- 使用 JWT Bearer Token 认证

### 4.2 API 分组与命名

| 路径前缀 | 功能 | 操作示例 |
|---------|------|---------|
| `/api/auth/*` | 认证 | `POST /login`、`GET /me`、`POST /change_password` |
| `/api/users/*` | 用户 | CRUD |
| `/api/metrics/*` | 指标 | `GET /realtime`、`/history`、`/summary` |
| `/api/deadlocks/*` | 死锁 | `GET /`、`GET /{id}`、`POST /{id}/analyze` |
| `/api/alerts/*` | 告警 | `GET /`、`PUT /{id}/acknowledge` |
| `/api/alert-rules/*` | 规则 | CRUD + `PUT /{id}/toggle` |
| `/api/instances/*` | 实例 | CRUD + `POST /{id}/test` |
| `/api/slow-queries/*` | 慢查询 | `GET /`、`GET /stats` |
| `/api/blocking/*` | 阻塞链 | `/realtime`、`/history` |
| `/api/disk/*` | 磁盘 | `/space`、`/history` |
| `/api/indexes/*` | 索引 | `/missing`、`/fragmentation` |
| `/api/audit-logs/*` | 审计 | `GET /` |
| `/api/config/*` | 配置 | `GET`、`PUT`、`POST /test_*` |
| `/api/export/*` | 导出 | `/metrics`、`/alerts`、`/deadlocks`、`/slow-queries` |
| `/api/notifications/*` | 通知 | `GET`、`PUT /{id}/read`、`POST /read-all` |
| `/api/reports/*` | 报告 | `GET /summary`、`POST /save`、`GET /history` |
| `/api/upgrade/*` | 升级 | `GET /check`、`GET /git-status`、`POST /apply` |

### 4.3 JWT 认证流程

```
Client                          FastAPI                        DB
  │                               │                             │
  │ POST /api/auth/login          │                             │
  │ { username, password }        │                             │
  ├──────────────────────────────▶│                             │
  │                               │ 1. SELECT user FROM users   │
  │                               │────────────────────────────▶│
  │                               │ 2. 返回用户信息             │
  │                               │◀────────────────────────────│
  │                               │ 3. bcrypt.checkpw()         │
  │                               │ 4. 生成 JWT Token           │
  │                               │                               │
  │ { access_token, user }        │                               │
  │◀──────────────────────────────┤                               │
  │                               │                               │
  │ GET /api/metrics/realtime     │                               │
  │ Authorization: Bearer <token> │                               │
  ├──────────────────────────────▶│                               │
  │                               │ 5. jwt.decode(token)         │
  │                               │ 6. 校验 exp（过期时间）       │
  │                               │ 7. 查询当前用户               │
  │                               │────────────────────────────▶│
  │                               │ 8. 查询 metrics 表            │
  │                               │────────────────────────────▶│
  │       JSON 响应               │                               │
  │◀──────────────────────────────┤                               │
```

### 4.4 响应格式规范

**成功响应：**
```json
{
  "data": { ... },
  "message": "操作成功"
}
```
或直接返回对象/数组（列表接口常直接返回）

**错误响应：**
```json
{
  "detail": "用户名或密码错误"
}
```

**分页响应：**
```json
{
  "items": [...],
  "page": 1,
  "page_size": 20,
  "total": 120,
  "total_pages": 6
}
```

### 4.5 关键接口请求/响应示例

**登录接口：**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "Admin",
  "password": "Chuz0001"
}

HTTP/1.1 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "Admin",
    "role": "super_admin",
    "full_name": "系统管理员"
  }
}
```

**获取实时指标：**
```http
GET /api/metrics/realtime
Authorization: Bearer <token>

HTTP/1.1 200 OK
{
  "cpu": {
    "cpu_usage": 45.2,
    "sql_cpu": 42.1
  },
  "memory": {
    "sql_server_memory_mb": 8192,
    "buffer_cache_hit_ratio": 99.5,
    "target_memory_mb": 16384,
    "page_life_expectancy": 3600
  },
  "connection": { ... },
  "io": { ... },
  "os_memory": { ... },
  "locks": { ... },
  "batch_requests": { ... },
  "server_address": "10.0.0.1:1433",
  "collected_at": "2024-01-15T10:30:00Z"
}
```

---

## 五、数据库设计

### 5.1 ER 图（核心实体关系）

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      users      │       │  alert_rules    │       │  alert_logs     │
│  PK id          │       │  PK id          │       │  PK id          │
│  username       │       │  name           │       │  alert_type     │
│  password_hash  │       │  metric_name    │       │  severity       │
│  role           │       │  threshold      │       │  triggered_at   │
│  full_name      │       │  enabled        │       │  acknowledged   │
└────────┬────────┘       └─────────────────┘       └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   audit_logs    │       │monitored_instances│      │ system_configs  │
│  PK id          │       │  PK id          │       │  PK id          │
│  FK user_id     │       │  host           │       │  config_key     │
│  action         │       │  port           │       │  config_value   │
│  created_at     │       │  username       │       │  description    │
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │ 1:N              │ 1:N              │ 1:N
                ▼                  ▼                  ▼
          ┌─────────┐       ┌───────────┐       ┌──────────────┐
          │ metrics │       │ deadlocks │       │ slow_queries │
          │ ...     │       │ ...       │       │ ...          │
          └─────────┘       └─────┬─────┘       └──────────────┘
                                   │ 1:N
                                   ▼
                            ┌──────────────┐
                            │deadlock_sqls │
                            │ ...          │
                            └──────────────┘

                        （其他表：blocking_events / disk_space_records /
                         missing_indexes / index_fragmentation /
                         report_records / notifications）
```

### 5.2 推荐索引设计

为优化查询性能，建议为以下列添加索引：

```sql
-- 性能指标表（查询最频繁）
CREATE INDEX idx_metrics_collected_at      ON metrics(collected_at);
CREATE INDEX idx_metrics_category           ON metrics(category);
CREATE INDEX idx_metrics_server_address     ON metrics(server_address);
CREATE INDEX idx_metrics_category_collected ON metrics(category, collected_at);
CREATE INDEX idx_metrics_name_collected     ON metrics(metric_name, collected_at);

-- 死锁表
CREATE INDEX idx_deadlocks_occur_at         ON deadlocks(occur_at DESC);
CREATE INDEX idx_deadlocks_server_address   ON deadlocks(server_address);

-- 死锁 SQL 明细
CREATE INDEX idx_deadlock_sqls_event_id     ON deadlock_sqls(event_id);

-- 慢查询表
CREATE INDEX idx_slow_queries_collected_at  ON slow_queries(collected_at DESC);
CREATE INDEX idx_slow_queries_sql_hash      ON slow_queries(sql_hash);
CREATE INDEX idx_slow_queries_server        ON slow_queries(server_address);

-- 告警日志
CREATE INDEX idx_alert_logs_triggered_at    ON alert_logs(triggered_at DESC);
CREATE INDEX idx_alert_logs_severity        ON alert_logs(severity);
CREATE INDEX idx_alert_logs_acknowledged    ON alert_logs(acknowledged);

-- 告警规则
CREATE INDEX idx_alert_rules_enabled        ON alert_rules(enabled);

-- 用户表
CREATE UNIQUE INDEX idx_users_username      ON users(username);
CREATE INDEX idx_users_role                 ON users(role);

-- 审计日志
CREATE INDEX idx_audit_logs_created_at      ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_user_id         ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action          ON audit_logs(action);

-- 阻塞事件
CREATE INDEX idx_blocking_collected_at      ON blocking_events(collected_at DESC);

-- 磁盘记录
CREATE INDEX idx_disk_collected_at          ON disk_space_records(collected_at DESC);

-- 报告记录
CREATE INDEX idx_reports_created_at         ON report_records(created_at DESC);
```

---

## 六、部署与运维

### 6.1 Docker 部署流程

```bash
# 1. 拉取代码
git clone <repo-url>
cd sql-monitor-platform

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改 PG_PASSWORD、MSSQL_HOST/USER/PASSWORD 等

# 3. 启动服务
docker-compose up -d
# 实际执行步骤：
#   a) 拉取 postgres:16 镜像
#   b) 构建 backend 镜像（FROM python:3.12-slim）
#   c) 构建 frontend 镜像（FROM node:20-alpine → Nginx 二阶段）
#   d) 创建 docker-compose 网络
#   e) 启动 postgres、backend、frontend 三个容器

# 4. 检查容器状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f backend

# 6. 访问前端
# http://localhost:3000
# 默认账号：Admin / Chuz0001
```

### 6.2 docker-compose.yml 服务说明

| 服务 | 镜像/构建 | 端口 | 数据卷 | 依赖 |
|------|----------|------|-------|-----|
| `postgres` | postgres:16 | 5432（容器内，默认不对外暴露） | `postgres_data:/var/lib/postgresql/data` | — |
| `backend` | `build: ./backend` | 8000（容器内，前端经 Nginx 代理访问） | `./backend/.env:/app/.env` （可选） | `postgres` |
| `frontend` | `build: ./frontend` | 3000:80（宿主机 3000 → 容器 80） | — | `backend` |

### 6.3 版本升级

**推荐流程：**

```bash
# 方案 A：使用内置在线升级（前端 Upgrade 页面）
# 1. 超级管理员登录前端
# 2. 进入"在线升级"页面
# 3. 点击"检查更新"
# 4. 若有新版本，点击"执行升级"
#    → 后端自动执行 git pull + docker-compose up -d --build

# 方案 B：手动升级
git pull
docker-compose up -d --build
docker image prune -f  # 清理旧镜像
```

### 6.4 备份策略

**PostgreSQL 数据备份：**
```bash
# 每日自动备份（可写入 crontab 或添加到 docker-compose cron 容器）
docker-compose exec -T postgres \
    pg_dump -U postgres sql_monitor | gzip > /backup/sql_monitor_$(date +%Y%m%d).sql.gz

# 保留策略：保留 30 天
find /backup -name "sql_monitor_*.sql.gz" -mtime +30 -delete
```

**配置文件备份：**
- `.env` 文件建议单独备份，不提交到 Git
- `docker-compose.yml` 如有修改需纳入版本管理

### 6.5 日志管理

**容器日志：**
```bash
# 查看所有服务实时日志
docker-compose logs -f

# 仅看后端
docker-compose logs -f backend

# 查看最近 100 行
docker-compose logs --tail=100 backend
```

**日志轮转：**
建议在 `docker-compose.yml` 中配置日志驱动：
```yaml
x-logging: &logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "5"
```

---

## 七、安全最佳实践

### 7.1 认证与授权

1. **修改默认密码**：首次登录后立即修改 `Admin` 的默认密码
2. **修改 JWT 密钥**：`JWT_SECRET_KEY` 生产环境必须修改为 ≥ 32 字符的随机字符串
3. **最小权限原则**：为每个用户分配 `viewer` 角色，仅授予必要的管理权限
4. **密码强度**：建议启用密码强度校验（至少 12 位，含大小写数字特殊字符）

### 7.2 网络安全

1. **启用 HTTPS**：前端 Nginx 配置 SSL 证书（Let's Encrypt 免费证书）
2. **限制端口暴露**：仅暴露前端端口（3000/443），PostgreSQL 和后端 API 不直接暴露
3. **防火墙规则**：仅允许信任 IP 访问监控平台
4. **CORS 配置**：正确设置 `CORS_ORIGINS`，不使用 `["*"]` 通配符

### 7.3 SQL Server 被监控侧

1. **最小权限账号**：为监控账号仅授予 `VIEW SERVER STATE` 和 `VIEW DATABASE STATE` 权限
2. **独立账号**：避免使用 sa 或管理员账号用于监控
3. **连接加密**：如 SQL Server 支持，启用 SSL 加密连接
4. **防火墙**：在 SQL Server 侧限制仅允许监控平台所在服务器的 IP 连接 1433 端口

### 7.4 数据安全

1. **敏感字段**：`password_hash`、`MSSQL_PASSWORD` 等敏感信息不在日志和错误信息中展示
2. **.env 文件**：确保 `.env` 文件权限为 `600`，且不被提交到 Git（已在 `.gitignore` 中排除）
3. **数据加密**：PostgreSQL 可启用 pgcrypto 扩展对敏感配置进行加密存储

---

## 八、性能优化建议

### 8.1 后端性能

1. **采集间隔**：大型 SQL Server 建议将 `SCHEDULER_INTERVAL_SECONDS` 调整为 120~300 秒
2. **数据库连接池**：合理设置 `pool_size` 和 `max_overflow`，避免连接耗尽
3. **批量写入**：指标数据使用 `insert().values(list)` 批量插入，减少数据库 round trip
4. **异步 IO**：FastAPI + asyncpg + httpx 的异步架构已充分利用 CPU，避免在路由中使用同步阻塞 IO

### 8.2 数据库性能

1. **分区表**：`metrics` 表可按月分区（PostgreSQL 10+ 支持声明式分区），大幅提升历史查询性能
2. **索引维护**：定期 `REINDEX` 重建膨胀索引
3. **VACUUM ANALYZE**：PostgreSQL 定期 VACUUM（已内置 autovacuum，默认即可）
4. **数据保留策略**：
   - `metrics`：建议保留 30~90 天
   - `slow_queries`：建议保留 30 天
   - `blocking_events`：建议保留 30 天
   - `deadlocks`：建议长期保留（用于审计分析）
   - `alert_logs`：建议保留 180 天

### 8.3 前端性能

1. **路由懒加载**：各页面组件按路由分割，减少首屏加载体积
2. **图表数据采样**：长周期趋势图对密集数据点进行降采样（如最多显示 1000 点）
3. **CDN 加速**：公共静态资源可通过 CDN 加载
4. **缓存策略**：为静态资源配置合理的 HTTP Cache-Control 头

---

## 九、故障排查指南

### 9.1 常见问题及解决

| 现象 | 可能原因 | 排查步骤 | 解决方案 |
|------|---------|---------|---------|
| 前端无法加载 | Nginx 未启动 / 端口冲突 | `docker-compose ps` 检查 frontend 状态；`docker-compose logs frontend` | 重启容器或更换端口 |
| 登录失败返回 401 | 密码错误 / JWT 密钥被修改 / 用户未创建 | 检查 backend 日志中是否有认证失败记录；确认 `.env` 中 `JWT_SECRET_KEY` 一致 | 重置密码或恢复正确密钥 |
| 指标卡片无数据 | SQL Server 连接失败 / 采集任务未启动 | `docker-compose logs -f backend` 查看采集错误；检查 `MSSQL_HOST/USER/PASSWORD` | 修正 SQL Server 连接配置 |
| 死锁无记录 | system_health 会话未启用 / 死锁 XML 格式异常 | 在 SQL Server 执行：`SELECT * FROM sys.dm_xe_sessions WHERE name = 'system_health'` | 手动启用 system_health 会话 |
| 告警不触发 | 规则未启用 / 指标未到达阈值 / 处于冷却期 | 查询 `alert_logs` 表；检查 `alert_rules.enabled` 字段 | 调整阈值或禁用冷却期测试 |
| 邮件通知失败 | SMTP 配置错误 / 服务器拦截 25 端口 | 测试 `/api/config/test_smtp` 接口；查看通知服务日志 | 更换 SMTP 端口（465/587）或检查网络 |
| 数据库查询缓慢 | 缺少索引 / 表数据过大 | 对关键查询执行 `EXPLAIN ANALYZE`；检查表大小 | 创建推荐索引 / 清理旧数据 |
| 容器无法启动 | 端口被占用 / 磁盘空间不足 | `docker logs` 查看容器启动日志；`df -h` 检查磁盘 | 释放端口/磁盘空间 |

### 9.2 常用诊断命令

```bash
# 检查所有容器状态
docker-compose ps

# 查看后端日志（最近 200 行，持续输出）
docker-compose logs --tail=200 -f backend

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 进入后端容器调试
docker-compose exec backend bash

# 进入 PostgreSQL 容器调试
docker-compose exec postgres psql -U postgres -d sql_monitor

# 查看当前数据库连接数
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 查看各表记录数
docker-compose exec postgres psql -U postgres -c "\
SELECT schemaname, relname, n_live_tup \
FROM pg_stat_user_tables \
ORDER BY n_live_tup DESC;"
```

---

## 十、开发规范

### 10.1 代码风格

- **后端（Python）**：遵循 PEP 8，使用 `black` 或 `ruff` 格式化；类型注解优先（FastAPI 依赖类型提示）
- **前端（Vue 3）**：使用 Composition API；`<script setup>` 语法；组件名使用 PascalCase

### 10.2 Git 提交规范

推荐使用 Conventional Commits：

```
feat: 新增功能
fix: 修复 bug
docs: 文档变更
style: 代码格式调整
refactor: 代码重构（非功能变更）
perf: 性能优化
test: 测试相关
build: 构建/依赖变更
ci: CI/CD 配置变更
chore: 其他杂项
```

### 10.3 版本号规范

采用语义化版本（Semantic Versioning）：`MAJOR.MINOR.PATCH`
- `MAJOR`：不兼容的 API 变更
- `MINOR`：向后兼容的功能新增
- `PATCH`：向后兼容的 Bug 修复

当前版本：**1.0.11**（见 `backend/VERSION` 与 `backend/app/config.py`）

### 10.4 迁移脚本规范

**禁止**：直接在生产环境使用 `metadata.create_all()` 来修改表结构
**正确**：使用 Alembic 生成迁移脚本：

```bash
cd backend
# 自动生成迁移
alembic revision --autogenerate -m "add_column_to_users"
# 审查生成的版本文件（非常重要！）
# 应用迁移
alembic upgrade head
# 回滚
alembic downgrade -1
```

---

## 附：配置项完整速查表

| env 变量 | 默认值 | 说明 |
|---------|-------|------|
| `PROJECT_NAME` | SQL 监控平台 | 项目名称 |
| `VERSION` | 1.0.11 | 版本号（自动从 VERSION 文件读取） |
| `DEBUG` | false | 调试模式开关 |
| `CORS_ORIGINS` | ["http://localhost:3000"] | 允许的跨域来源 |
| `PG_HOST` | postgres | PostgreSQL 主机 |
| `PG_PORT` | 5432 | PostgreSQL 端口 |
| `PG_USER` | postgres | PostgreSQL 用户 |
| `PG_PASSWORD` | （必填） | PostgreSQL 密码 |
| `PG_DATABASE` | sql_monitor | 数据库名 |
| `MSSQL_HOST` | 127.0.0.1 | 目标 SQL Server 主机 |
| `MSSQL_PORT` | 1433 | 目标 SQL Server 端口 |
| `MSSQL_USER` | sa | 目标 SQL Server 用户 |
| `MSSQL_PASSWORD` | （必填） | 目标 SQL Server 密码 |
| `MSSQL_DATABASE` | master | 默认连接数据库 |
| `SCHEDULER_INTERVAL_SECONDS` | 60 | 采集间隔（秒） |
| `SMTP_SERVER` | smtp.example.com | SMTP 服务器 |
| `SMTP_PORT` | 587 | SMTP 端口 |
| `SMTP_USER` | （可选） | SMTP 用户名 |
| `SMTP_PASSWORD` | （可选） | SMTP 密码 |
| `ALERT_EMAILS` | [] | 告警接收邮箱列表 |
| `DINGTALK_WEBHOOK_URL` | （可选） | 钉钉机器人 Webhook |
| `FEISHU_WEBHOOK_URL` | （可选） | 企业微信机器人 Webhook |
| `GITHUB_TOKEN` | （可选） | GitHub 访问 Token（用于私有仓库升级） |
| `LOG_LEVEL` | INFO | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `JWT_SECRET_KEY` | sql-monitor-secret-key-change-me-in-production | JWT 签名密钥 ⚠ |
| `JWT_ALGORITHM` | HS256 | JWT 算法 |
| `JWT_EXPIRE_HOURS` | 24 | JWT 过期时间（小时） |
| `DEFAULT_ADMIN_USERNAME` | Admin | 默认管理员用户名 |
| `DEFAULT_ADMIN_PASSWORD` | Chuz0001 | 默认管理员密码 ⚠ |
