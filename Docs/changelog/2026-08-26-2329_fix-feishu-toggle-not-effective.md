# 变更记录 - 修复飞书通知开关不生效（配置缓存问题）

- **日期**: 2026-08-26 23:29
- **类型**: Bug修复
- **影响范围**: backend/app/services/notification.py, backend/app/routers/feishu_test.py, backend/app/routers/smtp_test.py

## 变更内容
修复"前端关闭飞书消息通知开关后仍持续收到通知"的问题。

根因：`FeishuAppNotifier` 与 `EmailNotifier` 的 `_load_db_config()` 使用 `_db_loaded` 标志，只在服务进程生命周期内首次从数据库加载一次配置。`NotificationService` 实例挂载于长生命周期的告警引擎（AlertEngine），因此前端在设置页把 `feishu_app_enabled` / `smtp_enabled` 改为 `false` 并保存到数据库后，运行中的后端进程仍使用首次加载的旧配置（enabled=true）继续发送，只有重启服务才能生效。

修复内容：
1. **FeishuAppNotifier._load_db_config()**：移除 `_db_loaded` 缓存判断，每次发送前重新读取数据库中的 `feishu_app_enabled` / `feishu_app_id` / `feishu_app_secret` / `feishu_receive_open_id`，关闭开关后 `_is_configured()` 立即返回 False，不再发送。
2. **EmailNotifier._load_db_config()**：同样移除缓存；并修复 `smtp_enabled != true` 时提前 return 却不清空配置的问题——关闭开关后清空 server/user/password/recipients，确保 `_is_configured()` 返回 False 不再发送邮件。
3. **feishu_test.py / smtp_test.py**：移除已无意义的 `notifier._db_loaded = True` 赋值（测试路由直接调用底层发送方法，不经过 `_load_db_config`，注入配置不受影响）。

## 变更原因
用户反馈"关闭了飞书消息通知，为什么依旧在通知"。配置缓存导致开关变更无法即时生效，与用户预期（关闭即停）不符。

## 涉及文件
| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| backend/app/services/notification.py | 修改 | 移除 EmailNotifier / FeishuAppNotifier 的 _db_loaded 配置缓存，关闭开关立即生效 |
| backend/app/routers/feishu_test.py | 修改 | 移除已失效的 _db_loaded 赋值 |
| backend/app/routers/smtp_test.py | 修改 | 移除已失效的 _db_loaded 赋值 |
