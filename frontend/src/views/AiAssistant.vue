<template>
  <div class="ai-assistant">
    <!-- Left sidebar -->
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

    <!-- Right main area -->
    <div class="task-main">
      <!-- Welcome / Input area -->
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

      <!-- Task execution view -->
      <div v-else class="execution-area">
        <div class="execution-header">
          <h3 class="execution-title">{{ currentTask.query }}</h3>
          <span class="execution-status" :class="'status-' + currentTask.status">
            {{ statusLabel(currentTask.status) }}
          </span>
        </div>

        <!-- Steps list -->
        <div class="steps-list">
          <div
            v-for="step in currentTask.steps"
            :key="step.id"
            class="step-card"
            :class="['step-' + step.status, { expanded: expandedStep === step.id }]"
          >
            <div class="step-header" @click="toggleStep(step)">
              <div class="step-icon">
                <span v-if="step.status === 'pending'" class="step-dot pending"></span>
                <span v-else-if="step.status === 'running'" class="spinner small"></span>
                <svg v-else-if="step.status === 'completed'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#52c41a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <svg v-else-if="step.status === 'failed'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff4d4f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <div class="step-info">
                <span class="step-title">{{ step.title }}</span>
                <span class="step-desc">{{ step.description }}</span>
              </div>
              <span v-if="step.status === 'completed' || step.status === 'failed'" class="step-expand-icon">
                {{ expandedStep === step.id ? '▲' : '▼' }}
              </span>
            </div>
            <div v-if="expandedStep === step.id && step.result" class="step-result">
              <div class="result-content" v-html="renderMarkdown(step.result)"></div>
            </div>
            <div v-if="expandedStep === step.id && step.error" class="step-error">
              {{ step.error }}
            </div>
          </div>
        </div>
      </div>

      <!-- Input at bottom when viewing a task -->
      <div v-if="currentTask" class="input-area bottom-input">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { createAiTask, getAiTasks, getAiTaskDetail, deleteAiTask } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const { t } = useI18n()

const tasks = ref([])
const currentTaskId = ref(null)
const currentTask = ref(null)
const newQuery = ref('')
const creating = ref(false)
const expandedStep = ref(null)
let pollTimer = null

async function fetchTasks() {
  try {
    tasks.value = await getAiTasks()
  } catch (e) {
    console.error('获取任务列表失败', e)
  }
}

async function selectTask(taskId) {
  currentTaskId.value = taskId
  expandedStep.value = null
  try {
    currentTask.value = await getAiTaskDetail(taskId)
    startPolling()
  } catch (e) {
    console.error('获取任务详情失败', e)
  }
}

