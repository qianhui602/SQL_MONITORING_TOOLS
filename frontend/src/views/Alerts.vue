<template>
  <div class="alerts">
    <div class="toolbar">
      <div class="toolbar-group">
        <label class="toolbar-label">严重级别</label>
        <select v-model="severityFilter" class="select-input" @change="onFilterChange">
          <option value="">全部</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">开始时间</label>
        <input type="datetime-local" v-model="startTime" class="input" />
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">结束时间</label>
        <input type="datetime-local" v-model="endTime" class="input" />
      </div>
      <button class="btn-primary" @click="onSearch">查询</button>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>告警类型</th>
            <th>严重级别</th>
            <th>消息</th>
            <th>触发时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in list" :key="row.id">
            <td>{{ row.alert_type }}</td>
            <td>
              <span class="severity-tag" :class="severityClass(row.severity)">{{ row.severity }}</span>
            </td>
            <td class="msg-cell">{{ row.message }}</td>
            <td>{{ formatDateTime(row.triggered_at, { second: true }) }}</td>
          </tr>
          <tr v-if="list.length === 0">
            <td colspan="4" class="empty-cell">暂无数据</td>
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
import { getAlerts } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const severityFilter = ref('')
const startTime = ref('')
const endTime = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function severityClass(severity) {
  const map = {
    critical: 'sev-critical',
    high: 'sev-high',
    medium: 'sev-medium',
    low: 'sev-low'
  }
  return map[severity] || ''
}

async function fetchList() {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (severityFilter.value) params.severity = severityFilter.value
    if (startTime.value) params.start_time = startTime.value
    if (endTime.value) params.end_time = endTime.value

    const data = await getAlerts(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取告警列表失败', e)
  }
}

function onFilterChange() {
  page.value = 1
  fetchList()
}

function onSearch() {
  page.value = 1
  fetchList()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchList()
}

function onPageSizeChange() {
  page.value = 1
  fetchList()
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.alerts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-end;
  background: #fff;
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
  color: #8c8c8c;
}

.select-input {
  height: 32px;
  min-width: 130px;
  padding: 0 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  background: #fff;
}

.select-input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.input {
  height: 32px;
  padding: 0 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}

.input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
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
}

.btn-primary:hover {
  background: #40a9ff;
}

.table-card {
  background: #fff;
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
  background: #fafafa;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
}

.data-table tr.acknowledged td {
  opacity: 0.5;
}

.msg-cell {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.severity-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.sev-critical {
  background: #fff1f0;
  color: #cf1322;
}

.sev-high {
  background: #fff7e6;
  color: #d46b08;
}

.sev-medium {
  background: #fffbe6;
  color: #d4b106;
}

.sev-low {
  background: #e6f7ff;
  color: #096dd9;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  font-size: 13px;
}

.page-info {
  color: #666;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-actions button {
  height: 28px;
  padding: 0 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}

.page-actions button:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}

.page-actions button:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

.page-text {
  color: #333;
}

.page-size-control {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.page-size-control select {
  height: 28px;
  padding: 0 4px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}
</style>
