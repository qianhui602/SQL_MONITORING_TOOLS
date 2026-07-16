<template>
  <div class="dashboard">
    <div class="stat-grid">
      <div
        v-for="(card, idx) in statCardOrder"
        :key="card.key"
        class="stat-card"
        :class="['stat-' + card.key, { 'drag-over': dragOverIndex === idx }]"
        :draggable="true"
        @click="$router.push(card.route)"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent="onDragOver($event, idx)"
        @dragleave="onDragLeave"
        @drop="onDrop($event, idx)"
        @dragend="onDragEnd"
      >
        <div class="stat-drag-handle" @click.stop :title="t('dashboard.dragSort')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/></svg>
        </div>
        <div class="stat-icon-wrapper" :class="'icon-' + card.key">
          <svg v-html="card.icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value" :style="card.valueStyle || {}">{{ card.value }}</div>
        </div>
      </div>
    </div>

    <!-- 数据库连接状态概览 -->
    <div class="db-status-section" v-if="instances.length > 0">
      <div class="db-status-header">
        <div class="db-status-title-wrapper">
          <div class="db-status-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <ellipse cx="12" cy="5" rx="9" ry="3"/>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
          </div>
          <span class="db-status-title">{{ t('dashboard.dbStatus') }}</span>
        </div>
        <span class="db-status-summary" :class="allInstancesOnline ? 'status-badge status-badge-online' : 'status-badge status-badge-offline'">
          {{ instancesOnline }} / {{ instances.length }} {{ t('common.online') }}
        </span>
      </div>
      <div class="db-status-list">
        <div v-for="inst in instances" :key="inst.id" class="db-status-item" @click="$router.push('/instances')"
             :title="inst.is_active && !inst.is_connected ? (inst.connection_error || t('common.connectError')) : ''">
          <div class="db-item-left">
            <span :class="['status-dot-sm', inst.is_active ? (inst.is_connected ? 'dot-online dot-pulse' : 'dot-offline') : 'dot-disabled']"></span>
            <div class="db-item-info">
              <span class="db-instance-name">{{ inst.name }}</span>
              <span class="db-instance-address">{{ inst.host }}:{{ inst.port }}</span>
            </div>
          </div>
          <span class="db-instance-status" :class="inst.is_active ? (inst.is_connected ? 'status-tag status-tag-online' : 'status-tag status-tag-offline') : 'status-tag status-tag-disabled'">
            {{ inst.is_active ? (inst.is_connected ? t('common.online') : t('common.offline')) : t('common.disabledStatus') }}
          </span>
        </div>
      </div>
    </div>

    <!-- loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>{{ t('common.loading') }}</span>
    </div>

    <div class="chart-toolbar">
      <div class="chart-toolbar-left">
        <!-- 实例选择 -->
        <select v-model="selectedInstance" @change="fetchData" class="instance-select" :disabled="loadingInstances">
          <option value="">{{ t('dashboard.allInstances') }}</option>
          <option v-for="inst in instances" :key="inst.id" :value="`${inst.name}(${inst.host}:${inst.port})`">
            {{ inst.name }} ({{ inst.host }}:{{ inst.port }})
          </option>
        </select>
        <span class="chart-toolbar-label">{{ t('dashboard.timeRange') }}：</span>
        <div class="range-tabs">
          <button
            v-for="opt in rangeOptions"
            :key="opt.value"
            :class="['range-tab', { active: timeRange === opt.value }]"
            @click="onTimeRangeChange(opt.value)"
          >{{ opt.label }}</button>
        </div>
        <span class="chart-toolbar-divider"></span>
        <span class="chart-toolbar-label">{{ t('dashboard.refresh') }}：</span>
        <select v-model="refreshInterval" class="refresh-select" @change="restartTimer">
          <option v-for="opt in refreshOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <div class="chart-toolbar-right">
        <!-- 对比模式 -->
        <span class="compare-label">{{ t('dashboard.compare') }}</span>
        <label class="compare-switch">
          <input type="checkbox" v-model="compareMode" @change="onCompareModeChange">
          <span class="compare-slider"></span>
        </label>
        <select v-if="compareMode" v-model="compareRange" class="compare-select" @change="fetchData">
          <option value="yesterday">{{ t('dashboard.compareYesterday') }}</option>
          <option value="last_week">{{ t('dashboard.compareLastWeek') }}</option>
          <option value="last_month">{{ t('dashboard.compareLastMonth') }}</option>
        </select>
        <!-- 图表自定义 -->
        <div class="custom-btn-wrapper">
          <button class="custom-btn" @click="showCustomPanel = !showCustomPanel">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            {{ t('dashboard.customize') }}
          </button>
          <div v-if="showCustomPanel" class="custom-panel" @click.stop>
            <div class="custom-panel-title">{{ t('dashboard.statCardsTitle') }}</div>
            <label v-for="item in statCardVisibilityOptions" :key="item.key" class="custom-checkbox">
              <input type="checkbox" v-model="visibleStatCards[item.key]" @change="saveStatCardVisibility">
              <span>{{ item.label }}</span>
            </label>
            <div class="custom-panel-divider"></div>
            <div class="custom-panel-title">{{ t('dashboard.chartsTitle') }}</div>
            <label v-for="item in chartVisibilityOptions" :key="item.key" class="custom-checkbox">
              <input type="checkbox" v-model="visibleCharts[item.key]">
              <span>{{ item.label }}</span>
            </label>
          </div>
        </div>
        <div class="custom-btn-wrapper">
          <button class="custom-btn" @click="showOrderPanel = !showOrderPanel" :class="{ active: showOrderPanel }" :title="t('dashboard.customLayoutSort')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            {{ t('dashboard.sort') }}
          </button>
          <div v-if="showOrderPanel" class="custom-panel order-panel" @click.stop>
            <div class="custom-panel-title">{{ t('dashboard.chartSort') }}</div>
            <div class="order-list">
              <div v-for="(chartKey, idx) in chartOrder" :key="chartKey" class="order-item">
                <span class="order-item-label">{{ chartVisibilityOptions.find(o => o.key === chartKey)?.label || chartKey }}</span>
                <span class="order-item-actions">
                  <button class="order-arrow-btn" @click="moveChartUp(idx)" :disabled="idx === 0" :title="t('dashboard.moveUp')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
                  </button>
                  <button class="order-arrow-btn" @click="moveChartDown(idx)" :disabled="idx === chartOrder.length - 1" :title="t('dashboard.moveDown')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </span>
              </div>
            </div>
            <button class="order-reset-btn" @click="resetChartOrder">{{ t('dashboard.resetChartOrder') }}</button>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-grid">
      <div
        v-for="chartKey in chartOrder"
        :key="chartKey"
        class="chart-card"
        :class="'chart-' + chartKey"
        v-show="visibleCharts[chartKey]"
        @click="openModal(chartKey)"
      >
        <div class="chart-header">
          <div class="chart-title-bar">
            <span class="chart-color-dot" :class="'dot-' + chartKey"></span>
            <span class="chart-title">{{ chartTitleMap[chartKey] }}{{ chartTitleSuffix }}</span>
          </div>
          <span class="chart-zoom-btn" :title="t('dashboard.details')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
          </span>
        </div>
        <div :ref="(el) => { if (el) chartRefInstances[chartKey].value = el }" class="chart-container"></div>
      </div>
    </div>

    <!-- 放大模态框 -->
    <div v-if="modalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div ref="modalChartRef" class="modal-chart-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { getMetricsSummary, getHistoryMetrics, getDeadlocks, getInstances } from '@/api'
