<template>
  <div class="deadlocks">
    <div class="toolbar">
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
            <th class="col-expand"></th>
            <th>发生时间</th>
            <th>受害会话 ID</th>
            <th>SQL Server 地址</th>
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
              <td>{{ formatDateTime(row.occur_at, { second: true }) }}</td>
              <td>
                <span :class="{ 'victim-tag': true }">{{ row.victim_session_id }}</span>
              </td>
              <td>{{ row.server_address }}</td>
            </tr>
            <tr v-if="expandedId === row.id" class="detail-row">
              <td colspan="4">
                <div class="detail-content">
                  <div class="detail-section">
                    <h4 class="detail-title">关联 SQL 语句</h4>
                    <div v-if="detailData?.sql_statements?.length">
                      <pre
                        v-for="(sql, idx) in detailData.sql_statements"
                        :key="idx"
                        class="sql-block"
                      >{{ sql }}</pre>
                    </div>
                    <p v-else class="no-data">无</p>
                  </div>

                  <div class="detail-section">
            <h4 class="detail-title">涉及对象</h4>
            <div v-if="detailData?.involved_objects?.length">
              <span
                v-for="(obj, idx) in detailData.involved_objects"
                :key="idx"
                class="object-tag"
              >{{ obj }}</span>
            </div>
            <p v-else class="no-data">无</p>
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4 class="detail-title">DeepSeek AI 分析</h4>
              <button
                class="btn-analyze"
                :disabled="analyzing"
                @click.stop="onAnalyze(row)"
              >
                <span v-if="analyzing" class="analyze-spinner"></span>
                {{ analyzing ? '分析中...' : 'AI 分析' }}
              </button>
            </div>
            <div
              v-if="detailData?.analysis_result"
              class="analysis-panel"
              v-html="renderAnalysis(detailData.analysis_result)"
            ></div>
            <p
              v-else-if="detailData && !detailData.analysis_result"
              class="no-data"
            >点击「AI 分析」按钮调用 DeepSeek 大模型分析死锁原因</p>
          </div>

                  <div class="detail-section">
                    <div
                      class="section-header collapsible"
                      @click.stop="xmlExpanded = !xmlExpanded"
                    >
                      <h4 class="detail-title">原始死锁 XML</h4>
                      <span class="collapse-icon">{{ xmlExpanded ? '▼' : '▶' }}</span>
                    </div>
                    <template v-if="xmlExpanded">
                      <pre
                        v-if="detailData?.deadlock_xml"
                        class="xml-block"
                      >{{ detailData.deadlock_xml }}</pre>
                      <p v-else class="no-data">无</p>
                    </template>
                  </div>
                </div>
              </td>
            </tr>
          </template>
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
import { getDeadlocks, getDeadlockDetail, analyzeDeadlock } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const startTime = ref('')
const endTime = ref('')
const expandedId = ref(null)
const detailData = ref(null)
const analyzing = ref(false)
const xmlExpanded = ref(false)

function renderAnalysis(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

async function fetchList() {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (startTime.value) params.start_time = startTime.value
    if (endTime.value) params.end_time = endTime.value

    const data = await getDeadlocks(params)
    list.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('获取死锁列表失败', e)
  }
}

function onSearch() {
  page.value = 1
  expandedId.value = null
  detailData.value = null
  fetchList()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  expandedId.value = null
  detailData.value = null
  fetchList()
}

function onPageSizeChange() {
  page.value = 1
  expandedId.value = null
  detailData.value = null
  fetchList()
}

async function toggleExpand(row) {
  if (expandedId.value === row.id) {
    expandedId.value = null
    detailData.value = null
    return
  }
  expandedId.value = row.id
  xmlExpanded.value = false
  try {
    const data = await getDeadlockDetail(row.id)
    detailData.value = data
  } catch (e) {
    console.error('获取死锁详情失败', e)
    detailData.value = null
  }
}

async function onAnalyze(row) {
  if (analyzing.value) return
  analyzing.value = true
  try {
    const result = await analyzeDeadlock(row.id)
    if (detailData.value) {
      detailData.value.analysis_result = result.analysis
    }
  } catch (e) {
    console.error('AI 分析失败', e)
  } finally {
    analyzing.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.deadlocks {
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

.col-expand {
  width: 40px;
  text-align: center;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
}

.data-row {
  cursor: pointer;
  transition: background 0.15s;
}

.data-row:hover {
  background: #e6f7ff;
}

.data-row.expanded {
  background: #f0f5ff;
}

.expand-icon {
  font-size: 11px;
  color: #999;
  user-select: none;
}

.victim-tag {
  display: inline-block;
  background: #fff1f0;
  color: #cf1322;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}

.detail-row td {
  padding: 0;
  background: #fafafa;
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
  color: #333;
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
}

.object-tag {
  display: inline-block;
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
  margin-bottom: 4px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-header.collapsible {
  cursor: pointer;
  user-select: none;
}

.section-header.collapsible:hover {
  opacity: 0.8;
}

.collapse-icon {
  font-size: 11px;
  color: #999;
}

.btn-analyze {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 14px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  background: linear-gradient(135deg, #4338ca, #4f46e5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.btn-analyze:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.analyze-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.analysis-panel {
  background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
  border: 1px solid #e0e7ff;
  border-radius: 8px;
  padding: 16px 20px;
  font-size: 13px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.analysis-panel :deep(strong) {
  color: #4f46e5;
  font-weight: 600;
}

.xml-block {
  background: #f5f5f5;
  color: #333;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
  border: 1px solid #e8e8e8;
}

.no-data {
  color: #999;
  font-size: 13px;
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
