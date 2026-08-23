# 变更记录 - 优化侧边栏菜单和通知渠道弹窗

- **日期**: 2026-08-24 10:30
- **类型**: 逻辑修改
- **影响范围**: 前端布局、设置页、通知配置

## 变更内容

1. **侧边栏菜单优化**（[Layout.vue](file:///workspace/frontend/src/components/Layout.vue)）：
   - `nav-menu` 增加细滚动条（4px 宽，半透明）
   - 菜单项间距从 12px→9px，字号 14→13，图标 20→18
   - padding 从 16px→8px，margin-bottom 从 2px→1px
   - 使 16 个菜单项在标准高度下无需缩小浏览器即可全部显示

2. **通知渠道配置弹窗化**（[Settings.vue](file:///workspace/frontend/src/views/Settings.vue)）：
   - 将原来 4 个独立的通知配置区（企微/飞书应用/SMTP/飞书 Webhook）合并为 1 个"通知渠道配置"卡片网格
   - 每个渠道显示为带图标、名称、状态的卡片，点击打开弹窗配置
   - 弹窗内包含该渠道的所有配置项和测试按钮
   - 新增 `channelModalVisible`、`currentChannel`、`channelModalTitle` 状态
   - 新增 `openChannelModal`、`closeChannelModal`、`saveChannelConfig` 函数
   - 新增飞书 Webhook 配置支持（`feishuConfigs`、`feishu_enabled`、`feishu_webhook_url`）

3. **后端初始化配置**（[init_db.py](file:///workspace/backend/app/init_db.py)）：
   - 新增 `feishu_enabled`、`feishu_webhook_url` 默认配置项

4. **i18n 文案**（[zh-CN.js](file:///workspace/frontend/src/i18n/zh-CN.js)、[en-US.js](file:///workspace/frontend/src/i18n/en-US.js)）：
   - 新增 `wecomChannel`、`feishuAppChannel`、`smtpChannel`、`feishuWebhookChannel`
   - 新增 `feishuToggle`、`feishuToggleDesc`、`feishuWebhook`、`feishuWebhookDesc`

## 变更原因

1. 侧边栏菜单项过多（16 项），用户需要缩小浏览器才能看到全部菜单，体验不佳
2. 通知渠道配置（企微/飞书应用/SMTP/飞书 Webhook）占用过多垂直空间，导致设置页过长，改为弹窗模式可显著缩短页面长度

## 涉及文件

| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| frontend/src/components/Layout.vue | 修改 | 侧边栏菜单紧凑化、增加滚动条 |
| frontend/src/views/Settings.vue | 修改 | 通知渠道改为卡片+弹窗模式，新增飞书 Webhook 配置 |
| backend/app/init_db.py | 修改 | 新增飞书 Webhook 默认配置项 |
| frontend/src/i18n/zh-CN.js | 修改 | 新增渠道名称和飞书 Webhook 文案 |
| frontend/src/i18n/en-US.js | 修改 | 新增渠道名称和飞书 Webhook 文案 |
