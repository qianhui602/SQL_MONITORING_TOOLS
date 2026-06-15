# Tasks

- [x] Task 1: 创建后端 Setup 路由（`/api/setup/*`）
  - [x] 1.1 新建 `backend/app/routers/setup.py`，实现 `GET /api/setup/status`（检查是否有管理员账号）
  - [x] 1.2 实现 `POST /api/setup/admin`（创建超级管理员，已有则返回 400）
  - [x] 1.3 注册路由到 `backend/app/routers/__init__.py`
  - [x] 1.4 确保 `/api/setup/*` 路由无需认证即可访问

- [x] Task 2: 创建前端安装引导页面
  - [x] 2.1 新建 `frontend/src/views/Setup.vue`，实现 4 步引导界面：
    - Step 1: 欢迎页（系统介绍、环境检测）
    - Step 2: 管理员创建（用户名、密码、显示名称）
    - Step 3: 基础配置（时区、数据保留天数）
    - Step 4: 完成页（提示重启登录）
  - [x] 2.2 添加美观的步骤进度条和过渡动画

- [x] Task 3: 前端路由和 API 集成
  - [x] 3.1 在 `frontend/src/api/index.js` 中添加 `getSetupStatus()`、`createSetupAdmin()`、`saveSetupConfig()` 函数
  - [x] 3.2 在 `frontend/src/router/index.js` 中添加 `/setup` 路由（public, no layout）
  - [x] 3.3 增强路由守卫：检查 `/api/setup/status`，未初始化时跳转到 `/setup`

- [ ] Task 4: 验证
  - [ ] 4.1 确认未初始化时访问任何页面跳转到 `/setup`
  - [ ] 4.2 确认完成向导后可正常登录
  - [ ] 4.3 确认初始化后 `GET /api/setup/status` 返回 `initialized: true`

# Task Dependencies
- Task 1 是 Task 2 和 Task 3 的前置依赖
- Task 2 依赖 Task 3.1 (API 函数)
- Task 3 无前置依赖
