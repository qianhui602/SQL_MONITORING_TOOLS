<template>
  <div class="trends">
    <div class="toolbar">
      <div class="toolbar-group">
        <label class="toolbar-label">{{ t('trends.instance') }}</label>
        <select v-model="selectedInstance" class="instance-select">
          <option value="">{{ t('trends.allInstances') }}</option>
          <option v-for="item in instances" :key="item.id" :value="item">{{ item.name }} ({{ item.host }}:{{ item.port }})</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">{{ t('trends.metricCategory') }}</label>
        <select v-model="category" class="select-input" @change="onCategoryChange">
          <option value="cpu">CPU</option>
          <option value="memory">{{ t('trends.categories.memory') }}</option>
          <option value="connections">{{ t('trends.categories.connections') }}</option>
          <option value="io">IO</option>
          <option value="locks">{{ t('trends.categories.locks') }}</option>
          <option value="batch_requests">{{ t('trends.categories.batch_requests') }}</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">{{ t('trends.timeRange') }}</label>
        <select v-model="timeRange" class="select-input" @change="onTimeRangeChange">
          <option value="1h">{{ t('trends.ranges["1h"]') }}</option>
          <option value="6h">{{ t('trends.ranges["6h"]') }}</option>
          <option value="24h">{{ t('trends.ranges["24h"]') }}</option>
          <option value="7d">{{ t('trends.ranges["7d"]') }}</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">{{ t('trends.metricName') }}</label>
        <div class="checkbox-group">
          <label v-for="m in availableMetrics" :key="m.value" class="checkbox-item">
            <input type="checkbox" :value="m.value" v-model="selectedMetrics" @change="fetchHistory" />
            <span>{{ m.label }}</span>
          </label>
        </div>
      </div>
    </div>

    <div class="chart-card">
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { getHistoryMetrics } from '@/api'
import { formatTime } from '@/utils/datetime'
import { useInstanceFilter } from '@/composables/useInstanceFilter'

const { t } = useI18n()

const { instances, selectedInstance, loadingInstances, getServerAddress } = useInstanceFilter()

const category = ref('cpu')
const timeRange = ref('1h')
const selectedMetrics = ref([])
const chartRef = ref(null)
let chart = null

const metricOptions = computed(() => ({
  cpu: [
    { label: t('trends.metrics.cpu_usage'), value: 'cpu_usage' },
    { label: t('trends.metrics.sql_cpu'), value: 'sql_cpu' }
  ],
  memory: [
    { label: t('trends.metrics.sql_server_memory_mb'), value: 'sql_server_memory_mb' },
    { label: t('trends.metrics.buffer_cache_hit_ratio'), value: 'buffer_cache_hit_ratio' },
    { label: t('trends.metrics.target_memory_mb'), value: 'target_memory_mb' },
    { label: t('trends.metrics.page_life_expectancy'), value: 'page_life_expectancy' }
  ],
  connections: [
    { label: t('trends.metrics.total_connections'), value: 'total_connections' },
    { label: t('trends.metrics.active_sessions'), value: 'active_sessions' },
    { label: t('trends.metrics.user_connections'), value: 'user_connections' },
    { label: t('trends.metrics.user_processes'), value: 'user_processes' }
  ],
  io: [
    { label: t('trends.metrics.avg_read_latency_ms'), value: 'avg_read_latency_ms' },
    { label: t('trends.metrics.avg_write_latency_ms'), value: 'avg_write_latency_ms' },
    { label: t('trends.metrics.total_reads'), value: 'total_reads' },
    { label: t('trends.metrics.total_writes'), value: 'total_writes' },
    { label: t('trends.metrics.read_mb'), value: 'read_mb' },
    { label: t('trends.metrics.write_mb'), value: 'write_mb' }
  ],
  locks: [
    { label: t('trends.metrics.waiting_locks'), value: 'waiting_locks' },
    { label: t('trends.metrics.lock_waits'), value: 'lock_waits' },
    { label: t('trends.metrics.avg_lock_wait_ms'), value: 'avg_lock_wait_ms' }
  ],
  batch_requests: [
    { label: t('trends.metrics.batch_requests_sec'), value: 'batch_requests_sec' },
    { label: t('trends.metrics.sql_compilations_sec'), value: 'sql_compilations_sec' },
    { label: t('trends.metrics.sql_recompilations_sec'), value: 'sql_recompilations_sec' }
  ]
}))

const availableMetrics = computed(() => metricOptions.value[category.value] || [])

function onCategoryChange() {
  selectedMetrics.value = availableMetrics.value.length > 0 ? [availableMetrics.value[0].value] : []
  fetchHistory()
}

function onTimeRangeChange() {
  fetchHistory()
}

const colors = ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1', '#13c2c2']

function buildOption(timeLabels, seriesList) {
  return {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: seriesList.map(s => s.name),
      bottom: 0
    },
    grid: {
      left: 50,
      right: 20,
      top: 20,
      bottom: 40
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, bottom: 0 }
    ],
    xAxis: {
      type: 'category',
      data: timeLabels,
      axisLabel: { fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#e8e8e8' } }
    },
    series: seriesList.map((s, i) => ({
      name: s.name,
      type: 'line',
      data: s.data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: colors[i % colors.length], width: 2 },
      itemStyle: { color: colors[i % colors.length] }
    }))
  }
}

async function fetchHistory() {
  try {
    const rangeMap = { '1h': 1, '6h': 6, '24h': 24, '7d': 168 }
    const hours = rangeMap[timeRange.value] || 1
    const now = new Date()
    const start = new Date(now.getTime() - hours * 60 * 60 * 1000)
    const params = {
      category: category.value,
      start_time: start.toISOString(),
      end_time: now.toISOString(),
      limit: 1000
    }
    const serverAddress = getServerAddress()
    if (serverAddress) params.server_address = serverAddress

    const seriesList = []
    let allLabels = []

    for (const metric of selectedMetrics.value) {
      const p = { ...params, metric_name: metric }
      const data = await getHistoryMetrics(p)
      if (data?.length) {
        const labels = data.map(m => formatTime(m.collected_at))
        if (labels.length > allLabels.length) {
          allLabels = labels
        }
        const values = data.map(m => m.metric_value)
        const opt = metricOptions.value[category.value]?.find(o => o.value === metric)
        seriesList.push({ name: opt?.label || metric, data: values })
      }
    }

    if (chart) {
      chart.setOption(buildOption(allLabels, seriesList), true)
    }
  } catch (e) {
    console.error('获取历史指标失败', e)
  }
}

watch(selectedInstance, () => {
  fetchHistory()
})

function handleResize() {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
  }
  selectedMetrics.value = availableMetrics.value.length > 0 ? [availableMetrics.value[0].value] : []
  await fetchHistory()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.trends {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
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
  font-weight: 500;
}

.select-input {
  height: 32px;
  min-width: 140px;
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

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  cursor: pointer;
  user-select: none;
}

.checkbox-item input {
  cursor: pointer;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.chart-container {
  width: 100%;
  height: 480px;
}
</style>
