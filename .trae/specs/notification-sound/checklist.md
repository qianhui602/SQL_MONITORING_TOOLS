# Checklist

- [x] 后端 `GET /api/notifications/unread-count` 接口返回 `{ unread_count: N }`
- [x] 前端 `api/index.js` 中 `getUnreadCount()` 函数存在且正确调用
- [x] Layout.vue 有30秒间隔轮询定时器，页面卸载时清除
- [x] 未读数增加时播放提示音（soundEnabled=true 时）
- [x] 铃铛旁有静音/开启切换按钮
- [x] 声音开关状态持久化到 localStorage
- [x] Web Audio API 提示音在无用户交互时通过 AudioContext resume 处理
