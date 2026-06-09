<template>
  <div class="indexes-page">
    <div class="page-header">
      <h2>索引分析</h2>
      <div class="toolbar-group">
        <label class="toolbar-label">实例</label>
        <select v-model="selectedInstance" class="instance-select">
          <option value="">全部实例</option>
          <option v-for="item in instances" :key="item.id" :value="item">{{ item.name }} ({{ item.host }}:{{ item.port }})</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">数据库</label>
        <input
          v-model="databaseFilter"
          class="input"
          placeholder="输入数据库名筛选"
          @keyup.enter="onFilterChange"
        />
      </div>
    </div>

    <div class="tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'missing' }]"
        @click="switchTab('missing')"
      >
        缺失索引
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'fragmentation' }]"
        @click="switchTab('fragmentation')"
      >
        索引碎片
      </button>
    </div>

    <!-- 缺失索引 -->
    <div v-if="activeTab === 'missing'" class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>数据库名</th>
            <th>架构名</th>
            <th>表名</th>
            <th>相等列</th>
            <th>包含列</th>
            <th>预估影响(%)</th>
            <th>用户查找次数</th>
            <th>用户扫描次数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="missingLoading">
            <td colspan="8" class="empty-cell">加载中...</td>
          </tr>
          <tr v-else-if="missingList.length === 0">
            <td colspan="8" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-for="row in missingList" :key="row.id">
            <td>{{ row.database_name }}</td>
            <td>{{ row.schema_name }}</td>
            <td>{{ row.table_name }}</td>
            <td class="col-break">{{ row.equality_columns || '-' }}</td>
            <td class="col-break">{{ row.included_columns || '-' }}</td>
            <td>
              <span class="impact-badge">{{ row.avg_user_impact?.toFixed(1) }}</span>
            </td>
            <td>{{ row.user_seeks }}</td>
            <td>{{ row.user_scans }}</td>
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        <span class="page-info">共 {{ missingTotal }} 条</span>
        <div class="page-actions">
          <button :disabled="missingPage <= 1" @click="goMissingPage(missingPage - 1)">上一页</button>
          <span class="page-text">第 {{ missingPage }} / {{ missingTotalPages }} 页</span>
          <button :disabled="missingPage >= missingTotalPages" @click="goMissingPage(missingPage + 1)">下一页</button>
        </div>
        <div class="page-size-control">
          <label>每页</label>
          <select v-model.number="missingPageSize" @change="onMissingPageSizeChange">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
          <label>条</label>
        </div>
      </div>
    </div>

    <!-- 索引碎片 -->
    <div v-if="activeTab === 'fragmentation'" class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>数据库名</th>
            <th>架构名</th>
            <th>表名</th>
            <th>索引名</th>
            <th>碎片率(%)</th>
            <th>页数</th>
            <th>索引类型</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="fragLoading">
            <td colspan="7" class="empty-cell">加载中...</td>
          </tr>
          <tr v-else-if="fragList.length === 0">
            <td colspan="7" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-for="row in fragList" :key="row.id">
            <td>{{ row.database_name }}</td>
            <td>{{ row.schema_name }}</td>
            <td>{{ row.table_name }}</td>
            <td class="col-break">{{ row.index_name }}</td>
            <td>
              <span class="frag-badge" :class="fragClass(row.fragment_percentage)">
                {{ row.fragment_percentage?.toFixed(2) }}
              </span>
            </td>
            <td>{{ row.page_count }}</td>
            <td>{{ row.index_type }}</td>
          </tr>
        </tbody>
      </table>
      <div class="pagination">
        <span class="page-info">共 {{ fragTotal }} 条</span>
        <div class="page-actions">
          <button :disabled="fragPage <= 1" @click="goFragPage(fragPage - 1)">上一页</button>
          <span class="page-text">第 {{ fragPage }} / {{ fragTotalPages }} 页</span>
          <button :disabled="fragPage >= fragTotalPages" @click="goFragPage(fragPage + 1)">下一页</button>
        </div>
        <div class="page-size-control">
          <label>每页</label>
          <select v-model.number="fragPageSize" @change="onFragPageSizeChange">
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
import { ref, computed, watch, onMounted } from 'vue'
import { getMissingIndexes, getIndexFragmentation } from '@/api'
import { useInstanceFilter } from '@/composables/useInstanceFilter'

