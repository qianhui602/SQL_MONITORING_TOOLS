<template>
  <div class="blocking">
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="toolbar-title">阻塞进程</span>
        <select v-model="selectedInstance" class="instance-select">
          <option value="">全部实例</option>
          <option v-for="item in instances" :key="item.id" :value="item">{{ item.name }} ({{ item.host }}:{{ item.port }})</option>
        </select>
        <span class="blocking-count" v-if="list.length > 0">共 {{ list.length }} 个阻塞链</span>
      </div>
      <div class="toolbar-right">
        <span class="auto-refresh-hint" v-if="autoRefreshEnabled">
          <span class="refresh-dot"></span>
          每30秒自动刷新
        </span>
        <button class="btn-primary" @click="onManualRefresh" :disabled="refreshing">
          {{ refreshing ? '刷新中...' : '刷新' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="M8 12h8"></path>
        </svg>
      </div>
      <p class="empty-text">当前无阻塞进程</p>
      <p class="empty-hint">系统运行正常，没有检测到阻塞链</p>
    </div>

    <div v-else class="chain-list">
      <div
        v-for="(chain, index) in list"
        :key="chain.id || index"
        class="chain-card"
      >
        <div class="chain-header">
          <span class="chain-number">#{{ index + 1 }}</span>
          <span class="chain-database" v-if="chain.database_name">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
            {{ chain.database_name }}
          </span>
          <span class="chain-time" v-if="chain.collected_at">
            {{ formatDateTime(chain.collected_at, { second: true }) }}
          </span>
        </div>

        <div class="chain-body">
          <!-- 阻塞者 (Blocker) -->
          <div class="session-card blocker">
            <div class="session-label">
              <span class="status-tag tag-blocker">阻塞者</span>
              <span class="session-spid">SPID: {{ chain.blocking_spid }}</span>
            </div>
            <div class="session-details">
              <div class="session-detail">
                <span class="detail-label">等待类型</span>
                <span class="detail-value">{{ chain.blocking_wait_type || '-' }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">等待时间</span>
                <span class="detail-value">{{ formatWaitTime(chain.blocking_wait_time) }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">主机名</span>
                <span class="detail-value">{{ chain.blocking_host_name || '-' }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">登录名</span>
                <span class="detail-value">{{ chain.blocking_login_name || '-' }}</span>
              </div>
            </div>
            <div class="session-sql" v-if="chain.blocking_sql">
              <span class="sql-label">SQL:</span>
              <pre class="sql-preview">{{ truncateText(chain.blocking_sql, 150) }}</pre>
            </div>
          </div>

          <!-- 阻塞箭头 -->
          <div class="block-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5222d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <polyline points="19 12 12 19 5 12"></polyline>
            </svg>
            <span class="block-arrow-text">阻塞</span>
          </div>

          <!-- 被阻塞者 (Blocked) -->
          <div class="session-card blocked">
            <div class="session-label">
              <span class="status-tag tag-blocked">被阻塞</span>
              <span class="session-spid">SPID: {{ chain.blocked_spid }}</span>
            </div>
            <div class="session-details">
              <div class="session-detail">
                <span class="detail-label">等待类型</span>
                <span class="detail-value">{{ chain.wait_type || '-' }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">等待时间</span>
                <span class="detail-value">{{ formatWaitTime(chain.wait_time) }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">主机名</span>
                <span class="detail-value">{{ chain.host_name || '-' }}</span>
              </div>
              <div class="session-detail">
                <span class="detail-label">登录名</span>
                <span class="detail-value">{{ chain.login_name || '-' }}</span>
              </div>
            </div>
            <div class="session-sql" v-if="chain.blocked_sql">
              <span class="sql-label">SQL:</span>
              <pre class="sql-preview">{{ truncateText(chain.blocked_sql, 150) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { getBlockingRealtime } from '@/api'
import { formatDateTime } from '@/utils/datetime'
import { useInstanceFilter } from '@/composables/useInstanceFilter'

const { instances, selectedInstance, loadingInstances, getServerAddress } = useInstanceFilter()

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const autoRefreshEnabled = ref(true)
let autoRefreshTimer = null

async function fetchData() {
  try {
    const params = {}
    const serverAddress = getServerAddress()
    if (serverAddress) params.server_address = serverAddress
    const data = await getBlockingRealtime(params)
    list.value = data?.items || data || []
  } catch (e) {
    console.error('获取阻塞进程数据失败', e)
  }
}

async function onManualRefresh() {
  refreshing.value = true
  await fetchData()
  refreshing.value = false
}

function formatWaitTime(ms) {
  if (ms === null || ms === undefined) return '-'
  const num = Number(ms)
  if (num < 1000) return `${num} ms`
  const seconds = Math.floor(num / 1000)
  if (seconds < 60) return `${seconds} 秒`
  const minutes = Math.floor(seconds / 60)
  const remainSec = seconds % 60
  if (minutes < 60) return `${minutes} 分 ${remainSec} 秒`
  const hours = Math.floor(minutes / 60)
  const remainMin = minutes % 60
  return `${hours} 小时 ${remainMin} 分`
}

function truncateText(text, maxLen) {
  if (!text) return '-'
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

function startAutoRefresh() {
  stopAutoRefresh()
  autoRefreshEnabled.value = true
  autoRefreshTimer = setInterval(() => {
    fetchData()
  }, 30000)
}

function stopAutoRefresh() {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
  autoRefreshEnabled.value = false
}

watch(selectedInstance, () => {
  fetchData()
})

onMounted(async () => {
  loading.value = true
  await fetchData()
  loading.value = false
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.blocking {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #333);
}

.blocking-count {
  font-size: 13px;
  color: var(--text-muted, #999);
  background: var(--bg-primary, #f5f6fa);
  padding: 2px 10px;
  border-radius: 10px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auto-refresh-hint {
  font-size: 12px;
  color: #52c41a;
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #52c41a;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.btn-primary {
  height: 32px;
  padding: 0 16px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-primary:disabled {
  background: #91d5ff;
  cursor: not-allowed;
}

.instance-select {
  height: 32px;
  min-width: 160px;
  padding: 0 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  background: #fff;
}

.instance-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: var(--text-muted, #999);
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color, #e8e8e8);
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.empty-icon {
  color: #52c41a;
  margin-bottom: 8px;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary, #333);
  margin: 0;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-muted, #999);
  margin: 4px 0 0 0;
}

/* Chain List */
.chain-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chain-card {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.chain-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-primary, #fafafa);
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.chain-number {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted, #999);
  background: var(--bg-card, #fff);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-color, #e8e8e8);
}

.chain-database {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary, #666);
  font-weight: 500;
}

.chain-database svg {
  flex-shrink: 0;
}

.chain-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted, #999);
}

.chain-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-card {
  padding: 14px;
  border-radius: 6px;
  border: 1px solid var(--border-color, #f0f0f0);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-card.blocker {
  background: #fff1f0;
  border-color: #ffa39e;
}

.session-card.blocked {
  background: #fff7e6;
  border-color: #ffd591;
}

.session-label {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.tag-blocker {
  background: #f5222d;
  color: #fff;
}

.tag-blocked {
  background: #fa8c16;
  color: #fff;
}

.session-spid {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #333);
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

.session-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 6px 16px;
}

.session-detail {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted, #999);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary, #333);
  font-weight: 500;
}

.session-sql {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sql-label {
  font-size: 11px;
  color: var(--text-muted, #999);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.sql-preview {
  margin: 0;
  background: rgba(0, 0, 0, 0.04);
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--text-primary, #333);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 60px;
  overflow: hidden;
}

.block-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 4px 0;
}

.block-arrow svg {
  flex-shrink: 0;
}

.block-arrow-text {
  font-size: 12px;
  color: #f5222d;
  font-weight: 500;
}

/* Dark theme overrides */
[data-theme='dark'] .session-card.blocker {
  background: rgba(245, 34, 45, 0.1);
  border-color: rgba(245, 34, 45, 0.4);
}

[data-theme='dark'] .session-card.blocked {
  background: rgba(250, 140, 22, 0.1);
  border-color: rgba(250, 140, 22, 0.4);
}

[data-theme='dark'] .sql-preview {
  background: rgba(255, 255, 255, 0.06);
}
</style>
