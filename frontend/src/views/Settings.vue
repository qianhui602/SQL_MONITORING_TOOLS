<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统配置</h2>
      <div class="header-actions">
        <button class="btn btn-test" @click="testConnection">测试 SQL Server 连接</button>
        <button class="btn btn-primary" @click="saveAll">保存并应用</button>
      </div>
    </div>

    <div v-if="message" :class="['message-toast', messageType === 'error' ? 'error' : 'success']">
      {{ message }}
    </div>

    <div class="config-sections">
      <!-- 品牌设置 -->
      <div class="config-section">
        <h3 class="section-title">品牌设置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">系统标题</label>
            <input
              type="text"
              v-model="brandTitle"
              class="config-input"
              placeholder="数据库监控平台"
            />
            <span class="config-desc">登录页和侧边栏显示的系统标题</span>
          </div>
          <div class="config-item">
            <label class="config-label">通知声音</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="notifSoundEnabled" class="toggle-input" @change="onNotifSoundToggle" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ notifSoundEnabled ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">有新通知时播放提示音</span>
          </div>
          <div class="config-item brand-logo-item">
            <label class="config-label">Logo 图片</label>
            <div class="logo-upload-area">
              <div class="logo-preview" v-if="logoPreviewUrl">
                <img :src="logoPreviewUrl" alt="Logo" class="logo-preview-img" />
              </div>
              <div class="logo-preview logo-placeholder" v-else>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#bfbfbf" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <span>暂无自定义 Logo</span>
              </div>
              <div class="logo-actions">
                <label class="btn btn-sm btn-upload">
                  <input type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" @change="onLogoUpload" hidden />
                  {{ logoPreviewUrl ? '更换 Logo' : '上传 Logo' }}
                </label>
                <button v-if="logoPreviewUrl" class="btn btn-sm btn-danger" @click="onDeleteLogo">恢复默认</button>
                <span class="config-desc">支持 PNG、JPG、SVG、WebP，建议尺寸 200x50px</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统设置 -->
      <div class="config-section">
        <h3 class="section-title">系统设置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">系统时区</label>
            <select v-model="timezone" class="config-select">
              <option value="Asia/Shanghai">Asia/Shanghai (UTC+8) - 北京时间</option>
              <option value="Asia/Tokyo">Asia/Tokyo (UTC+9) - 东京时间</option>
              <option value="America/New_York">America/New_York (UTC-5) - 纽约时间</option>
              <option value="America/Los_Angeles">America/Los_Angeles (UTC-8) - 洛杉矶时间</option>
              <option value="Europe/London">Europe/London (UTC+0) - 伦敦时间</option>
              <option value="Europe/Berlin">Europe/Berlin (UTC+1) - 柏林时间</option>
              <option value="UTC">UTC (UTC+0)</option>
            </select>
            <span class="config-desc">系统时区（用于日志和报表时间显示）</span>
          </div>
          <div class="config-item">
            <label class="config-label">数据保留天数</label>
            <input
              type="number"
              v-model="dataRetentionDays"
              class="config-input"
              min="7"
              max="3650"
              placeholder="90"
            />
            <span class="config-desc">超过此天数的监控数据将被自动清理（建议 90-365 天）</span>
          </div>
        </div>
      </div>

      <!-- SQL Server 连接配置 -->
      <div class="config-section">
        <h3 class="section-title">SQL Server 连接配置</h3>
        <div class="config-grid">
          <div class="config-item" v-for="item in mssqlConfigs" :key="item.key">
            <label class="config-label">{{ item.label }}</label>
            <input
              :type="item.password ? 'password' : 'text'"
              v-model="item.value"
              class="config-input"
              :placeholder="item.desc"
            />
            <span class="config-desc">{{ item.desc }}</span>
          </div>
        </div>
      </div>

      <!-- PostgreSQL 后台数据库 -->
      <div class="config-section">
        <h3 class="section-title">PostgreSQL 后台数据库</h3>
        <div class="config-grid">
          <div class="config-item" v-for="item in pgConfigs" :key="item.key">
            <label class="config-label">{{ item.label }}</label>
            <input
              :type="item.password ? 'password' : 'text'"
              v-model="item.value"
              class="config-input"
              :placeholder="item.desc"
            />
            <span class="config-desc">{{ item.desc }}</span>
          </div>
        </div>
      </div>

      <!-- 数据采集配置 -->
      <div class="config-section">
        <h3 class="section-title">数据采集配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">启用多实例采集</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="collectConfigs.mssql_instances_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ collectConfigs.mssql_instances_enabled ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">开启后从「实例管理」读取监控目标列表，关闭则使用上方 SQL Server 配置</span>
          </div>
          <div class="config-item">
            <label class="config-label">采集间隔（秒）</label>
            <input
              type="number"
              v-model="collectConfigs.scheduler_interval_seconds"
              class="config-input"
              min="10"
              max="3600"
              placeholder="60"
            />
            <span class="config-desc">数据采集频率，建议 30-120 秒</span>
          </div>
        </div>
      </div>

      <!-- 告警规则配置 -->
      <div class="config-section">
        <h3 class="section-title">告警规则配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">内存告警阈值（%）</label>
            <input
              type="number"
              v-model="alertConfigs.memory_alert_threshold_pct"
              class="config-input"
              min="50"
              max="100"
              placeholder="85"
            />
            <span class="config-desc">SQL Server 内存使用率超过此值触发告警</span>
          </div>
          <div class="config-item">
            <label class="config-label">内存告警持续时长（分钟）</label>
            <input
              type="number"
              v-model="alertConfigs.memory_alert_duration_minutes"
              class="config-input"
              min="1"
              max="60"
              placeholder="5"
            />
            <span class="config-desc">内存持续超过阈值超过此时长才触发告警</span>
          </div>
          <div class="config-item">
            <label class="config-label">死锁告警开关</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="alertConfigs.deadlock_alert_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ alertConfigs.deadlock_alert_enabled ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">检测到死锁事件时是否触发告警通知</span>
          </div>
          <div class="config-item">
            <label class="config-label">采集中断阈值（次）</label>
            <input
              type="number"
              v-model="alertConfigs.collection_interrupt_threshold"
              class="config-input"
              min="1"
              max="10"
              placeholder="3"
            />
            <span class="config-desc">连续多少次采集失败后触发中断告警</span>
          </div>
          <div class="config-item">
            <label class="config-label">告警冷却期（分钟）</label>
            <input
              type="number"
              v-model="alertConfigs.alert_cooldown_minutes"
              class="config-input"
              min="5"
              max="1440"
              placeholder="30"
            />
            <span class="config-desc">相同类型告警在此期间不重复发送</span>
          </div>
          <div class="config-item">
            <label class="config-label">收件人邮箱</label>
            <input
              type="text"
              v-model="alertConfigs.smtp_recipients"
              class="config-input"
              placeholder="user1@example.com, user2@example.com"
            />
            <span class="config-desc">告警邮件接收人，多个用逗号分隔</span>
          </div>
        </div>
      </div>

      <!-- 通知渠道配置 -->
      <div class="config-section">
        <h3 class="section-title">通知渠道配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">企业微信通知开关</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="notifyConfigs.wecom_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ notifyConfigs.wecom_enabled ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">是否通过企业微信机器人发送告警通知</span>
          </div>
          <div class="config-item">
            <label class="config-label">企业微信 Webhook URL</label>
            <input
              type="text"
              v-model="notifyConfigs.wecom_webhook_url"
              class="config-input"
              placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
            />
            <span class="config-desc">企业微信群机器人 Webhook 地址</span>
          </div>
        </div>
      </div>

      <!-- SMTP 邮件配置 -->
      <div class="config-section">
        <h3 class="section-title">SMTP 邮件配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">邮件告警开关</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="smtpConfigs.smtp_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ smtpConfigs.smtp_enabled ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">是否通过邮件发送告警通知和欢迎邮件</span>
          </div>
          <div class="config-item">
            <label class="config-label">SMTP 服务器</label>
            <input
              type="text"
              v-model="smtpConfigs.smtp_server"
              class="config-input"
              placeholder="smtp.example.com"
            />
            <span class="config-desc">SMTP 服务器地址</span>
          </div>
          <div class="config-item">
            <label class="config-label">SMTP 端口</label>
            <input
              type="number"
              v-model="smtpConfigs.smtp_port"
              class="config-input"
              placeholder="587"
            />
            <span class="config-desc">SMTP 端口（TLS 用 587，SSL 用 465）</span>
          </div>
          <div class="config-item">
            <label class="config-label">发件人账号</label>
            <input
              type="text"
              v-model="smtpConfigs.smtp_user"
              class="config-input"
              placeholder="alert@example.com"
            />
            <span class="config-desc">SMTP 登录账号 / 发件人邮箱</span>
          </div>
          <div class="config-item">
            <label class="config-label">发件人密码</label>
            <input
              type="password"
              v-model="smtpConfigs.smtp_password"
              class="config-input"
              placeholder="密码或授权码"
            />
            <span class="config-desc">SMTP 登录密码或应用授权码</span>
          </div>
        </div>
        <div style="margin-top: 12px;">
          <button class="btn btn-sm btn-test" @click="testSmtp" :disabled="smtpTesting">
            {{ smtpTesting ? '发送中...' : '发送测试邮件' }}
          </button>
          <span v-if="smtpTestResult" :class="['smtp-test-result', smtpTestOk ? 'ok' : 'fail']">
            {{ smtpTestResult }}
          </span>
        </div>
      </div>

      <!-- AI 模型配置 -->
      <div class="config-section">
        <h3 class="section-title">AI 模型配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">AI 提供商</label>
            <select v-model="aiConfigs.ai_provider" class="config-select" @change="onProviderChange">
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
              <option value="xiaomi">Xiaomi MiMo</option>
              <option value="custom">自定义（OpenAI 兼容）</option>
            </select>
            <span class="config-desc">选择 AI 服务提供商</span>
          </div>
          <div class="config-item">
            <label class="config-label">API 密钥</label>
            <input
              type="password"
              v-model="aiConfigs.ai_api_key"
              class="config-input"
              placeholder="API Key"
            />
            <span class="config-desc">{{ providerName }} API 密钥，用于 AI 死锁分析和报告生成</span>
          </div>
          <div class="config-item">
            <label class="config-label">AI 模型</label>
            <select v-if="currentModels.length" v-model="aiConfigs.ai_model" class="config-select">
              <option v-for="m in currentModels" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
            <input v-else v-model="aiConfigs.ai_model" class="config-input" placeholder="输入模型名称" />
            <span class="config-desc">选择或输入用于 AI 分析的模型</span>
          </div>
          <div class="config-item" v-if="aiConfigs.ai_provider === 'custom'">
            <label class="config-label">API Base URL</label>
            <input
              type="text"
              v-model="aiConfigs.ai_base_url"
              class="config-input"
              placeholder="https://your-api.com"
            />
            <span class="config-desc">自定义 API 地址（需兼容 OpenAI /v1/chat/completions 接口）</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import request, { getConfigs, updateConfig, getAiProviders, getLogoUrl, uploadLogo, deleteLogo } from '@/api'
