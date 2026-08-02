# 变更记录 - AI助手流式报告与工具折叠

- **日期**: 2026-07-30 12:57
- **类型**: 新增功能 / 逻辑修改
- **影响范围**: 后端AI执行引擎、AI任务路由、前端AI助手页面、i18n

## 变更内容

### 1. 后端：流式输出报告（SSE）
- **deepseek.py**：新增 `chat_completion_stream()` 函数，使用 `stream: true` 调用AI API，逐块 yield 内容
- **ai_executor.py**：
  - `execute_task()` 跳过 summary 步骤，工具步骤完成后标记任务为 `awaiting_report`
  - 新增 `execute_summary_stream()` 函数：聚合所有工具步骤结果，流式生成诊断报告，完成后保存到数据库
- **ai_tasks.py**：新增 `GET /tasks/{task_id}/stream-report` SSE端点，返回 `text/event-stream`

### 2. 前端：DeepSeek 式体验
- **AiAssistant.vue** 完全重写：
  - **思考/任务拆解区域**：顶部显示"思考 / 任务拆解"标签
  - **工具调用步骤**：默认折叠，只显示标题和状态图标，点击可展开查看详细结果
  - **诊断报告区域**：独立的报告卡片，通过 SSE 流式接收内容，实时 Markdown 渲染
  - **打字动画**：报告生成中显示三点跳动动画
  - **轮询逻辑**：任务状态为 `awaiting_report` 时自动连接 SSE 流式端点
  - **已完成任务**：直接从数据库读取 summary 结果显示

### 3. i18n 新增键
- `taskPlanning`: 思考 / 任务拆解
- `diagnosticReport`: 诊断报告
- `generatingReport`: 正在生成报告...
- `taskAwaitingReport`: 等待报告生成

## 变更原因
用户需求：类似 DeepSeek 的体验——先思考、拆解任务，工具调用折叠，最后单独流式输出报告。

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|------|------|
| backend/app/services/deepseek.py | 修改 | 新增 chat_completion_stream 流式调用函数 |
| backend/app/services/ai_executor.py | 修改 | execute_task 跳过 summary；新增 execute_summary_stream |
| backend/app/routers/ai_tasks.py | 修改 | 新增 SSE 流式报告端点 |
| frontend/src/views/AiAssistant.vue | 修改 | 完全重写：工具折叠、报告流式区域 |
| frontend/src/i18n/zh-CN.js | 修改 | 新增4个 i18n 键 |
| frontend/src/i18n/en-US.js | 修改 | 新增4个 i18n 键 |
