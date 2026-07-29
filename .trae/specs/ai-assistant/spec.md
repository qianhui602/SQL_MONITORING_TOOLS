# AI 小助手 Spec

## Why
系统已具备 AI 分析能力（死锁分析、报告生成），但用户需要一个统一的入口来自动执行数据库诊断任务。当前 AI 能力分散在各页面，缺乏一个集中式的智能助手交互界面。

## What Changes
- 新增后端 `/api/ai/tasks` 任务管理接口（创建任务、查询状态、获取结果）
- 新增后端 AI 任务执行引擎，自动规划并逐步执行诊断任务
- 新增前端 AI 助手页面（`/ai-assistant`），包含会话列表侧边栏和任务执行主区域
- 支持任务模式：用户输入诊断需求，AI 自动生成执行计划并逐步执行
- 任务历史持久化到数据库，支持查看历史任务
- 在侧边栏菜单中添加 AI 助手入口

## Impact
- Affected specs: 无
- Affected code:
  - `backend/app/models/` — 新增 `ai_task.py`、`ai_task_step.py` 模型
  - `backend/app/routers/` — 新增 `ai_tasks.py` 路由
  - `backend/app/services/deepseek.py` — 扩展支持任务规划和执行
  - `backend/app/services/ai_context.py` — 新增，封装监控数据上下文构建
  - `frontend/src/views/AiAssistant.vue` — 新增 AI 助手页面
  - `frontend/src/router/index.js` — 新增路由
  - `frontend/src/api/index.js` — 新增 API 调用函数
  - `frontend/src/i18n/zh-CN.js` / `en-US.js` — 新增翻译条目
  - `frontend/src/components/Layout.vue` — 侧边栏添加菜单项
  - `backend/alembic/versions/` — 数据库迁移脚本

## ADDED Requirements

### Requirement: AI 任务接口
系统 SHALL 提供 `/api/ai/tasks` POST 接口，接收用户诊断需求并创建执行任务。

#### Scenario: 创建诊断任务
- **WHEN** 用户输入诊断需求（如"帮我分析一下数据库的健康状况"）
- **THEN** 系统查询最新监控数据，AI 生成执行计划（多个步骤）
- **AND** 返回任务 ID 和步骤列表

#### Scenario: 逐步执行
- **WHEN** 任务创建后
- **THEN** 系统按计划逐步执行每个诊断步骤
- **AND** 每个步骤完成后更新状态（进行中 → 已完成/失败）和结果

#### Scenario: 查询任务状态
- **WHEN** 前端轮询 `GET /api/ai/tasks/{id}`
- **THEN** 返回任务当前状态和所有步骤的执行进度

### Requirement: 任务步骤
系统 SHALL 将诊断任务拆分为可执行的步骤。

#### Scenario: 步骤类型
- **WHEN** AI 生成执行计划
- **THEN** 步骤可包括：查询性能指标、分析死锁、检查慢查询、检查磁盘空间、检查索引等
- **AND** 每个步骤包含标题、描述、类型和状态

#### Scenario: 步骤执行
- **WHEN** 执行一个诊断步骤
- **THEN** 系统根据步骤类型调用对应的 API 获取数据
- **AND** 将数据传给 AI 生成分析结果

### Requirement: 智能上下文
系统 SHALL 在 AI 生成任务计划时注入当前数据库状态。

#### Scenario: 自动注入监控数据
- **WHEN** AI 生成执行计划
- **THEN** 系统自动查询最新的性能指标（CPU、内存、连接数、死锁、慢查询、磁盘、索引等）作为上下文
- **AND** AI 基于真实数据规划合理的诊断步骤

### Requirement: 会话历史
系统 SHALL 持久化任务历史，支持查看。

#### Scenario: 任务列表
- **WHEN** 用户访问 AI 助手页面
- **THEN** 左侧显示历史任务列表，按创建时间倒序排列
- **AND** 显示任务摘要（用户输入的前 N 个字符）

#### Scenario: 查看历史任务
- **WHEN** 用户点击历史任务
- **THEN** 右侧显示该任务的执行计划和各步骤结果

#### Scenario: 删除任务
- **WHEN** 用户删除一个任务
- **THEN** 任务及其所有步骤从数据库中永久删除

### Requirement: UI 布局
系统 SHALL 提供任务执行界面。

#### Scenario: 页面布局
- **WHEN** 用户访问 `/ai-assistant`
- **THEN** 左侧显示任务历史列表侧边栏（可新建任务、选择历史任务、删除任务）
- **AND** 右侧显示任务执行主区域

#### Scenario: 新建任务
- **WHEN** 用户点击"新建任务"并输入诊断需求
- **THEN** 显示执行计划（步骤列表），每个步骤显示编号、描述和状态图标

#### Scenario: 步骤状态展示
- **WHEN** 任务正在执行
- **THEN** 进行中的步骤显示加载动画
- **AND** 已完成的步骤显示绿色对勾和分析结果
- **AND** 失败的步骤显示红色错误图标和错误信息

## MODIFIED Requirements
无

## REMOVED Requirements
无
