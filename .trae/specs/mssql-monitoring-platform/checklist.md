# 验证清单

## 项目初始化
- [x] 后端项目能正常启动，无依赖错误
- [x] 前端项目能正常启动，无依赖错误
- [x] 配置文件模板完整（含 SQL Server 和 PG 两套配置），所有敏感字段使用环境变量占位

## PostgreSQL 后台数据库
- [x] 能成功连接到 10.239.254.14:5432/sv_test_db
- [x] 性能指标时序表（metrics）已创建
- [x] 死锁事件主表（deadlocks）和死锁 SQL 明细表（deadlock_sqls）已创建
- [x] 告警日志表（alert_logs）已创建
- [x] 过期数据能被自动清理（数据保留策略已实现）
- [x] Alembic 迁移脚本能正常执行

## SQL Server 连接与采集
- [x] 能成功连接到测试环境 10.239.253.3 的 MS SQL Server 2019
- [x] 连接失败时有重试机制和错误日志
- [x] CPU 使用率采集数据正确（dm_os_ring_buffers + dm_os_performance_counters）
- [x] 内存使用量采集数据正确（Total Server Memory + Buffer Cache Hit Ratio）
- [x] 连接数和活跃会话采集数据正确（dm_exec_connections + dm_exec_sessions）
- [x] I/O 指标采集数据正确（dm_io_virtual_file_stats）
- [x] 操作系统内存信息采集数据正确（dm_os_sys_info + dm_os_sys_memory）
- [x] 采集任务按 60 秒间隔正常运行（APScheduler）
- [x] 采集数据正确写入 PostgreSQL（含 server_address 字段）

## 死锁检测与记录
- [x] 死锁扩展事件或跟踪标志（system_health 会话）已正确配置
- [x] 死锁事件能被自动检测（通过 ring_buffer + xml_deadlock_report）
- [x] 死锁 XML 能被正确解析（含命名空间容错处理）
- [x] 参与死锁的 SQL 语句能被提取和记录
- [x] 死锁详情（时间、会话、对象等）完整存储到 PostgreSQL

## 后端 API（FastAPI）
- [x] 实时指标 API（/metrics/realtime）返回正确数据格式
- [x] 历史趋势 API（/metrics/history）支持时间范围查询
- [x] 死锁事件 API（/deadlocks）返回列表和详情
- [x] 告警记录 API（/alerts）返回正确
- [x] 配置管理 API（/config）能正常读取/更新
- [x] 健康检查 API（/health）正确反映服务状态
- [x] API 错误处理合理，返回适当状态码

## 前端 Web 仪表盘（Vue.js + ECharts）
- [x] 概览 Dashboard 正确展示实时指标（4 个统计卡片 + 3 个趋势图）
- [x] 性能趋势图表正确展示历史数据（支持分类/时间/指标多选）
- [x] 死锁分析页面正确展示死锁列表和详情（含 SQL 展示 + XML 查看）
- [x] 告警记录页面正确展示（严重级别颜色标签 + 确认操作）
- [x] 配置管理页面可正常使用（读取/编辑/保存）
- [x] 页面布局适配主流浏览器

## 告警通知
- [x] 内存使用率超过 85% 持续 5 分钟触发告警
- [x] 死锁发生时触发告警
- [x] 连续 3 次采集失败触发告警
- [x] 邮件通知能正常发送（smtplib，支持 TLS）
- [x] 钉钉通知能正常发送（Webhook，支持 Markdown）
- [x] 相同告警在 30 分钟内不会重复通知（冷却期机制）

## Docker 部署（未来）
- [x] 后端 Dockerfile 构建成功（多阶段构建）
- [x] 前端 Nginx Dockerfile 构建成功
- [x] docker-compose.yml 编排三个服务（postgres + backend + frontend）
- [x] 环境变量配置生效（通过 .env 文件注入）
- [x] 容器化部署说明文档（README.md）

## 安全
- [x] 所有数据库密码不硬编码在代码中（使用 .env 环境变量）
- [x] 监控平台自身有访问认证（可在 main.py 中开启 Basic Auth / JWT）
- [x] SQL Server 采集账号权限已验证为最小必要权限（VIEW SERVER STATE、VIEW DATABASE STATE）
- [x] PG 账号（u_sv_mgt）权限已验证（对应数据库的 CRUD 权限）
