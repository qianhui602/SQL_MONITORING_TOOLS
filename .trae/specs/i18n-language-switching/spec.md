# 多语言切换 Spec

## Why
当前前端所有 UI 文本均硬编码为中文，无法支持非中文用户。为满足国际化需求，需引入 i18n 机制，支持中文（zh-CN）与英文（en-US）切换，并为未来添加更多语言预留扩展能力。

## What Changes
- 引入 `vue-i18n` 作为 i18n 框架
- 创建语言文件（`zh-CN`、`en-US`），覆盖所有前端视图中的 UI 文本
- 在顶栏（topbar）添加语言切换下拉按钮
- 用户切换语言后将偏好持久化到 `localStorage`，下次访问自动恢复
- 将路由 `meta.title` 改为 i18n key，使标签页和面包屑自动跟随语言切换

## Impact
- Affected specs: 无
- Affected code:
  - `frontend/package.json` — 新增 `vue-i18n` 依赖
  - `frontend/src/main.js` — 注册 i18n 插件
  - `frontend/src/i18n/` — 新增语言文件目录（`index.js`、`zh-CN.js`、`en-US.js`）
  - `frontend/src/components/Layout.vue` — 添加语言切换按钮，替换硬编码文本
  - `frontend/src/views/*.vue` — 所有视图中的硬编码中文替换为 `$t()` 调用
  - `frontend/src/router/index.js` — `meta.title` 改为 i18n key
  - `frontend/src/views/Login.vue` — 登录页等无 Layout 页面也需支持 i18n

## ADDED Requirements

### Requirement: i18n 基础设施
系统 SHALL 在前端引入 `vue-i18n`，提供 `zh-CN`（默认）和 `en-US` 两种语言包。

#### Scenario: 初始化加载
- **WHEN** 用户首次访问系统
- **THEN** 系统默认使用中文（zh-CN）加载 UI 文本

#### Scenario: 语言包结构
- **WHEN** 查看语言文件
- **THEN** 每种语言包含按模块分组的翻译 key（layout、dashboard、settings、login 等）

### Requirement: 语言切换 UI
系统 SHALL 在顶栏提供语言切换下拉按钮，位于主题切换按钮旁。

#### Scenario: 切换语言
- **WHEN** 用户点击语言切换按钮并选择另一种语言
- **THEN** 所有 UI 文本立即切换为目标语言，无需刷新页面

#### Scenario: 持久化语言偏好
- **WHEN** 用户切换语言
- **THEN** 偏好保存到 `localStorage`（key: `app_language`）
- **WHEN** 用户再次访问系统
- **THEN** 自动使用上次保存的语言

### Requirement: 路由标题国际化
系统 SHALL 使路由 `meta.title` 和标签页标题跟随当前语言自动更新。

#### Scenario: 标签页标题
- **WHEN** 用户切换语言
- **THEN** 侧边栏菜单项和标签页标题自动更新为当前语言的翻译

### Requirement: 向后兼容
系统 SHALL 保持中文为默认语言，确保不支持 i18n 的区域（如动态获取的后端消息）仍正确显示。

#### Scenario: 后端返回的中文消息
- **WHEN** 后端 API 返回中文错误或提示信息
- **THEN** 前端直接展示后端返回的原始文本，不做翻译处理

## MODIFIED Requirements
无

## REMOVED Requirements
无
