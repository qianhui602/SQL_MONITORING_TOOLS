<template>
  <div class="report-page">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-row">
        <div class="toolbar-group">
          <label class="toolbar-label">{{ t('report.instance') }}</label>
          <select v-model="selectedInstanceId" class="instance-select" :disabled="loadingInstances" @change="generateReport">
            <option value="">{{ t('report.allInstances') }}</option>
            <option v-for="inst in instances" :key="inst.id" :value="inst.id">
              {{ inst.name }} ({{ inst.host }}:{{ inst.port }})
            </option>
          </select>
        </div>
        <div class="toolbar-group">
          <label class="toolbar-label">{{ t('report.timeRange') }}</label>
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
          <label class="toolbar-label">{{ t('report.startEnd') }}</label>
          <div class="custom-range">
            <input type="datetime-local" v-model="customStart" class="date-input" />
            <span class="date-sep">→</span>
            <input type="datetime-local" v-model="customEnd" class="date-input" />
          </div>
        </div>
        <div class="toolbar-spacer"></div>
        <button class="btn-primary" :disabled="loading" @click="generateReport">
          <span v-if="loading" class="btn-loading-icon"></span>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          {{ loading ? t('report.generating') : t('report.generate') }}
        </button>
        <button class="btn-secondary" :disabled="!reportData || exporting" @click="exportPDF">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          {{ exporting ? t('report.exporting') : t('report.exportPdf') }}
        </button>
        <button class="btn-secondary" @click="showHistory = true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          {{ t('report.history') }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ t('report.generatingReport') }}</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <p class="error-text">{{ error }}</p>
      <button class="btn-primary" @click="generateReport">{{ t('report.regenerate') }}</button>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="reportData" id="report-content" class="report-content">
      <div class="report-header">
        <div class="report-header-bar"></div>
        <h1 class="report-title">{{ t('report.reportTitle') }}</h1>
        <p class="report-period">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          {{ formatPeriod(reportData.start_time, reportData.end_time) }}
        </p>
        <p class="report-generated-at">{{ t('report.generatedAt') }}{{ formatDateTime(new Date().toISOString(), { second: true }) }}</p>
      </div>

      <!-- 概览摘要卡片 -->
      <section class="report-section">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">{{ t('report.overview') }}</h2>
        </div>
        <div class="summary-grid">
          <div class="summary-card">
            <div class="card-icon-wrap icon-blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="2" x2="9" y2="4"/><line x1="15" y1="2" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="22"/><line x1="15" y1="20" x2="15" y2="22"/><line x1="20" y1="9" x2="22" y2="9"/><line x1="20" y1="14" x2="22" y2="14"/><line x1="2" y1="9" x2="4" y2="9"/><line x1="2" y1="14" x2="4" y2="14"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.cpuUsage') }}</span>
            <span class="card-value" :class="valueColor(reportData.summary.cpu_usage, 80)">
              {{ formatNum(reportData.summary.cpu_usage) }}<span class="unit">%</span>
            </span>
          </div>
          <div class="summary-card">
            <div class="card-icon-wrap icon-green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 19V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v14"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.memoryUsage') }}</span>
            <span class="card-value">
              {{ formatNum(reportData.summary.sql_server_memory_mb) }}<span class="unit">MB</span>
            </span>
          </div>
          <div class="summary-card">
            <div class="card-icon-wrap icon-orange">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.activeConnections') }}</span>
            <span class="card-value">{{ reportData.summary.active_sessions ?? '-' }}</span>
          </div>
          <div class="summary-card">
            <div class="card-icon-wrap icon-purple">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12A10 10 0 1 1 12 2v10z"/><path d="M22 12A10 10 0 0 0 12 2v10z" fill="currentColor" fill-opacity="0.3"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.cacheHitRate') }}</span>
            <span class="card-value" :class="valueColor(reportData.summary.buffer_cache_hit_ratio, 95, true)">
              {{ formatNum(reportData.summary.buffer_cache_hit_ratio) }}<span class="unit">%</span>
            </span>
          </div>
          <div class="summary-card">
            <div class="card-icon-wrap" :class="reportData.deadlocks.total_count > 0 ? 'icon-red' : 'icon-grey'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.deadlockCount') }}</span>
            <span class="card-value" :class="reportData.deadlocks.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.deadlocks.total_count }}
            </span>
          </div>
          <div class="summary-card">
            <div class="card-icon-wrap" :class="reportData.slow_queries.total_count > 0 ? 'icon-red' : 'icon-grey'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <span class="card-label">{{ t('report.slowQueryCount') }}</span>
            <span class="card-value" :class="reportData.slow_queries.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.slow_queries.total_count }}
            </span>
          </div>
        </div>
      </section>

      <!-- 性能趋势图表 -->
      <section class="report-section">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">{{ t('report.performanceTrend') }}</h2>
        </div>
        <div v-if="!hasTrendData" class="no-data-state">
          <div class="no-data-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
              <path d="M3 3v18h18"/><path d="M7 12l4-4 4 4 6-6"/>
            </svg>
          </div>
          <p class="no-data">{{ t('report.noTrendData') }}</p>
        </div>
        <div v-else class="chart-grid">
          <div class="chart-card">
            <div class="chart-header">
              <span class="chart-dot" style="background:#1890ff"></span>
              <h3 class="chart-title">{{ t('report.cpuUsage') }}</h3>
            </div>
            <div ref="chartCpu" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <span class="chart-dot" style="background:#52c41a"></span>
              <h3 class="chart-title">{{ t('report.memoryUsage') }}</h3>
            </div>
            <div ref="chartMemory" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <span class="chart-dot" style="background:#faad14"></span>
              <h3 class="chart-title">{{ t('report.connections') }}</h3>
            </div>
            <div ref="chartConnections" class="chart-box"></div>
          </div>
          <div class="chart-card">
            <div class="chart-header">
              <span class="chart-dot" style="background:#f5222d"></span>
              <h3 class="chart-title">{{ t('report.ioLatency') }}</h3>
            </div>
            <div ref="chartIo" class="chart-box"></div>
          </div>
        </div>
      </section>

      <!-- 死锁分析 -->
      <section class="report-section">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">{{ t('report.deadlockAnalysis') }}</h2>
          <span class="section-tag" :class="reportData.deadlocks.total_count > 0 ? 'tag-warn' : 'tag-ok'">
            {{ reportData.deadlocks.total_count > 0 ? t('report.deadlockTimes', { count: reportData.deadlocks.total_count }) : t('report.deadlockNormal') }}
          </span>
        </div>
        <table v-if="reportData.deadlocks.latest_events.length > 0" class="data-table">
          <thead>
            <tr>
              <th>{{ t('report.occurTime') }}</th>
              <th>{{ t('report.victimSession') }}</th>
              <th>{{ t('report.server') }}</th>
              <th>{{ t('deadlocks.user') }}</th>
              <th>{{ t('deadlocks.host') }}</th>
              <th>{{ t('report.application') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ev in reportData.deadlocks.latest_events" :key="ev.id">
              <td>{{ formatDateTime(ev.occur_at, { second: true }) }}</td>
              <td><code class="inline-code">{{ ev.victim_session_id }}</code></td>
              <td>{{ ev.server_address }}</td>
              <td>{{ ev.login_name || '-' }}</td>
              <td>{{ ev.host_name || '-' }}</td>
              <td>{{ ev.client_app || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-block">
          <div class="empty-icon-ok">✓</div>
          <span>{{ t('report.noDeadlockEvents') }}</span>
        </div>
      </section>

      <!-- 慢查询分析 -->
      <section class="report-section">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">{{ t('report.slowQueryAnalysis') }}</h2>
        </div>
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">{{ t('report.slowQueryCount') }}</span>
            <span class="stat-value">{{ reportData.slow_queries.total_count }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ t('report.avgDurationLabel') }}</span>
            <span class="stat-value">
              {{ formatNum(reportData.slow_queries.avg_duration) }}<span class="stat-unit">ms</span>
            </span>
          </div>
        </div>
        <table v-if="reportData.slow_queries.top_queries.length > 0" class="data-table">
          <thead>
            <tr>
              <th style="width:48px">#</th>
              <th>{{ t('report.sqlPreview') }}</th>
              <th style="width:100px">{{ t('slowQueries.execCount') }}</th>
              <th style="width:120px">{{ t('report.avgDurationMs') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(q, i) in reportData.slow_queries.top_queries" :key="q.id">
              <td><span class="rank-badge">{{ i + 1 }}</span></td>
              <td class="sql-cell" :title="q.sql_text">
                <code>{{ truncateText(q.sql_text, 120) }}</code>
              </td>
              <td>{{ q.execution_count }}</td>
              <td><strong>{{ formatNum(q.avg_elapsed_ms) }}</strong></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-block">
          <div class="empty-icon-ok">✓</div>
          <span>{{ t('report.noSlowQueryData') }}</span>
        </div>
      </section>

      <!-- 阻塞 / 磁盘 / 索引 -->
      <section class="report-section">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">{{ t('report.systemStatus') }}</h2>
        </div>
        <div class="status-grid">
          <div class="status-card">
            <div class="status-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
            </div>
            <h3>{{ t('report.blockingProcess') }}</h3>
            <p class="status-value" :class="reportData.blocking.total_count > 0 ? 'value-warn' : ''">
              {{ reportData.blocking.total_count }}
            </p>
            <p class="status-label">{{ t('report.blockingEvents') }}</p>
          </div>
          <div class="status-card" v-if="reportData.disk">
            <div class="status-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
              </svg>
            </div>
            <h3>{{ t('report.diskSpace') }}</h3>
            <p class="status-value" :class="valueColor(reportData.disk.usage_pct, 85)">
              {{ formatNum(reportData.disk.usage_pct) }}<span class="stat-unit">%</span>
            </p>
            <p class="status-label">{{ t('report.usageLabel') }} ({{ reportData.disk.database_name || '-' }})</p>
          </div>
          <div class="status-card">
            <div class="status-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>
              </svg>
            </div>
            <h3>{{ t('report.indexStatus') }}</h3>
            <div class="status-duo">
              <div>
                <p class="status-value" :class="reportData.indexes.missing_index_count > 0 ? 'value-warn' : ''">
                  {{ reportData.indexes.missing_index_count }}
                </p>
                <p class="status-label">{{ t('report.missingIndex') }}</p>
              </div>
              <div class="status-divider"></div>
              <div>
                <p class="status-value" :class="reportData.indexes.high_fragmentation_count > 0 ? 'value-warn' : ''">
                  {{ reportData.indexes.high_fragmentation_count }}
                </p>
                <p class="status-label">{{ t('report.highFragIndex') }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- AI 分析 -->
      <section class="report-section" v-if="reportData.ai_analysis">
        <div class="section-header">
          <div class="section-title-bar"></div>
          <h2 class="section-title">
            {{ t('report.aiAnalysis') }}
            <span class="ai-badge">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L9.5 9.5 2 12l7.5 2.5L12 22l2.5-7.5L22 12l-7.5-2.5z"/>
              </svg>
              DeepSeek
            </span>
          </h2>
        </div>
        <div class="ai-analysis" v-html="renderMarkdown(reportData.ai_analysis)"></div>
      </section>
    </div>

    <!-- 历史记录面板 -->
    <Transition name="slide-right">
      <div v-if="showHistory" class="history-overlay" @click.self="showHistory = false">
        <div class="history-panel">
          <div class="history-header">
            <h3>{{ t('report.historyReports') }}</h3>
            <button class="close-btn" @click="showHistory = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
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
                <span class="history-time">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                  {{ formatDateTime(rec.created_at, { second: true }) }}
                </span>
              </div>
              <button class="btn-icon" @click.stop="deleteHistory(rec.id)" :title="t('common.delete')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/>
                </svg>
              </button>
            </div>
            <div v-if="historyList.length === 0" class="empty-block">
              <div class="empty-icon-grey">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <span>{{ t('report.noHistory') }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { getReportSummary, saveReport, getReportHistory, deleteReportHistory, getInstances } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const { t } = useI18n()

// ---- 状态 ----
const timePresets = computed(() => [
  { label: t('report.ranges.1h'), value: '1h' },
  { label: t('report.ranges.6h'), value: '6h' },
  { label: t('report.ranges.24h'), value: '24h' },
  { label: t('report.ranges.7d'), value: '7d' },
  { label: t('report.ranges.custom'), value: 'custom' },
])
const timePreset = ref('24h')
const customStart = ref('')
const customEnd = ref('')
const loading = ref(false)
const exporting = ref(false)
const error = ref('')
const reportData = ref(null)
const showHistory = ref(false)
const historyList = ref([])

// 实例筛选
const instances = ref([])
const selectedInstanceId = ref('')
const loadingInstances = ref(false)

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
    const params = {
      start_time: range.start_time,
      end_time: range.end_time,
    }
    if (selectedInstanceId.value) {
      params.instance_id = selectedInstanceId.value
    }
    const data = await getReportSummary(params)
    data.start_time = range.start_time
    data.end_time = range.end_time
    reportData.value = data

    // 自动保存历史
    try {
      await saveReport({
        title: `${t('report.generate')} ${formatDateTime(new Date().toISOString(), { second: true })}`,
        start_time: range.start_time,
        end_time: range.end_time,
        summary_data: JSON.stringify(data),
      })
    } catch { /* ignore save errors */ }

    // 等待 DOM 更新后再渲染图表
    await nextTick()
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('生成报告失败', e)
    error.value = t('report.generateFailed')
  } finally {
    loading.value = false
  }
}

// ---- 图表渲染 ----
function makeOption(trend, color) {
  const items = trend || []
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.85)',
      borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 },
      axisPointer: { type: 'line', lineStyle: { color: 'rgba(24,144,255,0.3)' } },
    },
    grid: { left: 45, right: 12, top: 12, bottom: 28 },
    xAxis: {
      type: 'category',
      data: items.map((i) => {
        const d = new Date(i.collected_at)
        return d.getHours() + ':' + String(d.getMinutes()).padStart(2, '0')
      }),
      axisLine: { lineStyle: { color: '#d9d9d9' } },
      axisTick: { show: false },
      axisLabel: { fontSize: 10, color: '#999' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } },
      axisLabel: { fontSize: 10, color: '#999' },
    },
    series: [
      {
        type: 'line',
        data: items.map((i) => i.metric_value),
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
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
  // 先清理旧的图表实例，避免重复渲染导致内存泄漏
  chartInstances.forEach(c => {
    try { c.dispose() } catch (e) { /* ignore */ }
  })
  chartInstances.length = 0

  if (!hasTrendData.value) return
  const trends = reportData.value?.trends || {}
  const charts = [
    { ref: chartCpu, data: trends.cpu, color: '#1890ff' },
    { ref: chartMemory, data: trends.memory, color: '#52c41a' },
    { ref: chartConnections, data: trends.connections, color: '#faad14' },
    { ref: chartIo, data: trends.io, color: '#f5222d' },
  ]

  charts.forEach(({ ref: elRef, data, color }) => {
    if (!elRef.value) return
    const chart = echarts.init(elRef.value)
    chart.setOption(makeOption(data, color))
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
        t('report.pdfTitle', { page: `${i} / ${pageNum}` }),
        pdfWidth / 2,
        pdfHeight - 5,
        { align: 'center' }
      )
    }

    pdf.save(`${t('report.pdfFilename')}${new Date().toISOString().substring(0, 10)}.pdf`)
  } catch (e) {
    console.error('PDF 导出失败', e)
    alert(t('report.exportFailed'))
  } finally {
    exporting.value = false
  }
}

// ---- Markdown 渲染 ----
function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

// 行内格式：加粗、行内代码（顺序很重要：先转义再替换）
function inlineFormat(s) {
  return s
    .replace(/`([^`]+)`/g, (_, code) => `<code class="md-code">${escapeHtml(code)}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
}

function renderMarkdown(text) {
  if (!text) return ''
  const lines = text.split('\n')
  const out = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // 代码块 ```
    if (/^```/.test(line)) {
      const lang = line.replace(/^```\s*/, '').trim()
      const codeLines = []
      i++
      while (i < lines.length && !/^```/.test(lines[i])) {
        codeLines.push(lines[i])
        i++
      }
      i++ // 跳过结束 ```
      out.push(`<pre class="md-pre"><code${lang ? ` class="lang-${escapeHtml(lang)}"` : ''}>${escapeHtml(codeLines.join('\n'))}</code></pre>`)
      continue
    }

    // 表格检测 (| col1 | col2 |)
    if (/^\|.*\|/.test(line.trim())) {
      const tableLines = []
      while (i < lines.length && /^\|.*\|/.test(lines[i].trim())) {
        tableLines.push(lines[i])
        i++
      }
      // 解析表格
      const parseRow = (row) => row.split('|').slice(1, -1).map(c => c.trim())
      const header = parseRow(tableLines[0])
      // 检查分隔行 (|---|---|)
      const hasDivider = tableLines.length > 1 && /^[\|\s:-]+$/.test(tableLines[1])
      const dataStart = hasDivider ? 2 : 1
      const rows = tableLines.slice(dataStart).map(parseRow)
      // 构建表格 HTML
      let tableHtml = '<div class="md-table-wrap"><table class="md-table"><thead><tr>'
      header.forEach(h => { tableHtml += `<th>${inlineFormat(escapeHtml(h))}</th>` })
      tableHtml += '</tr></thead><tbody>'
      rows.forEach(row => {
        tableHtml += '<tr>'
        row.forEach((cell, ci) => { tableHtml += `<td${ci === 0 ? ' class="col-label"' : ''}>${inlineFormat(escapeHtml(cell))}</td>` })
        tableHtml += '</tr>'
      })
      tableHtml += '</tbody></table></div>'
      out.push(tableHtml)
      continue
    }

    // 标题
    const h4 = line.match(/^####\s+(.+)$/)
    if (h4) { out.push(`<h4>${inlineFormat(escapeHtml(h4[1]))}</h4>`); i++; continue }
    const h3 = line.match(/^###\s+(.+)$/)
    if (h3) { out.push(`<h3>${inlineFormat(escapeHtml(h3[1]))}</h3>`); i++; continue }
    const h2 = line.match(/^##\s+(.+)$/)
    if (h2) { out.push(`<h2>${inlineFormat(escapeHtml(h2[1]))}</h2>`); i++; continue }
    const h1 = line.match(/^#\s+(.+)$/)
    if (h1) { out.push(`<h1>${inlineFormat(escapeHtml(h1[1]))}</h1>`); i++; continue }

    // 优先级标记 #### 🟥 优先级1 → 提示框
    const priMatch = line.match(/^####\s*(🔴|🟠|🟡|🟢|🟣|🟤|⚪|⚫|🔵)?\s*(.+)$/)
    if (priMatch) {
      const emoji = priMatch[1] || ''
      const title = inlineFormat(escapeHtml(priMatch[2]))
      const colorClass = ['🔴', '🟥'].includes(emoji) ? 'prio-red'
        : ['🟠', '🟧'].includes(emoji) ? 'prio-orange'
        : ['🟡'].includes(emoji) ? 'prio-yellow'
        : ['🟢'].includes(emoji) ? 'prio-green'
        : ''
      out.push(`<div class="prio-box ${colorClass}">${emoji ? `<span class="prio-emoji">${emoji}</span>` : ''}<span class="prio-title">${title}</span></div>`)
      i++
      continue
    }

    // 水平线 ---
    if (/^---+$/.test(line.trim())) {
      out.push('<hr/>')
      i++
      continue
    }

    // 引用 >
    const quoteMatch = line.match(/^>\s*(.*)$/)
    if (quoteMatch) {
      const quoteLines = [quoteMatch[1]]
      i++
      while (i < lines.length && /^>\s*/.test(lines[i])) {
        quoteLines.push(lines[i].replace(/^>\s*/, ''))
        i++
      }
      out.push(`<blockquote>${inlineFormat(escapeHtml(quoteLines.join('\n'))).replace(/\n/g, '<br/>')}</blockquote>`)
      continue
    }

    // 有序列表
    if (/^\d+\.\s+/.test(line)) {
      const items = []
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s+/, ''))
        i++
      }
      out.push('<ol>' + items.map(it => `<li>${inlineFormat(escapeHtml(it))}</li>`).join('') + '</ol>')
      continue
    }

    // 无序列表
    if (/^[-*]\s+/.test(line)) {
      const items = []
      while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s+/, ''))
        i++
      }
      out.push('<ul>' + items.map(it => `<li>${inlineFormat(escapeHtml(it))}</li>`).join('') + '</ul>')
      continue
    }

    // 空行
    if (line.trim() === '') {
      i++
      continue
    }

    // 普通段落（合并连续非空行）
    const paraLines = [line]
    i++
    while (i < lines.length && lines[i].trim() !== '' && !/^(#|>|[-*]\s+|\d+\.\s+|```|----+)/.test(lines[i])) {
      paraLines.push(lines[i])
      i++
    }
    out.push(`<p>${inlineFormat(escapeHtml(paraLines.join('\n'))).replace(/\n/g, '<br/>')}</p>`)
  }

  return out.join('\n')
}

