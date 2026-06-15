# 系统安装引导页 (Setup Wizard) Spec

## Why

当前系统首次部署时，数据库表创建、管理员账号初始化、基础配置等操作完全在后台自动完成，用户对初始化过程无感知。当部署到新环境时，用户需要一个可视化的引导流程来完成以下操作：
1. 确认数据库表已正确创建
2. 设置超级管理员账号和密码
3. 配置后台 PostgreSQL 数据库连接
4. 完成基础系统设置

## What Changes

### 后端新增
- **POST `/api/setup/init`** — 执行系统初始化（建表、创建管理员、插入默认配置）
- **GET `/api/setup/status`** — 检查系统初始化状态（返回 `initialized: true/false`、管理员是否已创建、配置是否完整）
- **POST `/api/setup/admin`** — 创建超级管理员账号（仅首次安装时可用）
- **POST `/api/setup/config`** — 保存基础系统配置（时区、数据保留天数等）
- 在 `auth_service.py` 中放行未初始化时的 `/api/setup/*` 路由访问（无需认证）

### 前端新增
- **`Setup.vue`** — 多步安装引导页（Step 1: 欢迎 → Step 2: 管理员创建 → Step 3: 基础配置 → Step 4: 完成）
- **路由配置** — 新增 `/setup` 路由，`meta: { public: true, layout: false }`
- **路由守卫增强** — `router.beforeEach` 中增加检测：如果系统未初始化，重定向到 `/setup`

### 不修改
- 不修改现有 `init_db.py` 的自动建表逻辑
- 不修改现有 `/api/auth/*` 认证流程
- 不修改现有 Layout 组件

## Impact

- Affected specs: 认证系统、前端路由、系统配置
- Affected code:
  - `backend/app/routers/setup.py` (新文件)
  - `backend/app/routers/__init__.py` (注册新路由)
  - `frontend/src/views/Setup.vue` (新文件)
  - `frontend/src/router/index.js` (新增路由和守卫)
  - `frontend/src/api/index.js` (新增 API 函数)

## Requirements

### Requirement: 系统初始化状态检测
The system SHALL provide an endpoint to check whether the system has been initialized.

#### Scenario: 未初始化状态
- **WHEN** 首次部署，数据库表已创建但无管理员用户
- **THEN** 返回 `{ initialized: false, has_admin: false }`

#### Scenario: 已初始化状态
- **WHEN** 管理员账号已创建
- **THEN** 返回 `{ initialized: true, has_admin: true }`

### Requirement: 安装引导页
The system SHALL provide a multi-step setup wizard page.

#### Scenario: 访问未初始化系统
- **WHEN** 用户访问任意页面且系统未初始化
- **THEN** 路由守卫自动重定向到 `/setup`

#### Scenario: 完成初始化
- **WHEN** 用户完成设置向导所有步骤
- **THEN** 跳转到登录页，可正常登录使用

### Requirement: 管理员创建
The system SHALL allow creating the initial super admin account through the setup wizard.

#### Scenario: 创建管理员
- **WHEN** 用户在设置向导中填写用户名、密码、显示名称
- **THEN** 系统创建超级管理员账号并提示成功
- **AND** 后续再次调用该接口返回 400（已存在管理员）

### Requirement: 基础配置
The system SHALL allow setting basic system configurations during setup.

#### Scenario: 配置时区
- **WHEN** 用户在设置向导中选择时区
- **THEN** 系统保存时区配置到 `system_configs` 表