import { setTimezone } from '@/utils/datetime'

const configList = ref([])
const originalConfigs = ref({})
const aiProviders = ref({})
const aiConfigs = reactive({
  ai_provider: 'deepseek',
  ai_api_key: '',
  ai_model: 'deepseek-v4-flash',
  ai_base_url: '',
})
const timezone = ref('Asia/Shanghai')
const dataRetentionDays = ref(90)
const message = ref('')
const messageType = ref('success')
const smtpTesting = ref(false)
const smtpTestResult = ref('')
const smtpTestOk = ref(false)
let toastTimer = null

// 品牌设置
const brandTitle = ref('数据库监控平台')
const logoPreviewUrl = ref('')
const logoCacheBust = ref('')
const notifSoundEnabled = ref(localStorage.getItem('notif_sound_enabled') !== 'false')

function onNotifSoundToggle() {
  localStorage.setItem('notif_sound_enabled', notifSoundEnabled.value)
}

// 数据采集配置
const collectConfigs = reactive({
  mssql_instances_enabled: 'false',
  scheduler_interval_seconds: '60',
})

// 告警规则配置
const alertConfigs = reactive({
  memory_alert_threshold_pct: '85',
  memory_alert_duration_minutes: '5',
  deadlock_alert_enabled: 'true',
  collection_interrupt_threshold: '3',
  alert_cooldown_minutes: '30',
  smtp_recipients: '',
})

