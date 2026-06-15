# Checklist

- [x] Backend: `GET /api/setup/status` 返回正确的初始化状态
- [x] Backend: `POST /api/setup/admin` 可创建第一个超级管理员
- [x] Backend: `POST /api/setup/admin` 重复调用返回 400
- [x] Backend: `/api/setup/*` 路由无需认证
- [x] Backend: Setup 路由已注册到 `api_router`
- [x] Frontend: `Setup.vue` 实现 4 步引导流程
- [x] Frontend: 步骤进度条显示正确
- [x] Frontend: `/setup` 路由可访问且不使用 Layout
- [x] Frontend: 路由守卫在未初始化时重定向到 `/setup`
- [x] Frontend: API 函数 (`getSetupStatus`, `createSetupAdmin`, `saveSetupConfig`) 已添加
- [x] Integration: 未初始化 → 访问任意页面 → 跳转到 `/setup`
- [x] Integration: 完成向导 → 跳转到登录页 → 可正常登录
