<template>
  <div class="ai-assistant">
    <!-- 左侧任务列表 -->
    <div class="task-sidebar">
      <div class="sidebar-header">
        <h3 class="sidebar-title">{{ t('aiAssistant.title') }}</h3>
      </div>
      <button class="new-task-btn" @click="startNewTask">
        {{ t('aiAssistant.newTask') }}
      </button>
      <div class="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-card"
          :class="{ active: currentTaskId === task.id }"
          @click="selectTask(task.id)"
        >
          <div class="task-card-content">
            <span class="task-card-text">{{ task.query }}</span>
            <span class="task-card-time">{{ formatTime(task.created_at) }}</span>
          </div>
          <span class="task-status-dot" :class="'status-' + task.status"></span>
          <button class="task-delete-btn" @click.stop="onDeleteTask(task)" title="删除">×</button>
        </div>
        <div v-if="tasks.length === 0" class="task-empty">
          <p>{{ t('aiAssistant.noTasks') }}</p>
          <p class="task-empty-hint">{{ t('aiAssistant.noTasksHint') }}</p>
        </div>
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="task-main">
      <!-- 欢迎页 -->
      <div v-if="!currentTask" class="welcome-area">
        <div class="welcome-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1.27a2 2 0 0 1-3.46 0H6.73a2 2 0 0 1-3.46 0H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2zM9.5 13a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm5 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>
          </svg>
        </div>
        <h2 class="welcome-title">{{ t('aiAssistant.title') }}</h2>
        <p class="welcome-subtitle">{{ t('aiAssistant.subtitle') }}</p>
        <div class="input-area">
          <div class="input-wrap">
            <input
              v-model="newQuery"
              type="text"
              class="task-input"
              :placeholder="t('aiAssistant.inputPlaceholder')"
              :disabled="creating"
              @keyup.enter="onCreateTask"
            />
            <button class="send-btn" :disabled="!newQuery.trim() || creating" @click="onCreateTask">
              <svg v-if="!creating" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
              <span v-else class="spinner"></span>
            </button>
          </div>
        </div>
      </div>

      <!-- 任务执行视图 -->
      <div v-else class="execution-area" ref="executionAreaRef">
        <div class="execution-header">
          <h3 class="execution-title">{{ currentTask.query }}</h3>
          <span class="execution-status" :class="'status-' + currentTask.status">
            {{ statusLabel(currentTask.status) }}
          </span>
        </div>

        <!-- 思考 / 任务拆解区域 -->
        <div class="thinking-section">
          <div class="section-label">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>{{ t('aiAssistant.taskPlanning') }}</span>
          </div>
        </div>

        <!-- 工具调用步骤列表（折叠） -->
        <div class="steps-section">
          <div
            v-for="step in toolSteps"
            :key="step.id"
            class="step-card"
            :class="['step-' + step.status, { expanded: isStepExpanded(step.id) }]"
          >
            <div class="step-header" @click="toggleStep(step)">
              <div class="step-icon">
                <span v-if="step.status === 'pending'" class="step-dot pending"></span>
                <span v-else-if="step.status === 'running'" class="spinner small"></span>
                <svg v-else-if="step.status === 'completed'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#52c41a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <svg v-else-if="step.status === 'failed'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ff4d4f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <div class="step-info">
                <span class="step-title">{{ step.title }}</span>
              </div>
              <span v-if="step.status === 'completed' || step.status === 'failed'" class="step-expand-icon">
                {{ isStepExpanded(step.id) ? '▲' : '▼' }}
              </span>
            </div>
            <div v-if="isStepExpanded(step.id) && step.result" class="step-result">
              <div class="result-content" v-html="renderMarkdown(step.result)"></div>
            </div>
            <div v-if="isStepExpanded(step.id) && step.error" class="step-error">
              {{ step.error }}
            </div>
          </div>
        </div>

        <!-- 诊断报告区域（流式输出） -->
        <div v-if="showReportArea" class="report-section">
          <div class="report-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <line x1="10" y1="9" x2="8" y2="9"/>
            </svg>
            <span class="report-title">{{ t('aiAssistant.diagnosticReport') }}</span>
            <span v-if="reportStreaming" class="report-status streaming">
              <span class="typing-dots"><span></span><span></span><span></span></span>
            </span>
          </div>
          <div class="report-content" v-html="renderMarkdown(reportText)"></div>
          <div v-if="reportStreaming && !reportText" class="report-loading">
            <span class="spinner small"></span>
            <span>{{ t('aiAssistant.generatingReport') }}</span>
          </div>
        </div>

        <!-- 对话区域：追问消息 -->
        <div v-if="followUpSteps.length > 0" class="chat-section">
          <div
            v-for="step in followUpSteps"
            :key="'chat-' + step.id"
            class="chat-message"
          >
            <div class="chat-bubble user-bubble">
              <div class="chat-role">{{ t('aiAssistant.userMessage') }}</div>
              <div class="chat-text">{{ step.title }}</div>
            </div>
            <div v-if="step.status === 'running'" class="chat-bubble ai-bubble">
              <div class="chat-role">{{ t('aiAssistant.aiResponse') }}</div>
              <div class="chat-thinking"><span class="spinner small"></span> {{ t('aiAssistant.sending') }}</div>
            </div>
            <div v-else-if="step.status === 'completed' && step.result" class="chat-bubble ai-bubble">
              <div class="chat-role">{{ t('aiAssistant.aiResponse') }}</div>
              <div class="chat-text" v-html="renderMarkdown(step.result)"></div>
            </div>
            <div v-else-if="step.status === 'failed'" class="chat-bubble ai-bubble error-bubble">
              <div class="chat-role">{{ t('aiAssistant.aiResponse') }}</div>
              <div class="chat-text error-text">{{ step.error || t('aiAssistant.followUpFailed') }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入框 -->
      <div v-if="currentTask" class="input-area bottom-input">
        <div class="input-wrap">
          <input
            v-model="newQuery"
            type="text"
            class="task-input"
            :placeholder="t('aiAssistant.followUpPlaceholder')"
            :disabled="creating"
            @keyup.enter="onFollowUp"
          />
          <button class="send-btn" :disabled="!newQuery.trim() || creating" @click="onFollowUp">
            <svg v-if="!creating" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
            <span v-else class="spinner"></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { createAiTask, getAiTasks, getAiTaskDetail, deleteAiTask, followUpAiTask } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const { t } = useI18n()

const tasks = ref([])
const currentTaskId = ref(null)
const currentTask = ref(null)
const newQuery = ref('')
const creating = ref(false)
const expandedSteps = ref([])
const executionAreaRef = ref(null)
let pollTimer = null

// 报告流式状态
const reportText = ref('')
const reportStreaming = ref(false)
let streamAbortController = null

// 工具步骤（非 summary、非 followup）
const toolSteps = computed(() => {
  if (!currentTask.value || !currentTask.value.steps) return []
  return currentTask.value.steps.filter(s => s.step_type !== 'summary' && s.step_type !== 'followup')
})

// 追问步骤
const followUpSteps = computed(() => {
  if (!currentTask.value || !currentTask.value.steps) return []
  return currentTask.value.steps.filter(s => s.step_type === 'followup')
})

// 是否显示报告区域
const showReportArea = computed(() => {
  if (!currentTask.value) return false
  // 当所有工具步骤完成，或任务进入 awaiting_report / completed 状态
  const status = currentTask.value.status
  if (status === 'awaiting_report' || status === 'completed' || status === 'failed') {
    return toolSteps.value.length > 0 || reportText.value.length > 0
  }
  // 如果已有报告内容也显示
  if (reportText.value) return true
  return false
})

async function fetchTasks() {
  try {
    tasks.value = await getAiTasks()
  } catch (e) {
    console.error('获取任务列表失败', e)
  }
}

async function selectTask(taskId) {
  currentTaskId.value = taskId
  expandedSteps.value = []
  reportText.value = ''
  reportStreaming.value = false
  stopStream()
  try {
    currentTask.value = await getAiTaskDetail(taskId)
    // 如果任务已完成且 summary 步骤有结果，直接显示
    const summaryStep = currentTask.value.steps?.find(s => s.step_type === 'summary')
    if (summaryStep?.result && summaryStep?.status === 'completed') {
      reportText.value = summaryStep.result
    }
    startPolling()
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error('获取任务详情失败', e)
  }
}

function startNewTask() {
  currentTaskId.value = null
  currentTask.value = null
  newQuery.value = ''
  expandedSteps.value = []
  reportText.value = ''
  reportStreaming.value = false
  stopPolling()
  stopStream()
}

async function onCreateTask() {
  const query = newQuery.value.trim()
  if (!query || creating.value) return
  creating.value = true
  try {
    const result = await createAiTask(query)
    newQuery.value = ''
    await fetchTasks()
    await selectTask(result.task_id)
  } catch (e) {
    console.error('创建任务失败', e)
  } finally {
    creating.value = false
  }
}

async function onFollowUp() {
  const query = newQuery.value.trim()
  if (!query || creating.value || !currentTaskId.value) return
  creating.value = true
  try {
    await followUpAiTask(currentTaskId.value, query)
    newQuery.value = ''
    await selectTask(currentTaskId.value)
  } catch (e) {
    console.error('追问失败', e)
  } finally {
    creating.value = false
  }
}

async function onDeleteTask(task) {
  if (!confirm(t('aiAssistant.confirmDelete'))) return
  try {
    await deleteAiTask(task.id)
    if (currentTaskId.value === task.id) {
      currentTaskId.value = null
      currentTask.value = null
      stopPolling()
      stopStream()
    }
    await fetchTasks()
  } catch (e) {
    console.error('删除任务失败', e)
  }
}

function toggleStep(step) {
  if (step.status === 'completed' || step.status === 'failed') {
    const idx = expandedSteps.value.indexOf(step.id)
    if (idx === -1) {
      expandedSteps.value.push(step.id)
    } else {
      expandedSteps.value.splice(idx, 1)
    }
  }
}

function isStepExpanded(stepId) {
  return expandedSteps.value.includes(stepId)
}

function statusLabel(status) {
  const map = {
    pending: t('aiAssistant.taskPending'),
    planning: t('aiAssistant.taskRunning'),
    running: t('aiAssistant.taskRunning'),
    awaiting_report: t('aiAssistant.taskAwaitingReport'),
    completed: t('aiAssistant.taskCompleted'),
    failed: t('aiAssistant.taskFailed'),
  }
  return map[status] || status
}

function formatTime(dt) {
  if (!dt) return ''
  try {
    return formatDateTime(dt, { hour: true, minute: true })
  } catch {
    return dt
  }
}

function scrollToBottom() {
  if (executionAreaRef.value) {
    executionAreaRef.value.scrollTop = executionAreaRef.value.scrollHeight
  }
}

/**
 * 连接 SSE 流式获取报告
 */
async function startStreamReport(taskId) {
  if (reportStreaming.value) return

  // 如果已有完整报告，不重复请求
  const summaryStep = currentTask.value?.steps?.find(s => s.step_type === 'summary')
  if (summaryStep?.result && summaryStep?.status === 'completed') {
    reportText.value = summaryStep.result
    return
  }

  reportStreaming.value = true
  reportText.value = ''

  const token = localStorage.getItem('sql_monitor_token')
  streamAbortController = new AbortController()

  try {
    const resp = await fetch(`/api/ai/tasks/${taskId}/stream-report`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'text/event-stream',
      },
      signal: streamAbortController.signal,
    })

    if (!resp.ok) {
      reportText.value = '报告获取失败：' + resp.status
      reportStreaming.value = false
      return
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6).trim()
        if (!data) continue

        try {
          const parsed = JSON.parse(data)
          if (parsed.done) {
            reportStreaming.value = false
            // 刷新任务详情
            await fetchTasks()
            break
          }
          if (parsed.error) {
            reportText.value += `\n\n**错误：** ${parsed.error}`
            reportStreaming.value = false
            break
          }
          if (parsed.content) {
            reportText.value += parsed.content
            await nextTick()
            scrollToBottom()
          }
        } catch {
          // ignore parse errors
        }
      }
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      console.error('流式报告连接失败', e)
      reportText.value = '报告连接失败：' + (e.message || e)
    }
  } finally {
    reportStreaming.value = false
    streamAbortController = null
  }
}

