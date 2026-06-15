# Tasks

- [x] Task 1: 后端新增未读通知计数接口
  - 在 `notifications.py` 中新增 `GET /notifications/unread-count` 端点
  - 仅执行一条 `SELECT count(*) FROM alert_logs WHERE acknowledged = false` 查询
  - 返回 `{ unread_count: N }`

- [x] Task 2: 前端新增 `getUnreadCount()` API 函数
  - 在 `api/index.js` 中新增 `getUnreadCount()` 函数，调用 `/notifications/unread-count`

- [x] Task 3: Layout.vue 新增通知轮询和声音播放
  - 新增 `soundEnabled` ref（从 localStorage 读取，默认 true）
  - 新增 `prevUnreadCount` ref 用于对比未读数变化
  - 新增 `notifPollTimer` 定时器，每30秒调用 `getUnreadCount()`
  - 当 `unread_count > prevUnreadCount` 且 `soundEnabled` 为 true 时，使用 Web Audio API 播放提示音
  - 新增 `playNotificationSound()` 函数，用 OscillatorNode 生成短促的双音提示音
  - 新增 `toggleSound()` 函数，切换 `soundEnabled` 并保存到 localStorage
  - 在铃铛按钮旁新增静音/开启图标按钮
  - `onMounted` 时启动轮询，`onUnmounted` 时清除定时器

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
