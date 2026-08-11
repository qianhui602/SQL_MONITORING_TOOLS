# 变更记录 - AI助手布局修复

- **日期**: 2026-08-10 12:00
- **类型**: Bug修复
- **影响范围**: 前端AI助手页面布局

## 变更内容

### 问题
AI助手页面左侧sidebar显示异常，占据过多空间，挤压右侧主内容区。

### 根因
1. `height: calc(100vh - 190px)` 高度计算不正确
2. `margin: -24px` 负边距导致布局溢出
3. sidebar宽度280px过宽

### 修复
- 修正高度计算为 `calc(100vh - 152px)` (topbar 64px + footer 40px + padding 48px)
- 移除 `margin: -24px` 负边距
- 添加 `border-radius: 8px` 圆角
- sidebar宽度从280px缩小到220px

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|------|------|
| frontend/src/views/AiAssistant.vue | 修改 | 修正高度计算、移除负margin、缩小sidebar |
