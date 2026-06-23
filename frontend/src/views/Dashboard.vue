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
        <div class="stat-drag-handle" @click.stop title="拖拽排序">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/></svg>
        </div>
        <div class="stat-info">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value" :style="card.valueStyle || {}">{{ card.value }}</div>
        </div>
      </div>
    </div>

    <!-- loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>数据加载中…</span>
    </div>

    <div class="chart-toolbar">
      <div class="chart-toolbar-left">
        <!-- 实例选择 -->
        <select v-model="selectedInstance" @change="fetchData" class="instance-select" :disabled="loadingInstances">
          <option value="">所有实例</option>
          <option v-for="inst in instances" :key="inst.id" :value="`${inst.name}(${inst.host}:${inst.port})`">
            {{ inst.name }} ({{ inst.host }}:{{ inst.port }})
          </option>
        </select>
        <span class="chart-toolbar-label">时间范围：</span>
        <div class="range-tabs">
          <button
            v-for="opt in rangeOptions"
            :key="opt.value"
            :class="['range-tab', { active: timeRange === opt.value }]"
            @click="onTimeRangeChange(opt.value)"
          >{{ opt.label }}</button>
        </div>
        <span class="chart-toolbar-divider"></span>
        <span class="chart-toolbar-label">刷新：</span>
        <select v-model="refreshInterval" class="refresh-select" @change="restartTimer">
          <option v-for="opt in refreshOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>
      <div class="chart-toolbar-right">
        <!-- 对比模式 -->
        <span class="compare-label">对比</span>
        <label class="compare-switch">
          <input type="checkbox" v-model="compareMode" @change="onCompareModeChange">
          <span class="compare-slider"></span>
        </label>
        <select v-if="compareMode" v-model="compareRange" class="compare-select" @change="fetchData">
          <option value="yesterday">昨天此时</option>
          <option value="last_week">上周此时</option>
          <option value="last_month">上月此时</option>
        </select>
        <!-- 图表自定义 -->
        <div class="custom-btn-wrapper">
          <button class="custom-btn" @click="showCustomPanel = !showCustomPanel">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            自定义
          </button>
          <div v-if="showCustomPanel" class="custom-panel" @click.stop>
            <div class="custom-panel-title">选择显示的图表</div>
            <label v-for="item in chartVisibilityOptions" :key="item.key" class="custom-checkbox">
              <input type="checkbox" v-model="visibleCharts[item.key]">
              <span>{{ item.label }}</span>
            </label>
          </div>
        </div>
        <div class="custom-btn-wrapper">
          <button class="custom-btn" @click="showOrderPanel = !showOrderPanel" :class="{ active: showOrderPanel }" title="自定义布局排序">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
            排序
          </button>
          <div v-if="showOrderPanel" class="custom-panel order-panel" @click.stop>
            <div class="custom-panel-title">图表排序（点击箭头调整位置）</div>
            <div class="order-list">
              <div v-for="(chartKey, idx) in chartOrder" :key="chartKey" class="order-item">
                <span class="order-item-label">{{ chartVisibilityOptions.find(o => o.key === chartKey)?.label || chartKey }}</span>
                <span class="order-item-actions">
                  <button class="order-arrow-btn" @click="moveChartUp(idx)" :disabled="idx === 0" title="上移">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
                  </button>
                  <button class="order-arrow-btn" @click="moveChartDown(idx)" :disabled="idx === chartOrder.length - 1" title="下移">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                  </button>
                </span>
              </div>
            </div>
            <button class="order-reset-btn" @click="resetChartOrder">恢复默认排序</button>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-grid">
      <div
        v-for="chartKey in chartOrder"
        :key="chartKey"
        class="chart-card"
        v-show="visibleCharts[chartKey]"
        @click="openModal(chartKey)"
      >
        <div class="chart-header">
          <div class="chart-title">{{ chartTitleMap[chartKey] }}{{ chartTitleSuffix }}</div>
          <span class="chart-zoom-icon">&#x2B3A;</span>
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
import * as echarts from 'echarts'
import { getMetricsSummary, getHistoryMetrics, getDeadlocks, getInstances } from '@/api'
import { formatTime, formatDateTime } from '@/utils/datetime'

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
const refreshOptions = [
  { label: '5 秒', value: 5000 },
  { label: '10 秒', value: 10000 },
  { label: '30 秒', value: 30000 },
  { label: '60 秒', value: 60000 },
  { label: '关闭', value: 0 },
]

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

