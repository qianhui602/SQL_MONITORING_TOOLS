import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const TOKEN_KEY = 'sql_monitor_token'
const USER_KEY = 'sql_monitor_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setStoredUser(user) {
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
  else localStorage.removeItem(USER_KEY)
}

export function clearAuth() {
  setToken(null)
  setStoredUser(null)
}

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response && error.response.status === 401) {
      clearAuth()
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ===== 认证相关 =====
export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

export function getMe() {
  return request.get('/auth/me')
}

export function changePassword(oldPassword, newPassword) {
  return request.post('/auth/change_password', {
    old_password: oldPassword,
    new_password: newPassword
  })
}

// ===== 用户管理 =====
export function listUsers() {
  return request.get('/users')
}

export function createUser(payload) {
  return request.post('/users', payload)
}

export function updateUser(id, payload) {
  return request.put(`/users/${id}`, payload)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

// ===== 监控相关 =====
export function getRealtimeMetrics() {
  return request.get('/metrics/realtime')
}

export function getHistoryMetrics(params) {
  return request.get('/metrics/history', { params })
}

export function getMetricsSummary(params) {
  return request.get('/metrics/summary', { params })
}

export function getDeadlocks(params) {
  return request.get('/deadlocks', { params })
}

export function getDeadlockDetail(id) {
  return request.get(`/deadlocks/${id}`)
}

export function analyzeDeadlock(id) {
  return request.post(`/deadlocks/${id}/analyze`)
}

export function getAlerts(params) {
  return request.get('/alerts', { params })
}

export function acknowledgeAlert(id) {
  return request.put(`/alerts/${id}/acknowledge`)
}

export function getConfigs() {
  return request.get('/config')
}

export function getConfig(key) {
  return request.get(`/config/${key}`)
}

export function updateConfig(key, value) {
  return request.put(`/config/${key}`, { config_value: value })
}

// ===== 慢查询 =====
export function getSlowQueries(params) { return request.get('/slow-queries', { params }) }
export function getSlowQueryStats(params) { return request.get('/slow-queries/stats', { params }) }

// ===== 阻塞分析 =====
export function getBlockingRealtime() { return request.get('/blocking/realtime') }
export function getBlockingHistory(params) { return request.get('/blocking/history', { params }) }

// ===== 磁盘监控 =====
export function getDiskSpace(params) { return request.get('/disk/space', { params }) }
export function getDiskHistory(params) { return request.get('/disk/history', { params }) }

// ===== 索引分析 =====
export function getMissingIndexes(params) { return request.get('/indexes/missing', { params }) }
export function getIndexFragmentation(params) { return request.get('/indexes/fragmentation', { params }) }

// ===== 实例管理 =====
export function getInstances() { return request.get('/instances') }
export function createInstance(data) { return request.post('/instances', data) }
export function updateInstance(id, data) { return request.put(`/instances/${id}`, data) }
export function deleteInstance(id) { return request.delete(`/instances/${id}`) }
export function testInstanceConnection(id) { return request.post(`/instances/${id}/test`) }

// ===== 告警规则 =====
export function getAlertRules() { return request.get('/alert-rules') }
export function createAlertRule(data) { return request.post('/alert-rules', data) }
export function updateAlertRule(id, data) { return request.put(`/alert-rules/${id}`, data) }
export function deleteAlertRule(id) { return request.delete(`/alert-rules/${id}`) }
export function toggleAlertRule(id) { return request.put(`/alert-rules/${id}/toggle`) }

// ===== 审计日志 =====
export function getAuditLogs(params) { return request.get('/audit-logs', { params }) }

// ===== 数据导出 =====
export function exportMetrics(params) { return request.get('/export/metrics', { params, responseType: 'blob' }) }
export function exportAlerts(params) { return request.get('/export/alerts', { params, responseType: 'blob' }) }
export function exportDeadlocks(params) { return request.get('/export/deadlocks', { params, responseType: 'blob' }) }
export function exportSlowQueries(params) { return request.get('/export/slow-queries', { params, responseType: 'blob' }) }

// ===== 通知管理 =====
export function getNotifications(limit = 20) { return request.get('/notifications', { params: { limit } }) }
export function markNotificationRead(id) { return request.put(`/notifications/${id}/read`) }
export function deleteNotification(id) { return request.delete(`/notifications/${id}`) }
export function markAllNotificationsRead() { return request.post('/notifications/read-all') }

// ===== 报告功能 =====
export function getReportSummary(params) { return request.get('/reports/summary', { params }) }
export function saveReport(data) { return request.post('/reports/save', data) }
export function getReportHistory() { return request.get('/reports/history') }
export function deleteReportHistory(id) { return request.delete(`/reports/history/${id}`) }

// ===== 在线升级 =====
export function checkUpgrade() { return request.get('/upgrade/check') }
export function getUpgradeGitStatus() { return request.get('/upgrade/git-status') }
export function applyUpgrade() { return request.post('/upgrade/apply') }
export function uploadZipUpgrade(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upgrade/upload-zip', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export default request
