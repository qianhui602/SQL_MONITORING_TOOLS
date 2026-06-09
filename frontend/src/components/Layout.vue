<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <img src="/LOGO.png" alt="太阳谷" class="sidebar-logo-img" v-show="!isCollapsed" />
        <img src="/LOGO.png" alt="太阳谷" class="sidebar-logo-img-mini" v-show="isCollapsed" />
      </div>

      <nav class="nav-menu">
        <router-link
          v-for="item in visibleMenuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon-wrapper">
            <span class="nav-icon" v-html="item.icon"></span>
            <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
          </span>
          <span class="nav-arrow" v-show="!isCollapsed">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </span>
        </router-link>
        <div class="nav-collapse-area" @click="toggleSidebar">
          <span v-html="isCollapsed ? collapseIconRight : collapseIconLeft"></span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <span class="version-text">v1.0.0</span>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="topbar-right">
          <!-- 通知铃铛 -->
          <div class="notification-wrap" ref="notifRef">
            <button class="notif-btn" @click="toggleNotifPanel" :title="notifUnread > 0 ? `有 ${notifUnread} 条未读通知` : '通知'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              <span v-if="notifUnread > 0" class="notif-badge">{{ notifUnread > 99 ? '99+' : notifUnread }}</span>
            </button>
            <!-- 通知下拉面板 -->
            <div v-if="notifPanelOpen" class="notif-dropdown" @click.stop>
              <div class="notif-header">
                <span class="notif-title">通知</span>
                <button v-if="notifUnread > 0" class="notif-read-all" @click="onMarkAllRead">全部已读</button>
              </div>
              <div class="notif-list">
                <div v-for="item in notifList" :key="item.id" class="notif-item" :class="{ unread: !item.read }">
                  <div class="notif-item-left">
                    <span class="notif-dot" :class="severityClass(item.severity)"></span>
                  </div>
                  <div class="notif-item-body">
                    <div class="notif-msg">{{ item.message }}</div>
                    <div class="notif-meta">
                      <span class="notif-type-tag" :class="severityClass(item.severity)">{{ item.alert_type }}</span>
                      <span class="notif-time">{{ formatTime(item.triggered_at) }}</span>
                    </div>
                  </div>
                  <div class="notif-item-actions">
                    <button class="notif-action notif-del" title="删除" @click.stop="onDelete(item)">✕</button>
                  </div>
                </div>
                <div v-if="notifList.length === 0" class="notif-empty">暂无通知</div>
              </div>
            </div>
          </div>
          <button class="theme-toggle-btn" @click="toggleTheme" :title="theme === 'light' ? '切换到暗色模式' : '切换到浅色模式'">
            <span v-if="theme === 'light'" v-html="moonIcon"></span>
            <span v-else v-html="sunIcon"></span>
          </button>
          <div class="user-info" @click="toggleUserMenu" ref="userMenuRef">
            <div class="avatar">{{ avatarText }}</div>
            <div class="user-meta" v-show="!isCollapsed">
              <span class="username">{{ displayName }}</span>
              <span class="role-tag" :class="roleClass">{{ authStore.roleLabel.value }}</span>
            </div>
            <span class="caret" v-html="caretIcon"></span>

            <div v-if="userMenuOpen" class="user-dropdown" @click.stop>
              <div class="dropdown-item disabled">
                <strong>{{ authStore.state.user?.username }}</strong>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item" @click="onLogout">
                <span v-html="logoutIcon"></span>
                <span>退出登录</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <slot />
      </main>

      <!-- 底部版权 -->
      <footer class="footer">
        太阳谷信息技术部 2026
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authStore } from '@/stores/auth'
import { useTheme } from '@/stores/theme'
import { getNotifications, markNotificationRead, deleteNotification, markAllNotificationsRead, checkUpgrade } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const { theme, toggleTheme } = useTheme()

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const userMenuOpen = ref(false)
const userMenuRef = ref(null)
const notifPanelOpen = ref(false)
const notifRef = ref(null)
const notifList = ref([])
const notifUnread = ref(0)

function severityClass(sev) {
  return { critical: 'sev-critical', high: 'sev-high', medium: 'sev-medium', low: 'sev-low' }[sev] || 'sev-medium'
}

function formatTime(d) {
  return formatDateTime(d, { second: true })
}

async function fetchNotifications() {
  try {
    const data = await getNotifications(20)
    notifList.value = data.items || []
    notifUnread.value = data.unread_count || 0
  } catch { /* ignore */ }
}

function toggleNotifPanel() {
  notifPanelOpen.value = !notifPanelOpen.value
  if (notifPanelOpen.value) fetchNotifications()
}

async function onMarkRead(item) {
  try {
    await markNotificationRead(item.id)
    item.read = true
    notifUnread.value = Math.max(0, notifUnread.value - 1)
  } catch { /* ignore */ }
}

async function onDelete(item) {
  try {
    await deleteNotification(item.id)
    const idx = notifList.value.indexOf(item)
    if (idx > -1) notifList.value.splice(idx, 1)
    if (!item.read) notifUnread.value = Math.max(0, notifUnread.value - 1)
  } catch { /* ignore */ }
}

