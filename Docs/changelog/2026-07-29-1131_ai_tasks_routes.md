# 变更记录 - AI 诊断任务路由

- **日期**: 2026-07-29 11:31
- **类型**: 新增功能
- **影响范围**: backend/app/routers/, backend/app/services/, backend/app/routers/__init__.py

## 变更内容

新增 AI 诊断任务的后端 API 路由，包含：

1. **`backend/app/routers/ai_tasks.py`** - 新建路由模块，提供 4 个接口：
   - `POST /api/ai/tasks` - 创建 AI 诊断任务（异步执行，不阻塞响应）
   - `GET /api/ai/tasks` - 获取当前用户的任务列表（最近 50 条）
   - `GET /api/ai/tasks/{task_id}` - 获取任务详情（含执行步骤）
   - `DELETE /api/ai/tasks/{task_id}` - 删除任务及其关联步骤

2. **`backend/app/services/ai_executor.py`** - 新建任务执行器服务：
   - `create_task()` - 创建任务记录和默认诊断步骤（6 步：性能指标、死锁、慢查询、磁盘、索引、综合报告）
   - `execute_task()` - 逐步执行诊断任务，更新每步状态和结果
   - `_run_step()` - 单步执行骨架（待集成具体监控数据采集和 AI 分析）

3. **`backend/app/routers/__init__.py`** - 注册新路由到 `api_router`

## 变更原因

为 AI 诊断功能提供后端 API 支撑，使前端可以创建诊断任务、查看执行进度和结果、管理任务列表。

## 涉及文件

| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| `backend/app/routers/ai_tasks.py` | 新增 | AI 诊断任务路由模块（4 个端点） |
| `backend/app/services/ai_executor.py` | 新增 | 任务创建与执行器服务 |
| `backend/app/routers/__init__.py` | 修改 | 导入并注册 ai_tasks_router |
