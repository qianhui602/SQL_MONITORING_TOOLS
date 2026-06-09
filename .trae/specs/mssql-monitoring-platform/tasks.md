# 任务清单

## Task 1: 项目初始化与目录结构搭建
搭建项目基础骨架，包括前后端项目结构、依赖管理和配置文件。
- [x] 创建后端项目目录（Python FastAPI）
- [x] 创建前端项目目录（Vue.js）
- [x] 配置虚拟环境和依赖管理（requirements.txt / poetry）
- [x] 配置前端依赖（package.json）
- [x] 创建配置文件模板，包含 SQL Server 和 PG 两套连接配置（config.py / .env.example）
- [x] 初始化 Git 仓库并配置 .gitignore

## Task 2: PostgreSQL 后台数据库设计与初始化
在 PG 10.239.254.14:5432/sv_test_db 上创建所需的表结构。
- [x] 设计并创建性能指标时序表（按指标分类，含采集时间戳）
- [x] 设计并创建死锁事件主表（含死锁 XML、发生时间、受害会话等）
- [x] 设计并创建死锁 SQL 明细表（关联死锁事件主表）
- [x] 设计并创建告警日志表
- [x] 设计并创建系统配置表
- [x] 实现自动建表/数据库迁移脚本（Alembic）
- [x] 实现数据保留策略（定时清理过期数据）

## Task 3: MS SQL Server 连接与数据采集模块
实现与目标 SQL Server（测试环境 10.239.253.3）的连接，并编写采集各类性能指标的 SQL 查询。
- [x] 实现数据库连接管理器（连接池、重试机制、多目标切换）
- [x] 编写 SQL Server CPU 使用率采集查询
- [x] 编写 SQL Server 内存使用量采集查询（缓冲池、缓存命中率等）
- [x] 编写当前连接数和活跃会话采集查询
- [x] 编写 I/O 指标采集查询
- [x] 编写数据库文件状态采集查询
- [x] 编写服务器操作系统内存信息采集查询（通过 `sys.dm_os_sys_info` 等）
- [x] 实现定时任务调度框架（APScheduler），配置 60 秒采集间隔
- [x] 将采集数据写入 PostgreSQL

## Task 4: 死锁检测与死锁 SQL 记录模块
实现死锁事件的自动捕获、XML 解析和 SQL 语句提取。
- [x] 配置 SQL Server 扩展事件（Extended Events）或启用跟踪标志 1222 捕获死锁
- [x] 编写死锁事件轮询/监听代码
- [x] 解析死锁 XML 报告，提取参与会话、SQL 语句、涉及对象
- [x] 将死锁详情存储到 PostgreSQL
- [x] 实现死锁告警触发逻辑

## Task 5: 后端 API 开发
开发供前端调用的 RESTful API（FastAPI）。
- [x] 实现获取实时指标数据 API（当前 CPU/内存/连接）
- [x] 实现获取历史趋势数据 API（按时间范围）
- [x] 实现死锁事件列表与详情 API
- [x] 实现告警记录列表 API
- [x] 实现系统配置读取/更新 API
- [x] 实现健康检查 API（含 SQL Server 和 PG 连接状态）

## Task 6: 前端 Web 仪表盘开发
基于 Vue.js + ECharts 构建可视化监控面板。
- [x] 初始化 Vue.js 项目并配置路由
- [x] 实现整体布局框架（侧边栏导航、顶部栏）
- [x] 实现概览 Dashboard 页面（CPU/内存/连接数仪表盘卡片）
- [x] 实现性能趋势图表页面（ECharts 折线图）
- [x] 实现死锁分析页面（列表 + 详情弹窗 + SQL 展示）
- [x] 实现告警记录页面
- [x] 实现配置管理页面（采集间隔、告警阈值、目标 SQL Server 切换等）

## Task 7: 告警通知模块
实现邮件和钉钉通知功能。
- [x] 实现邮件发送功能（smtplib）
- [x] 实现钉钉机器人 Webhook 通知
- [x] 实现告警规则引擎（阈值判断、持续次数判定）
- [x] 实现告警去重和防重复通知（相同告警 30 分钟内不重复发送）

## Task 8: Docker 容器化部署（未来）
配置 Docker 构建和编排文件。
- [x] 编写后端 Dockerfile（Task 1 完成）
- [x] 编写前端 Nginx Dockerfile（Task 1 完成）
- [x] 编写 docker-compose.yml（PG 为外部依赖）
- [x] 配置环境变量注入（SQL Server 连接串、PG 连接串等）
- [x] 编写部署说明文档（README.md）

## Task 9: 代码验证与全面修复
对系统进行代码审查、问题修复和最终验证。
- [x] 代码结构完整性验证
- [x] Python 语法检查
- [x] Import 依赖关系验证
- [x] SQL 查询语法检查
- [x] 配置一致性验证
- [x] P1: ORM 表名一致性修复（metric_records→metrics, deadlock_events→deadlocks, FK引用修正）
- [x] P2: Dashboard 前后端数据字段匹配修复（summary/cpu/memory/connection 字段对齐）
- [x] P3: 配置更新 API 参数名修复（{value}→{config_value}）
- [x] P4: 插入数据缺少 server_address 字段修复
- [x] P5: 缺失 httpx/python-dateutil 依赖修复
- [x] P6: Trends 页面参数与数据字段匹配修复
- [x] P7: Deadlocks 页面字段名修复（occurred_at→occur_at, objects→involved_objects）

## 任务依赖关系
- [Task 2] 依赖 [Task 1] 完成 ✅
- [Task 3] 依赖 [Task 1] 完成 ✅
- [Task 4] 依赖 [Task 1] 完成 ✅
- [Task 5] 依赖 [Task 2]、[Task 3]、[Task 4] 完成 ✅
- [Task 6] 依赖 [Task 5] 完成 ✅
- [Task 7] 依赖 [Task 1]、[Task 2] 完成 ✅
- [Task 8] 依赖 [Task 1]~[Task 7] 全部完成 ✅
- [Task 9] 依赖 [Task 1]~[Task 7] 完成 ✅
