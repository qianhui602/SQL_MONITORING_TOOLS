<template>
  <div class="layout">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="sidebar-logo-img" v-show="!isCollapsed" />
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="sidebar-logo-img-mini" v-show="isCollapsed" />
      </div>
      <nav class="nav-menu">
        <router-link v-for="item in visibleMenuItems" :key="item.path" :to="item.path" class="nav-item" :class="{ active: isActive(item.path) }">
          <span class="nav-icon-wrapper">
            <span class="nav-icon" v-html="item.icon"></span>
            <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
          </span>
          <span class="nav-arrow" v-show="!isCollapsed">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </span>
        </router-link>
        <div class="nav-collapse-area" @click="toggleSidebar">
          <span v-html="isCollapsed ? collapseIconRight : collapseIconLeft"></span>
        </div>
      </nav>
      <div class="sidebar-footer">
        <span class="version-text" :class="{ 'has-update': hasUpdate }" @click="hasUpdate && (showUpdateBanner = true)">
          <span class="version-label">版本</span>
          <span class="version-num">v{{ currentVersion }}</span>
          <span v-if="hasUpdate" class="update-dot"></span>
        </span>
      </div>
    </aside>
    <div v-if="showUpdateBanner && hasUpdate" class="update-banner" @click.self="showUpdateBanner = false">
      <div class="update-banner-content">
        <div class="update-banner-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="update-banner-text">
          <strong>发现新版本 v{{ latestVersion }}</strong>
          <span>{{ versionMessage }}</span>
        </div>
        <div class="update-banner-actions">
          <a href="https://github.com/qianhui602/SQL_MONITORING_TOOLS" target="_blank" class="update-btn-primary">查看升级指南</a>
          <button class="update-btn-close" @click="showUpdateBanner = false">稍后再说</button>
        </div>
      </div>
    </div>
    <div class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <span class="page-title">{{ currentTitle }}</span>
          <span class="version-topbar" :class="{ 'has-update': hasUpdate }" @click="hasUpdate && (showUpdateBanner = true)">
            v{{ currentVersion }}
            <span v-if="hasUpdate" class="update-dot-topbar"></span>
          </span>
        </div>
        <div class="topbar-right">
          <div class="notification-wrap" ref="notifRef">
            <button class="notif-btn" @click="toggleNotifPanel" :title="notifUnread > 0 ? `有 ${notifUnread} 条未读通知` : '通知'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              <span v-if="notifUnread > 0" class="notif-badge">{{ notifUnread > 99 ? '99+' : notifUnread }}</span>
            </button>
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
              <div class="notif-footer">
                <label class="notif-setting">
                  <input type="checkbox" v-model="soundEnabled" @change="toggleSound" />
                  <span>声音提醒</span>
                </label>
                <label class="notif-setting" v-if="desktopNotifSupported">
                  <input type="checkbox" v-model="desktopNotifEnabled" @change="toggleDesktopNotif" />
                  <span>桌面通知</span>
                </label>
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
              <div class="dropdown-item" @click="goToProfile">
                <span v-html="profileIcon"></span>
                <span>个人设置</span>
              </div>
              <div class="dropdown-divider"></div>
              <div class="dropdown-item about-item">
                <span>版本</span>
                <span class="version-badge" :class="{ 'has-update': hasUpdate }" @click="hasUpdate && (showUpdateBanner = true)">
                  v{{ currentVersion }}
                  <span v-if="hasUpdate" class="update-dot-sm"></span>
                </span>
              </div>
              <div v-if="hasUpdate" class="dropdown-item update-hint" @click="showUpdateBanner = true">
                <span style="color:#faad14">发现新版本 v{{ latestVersion }}</span>
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
      <div class="tab-bar" ref="tabBarRef">
        <div class="tab-list" ref="tabListRef">
          <div v-for="tab in tabs" :key="tab.path" class="tab-item" :class="{ active: isActive(tab.path) }" @click="switchTab(tab)" @contextmenu.prevent="openTabMenu($event, tab)">
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.closable" class="tab-close" @click.stop="closeTab(tab)">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </span>
          </div>
        </div>
        <div class="tab-actions">
          <button class="tab-action-btn" @click="closeOtherTabs" title="关闭其他">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
            </svg>
          </button>
        </div>
        <div v-if="tabMenuVisible" class="tab-context-menu" :style="tabMenuStyle" @click.stop>
          <div class="context-menu-item" @click="closeTab(tabMenuTarget)">关闭当前</div>
          <div class="context-menu-item" @click="closeOtherTabs">关闭其他</div>
          <div class="context-menu-item" @click="closeAllTabs">关闭全部</div>
        </div>
      </div>
      <main class="content">
        <slot />
      </main>
      <footer class="footer">
        太阳谷信息技术部 2026 ｜ helpdesk@sunvalleyco.com
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authStore } from '@/stores/auth'
import { useTheme } from '@/stores/theme'
import { getUnreadCount, getNotifications, markNotificationRead, deleteNotification, markAllNotificationsRead, getConfig, getLogoUrl, checkVersion } from '@/api'
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
const prevUnreadCount = ref(0)
const soundEnabled = ref(localStorage.getItem('notif_sound_enabled') !== 'false')
const notifPollTimer = ref(null)
const currentVersion = ref('1.0.0')
const hasUpdate = ref(false)
const latestVersion = ref('')
const versionMessage = ref('')
const showUpdateBanner = ref(false)
const tabs = ref([])
const tabBarRef = ref(null)
const tabListRef = ref(null)
const tabMenuVisible = ref(false)
const tabMenuStyle = ref({})
const tabMenuTarget = ref(null)
const brandTitle = ref('数据库监控平台')
const customLogoUrl = ref('')