import { formatTime, formatDateTime } from '@/utils/datetime'

const { t } = useI18n()

const cpuUsage = ref(0)
const memoryUsage = ref(0)
const activeConnections = ref(0)
const cacheHitRate = ref(0)
const pageLifeExpectancy = ref(0)
const lockWaits = ref(0)
const deadlockCount = ref(0)
const latestDeadlockTime = ref('')
const diskUsage = ref(0)
const batchRequests = ref(0)

// 实例相关
const instances = ref([])
const selectedInstance = ref('')
const loadingInstances = ref(false)

// 在线实例数计算属性
const instancesOnline = computed(() => {
  return instances.value.filter(i => i.is_active && i.is_connected).length
})
const allInstancesOnline = computed(() => {
  const active = instances.value.filter(i => i.is_active)
  return active.length > 0 && active.every(i => i.is_connected)
})

const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const connChartRef = ref(null)
const ioChartRef = ref(null)
const lockChartRef = ref(null)
const batchChartRef = ref(null)
const modalChartRef = ref(null)

let cpuChart = null
let memoryChart = null
let connChart = null
let ioChart = null
let lockChart = null
let batchChart = null
let modalChart = null
let timer = null
let fetching = false
let resizeTimeout = null

const cpuTimeData = ref([])
const cpuValueData = ref([])
const memoryValueData = ref([])
const connValueData = ref([])
const ioReadData = ref([])
const ioWriteData = ref([])
const lockValueData = ref([])
const batchValueData = ref([])

// 对比数据
const compareCpuValueData = ref([])
const compareMemoryValueData = ref([])
const compareConnValueData = ref([])
const compareIoReadData = ref([])
const compareIoWriteData = ref([])
const compareLockValueData = ref([])
const compareBatchValueData = ref([])
const compareTimeData = ref([])

const cpuColor = ref('#52c41a')
const cacheColor = ref('#52c41a')
const lockColor = ref('#52c41a')
const diskColor = ref('#52c41a')

const modalVisible = ref(false)
const modalTitle = ref('')
const modalType = ref('')

const timeRange = ref('1h')
const loading = ref(false)
const compareMode = ref(false)
const compareRange = ref('yesterday')
const refreshInterval = ref(10000)
const refreshOptions = computed(() => [
  { label: t('dashboard.refreshOptions.5s'), value: 5000 },
  { label: t('dashboard.refreshOptions.10s'), value: 10000 },
  { label: t('dashboard.refreshOptions.30s'), value: 30000 },
  { label: t('dashboard.refreshOptions.60s'), value: 60000 },
  { label: t('dashboard.refreshOptions.off'), value: 0 },
])

// 获取实例列表
async function fetchInstances() {
  try {
    loadingInstances.value = true
    const data = await getInstances()
    instances.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    console.error('获取实例列表失败', e)
  } finally {
    loadingInstances.value = false
  }
}

const showCustomPanel = ref(false)
const visibleCharts = ref({
  cpu: true,
  memory: true,
  connections: true,
  io: true,
  locks: true,
  batch: true
})

const chartVisibilityOptions = computed(() => [
  { key: 'cpu', label: t('dashboard.charts.cpu') },
  { key: 'memory', label: t('dashboard.charts.memory') },
  { key: 'connections', label: t('dashboard.charts.connections') },
  { key: 'io', label: t('dashboard.charts.io') },
  { key: 'locks', label: t('dashboard.charts.locks') },
  { key: 'batch', label: t('dashboard.charts.batch') }
])

// 图表排序
const defaultChartOrder = ['cpu', 'memory', 'connections', 'io', 'locks', 'batch']
const STORAGE_KEY_CHART_ORDER = 'sql_monitor_chart_order'
function loadChartOrder() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_CHART_ORDER)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length === defaultChartOrder.length) {
        return parsed
      }
    }
  } catch (e) { /* ignore */ }
  return [...defaultChartOrder]
}
const chartOrder = ref(loadChartOrder())
const showOrderPanel = ref(false)

function saveChartOrder() {
  localStorage.setItem(STORAGE_KEY_CHART_ORDER, JSON.stringify(chartOrder.value))
}

function moveChartUp(index) {
  if (index <= 0) return
  const tmp = chartOrder.value[index]
  chartOrder.value[index] = chartOrder.value[index - 1]
  chartOrder.value[index - 1] = tmp
  saveChartOrder()
}

function moveChartDown(index) {
  if (index >= chartOrder.value.length - 1) return
  const tmp = chartOrder.value[index]
  chartOrder.value[index] = chartOrder.value[index + 1]
  chartOrder.value[index + 1] = tmp
  saveChartOrder()
}

// ---------- 指标卡片排序 ----------
const defaultStatCardOrder = ['cpu', 'memory', 'connections', 'cache', 'disk', 'batch', 'locks', 'deadlock', 'instances']
const STORAGE_KEY_STAT_ORDER = 'sql_monitor_stat_order'

const iconPaths = {
  cpu: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
  memory: '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10v.01M10 10v.01M14 10v.01M18 10v.01M6 14v.01M10 14v.01M14 14v.01M18 14v.01"/>',
  connections: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  cache: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
  disk: '<rect x="2" y="6" width="20" height="12" rx="2"/><line x1="6" y1="10" x2="6" y2="14"/><line x1="10" y1="10" x2="10" y2="14"/><line x1="14" y1="10" x2="14" y2="14"/><line x1="18" y1="10" x2="18" y2="14"/>',
  batch: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  locks: '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  deadlock: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  instances: '<rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
}

