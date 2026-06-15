# 通知声音提醒 Spec

## Why

当前系统在 Layout.vue 顶部有通知铃铛和未读计数，但只在页面加载或手动打开面板时才拉取数据。用户无法及时感知新告警通知，需要实时轮询并在有新通知时发出声音提醒。

## What Changes

### 后端新增
- **GET `/api/notifications/unread-count`** — 轻量级接口，仅返回 `{ unread_count: N }`，用于高频轮询（避免每次拉取全量通知列表）

### 前端修改
- **`Layout.vue`** — 新增30秒间隔轮询未读通知数；当未读数增加时播放提示音；顶部铃铛旁新增声音开关按钮（静音/开启）
- **`api/index.js`** — 新增 `getUnreadCount()` API 函数

### 不修改
- 不修改现有通知列表拉取逻辑
- 不修改现有告警写入逻辑
- 不修改 AlertLog 模型

## Impact

- Affected specs: 通知系统、告警系统
- Affected code:
  - `backend/app/routers/notifications.py` (新增接口)
  - `frontend/src/components/Layout.vue` (轮询+声音+开关)
  - `frontend/src/api/index.js` (新增 API 函数)

## Requirements

### Requirement: 未读通知计数接口
The system SHALL provide a lightweight endpoint to get unread notification count.

#### Scenario: 获取未读数
- **WHEN** 前端调用 `GET /api/notifications/unread-count`
- **THEN** 返回 `{ unread_count: N }`，N 为未确认告警数量

### Requirement: 通知轮询
The system SHALL poll for new notifications at regular intervals.

#### Scenario: 登录后自动轮询
- **WHEN** 用户已登录并处于任意页面
- **THEN** 每30秒调用一次未读计数接口

#### Scenario: 未读数增加
- **WHEN** 轮询发现未读数比上次增加
- **THEN** 播放提示音（如果声音开关为开启状态）

### Requirement: 声音开关
The system SHALL allow users to toggle notification sounds.

#### Scenario: 默认状态
- **WHEN** 用户首次访问系统
- **THEN** 声音提醒默认开启

#### Scenario: 切换声音
- **WHEN** 用户点击铃铛旁的静音按钮
- **THEN** 切换声音开关状态，保存到 localStorage
- **AND** 下次轮询时根据新状态决定是否播放

#### Scenario: 浏览器限制
- **WHEN** 用户未与页面交互过（浏览器 autoplay policy）
- **THEN** 第一次声音播放需要用户交互激活 AudioContext
- **AND** 之后的播放不受限制