// 通知渠道配置
const notifyConfigs = reactive({
  wecom_webhook_url: '',
  wecom_enabled: 'false',
})

// SMTP 配置
const smtpConfigs = reactive({
  smtp_enabled: 'false',
  smtp_server: '',
  smtp_port: '587',
  smtp_user: '',
  smtp_password: '',
})

const providerName = computed(() => {
  return aiProviders.value[aiConfigs.ai_provider]?.name || aiConfigs.ai_provider
})

const currentModels = computed(() => {
  return aiProviders.value[aiConfigs.ai_provider]?.models || []
})

function onProviderChange() {
  const models = currentModels.value
  if (models.length && !models.find(m => m.id === aiConfigs.ai_model)) {
    aiConfigs.ai_model = models[0].id
  }
  if (aiConfigs.ai_provider !== 'custom') {
    aiConfigs.ai_base_url = ''
  }
}

const mssqlConfigs = computed(() => {
  const map = {
    mssql_host: { label: '服务器地址', password: false },
    mssql_port: { label: '端口', password: false },
    mssql_user: { label: '账号', password: false },
    mssql_password: { label: '密码', password: true },
    mssql_database: { label: '数据库', password: false },
  }
  return filterAndMap(configList.value, map)
})

const pgConfigs = computed(() => {
  const map = {
    pg_host: { label: '服务器地址', password: false },
    pg_port: { label: '端口', password: false },
    pg_database: { label: '数据库名', password: false },
    pg_user: { label: '账号', password: false },
    pg_password: { label: '密码', password: true },
  }
  return filterAndMap(configList.value, map)
})

