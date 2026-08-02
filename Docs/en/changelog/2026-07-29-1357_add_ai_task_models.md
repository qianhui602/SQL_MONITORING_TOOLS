# Change Log - New AI Diagnostic Task Data Models & Migration Scripts

[简体中文](../../changelog/2026-07-29-1357_add_ai_task_models.md) | **English**

- **Date**: 2026-07-29 13:57
- **Type**: New feature
- **Scope**: backend/app/models, backend/alembic/versions

## Changes
Added data models and Alembic migration scripts for the AI diagnostic task feature:
- `AiTask` model: stores user-created AI diagnostic tasks, including task status (pending/planning/running/completed/failed) and timestamps
- `AiTaskStep` model: stores task execution steps and their results, linked to AiTask via a foreign key with cascade delete
- Updated `__init__.py` to centrally export the new models
- Added migration script `002_add_ai_tasks.py` to create the `ai_tasks` and `ai_task_steps` tables

## Reason
To add AI intelligent diagnostic capability to the SQL monitoring tool, persisting user-initiated diagnostic tasks and the results of their execution steps.

## Files Involved
| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| backend/app/models/ai_task.py | Added | AiTask ORM model |
| backend/app/models/ai_task_step.py | Added | AiTaskStep ORM model |
| backend/app/models/__init__.py | Modified | Added AiTask, AiTaskStep exports |
| backend/alembic/versions/002_add_ai_tasks.py | Added | Database migration script |