function startNewTask() {
  currentTaskId.value = null
  currentTask.value = null
  newQuery.value = ''
  expandedStep.value = null
  stopPolling()
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

async function onDeleteTask(task) {
  if (!confirm(t('aiAssistant.confirmDelete'))) return
  try {
    await deleteAiTask(task.id)
    if (currentTaskId.value === task.id) {
      currentTaskId.value = null
      currentTask.value = null
      stopPolling()
    }
    await fetchTasks()
  } catch (e) {
    console.error('删除任务失败', e)
  }
}

function toggleStep(step) {
  if (step.status === 'completed' || step.status === 'failed') {
    expandedStep.value = expandedStep.value === step.id ? null : step.id
  }
}

function statusLabel(status) {
  const map = {
    pending: t('aiAssistant.taskPending'),
    planning: t('aiAssistant.taskRunning'),
    running: t('aiAssistant.taskRunning'),
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

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
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
      if (detail.status === 'completed' || detail.status === 'failed') {
        stopPolling()
        await fetchTasks()
      }
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
})
</script>

<style scoped>
.ai-assistant {
  display: flex;
  height: calc(100vh - 56px);
  overflow: hidden;
  background: var(--bg-primary, #f5f6fa);
}

/* ===== Left Sidebar ===== */
.task-sidebar {
  width: 280px;
  min-width: 280px;
  background: var(--bg-card, #fff);
  border-right: 1px solid var(--border-color, #e8ecf4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px 16px 12px;
}

.sidebar-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
}

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

.new-task-btn:hover {
  background: #40a9ff;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

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

.task-card:hover {
  background: var(--bg-primary, #f5f6fa);
}

.task-card.active {
  background: #e6f7ff;
}

[data-theme='dark'] .task-card.active {
  background: rgba(24, 144, 255, 0.12);
}

.task-card-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-card-text {
  font-size: 13px;
  color: var(--text-primary, #2c3e50);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-card-time {
  font-size: 11px;
  color: var(--text-muted, #999);
}

.task-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.task-status-dot.status-pending { background: #d9d9d9; }
.task-status-dot.status-planning { background: #1890ff; }
.task-status-dot.status-running { background: #1890ff; }
.task-status-dot.status-completed { background: #52c41a; }
.task-status-dot.status-failed { background: #ff4d4f; }

.task-delete-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted, #999);
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s, background 0.15s;
}

.task-card:hover .task-delete-btn {
  opacity: 1;
}

.task-delete-btn:hover {
  background: #fff1f0;
  color: #ff4d4f;
}

.task-empty {
  text-align: center;
  padding: 40px 16px;
  color: var(--text-muted, #999);
}

.task-empty p {
  margin: 0;
  font-size: 13px;
}

.task-empty-hint {
  margin-top: 4px !important;
  font-size: 12px !important;
  opacity: 0.7;
}

/* ===== Right Main Area ===== */
.task-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* ===== Welcome Area ===== */
.welcome-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.welcome-icon {
  margin-bottom: 24px;
}

.welcome-title {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
}

.welcome-subtitle {
  margin: 0 0 32px;
  font-size: 14px;
  color: var(--text-secondary, #666);
}

/* ===== Input Area ===== */
.input-area {
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border-color, #e8ecf4);
  border-radius: 10px;
  padding: 6px 6px 6px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrap:focus-within {
  border-color: #1890ff;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.12);
}

.task-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  background: transparent;
  color: var(--text-primary, #2c3e50);
  min-width: 0;
}

.task-input::placeholder {
  color: var(--text-muted, #999);
}

.task-input:disabled {
  opacity: 0.6;
}

.send-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #1890ff;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.send-btn:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

/* ===== Bottom Input ===== */
.bottom-input {
  padding: 12px 24px 20px;
  max-width: 100%;
  border-top: 1px solid var(--border-color, #e8ecf4);
  background: var(--bg-card, #fff);
}

/* ===== Execution Area ===== */
.execution-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.execution-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.execution-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #2c3e50);
}

.execution-status {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.execution-status.status-pending {
  background: #f5f5f5;
  color: #8c8c8c;
}

.execution-status.status-planning,
.execution-status.status-running {
  background: #e6f7ff;
  color: #1890ff;
}

.execution-status.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.execution-status.status-failed {
  background: #fff1f0;
  color: #ff4d4f;
}

/* ===== Steps ===== */
.steps-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-card {
  background: var(--bg-card, #fff);
  border-radius: 8px;
  border: 1px solid var(--border-color, #e8ecf4);
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.step-card.step-running {
  border-color: #1890ff;
  box-shadow: 0 0 0 1px rgba(24, 144, 255, 0.1);
}

.step-card.step-completed {
  border-color: #b7eb8f;
}

.step-card.step-failed {
  border-color: #ffa39e;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  cursor: default;
}

.step-card.step-completed .step-header,
.step-card.step-failed .step-header {
  cursor: pointer;
}

.step-card.step-completed .step-header:hover,
.step-card.step-failed .step-header:hover {
  background: var(--bg-primary, #fafafa);
}

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-dot {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.step-dot.pending {
  background: #d9d9d9;
}

.step-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #2c3e50);
}

.step-desc {
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.step-expand-icon {
  font-size: 12px;
  color: var(--text-muted, #999);
  flex-shrink: 0;
  margin-left: 8px;
}

.step-result {
  border-top: 1px solid var(--border-color, #e8ecf4);
  padding: 14px 16px 14px 52px;
  background: var(--bg-primary, #fafafa);
}

.result-content {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary, #2c3e50);
  word-break: break-word;
}

.result-content :deep(strong) {
  font-weight: 600;
}

.step-error {
  border-top: 1px solid #ffa39e;
  padding: 14px 16px 14px 52px;
  background: #fff1f0;
  font-size: 13px;
  line-height: 1.6;
  color: #cf1322;
  word-break: break-word;
}

/* ===== Spinner ===== */
.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.spinner.small {
  width: 16px;
  height: 16px;
  border-width: 2px;
  border-color: rgba(24, 144, 255, 0.25);
  border-top-color: #1890ff;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Scrollbar ===== */
.task-list::-webkit-scrollbar,
.execution-area::-webkit-scrollbar {
  width: 6px;
}

.task-list::-webkit-scrollbar-track,
.execution-area::-webkit-scrollbar-track {
  background: transparent;
}

.task-list::-webkit-scrollbar-thumb,
.execution-area::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 3px;
}

.task-list::-webkit-scrollbar-thumb:hover,
.execution-area::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