// ---- 历史记录 ----
async function loadHistory() {
  try {
    const res = await getReportHistory()
    historyList.value = res.items || res || []
  } catch { /* ignore */ }
}

function loadFromHistory(rec) {
  try {
    if (!rec.summary_data) {
      alert(t('report.historyIncomplete'))
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
    alert(t('report.loadHistoryFailed'))
  }
}

async function deleteHistory(id) {
  try {
    await deleteReportHistory(id)
    historyList.value = historyList.value.filter((r) => r.id !== id)
  } catch { /* ignore */ }
}

// ---- 实例列表 ----
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

// ---- 生命周期 ----
function handleResize() {
  chartInstances.forEach(c => {
    try { c.resize() } catch (e) { /* ignore */ }
  })
}

onMounted(() => {
  loadHistory()
  fetchInstances()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach(c => {
    try { c.dispose() } catch (e) { /* ignore */ }
  })
  chartInstances.length = 0
})
</script>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ============== Toolbar ============== */
.toolbar {
  background: var(--bg-card, #fff);
  border-radius: 6px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-color, #f0f0f0);
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

.toolbar-spacer { flex: 1; }

.toolbar-label {
  font-size: 12px;
  color: var(--text-muted, #8c8c8c);
  font-weight: 500;
}

.time-range-group {
  display: flex;
  gap: 4px;
  background: var(--bg-primary, #f5f6fa);
  border-radius: 8px;
  padding: 3px;
}

.time-btn {
  height: 30px;
  padding: 0 14px;
  border: none;
  border-radius: 5px;
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

.custom-range {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-sep {
  color: var(--text-muted, #999);
  font-size: 13px;
}

.date-input {
  height: 30px;
  padding: 0 8px;
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
  transition: border-color 0.2s;
}

.date-input:focus { border-color: #1890ff; }

/* 实例选择下拉框 */
.instance-select {
  height: 30px;
  padding: 0 10px;
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 6px;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  min-width: 180px;
}
.instance-select:focus { border-color: #1890ff; }
.instance-select:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-primary {
  height: 32px;
  padding: 0 16px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transform: translateY(-1px);
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.btn-secondary {
  height: 32px;
  padding: 0 14px;
  background: var(--bg-card, #fff);
  color: var(--text-primary, #333);
  border: 1px solid var(--border-color, #d9d9d9);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-secondary:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
  background: rgba(24, 144, 255, 0.04);
}
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-loading-icon {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ============== Loading / Error ============== */
.loading-state, .error-state {
  text-align: center;
  padding: 80px 20px;
  background: var(--bg-card, #fff);
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  border: 1px solid var(--border-color, #f0f0f0);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color, #f0f0f0);
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin: 0 auto 16px;
}

.loading-text { color: var(--text-muted, #999); font-size: 14px; }

.error-icon { color: #f5222d; margin-bottom: 12px; opacity: 0.7; }
.error-text { color: #f5222d; margin-bottom: 16px; font-size: 14px; }

/* ============== Report Content ============== */
.report-content {
  background: var(--bg-card, #fff);
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  padding: 36px 40px;
  border: 1px solid var(--border-color, #f0f0f0);
}

.report-header {
  text-align: center;
  margin-bottom: 36px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  position: relative;
}

.report-header-bar {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: #1890ff;
  border-radius: 2px;
}

.report-title {
  font-size: 22px;
  margin: 8px 0 12px;
  color: var(--text-primary, #1f2937);
  font-weight: 700;
  letter-spacing: -0.3px;
}

.report-period {
  font-size: 14px;
  color: var(--text-secondary, #4b5563);
  margin: 6px 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--bg-primary, #f5f6fa);
  border-radius: 6px;
}

.report-generated-at { font-size: 12px; color: var(--text-muted, #9ca3af); margin: 8px 0 0; }

.report-section { margin-bottom: 32px; }

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.section-title-bar {
  width: 4px;
  height: 18px;
  background: #1890ff;
  border-radius: 2px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 6px;
  font-weight: 500;
}

.tag-ok { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
.tag-warn { background: rgba(245, 34, 45, 0.1); color: #f5222d; }

/* ============== Summary Cards ============== */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.summary-card {
  padding: 18px 14px;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  text-align: center;
  border: 1px solid var(--border-color, #f0f0f0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.summary-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
  border-color: #1890ff;
}

.card-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.icon-blue { background: rgba(24, 144, 255, 0.1); color: #1890ff; }
.icon-green { background: rgba(82, 196, 26, 0.1); color: #52c41a; }
.icon-orange { background: rgba(250, 173, 20, 0.1); color: #faad14; }
.icon-purple { background: rgba(114, 46, 209, 0.1); color: #722ed1; }
.icon-red { background: rgba(245, 34, 45, 0.1); color: #f5222d; }
.icon-grey { background: rgba(140, 140, 140, 0.1); color: #8c8c8c; }

.card-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted, #8c8c8c);
  margin-bottom: 6px;
  font-weight: 500;
}

.card-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
  line-height: 1.2;
}

.unit { font-size: 13px; font-weight: 500; color: var(--text-muted, #999); margin-left: 2px; }

.value-warn { color: #f5222d !important; }

/* ============== Charts ============== */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.chart-card {
  padding: 14px 16px;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  border: 1px solid var(--border-color, #f0f0f0);
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.chart-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.chart-title {
  font-size: 13px;
  margin: 0;
  color: var(--text-secondary, #4b5563);
  font-weight: 500;
}

.chart-box { height: 180px; }

/* ============== No Data ============== */
.no-data-state {
  padding: 50px 20px;
  text-align: center;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  border: 1px dashed var(--border-color, #d9d9d9);
  margin: 0;
}

.no-data-icon { color: var(--text-muted, #999); opacity: 0.5; margin-bottom: 8px; }
.no-data { color: var(--text-muted, #999); font-size: 13px; margin: 0; }

/* ============== Stats ============== */
.stat-row {
  display: flex;
  gap: 32px;
  margin-bottom: 16px;
  padding: 14px 18px;
  background: var(--bg-primary, #fafafa);
  border-radius: 8px;
  border: 1px solid var(--border-color, #f0f0f0);
}

.stat-item { display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 12px; color: var(--text-muted, #8c8c8c); }
.stat-value { font-size: 20px; font-weight: 700; color: var(--text-primary, #1f2937); }
.stat-unit { font-size: 13px; font-weight: 500; color: var(--text-muted, #999); margin-left: 2px; }

/* ============== Tables ============== */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-color, #f0f0f0);
}

.data-table th {
  background: #f5f7fa;
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  font-size: 13px;
}

.data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  color: var(--text-secondary, #4b5563);
  font-size: 13px;
  vertical-align: middle;
}

.data-table tbody tr:hover { background: rgba(24, 144, 255, 0.04); }
.data-table tbody tr:last-child td { border-bottom: none; }

.sql-cell {
  max-width: 360px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sql-cell code, .inline-code {
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  font-size: 12px;
  background: rgba(24, 144, 255, 0.08);
  color: #1f2937;
  padding: 1px 6px;
  border-radius: 3px;
  border: 1px solid rgba(24, 144, 255, 0.12);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #1890ff;
  color: #fff;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

/* ============== Status Cards ============== */
.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.status-card {
  padding: 20px 16px;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  border: 1px solid var(--border-color, #f0f0f0);
  text-align: center;
  transition: all 0.2s;
}

.status-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.status-card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #f7f8fa;
  color: #1890ff;
  border-radius: 6px;
  margin-bottom: 10px;
}

.status-card h3 {
  font-size: 14px;
  margin: 0 0 10px;
  color: var(--text-secondary, #4b5563);
  font-weight: 500;
}

.status-value { font-size: 24px; font-weight: 700; color: var(--text-primary, #1f2937); margin: 0; line-height: 1.2; }
.status-label { font-size: 12px; color: var(--text-muted, #8c8c8c); margin-top: 4px; }

.status-duo {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 16px;
}

.status-divider {
  width: 1px;
  background: var(--border-color, #e5e7eb);
}

/* ============== Empty Block ============== */
.empty-block {
  padding: 32px 20px;
  text-align: center;
  color: var(--text-muted, #8c8c8c);
  font-size: 13px;
  background: var(--bg-primary, #fafafa);
  border-radius: 6px;
  border: 1px dashed var(--border-color, #d9d9d9);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.empty-icon-ok {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}

.empty-icon-grey { color: var(--text-muted, #999); opacity: 0.5; }

/* ============== AI Analysis ============== */
.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 6px;
  background: #722ed1;
  color: #fff;
}

.ai-analysis {
  padding: 24px 28px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid var(--border-color, #f0f0f0);
  font-size: 14px;
  line-height: 1.85;
  color: var(--text-primary, #1f2937);
  position: relative;
}

.ai-analysis::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #1890ff;
  border-radius: 3px 0 0 3px;
}

.ai-analysis :deep(h1) {
  font-size: 18px;
  margin: 18px 0 10px;
  color: #1890ff;
  font-weight: 700;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}
.ai-analysis :deep(h1):first-child { margin-top: 0; }

.ai-analysis :deep(h2) {
  font-size: 16px;
  margin: 16px 0 8px;
  color: #1f2937;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.ai-analysis :deep(h2)::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #1890ff;
  border-radius: 2px;
}

.ai-analysis :deep(h3) {
  font-size: 14px;
  margin: 12px 0 6px;
  color: #4b5563;
  font-weight: 600;
}

.ai-analysis :deep(h4) {
  font-size: 13px;
  margin: 10px 0 4px;
  color: #6b7280;
  font-weight: 600;
}

.ai-analysis :deep(p) {
  margin: 8px 0;
  color: #374151;
}

.ai-analysis :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.ai-analysis :deep(em) {
  font-style: italic;
  color: #4b5563;
}

.ai-analysis :deep(ul), .ai-analysis :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.ai-analysis :deep(ul li), .ai-analysis :deep(ol li) {
  margin: 4px 0;
  line-height: 1.7;
  color: #374151;
}

.ai-analysis :deep(ul li::marker) { color: #1890ff; }
.ai-analysis :deep(ol li::marker) { color: #1890ff; font-weight: 600; }

.ai-analysis :deep(.md-code) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  font-size: 12px;
  border: 1px solid #334155;
}

.ai-analysis :deep(.md-pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 10px 0;
  border: 1px solid #334155;
  font-size: 12.5px;
  line-height: 1.6;
}
.ai-analysis :deep(.md-pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
  border: none;
  white-space: pre;
}

.ai-analysis :deep(blockquote) {
  border-left: 3px solid #1890ff;
  background: rgba(24, 144, 255, 0.04);
  padding: 8px 14px;
  margin: 10px 0;
  color: #4b5563;
  border-radius: 0 6px 6px 0;
}

.ai-analysis :deep(hr) {
  border: none;
  border-top: 1px dashed var(--border-color, #e5e7eb);
  margin: 16px 0;
}

.ai-analysis :deep(.prio-box) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  margin: 10px 0 6px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  background: var(--bg-primary, #f5f7fa);
  border: 1px solid var(--border-color, #e5e7eb);
}
.ai-analysis :deep(.prio-emoji) { font-size: 14px; }
.ai-analysis :deep(.prio-box.prio-red) { background: rgba(245, 34, 45, 0.08); border-color: rgba(245, 34, 45, 0.3); color: #cf1322; }
.ai-analysis :deep(.prio-box.prio-orange) { background: rgba(250, 140, 22, 0.08); border-color: rgba(250, 140, 22, 0.3); color: #d46b08; }
.ai-analysis :deep(.prio-box.prio-yellow) { background: rgba(250, 173, 20, 0.08); border-color: rgba(250, 173, 20, 0.3); color: #d48806; }
.ai-analysis :deep(.prio-box.prio-green) { background: rgba(82, 196, 26, 0.08); border-color: rgba(82, 196, 26, 0.3); color: #389e0d; }

/* Markdown 表格样式 */
.ai-analysis :deep(.md-table-wrap) {
  overflow-x: auto;
  margin: 12px 0;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e5e7eb);
}
.ai-analysis :deep(.md-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  line-height: 1.6;
}
.ai-analysis :deep(.md-table thead) {
  background: var(--bg-secondary, #f8fafc);
}
.ai-analysis :deep(.md-table th) {
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  border-bottom: 2px solid var(--border-color, #e5e7eb);
  white-space: nowrap;
}
.ai-analysis :deep(.md-table td) {
  padding: 9px 14px;
  border-bottom: 1px solid var(--border-light, #f1f5f9);
  color: var(--text-secondary, #4b5563);
  vertical-align: top;
}
.ai-analysis :deep(.md-table td.col-label) {
  font-weight: 500;
  color: var(--text-primary, #1f2937);
  white-space: nowrap;
  min-width: 120px;
}
.ai-analysis :deep(.md-table tbody tr:hover) {
  background: rgba(24, 144, 255, 0.03);
}
.ai-analysis :deep(.md-table tbody tr:last-child td) {
  border-bottom: none;
}

/* ============== History Panel ============== */
.history-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  backdrop-filter: blur(2px);
}

.history-panel {
  width: 380px;
  background: var(--bg-card, #fff);
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.history-header h3 { margin: 0; font-size: 16px; font-weight: 600; }

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted, #999);
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover { color: var(--text-primary, #333); background: var(--bg-primary, #f5f6fa); }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.history-item:hover {
  background: var(--bg-primary, #f5f6fa);
  border-color: var(--border-color, #e5e7eb);
}

.history-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
  flex: 1;
  margin-right: 8px;
}

.history-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #1f2937);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 11px;
  color: var(--text-muted, #8c8c8c);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  color: var(--text-muted, #999);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover { color: #f5222d; background: rgba(245, 34, 45, 0.08); }

/* Slide animation */
.slide-right-enter-active, .slide-right-leave-active {
  transition: all 0.2s ease;
}
.slide-right-enter-from, .slide-right-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
.slide-right-enter-active .history-panel, .slide-right-leave-active .history-panel {
  transition: transform 0.3s ease;
}
.slide-right-enter-from .history-panel, .slide-right-leave-to .history-panel {
  transform: translateX(100%);
}

/* ============== Responsive ============== */
@media (max-width: 1100px) {
  .summary-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .summary-grid, .chart-grid, .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .report-content { padding: 24px 20px; }
}
</style>