function filterAndMap(list, map) {
  return list
    .filter(cfg => map[cfg.config_key])
    .map(cfg => ({
      key: cfg.config_key,
      label: map[cfg.config_key].label,
      value: cfg.config_value,
      desc: cfg.description,
      password: map[cfg.config_key].password,
    }))
}

async function fetchConfigs() {
  try {
    const data = await getConfigs()
    configList.value = Array.isArray(data) ? data : (data.items || [])

    const find = key => configList.value.find(c => c.config_key === key)?.config_value || ''

    // 保存原始配置快照，用于对比变化
    const originals = {}
    configList.value.forEach(c => { originals[c.config_key] = c.config_value })
    originalConfigs.value = originals

    // AI 配置（兼容旧 deepseek_ 前缀）
    aiConfigs.ai_provider = find('ai_provider') || 'deepseek'
    aiConfigs.ai_api_key = find('ai_api_key') || find('deepseek_api_key') || ''
    aiConfigs.ai_model = find('ai_model') || find('deepseek_model') || 'deepseek-v4-flash'
    aiConfigs.ai_base_url = find('ai_base_url') || ''

    // 系统设置
    timezone.value = find('timezone') || 'Asia/Shanghai'
    dataRetentionDays.value = find('data_retention_days') || '90'
    setTimezone(timezone.value)

    // 采集配置
    collectConfigs.mssql_instances_enabled = find('mssql_instances_enabled') || 'false'
    collectConfigs.scheduler_interval_seconds = find('scheduler_interval_seconds') || '60'

    // 告警配置
    alertConfigs.memory_alert_threshold_pct = find('memory_alert_threshold_pct') || '85'
    alertConfigs.memory_alert_duration_minutes = find('memory_alert_duration_minutes') || '5'
    alertConfigs.deadlock_alert_enabled = find('deadlock_alert_enabled') || 'true'
    alertConfigs.collection_interrupt_threshold = find('collection_interrupt_threshold') || '3'
    alertConfigs.alert_cooldown_minutes = find('alert_cooldown_minutes') || '30'
    alertConfigs.smtp_recipients = find('smtp_recipients')

    // 通知配置
    notifyConfigs.wecom_webhook_url = find('wecom_webhook_url')
    notifyConfigs.wecom_enabled = find('wecom_enabled') || 'false'

    // SMTP 配置
    smtpConfigs.smtp_enabled = find('smtp_enabled') || 'false'
    smtpConfigs.smtp_server = find('smtp_server')
    smtpConfigs.smtp_port = find('smtp_port') || '587'
    smtpConfigs.smtp_user = find('smtp_user')
    smtpConfigs.smtp_password = find('smtp_password')
    smtpConfigs.smtp_recipients = find('smtp_recipients')

    // 品牌配置
    brandTitle.value = find('brand_title') || '数据库监控平台'

    // 检查是否有自定义 Logo
    checkLogoExists()
  } catch (e) {
    console.error('获取配置失败', e)
  }
}

