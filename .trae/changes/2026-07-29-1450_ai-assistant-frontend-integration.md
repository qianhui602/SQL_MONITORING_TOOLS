# 变更记录 - AI 助手前端集成（API、路由、i18n）

- **日期**: 2026-07-29 14:50
- **类型**: 新增功能
- **影响范围**: frontend/src/api/index.js, frontend/src/router/index.js, frontend/src/i18n/zh-CN.js, frontend/src/i18n/en-US.js

## 变更内容
为 AI 助手功能添加前端基础设施代码：

1. **API 函数**：在 `api/index.js` 中新增 4 个 AI 任务相关 API 函数（createAiTask、getAiTasks、getAiTaskDetail、deleteAiTask），遵循现有 codebase 中直接返回 `request` Promise 的模式（因响应拦截器已自动解包 `response.data`）。
2. **路由入口**：在 `router/index.js` 中添加 `/ai-assistant` 路由，懒加载 `AiAssistant.vue` 组件，菜单标题使用 i18n key `layout.menu.aiAssistant`。
3. **i18n 翻译**：在 `zh-CN.js` 和 `en-US.js` 中新增 `aiAssistant` 翻译区块（22 个键值对），以及在 `layout.menu` 中添加 `aiAssistant` 菜单项。

## 变更原因
AI 助手功能需要前端的 API 层、路由导航和多语言支持，这些是 Vue 3 组件开发的前置依赖。

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|------|------|
| frontend/src/api/index.js | 修改 | 新增 4 个 AI 任务 API 函数 |
| frontend/src/router/index.js | 修改 | 新增 /ai-assistant 路由 |
| frontend/src/i18n/zh-CN.js | 修改 | 新增 aiAssistant 翻译区块 + 菜单项 |
| frontend/src/i18n/en-US.js | 修改 | 新增 aiAssistant 翻译区块 + 菜单项 |
