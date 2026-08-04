# Change Log - Fix excessive right blank area in AI Assistant page

[简体中文](../../changelog/2026-08-04-1943_fix_ai_assistant_right_blank.md) | **English**

- **Date**: 2026-08-04 19:43
- **Type**: Bug fix
- **Scope**: AI Assistant frontend page

## Issue Description

On the AI Assistant page (`/ai-assistant`), when viewing a diagnostic report, the right side of the main area shows a large blank area. Report content (code blocks, SQL optimization suggestions) only takes about 50-60% of the main area's width on the left side, while the right ~40% is completely blank.

## Root Cause

1. `.execution-area` did not constrain `overflow-x` and did not have `min-width: 0`. When `.execution-title` (h3 tag displaying the task query) had long content, the default `min-width: auto` of the flex item would expand the container; meanwhile `.task-main`'s `overflow: hidden` clipped the right side, so only the left content was visible.
2. `.input-area`'s `margin: 0 auto` was also applied to `.bottom-input`, causing the bottom input box to be unintentionally centered and compressed (although `max-width: 100%` overrode `640px`, the margin was not reset).

## Changes

### 1. `.execution-area` Prevent Content Overflow
```css
.execution-area {
  flex: 1;
  min-width: 0;           /* added: prevent content from expanding */
  overflow-y: auto;
  overflow-x: hidden;     /* added: disallow horizontal overflow */
  padding: 16px 24px;
}
```

### 2. `.execution-header` and `.execution-title` Add Overflow Protection
```css
.execution-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  min-width: 0;           /* added */
}

.execution-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
  flex: 1;                /* added: fill remaining space */
  min-width: 0;           /* added: allow shrinking */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;    /* added: ellipsis for long titles */
}
```

### 3. Bottom Input Reset `.input-area` Centering Style
```css
/* added */
.bottom-input.input-area { margin: 0; max-width: 100%; }
```

## Reason

Fix the layout issue of excessive right blank area on the AI Assistant page. After the fix, the report area, conversation area, and bottom input box all correctly fill the main area.

## Files Involved

| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| `frontend/src/views/AiAssistant.vue` | Modified | Fixed .execution-area / .execution-header / .execution-title / .bottom-input styles |

## Verification

- Open `/ai-assistant` in the browser and enter any task with a report
- Check whether the diagnostic report area fully fills the main area width (no large blanks on left or right)
- Check whether the bottom "Continue question" input box fills the width
- Check whether long task titles correctly display ellipsis