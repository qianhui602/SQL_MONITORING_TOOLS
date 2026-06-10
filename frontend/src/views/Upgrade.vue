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

      <!-- 未检测到 Git 仓库但项目正常 -->
      <div v-else-if="!gitStatus.is_git_repo" class="card-body">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">项目状态</span>
            <span class="info-value" :class="gitStatus.project_ready ? 'text-ok' : 'text-warn'">
              <span class="status-dot" :class="gitStatus.project_ready ? 'dot-ok' : 'dot-warn'"></span>
              {{ gitStatus.project_ready ? '项目文件完整' : '项目文件不完整' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">当前版本</span>
            <span class="info-value">v{{ gitStatus.current_version }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">后端服务</span>
            <span class="info-value" :class="gitStatus.has_backend ? 'text-ok' : 'text-warn'">
              <span class="status-dot" :class="gitStatus.has_backend ? 'dot-ok' : 'dot-warn'"></span>
              {{ gitStatus.has_backend ? '已部署' : '未找到' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">前端服务</span>
            <span class="info-value" :class="gitStatus.has_frontend ? 'text-ok' : 'text-warn'">
              <span class="status-dot" :class="gitStatus.has_frontend ? 'dot-ok' : 'dot-warn'"></span>
              {{ gitStatus.has_frontend ? '已部署' : '未找到' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">升级方式</span>
            <span class="info-value">{{ gitStatus.hint || '通过 Release ZIP 更新' }}</span>
          </div>
        </div>
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

    <!-- ZIP 文件上传升级 -->
    <div class="card">
      <div class="card-header">
        <svg class="card-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <h3>ZIP 上传升级</h3>
      </div>

      <div class="card-body">
        <p class="upload-hint">从 GitHub Release 下载 ZIP 文件后，手动上传进行升级。支持 <code>.zip</code> 格式，最大 100MB。</p>

        <div
          class="upload-zone"
          :class="{ 'drag-over': isDragging, 'uploading': zipUploading }"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDropZip"
          @click="triggerFileInput"
        >
          <input
            ref="zipFileInput"
            type="file"
            accept=".zip"
            style="display:none"
            @change="onZipFileSelect"
          />
          <div v-if="zipUploading" class="upload-loading">
            <div class="spinner-sm"></div>
            <span>上传并升级中...</span>
          </div>
          <div v-else class="upload-content">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p v-if="zipFile">{{ zipFile.name }} ({{ formatFileSize(zipFile.size) }})</p>
            <p v-else>点击或拖拽 ZIP 文件到此处</p>
            <p class="upload-sub">从 <a href="https://github.com/qianhui602/SQL_MONITORING_TOOLS/releases" target="_blank" @click.stop>GitHub Releases</a> 下载最新版本</p>
          </div>
        </div>

        <button
          v-if="zipFile && !zipUploading"
          class="btn btn-upgrade"
          @click="onUploadZip"
          :disabled="zipUploading"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          开始上传升级
        </button>

        <!-- 上传升级日志 -->
        <div v-if="zipLogs.length > 0" class="log-panel">
          <div class="log-header">
            <span>升级日志</span>
            <span class="log-status" v-if="zipSuccess === true">✓ 完成</span>
            <span class="log-status log-status-fail" v-else-if="zipSuccess === false">✗ 失败</span>
          </div>
          <div class="log-content">
            <div
              v-for="(line, i) in zipLogs" :key="i"
              class="log-line"
              :class="{
                'log-success': line.includes('✓'),
                'log-error': line.includes('✗'),
                'log-info': line.includes('!')
              }"
            >{{ line }}</div>
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
import { checkUpgrade, getUpgradeGitStatus, applyUpgrade, uploadZipUpgrade } from '@/api'

const checking = ref(false)
const checkingGit = ref(false)
const loadingVersion = ref(true)
const loadingGit = ref(true)
const upgrading = ref(false)
const upgradeStep = ref(0)
const upgradeSuccess = ref(null)
const logRef = ref(null)

// ZIP 上传相关
const zipFileInput = ref(null)
const zipFile = ref(null)
const isDragging = ref(false)
const zipUploading = ref(false)
const zipLogs = ref([])
const zipSuccess = ref(null)

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
  current_version: '0.0.0',
  project_ready: false,
  has_backend: false,
  has_frontend: false,
  has_docker_compose: false,
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
      if (data.logs.some(l => l.includes('步骤 4'))) upgradeStep.value = 3
    }
    upgradeSuccess.value = data.success
    if (data.success) {
      upgradeStep.value = 4
    }
    await nextTick()
    if (logRef.value) {
      logRef.value.scrollTop = logRef.value.scrollHeight
    }
  } catch (e) {
    upgradeSuccess.value = false
    upgradeLogs.value.push(`[${new Date().toLocaleTimeString()}] ✗ 升级请求失败: ${e.message}`)
  } finally {
    upgrading.value = false
  }
}

// ZIP 上传相关
function triggerFileInput() {
  if (!zipUploading.value) {
    zipFileInput.value?.click()
  }
}

function onZipFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) {
    zipFile.value = file
  }
}

function onDropZip(e) {
  isDragging.value = false
  const file = e.dataTransfer.files?.[0]
  if (file && file.name.endsWith('.zip')) {
    zipFile.value = file
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function onUploadZip() {
  if (!zipFile.value) return

  zipUploading.value = true
  zipLogs.value = []
  zipSuccess.value = null

  try {
    const data = await uploadZipUpgrade(zipFile.value)
    if (data.logs) {
      zipLogs.value = data.logs
    }
    zipSuccess.value = data.success
  } catch (e) {
    zipSuccess.value = false
    zipLogs.value.push(`[${new Date().toLocaleTimeString()}] ✗ 上传失败: ${e.message}`)
  } finally {
    zipUploading.value = false
  }
}

// 初始化加载
onCheckVersion()
onCheckGitStatus()
</script>

<style scoped>
.upgrade-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  flex: 1;
}

.card-icon {
  color: #666;
}

.card-body {
  padding: 20px;
}

/* Badge */
.badge {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
}
.badge-update { background: #e6f7ff; color: #1890ff; }
.badge-ok { background: #f6ffed; color: #52c41a; }
.badge-warn { background: #fff7e6; color: #fa8c16; }
.badge-loading { background: #f5f5f5; color: #999; }

/* Version Compare */
.version-compare {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 20px 0;
}

.version-block {
  text-align: center;
  padding: 16px 32px;
  border-radius: 10px;
  background: #fafafa;
}

.version-block.current {
  border: 1px solid #e8e8e8;
}

.version-block.has-update {
  border: 2px solid #52c41a;
  background: #f6ffed;
}

.version-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 6px;
}

.version-number {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.version-number.unknown {
  color: #ccc;
}

.version-arrow {
  color: #bbb;
}

/* Release Notes */
.release-notes-block {
  margin-top: 16px;
}

.block-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.release-notes-content {
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

/* Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-top: 12px;
}
.status-error { background: #fff2f0; color: #ff4d4f; border: 1px solid #ffccc7; }

/* Release Link */
.release-link {
  margin-top: 12px;
}
.release-link a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #1890ff;
  font-size: 13px;
  text-decoration: none;
}
.release-link a:hover { text-decoration: underline; }

/* Info Grid */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #666;
  font-size: 14px;
  min-width: 90px;
}

.info-value {
  font-size: 14px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-value.mono {
  font-family: 'SF Mono', monospace;
  font-size: 12px;
  word-break: break-all;
}

.info-value.small {
  font-size: 12px;
}

.text-ok { color: #52c41a; }
.text-warn { color: #fa8c16; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.dot-ok { background: #52c41a; }
.dot-warn { background: #fa8c16; }

/* Upload Zone */
.upload-hint {
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
}

.upload-zone {
  border: 2px dashed #d9d9d9;
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-zone:hover, .upload-zone.drag-over {
  border-color: #1890ff;
  background: #f0f5ff;
}

.upload-zone.uploading {
  cursor: default;
  border-color: #1890ff;
  background: #f0f5ff;
}

.upload-content p {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

.upload-sub {
  font-size: 12px !important;
  color: #999 !important;
}

.upload-sub a {
  color: #1890ff;
  text-decoration: none;
}

.upload-sub a:hover {
  text-decoration: underline;
}

.upload-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #1890ff;
  font-size: 14px;
}

/* Buttons */
.btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-outline {
  background: #fff;
  border: 1px solid #d9d9d9;
  color: #666;
}

.btn-outline:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-upgrade {
  background: #1890ff;
  color: #fff;
  margin-top: 16px;
}

.btn-upgrade:hover {
  background: #40a9ff;
}

.btn-upgrade:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

/* Upgrade Steps */
.upgrade-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 16px 0;
}

.step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #eee;
  min-width: 160px;
}

.step-active {
  background: #e6f7ff;
  border-color: #91d5ff;
}

.step-completed {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.step-indicator {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #d9d9d9;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-active .step-indicator {
  background: #1890ff;
}

.step-completed .step-indicator {
  background: #52c41a;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.step-desc {
  font-size: 12px;
  color: #999;
}

.step-connector {
  width: 30px;
  height: 2px;
  background: #eee;
  flex-shrink: 0;
}

.step-connector.active {
  background: #52c41a;
}

/* Warning */
.upgrade-warning {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  margin-top: 16px;
  font-size: 13px;
  color: #ad6800;
}

/* Log Panel */
.log-panel {
  margin-top: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #fafafa;
  border-bottom: 1px solid #eee;
  font-size: 13px;
}

.log-status {
  color: #52c41a;
  font-weight: 500;
}

.log-status-fail {
  color: #ff4d4f;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px 14px;
  font-family: 'SF Mono', monospace;
  font-size: 12px;
  line-height: 1.8;
  background: #1e1e1e;
  color: #d4d4d4;
}

.log-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-success { color: #4ec9b0; }
.log-error { color: #f44747; }
.log-info { color: #dcdcaa; }

/* Skeleton */
.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Spinner */
.spinner-sm {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.btn-outline .spinner-sm {
  border-color: rgba(0,0,0,0.1);
  border-top-color: #1890ff;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
