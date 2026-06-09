<template>
  <div class="slow-queries">
    <div class="toolbar">
      <div class="toolbar-group">
        <label class="toolbar-label">实例</label>
        <select v-model="selectedInstance" class="instance-select">
          <option value="">全部实例</option>
          <option v-for="item in instances" :key="item.id" :value="item">{{ item.name }} ({{ item.host }}:{{ item.port }})</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">时间范围</label>
        <div class="time-range-group">
          <button
            v-for="opt in timeRangeOptions"
            :key="opt.value"
            class="time-btn"
            :class="{ active: timeRange === opt.value }"
            @click="onTimeRangeChange(opt.value)"
          >{{ opt.label }}</button>
        </div>
      </div>
      <button class="btn-primary" @click="onSearch">查询</button>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-expand"></th>
            <th>查询文本</th>
            <th>执行次数</th>
            <th>总CPU时间(ms)</th>
            <th>总逻辑读</th>
            <th>平均耗时(ms)</th>
            <th>最后执行时间</th>
            <th>采集时间</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="row in list" :key="row.id">
            <tr
              class="data-row"
              :class="{ expanded: expandedId === row.id }"
              @click="toggleExpand(row)"
            >
              <td class="col-expand">
                <span class="expand-icon">{{ expandedId === row.id ? '▼' : '▶' }}</span>
              </td>
              <td class="col-query" :title="row.query_text">{{ truncateText(row.query_text, 80) }}</td>
              <td>{{ row.execution_count }}</td>
              <td>{{ formatNumber(row.total_cpu_time_ms) }}</td>
              <td>{{ formatNumber(row.total_logical_reads) }}</td>
              <td>{{ formatNumber(row.avg_duration_ms) }}</td>
              <td>{{ formatDateTime(row.last_execution_time, { second: true }) }}</td>
              <td>{{ formatDateTime(row.collected_at, { second: true }) }}</td>
            </tr>
            <tr v-if="expandedId === row.id" class="detail-row">
              <td colspan="8">
                <div class="detail-content">
                  <div class="detail-section">
                    <h4 class="detail-title">完整 SQL 语句</h4>
                    <pre class="sql-block">{{ expandedQuery }}</pre>
                  </div>
                  <div class="detail-meta">
                    <div class="meta-item">
                      <span class="meta-label">执行次数</span>
                      <span class="meta-value">{{ row.execution_count }}</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">总CPU时间</span>
                      <span class="meta-value">{{ formatNumber(row.total_cpu_time_ms) }} ms</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">总逻辑读</span>
                      <span class="meta-value">{{ formatNumber(row.total_logical_reads) }}</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">平均耗时</span>
                      <span class="meta-value">{{ formatNumber(row.avg_duration_ms) }} ms</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">最小耗时</span>
                      <span class="meta-value">{{ formatNumber(row.min_duration_ms) }} ms</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">最大耗时</span>
                      <span class="meta-value">{{ formatNumber(row.max_duration_ms) }} ms</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">最后执行时间</span>
                      <span class="meta-value">{{ formatDateTime(row.last_execution_time, { second: true }) }}</span>
                    </div>
                    <div class="meta-item">
                      <span class="meta-label">数据库</span>
                      <span class="meta-value">{{ row.database_name || '-' }}</span>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="list.length === 0">
            <td colspan="8" class="empty-cell">暂无数据</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <span class="page-info">共 {{ total }} 条</span>
        <div class="page-actions">
          <button :disabled="page <= 1" @click="goPage(page - 1)">上一页</button>
          <span class="page-text">第 {{ page }} / {{ totalPages }} 页</span>
          <button :disabled="page >= totalPages" @click="goPage(page + 1)">下一页</button>
        </div>
        <div class="page-size-control">
          <label>每页</label>
          <select v-model.number="pageSize" @change="onPageSizeChange">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
          <label>条</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSlowQueries } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const timeRangeOptions = [
  { label: '最近1小时', value: '1h' },
  { label: '最近6小时', value: '6h' },
  { label: '最近24小时', value: '24h' },
  { label: '最近7天', value: '7d' }
]