const allStatCards = computed(() => ({
  cpu:       { key: 'cpu',       label: t('dashboard.statCards.cpu'),   route: '/?focus=cpu',        icon: iconPaths.cpu },
  memory:    { key: 'memory',    label: t('dashboard.statCards.memory'),   route: '/?focus=memory',     icon: iconPaths.memory },
  connections:{ key: 'connections', label: t('dashboard.statCards.connections'),   route: '/?focus=connections', icon: iconPaths.connections },
  cache:     { key: 'cache',     label: t('dashboard.statCards.cache'),   route: '/?focus=cache',      icon: iconPaths.cache },
  disk:      { key: 'disk',      label: t('dashboard.statCards.disk'),   route: '/disk-space',        icon: iconPaths.disk },
  batch:     { key: 'batch',     label: t('dashboard.statCards.batch'),    route: '/?focus=batch',      icon: iconPaths.batch },
  locks:     { key: 'locks',     label: t('dashboard.statCards.locks'),       route: '/?focus=locks',      icon: iconPaths.locks },
  deadlock:  { key: 'deadlock',  label: t('dashboard.statCards.deadlock'),     route: '/deadlocks',         icon: iconPaths.deadlock },
  instances: { key: 'instances', label: t('dashboard.statCards.instances'),   route: '/instances',         icon: iconPaths.instances },
}))

const STORAGE_KEY_STAT_VISIBILITY = 'sql_monitor_stat_visibility'
function loadStatCardVisibility() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_STAT_VISIBILITY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) { /* ignore */ }
  const defaultVisibility = {}
  defaultStatCardOrder.forEach(key => {
    defaultVisibility[key] = true
  })
  return defaultVisibility
}

function saveStatCardVisibility() {
  localStorage.setItem(STORAGE_KEY_STAT_VISIBILITY, JSON.stringify(visibleStatCards.value))
}

const visibleStatCards = ref(loadStatCardVisibility())

const statCardVisibilityOptions = computed(() => Object.entries(allStatCards.value).map(([key, card]) => ({
  key,
  label: card.label
})))

function loadStatCardOrder() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_STAT_ORDER)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed)) {
        const validKeys = parsed.filter(key => allStatCards.value[key])
        if (validKeys.length === defaultStatCardOrder.length) {
          return validKeys
        }
      }
    }
  } catch (e) { /* ignore */ }
  return [...defaultStatCardOrder]
}

function saveStatCardOrder() {
  localStorage.setItem(STORAGE_KEY_STAT_ORDER, JSON.stringify(statCardOrderKeys.value))
}

const statCardOrderKeys = ref(loadStatCardOrder())
const dragIndex = ref(null)
const dragOverIndex = ref(null)

function buildStatCard(key) {
  const card = allStatCards.value[key]
  if (!card) return null
  const valueStyle = {}
  if (key === 'cpu')     card.value = cpuUsage.value + '%'
  else if (key === 'memory')    card.value = memoryUsage.value + ' GB'
  else if (key === 'connections') card.value = activeConnections.value
  else if (key === 'cache')     card.value = cacheHitRate.value + '%'
  else if (key === 'disk')      { card.value = diskUsage.value + '%'; valueStyle.color = diskColor.value }
  else if (key === 'batch')     card.value = batchRequests.value
  else if (key === 'locks')     { card.value = lockWaits.value; valueStyle.color = lockColor.value }
  else if (key === 'deadlock')  card.value = deadlockCount.value
  else if (key === 'instances') {
    const active = instances.value.filter(i => i.is_active)
    if (active.length === 0) {
      card.value = t('dashboard.noInstances')
      valueStyle.color = '#999'
    } else {
      card.value = `${instancesOnline.value}/${instances.value.length}`
      valueStyle.color = allInstancesOnline.value ? '#52c41a' : '#ff4d4f'
    }
  }
  return { ...card, valueStyle }
}

const statCardOrder = computed(() => {
  const validCards = statCardOrderKeys.value
    .filter(key => visibleStatCards.value[key] !== false)
    .map(buildStatCard)
    .filter(Boolean)
  return validCards
})

function onDragStart(e, idx) {
  dragIndex.value = idx
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', idx)
}
function onDragOver(e, idx) {
  dragOverIndex.value = idx
}
function onDragLeave() {
  dragOverIndex.value = null
}
function onDrop(e, idx) {
  const from = dragIndex.value
  if (from === null || from === idx) return
  const keys = [...statCardOrderKeys.value]
  const [moved] = keys.splice(from, 1)
  keys.splice(idx, 0, moved)
  statCardOrderKeys.value = keys
  saveStatCardOrder()
  dragOverIndex.value = null
}
function onDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
}

function resetChartOrder() {
  chartOrder.value = [...defaultChartOrder]
  saveChartOrder()
}

// 图表标题映射
const chartTitleMap = computed(() => ({
  cpu: t('dashboard.charts.cpu'),
  memory: t('dashboard.charts.memory'),
  connections: t('dashboard.charts.connections'),
  io: t('dashboard.charts.io'),
  locks: t('dashboard.charts.locks'),
  batch: t('dashboard.charts.batch')
}))

// 图表 ref 映射（动态渲染用函数 ref）
const chartRefInstances = {
  cpu: cpuChartRef,
  memory: memoryChartRef,
  connections: connChartRef,
  io: ioChartRef,
  locks: lockChartRef,
  batch: batchChartRef
}

const rangeOptions = computed(() => [
  { label: t('dashboard.ranges["1h"]'), value: '1h', hours: 1, refreshMs: 10000 },
  { label: t('dashboard.ranges["6h"]'), value: '6h', hours: 6, refreshMs: 30000 },
  { label: t('dashboard.ranges["24h"]'), value: '24h', hours: 24, refreshMs: 60000 },
  { label: t('dashboard.ranges["7d"]'), value: '7d', hours: 168, refreshMs: 120000 }
])

const rangeLabelMap = computed(() => ({
  '1h': `（${t('dashboard.ranges["1h"]}）`,
  '6h': `（${t('dashboard.ranges["6h"]}）`,
  '24h': `（${t('dashboard.ranges["24h"]}）`,
  '7d': `（${t('dashboard.ranges["7d"]}）`
}))
const chartTitleSuffix = computed(() => rangeLabelMap.value[timeRange.value] || '')

function updateCpuColor(val) {
  if (val > 90) cpuColor.value = '#f5222d'
  else if (val > 70) cpuColor.value = '#fa8c16'
  else cpuColor.value = '#52c41a'
}