function severityClass(sev) { return { critical: 'sev-critical', high: 'sev-high', medium: 'sev-medium', low: 'sev-low' }[sev] || 'sev-medium' }
function formatTime(d) { return formatDateTime(d, { second: true }) }

function addTab(tabRoute) {
  if (tabRoute.meta?.hideInMenu || tabRoute.meta?.public) return
  const exists = tabs.value.find(t => t.path === tabRoute.path)
  if (!exists) {
    const menuItem = visibleMenuItems.value.find(m => m.path === tabRoute.path)
    tabs.value.push({ path: tabRoute.path, label: tabRoute.meta?.title || '未知页面', closable: tabRoute.path !== '/dashboard' })
  }
}
function switchTab(tab) { router.push(tab.path) }
function closeTab(tab) {
  const idx = tabs.value.findIndex(t => t.path === tab.path)
  if (idx === -1) return
  tabs.value.splice(idx, 1)
  if (isActive(tab.path)) {
    const prev = tabs.value[Math.min(idx, tabs.value.length - 1)]
    if (prev) router.push(prev.path)
    else router.push('/dashboard')
  }
}
function closeOtherTabs() { const current = tabs.value.find(t => isActive(t.path)); tabs.value = current ? [current] : []; tabMenuVisible.value = false }
function closeAllTabs() { tabs.value = []; tabMenuVisible.value = false; router.push('/dashboard') }
function openTabMenu(e, tab) { tabMenuTarget.value = tab; tabMenuStyle.value = { left: e.clientX + 'px', top: e.clientY + 'px' }; tabMenuVisible.value = true }
function closeTabMenu() { tabMenuVisible.value = false }

async function fetchNotifications() { try { const data = await getNotifications(20); notifList.value = data.items || []; notifUnread.value = data.unread_count || 0 } catch {} }
function toggleNotifPanel() { notifPanelOpen.value = !notifPanelOpen.value; if (notifPanelOpen.value) fetchNotifications() }
async function onMarkRead(item) { try { await markNotificationRead(item.id); item.read = true; notifUnread.value = Math.max(0, notifUnread.value - 1) } catch {} }
async function onDelete(item) { try { await deleteNotification(item.id); const idx = notifList.value.indexOf(item); if (idx > -1) notifList.value.splice(idx, 1); if (!item.read) notifUnread.value = Math.max(0, notifUnread.value - 1) } catch {} }
async function onMarkAllRead() { try { await markAllNotificationsRead(); notifList.value.forEach(item => { item.read = true }); notifUnread.value = 0 } catch {} }
function handleNotifOutside(e) { if (notifPanelOpen.value && notifRef.value && !notifRef.value.contains(e.target)) notifPanelOpen.value = false }

