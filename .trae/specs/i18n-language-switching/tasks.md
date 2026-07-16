# Tasks

- [x] Task 1: 搭建 i18n 基础设施
  - [ ] SubTask 1.1: 安装 `vue-i18n` 依赖（`npm install vue-i18n`）
  - [ ] SubTask 1.2: 创建 `src/i18n/index.js`，配置 vue-i18n 实例（默认 zh-CN，从 localStorage 读取用户偏好）
  - [ ] SubTask 1.3: 创建 `src/i18n/zh-CN.js` 语言文件，定义所有模块的翻译 key
  - [ ] SubTask 1.4: 创建 `src/i18n/en-US.js` 语言文件，定义对应英文翻译
  - [ ] SubTask 1.5: 在 `src/main.js` 中注册 i18n 插件

- [x] Task 2: Layout 组件国际化（Layout.vue）
  - [ ] SubTask 2.1: 将侧边栏菜单项 `menuItems` 中的 label 改为 i18n key
  - [ ] SubTask 2.2: 替换顶栏中的硬编码中文（通知面板、用户下拉菜单、更新提示等）
  - [ ] SubTask 2.3: 替换标签页右键菜单中的硬编码中文
  - [ ] SubTask 2.4: 在顶栏主题切换按钮旁添加语言切换下拉按钮（显示当前语言图标/文字，点击切换 zh-CN/en-US）

- [x] Task 3: 路由标题国际化
  - [ ] SubTask 3.1: 将 `router/index.js` 中 `meta.title` 改为 i18n key
  - [ ] SubTask 3.2: 修改 Layout.vue 中的 `addTab` 函数，使标签页标题使用 i18n 翻译

- [ ] Task 4: 登录相关页面国际化（Login.vue、ForgotPassword.vue、ResetPassword.vue、Setup.vue）
  - [ ] SubTask 4.1: 提取 Login.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 4.2: 提取 ForgotPassword.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 4.3: 提取 ResetPassword.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 4.4: 提取 Setup.vue 中所有硬编码中文到语言文件并替换

- [ ] Task 5: 核心监控页面国际化（Dashboard.vue、Trends.vue、Alerts.vue、Deadlocks.vue）
  - [ ] SubTask 5.1: 提取 Dashboard.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 5.2: 提取 Trends.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 5.3: 提取 Alerts.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 5.4: 提取 Deadlocks.vue 中所有硬编码中文到语言文件并替换

- [ ] Task 6: 其他功能页面国际化（SlowQueries.vue、Blocking.vue、Disk.vue、Indexes.vue、Report.vue）
  - [ ] SubTask 6.1: 提取 SlowQueries.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 6.2: 提取 Blocking.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 6.3: 提取 Disk.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 6.4: 提取 Indexes.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 6.5: 提取 Report.vue 中所有硬编码中文到语言文件并替换

- [x] Task 7: 管理页面国际化（Settings.vue、Users.vue、AuditLogs.vue、AlertRules.vue、Instances.vue、Profile.vue、Help.vue）
  - [ ] SubTask 7.1: 提取 Settings.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.2: 提取 Users.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.3: 提取 AuditLogs.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.4: 提取 AlertRules.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.5: 提取 Instances.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.6: 提取 Profile.vue 中所有硬编码中文到语言文件并替换
  - [ ] SubTask 7.7: 提取 Help.vue 中所有硬编码中文到语言文件并替换

# Task Dependencies
- Task 2 依赖 Task 1（需要 i18n 基础设施）
- Task 3 依赖 Task 1
- Task 4-7 依赖 Task 1（可与 Task 2、3 并行，但必须在 Task 1 完成后）
- Task 4-7 之间可并行执行
