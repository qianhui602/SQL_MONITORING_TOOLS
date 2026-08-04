# 变更记录 - 修复 AI 助手右侧空白过大

- **日期**: 2026-08-04 19:43
- **类型**: Bug修复
- **影响范围**: AI 助手前端页面

## 问题描述

在 AI 助手页面（`/ai-assistant`），当查看诊断报告时，主区域右侧出现大块空白。报告内容（代码块、SQL 优化建议）只占主区域左侧约 50-60% 的宽度，右侧约 40% 完全空白。

## 根因分析

1. `.execution-area` 没有限制 `overflow-x`，且没有 `min-width: 0`。当 `.execution-title`（h3 标签显示任务查询语句）内容较长时，flex item 默认 `min-width: auto` 会把容器撑大；同时 `.task-main` 的 `overflow: hidden` 会把右侧裁掉，导致只有左侧内容可见。
2. `.input-area` 的 `margin: 0 auto` 同时作用于 `.bottom-input`，导致底部输入框意外居中、宽度被压缩（虽然 `max-width: 100%` 覆盖了 `640px`，但 margin 没被重置）。

## 变更内容

### 1. `.execution-area` 防止内容溢出
```css
.execution-area {
  flex: 1;
  min-width: 0;           /* 新增：防止内容撑大 */
  overflow-y: auto;
  overflow-x: hidden;     /* 新增：禁止横向溢出 */
  padding: 16px 24px;
}
```

### 2. `.execution-header` 和 `.execution-title` 加溢出保护
```css
.execution-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  min-width: 0;           /* 新增 */
}

.execution-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
  flex: 1;                /* 新增：占满剩余空间 */
  min-width: 0;           /* 新增：允许收缩 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;    /* 新增：长标题省略号 */
}
```

### 3. 底部输入框重置 `.input-area` 的居中样式
```css
/* 新增 */
.bottom-input.input-area { margin: 0; max-width: 100%; }
```

## 变更原因

解决 AI 助手页面右侧空白过大的布局问题。修复后报告区域、对话区域、底部输入框均能正确撑满主区域。

## 涉及文件

| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| `frontend/src/views/AiAssistant.vue` | 修改 | 修复 .execution-area / .execution-header / .execution-title / .bottom-input 样式 |

## 验证

- 在浏览器中打开 `/ai-assistant` 页面，进入任意一个含报告的任务
- 检查诊断报告区域是否完整撑满主区域宽度（左右无大块空白）
- 检查底部"继续提问"输入框是否撑满宽度
- 检查长任务标题是否正确显示省略号