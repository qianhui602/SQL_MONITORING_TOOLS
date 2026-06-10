<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统配置</h2>
      <div class="header-actions">
        <button class="btn btn-test" @click="testConnection">测试 SQL Server 连接</button>
        <button class="btn btn-primary" @click="saveAll">保存并应用</button>
      </div>
    </div>

    <div class="config-sections">
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
        </div>
      </div>

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

      <div class="config-section">
        <h3 class="section-title">采集与告警配置</h3>
        <div class="config-grid">
          <div class="config-item" v-for="item in alertConfigs" :key="item.key">
            <label class="config-label">{{ item.label }}</label>
            <input
              v-if="item.key !== 'mssql_instances_enabled' && item.key !== 'deadlock_alert_enabled' && item.key !== 'wecom_enabled'"
              v-model="item.value"
              class="config-input"
              :placeholder="item.desc"
            />
            <label v-else class="toggle-label">
              <input type="checkbox" v-model="item.value" true-value="true" false-value="false" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ item.value === 'true' ? '已开启' : '已关闭' }}</span>
            </label>
            <span class="config-desc">{{ item.desc }}</span>
          </div>
        </div>
      </div>

      <div class="config-section">
        <h3 class="section-title">DeepSeek AI 配置</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">API 密钥</label>
            <input
              type="password"
              v-model="deepseekApiKey"
              class="config-input"
              placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            />
            <span class="config-desc">DeepSeek API 密钥，用于 AI 死锁分析和报告生成</span>
          </div>
          <div class="config-item">
            <label class="config-label">AI 模型</label>
            <select v-model="deepseekModel" class="config-select">
              <option value="deepseek-v4-flash">DeepSeek-V4-Flash（快速）</option>
              <option value="deepseek-v4-pro">DeepSeek-V4-Pro（增强）</option>
            </select>
            <span class="config-desc">选择用于 AI 分析的 DeepSeek 模型版本</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" :class="['message', messageType === 'error' ? 'error' : 'success']">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import request, { getConfigs, updateConfig } from '@/api'
import { setTimezone } from '@/utils/datetime'

const configList = ref([])
const deepseekApiKey = ref('')
const deepseekModel = ref('deepseek-v4-flash')
const timezone = ref('Asia/Shanghai')
const message = ref('')
const messageType = ref('success')
let toastTimer = null

const mssqlConfigs = computed(() => {
  const map = {
    mssql_host: { label: '服务器地址', password: false },
    mssql_port: { label: '端口', password: false },
    mssql_user: { label: '账号', password: false },
    mssql_password: { label: '密码', password: true },
    mssql_database: { label: '数据库', password: false },
  }
  return filterAndMap(configList.value, map, 'MSSQL')
})

const pgConfigs = computed(() => {
  const map = {
    pg_host: { label: '服务器地址', password: false },
    pg_port: { label: '端口', password: false },
    pg_database: { label: '数据库名', password: false },
    pg_user: { label: '账号', password: false },
    pg_password: { label: '密码', password: true },
  }
  return filterAndMap(configList.value, map, 'PG')
})

const alertConfigs = computed(() => {
  const map = {
    mssql_instances_enabled: { label: '启用多实例采集', password: false },
    scheduler_interval_seconds: { label: '采集间隔(秒)', password: false },
    memory_alert_threshold_pct: { label: '内存告警阈值(%)', password: false },
    memory_alert_duration_minutes: { label: '内存告警持续时长(分钟)', password: false },
    deadlock_alert_enabled: { label: '死锁告警开关', password: false },
    collection_interrupt_threshold: { label: '采集中断阈值(次)', password: false },
    alert_cooldown_minutes: { label: '告警冷却期(分钟)', password: false },
    wecom_webhook_url: { label: '企业微信 Webhook URL', password: false },
    wecom_enabled: { label: '企业微信通知开关', password: false },
  }
  return filterAndMap(configList.value, map, null)
})

function filterAndMap(list, map, prefix) {
  const result = []
  for (const cfg of list) {
    const meta = map[cfg.config_key]
    if (meta) {
      result.push({
        key: cfg.config_key,
        label: meta.label,
        value: cfg.config_value,
        desc: cfg.description,
        password: meta.password,
      })
    }
  }
  return result
}

function getVisibleLabel(config) {
  if (config.config_key === 'pg_password' || config.config_key === 'mssql_password') return '********'
  return config.config_value
}

async function fetchConfigs() {
  try {
    const data = await getConfigs()
    configList.value = Array.isArray(data) ? data : (data.items || [])
    // 提取 DeepSeek 配置
    const apiKeyCfg = configList.value.find(c => c.config_key === 'deepseek_api_key')
    const modelCfg = configList.value.find(c => c.config_key === 'deepseek_model')
    if (apiKeyCfg) deepseekApiKey.value = apiKeyCfg.config_value
    if (modelCfg) deepseekModel.value = modelCfg.config_value
    // 提取系统时区配置
    const tzCfg = configList.value.find(c => c.config_key === 'timezone')
    if (tzCfg) {
      timezone.value = tzCfg.config_value
      setTimezone(tzCfg.config_value)
    }
  } catch (e) {
    console.error('获取配置失败', e)
  }
}

async function saveAll() {
  const allConfigs = [...mssqlConfigs.value, ...pgConfigs.value, ...alertConfigs.value]
  // 添加 DeepSeek 配置
  allConfigs.push(
    { key: 'deepseek_api_key', value: deepseekApiKey.value },
    { key: 'deepseek_model', value: deepseekModel.value }
  )
  // 添加系统时区配置
  allConfigs.push(
    { key: 'timezone', value: timezone.value }
  )
  try {
    for (const cfg of allConfigs) {
      await updateConfig(cfg.key, cfg.value)
    }
    message.value = '保存成功！配置将在下一个采集周期自动应用。'
    messageType.value = 'success'
    // 立即应用时区设置
    setTimezone(timezone.value)
  } catch (e) {
    message.value = '保存失败: ' + (e.message || '未知错误')
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

onMounted(() => {
  fetchConfigs()
})

onUnmounted(() => {
  if (toastTimer) clearTimeout(toastTimer)
})
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
.config-desc {
  font-size: 12px;
  color: #999;
}
.message {
  margin-top: 20px;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
}
.message.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}
.message.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
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
  border-radius: 12px;
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
[data-theme='dark'] .toggle-switch {
  background: #475569;
}
[data-theme='dark'] .toggle-input:checked + .toggle-switch {
  background: #3b82f6;
}
[data-theme='dark'] .toggle-text {
  color: #94a3b8;
}
</style>