let audioCtx = null
function getAudioContext() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  if (audioCtx.state === 'suspended') audioCtx.resume()
  return audioCtx
}
function playNotificationSound() {
  if (!soundEnabled.value) return
  try {
    const ctx = getAudioContext(); const now = ctx.currentTime
    ;[880, 1100].forEach((freq, i) => {
      const osc = ctx.createOscillator(); const gain = ctx.createGain()
      osc.type = 'sine'; osc.frequency.value = freq
      gain.gain.setValueAtTime(0.3, now + i * 0.18)
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.18 + 0.15)
      osc.connect(gain); gain.connect(ctx.destination)
      osc.start(now + i * 0.18); osc.stop(now + i * 0.18 + 0.15)
    })
  } catch {}
}
function toggleSound() { soundEnabled.value = !soundEnabled.value; localStorage.setItem('notif_sound_enabled', soundEnabled.value) }
const desktopNotifSupported = ref(typeof window !== 'undefined' && 'Notification' in window)
const desktopNotifEnabled = ref(localStorage.getItem('desktop_notif_enabled') === 'true')
async function toggleDesktopNotif() {
  if (!desktopNotifSupported.value) return
  if (desktopNotifEnabled.value) {
    const perm = await Notification.requestPermission()
    if (perm === 'granted') {
      localStorage.setItem('desktop_notif_enabled', 'true')
      showDesktopNotification('桌面通知已开启', '新告警将通过系统通知提醒您', 'low')
    } else {
      desktopNotifEnabled.value = false
      localStorage.setItem('desktop_notif_enabled', 'false')
      alert('您已拒绝通知权限，桌面通知无法开启。请在浏览器设置中手动开启。')
    }
  } else {
    localStorage.setItem('desktop_notif_enabled', 'false')
  }
}
function showDesktopNotification(title, body, severity) {
  if (!desktopNotifSupported.value || !desktopNotifEnabled.value) return
  if (Notification.permission !== 'granted') return
  try {
    const colorMap = { critical: '#ff4d4f', high: '#fa8c16', medium: '#faad14', low: '#52c41a' }
    const notif = new Notification(title, {
      body: body,
      icon: '',
      badge: '',
      tag: 'sql-monitor-alert',
      requireInteraction: severity === 'critical'
    })
    notif.onclick = () => {
      window.focus()
      router.push('/alerts')
      notif.close()
    }
    setTimeout(() => notif.close(), 8000)
  } catch {}
}
async function pollUnreadCount() {
  try {
    const data = await getUnreadCount()
    const newCount = data.unread_count || 0
    if (prevUnreadCount.value > 0 && newCount > prevUnreadCount.value) {
      playNotificationSound()
      if (desktopNotifSupported.value && desktopNotifEnabled.value && Notification.permission === 'granted') {
        try {
          const latest = await getNotifications(1)
          if (latest.items && latest.items.length > 0) {
            const item = latest.items[0]
            const sevLabel = { critical: '严重告警', high: '高级告警', medium: '中级告警', low: '低级告警' }[item.severity] || '告警'
            showDesktopNotification(sevLabel + ': ' + (item.alert_type || '数据库告警'), item.message || '', item.severity)
          }
        } catch {}
      }
    }
    prevUnreadCount.value = newCount
    notifUnread.value = newCount
  } catch {}
}
function startNotifPolling() { stopNotifPolling(); notifPollTimer.value = setInterval(pollUnreadCount, 30000) }
function stopNotifPolling() { if (notifPollTimer.value) { clearInterval(notifPollTimer.value); notifPollTimer.value = null } }

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
  help: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
}
const collapseIconLeft = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>'
const collapseIconRight = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
const caretIcon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
const logoutIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>'
const profileIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
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
  { path: '/help', label: '帮助', icon: icons.help, requiresAdmin: false }
]