const { instances, selectedInstance, loadingInstances, getServerAddress } = useInstanceFilter()

const activeTab = ref('missing')
const databaseFilter = ref('')

// 缺失索引
const missingList = ref([])
const missingTotal = ref(0)
const missingPage = ref(1)
const missingPageSize = ref(10)
const missingLoading = ref(false)

const missingTotalPages = computed(() => Math.max(1, Math.ceil(missingTotal.value / missingPageSize.value)))

// 索引碎片
const fragList = ref([])
const fragTotal = ref(0)
const fragPage = ref(1)
const fragPageSize = ref(10)
const fragLoading = ref(false)

const fragTotalPages = computed(() => Math.max(1, Math.ceil(fragTotal.value / fragPageSize.value)))

function fragClass(pct) {
  if (pct == null) return ''
  if (pct > 30) return 'frag-danger'
  if (pct > 5) return 'frag-warning'
  return 'frag-good'
}

function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'missing' && missingList.value.length === 0) fetchMissing()
  if (tab === 'fragmentation' && fragList.value.length === 0) fetchFrag()
}

async function fetchMissing() {
  missingLoading.value = true
  try {
    const params = {
      page: missingPage.value,
      page_size: missingPageSize.value
    }
    if (databaseFilter.value) params.database_name = databaseFilter.value
    const serverAddress = getServerAddress()
    if (serverAddress) params.server_address = serverAddress
    const data = await getMissingIndexes(params)
    missingList.value = data.items || []
    missingTotal.value = data.total || 0
  } catch (e) {
    console.error('获取缺失索引失败', e)
  } finally {
    missingLoading.value = false
  }
}

async function fetchFrag() {
  fragLoading.value = true
  try {
    const params = {
      page: fragPage.value,
      page_size: fragPageSize.value
    }
    if (databaseFilter.value) params.database_name = databaseFilter.value
    const serverAddress = getServerAddress()
    if (serverAddress) params.server_address = serverAddress
    const data = await getIndexFragmentation(params)
    fragList.value = data.items || []
    fragTotal.value = data.total || 0
  } catch (e) {
    console.error('获取索引碎片失败', e)
  } finally {
    fragLoading.value = false
  }
}

function onFilterChange() {
  missingPage.value = 1
  fragPage.value = 1
  if (activeTab.value === 'missing') fetchMissing()
  else fetchFrag()
}

function goMissingPage(p) {
  if (p < 1 || p > missingTotalPages.value) return
  missingPage.value = p
  fetchMissing()
}

function onMissingPageSizeChange() {
  missingPage.value = 1
  fetchMissing()
}

function goFragPage(p) {
  if (p < 1 || p > fragTotalPages.value) return
  fragPage.value = p
  fetchFrag()
}

function onFragPageSizeChange() {
  fragPage.value = 1
  fetchFrag()
}

watch(selectedInstance, () => {
  onFilterChange()
})

onMounted(() => {
  if (activeTab.value === 'missing') fetchMissing()
  else fetchFrag()
})
</script>

<style scoped>
.indexes-page {
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

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-label {
  font-size: 13px;
  color: #8c8c8c;
  white-space: nowrap;
}

.input {
  height: 32px;
  padding: 0 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  width: 200px;
}

.input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
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

.tabs {
  display: flex;
  gap: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  background: #fafafa;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  color: #1890ff;
  background: #f0f7ff;
}

.tab-btn.active {
  color: #1890ff;
  background: #fff;
  border-bottom-color: #1890ff;
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
  padding: 10px 14px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
}

.data-table tbody tr:hover {
  background: #f9fbff;
}

.col-break {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: #999;
}

.impact-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  background: #e6f7ff;
  color: #096dd9;
}

.frag-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.frag-danger {
  background: #fff1f0;
  color: #cf1322;
}

.frag-warning {
  background: #fff7e6;
  color: #d46b08;
}

.frag-good {
  background: #f6ffed;
  color: #52c41a;
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