function updateCacheColor(val) {
  if (val < 60) cacheColor.value = '#f5222d'
  else if (val < 80) cacheColor.value = '#fa8c16'
  else cacheColor.value = '#52c41a'
}

function updateLockColor(val) {
  if (val > 10) lockColor.value = '#f5222d'
  else if (val > 5) lockColor.value = '#fa8c16'
  else lockColor.value = '#52c41a'
}

function updateDiskColor(val) {
  if (val > 90) diskColor.value = '#f5222d'
  else if (val > 75) diskColor.value = '#fa8c16'
  else diskColor.value = '#52c41a'
}

function getTimeRange() {
  const opt = rangeOptions.value.find(o => o.value === timeRange.value)
  const hours = opt ? opt.hours : 1
  const now = new Date()
  const start = new Date(now.getTime() - hours * 60 * 60 * 1000)
  return { start: start.toISOString(), end: now.toISOString() }
}

function getCompareTimeRange() {
  const opt = rangeOptions.value.find(o => o.value === timeRange.value)
  const hours = opt ? opt.hours : 1
  const now = new Date()
  // 对比时段偏移
  const offsetMs = compareRange.value === 'yesterday' ? 24 * 60 * 60 * 1000
    : compareRange.value === 'last_week' ? 7 * 24 * 60 * 60 * 1000
    : 30 * 24 * 60 * 60 * 1000
  const end = new Date(now.getTime() - offsetMs)
  const start = new Date(end.getTime() - hours * 60 * 60 * 1000)
  return { start: start.toISOString(), end: end.toISOString() }
}

function getHistoryLimit() {
  // 根据时间范围调整数据量：图表宽度约 600px，约 500 个数据点即可流畅显示
  const limitMap = { '1h': 800, '6h': 1500, '24h': 2500, '7d': 3000 }
  return limitMap[timeRange.value] || 2500
}

function getRefreshInterval() {
  return refreshInterval.value
}

function createOption(title, data, timeLabels, color, unit, extraSeries = null) {
  const series = [{
    name: title,
    type: 'line',
    data: data,
    smooth: true,
    symbol: 'none',
    sampling: 'lttb',
    lineStyle: { color: color, width: 2 },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: color + '40' },
        { offset: 1, color: color + '05' }
      ])
    }
  }]
  if (extraSeries) {
    series.push({ sampling: 'lttb', ...extraSeries })
  }
  return {
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let html = params[0].axisValue + '<br/>'
        params.forEach(p => {
          html += `${p.seriesName || title}: ${p.value}${unit}<br/>`
        })
        return html
      }
    },
    legend: extraSeries ? {
      data: [title, extraSeries.name],
      top: 0,
      textStyle: { fontSize: 11 }
    } : undefined,
    grid: {
      left: 50,
      right: 20,
      top: extraSeries ? 30 : 20,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { fontSize: 10, interval: 'auto' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#e8e8e8' } }
    },
    series
  }
}

function createDualOption(title1, data1, title2, data2, timeLabels, color1, color2, unit, extraSeries1 = null, extraSeries2 = null) {
  const series = [
    {
      name: title1,
      type: 'line',
      data: data1,
      smooth: true,
      symbol: 'none',
      sampling: 'lttb',
      lineStyle: { color: color1, width: 2 }
    },
    {
      name: title2,
      type: 'line',
      data: data2,
      smooth: true,
      symbol: 'none',
      sampling: 'lttb',
      lineStyle: { color: color2, width: 2 }
    }
  ]
  if (extraSeries1) series.push({ sampling: 'lttb', ...extraSeries1 })
  if (extraSeries2) series.push({ sampling: 'lttb', ...extraSeries2 })

  const legendData = [title1, title2]
  if (extraSeries1) legendData.push(extraSeries1.name)
  if (extraSeries2) legendData.push(extraSeries2.name)

  return {
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let html = params[0].axisValue + '<br/>'
        params.forEach(p => {
          html += `${p.seriesName}: ${p.value}${unit}<br/>`
        })
        return html
      }
    },
    legend: {
      data: legendData,
      top: 0,
      textStyle: { fontSize: 11 }
    },
    grid: {
      left: 50,
      right: 20,
      top: 30,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { fontSize: 10, interval: 'auto' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#e8e8e8' } }
    },
    series
  }
}

/**
 * 构建对比系列的虚线样式
 */
function buildCompareSeries(name, data, color) {
  return {
    name: t('dashboard.previousPeriod') + ' ' + name,
    type: 'line',
    data: data,
    smooth: true,
    symbol: 'none',
    lineStyle: { color: color, width: 2, type: 'dashed' },
    itemStyle: { color: color }
  }
}

function initCpuChart() {
  if (!cpuChartRef.value) return
  cpuChart = echarts.init(cpuChartRef.value)
  cpuChart.setOption(createOption(t('dashboard.series.cpuUsage'), cpuValueData.value, cpuTimeData.value, '#1890ff', '%'))
}

function initMemoryChart() {
  if (!memoryChartRef.value) return
  memoryChart = echarts.init(memoryChartRef.value)
  memoryChart.setOption(createOption(t('dashboard.series.memoryUsage'), memoryValueData.value, cpuTimeData.value, '#52c41a', ' MB'))
}

function initConnChart() {
  if (!connChartRef.value) return
  connChart = echarts.init(connChartRef.value)
  connChart.setOption(createOption(t('dashboard.series.activeConnections'), connValueData.value, cpuTimeData.value, '#fa8c16', ''))
}

function initIoChart() {
  if (!ioChartRef.value) return
  ioChart = echarts.init(ioChartRef.value)
  ioChart.setOption(createDualOption(t('dashboard.series.ioReadLatency'), ioReadData.value, t('dashboard.series.ioWriteLatency'), ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms'))
}

function initLockChart() {
  if (!lockChartRef.value) return
  lockChart = echarts.init(lockChartRef.value)
  lockChart.setOption(createOption(t('dashboard.series.lockWaits'), lockValueData.value, cpuTimeData.value, '#f5222d', ''))
}

function initBatchChart() {
  if (!batchChartRef.value) return
  batchChart = echarts.init(batchChartRef.value)
  batchChart.setOption(createOption(t('dashboard.series.batchRequests'), batchValueData.value, cpuTimeData.value, '#722ed1', '/s'))
}

function resizeCharts() {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout)
  }
  resizeTimeout = setTimeout(() => {
    cpuChart?.resize()
    memoryChart?.resize()
    connChart?.resize()
    ioChart?.resize()
    lockChart?.resize()
    batchChart?.resize()
    modalChart?.resize()
  }, 200)
}

