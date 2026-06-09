<template>
  <div class="upgrade-page">
    <div class="page-header">
      <h2>在线升级</h2>
    </div>

    <!-- 当前版本 -->
    <div class="card">
      <div class="card-header">
        <h3>版本信息</h3>
      </div>
      <div class="card-body version-info">
        <div class="version-row">
          <span class="label">当前版本</span>
          <span class="value version-current">v{{ versionData.current_version }}</span>
        </div>
        <div class="version-row" v-if="versionData.latest_version">
          <span class="label">最新版本</span>
          <span class="value" :class="{ 'has-update': versionData.has_update }">
            v{{ versionData.latest_version }}
            <span v-if="versionData.has_update" class="update-badge">有新版本</span>
          </span>
        </div>
        <div class="version-row" v-if="versionData.release_notes">
          <span class="label">更新说明</span>
          <span class="value release-notes">{{ versionData.release_notes }}</span>
        </div>
        <div class="version-row" v-if="versionData.error">
          <span class="label">检测状态</span>
          <span class="value error-text">{{ versionData.error }}</span>
        </div>
        <div class="version-actions">
          <button class="btn btn-outline" @click="onCheckVersion" :disabled="checking">
            {{ checking ? '检查中...' : '检查更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Git 仓库状态 -->
    <div class="card">
      <div class="card-header">
        <h3>Git 仓库状态</h3>
      </div>
      <div class="card-body">
        <div v-if="!gitStatus.is_git_repo" class="empty-state">
          <p>未检测到 Git 仓库</p>
          <p class="hint">请先在服务器上初始化 Git 仓库并配置远程地址</p>
        </div>
        <template v-else>
          <div class="info-row">
            <span class="label">远程仓库</span>
            <span class="value mono">{{ gitStatus.remote_url || '未设置' }}</span>
          </div>
          <div class="info-row">
            <span class="label">当前分支</span>
            <span class="value">{{ gitStatus.branch }}</span>
          </div>
          <div class="info-row">
            <span class="label">最近提交</span>
            <span class="value mono small">{{ gitStatus.last_commit }}</span>
          </div>
          <div class="info-row">
            <span class="label">未提交变更</span>
            <span class="value" :class="gitStatus.has_uncommitted ? 'warn-text' : 'ok-text'">
              {{ gitStatus.has_uncommitted ? '存在未提交变更' : '工作区干净' }}
            </span>
          </div>
          <div class="info-row">
            <span class="label">落后远程</span>
            <span class="value">{{ gitStatus.behind_remote }} 个提交</span>
          </div>
        </template>
        <div class="version-actions">
          <button class="btn btn-outline" @click="onCheckGitStatus" :disabled="checkingGit">
            {{ checkingGit ? '检查中...' : '刷新状态' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 执行升级 -->
    <div class="card">
      <div class="card-header">
        <h3>执行升级</h3>
      </div>
      <div class="card-body">
        <div class="upgrade-warning">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>升级期间服务可能短暂不可用，建议在业务低峰期执行。</span>
        </div>

        <div class="version-actions">
          <button
            class="btn btn-upgrade"
            @click="onApplyUpgrade"
            :disabled="upgrading || !gitStatus.is_git_repo"
          >
            <span v-if="upgrading" class="btn-spinner"></span>
            {{ upgrading ? '升级中...' : '开始升级' }}
          </button>
        </div>

        <!-- 升级日志 -->
        <div v-if="upgradeLogs.length > 0" class="log-panel">
          <div class="log-header">升级日志</div>
          <div class="log-content" ref="logRef">
            <div v-for="(line, i) in upgradeLogs" :key="i" class="log-line"
              :class="{ 'log-success': line.includes('✓'), 'log-error': line.includes('失败') || line.includes('✗') }">
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
const upgrading = ref(false)
const logRef = ref(null)
const versionData = ref({ current_version: '0.0.0', latest_version: '', has_update: false })
const gitStatus = ref({ is_git_repo: false })
const upgradeLogs = ref([])

async function onCheckVersion() {
  checking.value = true
  try {
    const data = await checkUpgrade()
    versionData.value = data
  } catch (e) {
    versionData.value = { current_version: '0.0.0', latest_version: '', has_update: false, error: e.message }
  } finally {
    checking.value = false
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
  }
}

async function onApplyUpgrade() {
  if (!confirm('确定要执行升级吗？升级期间服务可能短暂不可用。')) return

  upgrading.value = true
  upgradeLogs.value = []

  try {
    const data = await applyUpgrade()
    if (data.logs) {
      upgradeLogs.value = data.logs
    }
    if (!data.success) {
      upgradeLogs.value.push(`[错误] ${data.error}`)
    }
  } catch (e) {
    upgradeLogs.value.push(`[错误] ${e.message}`)
  } finally {
    upgrading.value = false
    nextTick(() => {
      if (logRef.value) {
        logRef.value.scrollTop = logRef.value.scrollHeight
      }
    })
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
  margin-bottom: 20px;
}
.page-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.card {
  background: var(--bg-card);
  border-radius: 8px;
  box-shadow: var(--shadow);
  margin-bottom: 20px;
  overflow: hidden;
}
.card-header {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color);
}
.card-header h3 {
  margin: 0;
  font-size: 15px;
  color: var(--text-primary);
}
.card-body {
  padding: 20px;
}

.version-info, .info-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}
.info-row:last-child,
.version-row:last-child {
  border-bottom: none;
}

.label {
  width: 120px;
  flex-shrink: 0;
  font-size: 13px;
  color: var(--text-muted);
}
.value {
  font-size: 14px;
  color: var(--text-primary);
}
.version-current {
  font-weight: 600;
  font-size: 18px;
  color: #1890ff;
}
.has-update {
  color: #52c41a;
  font-weight: 500;
}
.update-badge {
  display: inline-block;
  background: #ff4d4f;
  color: #fff;
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
  margin-left: 8px;
}
.error-text { color: #ff4d4f; }
.ok-text { color: #52c41a; }
.warn-text { color: #fa8c16; }

.release-notes {
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  max-height: 80px;
  overflow-y: auto;
  flex: 1;
}

.mono { font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 13px; }
.small { font-size: 12px; }

.empty-state {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
}
.empty-state p { margin: 4px 0; }
.hint { font-size: 12px; }

.version-actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
}

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
  opacity: 0.6;
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
}
.btn-upgrade:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.35);
  transform: translateY(-1px);
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.upgrade-warning {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 6px;
  color: #d46b08;
  font-size: 13px;
}
[data-theme='dark'] .upgrade-warning {
  background: rgba(250, 140, 22, 0.1);
  border-color: rgba(250, 140, 22, 0.3);
  color: #fa8c16;
}

.log-panel {
  margin-top: 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}
.log-header {
  padding: 8px 14px;
  background: var(--bg-primary);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}
.log-content {
  padding: 12px 14px;
  max-height: 300px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Cascadia Code', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.8;
}
.log-line.log-success { color: #4ecb71; }
.log-line.log-error { color: #f44747; }
</style>
