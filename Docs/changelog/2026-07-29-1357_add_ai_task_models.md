# 变更记录 - 新增 AI 诊断任务数据模型与迁移脚本

- **日期**: 2026-07-29 13:57
- **类型**: 新增功能
- **影响范围**: backend/app/models, backend/alembic/versions

## 变更内容
新增 AI 诊断任务功能的数据模型和 Alembic 迁移脚本：
- `AiTask` 模型：存储用户创建的 AI 诊断任务，包含任务状态（pending/planning/running/completed/failed）和时间戳
- `AiTaskStep` 模型：存储任务的执行步骤及每个步骤的结果，通过外键关联到 AiTask，支持级联删除
- 更新 `__init__.py` 集中导出新模型
- 新增迁移脚本 `002_add_ai_tasks.py`，创建 `ai_tasks` 和 `ai_task_steps` 两张表

## 变更原因
为 SQL 监控工具添加 AI 智能诊断功能，需要持久化存储用户发起的诊断任务及其执行步骤的结果。

## 涉及文件
| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| backend/app/models/ai_task.py | 新增 | AiTask ORM 模型 |
| backend/app/models/ai_task_step.py | 新增 | AiTaskStep ORM 模型 |
| backend/app/models/__init__.py | 修改 | 添加 AiTask、AiTaskStep 导出 |
| backend/alembic/versions/002_add_ai_tasks.py | 新增 | 数据库迁移脚本 |
