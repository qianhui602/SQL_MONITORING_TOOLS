<template>
  <div class="trends">
    <div class="toolbar">
      <div class="toolbar-group">
        <label class="toolbar-label">指标分类</label>
        <select v-model="category" class="select-input" @change="onCategoryChange">
          <option value="cpu">CPU</option>
          <option value="memory">内存</option>
          <option value="connections">连接数</option>
          <option value="io">IO</option>
          <option value="locks">锁等待</option>
          <option value="batch_requests">批处理请求</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">时间范围</label>
        <select v-model="timeRange" class="select-input" @change="onTimeRangeChange">
          <option value="1h">最近 1 小时</option>
          <option value="6h">最近 6 小时</option>
          <option value="24h">最近 24 小时</option>
          <option value="7d">最近 7 天</option>
        </select>
      </div>
      <div class="toolbar-group">
        <label class="toolbar-label">指标名称</label>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getHistoryMetrics } from '@/api'
import { formatTime } from '@/utils/datetime'

const category = ref('cpu')
const timeRange = ref('1h')
const selectedMetrics = ref([])
const chartRef = ref(null)
let chart = null

const metricOptions = {
  cpu: [
    { label: 'CPU 使用率', value: 'cpu_usage' },
    { label: 'SQL CPU 占用', value: 'sql_cpu' }
  ],
  memory: [
    { label: '内存使用量(MB)', value: 'sql_server_memory_mb' },
    { label: '缓存命中率', value: 'buffer_cache_hit_ratio' },
    { label: '目标内存(MB)', value: 'target_memory_mb' },
    { label: '页生命周期', value: 'page_life_expectancy' }
  ],
  connections: [
    { label: '总连接数', value: 'total_connections' },
    { label: '活跃会话', value: 'active_sessions' },
    { label: '用户连接', value: 'user_connections' },
    { label: '用户进程', value: 'user_processes' }
  ],
  io: [
    { label: '读延迟(ms)', value: 'avg_read_latency_ms' },
    { label: '写延迟(ms)', value: 'avg_write_latency_ms' },
    { label: '总读取次数', value: 'total_reads' },
    { label: '总写入次数', value: 'total_writes' },
    { label: '读取MB', value: 'read_mb' },
    { label: '写入MB', value: 'write_mb' }
  ],
  locks: [
    { label: '等待锁数量', value: 'waiting_locks' },
    { label: '锁等待数', value: 'lock_waits' },
    { label: '平均锁等待(ms)', value: 'avg_lock_wait_ms' }
  ],
  batch_requests: [
    { label: '批处理请求/秒', value: 'batch_requests_sec' },
    { label: 'SQL编译/秒', value: 'sql_compilations_sec' },
    { label: 'SQL重编译/秒', value: 'sql_recompilations_sec' }
  ]
}

const availableMetrics = computed(() => metricOptions[category.value] || [])

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
        const opt = metricOptions[category.value]?.find(o => o.value === metric)
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

onMounted(async () => {
  await nextTick()
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
  }
  selectedMetrics.value = availableMetrics.value.length > 0 ? [availableMetrics.value[0].value] : []
  await fetchHistory()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
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