async function onMarkAllRead() {
  try {
    await markAllNotificationsRead()
    notifList.value.forEach(item => { item.read = true })
    notifUnread.value = 0
  } catch { /* ignore */ }
}

function handleNotifOutside(e) {
  if (notifPanelOpen.value && notifRef.value && !notifRef.value.contains(e.target)) {
    notifPanelOpen.value = false
  }
}

const icons = {
  dashboard: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  trending_up: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
  lock: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
  notifications: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  clock: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  blocking: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
  disk: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
  indexes: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
  report: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
  alert_rule: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
  server: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>',
  audit: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  settings: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  users: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  upgrade: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>'
}

const collapseIconLeft = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>'
const collapseIconRight = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
const caretIcon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
const logoutIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>'
const moonIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
const sunIcon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'

const menuItems = [
  { path: '/dashboard', label: '总览', icon: icons.dashboard, requiresAdmin: false },
  { path: '/trends', label: '性能趋势', icon: icons.trending_up, requiresAdmin: false },
  { path: '/deadlocks', label: '死锁监控', icon: icons.lock, requiresAdmin: false },
  { path: '/alerts', label: '告警管理', icon: icons.notifications, requiresAdmin: false },
  { path: '/slow-queries', label: '慢查询分析', icon: icons.clock, requiresAdmin: false },
  { path: '/blocking', label: '阻塞进程', icon: icons.blocking, requiresAdmin: false },
  { path: '/disk', label: '磁盘空间', icon: icons.disk, requiresAdmin: false },
  { path: '/indexes', label: '索引分析', icon: icons.indexes, requiresAdmin: false },
  { path: '/report', label: '系统报告', icon: icons.report, requiresAdmin: false },
  { path: '/alert-rules', label: '告警规则', icon: icons.alert_rule, requiresAdmin: true },
  { path: '/instances', label: '实例管理', icon: icons.server, requiresAdmin: true },
  { path: '/audit-logs', label: '审计日志', icon: icons.audit, requiresAdmin: true },
  { path: '/settings', label: '系统设置', icon: icons.settings, requiresAdmin: true },
  { path: '/users', label: '用户管理', icon: icons.users, requiresAdmin: true },
  { path: '/upgrade', label: '在线升级', icon: icons.upgrade, requiresAdmin: true }
]

const visibleMenuItems = computed(() =>
  menuItems.filter((item) => !item.requiresAdmin || authStore.isAdmin.value)
)

const currentTitle = computed(() => route.meta?.title || '数据库监控平台')

const displayName = computed(() => {
  const u = authStore.state.user
  if (!u) return '游客'
  return u.full_name || u.username
})

const avatarText = computed(() => {
  const u = authStore.state.user
  if (!u) return '?'
  const name = u.full_name || u.username
  return name.charAt(0).toUpperCase()
})

const roleClass = computed(() => {
  const r = authStore.state.user?.role
  return {
    super_admin: 'role-purple',
    admin: 'role-blue',
    viewer: 'role-gray'
  }[r] || 'role-gray'
})

function isActive(path) {
  return route.path === path
}

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function onLogout() {
  authStore.logout()
  userMenuOpen.value = false
  router.push('/login')
}

function handleClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false
  }
  handleNotifOutside(e)
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchNotifications()
  // 获取版本号
  checkUpgrade().then(d => { currentVersion.value = d.current_version }).catch(() => {})
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ---- Sidebar ---- */
.sidebar {
  width: 240px;
  background: var(--bg-sidebar);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.sidebar.collapsed { width: 64px; }

.sidebar-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo { 
  font-size: 17px; 
  font-weight: 600; 
  white-space: nowrap; 
  letter-spacing: 0.5px; 
  color: #fff;
}
.logo-mini { 
  font-size: 18px; 
  font-weight: 700; 
  letter-spacing: 1px; 
  color: #fff;
}
.sidebar-logo-img {
  max-width: 200px;
  max-height: 50px;
  object-fit: contain;
}
.sidebar-logo-img-mini {
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
  border-radius: 4px;
}

.nav-menu {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
  position: relative;
}

.nav-collapse-area {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 48px;
  color: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  border-radius: 4px 0 0 4px;
  background: rgba(255, 255, 255, 0.04);
  transition: all 0.2s;
}
.nav-collapse-area:hover {
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.1);
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  margin-bottom: 2px;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border-radius: 6px;
  position: relative;
}

.nav-icon-wrapper {
  display: flex;
  align-items: center;
}

.nav-icon {
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; width: 20px; height: 20px;
  color: rgba(255, 255, 255, 0.55);
  transition: color 0.2s;
}

.nav-label { 
  margin-left: 12px; 
  font-size: 14px; 
  white-space: nowrap; 
  font-weight: 400; 
}

.nav-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: rgba(255, 255, 255, 0.35);
  flex-shrink: 0;
  transition: transform 0.2s;
}

.nav-item:hover {
  color: rgba(255, 255, 255, 0.95);
  background-color: rgba(255, 255, 255, 0.08);
}

