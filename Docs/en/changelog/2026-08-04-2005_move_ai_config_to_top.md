# Change Log - Move AI Model Config to Top of System Settings

[简体中文](../../changelog/2026-08-04-2005_move_ai_config_to_top.md) | **English**

- **Date**: 2026-08-04 20:05
- **Type**: UI optimization
- **Scope**: Frontend System Settings page

## Issue Description

On the `/settings` System Settings page, the "AI Model Config" section was located at the very bottom of the page (after SQL Server Connection Config → SMTP Email Notification → AI Model Config), forcing administrators to scroll down to configure DeepSeek or other AI services. Super Admin feedback indicated they "could not find the AI Model Config entry".

## Changes

Moved the "AI Model Config" block from its original position (bottom of the page, after SMTP email notification) to the top of the page, right after "Brand Settings", making it the second configuration block.

New page order:
1. Brand Settings
2. **AI Model Config** ← new position
3. System Settings
4. SQL Server Connection Config
5. SMTP Email Notification
6. (Notification test button)

## Reason

AI Model Config is the key prerequisite for the AI Assistant feature. Placing it at the top of the page ensures administrators see it immediately upon opening System Settings, with no scrolling required.

## Files Involved

| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| `frontend/src/views/Settings.vue` | Modified | Moved AI Model Config block from bottom to top |

## Verification

- Visit `/settings` and confirm the AI Model Config block is in the second position (right after Brand Settings)
- Configure DeepSeek API Key, select a model, click "Save and Apply"
- Open the AI Assistant page and start a task; confirm it uses the new configuration