const timeRange = ref('1h')
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const expandedId = ref(null)
const expandedQuery = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function getTimeRange() {
  const rangeMap = { '1h': 1, '6h': 6, '24h': 24, '7d': 168 }
  const hours = rangeMap[timeRange.value] || 1
  const now = new Date()
  const start = new Date(now.getTime() - hours * 60 * 60 * 1000)
  return { start_time: start.toISOString(), end_time: now.toISOString() }
}

async function fetchList() {
  try {
    const range = getTimeRange()
    const params = {
      page: page.value,
      page_size: pageSize.value,
      start_time: range.start_time,
      end_time: range.end_time
    }
    const serverAddress = getServerAddress()
    if (serverAddress) params.server_address = serverAddress
    const data = await getSlowQueries(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取慢查询列表失败', e)
  }
}

function onTimeRangeChange(value) {
  timeRange.value = value
  page.value = 1
  expandedId.value = null
  expandedQuery.value = ''
  fetchList()
}

function onSearch() {
  page.value = 1
  expandedId.value = null
  expandedQuery.value = ''
  fetchList()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  expandedId.value = null
  expandedQuery.value = ''
  fetchList()
}

function onPageSizeChange() {
  page.value = 1
  expandedId.value = null
  expandedQuery.value = ''
  fetchList()
}

function toggleExpand(row) {
  if (expandedId.value === row.id) {
    expandedId.value = null
    expandedQuery.value = ''
    return
  }
  expandedId.value = row.id
  expandedQuery.value = row.query_text || ''
}

function truncateText(text, maxLen) {
  if (!text) return '-'
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

function formatNumber(num) {
  if (num === null || num === undefined) return '-'
  return Number(num).toLocaleString()
}

watch(selectedInstance, () => {
  page.value = 1
  expandedId.value = null
  expandedQuery.value = ''
  fetchList()
})

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.slow-queries {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.toolbar-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toolbar-label {
  font-size: 13px;
  color: var(--text-muted, #8c8c8c);
  font-weight: 500;
}

.time-range-group {
  display: flex;
  gap: 4px;
  background: var(--bg-primary, #f5f6fa);
  border-radius: 6px;
  padding: 2px;
}

.time-btn {
  height: 30px;
  padding: 0 14px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-secondary, #666);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.time-btn:hover {
  color: var(--text-primary, #333);
}

.time-btn.active {
  background: var(--bg-card, #fff);
  color: #1890ff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 500;
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

.btn-primary:hover {
  background: #40a9ff;
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

.col-expand {
  width: 40px;
  text-align: center;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  color: var(--text-secondary, #555);
}

.col-query {
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
}

.data-row {
  cursor: pointer;
  transition: background 0.15s;
}

.data-row:hover {
  background: var(--row-hover, #e6f7ff);
}

.data-row.expanded {
  background: var(--row-expanded, #f0f5ff);
}

.expand-icon {
  font-size: 11px;
  color: var(--text-muted, #999);
  user-select: none;
}

.detail-row td {
  padding: 0;
  background: var(--bg-primary, #fafafa);
}

.detail-content {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin: 0;
}

.sql-block {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 12px;
  color: var(--text-muted, #999);
}

.meta-value {
  font-size: 13px;
  color: var(--text-primary, #333);
  font-weight: 500;
}

.no-data {
  color: var(--text-muted, #999);
  font-size: 13px;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: var(--text-muted, #999);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color, #f0f0f0);
  font-size: 13px;
}

.page-info {
  color: var(--text-secondary, #666);
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-actions button {
  height: 28px;
  padding: 0 12px;
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 4px;
  background: var(--bg-card, #fff);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-primary, #333);
  transition: all 0.2s;
}

.page-actions button:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}

.page-actions button:disabled {
  color: var(--text-muted, #d9d9d9);
  cursor: not-allowed;
}

.page-text {
  color: var(--text-primary, #333);
}

.page-size-control {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary, #666);
}

.page-size-control select {
  height: 28px;
  padding: 0 4px;
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
}
</style>