const chartVisibilityOptions = [
  { key: 'cpu', label: 'CPU 使用率趋势' },
  { key: 'memory', label: '内存使用趋势' },
  { key: 'connections', label: '连接数趋势' },
  { key: 'io', label: 'IO 延迟趋势' },
  { key: 'locks', label: '锁等待趋势' },
  { key: 'batch', label: '批处理请求趋势' }
]

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
const defaultStatCardOrder = ['cpu', 'memory', 'connections', 'cache', 'disk', 'batch', 'locks', 'deadlock']
const STORAGE_KEY_STAT_ORDER = 'sql_monitor_stat_order'

const allStatCards = {
  cpu:       { key: 'cpu',       label: 'CPU 使用率',   route: '/?focus=cpu' },
  memory:    { key: 'memory',    label: '内存使用量',   route: '/?focus=memory' },
  connections:{ key: 'connections', label: '活跃连接',   route: '/?focus=connections' },
  cache:     { key: 'cache',     label: '缓存命中率',   route: '/?focus=cache' },
  disk:      { key: 'disk',      label: '磁盘使用率',   route: '/disk-space' },
  batch:     { key: 'batch',     label: '批处理/秒',    route: '/?focus=batch' },
  locks:     { key: 'locks',     label: '锁等待',       route: '/?focus=locks' },
  deadlock:  { key: 'deadlock',  label: '死锁事件',     route: '/deadlocks' },
}

