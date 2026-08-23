# 变更记录 - 增加关键错误飞书应用通知

- **日期**: 2026-08-23 14:50
- **类型**: 新增功能
- **影响范围**: 通知服务、告警引擎、系统配置、设置页、i18n

## 变更内容

新增飞书自建应用通知（应用通知）渠道，用于关键错误（critical 严重告警）通知：

1. **`backend/app/services/notification.py`**：
   - 新增 `FeishuAppNotifier` 类：通过飞书自建应用获取 `tenant_access_token`（带类级缓存，有效期 2 小时，提前 5 分钟刷新），再调用 `im/v1/messages` 接口以 `open_id` 为目标发送交互卡片消息。
   - 配置优先从数据库 `system_configs` 读取（`feishu_app_enabled` / `feishu_app_id` / `feishu_app_secret` / `feishu_receive_open_id`），回退到环境变量。
   - `NotificationService` 新增 `feishu_app_notifier`，`notify_all` 增加 `severity` 参数，仅当 `severity == "critical"` 时触发飞书应用通知。

2. **`backend/app/services/alert_service.py`**：`create_alert` 调用 `notify_all` 时传入 `severity`，使关键错误（内存超高、连接断开等 critical 告警）触发飞书应用通知。

3. **`backend/app/routers/feishu_test.py`**（新增）：`POST /api/feishu/test` 测试接口，校验 App ID / App Secret / open_id 并发送测试消息。

4. **`backend/app/routers/__init__.py`**：注册飞书测试路由（前缀 `/feishu`）。

5. **`backend/app/config.py`**：新增 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_RECEIVE_OPEN_ID` 环境变量配置。

6. **`backend/app/init_db.py`**：新增 4 项默认系统配置（`feishu_app_enabled` 等），启动时自动写入。

7. **`.env.example`**（根目录与 backend 目录）：补充飞书应用通知环境变量示例。

8. **`frontend/src/views/Settings.vue`**：新增"飞书应用通知（关键错误）"配置区（开关、App ID、App Secret、接收人 open_id、发送测试消息按钮）。

9. **`frontend/src/i18n/zh-CN.js` / `en-US.js`**：新增飞书应用通知配置的中英文文案。

## 变更原因

现有飞书通知仅支持群机器人 Webhook（推送到群），无法直接给指定运维人员个人发送关键错误通知。通过飞书自建应用"应用通知"可直接向用户 open_id 发送消息，实现关键错误（严重告警）的精准触达。

## 涉及文件

| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| backend/app/services/notification.py | 修改 | 新增 FeishuAppNotifier 并接入 NotificationService |
| backend/app/services/alert_service.py | 修改 | notify_all 传入 severity |
| backend/app/routers/feishu_test.py | 新增 | 飞书应用通知测试接口 |
| backend/app/routers/__init__.py | 修改 | 注册 feishu 路由 |
| backend/app/config.py | 修改 | 新增飞书应用环境变量 |
| backend/app/init_db.py | 修改 | 新增飞书应用默认配置项 |
| backend/.env.example | 修改 | 飞书应用环境变量示例 |
| .env.example | 修改 | 飞书应用环境变量示例（Docker） |
| frontend/src/views/Settings.vue | 修改 | 新增飞书应用通知配置区与测试按钮 |
| frontend/src/i18n/zh-CN.js | 修改 | 新增中文文案 |
| frontend/src/i18n/en-US.js | 修改 | 新增英文文案 |
