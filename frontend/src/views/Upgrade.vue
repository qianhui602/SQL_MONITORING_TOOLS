<template>
  <div class="upgrade-page">
    <div class="page-header">
      <h2>在线升级</h2>
      <div class="header-actions">
        <button class="btn btn-outline" @click="onCheckVersion" :disabled="checking">
          <span v-if="checking" class="spinner-sm"></span>
          {{ checking ? '检测中...' : '检测版本' }}
        </button>
        <button class="btn btn-outline" @click="onCheckGitStatus" :disabled="checkingGit">
          <span v-if="checkingGit" class="spinner-sm"></span>
          {{ checkingGit ? '检测中...' : '刷新状态' }}
        </button>
      </div>
    </div>

    <!-- 版本信息面板 -->
    <div class="card">
      <div class="card-header">
        <svg class="card-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
        </svg>
        <h3>版本信息</h3>
        <div v-if="versionData.has_update" class="badge badge-update">有新版本</div>
        <div v-else-if="versionData.error" class="badge badge-warn">检测异常</div>
      </div>

      <!-- 加载骨架 -->
      <div v-if="loadingVersion" class="card-body">
        <div class="skeleton-line" style="width:60%"></div>
        <div class="skeleton-line" style="width:40%"></div>
        <div class="skeleton-line" style="width:80%"></div>
      </div>

      <div v-else class="card-body">
        <!-- 版本对比 -->
        <div class="version-compare">
          <div class="version-block current">
            <div class="version-label">当前版本</div>
            <div class="version-number">v{{ versionData.current_version }}</div>
          </div>
          <div class="version-arrow">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M13 5l7 7-7 7"/>
            </svg>
          </div>
          <div class="version-block" :class="versionData.has_update ? 'latest has-update' : 'latest'">
            <div class="version-label">最新版本</div>
            <div class="version-number" v-if="versionData.latest_version">
              v{{ versionData.latest_version }}
            </div>
            <div class="version-number unknown" v-else>--</div>
          </div>
        </div>

        <!-- 更新说明 -->
        <div v-if="versionData.release_notes" class="release-notes-block">
          <div class="block-label">更新说明</div>
          <pre class="release-notes-content">{{ versionData.release_notes }}</pre>
        </div>

        <!-- 错误/信息提示 -->
        <div v-if="versionData.error" class="status-bar status-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ versionData.error }}</span>
        </div>

        <!-- 版本发布链接 -->
        <div v-if="versionData.release_url" class="release-link">
          <a :href="versionData.release_url" target="_blank" rel="noopener">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            在 GitHub 上查看发布页
          </a>
        </div>
      </div>
    </div>

    <!-- Git 仓库状态 -->
    <div class="card">
      <div class="card-header">
        <svg class="card-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 12A10 10 0 1 1 12 2a10 10 0 0 1 10 10z"/><path d="M12 6v6l4 2"/>
        </svg>
        <h3>Git 仓库状态</h3>
        <div v-if="loadingGit" class="badge badge-loading">检测中...</div>
        <div v-else-if="gitStatus.is_git_repo" class="badge badge-ok">就绪</div>
        <div v-else class="badge badge-warn">未就绪</div>
      </div>

      <div v-if="loadingGit" class="card-body">
        <div class="skeleton-line" style="width:70%"></div>
        <div class="skeleton-line" style="width:50%"></div>
        <div class="skeleton-line" style="width:30%"></div>
      </div>

      <!-- 未检测到 Git 仓库 -->
      <div v-else-if="!gitStatus.is_git_repo" class="card-body">
        <div class="empty-state-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
          </svg>
        </div>
        <p class="empty-title">未检测到 Git 仓库</p>
        <p class="empty-desc">{{ gitStatus.error }}</p>
        <p v-if="gitStatus.hint" class="empty-hint">{{ gitStatus.hint }}</p>
      </div>

      <div v-else class="card-body">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">远程仓库</span>
            <span class="info-value mono">{{ gitStatus.remote_url || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">当前分支</span>
            <span class="info-value">{{ gitStatus.branch }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最近提交</span>
            <span class="info-value mono small">{{ gitStatus.last_commit }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">工作区状态</span>
            <span class="info-value" :class="gitStatus.has_uncommitted ? 'text-warn' : 'text-ok'">
              <span class="status-dot" :class="gitStatus.has_uncommitted ? 'dot-warn' : 'dot-ok'"></span>
              {{ gitStatus.has_uncommitted ? '存在未提交变更' : '工作区干净' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">落后远程</span>
            <span class="info-value">{{ gitStatus.behind_remote }} 个提交</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 执行升级 -->
    <div class="card">
      <div class="card-header">
        <svg class="card-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
        </svg>
        <h3>执行升级</h3>
        <div v-if="upgrading" class="badge badge-loading">升级中...</div>
      </div>

      <div class="card-body">
        <!-- 升级流程步骤示意 -->
        <div class="upgrade-steps">
          <div class="step" :class="stepState(0)">
            <div class="step-indicator">
              <span v-if="upgradeStep > 0">✓</span>
              <span v-else>1</span>
            </div>
            <div class="step-content">
              <div class="step-title">拉取代码</div>
              <div class="step-desc">从 Git 远程仓库拉取最新代码</div>
            </div>
          </div>
          <div class="step-connector" :class="{ active: upgradeStep > 1 }"></div>
          <div class="step" :class="stepState(1)">
            <div class="step-indicator">
              <span v-if="upgradeStep > 1">✓</span>
              <span v-else>2</span>
            </div>
            <div class="step-content">
              <div class="step-title">构建镜像</div>
              <div class="step-desc">使用最新代码构建 Docker 镜像</div>
            </div>
          </div>
          <div class="step-connector" :class="{ active: upgradeStep > 2 }"></div>
          <div class="step" :class="stepState(2)">
            <div class="step-indicator">
              <span v-if="upgradeStep > 2">✓</span>
              <span v-else>3</span>
            </div>
            <div class="step-content">
              <div class="step-title">重启服务</div>
              <div class="step-desc">使用新镜像重新启动所有服务</div>
            </div>
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="upgrade-warning">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>升级期间服务可能短暂不可用，建议在业务低峰期执行。</span>
        </div>

        <!-- 执行按钮 -->
        <button
          class="btn btn-upgrade"
          @click="onApplyUpgrade"
          :disabled="upgrading || !gitStatus.is_git_repo"
        >
          <span v-if="upgrading" class="spinner-sm"></span>
          {{ upgrading ? '升级中...' : '开始升级' }}
        </button>

        <!-- 升级日志 -->
        <div v-if="upgradeLogs.length > 0" class="log-panel">
          <div class="log-header">
            <span>升级日志</span>
            <span class="log-status" v-if="upgradeSuccess === true">✓ 完成</span>
            <span class="log-status log-status-fail" v-else-if="upgradeSuccess === false">✗ 失败</span>
          </div>
          <div class="log-content" ref="logRef">
            <div
              v-for="(line, i) in upgradeLogs" :key="i"
              class="log-line"
              :class="{
                'log-success': line.includes('✓'),
                'log-error': line.includes('✗'),
                'log-info': line.includes('!')
              }"
            >
              {{ line }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { checkUpgrade, getUpgradeGitStatus, applyUpgrade } from '@/api'

const checking = ref(false)
const checkingGit = ref(false)
const loadingVersion = ref(true)
const loadingGit = ref(true)
const upgrading = ref(false)
const upgradeStep = ref(0)
const upgradeSuccess = ref(null)
const logRef = ref(null)

const versionData = ref({
  current_version: '0.0.0',
  latest_version: '',
  has_update: false,
  release_url: '',
  release_notes: '',
  error: '',
  upgrade_enabled: true,
})

const gitStatus = ref({
  is_git_repo: false,
  remote_url: '',
  branch: '',
  last_commit: '',
  has_uncommitted: false,
  behind_remote: 0,
  error: '',
  hint: '',
})

const upgradeLogs = ref([])

function stepState(index) {
  if (upgradeStep > index + 1) return 'step-completed'
  if (upgradeStep === index + 1 && upgrading.value) return 'step-active'
  return ''
}

async function onCheckVersion() {
  checking.value = true
  try {
    const data = await checkUpgrade()
    versionData.value = data
  } catch (e) {
    versionData.value = {
      current_version: '0.0.0',
      latest_version: '',
      has_update: false,
      error: e.message,
    }
  } finally {
    checking.value = false
    loadingVersion.value = false
  }
}

async function onCheckGitStatus() {
  checkingGit.value = true
  try {
    const data = await getUpgradeGitStatus()
    gitStatus.value = data
  } catch (e) {
    gitStatus.value = { is_git_repo: false, error: e.message }
  } finally {
    checkingGit.value = false
    loadingGit.value = false
  }
}

async function onApplyUpgrade() {
  if (!confirm('确定要执行升级吗？升级期间服务可能短暂不可用。')) return

  upgrading.value = true
  upgradeStep.value = 0
  upgradeSuccess.value = null
  upgradeLogs.value = []

  try {
    const data = await applyUpgrade()
    if (data.logs) {
      upgradeLogs.value = data.logs
      // 根据日志推断当前步骤
      if (data.logs.some(l => l.includes('步骤 2'))) upgradeStep.value = 1
      if (data.logs.some(l => l.includes('步骤 3'))) upgradeStep.value = 2
      if (data.logs.some(l => l.includes('步骤 4') || l.includes('升级完成'))) upgradeStep.value = 3
    }
    upgradeSuccess.value = data.success
    if (!data.success) {
      upgradeLogs.value.push(`[错误] ${data.error}`)
    }
  } catch (e) {
    upgradeSuccess.value = false
    upgradeLogs.value.push(`[错误] ${e.message}`)
  } finally {
    upgrading.value = false
    // 升级完成后重新检查状态
    nextTick(() => {
      if (logRef.value) {
        logRef.value.scrollTop = logRef.value.scrollHeight
      }
    })
    onCheckVersion()
    onCheckGitStatus()
  }
}

// 页面加载时自动检查
onCheckVersion()
onCheckGitStatus()
</script>

<style scoped>
.upgrade-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* ========== Card ========== */
.card {
  background: var(--bg-card);
  border-radius: 10px;
  box-shadow: var(--shadow);
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  font-size: 15px;
  color: var(--text-primary);
  flex: 1;
}

.card-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.card-body {
  padding: 24px;
}

/* ========== Badges ========== */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-update {
  background: rgba(82, 196, 26, 0.12);
  color: #52c41a;
}

.badge-warn {
  background: rgba(250, 140, 22, 0.12);
  color: #fa8c16;
}

.badge-ok {
  background: rgba(82, 196, 26, 0.12);
  color: #52c41a;
}

.badge-loading {
  background: rgba(24, 144, 255, 0.12);
  color: #1890ff;
}

/* ========== Skeleton ========== */
.skeleton-line {
  height: 16px;
  background: var(--border-color);
  border-radius: 4px;
  margin-bottom: 12px;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* ========== Version Compare ========== */
.version-compare {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.version-block {
  text-align: center;
}

.version-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.version-number {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.version-block.current .version-number {
  color: var(--text-primary);
}

.version-block.latest .version-number {
  color: var(--text-muted);
}

.version-block.latest.has-update .version-number {
  color: #52c41a;
}

.version-block .version-number.unknown {
  color: var(--text-muted);
  font-weight: 400;
}

.version-arrow {
  color: var(--text-muted);
  display: flex;
  align-items: center;
}

/* ========== Release Notes ========== */
.release-notes-block {
  margin-bottom: 16px;
}

.block-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.release-notes-content {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

/* ========== Status Bar ========== */
.status-bar {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.status-error {
  background: rgba(245, 34, 45, 0.06);
  border: 1px solid rgba(245, 34, 45, 0.15);
  color: #f5222d;
}

.release-link {
  margin-top: 12px;
}

.release-link a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #1890ff;
  text-decoration: none;
}

.release-link a:hover {
  text-decoration: underline;
}

/* ========== Info Grid ========== */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 110px;
  flex-shrink: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.mono {
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}

.small {
  font-size: 12px;
  word-break: break-all;
}

.text-ok { color: #52c41a; }
.text-warn { color: #fa8c16; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-ok { background: #52c41a; }
.dot-warn { background: #fa8c16; }

/* ========== Empty State ========== */
.empty-state-icon {
  text-align: center;
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 12px;
}

.empty-title {
  text-align: center;
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.empty-desc {
  text-align: center;
  margin: 0 0 4px;
  font-size: 13px;
  color: var(--text-muted);
}

.empty-hint {
  text-align: center;
  margin: 8px 0 0;
  font-size: 13px;
  color: #fa8c16;
  padding: 8px 12px;
  background: rgba(250, 140, 22, 0.08);
  border-radius: 6px;
}

/* ========== Upgrade Steps ========== */
.upgrade-steps {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 8px;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
}

.step-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  background: var(--border-color);
  color: var(--text-muted);
  transition: all 0.3s;
}

.step-completed .step-indicator {
  background: #52c41a;
  color: #fff;
}

.step-active .step-indicator {
  background: #1890ff;
  color: #fff;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.2);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.2); }
  50% { box-shadow: 0 0 0 8px rgba(24, 144, 255, 0.1); }
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.step-connector {
  width: 24px;
  height: 2px;
  background: var(--border-color);
  margin-top: 15px;
  flex-shrink: 0;
  transition: background 0.3s;
}

.step-connector.active {
  background: #52c41a;
}

.step-completed .step-title {
  color: #52c41a;
}

/* ========== Buttons ========== */
.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-outline:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-upgrade {
  background: linear-gradient(135deg, #52c41a, #389e0d);
  color: #fff;
  font-weight: 500;
  padding: 10px 28px;
  font-size: 15px;
}

.btn-upgrade:hover:not(:disabled) {
  box-shadow: 0 4px 14px rgba(82, 196, 26, 0.4);
  transform: translateY(-1px);
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== Warning ========== */
.upgrade-warning {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(250, 140, 22, 0.08);
  border: 1px solid rgba(250, 140, 22, 0.2);
  border-radius: 8px;
  color: #d46b08;
  font-size: 13px;
  margin-bottom: 16px;
}

/* ========== Log Panel ========== */
.log-panel {
  margin-top: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--bg-primary);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.log-status {
  font-weight: 600;
  color: #52c41a;
  font-size: 12px;
}

.log-status-fail {
  color: #f5222d;
}

.log-content {
  padding: 12px 16px;
  max-height: 320px;
  overflow-y: auto;
  background: #1a1a2e;
  color: #d4d4d4;
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.8;
}

.log-line.log-success { color: #4ecb71; }
.log-line.log-error { color: #f44747; }
.log-line.log-info { color: #d4d4d4; }

/* ========== Dark Theme ========== */
[data-theme='dark'] .version-compare {
  background: #0f172a;
}

[data-theme='dark'] .release-notes-content {
  background: #0f172a;
}

[data-theme='dark'] .upgrade-steps {
  background: #0f172a;
}

[data-theme='dark'] .empty-state-icon {
  opacity: 0.3;
}
</style>
