# Change Log - AI Assistant Rework: Chat Interaction, Context Follow-ups, HTML Rendering

[简体中文](../../changelog/2026-07-30-0920_ai_assistant_rework.md) | **English**

- **Date**: 2026-07-30 09:20
- **Type**: New feature / Bug fix
- **Scope**: AI Assistant frontend page, backend task execution engine, tab management

## Changes

### 1. Step Result Display (Issue #1)
Completed diagnostic steps can now show detailed analysis results by clicking the expand arrow (▼). Step card titles and descriptions are always visible; results are shown after expanding.

### 2. Chat-style Follow-up Interaction (Issue #2 & #3)
After a task completes, the bottom input box stays visible (no longer covered). Users can type follow-up questions in the input box, and the AI answers based on the previous analysis context, forming multi-turn conversations. Follow-up results are displayed as chat bubbles below the step list.

### 3. Markdown → HTML Rendering (Issue #4)
Rewrote the `renderMarkdown` function to support HTML rendering of the following Markdown formats:
- Headings (h1-h4)
- Bold, italic
- Unordered lists, ordered lists
- Code blocks (```...```) and inline code
- Blockquotes (>)
- Horizontal rules (---)
- Links
- Auto line wrapping

### 4. Tab "Unknown" Label Fix (Issue #5)
Modified the `addTab` function to prefer the translated menu item label (`menuItem.label`); if the menu item doesn't exist, fall back to the route `meta.title` translation; if both are empty, skip adding the tab. Completely eliminates "Unknown" labels.

### 5. Backend Follow-up API
Added `POST /api/ai/tasks/{task_id}/followup` endpoint accepting `{ query: str }`:
- Loads task history steps as context
- Builds multi-turn conversation message list (system + user + assistant alternating)
- Calls AI to generate an answer, saved as a step record with `step_type="followup"`
- Added public `chat_completion()` and `get_base_url()` functions

### 6. i18n Translations
Added the following translation keys in both Chinese and English:
- `followUpPlaceholder`: follow-up input placeholder
- `followUpFailed`: follow-up failure message
- `userMessage`: user message label
- `aiResponse`: AI response label
- `stepResult`: step result label
- `followUp`: follow-up label

## Files Involved
| File | Action | Description |
|------|--------|-------------|
| frontend/src/views/AiAssistant.vue | Modified | Full rewrite: chat layout, Markdown rendering, follow-up feature |
| frontend/src/components/Layout.vue | Modified | Fixed addTab function, eliminated Unknown labels |
| frontend/src/api/index.js | Modified | Added followUpAiTask API function |
| frontend/src/i18n/zh-CN.js | Modified | Added 6 Chinese translation keys |
| frontend/src/i18n/en-US.js | Modified | Added 6 English translation keys |
| backend/app/routers/ai_tasks.py | Modified | Added followup endpoint and request model |
| backend/app/services/ai_executor.py | Modified | Added execute_followup function |
| backend/app/services/deepseek.py | Modified | Added chat_completion and get_base_url public functions |

## Git Info
- commit (feature): `aae313e`
- commit (fix): `9441f9e` — fixed create_task missing return causing task creation failure
- Branch: `master`
- Push: `02d01c5..9441f9e master -> master`
