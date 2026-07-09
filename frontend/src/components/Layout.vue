<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="sidebar-logo-img" v-show="!isCollapsed" />
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="sidebar-logo-img-mini" v-show="isCollapsed" />
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
        <span class="version-text" :class="{ 'has-update': hasUpdate }" @click="hasUpdate && (showUpdateBanner = true)">
          <span class="version-label">版本</span>
          <span class="version-num">v{{ currentVersion }}</span>
          <span v-if="hasUpdate" class="update-dot"></span>
        </span>
      </div>
    </aside>

    <!-- 版本更新提示横幅 -->
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

    <!-- 主区域 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <span class="page-title">{{ currentTitle }}</span>
          <span class="version-topbar" :class="{ 'has-update': hasUpdate }" @click="hasUpdate && (showUpdateBanner = true)">
            v{{ currentVersion }}
            <span v-if="hasUpdate" class="update-dot-topbar"></span>
          </span>
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

      <!-- 多标签页导航 -->
      <div class="tab-bar" ref="tabBarRef">
        <div class="tab-list" ref="tabListRef">
          <div
            v-for="tab in tabs"
            :key="tab.path"
            class="tab-item"
            :class="{ active: isActive(tab.path) }"
            @click="switchTab(tab)"
            @contextmenu.prevent="openTabMenu($event, tab)"
          >
            <span class="tab-icon" v-html="tab.icon" v-if="tab.icon"></span>
            <span class="tab-label">{{ tab.label }}</span>
            <span
              v-if="tab.closable"
              class="tab-close"
              @click.stop="closeTab(tab)"
            >
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
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
        <!-- 右键菜单 -->
        <div v-if="tabMenuVisible" class="tab-context-menu" :style="tabMenuStyle" @click.stop>
          <div class="context-menu-item" @click="closeTab(tabMenuTarget)">关闭当前</div>
          <div class="context-menu-item" @click="closeOtherTabs">关闭其他</div>
          <div class="context-menu-item" @click="closeAllTabs">关闭全部</div>
        </div>
      </div>

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

// 多标签页
const tabs = ref([])
const tabBarRef = ref(null)
const tabListRef = ref(null)
const tabMenuVisible = ref(false)
const tabMenuStyle = ref({})
const tabMenuTarget = ref(null)

const brandTitle = ref('数据库监控平台')
const customLogoUrl = ref('')

function severityClass(sev) {
  return { critical: 'sev-critical', high: 'sev-high', medium: 'sev-medium', low: 'sev-low' }[sev] || 'sev-medium'
}

function formatTime(d) {
  return formatDateTime(d, { second: true })
}

// ===== 多标签页管理 =====
function addTab(tabRoute) {
  if (tabRoute.meta?.hideInMenu || tabRoute.meta?.public) return
  const exists = tabs.value.find(t => t.path === tabRoute.path)
  if (!exists) {
    const menuItem = visibleMenuItems.value.find(m => m.path === tabRoute.path)
    tabs.value.push({
      path: tabRoute.path,
      label: tabRoute.meta?.title || '未知页面',
      icon: menuItem?.icon || '',
      closable: tabRoute.path !== '/dashboard'
    })
  }
}

function switchTab(tab) {
  router.push(tab.path)
}

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

function closeOtherTabs() {
  const current = tabs.value.find(t => isActive(t.path))
  tabs.value = current ? [current] : []
  tabMenuVisible.value = false
}

function closeAllTabs() {
  tabs.value = []
  tabMenuVisible.value = false
  router.push('/dashboard')
}

function openTabMenu(e, tab) {
  tabMenuTarget.value = tab
  tabMenuStyle.value = { left: e.clientX + 'px', top: e.clientY + 'px' }
  tabMenuVisible.value = true
}

function closeTabMenu() {
  tabMenuVisible.value = false
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

// ---- 通知声音提醒 ----
let audioCtx = null

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)()
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume()
  }
  return audioCtx
}

function playNotificationSound() {
  if (!soundEnabled.value) return
  try {
    const ctx = getAudioContext()
    const now = ctx.currentTime
    // 双音提示：880Hz + 1100Hz，各 0.15s
    ;[880, 1100].forEach((freq, i) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.type = 'sine'
      osc.frequency.value = freq
      gain.gain.setValueAtTime(0.3, now + i * 0.18)
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.18 + 0.15)
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start(now + i * 0.18)
      osc.stop(now + i * 0.18 + 0.15)
    })
  } catch { /* ignore audio errors */ }
}

function toggleSound() {
  soundEnabled.value = !soundEnabled.value
  localStorage.setItem('notif_sound_enabled', soundEnabled.value)
}

async function pollUnreadCount() {
  try {
    const data = await getUnreadCount()
    const newCount = data.unread_count || 0
    if (prevUnreadCount.value > 0 && newCount > prevUnreadCount.value) {
      playNotificationSound()
    }
    prevUnreadCount.value = newCount
    notifUnread.value = newCount
  } catch { /* ignore */ }
}

function startNotifPolling() {
  stopNotifPolling()
  notifPollTimer.value = setInterval(pollUnreadCount, 30000)
}

function stopNotifPolling() {
  if (notifPollTimer.value) {
    clearInterval(notifPollTimer.value)
    notifPollTimer.value = null
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

const visibleMenuItems = computed(() =>
  menuItems.filter((item) => !item.requiresAdmin || authStore.isAdmin.value)
)

const currentTitle = computed(() => route.meta?.title || brandTitle.value)

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

function goToProfile() {
  userMenuOpen.value = false
  router.push('/profile')
}

function handleClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false
  }
  if (tabMenuVisible.value) {
    tabMenuVisible.value = false
  }
  handleNotifOutside(e)
}

async function fetchBrandConfig() {
  try {
    const titleData = await getConfig('brand_title')
    if (titleData?.config_value) brandTitle.value = titleData.config_value
    else if (typeof titleData === 'string' && titleData) brandTitle.value = titleData

    const logoUrl = getLogoUrl()
    const resp = await fetch(logoUrl, { method: 'HEAD' })
    if (resp.ok) {
      customLogoUrl.value = logoUrl + '?t=' + Date.now()
    }
  } catch (e) {
    console.debug('品牌配置获取失败（首次安装或无配置）')
  }
}

async function fetchVersionCheck() {
  try {
    const data = await checkVersion()
    currentVersion.value = data.current_version || '1.0.0'
    hasUpdate.value = data.has_update || false
    latestVersion.value = data.latest_version || ''
    versionMessage.value = data.message || ''
    if (hasUpdate.value) {
      showUpdateBanner.value = true
    }
  } catch {
    // 静默失败
  }
}

// 监听路由变化，自动添加标签页
watch(() => route.path, (path) => {
  addTab(route)
  // 滚动到激活的标签
  nextTick(() => {
    const active = tabBarRef.value?.querySelector('.tab-item.active')
    if (active) active.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  })
}, { immediate: true })

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchNotifications()
  startNotifPolling()
  fetchBrandConfig()
  fetchVersionCheck()
  // 初始化当前路由的标签
  addTab(route)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  stopNotifPolling()
})
</script>