const visibleMenuItems = computed(() => menuItems.filter((item) => !item.requiresAdmin || authStore.isAdmin.value))
const currentTitle = computed(() => route.meta?.title || brandTitle.value)
const displayName = computed(() => { const u = authStore.state.user; if (!u) return '游客'; return u.full_name || u.username })
const avatarText = computed(() => { const u = authStore.state.user; if (!u) return '?'; const name = u.full_name || u.username; return name.charAt(0).toUpperCase() })
const roleClass = computed(() => { const r = authStore.state.user?.role; return { super_admin: 'role-purple', admin: 'role-blue', viewer: 'role-gray' }[r] || 'role-gray' })
function isActive(path) { return route.path === path }
function toggleSidebar() { isCollapsed.value = !isCollapsed.value }
function toggleUserMenu() { userMenuOpen.value = !userMenuOpen.value }
function onLogout() { authStore.logout(); userMenuOpen.value = false; router.push('/login') }
function goToProfile() { userMenuOpen.value = false; router.push('/profile') }
function handleClickOutside(e) { if (userMenuRef.value && !userMenuRef.value.contains(e.target)) userMenuOpen.value = false; if (tabMenuVisible.value) tabMenuVisible.value = false; handleNotifOutside(e) }

async function fetchBrandConfig() {
  try {
    const titleData = await getConfig('brand_title')
    if (titleData?.config_value) brandTitle.value = titleData.config_value
    else if (typeof titleData === 'string' && titleData) brandTitle.value = titleData
    const logoUrl = getLogoUrl()
    const resp = await fetch(logoUrl, { method: 'HEAD' })
    if (resp.ok) customLogoUrl.value = logoUrl + '?t=' + Date.now()
  } catch (e) { console.debug('品牌配置获取失败（首次安装或无配置）') }
}

async function fetchVersionCheck() {
  try {
    const data = await checkVersion()
    currentVersion.value = data.current_version || '1.0.0'
    hasUpdate.value = data.has_update || false
    latestVersion.value = data.latest_version || ''
    versionMessage.value = data.message || ''
    if (hasUpdate.value) showUpdateBanner.value = true
  } catch {}
}

