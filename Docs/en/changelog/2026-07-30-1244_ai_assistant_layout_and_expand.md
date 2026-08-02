# Change Log - AI Assistant Layout Optimization & Reports Expanded by Default

[简体中文](../../changelog/2026-07-30-1244_ai_assistant_layout_and_expand.md) | **English**

- **Date**: 2026-07-30 12:44
- **Type**: Logic change / UI optimization
- **Scope**: AI Assistant page, overall layout

## Changes

### 1. Removed Right Scrollbar for One-Screen Display
- Changed `.content` container's `overflow-y: auto` to `overflow: hidden` in `Layout.vue`, removing the right scrollbar from the content area
- Adjusted the `.ai-assistant` container height to `calc(100vh - 190px)` in `AiAssistant.vue` with `margin: -24px` to offset parent container padding
- Tightened area spacing: execution area padding changed from 24px to 16px 24px, bottom input box padding reduced, conversation area padding and gap reduced

### 2. Reports Expanded by Default
- Changed the single `expandedStep` value to an `expandedSteps` array, supporting multiple steps expanded simultaneously
- Added `isStepExpanded()` function to check if a step is expanded
- Modified `selectTask()` to auto-expand all completed steps with results after loading task details
- Modified `startPolling()` to auto-expand newly completed steps during polling
- Modified `toggleStep()` to use array operations (push/splice)

### 3. Compact Styling
- Step card spacing reduced from 12px to 8px
- Step card border radius reduced from 8px to 6px
- Step header padding reduced from 14px 16px to 10px 14px
- Step result area padding reduced from 14px 16px 14px 52px to 10px 14px 10px 50px
- Execution title font size reduced from 18px to 16px

## Reason
User requirements: 1) View everything on one screen without a right scrollbar; 2) Reports should be displayed below tool calls rather than collapsed.

## Files Involved
| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| frontend/src/components/Layout.vue | Modified | Removed scrollbar from content container |
| frontend/src/views/AiAssistant.vue | Modified | Step expansion logic changed to array support; all results expanded by default; compact layout |
