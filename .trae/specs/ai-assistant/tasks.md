# Tasks

- [x] Task 1: 后端数据模型与迁移
  - [ ] SubTask 1.1: 创建 `backend/app/models/ai_task.py` 任务模型（id, user_id, query, status, created_at, updated_at）
  - [ ] SubTask 1.2: 创建 `backend/app/models/ai_task_step.py` 步骤模型（id, task_id, step_order, title, description, step_type, status, result, created_at）
  - [ ] SubTask 1.3: 创建 Alembic 迁移脚本，添加 `ai_tasks` 和 `ai_task_steps` 表
  - [ ] SubTask 1.4: 在 `backend/app/models/__init__.py` 中注册新模型

- [x] Task 2: 后端 AI 任务服务
  - [ ] SubTask 2.1: 创建 `backend/app/services/ai_context.py`，封装自动查询最新监控数据（CPU、内存、连接数、死锁、慢查询、磁盘、索引）并构建上下文的逻辑
  - [ ] SubTask 2.2: 扩展 `deepseek.py`，新增 `plan_task()` 函数，接收用户需求和监控上下文，返回执行计划（步骤列表）
  - [ ] SubTask 2.3: 扩展 `deepseek.py`，新增 `execute_step()` 函数，根据步骤类型调用对应数据源并生成分析结果
  - [ ] SubTask 2.4: 创建 `backend/app/services/ai_executor.py`，实现任务执行引擎，按计划逐步执行步骤并更新状态

- [x] Task 3: 后端 API 路由
  - [ ] SubTask 3.1: 创建 `backend/app/routers/ai_tasks.py`，实现 `POST /api/ai/tasks` 创建任务接口（接收 query，返回 task_id 和步骤列表）
  - [ ] SubTask 3.2: 实现 `GET /api/ai/tasks` 获取当前用户任务列表
  - [ ] SubTask 3.3: 实现 `GET /api/ai/tasks/{id}` 获取任务详情（含步骤状态和结果）
  - [ ] SubTask 3.4: 实现 `DELETE /api/ai/tasks/{id}` 删除任务
  - [ ] SubTask 3.5: 在 `backend/app/main.py` 中注册新路由

- [x] Task 4: 前端 API 和路由
  - [ ] SubTask 4.1: 在 `frontend/src/api/index.js` 中新增 AI 任务相关 API 函数（createTask, getTasks, getTaskDetail, deleteTask）
  - [ ] SubTask 4.2: 在 `frontend/src/router/index.js` 中添加 `/ai-assistant` 路由
  - [ ] SubTask 4.3: 在 `frontend/src/i18n/zh-CN.js` 和 `en-US.js` 中新增 AI 助手相关翻译

- [x] Task 5: 前端 AI 助手页面 - 侧边栏
  - [ ] SubTask 5.1: 创建 `frontend/src/views/AiAssistant.vue` 基础布局（左侧任务列表 + 右侧执行区）
  - [ ] SubTask 5.2: 实现任务历史列表组件（新建任务按钮、任务卡片、删除按钮）
  - [ ] SubTask 5.3: 实现任务选择和切换逻辑

- [x] Task 6: 前端 AI 助手页面 - 任务执行区
  - [ ] SubTask 6.1: 实现新建任务输入框（文本输入 + 发送按钮 + Enter 发送）
  - [ ] SubTask 6.2: 实现任务创建后的执行计划展示（步骤列表，含编号和描述）
  - [ ] SubTask 6.3: 实现步骤状态展示（加载动画、绿色对勾、红色错误图标）
  - [ ] SubTask 6.4: 实现步骤结果展开/折叠（点击已完成步骤可查看 AI 分析结果）
  - [ ] SubTask 6.5: 实现轮询任务状态，实时更新步骤进度

- [x] Task 7: 侧边栏集成和收尾
  - [ ] SubTask 7.1: 在 `Layout.vue` 的 `menuItems` 中添加 AI 助手菜单项
  - [ ] SubTask 7.2: 添加 AI 助手图标（robot SVG）
  - [ ] SubTask 7.3: 确保 i18n 翻译完整

# Task Dependencies
- Task 2 依赖 Task 1（需要数据模型）
- Task 3 依赖 Task 1 和 Task 2（需要模型和服务）
- Task 4 依赖 Task 3（需要后端 API）
- Task 5-6 依赖 Task 4（需要前端 API 函数）
- Task 7 依赖 Task 5（需要页面组件）
- Task 5-6 之间可并行执行