watch(() => route.path, () => {
  addTab(route)
  nextTick(() => { const active = tabBarRef.value?.querySelector('.tab-item.active'); if (active) active.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }) })
}, { immediate: true })

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchNotifications()
  startNotifPolling()
  fetchBrandConfig()
  fetchVersionCheck()
  addTab(route)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  stopNotifPolling()
})
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }
.sidebar { width: 240px; background: var(--bg-sidebar); color: #fff; display: flex; flex-direction: column; transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); flex-shrink: 0; box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15); }
.sidebar.collapsed { width: 64px; }
.sidebar-header { height: 72px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
.sidebar-logo-img { max-width: 200px; max-height: 50px; object-fit: contain; }
.sidebar-logo-img-mini { max-width: 40px; max-height: 40px; object-fit: contain; border-radius: 4px; }
.nav-menu { flex: 1; padding: 16px 12px; overflow-y: auto; position: relative; }
.nav-collapse-area { position: absolute; right: 0; top: 50%; transform: translateY(-50%); display: flex; align-items: center; justify-content: center; width: 20px; height: 48px; color: rgba(255,255,255,0.45); cursor: pointer; border-radius: 4px 0 0 4px; background: rgba(255,255,255,0.04); transition: all 0.2s; }
.nav-collapse-area:hover { color: rgba(255,255,255,0.85); background: rgba(255,255,255,0.1); }
.nav-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; margin-bottom: 2px; color: rgba(255,255,255,0.75); text-decoration: none; transition: all 0.2s; cursor: pointer; border-radius: 6px; position: relative; }
.nav-icon-wrapper { display: flex; align-items: center; }
.nav-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 20px; height: 20px; color: rgba(255,255,255,0.55); transition: color 0.2s; }
.nav-label { margin-left: 12px; font-size: 14px; white-space: nowrap; font-weight: 400; }
.nav-arrow { display: flex; align-items: center; justify-content: center; width: 16px; height: 16px; color: rgba(255,255,255,0.35); flex-shrink: 0; transition: transform 0.2s; }
.nav-item:hover { color: rgba(255,255,255,0.95); background-color: rgba(255,255,255,0.08); }
.nav-item:hover .nav-icon { color: rgba(255,255,255,0.9); }
.nav-item.active { color: #fff; background-color: rgba(96,165,250,0.15); }
.nav-item.active .nav-icon { color: #60a5fa; }
.sidebar.collapsed .nav-item { justify-content: center; padding: 12px 0; }
.sidebar.collapsed .nav-label { display: none; }
.sidebar.collapsed .nav-arrow { display: none; }
.sidebar-footer { border-top: 1px solid rgba(255,255,255,0.08); padding: 12px; display: flex; justify-content: center; }
.version-text { font-size: 11px; color: rgba(255,255,255,0.3); cursor: default; display: inline-flex; align-items: center; gap: 4px; }
.version-text .version-label { opacity: 0.6; }
.version-text .version-num { font-weight: 500; }
.version-text.has-update { color: #faad14; cursor: pointer; }
.update-dot { width: 6px; height: 6px; border-radius: 50%; background: #faad14; display: inline-block; animation: updatePulse 2s infinite; }
@keyframes updatePulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
.update-banner { position: fixed; bottom: 20px; left: 260px; right: 20px; z-index: 1000; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.update-banner-content { display: flex; align-items: center; gap: 14px; padding: 14px 20px; background: linear-gradient(135deg, #fffbe6, #fff7cc); border: 1px solid #ffe58f; border-radius: 10px; box-shadow: 0 6px 20px rgba(250,173,20,0.2); }
.update-banner-icon { color: #faad14; flex-shrink: 0; }
.update-banner-text { flex: 1; display: flex; flex-direction: column; gap: 2px; font-size: 13px; color: #8c6e00; }
.update-banner-text strong { color: #614700; font-size: 14px; }
.update-banner-actions { display: flex; gap: 8px; flex-shrink: 0; }
.update-btn-primary { display: inline-flex; align-items: center; padding: 6px 14px; background: #faad14; color: #fff; border: none; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; text-decoration: none; transition: background 0.2s; }
.update-btn-primary:hover { background: #ffc53d; }
.update-btn-close { padding: 6px 14px; background: transparent; color: #8c6e00; border: 1px solid #ffe58f; border-radius: 6px; font-size: 13px; cursor: pointer; transition: all 0.2s; }
.update-btn-close:hover { background: rgba(250,173,20,0.1); }
.sidebar.collapsed ~ .update-banner { left: 84px; }
.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.topbar { height: 64px; background-color: var(--bg-card); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; box-shadow: var(--shadow); flex-shrink: 0; }
.topbar-right { display: flex; align-items: center; gap: 8px; }
.page-title { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.version-topbar { display: inline-flex; align-items: center; gap: 4px; margin-left: 12px; font-size: 12px; color: var(--text-muted); background: var(--bg-primary); padding: 2px 8px; border-radius: 10px; cursor: default; line-height: 1.4; }
.version-topbar.has-update { color: #faad14; background: #fffbe6; cursor: pointer; }
.update-dot-topbar { width: 6px; height: 6px; border-radius: 50%; background: #faad14; display: inline-block; animation: updatePulse 2s infinite; }
.theme-toggle-btn { width: 36px; height: 36px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-card); color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; padding: 0; }
.theme-toggle-btn:hover { color: #1890ff; border-color: #1890ff; background: rgba(24,144,255,0.06); }
.notification-wrap { position: relative; }
.notif-btn { position: relative; width: 36px; height: 36px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-card); color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; padding: 0; }
.notif-btn:hover { color: #1890ff; border-color: #1890ff; background: rgba(24,144,255,0.06); }
.notif-badge { position: absolute; top: -4px; right: -4px; min-width: 18px; height: 18px; padding: 0 5px; background: #ff4d4f; color: #fff; font-size: 11px; font-weight: 600; line-height: 18px; text-align: center; border-radius: 9px; pointer-events: none; }
.notif-dropdown { position: absolute; top: calc(100% + 8px); right: 0; width: 380px; max-height: 480px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); display: flex; flex-direction: column; z-index: 1000; overflow: hidden; }
.notif-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid var(--border-color); flex-shrink: 0; }
.notif-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.notif-read-all { font-size: 12px; color: #1890ff; background: none; border: none; cursor: pointer; padding: 0; }
.notif-list { overflow-y: auto; max-height: 400px; flex: 1; }
.notif-item { display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px; border-bottom: 1px solid var(--border-color); transition: background 0.15s; }
.notif-item.unread { background: rgba(24,144,255,0.04); }
.notif-item-left { padding-top: 2px; flex-shrink: 0; }
.notif-dot { display: block; width: 10px; height: 10px; border-radius: 50%; }
.notif-dot.sev-critical { background: #ff4d4f; }
.notif-dot.sev-high { background: #fa8c16; }
.notif-dot.sev-medium { background: #1890ff; }
.notif-dot.sev-low { background: #52c41a; }
.notif-item-body { flex: 1; min-width: 0; cursor: pointer; }
.notif-msg { font-size: 13px; color: var(--text-primary); line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; word-break: break-word; }
.notif-item.unread .notif-msg { font-weight: 500; }
.notif-meta { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.notif-type-tag { font-size: 11px; padding: 1px 6px; border-radius: 3px; font-weight: 500; }
.notif-type-tag.sev-critical { background: #fff1f0; color: #cf1322; }
.notif-type-tag.sev-high { background: #fff7e6; color: #d46b08; }
.notif-type-tag.sev-medium { background: #e6f7ff; color: #096dd9; }
.notif-type-tag.sev-low { background: #f6ffed; color: #389e0d; }
.notif-time { font-size: 11px; color: var(--text-muted); }
.notif-item-actions { display: flex; gap: 2px; flex-shrink: 0; opacity: 0; transition: opacity 0.15s; }
.notif-item:hover .notif-item-actions { opacity: 1; }
.notif-action { width: 24px; height: 24px; border: none; border-radius: 4px; background: transparent; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; transition: all 0.15s; }
.notif-action.notif-del:hover { color: #ff4d4f; background: rgba(255,77,79,0.08); }
.notif-empty { padding: 40px 16px; text-align: center; color: var(--text-muted); font-size: 13px; }
.notif-footer { display: flex; align-items: center; justify-content: space-around; padding: 10px 16px; border-top: 1px solid var(--border-color); background: var(--bg-hover); flex-shrink: 0; }
.notif-setting { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); cursor: pointer; user-select: none; }
.notif-setting input[type="checkbox"] { cursor: pointer; accent-color: #1890ff; }
.user-info { position: relative; display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: background-color 0.2s; }
.user-info:hover { background-color: var(--bg-primary); }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: #1890ff; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px; }
.user-meta { display: flex; flex-direction: column; line-height: 1.2; }
.username { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.role-tag { display: inline-block; padding: 1px 6px; margin-top: 2px; border-radius: 8px; font-size: 11px; border: 1px solid transparent; }
.role-purple { background:#f9f0ff; color:#722ed1; border-color:#d3adf7; }
.role-blue { background:#e6f4ff; color:#1677ff; border-color:#91caff; }
.role-gray { background:#f5f5f5; color:#666; border-color:#d9d9d9; }
.caret { color: var(--text-muted); display: inline-flex; }
.user-dropdown { position: absolute; top: 100%; right: 0; margin-top: 6px; min-width: 180px; background: var(--bg-card); border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 1px solid var(--border-color); overflow: hidden; z-index: 10; }
.dropdown-item { padding: 10px 14px; font-size: 13px; color: var(--text-primary); display: flex; align-items: center; gap: 8px; cursor: pointer; }
.dropdown-item:hover:not(.disabled) { background: var(--bg-primary); }
.dropdown-item.disabled { cursor: default; color: var(--text-muted); }
.dropdown-divider { height: 1px; background: var(--border-color); }
.about-item { justify-content: space-between; cursor: default; }
.version-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; color: var(--text-muted); background: var(--bg-primary); padding: 2px 8px; border-radius: 10px; }
.version-badge.has-update { color: #faad14; background: #fffbe6; }
.update-dot-sm { width: 5px; height: 5px; border-radius: 50%; background: #faad14; animation: updatePulse 2s infinite; }
.update-hint { cursor: pointer; font-size: 12px; }
.update-hint:hover { background: #fffbe6 !important; }
.tab-bar { display: flex; align-items: center; height: 38px; padding: 0 8px; background: var(--bg-card); border-bottom: 1px solid var(--border-color); position: relative; flex-shrink: 0; }
.tab-list { display: flex; align-items: center; gap: 2px; flex: 1; overflow-x: auto; overflow-y: hidden; scrollbar-width: none; }
.tab-list::-webkit-scrollbar { display: none; }
.tab-item { display: inline-flex; align-items: center; gap: 0; height: 28px; padding: 0 12px; border-radius: 4px; font-size: 12px; color: var(--text-secondary); background: transparent; cursor: pointer; white-space: nowrap; transition: all 0.15s ease; border: 1px solid transparent; flex-shrink: 0; }
.tab-item:hover { color: var(--text-primary); background: var(--bg-hover); }
.tab-item.active { color: #1890ff; background: #e6f7ff; border-color: #91d5ff; font-weight: 500; }
.tab-close { display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px; border-radius: 50%; margin-left: 2px; color: #999; transition: all 0.15s ease; }
.tab-close:hover { background: rgba(0,0,0,0.1); color: #ff4d4f; }
.tab-actions { display: flex; align-items: center; margin-left: 4px; flex-shrink: 0; }
.tab-action-btn { display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border: none; background: transparent; border-radius: 4px; color: #999; cursor: pointer; transition: all 0.15s ease; }
.tab-action-btn:hover { background: var(--bg-hover); color: #666; }
.tab-context-menu { position: fixed; z-index: 2000; background: #fff; border-radius: 6px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); padding: 4px; min-width: 120px; border: 1px solid #e8e8e8; }
.context-menu-item { padding: 6px 12px; font-size: 12px; color: #333; border-radius: 4px; cursor: pointer; transition: background 0.15s; }
.context-menu-item:hover { background: #f0f5ff; color: #1890ff; }
.content { flex: 1; padding: 24px; overflow-y: auto; background-color: var(--bg-primary); }
.footer { height: 40px; background-color: var(--bg-card); display: flex; align-items: center; justify-content: center; font-size: 12px; color: var(--text-muted); border-top: 1px solid var(--border-color); flex-shrink: 0; }
@media (max-width: 768px) {
  .sidebar { position: fixed; left: 0; top: 0; bottom: 0; z-index: 100; width: 100%; max-width: 280px; }
  .sidebar.collapsed { width: 0; overflow: hidden; }
  .sidebar:not(.collapsed) { width: 100%; max-width: 280px; }
  .topbar { height: 56px; padding: 0 16px; }
  .page-title { font-size: 16px; }
  .version-topbar { display: none; }
  .content { padding: 16px; }
  .user-meta { display: none; }
}
@media (max-width: 480px) {
  .topbar { height: 48px; padding: 0 12px; }
  .page-title { font-size: 14px; }
  .content { padding: 12px; }
}
</style>