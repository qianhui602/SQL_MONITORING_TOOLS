<template>
  <div class="audit-logs-page">
    <div class="page-header">
      <h2>审计日志</h2>
    </div>

    <div class="toolbar">
      <div class="toolbar-group">
        <label class="toolbar-label">用户名</label>
        <input v-model="filter.username" class="input" placeholder="输入用户名筛选" @keyup.enter="onSearch" />
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">操作类型</label>
        <select v-model="filter.action" class="select-input" @change="onSearch">
          <option value="">全部</option>
          <option value="CREATE">CREATE</option>
          <option value="UPDATE">UPDATE</option>
          <option value="DELETE">DELETE</option>
          <option value="LOGIN">LOGIN</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">开始时间</label>
        <input type="datetime-local" v-model="filter.startTime" class="input" />
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">结束时间</label>
        <input type="datetime-local" v-model="filter.endTime" class="input" />
      </div>
      <button class="btn-primary" @click="onSearch">查询</button>
    </div>

    <div v-if="error" class="error-state">
      <div class="error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f5222d" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      </div>
      <p class="error-text">{{ error }}</p>
      <button class="btn-primary" @click="fetchList">重试</button>
    </div>

    <div class="card" v-else>
      <table class="data-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>操作</th>
            <th>资源</th>
            <th>详情</th>
            <th>IP 地址</th>
            <th>操作时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="empty-cell">加载中...</td>
          </tr>
          <tr v-else-if="list.length === 0">
            <td colspan="6" class="empty-cell">暂无审计日志</td>
          </tr>
          <tr v-for="row in list" :key="row.id">
            <td>{{ row.username }}</td>
            <td>
              <span class="action-tag" :class="actionClass(row.action)">{{ row.action }}</span>
            </td>
            <td>{{ row.resource || '-' }}</td>
            <td class="detail-cell" :title="row.detail">{{ row.detail || '-' }}</td>
            <td>{{ row.ip_address || '-' }}</td>
            <td>{{ formatDate(row.created_at) }}</td>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { getAuditLogs } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const error = ref(null)

const filter = reactive({
  username: '',
  action: '',
  startTime: '',
  endTime: ''
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

function actionClass(action) {
  const map = {
    CREATE: 'act-create',
    UPDATE: 'act-update',
    DELETE: 'act-delete',
    LOGIN: 'act-login'
  }
  return map[action] || ''
}

function formatDate(d) {
  return formatDateTime(d, { second: true })
}

async function fetchList() {
  loading.value = true
  error.value = null
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filter.username) params.username = filter.username
    if (filter.action) params.action = filter.action
    if (filter.startTime) params.start_time = filter.startTime
    if (filter.endTime) params.end_time = filter.endTime

    const data = await getAuditLogs(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取审计日志失败', e)
    error.value = '获取审计日志失败，请稍后重试'
    list.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
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

onMounted(fetchList)
</script>

<style scoped>
.audit-logs-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #001529;
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

.card {
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
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
}

.data-table tbody tr:hover {
  background: #f9fbff;
}

.detail-cell {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.act-create {
  background: #e6f4ff;
  color: #1677ff;
  border: 1px solid #91caff;
}

.act-update {
  background: #fff7e6;
  color: #d46b08;
  border: 1px solid #ffd591;
}

.act-delete {
  background: #fff1f0;
  color: #cf1322;
  border: 1px solid #ffa39e;
}

.act-login {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
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