function loadStatCardOrder() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY_STAT_ORDER)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (Array.isArray(parsed) && parsed.length === defaultStatCardOrder.length) {
        return parsed
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

const statCardOrder = computed(() => {
  return statCardOrderKeys.value.map(key => {
    const card = allStatCards[key]
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
    return { ...card, valueStyle }
  }).filter(Boolean)
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
const chartTitleMap = {
  cpu: 'CPU 使用率趋势',
  memory: '内存使用趋势',
  connections: '连接数趋势',
  io: 'IO 延迟趋势',
  locks: '锁等待趋势',
  batch: '批处理请求趋势'
}

// 图表 ref 映射（动态渲染用函数 ref）
const chartRefInstances = {
  cpu: cpuChartRef,
  memory: memoryChartRef,
  connections: connChartRef,
  io: ioChartRef,
  locks: lockChartRef,
  batch: batchChartRef
}

const rangeOptions = [
  { label: '最近 1 小时', value: '1h', hours: 1, refreshMs: 10000 },
  { label: '最近 6 小时', value: '6h', hours: 6, refreshMs: 30000 },
  { label: '最近 24 小时', value: '24h', hours: 24, refreshMs: 60000 },
  { label: '最近 7 天', value: '7d', hours: 168, refreshMs: 120000 }
]

const rangeLabelMap = { '1h': '（最近 1 小时）', '6h': '（最近 6 小时）', '24h': '（最近 24 小时）', '7d': '（最近 7 天）' }
const chartTitleSuffix = computed(() => rangeLabelMap[timeRange.value] || '')

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
  const opt = rangeOptions.find(o => o.value === timeRange.value)
  const hours = opt ? opt.hours : 1
  const now = new Date()
  const start = new Date(now.getTime() - hours * 60 * 60 * 1000)
  return { start: start.toISOString(), end: now.toISOString() }
}

function getCompareTimeRange() {
  const opt = rangeOptions.find(o => o.value === timeRange.value)
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
    name: '上一周期 ' + name,
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
  cpuChart.setOption(createOption('CPU 使用率', cpuValueData.value, cpuTimeData.value, '#1890ff', '%'))
}

function initMemoryChart() {
  if (!memoryChartRef.value) return
  memoryChart = echarts.init(memoryChartRef.value)
  memoryChart.setOption(createOption('内存使用量', memoryValueData.value, cpuTimeData.value, '#52c41a', ' MB'))
}

function initConnChart() {
  if (!connChartRef.value) return
  connChart = echarts.init(connChartRef.value)
  connChart.setOption(createOption('活跃连接数', connValueData.value, cpuTimeData.value, '#fa8c16', ''))
}

function initIoChart() {
  if (!ioChartRef.value) return
  ioChart = echarts.init(ioChartRef.value)
  ioChart.setOption(createDualOption('读延迟', ioReadData.value, '写延迟', ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms'))
}

function initLockChart() {
  if (!lockChartRef.value) return
  lockChart = echarts.init(lockChartRef.value)
  lockChart.setOption(createOption('锁等待数', lockValueData.value, cpuTimeData.value, '#f5222d', ''))
}

function initBatchChart() {
  if (!batchChartRef.value) return
  batchChart = echarts.init(batchChartRef.value)
  batchChart.setOption(createOption('批处理请求/秒', batchValueData.value, cpuTimeData.value, '#722ed1', '/s'))
}

function resizeCharts() {
  cpuChart?.resize()
  memoryChart?.resize()
  connChart?.resize()
  ioChart?.resize()
  lockChart?.resize()
  batchChart?.resize()
  modalChart?.resize()
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
  loading.value = true
  try {
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
          const cmpSeries = buildCompareSeries('CPU 使用率', compareCpuValueData.value, '#91caff')
          cpuChart.setOption(createOption('CPU 使用率', cpuValueData.value, cpuTimeData.value, '#1890ff', '%', cmpSeries), true)
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
          ? buildCompareSeries('内存使用量', extractMetricValues(cmpMemHistory, 'sql_server_memory_mb').map(m => m.metric_value), '#95de64')
          : null
        memoryChart.setOption(createOption('内存使用量', memoryValueData.value, formatTimeLabels(memItems), '#52c41a', ' MB', extra), true)
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
          ? buildCompareSeries('活跃连接数', extractMetricValues(cmpConnHistory, 'active_sessions').map(m => m.metric_value), '#ffc069')
          : null
        connChart.setOption(createOption('活跃连接数', connValueData.value, formatTimeLabels(connItems), '#fa8c16', '', extra), true)
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
          if (cmpRead.length) extraRead = buildCompareSeries('读延迟', cmpRead.map(m => m.metric_value), '#91caff')
          if (cmpWrite.length) extraWrite = buildCompareSeries('写延迟', cmpWrite.map(m => m.metric_value), '#95de64')
        }
        ioChart.setOption(createDualOption('读延迟', ioReadData.value, '写延迟', ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms', extraRead, extraWrite), true)
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
          ? buildCompareSeries('锁等待数', extractMetricValues(cmpLockHistory, 'lock_waits').map(m => m.metric_value), '#ff7875')
          : null
        lockChart.setOption(createOption('锁等待数', lockValueData.value, formatTimeLabels(lockItems), '#f5222d', '', extra), true)
      }
    }

    // 批处理图表
    if (batchHistory?.length) {
      const batchItems = extractMetricValues(batchHistory, 'batch_requests_sec')
      batchValueData.value = batchItems.map(m => m.metric_value)
      if (batchChart) {
        const extra = compareMode.value && cmpBatchHistory?.length
          ? buildCompareSeries('批处理请求/秒', extractMetricValues(cmpBatchHistory, 'batch_requests_sec').map(m => m.metric_value), '#b37feb')
          : null
        batchChart.setOption(createOption('批处理请求/秒', batchValueData.value, formatTimeLabels(batchItems), '#722ed1', '/s', extra), true)
      }
    }
  } catch (e) {
    console.error('获取数据失败', e)
  } finally {
    loading.value = false
  }
}

function openModal(type) {
  modalType.value = type
  const titles = {
    cpu: `CPU 使用率趋势${chartTitleSuffix.value}`,
    memory: `内存使用趋势${chartTitleSuffix.value}`,
    connections: `连接数趋势${chartTitleSuffix.value}`,
    io: `IO 延迟趋势${chartTitleSuffix.value}`,
    locks: `锁等待趋势${chartTitleSuffix.value}`,
    batch: `批处理请求趋势${chartTitleSuffix.value}`
  }
  modalTitle.value = titles[type] || '图表详情'
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
          option = createOption('CPU 使用率', cpuValueData.value, cpuTimeData.value, '#1890ff', '%')
          break
        case 'memory':
          option = createOption('内存使用量', memoryValueData.value, cpuTimeData.value, '#52c41a', ' MB')
          break
        case 'connections':
          option = createOption('活跃连接数', connValueData.value, cpuTimeData.value, '#fa8c16', '')
          break
        case 'io':
          option = createDualOption('读延迟', ioReadData.value, '写延迟', ioWriteData.value, cpuTimeData.value, '#1890ff', '#52c41a', ' ms')
          break
        case 'locks':
          option = createOption('锁等待数', lockValueData.value, cpuTimeData.value, '#f5222d', '')
          break
        case 'batch':
          option = createOption('批处理请求/秒', batchValueData.value, cpuTimeData.value, '#722ed1', '/s')
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
  gap: 20px;
  position: relative;
}

/* loading overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.65);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  z-index: 50;
  border-radius: 8px;
  pointer-events: none;
}

.dark .loading-overlay {
  background: rgba(0, 0, 0, 0.35);
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

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  width: 100%;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  border-radius: 8px;
  padding: 18px 20px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--border-color);
  transition: box-shadow 0.2s, border-color 0.2s, transform 0.2s, opacity 0.2s;
  position: relative;
  cursor: pointer;
  min-height: 72px;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-card.drag-over {
  border-left-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.3);
}

.stat-card[draggable="true"] {
  cursor: grab;
}
.stat-card[draggable="true"]:active {
  cursor: grabbing;
  opacity: 0.7;
}

.stat-cpu       { border-left-color: #1890ff; }
.stat-memory    { border-left-color: #52c41a; }
.stat-connections { border-left-color: #13c2c2; }
.stat-cache     { border-left-color: #722ed1; }
.stat-disk      { border-left-color: #fa8c16; }
.stat-batch     { border-left-color: #eb2f96; }
.stat-locks     { border-left-color: #f5222d; }
.stat-deadlock  { border-left-color: #faad14; }

.stat-drag-handle {
  color: #bfbfbf;
  cursor: grab;
  flex-shrink: 0;
  padding: 2px;
  border-radius: 3px;
  opacity: 0;
  transition: opacity 0.2s;
}
.stat-card:hover .stat-drag-handle {
  opacity: 1;
}
.stat-drag-handle:active {
  cursor: grabbing;
  color: #1890ff;
}

.stat-icon { display: none; }

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-mini-chart {
  display: none;
}

.stat-deadlock .stat-value.deadlock-val {
  font-variant-numeric: tabular-nums;
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
  border-radius: 6px;
  padding: 16px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.chart-card:hover {
  box-shadow: var(--shadow-md);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-zoom-icon {
  font-size: 16px;
  color: var(--text-muted);
  opacity: 0.6;
  transition: opacity 0.2s;
}

.chart-card:hover .chart-zoom-icon {
  opacity: 1;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-toolbar {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 12px 20px;
  box-shadow: var(--shadow);
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
  gap: 6px;
}

.range-tab {
  padding: 5px 14px;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.range-tab:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.range-tab.active {
  color: #fff;
  background: #1890ff;
  border-color: #1890ff;
}

.chart-toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  margin: 0 4px;
}

.refresh-select {
  padding: 5px 10px;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-card);
  cursor: pointer;
  outline: none;
}
.refresh-select:focus {
  border-color: #1890ff;
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
  width: 40px;
  height: 22px;
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
  transition: .3s;
  border-radius: 11px;
}
.compare-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}
input:checked + .compare-slider { background-color: #1890ff; }
input:checked + .compare-slider:before { transform: translateX(18px); }

.compare-select {
  height: 28px;
  padding: 0 8px;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--text-secondary);
  font-size: 13px;
  outline: none;
}

/* 图表自定义 */
.custom-btn-wrapper {
  position: relative;
}

.custom-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.custom-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
}
.custom-btn.active {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.06);
}

.custom-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  min-width: 200px;
  background: var(--bg-card);
  border-radius: 6px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: 12px;
  z-index: 20;
}