.nav-item:hover .nav-icon {
  color: rgba(255, 255, 255, 0.9);
}

.nav-item.active {
  color: #fff;
  background-color: rgba(96, 165, 250, 0.15);
}

.nav-item.active .nav-icon {
  color: #60a5fa;
}

.sidebar.collapsed .nav-item { 
  justify-content: center; 
  padding: 12px 0;
}
.sidebar.collapsed .nav-label { display: none; }
.sidebar.collapsed .nav-arrow { display: none; }

.sidebar-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px;
  display: flex;
  justify-content: center;
}

.version-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

/* ---- Main Area ---- */
.main-area {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
}

.topbar {
  height: 64px;
  background-color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow);
  flex-shrink: 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }

/* ---- Theme Toggle ---- */
.theme-toggle-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;
}
.theme-toggle-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.06);
}
[data-theme='dark'] .theme-toggle-btn {
  color: #e0e0e0;
  border-color: #3a4a6e;
}
[data-theme='dark'] .theme-toggle-btn:hover {
  color: #60a5fa;
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
}

/* ---- Notification Bell ---- */
.notification-wrap {
  position: relative;
}

.notif-btn {
  position: relative;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  padding: 0;
}

.notif-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.06);
}

.notif-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ff4d4f;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
  border-radius: 9px;
  pointer-events: none;
}

.notif-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  max-height: 480px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.notif-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.notif-read-all {
  font-size: 12px;
  color: #1890ff;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.notif-read-all:hover {
  color: #40a9ff;
}

.notif-list {
  overflow-y: auto;
  max-height: 400px;
  flex: 1;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.15s;
}

.notif-item:hover {
  background: var(--hover-bg);
}

.notif-item.unread {
  background: rgba(24, 144, 255, 0.04);
}

.notif-item-left {
  padding-top: 2px;
  flex-shrink: 0;
}

.notif-dot {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.notif-dot.sev-critical { background: #ff4d4f; }
.notif-dot.sev-high { background: #fa8c16; }
.notif-dot.sev-medium { background: #1890ff; }
.notif-dot.sev-low { background: #52c41a; }

.notif-item-body {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.notif-msg {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.notif-item.unread .notif-msg {
  font-weight: 500;
}

.notif-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.notif-type-tag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.notif-type-tag.sev-critical { background: #fff1f0; color: #cf1322; }
.notif-type-tag.sev-high { background: #fff7e6; color: #d46b08; }
.notif-type-tag.sev-medium { background: #e6f7ff; color: #096dd9; }
.notif-type-tag.sev-low { background: #f6ffed; color: #389e0d; }

.notif-time {
  font-size: 11px;
  color: var(--text-muted);
}

.notif-item-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}

.notif-item:hover .notif-item-actions {
  opacity: 1;
}

.notif-action {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.15s;
}

.notif-action:hover {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.08);
}

.notif-action.notif-del:hover {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.08);
}

.notif-empty {
  padding: 40px 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}

/* ---- User Info ---- */
.user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.user-info:hover { background-color: var(--bg-primary); }

.avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 14px;
}

.user-meta {
  display: flex; flex-direction: column; line-height: 1.2;
}
.username { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.role-tag {
  display: inline-block;
  padding: 1px 6px;
  margin-top: 2px;
  border-radius: 8px;
  font-size: 11px;
  border: 1px solid transparent;
}
.role-purple { background:#f9f0ff; color:#722ed1; border-color:#d3adf7; }
.role-blue   { background:#e6f4ff; color:#1677ff; border-color:#91caff; }
.role-gray   { background:#f5f5f5; color:#666;    border-color:#d9d9d9; }

.caret { color: var(--text-muted); display: inline-flex; }

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  min-width: 180px;
  background: var(--bg-card);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 1px solid var(--border-color);
  overflow: hidden;
  z-index: 10;
}
.dropdown-item {
  padding: 10px 14px;
  font-size: 13px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.dropdown-item:hover:not(.disabled) { background: var(--bg-primary); }
.dropdown-item.disabled { cursor: default; color: var(--text-muted); }
.dropdown-divider {
  height: 1px;
  background: var(--border-color);
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg-primary);
}

.footer {
  height: 40px;
  background-color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    width: 100%;
    max-width: 280px;
  }
  .sidebar.collapsed {
    width: 0;
    overflow: hidden;
  }
  .sidebar:not(.collapsed) {
    width: 100%;
    max-width: 280px;
  }
  .topbar {
    height: 56px;
    padding: 0 16px;
  }
  .page-title {
    font-size: 16px;
  }
  .content {
    padding: 16px;
  }
  .user-meta {
    display: none;
  }
}

@media (max-width: 480px) {
  .topbar {
    height: 48px;
    padding: 0 12px;
  }
  .page-title {
    font-size: 14px;
  }
  .content {
    padding: 12px;
  }
  .data-table {
    font-size: 12px;
  }
  .data-table th,
  .data-table td {
    padding: 8px 10px;
  }
}
</style>