async function saveAll() {
  const allConfigs = [
    ...mssqlConfigs.value,
    ...pgConfigs.value,
    { key: 'ai_provider', value: aiConfigs.ai_provider },
    { key: 'ai_api_key', value: String(aiConfigs.ai_api_key) },
    { key: 'ai_model', value: String(aiConfigs.ai_model) },
    { key: 'ai_base_url', value: String(aiConfigs.ai_base_url) },
    { key: 'timezone', value: timezone.value },
    { key: 'data_retention_days', value: String(dataRetentionDays.value) },
    { key: 'mssql_instances_enabled', value: collectConfigs.mssql_instances_enabled },
    { key: 'scheduler_interval_seconds', value: collectConfigs.scheduler_interval_seconds },
    { key: 'memory_alert_threshold_pct', value: alertConfigs.memory_alert_threshold_pct },
    { key: 'memory_alert_duration_minutes', value: alertConfigs.memory_alert_duration_minutes },
    { key: 'deadlock_alert_enabled', value: alertConfigs.deadlock_alert_enabled },
    { key: 'collection_interrupt_threshold', value: alertConfigs.collection_interrupt_threshold },
    { key: 'alert_cooldown_minutes', value: alertConfigs.alert_cooldown_minutes },
    { key: 'wecom_webhook_url', value: notifyConfigs.wecom_webhook_url },
    { key: 'wecom_enabled', value: notifyConfigs.wecom_enabled },
    { key: 'smtp_enabled', value: smtpConfigs.smtp_enabled },
    { key: 'smtp_server', value: smtpConfigs.smtp_server },
    { key: 'smtp_port', value: smtpConfigs.smtp_port },
    { key: 'smtp_user', value: smtpConfigs.smtp_user },
    { key: 'smtp_password', value: smtpConfigs.smtp_password },
    { key: 'smtp_recipients', value: alertConfigs.smtp_recipients },
    { key: 'brand_title', value: brandTitle.value },
  ]

  const changedConfigs = allConfigs.filter(cfg => {
    const oldVal = originalConfigs.value[cfg.key]
    const newVal = String(cfg.value)
    return oldVal !== newVal
  })

  if (changedConfigs.length === 0) {
    message.value = '没有检测到配置变更。'
    messageType.value = 'success'
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 3000)
    return
  }

  try {
    const results = await Promise.allSettled(
      changedConfigs.map(cfg => updateConfig(cfg.key, String(cfg.value)))
    )
    const failures = results
      .map((r, i) => r.status === 'rejected' ? changedConfigs[i].key : null)
      .filter(Boolean)
    if (failures.length > 0) {
      message.value = `保存失败: ${failures.join(', ')} 配置项保存异常`
      messageType.value = 'error'
      return
    }
    message.value = `保存成功！已更新 ${changedConfigs.length} 项配置，将在下一个采集周期自动应用。`
    messageType.value = 'success'
    setTimezone(timezone.value)
    await fetchConfigs()
  } catch (e) {
    message.value = '保存失败: ' + (e?.response?.data?.detail || e.message || '未知错误')
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 5000)
  }
}

