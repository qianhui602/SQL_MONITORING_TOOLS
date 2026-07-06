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
    meta: { title: '登录', public: true, layout: false }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { title: '找回密码', public: true, layout: false }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPassword.vue'),
    meta: { title: '重置密码', public: true, layout: false }
  },
  {
    path: '/setup',
    name: 'Setup',
    component: () => import('@/views/Setup.vue'),
    meta: { title: '系统安装', public: true, layout: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '总览', icon: 'dashboard' }
  },
  {
    path: '/trends',
    name: 'Trends',
    component: () => import('@/views/Trends.vue'),
    meta: { title: '性能趋势', icon: 'trending_up' }
  },
  {
    path: '/deadlocks',
    name: 'Deadlocks',
    component: () => import('@/views/Deadlocks.vue'),
    meta: { title: '死锁监控', icon: 'lock' }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('@/views/Alerts.vue'),
    meta: { title: '告警管理', icon: 'notifications' }
  },
  {
    path: '/slow-queries',
    name: 'SlowQueries',
    component: () => import('@/views/SlowQueries.vue'),
    meta: { title: '慢查询分析', icon: 'clock' }
  },
  {
    path: '/blocking',
    name: 'Blocking',
    component: () => import('@/views/Blocking.vue'),
    meta: { title: '阻塞进程', icon: 'blocking' }
  },
  {
    path: '/disk',
    name: 'Disk',
    component: () => import('@/views/Disk.vue'),
    meta: { title: '磁盘空间', icon: 'disk' }
  },
  {
    path: '/indexes',
    name: 'Indexes',
    component: () => import('@/views/Indexes.vue'),
    meta: { title: '索引分析', icon: 'indexes' }
  },
  {
    path: '/alert-rules',
    name: 'AlertRules',
    component: () => import('@/views/AlertRules.vue'),
    meta: { title: '告警规则', icon: 'alert_rule', requiresAdmin: true }
  },
  {
    path: '/instances',
    name: 'Instances',
    component: () => import('@/views/Instances.vue'),
    meta: { title: '实例管理', icon: 'server', requiresAdmin: true }
  },
  {
    path: '/audit-logs',
    name: 'AuditLogs',
    component: () => import('@/views/AuditLogs.vue'),
    meta: { title: '审计日志', icon: 'audit', requiresAdmin: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '系统设置', icon: 'settings', requiresAdmin: true }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { title: '系统报告', icon: 'report' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: { title: '用户管理', icon: 'users', requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人设置', hideInMenu: true }
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
