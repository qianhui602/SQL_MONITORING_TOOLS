# Changelog

[简体中文](./changelog.md) | **English**

## 2026-08-26

**Title:** Critical-error Feishu app notifications / Email recipient support / Modal-based notification channel config
**Files:** `backend/app/services/notification.py`, `backend/app/routers/feishu_test.py`, `backend/app/init_db.py`, `frontend/src/views/Settings.vue`, `frontend/src/components/Layout.vue`, `frontend/src/i18n/zh-CN.js`, `frontend/src/i18n/en-US.js`
**Details:**
- Added critical-error Feishu app notifications (FeishuAppNotifier): calls the Feishu custom-app API (tenant_access_token + im/v1/messages) to push an interactive red card alert directly to designated users, separate from the group robot webhook channel
- Feishu app notifications trigger only for critical-severity alerts; tenant_access_token is cached at class level (valid ~2 hours, refreshed 5 minutes early)
- Recipients now support both open_id and email address: values containing @ are auto-detected as email receive_id_type, otherwise open_id is used
- Send results now return a (success, error message) tuple; exceptions such as network connection failures, timeouts, and HTTP status errors are classified and their specific reasons surfaced to the frontend
- Feishu config is read first from the database system_configs table (feishu_app_enabled / feishu_app_id / feishu_app_secret / feishu_receive_open_id), falling back to environment variables such as FEISHU_APP_ID
- "Notification Service" page redesign: WeCom / Feishu App / SMTP / Feishu Webhook channels are displayed as a card grid; clicking a card opens its config modal with test-message sending and detailed results
- Sidebar layout fix: layout container changed to min-height: 100vh to allow page scrolling and sidebar pinned via position: sticky, so all menus fit without zooming out the browser
- Bug fix: removed the _db_loaded config cache from EmailNotifier / FeishuAppNotifier so database config is re-read on every send — disabling the feishu_app_enabled / smtp_enabled toggles now stops sending immediately without a service restart; SMTP fields are cleared when smtp_enabled is off so _is_configured() returns False

---

## 2026-07-09

**Title:** Tab icons removed / Help page expanded / Browser desktop notifications
**Files:** `frontend/src/components/Layout.vue`, `frontend/src/views/Help.vue`
**Details:**
- Removed icons from top tabs, text only for a cleaner look
- Fine-tuned tab bar padding for better spacing
- Expanded the Help page with 16 fully documented sections including feature descriptions, operation steps, metric explanations, and FAQs
- Added browser desktop notifications (based on the Notification API)
- Added "Sound Alerts" and "Desktop Notifications" toggles at the bottom of the notification panel
- System-level desktop notifications are pushed when new alerts trigger; clicking navigates to the alerts page
- Desktop notifications support permission detection, state persistence, and auto-hide when the browser is unsupported

---

## 2026-07-09T15:30:00.000Z

**Title:** Fixed /help route not registered causing "unknown page"
**Files:** `frontend/src/router/index.js`
**Details:**
- The sidebar menu already had a Help entry, but the /help route was missing from the router table
- Added the `/help` route to Vue Router pointing to the Help.vue component
- Users can now access the Help page normally instead of seeing "unknown page"

---

## 2026-07-09

**Title:** Multi-tab navigation bar
**Files:** `frontend/src/components/Layout.vue`
**Details:**
- Added a multi-tab navigation bar (inspired by Dify / Shennong Channel products)
- Tabs are created automatically when navigating to a new page; click to switch
- Tabs support closing (X button); the home tab cannot be closed
- Right-click menu supports closing current, closing others, closing all
- Added a one-click "close other tabs" button on the toolbar right
- The active tab auto-scrolls into view
- Tab styles support dark mode

---

## 2026-07-09

**Title:** Help Center page
**Files:** `frontend/src/views/Help.vue`, `frontend/src/router/index.js`, `frontend/src/components/Layout.vue`
**Details:**
- Added Help Center page (/help), accessible to all users
- Left TOC navigation + right content display with scroll highlighting
- Top search box filters help content in real time
- Covers usage instructions for all modules (Overview, Performance Trends, Deadlocks, Alerts, Slow Queries, etc.)
- Includes FAQ and contact us
- Added Help entry to the navigation menu

---

## 2026-07-09

**Title:** Removed alert acknowledge button
**Files:** `frontend/src/views/Alerts.vue`
**Details:**
- Removed the "Acknowledge Status" column and "Actions" column from the alert management page
- Removed the acknowledge button and "processed" status text
- Cleaned up related CSS styles and unused API imports

---

## 2026-07-09

**Title:** Version detection and upgrade reminder
**Files:** `backend/app/routers/version.py`, `frontend/src/components/Layout.vue`, `frontend/src/api/index.js`, `README.md`
**Details:**
- Added backend version check API (/api/version/check) comparing local version with the latest GitHub version
- Fixed hardcoded version in main.py; now unified with VERSION from config.py
- Sidebar version number is fetched dynamically; a yellow blinking dot indicates a new version
- Upgrade notification banner at the bottom with version info and upgrade guide link
- README now includes a complete upgrade guide (Docker and local development)
- Provided upgrade.sh and upgrade.bat one-click upgrade scripts

---

## 2026-07-09

**Title:** Login page UI optimization
**Files:** `frontend/src/views/Login.vue`
**Details:**
- Added gradient background and floating decorative circle animations to the left brand area
- Added grid texture background for a tech feel
- Logo has a subtle floating animation
- Feature cards use glassmorphism styling with hover animations
- Right-side login card uses glassmorphism design with a top gradient decorative bar
- Input fields optimized with bold borders, rounded corners, and focus glow
- Login button uses gradient colors with hover animation
- Error messages have icons and rounded styling
- Fade-in and card slide-in animations on page load

---

## 2026-07-09

**Title:** Statistic card show/hide feature
**Files:** `frontend/src/views/Dashboard.vue`
**Details:**
- Statistic cards support custom show/hide (all 9 metrics independently controllable)
- Added a "Statistic Cards" section to the customization panel
- Stat cards and charts share the same customization panel, displayed in sections
- Display state persists to localStorage and survives page refresh
- Added panel divider styling to separate stat cards and chart areas

---

## 2026-07-01

**Title:** Dashboard display style optimization
**Files:** `frontend/src/views/Dashboard.vue`
**Details:**
- Stat cards now have colorful gradient icons (9 metrics, each with distinct colors and icons)
- Gradient decorative bar at the top of stat cards, shown on hover
- Stat card hover effects: lift + shadow enhancement + icon scale
- Database connection status area header with icon and gradient background
- Online status indicator with breathing-light pulse animation
- Instance status labels changed to background-colored label styles
- Blue indicator bar on the left when list items are hovered
- Chart cards with colored dot markers + top gradient bars
- Chart enlarge button optimized to an icon button with hover background
- Toolbar time-range buttons changed to segmented capsule design
- Unified rounded corners and focus states for all dropdowns and buttons
- Fade-in animations for customization and sort panels
- Modal scale-slide-in animation + frosted glass background
- Loading overlay with frosted glass blur effect
- Full dark mode support (icon backgrounds, status labels, etc.)
- Optimized multi-breakpoint responsive layout (1200px/900px/768px/640px/480px)

---