async function testConnection() {
  message.value = '正在测试连接...'
  messageType.value = 'success'
  try {
    const host = mssqlConfigs.value.find(c => c.key === 'mssql_host')?.value
    const portRaw = mssqlConfigs.value.find(c => c.key === 'mssql_port')?.value || '1433'
    const user = mssqlConfigs.value.find(c => c.key === 'mssql_user')?.value
    const password = mssqlConfigs.value.find(c => c.key === 'mssql_password')?.value
    const database = mssqlConfigs.value.find(c => c.key === 'mssql_database')?.value || 'master'

    if (!host || !user) {
      message.value = '请填写服务器地址和账号'
      messageType.value = 'error'
      return
    }

    const result = await request.post('/config/test_mssql', {
      host,
      port: parseInt(portRaw, 10) || 1433,
      user,
      password,
      database,
    })
    if (result && result.success) {
      message.value = '连接成功！SQL Server ' + host + ':' + portRaw
      messageType.value = 'success'
    } else {
      message.value = '连接失败: ' + (result?.error || '未知错误')
      messageType.value = 'error'
    }
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.response?.data?.error || e.message
    message.value = '测试连接失败: ' + detail
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 5000)
  }
}

async function testSmtp() {
  if (smtpTesting.value) return
  smtpTesting.value = true
  smtpTestResult.value = ''
  try {
    const result = await request.post('/smtp/test', {
      server: smtpConfigs.smtp_server,
      port: parseInt(smtpConfigs.smtp_port, 10) || 587,
      user: smtpConfigs.smtp_user,
      password: smtpConfigs.smtp_password,
      recipients: alertConfigs.smtp_recipients,
    })
    smtpTestOk.value = result?.success
    smtpTestResult.value = result?.message || result?.error || '未知结果'
  } catch (e) {
    smtpTestOk.value = false
    smtpTestResult.value = '测试失败: ' + (e?.response?.data?.detail || e.message)
  } finally {
    smtpTesting.value = false
  }
}

// ---------- Logo 管理 ----------
async function checkLogoExists() {
  try {
    const resp = await fetch(getLogoUrl(), { method: 'HEAD' })
    if (resp.ok) {
      logoPreviewUrl.value = getLogoUrl() + '?t=' + Date.now()
    } else {
      logoPreviewUrl.value = ''
    }
  } catch {
    logoPreviewUrl.value = ''
  }
}

async function onLogoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  try {
    const data = await uploadLogo(file)
    logoPreviewUrl.value = data.logo_url || (getLogoUrl() + '?t=' + Date.now())
    message.value = 'Logo 上传成功！'
    messageType.value = 'success'
  } catch (err) {
    message.value = 'Logo 上传失败: ' + (err?.response?.data?.detail || err.message)
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 3000)
  }
}