function formatTimeLabels(items) {
  if (timeRange.value === '1h') {
    return items.map(item => formatTime(item.collected_at))
  }
  return items.map(item => formatDateTime(item.collected_at, { second: true }))
}

function extractMetricValues(historyData, metricName) {
  const filtered = historyData.filter(m => m.metric_name === metricName)
  return filtered.length ? filtered : historyData
}

async function fetchData() {
  if (fetching) return
  fetching = true
  loading.value = true
  try {
    // 同步刷新实例连接状态
    if (instances.value.length > 0) {
      try {
        const data = await getInstances()
        instances.value = Array.isArray(data) ? data : (data.items || [])
      } catch (e) {
        console.warn('刷新实例状态失败', e)
      }
    }

    const range = getTimeRange()
    const limit = getHistoryLimit()
    const serverAddr = selectedInstance.value || undefined
    const promises = [
      getMetricsSummary({ server_address: serverAddr }),
      getHistoryMetrics({ category: 'cpu', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getHistoryMetrics({ category: 'memory', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getHistoryMetrics({ category: 'connections', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getHistoryMetrics({ category: 'io', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getHistoryMetrics({ category: 'locks', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getHistoryMetrics({ category: 'batch_requests', start_time: range.start, end_time: range.end, limit, server_address: serverAddr }),
      getDeadlocks({ page: 1, page_size: 1, server_address: serverAddr })
    ]

    // 对比模式额外请求
    if (compareMode.value) {
      const compareRange = getCompareTimeRange()
      promises.push(
        getHistoryMetrics({ category: 'cpu', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr }),
        getHistoryMetrics({ category: 'memory', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr }),
        getHistoryMetrics({ category: 'connections', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr }),
        getHistoryMetrics({ category: 'io', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr }),
        getHistoryMetrics({ category: 'locks', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr }),
        getHistoryMetrics({ category: 'batch_requests', start_time: compareRange.start, end_time: compareRange.end, limit, server_address: serverAddr })
      )
    }

    const results = await Promise.all(promises)
    const summary = results[0]
    const cpuHistory = results[1]
    const memHistory = results[2]
    const connHistory = results[3]
    const ioHistory = results[4]
    const lockHistory = results[5]
    const batchHistory = results[6]
    const deadlocksRes = results[7]

    let cmpCpuHistory, cmpMemHistory, cmpConnHistory, cmpIoHistory, cmpLockHistory, cmpBatchHistory
    if (compareMode.value) {
      cmpCpuHistory = results[8]
      cmpMemHistory = results[9]
      cmpConnHistory = results[10]
      cmpIoHistory = results[11]
      cmpLockHistory = results[12]
      cmpBatchHistory = results[13]
    }

    cpuUsage.value = summary.cpu_usage ?? 0
    const memMb = summary.sql_server_memory_mb ?? 0
    memoryUsage.value = Math.round(memMb / 1024 * 100) / 100
    activeConnections.value = summary.active_sessions ?? 0
    cacheHitRate.value = summary.buffer_cache_hit_ratio ?? 0
    diskUsage.value = summary.disk_usage_pct ?? 0
    batchRequests.value = summary.batch_requests_sec ?? 0

    updateCpuColor(cpuUsage.value)
    updateCacheColor(cacheHitRate.value)
    updateDiskColor(diskUsage.value)

    if (deadlocksRes?.total) {
      deadlockCount.value = deadlocksRes.total
    }
    if (deadlocksRes?.items?.length) {
      latestDeadlockTime.value = formatDateTime(deadlocksRes.items[0].occur_at, { second: true })
    } else {
      latestDeadlockTime.value = ''
    }

    // 处理对比时间数据（使用 CPU 对比数据的时间轴作为参考）
    if (cmpCpuHistory?.length) {
      const cmpCpuItems = extractMetricValues(cmpCpuHistory, 'cpu_usage')
      compareTimeData.value = formatTimeLabels(cmpCpuItems)
    }

    // CPU 图表
    if (cpuHistory?.length) {
      const cpuItems = extractMetricValues(cpuHistory, 'cpu_usage')
      cpuTimeData.value = formatTimeLabels(cpuItems)
      cpuValueData.value = cpuItems.map(m => m.metric_value)
      if (cpuChart) {
        const series = [{ data: cpuValueData.value }]
        if (compareMode.value && cmpCpuHistory?.length) {
          const cmpItems = extractMetricValues(cmpCpuHistory, 'cpu_usage')
          compareCpuValueData.value = cmpItems.map(m => m.metric_value)
          const cmpSeries = buildCompareSeries(t('dashboard.series.cpuUsage'), compareCpuValueData.value, '#91caff')
          cpuChart.setOption(createOption(t('dashboard.series.cpuUsage'), cpuValueData.value, cpuTimeData.value, '#1890ff', '%', cmpSeries), true)
        } else {
          cpuChart.setOption({
            xAxis: { data: cpuTimeData.value },
            series: series
          })
        }
      }
    }

    // 内存图表
    if (memHistory?.length) {
      const memItems = extractMetricValues(memHistory, 'sql_server_memory_mb')
      memoryValueData.value = memItems.map(m => m.metric_value)
      if (memoryChart) {
        const extra = compareMode.value && cmpMemHistory?.length
          ? buildCompareSeries(t('dashboard.series.memoryUsage'), extractMetricValues(cmpMemHistory, 'sql_server_memory_mb').map(m => m.metric_value), '#95de64')
          : null
        memoryChart.setOption(createOption(t('dashboard.series.memoryUsage'), memoryValueData.value, formatTimeLabels(memItems), '#52c41a', ' MB', extra), true)
      }
      const pleItems = memHistory.filter(m => m.metric_name === 'page_life_expectancy')
      if (pleItems.length) {
        pageLifeExpectancy.value = Math.round(pleItems[pleItems.length - 1].metric_value)
      }
    }

    // 连接数图表
    if (connHistory?.length) {
      const connItems = extractMetricValues(connHistory, 'active_sessions')
      connValueData.value = connItems.map(m => m.metric_value)
      if (connChart) {
        const extra = compareMode.value && cmpConnHistory?.length
          ? buildCompareSeries(t('dashboard.series.activeConnections'), extractMetricValues(cmpConnHistory, 'active_sessions').map(m => m.metric_value), '#ffc069')
          : null
        connChart.setOption(createOption(t('dashboard.series.activeConnections'), connValueData.value, formatTimeLabels(connItems), '#fa8c16', '', extra), true)
      }
    }

    // IO 图表
    if (ioHistory?.length) {
      const readItems = ioHistory.filter(m => m.metric_name === 'avg_read_latency_ms')
      const writeItems = ioHistory.filter(m => m.metric_name === 'avg_write_latency_ms')
      ioReadData.value = readItems.length ? readItems.map(m => m.metric_value) : []
      ioWriteData.value = writeItems.length ? writeItems.map(m => m.metric_value) : []
      if (ioChart) {
        let extraRead = null, extraWrite = null
        if (compareMode.value && cmpIoHistory?.length) {
          const cmpRead = extractMetricValues(cmpIoHistory, 'avg_read_latency_ms')
          const cmpWrite = extractMetricValues(cmpIoHistory, 'avg_write_latency_ms')
          if (cmpRead.length) extraRead = buildCompareSeries(t('dashboard.series.ioReadLatency'), cmpRead.map(m => m.metric_value), '#91caff')
          if (cmpWrite.length) extraWrite = buildCompareSeries(t('dashboard.series.ioWriteLatency'), cmpWrite.map(m => m.metric_value), '#95de64')
        }
        ioChart.setOption(createDualOption(t('dashboard.series.ioReadLatency'), ioReadData.value, t('dashboard.series.ioWriteLatency'), ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms', extraRead, extraWrite), true)
      }
    }

    // 锁图表
    if (lockHistory?.length) {
      const lockItems = extractMetricValues(lockHistory, 'lock_waits')
      lockValueData.value = lockItems.map(m => m.metric_value)
      lockWaits.value = Math.round(lockValueData.value[lockValueData.value.length - 1] || 0)
      updateLockColor(lockWaits.value)
      if (lockChart) {
        const extra = compareMode.value && cmpLockHistory?.length
          ? buildCompareSeries(t('dashboard.series.lockWaits'), extractMetricValues(cmpLockHistory, 'lock_waits').map(m => m.metric_value), '#ff7875')
          : null
        lockChart.setOption(createOption(t('dashboard.series.lockWaits'), lockValueData.value, formatTimeLabels(lockItems), '#f5222d', '', extra), true)
      }
    }

    // 批处理图表
    if (batchHistory?.length) {
      const batchItems = extractMetricValues(batchHistory, 'batch_requests_sec')
      batchValueData.value = batchItems.map(m => m.metric_value)
      if (batchChart) {
        const extra = compareMode.value && cmpBatchHistory?.length
          ? buildCompareSeries(t('dashboard.series.batchRequests'), extractMetricValues(cmpBatchHistory, 'batch_requests_sec').map(m => m.metric_value), '#b37feb')
          : null
        batchChart.setOption(createOption(t('dashboard.series.batchRequests'), batchValueData.value, formatTimeLabels(batchItems), '#722ed1', '/s', extra), true)
      }
    }
  } catch (e) {
    console.error('获取数据失败', e)
  } finally {
    loading.value = false
    fetching = false
  }
}

function openModal(type) {
  modalType.value = type
  const titles = {
    cpu: `${chartTitleMap.value.cpu}${chartTitleSuffix.value}`,
    memory: `${chartTitleMap.value.memory}${chartTitleSuffix.value}`,
    connections: `${chartTitleMap.value.connections}${chartTitleSuffix.value}`,
    io: `${chartTitleMap.value.io}${chartTitleSuffix.value}`,
    locks: `${chartTitleMap.value.locks}${chartTitleSuffix.value}`,
    batch: `${chartTitleMap.value.batch}${chartTitleSuffix.value}`
  }
  modalTitle.value = titles[type] || t('dashboard.chartDetail')
  modalVisible.value = true
  nextTick(() => {
    if (modalChartRef.value) {
      if (modalChart) {
        modalChart.dispose()
      }
      modalChart = echarts.init(modalChartRef.value)
      let option
      switch (type) {
        case 'cpu':
          option = createOption(t('dashboard.series.cpuUsage'), cpuValueData.value, cpuTimeData.value, '#1890ff', '%')
          break
        case 'memory':
          option = createOption(t('dashboard.series.memoryUsage'), memoryValueData.value, cpuTimeData.value, '#52c41a', ' MB')
          break
        case 'connections':
          option = createOption(t('dashboard.series.activeConnections'), connValueData.value, cpuTimeData.value, '#fa8c16', '')
          break
        case 'io':
          option = createDualOption(t('dashboard.series.ioReadLatency'), ioReadData.value, t('dashboard.series.ioWriteLatency'), ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms')
          break
        case 'locks':
          option = createOption(t('dashboard.series.lockWaits'), lockValueData.value, cpuTimeData.value, '#f5222d', '')
          break
        case 'batch':
          option = createOption(t('dashboard.series.batchRequests'), batchValueData.value, cpuTimeData.value, '#722ed1', '/s')
          break
      }
      if (option) {
        option.dataZoom = [
          {
            type: 'inside',
            start: 0,
            end: 100,
            zoomLock: false
          }
        ]
        modalChart.setOption(option, true)
      }
    }
  })
}

function closeModal() {
  modalVisible.value = false
  if (modalChart) {
    modalChart.dispose()
    modalChart = null
  }
}

watch(modalVisible, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function restartTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  const interval = getRefreshInterval()
  if (interval > 0) {
    timer = setInterval(fetchData, interval)
  }
}

function onTimeRangeChange(val) {
  timeRange.value = val
  fetchData()
  restartTimer()
}

function onCompareModeChange() {
  // 清理对比数据
  if (!compareMode.value) {
    compareCpuValueData.value = []
    compareMemoryValueData.value = []
    compareConnValueData.value = []
    compareIoReadData.value = []
    compareIoWriteData.value = []
    compareLockValueData.value = []
    compareBatchValueData.value = []
    compareTimeData.value = []
  }
  fetchData()
}

// 点击外部关闭自定义面板
function handleClickOutside(e) {
  if (showCustomPanel.value) {
    const panel = document.querySelector('.custom-panel:not(.order-panel)')
    const btn = document.querySelector('.custom-btn-wrapper:first-child .custom-btn')
    if (panel && !panel.contains(e.target) && btn && !btn.contains(e.target)) {
      showCustomPanel.value = false
    }
  }
  if (showOrderPanel.value) {
    const panel = document.querySelector('.order-panel')
    const btn = document.querySelector('.custom-btn-wrapper:last-child .custom-btn')
    if (panel && !panel.contains(e.target) && btn && !btn.contains(e.target)) {
      showOrderPanel.value = false
    }
  }
}

onMounted(async () => {
  await nextTick()
  await fetchInstances() // 获取实例列表
  initCpuChart()
  initMemoryChart()
  initConnChart()
  initIoChart()
  initLockChart()
  initBatchChart()
  window.addEventListener('resize', resizeCharts)
  document.addEventListener('click', handleClickOutside)
  await fetchData()
  restartTimer()
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  window.removeEventListener('resize', resizeCharts)
  document.removeEventListener('click', handleClickOutside)
  cpuChart?.dispose()
  memoryChart?.dispose()
  connChart?.dispose()
  ioChart?.dispose()
  lockChart?.dispose()
  batchChart?.dispose()
  modalChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
}

/* loading overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  z-index: 50;
  border-radius: 12px;
  pointer-events: none;
}

[data-theme='dark'] .loading-overlay {
  background: rgba(0, 0, 0, 0.4);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-color, #e8e8e8);
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.6, 0.2, 0.4, 0.8) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  width: 100%;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  cursor: pointer;
  min-height: 80px;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-cpu::before       { background: linear-gradient(90deg, #1890ff, #69c0ff); }
.stat-memory::before    { background: linear-gradient(90deg, #52c41a, #95de64); }
.stat-connections::before { background: linear-gradient(90deg, #13c2c2, #5cdbd3); }
.stat-cache::before     { background: linear-gradient(90deg, #722ed1, #b37feb); }
.stat-disk::before      { background: linear-gradient(90deg, #fa8c16, #ffc069); }
.stat-batch::before     { background: linear-gradient(90deg, #eb2f96, #ff85c0); }
.stat-locks::before     { background: linear-gradient(90deg, #f5222d, #ff7875); }
.stat-deadlock::before  { background: linear-gradient(90deg, #faad14, #ffd666); }
.stat-instances::before { background: linear-gradient(90deg, #1890ff, #69c0ff); }

.stat-card.drag-over {
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.4), 0 8px 24px rgba(24, 144, 255, 0.15);
  transform: translateY(-3px) scale(1.02);
}

.stat-card[draggable="true"] {
  cursor: grab;
}
.stat-card[draggable="true"]:active {
  cursor: grabbing;
  opacity: 0.8;
  transform: scale(0.98);
}

.stat-drag-handle {
  color: #bfbfbf;
  cursor: grab;
  flex-shrink: 0;
  padding: 2px;
  border-radius: 3px;
  opacity: 0;
  transition: opacity 0.2s;
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
}
.stat-card:hover .stat-drag-handle {
  opacity: 1;
}
.stat-drag-handle:active {
  cursor: grabbing;
  color: #1890ff;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.1);
}

.icon-cpu       { background: linear-gradient(135deg, #e6f7ff, #bae7ff); color: #1890ff; }
.icon-memory    { background: linear-gradient(135deg, #f6ffed, #d9f7be); color: #52c41a; }
.icon-connections { background: linear-gradient(135deg, #e6fffb, #b5f5ec); color: #13c2c2; }
.icon-cache     { background: linear-gradient(135deg, #f9f0ff, #efdbff); color: #722ed1; }
.icon-disk      { background: linear-gradient(135deg, #fff7e6, #ffe7ba); color: #fa8c16; }
.icon-batch     { background: linear-gradient(135deg, #fff0f6, #ffd6e8); color: #eb2f96; }
.icon-locks     { background: linear-gradient(135deg, #fff1f0, #ffccc7); color: #f5222d; }
.icon-deadlock  { background: linear-gradient(135deg, #fffbe6, #fff1b8); color: #faad14; }
.icon-instances { background: linear-gradient(135deg, #e6f7ff, #bae7ff); color: #1890ff; }

[data-theme='dark'] .icon-cpu       { background: linear-gradient(135deg, #112a45, #15395b); color: #40a9ff; }
[data-theme='dark'] .icon-memory    { background: linear-gradient(135deg, #1a2f1a, #234223); color: #73d13d; }
[data-theme='dark'] .icon-connections { background: linear-gradient(135deg, #0a2a2a, #134242); color: #36cfc9; }
[data-theme='dark'] .icon-cache     { background: linear-gradient(135deg, #241533, #392052); color: #9254de; }
[data-theme='dark'] .icon-disk      { background: linear-gradient(135deg, #2b1d0a, #402a0f); color: #ffa940; }
[data-theme='dark'] .icon-batch     { background: linear-gradient(135deg, #2b1320, #401e30); color: #f759ab; }
[data-theme='dark'] .icon-locks     { background: linear-gradient(135deg, #2b1310, #401e1a); color: #ff4d4f; }
[data-theme='dark'] .icon-deadlock  { background: linear-gradient(135deg, #2b2210, #403315); color: #ffc53d; }
[data-theme='dark'] .icon-instances { background: linear-gradient(135deg, #112a45, #15395b); color: #40a9ff; }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.5px;
}

.stat-mini-chart {
  display: none;
}

.stat-deadlock .stat-value.deadlock-val {
  font-variant-numeric: tabular-nums;
}

/* 数据库状态概览 */
.db-status-section {
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.db-status-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.db-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(24, 144, 255, 0.02), transparent);
}

.db-status-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.db-status-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  color: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

[data-theme='dark'] .db-status-icon {
  background: linear-gradient(135deg, #112a45, #15395b);
  color: #40a9ff;
}

.db-status-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.5;
}

.status-badge-online {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.status-badge-offline {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

[data-theme='dark'] .status-badge-online {
  background: rgba(82, 196, 26, 0.15);
}

[data-theme='dark'] .status-badge-offline {
  background: rgba(255, 77, 79, 0.15);
}

.db-status-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.db-status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1 1 300px;
  border-right: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  position: relative;
}

.db-status-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  border-radius: 0 3px 3px 0;
  transition: height 0.2s;
}

.db-status-item:hover {
  background: var(--bg-primary);
}

.db-status-item:hover::before {
  height: 60%;
  background: #1890ff;
}

.db-item-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.db-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.db-instance-name {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  font-size: 13px;
}

.db-instance-address {
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.status-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-tag-online {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.status-tag-offline {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.status-tag-disabled {
  background: rgba(153, 153, 153, 0.1);
  color: #999;
}

[data-theme='dark'] .status-tag-online {
  background: rgba(82, 196, 26, 0.15);
}

[data-theme='dark'] .status-tag-offline {
  background: rgba(255, 77, 79, 0.15);
}

[data-theme='dark'] .status-tag-disabled {
  background: rgba(153, 153, 153, 0.15);
}

.status-dot-sm {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
  position: relative;
}

.dot-online {
  background: #52c41a;
  box-shadow: 0 0 6px rgba(82, 196, 26, 0.6);
}

.dot-pulse::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #52c41a;
  transform: translate(-50%, -50%);
  animation: pulse-ring 1.5s ease-out infinite;
}

@keyframes pulse-ring {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

.dot-offline {
  background: #ff4d4f;
  box-shadow: 0 0 6px rgba(255, 77, 79, 0.6);
}

.dot-disabled {
  background: #d9d9d9;
  box-shadow: none;
}

[data-theme='dark'] .dot-disabled {
  background: #555;
}

.chart-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.chart-card {
  flex: 1 1 calc(50% - 8px);
  min-width: 400px;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 18px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--chart-accent, #1890ff), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.chart-card:hover::before {
  opacity: 1;
}

.chart-cpu::before       { --chart-accent: #1890ff; }
.chart-memory::before    { --chart-accent: #52c41a; }
.chart-connections::before { --chart-accent: #fa8c16; }
.chart-io::before        { --chart-accent: #13c2c2; }
.chart-locks::before     { --chart-accent: #f5222d; }
.chart-batch::before     { --chart-accent: #722ed1; }

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.chart-title-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-cpu       { background: #1890ff; box-shadow: 0 0 6px rgba(24, 144, 255, 0.5); }
.dot-memory    { background: #52c41a; box-shadow: 0 0 6px rgba(82, 196, 26, 0.5); }
.dot-connections { background: #fa8c16; box-shadow: 0 0 6px rgba(250, 140, 22, 0.5); }
.dot-io        { background: #13c2c2; box-shadow: 0 0 6px rgba(19, 194, 194, 0.5); }
.dot-locks     { background: #f5222d; box-shadow: 0 0 6px rgba(245, 34, 45, 0.5); }
.dot-batch     { background: #722ed1; box-shadow: 0 0 6px rgba(114, 46, 209, 0.5); }

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-zoom-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  opacity: 0.6;
  transition: all 0.2s;
}

.chart-card:hover .chart-zoom-btn {
  opacity: 1;
  background: var(--bg-primary);
  color: #1890ff;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-toolbar {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 14px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-toolbar-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.range-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-primary);
  padding: 3px;
  border-radius: 8px;
}

.range-tab {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.range-tab:hover {
  color: var(--text-primary);
}

.range-tab.active {
  color: #1890ff;
  background: var(--bg-card);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.chart-toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  margin: 0 4px;
}

.refresh-select {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-card);
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  height: 32px;
}
.refresh-select:hover {
  border-color: #1890ff;
}
.refresh-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

/* 对比模式 */
.compare-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.compare-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}
.compare-switch input { opacity: 0; width: 0; height: 0; }
.compare-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
}
.compare-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
input:checked + .compare-slider { background-color: #1890ff; }
input:checked + .compare-slider:before { transform: translateX(20px); }

.compare-select {
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
}
.compare-select:hover {
  border-color: #1890ff;
}
.compare-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

/* 图表自定义 */
.custom-btn-wrapper {
  position: relative;
}

.custom-btn {
  height: 32px;
  padding: 0 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-weight: 500;
}
.custom-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}
.custom-btn.active {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.08);
}

.custom-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  min-width: 220px;
  background: var(--bg-card);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid var(--border-color);
  padding: 14px;
  z-index: 20;
  animation: panelFadeIn 0.2s ease-out;
}

@keyframes panelFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.custom-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.custom-panel-divider {
  height: 1px;
  background: var(--border-color);
  margin: 12px 0;
}

.custom-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 8px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
}
.custom-checkbox:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}
.custom-checkbox input {
  cursor: pointer;
  accent-color: #1890ff;
}

/* 排序面板 */
.order-panel {
  min-width: 280px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 320px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all 0.15s;
}
.order-item:hover {
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}

.order-item-label {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.order-item-actions {
  display: flex;
  gap: 4px;
}

.order-arrow-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  padding: 0;
}
.order-arrow-btn:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.06);
}
.order-arrow-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.order-arrow-btn svg {
  display: block;
}

.order-reset-btn {
  width: 100%;
  margin-top: 12px;
  padding: 8px 12px;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}
.order-reset-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}

/* 实例选择下拉框 */
.instance-select {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
  min-width: 200px;
  cursor: pointer;
}
.instance-select:hover {
  border-color: #1890ff;
}
.instance-select:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}
.instance-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(4px);
  animation: modalFadeIn 0.2s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: var(--bg-card);
  border-radius: 12px;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  animation: modalSlideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-chart-container {
  flex: 1;
  padding: 20px 24px 24px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 900px) {
  .chart-card {
    flex: 1 1 100%;
    min-width: 0;
  }

  .stat-card {
    min-width: 140px;
  }

  .stat-icon-wrapper {
    width: 42px;
    height: 42px;
    border-radius: 10px;
  }

  .modal-content {
    width: 95%;
    height: 70vh;
  }

  .chart-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .db-status-item {
    flex: 1 1 100%;
  }
}

@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-grid {
    display: flex;
    flex-direction: column;
  }

  .chart-card {
    flex: 1 1 100%;
    min-width: 0;
  }

  .stat-value {
    font-size: 20px;
  }

  .db-status-header {
    padding: 14px 16px;
  }

  .db-status-item {
    padding: 12px 16px;
  }
}

@media (max-width: 640px) {
  .stat-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 14px 16px;
    min-height: 70px;
  }

  .stat-icon-wrapper {
    width: 38px;
    height: 38px;
    border-radius: 8px;
  }

  .stat-icon-wrapper svg {
    width: 18px;
    height: 18px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 12px;
  }

  .chart-toolbar {
    padding: 12px 16px;
  }

  .chart-toolbar-left,
  .chart-toolbar-right {
    flex-wrap: wrap;
    width: 100%;
  }

  .range-tabs {
    flex-wrap: wrap;
  }

  .instance-select {
    min-width: 140px;
    flex: 1;
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    min-width: 0;
    padding: 16px;
  }

  .stat-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 10px;
  }

  .stat-value {
    font-size: 22px;
  }

  .chart-toolbar-left {
    flex-wrap: wrap;
  }

  .db-status-item {
    flex: 1 1 100%;
  }
}
</style>
