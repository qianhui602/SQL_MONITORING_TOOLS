# Change Log - AI Assistant Streaming Report & Collapsed Tools

[简体中文](../../changelog/2026-07-30-1257_streaming_report_and_collapsed_tools.md) | **English**

- **Date**: 2026-07-30 12:57
- **Type**: New feature / Logic change
- **Scope**: Backend AI execution engine, AI task routes, frontend AI assistant page, i18n

## Changes

### 1. Backend: Streaming Report Output (SSE)
- **deepseek.py**: Added `chat_completion_stream()` function using `stream: true` to call the AI API, yielding content chunk by chunk
- **ai_executor.py**:
  - `execute_task()` skips the summary step; after tool steps complete, marks the task as `awaiting_report`
  - Added `execute_summary_stream()` function: aggregates all tool step results and generates the diagnostic report via streaming, saving to the database on completion
- **ai_tasks.py**: Added `GET /tasks/{task_id}/stream-report` SSE endpoint returning `text/event-stream`

### 2. Frontend: DeepSeek-style Experience
- **AiAssistant.vue** fully rewritten:
  - **Thinking/task breakdown area**: "Thinking / Task Breakdown" label at the top
  - **Tool call steps**: collapsed by default, showing only title and status icon; click to expand for detailed results
  - **Diagnostic report area**: standalone report card receiving content via SSE streaming with real-time Markdown rendering
  - **Typing animation**: three-dot bouncing animation while the report is generating
  - **Polling logic**: automatically connects to the SSE streaming endpoint when task status is `awaiting_report`
  - **Completed tasks**: summary result read directly from the database

### 3. New i18n Keys
- `taskPlanning`: Thinking / Task Breakdown
- `diagnosticReport`: Diagnostic Report
- `generatingReport`: Generating report...
- `taskAwaitingReport`: Waiting for report generation

## Reason
User requirement: DeepSeek-like experience — think first, break down the task, collapse tool calls, then stream the report separately at the end.

## Files Involved
| File | Action | Description |
|------|--------|-------------|
| backend/app/services/deepseek.py | Modified | Added chat_completion_stream streaming function |
| backend/app/services/ai_executor.py | Modified | execute_task skips summary; added execute_summary_stream |
| backend/app/routers/ai_tasks.py | Modified | Added SSE streaming report endpoint |
| frontend/src/views/AiAssistant.vue | Modified | Full rewrite: collapsed tools, streaming report area |
| frontend/src/i18n/zh-CN.js | Modified | Added 4 i18n keys |
| frontend/src/i18n/en-US.js | Modified | Added 4 i18n keys |