async function onDeleteLogo() {
  try {
    await deleteLogo()
    logoPreviewUrl.value = ''
    message.value = '已恢复默认 Logo'
    messageType.value = 'success'
  } catch (err) {
    message.value = '删除失败: ' + (err?.response?.data?.detail || err.message)
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 3000)
  }
}

onMounted(async () => {
  fetchConfigs()
  try {
    const data = await getAiProviders()
    aiProviders.value = data.providers || {}
  } catch (e) {
    console.error('获取 AI 提供商列表失败', e)
  }
})
onUnmounted(() => { if (toastTimer) clearTimeout(toastTimer) })
</script>

<style scoped>
.settings-page {
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
  color: #333;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.btn-primary {
  background: #1890ff;
  color: #fff;
}
.btn-primary:hover {
  background: #096dd9;
}
.btn-test {
  background: #52c41a;
  color: #fff;
}
.btn-test:hover {
  background: #389e0d;
}
.btn-sm {
  padding: 5px 14px;
  font-size: 13px;
}
.config-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.config-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.section-title {
  margin: 0 0 16px;
  font-size: 15px;
  color: #1890ff;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 8px;
}
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.config-label {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}
.config-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.config-input:focus {
  border-color: #1890ff;
}
.config-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
  cursor: pointer;
}
.config-select:focus {
  border-color: #1890ff;
}
.config-desc {
  font-size: 12px;
  color: #999;
}
.message-toast {
  position: sticky;
  top: 0;
  z-index: 100;
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
  animation: slideDown 0.2s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-toast.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}
.message-toast.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #f5222d;
}
.smtp-test-result {
  margin-left: 12px;
  font-size: 13px;
}
.smtp-test-result.ok {
  color: #52c41a;
}
.smtp-test-result.fail {
  color: #f5222d;
}
/* 开关样式 */
.toggle-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 0;
}
.toggle-input {
  display: none;
}
.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  background: #d9d9d9;
  border-radius: 6px;
  transition: background 0.3s;
  flex-shrink: 0;
}
.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s;
}
.toggle-input:checked + .toggle-switch {
  background: #1890ff;
}
.toggle-input:checked + .toggle-switch::after {
  transform: translateX(20px);
}
.toggle-text {
  font-size: 13px;
  color: #666;
}
/* Dark theme */
[data-theme='dark'] .config-section {
  background: #1e293b;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
[data-theme='dark'] .section-title {
  color: #60a5fa;
  border-bottom-color: #334155;
}
[data-theme='dark'] .config-label {
  color: #cbd5e1;
}
[data-theme='dark'] .config-input,
[data-theme='dark'] .config-select {
  background: #0f172a;
  border-color: #334155;
  color: #e2e8f0;
}
[data-theme='dark'] .config-input:focus,
[data-theme='dark'] .config-select:focus {
  border-color: #60a5fa;
}
[data-theme='dark'] .config-desc {
  color: #64748b;
}
[data-theme='dark'] .toggle-switch {
  background: #475569;
}
[data-theme='dark'] .toggle-input:checked + .toggle-switch {
  background: #3b82f6;
}
[data-theme='dark'] .toggle-text {
  color: #94a3b8;
}

/* 品牌 Logo 上传 */
.brand-logo-item {
  grid-column: 1 / -1;
}
.logo-upload-area {
  display: flex;
  align-items: center;
  gap: 20px;
}
.logo-preview {
  width: 160px;
  height: 60px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #fafafa;
  flex-shrink: 0;
}
.logo-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.logo-placeholder {
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  color: #bfbfbf;
}
.logo-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.btn-sm {
  padding: 5px 14px;
  font-size: 13px;
}
.btn-upload {
  background: #1890ff;
  color: #fff;
  cursor: pointer;
  display: inline-block;
  text-align: center;
}
.btn-upload:hover {
  background: #40a9ff;
}
.btn-danger {
  background: #ff4d4f;
  color: #fff;
  border: none;
}
.btn-danger:hover {
  background: #ff7875;
}
</style>