function stopStream() {
  if (streamAbortController) {
    streamAbortController.abort()
    streamAbortController = null
  }
  reportStreaming.value = false
}

/**
 * Markdown → HTML 渲染（轻量实现）
 */
function renderMarkdown(text) {
  if (!text) return ''
  let html = text

  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre class="md-code-block"><code>${code.trim()}</code></pre>`
  })

  html = html.replace(/`([^`]+)`/g, '<code class="md-inline-code">$1</code>')

  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')

  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')

  html = html.replace(/^---+$/gm, '<hr/>')

  html = html.replace(/^(?:- (.+)\n?)+/gm, (match) => {
    const items = match.trim().split('\n').map(l => `<li>${l.replace(/^- /, '')}</li>`).join('')
    return `<ul>${items}</ul>`
  })

  html = html.replace(/^(?:\d+\. (.+)\n?)+/gm, (match) => {
    const items = match.trim().split('\n').map(l => `<li>${l.replace(/^\d+\. /, '')}</li>`).join('')
    return `<ol>${items}</ol>`
  })

  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')

  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  html = `<p>${html}</p>`
  html = html.replace(/<p>\s*<\/p>/g, '')

  return html
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (!currentTaskId.value) return
    try {
      const detail = await getAiTaskDetail(currentTaskId.value)
      currentTask.value = detail

      const idx = tasks.value.findIndex(t => t.id === detail.id)
      if (idx > -1) {
        tasks.value[idx].status = detail.status
      }

      // 当工具步骤全部完成，任务进入 awaiting_report 时，启动流式报告
      if (detail.status === 'awaiting_report' && !reportStreaming.value && !reportText.value) {
        stopPolling()
        startStreamReport(detail.id)
        return
      }

      // 如果任务已完成且 summary 有结果
      if (detail.status === 'completed') {
        const summaryStep = detail.steps?.find(s => s.step_type === 'summary')
        if (summaryStep?.result && !reportText.value) {
          reportText.value = summaryStep.result
        }
        stopPolling()
        await fetchTasks()
      }

      if (detail.status === 'failed') {
        stopPolling()
        await fetchTasks()
      }

      await nextTick()
      scrollToBottom()
    } catch {
      // ignore polling errors
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(() => {
  fetchTasks()
})

onBeforeUnmount(() => {
  stopPolling()
  stopStream()
})
</script>

<style scoped>
.ai-assistant {
  display: flex;
  height: calc(100vh - 152px);
  overflow: hidden;
  background: var(--bg-primary, #f5f6fa);
  border-radius: 8px;
}

/* ===== 左侧栏 ===== */
.task-sidebar {
  width: 220px;
  min-width: 220px;
  background: var(--bg-card, #fff);
  border-right: 1px solid var(--border-color, #e8ecf4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header { padding: 20px 16px 12px; }
.sidebar-title { margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary, #2c3e50); }

.new-task-btn {
  margin: 0 16px 12px;
  height: 36px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.new-task-btn:hover { background: #40a9ff; }

.task-list { flex: 1; overflow-y: auto; padding: 0 8px; }

.task-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  position: relative;
}
.task-card:hover { background: var(--bg-primary, #f5f6fa); }
.task-card.active { background: #e6f7ff; }
[data-theme='dark'] .task-card.active { background: rgba(24, 144, 255, 0.12); }

.task-card-content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.task-card-text { font-size: 13px; color: var(--text-primary, #2c3e50); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-card-time { font-size: 11px; color: var(--text-muted, #999); }

.task-status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.task-status-dot.status-pending { background: #d9d9d9; }
.task-status-dot.status-planning { background: #1890ff; }
.task-status-dot.status-running { background: #1890ff; }
.task-status-dot.status-awaiting-report { background: #faad14; }
.task-status-dot.status-completed { background: #52c41a; }
.task-status-dot.status-failed { background: #ff4d4f; }

.task-delete-btn {
  width: 20px; height: 20px; border: none; background: transparent;
  color: var(--text-muted, #999); font-size: 16px; cursor: pointer;
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; opacity: 0; transition: opacity 0.15s, background 0.15s;
}
.task-card:hover .task-delete-btn { opacity: 1; }
.task-delete-btn:hover { background: #fff1f0; color: #ff4d4f; }

.task-empty { text-align: center; padding: 40px 16px; color: var(--text-muted, #999); }
.task-empty p { margin: 0; font-size: 13px; }
.task-empty-hint { margin-top: 4px !important; font-size: 12px !important; opacity: 0.7; }

/* ===== 右侧主区域 ===== */
.task-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }

/* ===== 欢迎页 ===== */
.welcome-area { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; }
.welcome-icon { margin-bottom: 24px; }
.welcome-title { margin: 0 0 8px; font-size: 24px; font-weight: 600; color: var(--text-primary, #2c3e50); }
.welcome-subtitle { margin: 0 0 32px; font-size: 14px; color: var(--text-secondary, #666); }

/* ===== 输入框 ===== */
.input-area { width: 100%; max-width: 640px; margin: 0 auto; }

/* 底部输入框重置 .input-area 的居中样式,撑满主区域 */
.bottom-input.input-area { margin: 0; max-width: 100%; }

.input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-card, #fff); border: 1px solid var(--border-color, #e8ecf4);
  border-radius: 10px; padding: 6px 6px 6px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: border-color 0.2s, box-shadow 0.2s;
}
.input-wrap:focus-within { border-color: #1890ff; box-shadow: 0 2px 12px rgba(24,144,255,0.12); }

.task-input { flex: 1; border: none; outline: none; font-size: 14px; background: transparent; color: var(--text-primary, #2c3e50); min-width: 0; }
.task-input::placeholder { color: var(--text-muted, #999); }
.task-input:disabled { opacity: 0.6; }

.send-btn {
  width: 36px; height: 36px; border: none; background: #1890ff; color: #fff;
  border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: background 0.2s;
}
.send-btn:hover:not(:disabled) { background: #40a9ff; }
.send-btn:disabled { background: #d9d9d9; cursor: not-allowed; }

/* ===== 底部输入框 ===== */
.bottom-input {
  padding: 8px 24px 12px; max-width: 100%;
  border-top: 1px solid var(--border-color, #e8ecf4);
  background: var(--bg-card, #fff);
}

/* ===== 执行区域 ===== */
.execution-area { flex: 1; min-width: 0; overflow-y: auto; overflow-x: hidden; padding: 16px 24px; }

.execution-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; min-width: 0; }
.execution-title { margin: 0; font-size: 16px; font-weight: 600; color: var(--text-primary, #2c3e50); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.execution-status {
  display: inline-block; padding: 2px 10px; border-radius: 12px;
  font-size: 12px; font-weight: 500; white-space: nowrap;
}
.execution-status.status-pending { background: #f5f5f5; color: #8c8c8c; }
.execution-status.status-planning,
.execution-status.status-running { background: #e6f7ff; color: #1890ff; }
.execution-status.status-awaiting-report { background: #fff7e6; color: #faad14; }
.execution-status.status-completed { background: #f6ffed; color: #52c41a; }
.execution-status.status-failed { background: #fff1f0; color: #ff4d4f; }

/* ===== 思考/任务拆解区域 ===== */
.thinking-section { margin-bottom: 8px; }
.section-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600; color: var(--text-secondary, #666);
  text-transform: uppercase; letter-spacing: 0.5px;
}

/* ===== 工具步骤卡片（折叠） ===== */
.steps-section { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }

.step-card {
  background: var(--bg-card, #fff); border-radius: 6px;
  border: 1px solid var(--border-color, #e8ecf4);
  overflow: hidden; transition: border-color 0.2s;
}
.step-card.step-running { border-color: #1890ff; }
.step-card.step-completed { border-color: #d9f7be; }
.step-card.step-failed { border-color: #ffa39e; }

.step-header {
  display: flex; align-items: center; gap: 10px; padding: 8px 12px; cursor: default;
}
.step-card.step-completed .step-header,
.step-card.step-failed .step-header { cursor: pointer; }
.step-card.step-completed .step-header:hover,
.step-card.step-failed .step-header:hover { background: var(--bg-primary, #fafafa); }

.step-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-dot { display: block; width: 8px; height: 8px; border-radius: 50%; }
.step-dot.pending { background: #d9d9d9; }

.step-info { flex: 1; min-width: 0; }
.step-title { font-size: 13px; font-weight: 500; color: var(--text-primary, #2c3e50); }

.step-expand-icon { font-size: 10px; color: var(--text-muted, #999); flex-shrink: 0; }

.step-result {
  border-top: 1px solid var(--border-color, #e8ecf4);
  padding: 8px 12px 8px 42px;
  background: var(--bg-primary, #fafafa);
}

.result-content {
  font-size: 12px; line-height: 1.6; color: var(--text-primary, #2c3e50);
  word-break: break-word;
}
.result-content :deep(strong) { font-weight: 600; }
.result-content :deep(h1),
.result-content :deep(h2),
.result-content :deep(h3),
.result-content :deep(h4) { margin: 8px 0 4px; font-weight: 600; color: var(--text-primary, #2c3e50); }
.result-content :deep(h1) { font-size: 16px; }
.result-content :deep(h2) { font-size: 14px; }
.result-content :deep(h3) { font-size: 13px; }
.result-content :deep(h4) { font-size: 12px; }
.result-content :deep(ul),
.result-content :deep(ol) { margin: 4px 0; padding-left: 18px; }
.result-content :deep(li) { margin: 2px 0; }
.result-content :deep(blockquote) {
  margin: 6px 0; padding: 4px 10px; border-left: 3px solid #1890ff;
  background: #e6f7ff; border-radius: 0 4px 4px 0; color: #0958d9;
}
.result-content :deep(.md-code-block) {
  margin: 6px 0; padding: 8px 12px; background: #1e1e1e; color: #d4d4d4;
  border-radius: 6px; font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 11px; overflow-x: auto; white-space: pre;
}
.result-content :deep(.md-inline-code) {
  padding: 1px 4px; background: #f0f0f0; border-radius: 3px;
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 11px; color: #d4380d;
}
.result-content :deep(hr) { border: none; border-top: 1px solid var(--border-color, #e8ecf4); margin: 8px 0; }
.result-content :deep(a) { color: #1890ff; text-decoration: none; }

.step-error {
  border-top: 1px solid #ffa39e; padding: 8px 12px 8px 42px;
  background: #fff1f0; font-size: 12px; color: #cf1322;
}

/* ===== 诊断报告区域 ===== */
.report-section {
  background: var(--bg-card, #fff);
  border: 1px solid #d9f7be;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.report-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #f6ffed 0%, #e6f7ff 100%);
  border-bottom: 1px solid var(--border-color, #e8ecf4);
}
.report-title {
  font-size: 14px; font-weight: 600; color: var(--text-primary, #2c3e50);
}
.report-status.streaming { margin-left: auto; }

.typing-dots { display: inline-flex; gap: 3px; }
.typing-dots span {
  width: 6px; height: 6px; border-radius: 50%; background: #1890ff;
  animation: typing-bounce 1.4s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

.report-content {
  padding: 16px;
  font-size: 13px; line-height: 1.8; color: var(--text-primary, #2c3e50);
  word-break: break-word;
}
.report-content :deep(strong) { font-weight: 600; }
.report-content :deep(h1),
.report-content :deep(h2),
.report-content :deep(h3),
.report-content :deep(h4) { margin: 14px 0 8px; font-weight: 600; color: var(--text-primary, #2c3e50); }
.report-content :deep(h1) { font-size: 18px; }
.report-content :deep(h2) { font-size: 16px; }
.report-content :deep(h3) { font-size: 14px; }
.report-content :deep(h4) { font-size: 13px; }
.report-content :deep(p) { margin: 6px 0; }
.report-content :deep(ul),
.report-content :deep(ol) { margin: 8px 0; padding-left: 22px; }
.report-content :deep(li) { margin: 3px 0; }
.report-content :deep(blockquote) {
  margin: 10px 0; padding: 8px 14px; border-left: 3px solid #1890ff;
  background: #e6f7ff; border-radius: 0 6px 6px 0; color: #0958d9;
}
.report-content :deep(.md-code-block) {
  margin: 10px 0; padding: 12px 16px; background: #1e1e1e; color: #d4d4d4;
  border-radius: 8px; font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px; overflow-x: auto; white-space: pre;
}
.report-content :deep(.md-inline-code) {
  padding: 2px 6px; background: #f0f0f0; border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 12px; color: #d4380d;
}
.report-content :deep(hr) { border: none; border-top: 1px solid var(--border-color, #e8ecf4); margin: 14px 0; }
.report-content :deep(a) { color: #1890ff; text-decoration: none; }
.report-content :deep(a:hover) { text-decoration: underline; }

.report-loading {
  display: flex; align-items: center; gap: 8px;
  padding: 20px 16px; font-size: 13px; color: var(--text-muted, #999);
}

/* ===== 对话区域 ===== */
.chat-section {
  border-top: 1px solid var(--border-color, #e8ecf4);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message { display: flex; flex-direction: column; gap: 8px; }

.chat-bubble { max-width: 85%; }
.user-bubble { align-self: flex-end; }
.ai-bubble { align-self: flex-start; }

.chat-role {
  font-size: 11px; font-weight: 600; color: var(--text-muted, #999);
  margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.5px;
}
.user-bubble .chat-role { text-align: right; }

.chat-text {
  font-size: 13px; line-height: 1.7; color: var(--text-primary, #2c3e50);
  padding: 10px 14px; border-radius: 10px; word-break: break-word;
}
.user-bubble .chat-text {
  background: #1890ff; color: #fff; border-bottom-right-radius: 2px;
}
.ai-bubble .chat-text {
  background: var(--bg-card, #fff); border: 1px solid var(--border-color, #e8ecf4);
  border-bottom-left-radius: 2px;
}
.ai-bubble .chat-text :deep(strong) { font-weight: 600; }
.ai-bubble .chat-text :deep(ul),
.ai-bubble .chat-text :deep(ol) { margin: 4px 0; padding-left: 18px; }
.ai-bubble .chat-text :deep(li) { margin: 2px 0; }
.ai-bubble .chat-text :deep(blockquote) {
  margin: 6px 0; padding: 4px 10px; border-left: 3px solid #1890ff;
  background: #e6f7ff; border-radius: 0 4px 4px 0; font-size: 12px;
}
.ai-bubble .chat-text :deep(.md-code-block) {
  margin: 6px 0; padding: 8px 12px; background: #1e1e1e; color: #d4d4d4;
  border-radius: 6px; font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px; overflow-x: auto; white-space: pre;
}
.ai-bubble .chat-text :deep(.md-inline-code) {
  padding: 1px 4px; background: #f0f0f0; border-radius: 3px;
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 12px;
}

.error-bubble .chat-text { background: #fff1f0; border-color: #ffa39e; }
.error-text { color: #cf1322; }

.chat-thinking {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-muted, #999);
  padding: 10px 14px; background: var(--bg-card, #fff);
  border: 1px solid var(--border-color, #e8ecf4);
  border-radius: 10px; border-bottom-left-radius: 2px;
}

/* ===== Spinner ===== */
.spinner {
  display: inline-block; width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
.spinner.small {
  width: 16px; height: 16px; border-width: 2px;
  border-color: rgba(24,144,255,0.25); border-top-color: #1890ff;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== 滚动条 ===== */
.task-list::-webkit-scrollbar,
.execution-area::-webkit-scrollbar { width: 6px; }
.task-list::-webkit-scrollbar-track,
.execution-area::-webkit-scrollbar-track { background: transparent; }
.task-list::-webkit-scrollbar-thumb,
.execution-area::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 3px; }
.task-list::-webkit-scrollbar-thumb:hover,
.execution-area::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.2); }
</style>
