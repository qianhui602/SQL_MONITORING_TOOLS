<template>
  <div class="report-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-row">
        <div class="toolbar-group">
          <label class="toolbar-label">时间范围</label>
          <div class="time-range-group">
            <button
              v-for="opt in timePresets"
              :key="opt.value"
              class="time-btn"
              :class="{ active: timePreset === opt.value }"
              @click="onPresetChange(opt.value)"
            >{{ opt.label }}</button>
          </div>
        </div>
        <div class="toolbar-group" v-if="timePreset === 'custom'">
          <label class="toolbar-label">开始</label>
          <input type="datetime-local" v-model="customStart" class="date-input" />
          <label class="toolbar-label" style="margin-left:8px">结束</label>
          <input type="datetime-local" v-model="customEnd" class="date-input" />
        </div>
        <button class="btn-primary" :disabled="loading" @click="generateReport">
          <span v-if="loading" class="btn-loading-icon"></span>
          {{ loading ? '生成中...' : '生成报告' }}
        </button>
        <button class="btn-secondary" :disabled="!reportData || exporting" @click="exportPDF">
          {{ exporting ? '导出中...' : '导出PDF' }}
        </button>
        <button class="btn-secondary" @click="showHistory = !showHistory">
          历史记录
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在生成报告，请稍候...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p class="error-text">{{ error }}</p>
      <button class="btn-primary" @click="generateReport">重新生成</button>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData" id="report-content" class="report-content">
      <div class="report-header">
        <h1 class="report-title">SQL 监控平台 - 系统性能分析报告</h1>
        <p class="report-period">
          报告周期：{{ formatPeriod(reportData.start_time, reportData.end_time) }}
        </p>
        <p class="report-generated-at">
          生成时间：{{ formatDateTime(new Date().toISOString(), { second: true }) }}
        </p>
      </div>

      <!-- 概览摘要卡片 -->
      <section class="report-section">
        <h2 class="section-title">概览摘要</h2>
        <div class="summary-grid">
          <div class="summary-card">
            <span class="card-label">CPU 使用率</span>
            <span class="card-value" :class="valueColor(reportData.summary.cpu_usage, 80)">
              {{ formatNum(reportData.summary.cpu_usage) }}%
            </span>
          </div>
          <div class="summary-card">
            <span class="card-label">内存使用量</span>
            <span class="card-value">{{ formatNum(reportData.summary.sql_server_memory_mb) }} MB</span>
          </div>
          <div class="summary-card">
            <span class="card-label">活跃连接数</span>
            <span class="card-value">{{ reportData.summary.active_sessions ?? '-' }}</span>
          </div>
          <div class="summary-card">
            <span class="card-label">缓存命中率</span>
            <span class="card-value" :class="valueColor(reportData.summary.buffer_cache_hit_ratio, 95, true)">
              {{ formatNum(reportData.summary.buffer_cache_hit_ratio) }}%
            </span>
          </div>
          <div class="summary-card">
            <span class="card-label">死锁次数</span>
            <span class="card-value" :class="reportData.deadlocks.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.deadlocks.total_count }}
            </span>
          </div>
          <div class="summary-card">
            <span class="card-label">慢查询数</span>
            <span class="card-value" :class="reportData.slow_queries.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.slow_queries.total_count }}
            </span>
          </div>
        </div>
      </section>

      <!-- 性能趋势图表 -->
      <section class="report-section">
        <h2 class="section-title">性能趋势</h2>
        <div v-if="!hasTrendData" class="no-data-state">
          <p class="no-data">暂无性能趋势数据，请确保监控数据采集任务已启动</p>
        </div>
        <div v-else class="chart-grid">
          <div class="chart-card">
            <h3 class="chart-title">CPU 使用率</h3>
            <div ref="chartCpu" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <h3 class="chart-title">内存使用</h3>
            <div ref="chartMemory" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <h3 class="chart-title">连接数</h3>
            <div ref="chartConnections" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <h3 class="chart-title">I/O 延迟</h3>
            <div ref="chartIo" class="chart-box"></div>
          </div>
        </div>
      </section>

      <!-- 死锁分析 -->
      <section class="report-section">
        <h2 class="section-title">死锁分析</h2>
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">死锁次数</span>
            <span class="stat-value" :class="reportData.deadlocks.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.deadlocks.total_count }}
            </span>
          </div>
        </div>
        <table v-if="reportData.deadlocks.latest_events.length > 0" class="data-table">
          <thead>
            <tr>
              <th>发生时间</th>
              <th>受害会话ID</th>
              <th>服务器</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in reportData.deadlocks.latest_events" :key="ev.id">
              <td>{{ formatDateTime(ev.occur_at, { second: true }) }}</td>
              <td>{{ ev.victim_session_id }}</td>
              <td>{{ ev.server_address }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">无死锁事件</p>
      </section>

      <!-- 慢查询分析 -->
      <section class="report-section">
        <h2 class="section-title">慢查询分析</h2>
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">慢查询数</span>
            <span class="stat-value">{{ reportData.slow_queries.total_count }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均耗时</span>
            <span class="stat-value">{{ formatNum(reportData.slow_queries.avg_duration) }} ms</span>
          </div>
        </div>
        <table v-if="reportData.slow_queries.top_queries.length > 0" class="data-table">
          <thead>
            <tr>
              <th style="width:40px">#</th>
              <th>SQL（前200字符）</th>
              <th>执行次数</th>
              <th>平均耗时(ms)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(q, i) in reportData.slow_queries.top_queries" :key="q.id">
              <td>{{ i + 1 }}</td>
              <td class="sql-cell" :title="q.sql_text">{{ truncateText(q.sql_text, 120) }}</td>
              <td>{{ q.execution_count }}</td>
              <td>{{ formatNum(q.avg_elapsed_ms) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="no-data">无慢查询数据</p>
      </section>

      <!-- 阻塞 / 磁盘 / 索引 -->
      <section class="report-section">
        <h2 class="section-title">系统状态</h2>
        <div class="status-grid">
          <div class="status-card">
            <h3>阻塞进程</h3>
            <p class="status-value">{{ reportData.blocking.total_count }}</p>
            <p class="status-label">阻塞事件数</p>
          </div>
          <div class="status-card" v-if="reportData.disk">
            <h3>磁盘空间</h3>
            <p class="status-value" :class="valueColor(reportData.disk.usage_pct, 85)">
              {{ formatNum(reportData.disk.usage_pct) }}%
            </p>
            <p class="status-label">使用率 ({{ reportData.disk.database_name || '-' }})</p>
          </div>
          <div class="status-card">
            <h3>索引状况</h3>
            <p class="status-value">{{ reportData.indexes.missing_index_count }}</p>
            <p class="status-label">缺失索引</p>
            <p class="status-value" style="margin-top:4px">{{ reportData.indexes.high_fragmentation_count }}</p>
            <p class="status-label">高碎片索引</p>
          </div>
        </div>
      </section>

      <!-- AI 分析 -->
      <section class="report-section" v-if="reportData.ai_analysis">
        <h2 class="section-title">AI 分析与建议</h2>
        <div class="ai-analysis" v-html="renderMarkdown(reportData.ai_analysis)"></div>
      </section>
    </div>

    <!-- 历史记录面板 -->
    <div v-if="showHistory" class="history-overlay" @click.self="showHistory = false">
      <div class="history-panel">
        <div class="history-header">
          <h3>历史报告</h3>
          <button class="close-btn" @click="showHistory = false">✕</button>
        </div>
        <div class="history-list">
          <div
            v-for="rec in historyList"
            :key="rec.id"
            class="history-item"
            @click="loadFromHistory(rec)"
          >
            <div class="history-item-info">
              <span class="history-title">{{ rec.title }}</span>
              <span class="history-time">{{ formatDateTime(rec.created_at, { second: true }) }}</span>
            </div>
            <button class="btn-icon" @click.stop="deleteHistory(rec.id)" title="删除">🗑</button>
          </div>
          <p v-if="historyList.length === 0" class="no-data">暂无历史记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getReportSummary, saveReport, getReportHistory, deleteReportHistory } from '@/api'
import { formatDateTime } from '@/utils/datetime'

// ---- 状态 ----
const timePresets = [
  { label: '最近1小时', value: '1h' },
  { label: '最近6小时', value: '6h' },
  { label: '最近24小时', value: '24h' },
  { label: '最近7天', value: '7d' },
  { label: '自定义', value: 'custom' },
]
const timePreset = ref('24h')
const customStart = ref('')
const customEnd = ref('')
const loading = ref(false)
const exporting = ref(false)
const error = ref('')
const reportData = ref(null)
const showHistory = ref(false)
const historyList = ref([])

const hasTrendData = computed(() => {
  if (!reportData.value?.trends) return false
  const trends = reportData.value.trends
  return !!(trends.cpu?.length || trends.memory?.length || trends.connections?.length || trends.io?.length)
})

// 图表 refs
const chartCpu = ref(null)
const chartMemory = ref(null)
const chartConnections = ref(null)
const chartIo = ref(null)
const chartInstances = []

// ---- 工具函数 ----
function formatNum(v) {
  if (v === null || v === undefined) return '-'
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: 1 })
}

function truncateText(text, maxLen) {
  if (!text) return '-'
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

function valueColor(val, threshold, reverse = false) {
  if (val === null || val === undefined) return ''
  if (reverse) {
    return val < threshold ? 'value-warn' : ''
  }
  return val > threshold ? 'value-warn' : ''
}

function formatPeriod(start, end) {
  const s = start ? start.replace('T', ' ').substring(0, 16) : '-'
  const e = end ? end.replace('T', ' ').substring(0, 16) : '-'
  return `${s} ~ ${e}`
}

// ---- 时间范围 ----
function getTimeRange() {
  const now = new Date()
  let start
  const rangeMap = { '1h': 1, '6h': 6, '24h': 24, '7d': 168 }
  if (timePreset.value === 'custom') {
    start = new Date(customStart.value)
    const end = new Date(customEnd.value)
    return {
      start_time: start.toISOString(),
      end_time: end.toISOString(),
    }
  }
  const hours = rangeMap[timePreset.value] || 24
  start = new Date(now.getTime() - hours * 60 * 60 * 1000)
  return { start_time: start.toISOString(), end_time: now.toISOString() }
}

function onPresetChange(value) {
  timePreset.value = value
  if (value === 'custom') {
    const now = new Date()
    const past = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    customStart.value = past.toISOString().substring(0, 16)
    customEnd.value = now.toISOString().substring(0, 16)
  } else {
    generateReport()
  }
}

// ---- 报告生成 ----
async function generateReport() {
  loading.value = true
  error.value = ''
  reportData.value = null
  try {
    const range = getTimeRange()
    const data = await getReportSummary({
      start_time: range.start_time,
      end_time: range.end_time,
    })
    data.start_time = range.start_time
    data.end_time = range.end_time
    reportData.value = data

    // 自动保存历史
    try {
      await saveReport({
        title: `系统性能报告 ${formatDateTime(new Date().toISOString(), { second: true })}`,
        start_time: range.start_time,
        end_time: range.end_time,
        summary_data: JSON.stringify(data),
      })
    } catch { /* ignore save errors */ }

    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('生成报告失败', e)
    error.value = '生成报告失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// ---- 图表渲染 ----
function makeOption(trend, valueKey, nameKey, color) {
  const items = trend || []
  return {
    tooltip: { trigger: 'axis', textStyle: { fontSize: 11 } },
    grid: { left: 50, right: 10, top: 10, bottom: 25 },
    xAxis: {
      type: 'category',
      data: items.map((i) => {
        const d = new Date(i.collected_at)
        return d.getHours() + ':' + String(d.getMinutes()).padStart(2, '0')
      }),
      axisLabel: { fontSize: 10, interval: 'auto' },
    },
    yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
    series: [
      {
        type: 'line',
        data: items.map((i) => i[nameKey || 'metric_value']),
        smooth: true,
        lineStyle: { width: 2, color },
        itemStyle: { color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '05' },
          ]),
        },
      },
    ],
  }
}

function renderCharts() {
  if (!hasTrendData.value) return
  const trends = reportData.value?.trends || {}
  const charts = [
    { ref: chartCpu, data: trends.cpu, nameKey: 'metric_value', color: '#1890ff' },
    { ref: chartMemory, data: trends.memory, nameKey: 'metric_value', color: '#52c41a' },
    { ref: chartConnections, data: trends.connections, nameKey: 'metric_value', color: '#faad14' },
    { ref: chartIo, data: trends.io, nameKey: 'metric_value', color: '#f5222d' },
  ]

  charts.forEach(({ ref: elRef, data, nameKey, color }) => {
    if (!elRef.value) return
    const chart = echarts.init(elRef.value)
    chart.setOption(makeOption(data, null, nameKey, color))
    chartInstances.push(chart)
  })
}

// ---- PDF 导出 ----
async function exportPDF() {
  if (!reportData.value) return
  exporting.value = true
  try {
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')

    const content = document.getElementById('report-content')
    if (!content) return

    const canvas = await html2canvas(content, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()
    const imgWidth = pdfWidth - 20
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 10
    let pageNum = 1

    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight)
    heightLeft -= pdfHeight - 20

    while (heightLeft > 0) {
      position = -(pdfHeight - 20) * pageNum + 10
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight)
      heightLeft -= pdfHeight - 20
      pageNum++
    }

    // 添加页码
    for (let i = 1; i <= pageNum; i++) {
      pdf.setPage(i)
      pdf.setFontSize(8)
      pdf.setTextColor(150)
      pdf.text(
        `SQL 监控平台报告 - 第 ${i} / ${pageNum} 页`,
        pdfWidth / 2,
        pdfHeight - 5,
        { align: 'center' }
      )
    }

    pdf.save(`SQL监控报告_${new Date().toISOString().substring(0, 10)}.pdf`)
  } catch (e) {
    console.error('PDF 导出失败', e)
    alert('PDF 导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// ---- Markdown 渲染 ----
function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // 标题 ###
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    // 标题 ##
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    // 标题 #
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码
    .replace(/`(.+?)`/g, '<code>$1</code>')
    // 无序列表
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // 有序列表
    .replace(/^\d+\.\s(.+)$/gm, '<li>$1</li>')
    // 换行
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')

  html = html.replace(/<li>/g, '<ul><li>').replace(/<\/li>(?!.*<\/li>)/g, '</li></ul>')
  return '<p>' + html + '</p>'
}

// ---- 历史记录 ----
async function loadHistory() {
  try {
    historyList.value = await getReportHistory()
  } catch { /* ignore */ }
}

function loadFromHistory(rec) {
  try {
    if (!rec.summary_data) {
      alert('历史报告数据不完整，无法加载')
      return
    }
    const data = JSON.parse(rec.summary_data)
    data.start_time = rec.start_time
    data.end_time = rec.end_time
    reportData.value = data
    showHistory.value = false
    nextTick(() => renderCharts())
  } catch (e) {
    console.error('加载历史报告失败', e)
    alert('加载历史报告失败')
  }
}

async function deleteHistory(id) {
  try {
    await deleteReportHistory(id)
    historyList.value = historyList.value.filter((r) => r.id !== id)
  } catch { /* ignore */ }
}

// ---- 生命周期 ----
onMounted(() => {
  loadHistory()
})

onUnmounted(() => {
  chartInstances.forEach((c) => c.dispose())
})
</script>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Toolbar */
.toolbar {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.toolbar-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
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

.time-btn:hover { color: var(--text-primary, #333); }

.time-btn.active {
  background: var(--bg-card, #fff);
  color: #1890ff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.date-input {
  height: 30px;
  padding: 0 8px;
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover:not(:disabled) { background: #40a9ff; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  height: 32px;
  padding: 0 16px;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover { color: #1890ff; border-color: #1890ff; }

.btn-loading-icon {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Loading / Error */
.loading-state, .error-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border-color, #f0f0f0);
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 12px;
}

.error-text { color: #f5222d; margin-bottom: 12px; }

/* Report Content */
.report-content {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 32px;
}

.report-header {
  text-align: center;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color, #f0f0f0);
}

.report-title { font-size: 22px; margin: 0 0 8px; color: var(--text-primary, #333); }
.report-period { font-size: 14px; color: var(--text-muted, #999); margin: 4px 0; }
.report-generated-at { font-size: 12px; color: var(--text-muted, #bbb); margin: 4px 0; }

.report-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin: 0 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

/* Summary Cards */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  justify-items: stretch;
}

.summary-card {
  padding: 20px 16px;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--border-color, #f0f0f0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.card-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted, #999);
  margin-bottom: 8px;
  font-weight: 500;
}

.card-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #333);
  line-height: 1.3;
}

.value-warn { color: #f5222d !important; }

/* Charts */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  padding: 12px;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  border: 1px solid var(--border-color, #f0f0f0);
}

.chart-title {
  font-size: 13px;
  margin: 0 0 8px;
  color: var(--text-secondary, #666);
}

.chart-box { height: 200px; }

/* No Data State */
.no-data-state {
  padding: 40px 20px;
  text-align: center;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  border: 1px dashed var(--border-color, #d9d9d9);
  margin: 16px 0;
}

/* Stats */
.stat-row {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label { font-size: 12px; color: var(--text-muted, #999); }
.stat-value { font-size: 20px; font-weight: 600; color: var(--text-primary, #333); }

/* Tables */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: var(--bg-primary, #fafafa);
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary, #333);
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  color: var(--text-secondary, #555);
  font-size: 12px;
}

.sql-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 11px;
}

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.status-card {
  padding: 16px;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  border: 1px solid var(--border-color, #f0f0f0);
  text-align: center;
}

.status-card h3 {
  font-size: 14px;
  margin: 0 0 12px;
  color: var(--text-secondary, #666);
}

.status-value { font-size: 22px; font-weight: 700; color: var(--text-primary, #333); }
.status-label { font-size: 12px; color: var(--text-muted, #999); margin-top: 2px; }

/* AI Analysis */
.ai-analysis {
  padding: 16px;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  border: 1px solid var(--border-color, #f0f0f0);
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary, #333);
}

.ai-analysis :deep(h2) { font-size: 16px; margin: 16px 0 8px; color: #1890ff; }
.ai-analysis :deep(h3) { font-size: 15px; margin: 14px 0 6px; }
.ai-analysis :deep(h4) { font-size: 14px; margin: 12px 0 4px; }
.ai-analysis :deep(strong) { font-weight: 600; }
.ai-analysis :deep(code) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}
.ai-analysis :deep(ul) { padding-left: 20px; margin: 6px 0; }
.ai-analysis :deep(li) { margin: 4px 0; }

.no-data {
  color: var(--text-muted, #999);
  font-size: 13px;
  text-align: center;
  padding: 20px;
}

/* History Panel */
.history-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.history-panel {
  width: 360px;
  background: var(--bg-card, #fff);
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.history-header h3 { margin: 0; font-size: 16px; }

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--text-muted, #999);
  padding: 4px;
}

.close-btn:hover { color: var(--text-primary, #333); }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 4px;
}

.history-item:hover { background: var(--bg-primary, #f5f6fa); }

.history-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.history-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #333);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 11px;
  color: var(--text-muted, #999);
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  opacity: 0.6;
  transition: opacity 0.15s;
}

.btn-icon:hover { opacity: 1; }
</style>