.custom-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.custom-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}
.custom-checkbox:hover {
  background: var(--bg-primary);
}
.custom-checkbox input {
  cursor: pointer;
}

/* 排序面板 */
.order-panel {
  min-width: 260px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 4px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: background 0.15s;
}
.order-item:hover {
  background: var(--table-hover);
}

.order-item-label {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.order-item-actions {
  display: flex;
  gap: 2px;
}

.order-arrow-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  padding: 0;
}
.order-arrow-btn:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
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
  margin-top: 10px;
  padding: 7px 12px;
  border: 1px dashed var(--input-border);
  border-radius: 4px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.order-reset-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
}

/* 实例选择下拉框 */
.instance-select {
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--input-border);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  min-width: 180px;
}
.instance-select:focus {
  border-color: #1890ff;
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
}

.modal-content {
  background: var(--bg-card);
  border-radius: 6px;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
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
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.modal-close:hover {
  background: var(--bg-primary);
  color: var(--text-primary);
}

.modal-chart-container {
  flex: 1;
  padding: 16px 24px 24px;
}

/* 响应式 */
.stat-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

@media (max-width: 900px) {
  .chart-card {
    flex: 1 1 100%;
    min-width: 0;
  }

  .stat-card {
    min-width: 140px;
  }

  .modal-content {
    width: 95%;
    height: 70vh;
  }

  .chart-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .stat-cards {
    display: grid;
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

  .deadlock-bar {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }

  .stat-card {
    min-width: 0;
    padding: 14px 16px;
  }

  .stat-value {
    font-size: 24px;
  }

  .chart-toolbar-left {
    flex-wrap: wrap;
  }
}
</style>
