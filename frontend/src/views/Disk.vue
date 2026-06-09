<template>
  <div class="disk">
    <div class="toolbar">
      <div class="toolbar-left">
        <span class="toolbar-title">磁盘空间监控</span>
        <span class="collect-time" v-if="collectedAt">
          采集时间: {{ formatDateTime(collectedAt, { second: true }) }}
        </span>
      </div>
      <button class="btn-primary" @click="onRefresh" :disabled="refreshing">
        {{ refreshing ? '刷新中...' : '刷新' }}
      </button>
    </div>

    <!-- 总览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <span class="overview-label">数据库总数</span>
        <span class="overview-value">{{ list.length }}</span>
      </div>
      <div class="overview-card">
        <span class="overview-label">总数据文件(MB)</span>
        <span class="overview-value">{{ formatNumber(totalDataFileMb) }}</span>
      </div>
      <div class="overview-card">
        <span class="overview-label">总日志文件(MB)</span>
        <span class="overview-value">{{ formatNumber(totalLogFileMb) }}</span>
      </div>
      <div class="overview-card">
        <span class="overview-label">总大小(MB)</span>
        <span class="overview-value">{{ formatNumber(totalSizeMb) }}</span>
      </div>
      <div class="overview-card">
        <span class="overview-label">总已用(MB)</span>
        <span class="overview-value">{{ formatNumber(totalUsedMb) }}</span>
      </div>
      <div class="overview-card">
        <span class="overview-label">总体使用率</span>
        <span class="overview-value" :style="{ color: totalUsageColor }">{{ formatPercent(overallUsage) }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="list.length === 0" class="empty-state">
      <p class="empty-text">暂无数据</p>
    </div>

    <template v-else>
      <!-- 进度条列表 -->
      <div class="progress-card">
        <h3 class="card-title">各数据库空间使用率</h3>
        <div class="progress-list">
          <div v-for="db in list" :key="db.database_name" class="progress-item">
            <div class="progress-header">
              <span class="progress-db-name">{{ db.database_name }}</span>
              <span class="progress-value" :style="{ color: usageColor(db.usage_pct) }">
                {{ formatPercent(db.usage_pct) }}
              </span>
            </div>
            <div class="progress-bar-track">
              <div
                class="progress-bar-fill"
                :style="{ width: clampPercent(db.usage_pct), background: usageColor(db.usage_pct) }"
              ></div>
            </div>
            <div class="progress-detail">
              <span>已用: {{ formatNumber(db.used_mb) }} MB</span>
              <span>可用: {{ formatNumber(db.free_mb) }} MB</span>
              <span>总计: {{ formatNumber(db.total_size_mb) }} MB</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 表格 -->
      <div class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>数据库名</th>
              <th>数据文件(MB)</th>
              <th>日志文件(MB)</th>
              <th>总大小(MB)</th>
              <th>已用(MB)</th>
              <th>可用(MB)</th>
              <th>使用率(%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="db in list" :key="db.database_name">
              <td class="col-name">{{ db.database_name }}</td>
              <td>{{ formatNumber(db.data_file_mb) }}</td>
              <td>{{ formatNumber(db.log_file_mb) }}</td>
              <td>{{ formatNumber(db.total_size_mb) }}</td>
              <td>{{ formatNumber(db.used_mb) }}</td>
              <td>{{ formatNumber(db.free_mb) }}</td>
              <td>
                <span class="usage-tag" :style="{ background: usageBgColor(db.usage_pct), color: usageColor(db.usage_pct) }">
                  {{ formatPercent(db.usage_pct) }}
                </span>
              </td>
            </tr>
            <tr v-if="list.length === 0">
              <td colspan="7" class="empty-cell">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getDiskSpace } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const collectedAt = ref(null)

const totalDataFileMb = computed(() =>
  list.value.reduce((sum, db) => sum + (Number(db.data_file_mb) || 0), 0)
)

const totalLogFileMb = computed(() =>
  list.value.reduce((sum, db) => sum + (Number(db.log_file_mb) || 0), 0)
)

const totalSizeMb = computed(() =>
  list.value.reduce((sum, db) => sum + (Number(db.total_size_mb) || 0), 0)
)

const totalUsedMb = computed(() =>
  list.value.reduce((sum, db) => sum + (Number(db.used_mb) || 0), 0)
)

const overallUsage = computed(() => {
  const total = totalSizeMb.value
  const used = totalUsedMb.value
  if (!total || total === 0) return 0
  return (used / total) * 100
})

const totalUsageColor = computed(() => usageColor(overallUsage.value))

async function fetchData() {
  try {
    const data = await getDiskSpace()
    const items = data?.items || data || []
    list.value = Array.isArray(items) ? items : []
    collectedAt.value = data?.collected_at || null
  } catch (e) {
    console.error('获取磁盘空间数据失败', e)
  }
}

async function onRefresh() {
  refreshing.value = true
  await fetchData()
  refreshing.value = false
}

function formatNumber(num) {
  if (num === null || num === undefined) return '-'
  return Number(num).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatPercent(val) {
  if (val === null || val === undefined) return '-'
  return Number(val).toFixed(1) + '%'
}

function clampPercent(val) {
  if (!val && val !== 0) return '0%'
  return Math.min(100, Math.max(0, Number(val))) + '%'
}

function usageColor(val) {
  const num = Number(val)
  if (num >= 80) return '#f5222d'
  if (num >= 60) return '#fa8c16'
  return '#52c41a'
}

function usageBgColor(val) {
  const num = Number(val)
  if (num >= 80) return '#fff1f0'
  if (num >= 60) return '#fff7e6'
  return '#f6ffed'
}

onMounted(async () => {
  loading.value = true
  await fetchData()
  loading.value = false
})
</script>

<style scoped>
.disk {
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

.collect-time {
  font-size: 12px;
  color: var(--text-muted, #999);
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

/* Overview Cards */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}

.overview-card {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overview-label {
  font-size: 12px;
  color: var(--text-muted, #999);
  font-weight: 500;
}

.overview-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary, #333);
  line-height: 1.2;
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
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.empty-text {
  font-size: 14px;
  color: var(--text-muted, #999);
  margin: 0;
}

/* Progress Card */
.progress-card {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin: 0 0 16px 0;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-db-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.progress-value {
  font-size: 13px;
  font-weight: 600;
}

.progress-bar-track {
  width: 100%;
  height: 8px;
  background: var(--bg-primary, #f0f0f0);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.progress-detail {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--text-muted, #999);
}

/* Table Card */
.table-card {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: var(--bg-primary, #fafafa);
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary, #333);
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  white-space: nowrap;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  color: var(--text-secondary, #555);
}

.col-name {
  font-weight: 500;
  color: var(--text-primary, #333);
}

.usage-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: var(--text-muted, #999);
}

/* Dark theme overrides */
[data-theme='dark'] .progress-bar-track {
  background: rgba(255, 255, 255, 0.08);
}

[data-theme='dark'] .overview-card {
  border: 1px solid var(--border-color, #333355);
}
</style>
