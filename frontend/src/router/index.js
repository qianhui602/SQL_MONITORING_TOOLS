import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '@/stores/auth'
import { getSetupStatus } from '@/api'

let setupStatusCache = null
let setupStatusCacheTime = 0
const CACHE_TTL = 5 * 60 * 1000

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'login.welcome', public: true, layout: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { title: 'forgotPassword.title', public: true, layout: false }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue'),
    meta: { title: 'forgotPassword.resetTitle', public: true, layout: false }
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/views/Setup.vue'),
    meta: { title: 'setup.welcomeTitle', public: true, layout: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'layout.menu.dashboard', icon: 'dashboard' }
  },
  {
    path: '/trends',
    name: 'Trends',
    component: () => import('@/views/Trends.vue'),
    meta: { title: 'layout.menu.trends', icon: 'trending_up' }
  },
  {
    path: '/deadlocks',
    name: 'Deadlocks',
    component: () => import('@/views/Deadlocks.vue'),
    meta: { title: 'layout.menu.deadlocks', icon: 'lock' }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('@/views/Alerts.vue'),
    meta: { title: 'layout.menu.alerts', icon: 'notifications' }
  },
  {
    path: '/slow-queries',
    name: 'SlowQueries',
    component: () => import('@/views/SlowQueries.vue'),
    meta: { title: 'layout.menu.slowQueries', icon: 'clock' }
  },
  {
    path: '/blocking',
    name: 'Blocking',
    component: () => import('@/views/Blocking.vue'),
    meta: { title: 'layout.menu.blocking', icon: 'blocking' }
  },
  {
    path: '/disk',
    name: 'Disk',
    component: () => import('@/views/Disk.vue'),
    meta: { title: 'layout.menu.disk', icon: 'disk' }
  },
  {
    path: '/indexes',
    name: 'Indexes',
    component: () => import('@/views/Indexes.vue'),
    meta: { title: 'layout.menu.indexes', icon: 'indexes' }
  },
  {
    path: '/alert-rules',
    name: 'AlertRules',
    component: () => import('@/views/AlertRules.vue'),
    meta: { title: 'layout.menu.alertRules', icon: 'alert_rule', requiresAdmin: true }
  },
  {
    path: '/instances',
    name: 'Instances',
    component: () => import('@/views/Instances.vue'),
    meta: { title: 'layout.menu.instances', icon: 'server', requiresAdmin: true }
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: () => import('@/views/AuditLogs.vue'),
    meta: { title: 'layout.menu.auditLogs', icon: 'audit', requiresAdmin: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: 'layout.menu.settings', icon: 'settings', requiresAdmin: true }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { title: 'layout.menu.report', icon: 'report' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: { title: 'layout.menu.users', icon: 'users', requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: 'profile.title', hideInMenu: true }
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('@/views/Help.vue'),
    meta: { title: 'layout.menu.help', icon: 'help' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  // 系统初始化检查（除 /setup 本身外均检测）
  if (to.path !== '/setup') {
    try {
      const now = Date.now()
      if (setupStatusCache && now - setupStatusCacheTime < CACHE_TTL) {
        if (!setupStatusCache.initialized) {
          return next({ path: '/setup' })
        }
      } else {
        const status = await getSetupStatus()
        setupStatusCache = status
        setupStatusCacheTime = now
        if (!status.initialized) {
          return next({ path: '/setup' })
        }
      }
    } catch {
      // 如果请求失败，继续正常导航
    }
  }

  const isPublic = to.meta?.public
  const authed = authStore.isAuthenticated.value

  if (!isPublic && !authed) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (to.meta?.requiresAdmin && !authStore.isAdmin.value) {
    return next({ path: '/dashboard' })
  }

  if (to.path === '/login' && authed) {
    return next({ path: '/dashboard' })
  }

  next()
})

export default router
