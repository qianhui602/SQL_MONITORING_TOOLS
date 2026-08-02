# 变更记录 - AI助手布局优化与报告默认展开

- **日期**: 2026-07-30 12:44
- **类型**: 逻辑修改 / UI优化
- **影响范围**: AI助手页面、整体布局

## 变更内容

### 1. 移除右侧滚动条，实现一屏显示
- 修改 `Layout.vue` 中 `.content` 容器的 `overflow-y: auto` 为 `overflow: hidden`，移除内容区右侧滚动条
- 调整 `AiAssistant.vue` 中 `.ai-assistant` 容器高度为 `calc(100vh - 190px)`，并添加 `margin: -24px` 抵消父容器padding
- 压缩各区域间距：执行区域padding从24px改为16px 24px，底部输入框padding减小，对话区域padding和gap减小

### 2. 报告默认展开显示
- 将 `expandedStep` 单值改为 `expandedSteps` 数组，支持多个步骤同时展开
- 新增 `isStepExpanded()` 函数判断步骤是否展开
- 修改 `selectTask()` 函数，加载任务详情后自动展开所有已完成且有结果的步骤
- 修改 `startPolling()` 函数，轮询时自动展开新完成的步骤
- 修改 `toggleStep()` 函数，改为数组操作（push/splice）

### 3. 样式紧凑化
- 步骤卡片间距从12px减为8px
- 步骤卡片圆角从8px减为6px
- 步骤头部内边距从14px 16px减为10px 14px
- 步骤结果区域内边距从14px 16px 14px 52px减为10px 14px 10px 50px
- 执行标题字号从18px减为16px

## 变更原因
用户需求：1）能在一个屏幕内查看，移除右侧滚动条；2）报告要在工具调用下显示而不是折叠。

## 涉及文件
| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| frontend/src/components/Layout.vue | 修改 | 移除content容器的滚动条 |
| frontend/src/views/AiAssistant.vue | 修改 | 步骤展开逻辑改为数组支持，默认展开所有结果；布局紧凑化 |
