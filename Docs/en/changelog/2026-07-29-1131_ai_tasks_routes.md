# Change Log - AI Diagnostic Task Routes

[简体中文](../../changelog/2026-07-29-1131_ai_tasks_routes.md) | **English**

- **Date**: 2026-07-29 11:31
- **Type**: New feature
- **Scope**: backend/app/routers/, backend/app/services/, backend/app/routers/__init__.py

## Changes

Added backend API routes for AI diagnostic tasks:

1. **`backend/app/routers/ai_tasks.py`** - New router module with 4 endpoints:
   - `POST /api/ai/tasks` - Create an AI diagnostic task (async execution, does not block the response)
   - `GET /api/ai/tasks` - Get the current user's task list (latest 50)
   - `GET /api/ai/tasks/{task_id}` - Get task details (including execution steps)
   - `DELETE /api/ai/tasks/{task_id}` - Delete a task and its related steps

2. **`backend/app/services/ai_executor.py`** - New task executor service:
   - `create_task()` - Create a task record and default diagnostic steps (6 steps: performance metrics, deadlocks, slow queries, disk, indexes, comprehensive report)
   - `execute_task()` - Execute diagnostic tasks step by step, updating each step's status and result
   - `_run_step()` - Single-step execution skeleton (awaiting integration with specific monitoring data collection and AI analysis)

3. **`backend/app/routers/__init__.py`** - Register the new router to `api_router`

## Reason

Provide backend API support for the AI diagnostic feature so the frontend can create diagnostic tasks, view execution progress and results, and manage the task list.

## Files Involved

| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| `backend/app/routers/ai_tasks.py` | Added | AI diagnostic task router module (4 endpoints) |
| `backend/app/services/ai_executor.py` | Added | Task creation and executor service |
| `backend/app/routers/__init__.py` | Modified | Import and register ai_tasks_router |
