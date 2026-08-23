<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>{{ t('settings.title') }}</h2>
      <div class="header-actions">
        <button class="btn btn-test" @click="testConnection">{{ t('settings.testConnection') }}</button>
        <button class="btn btn-primary" @click="saveAll">{{ t('settings.saveAndApply') }}</button>
      </div>
    </div>

    <div v-if="message" :class="['message-toast', messageType === 'error' ? 'error' : 'success']">
      {{ message }}
    </div>

    <div class="config-sections">
      <!-- 品牌设置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.brand') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">{{ t('settings.systemTitle') }}</label>
            <input
              type="text"
              v-model="brandTitle"
              class="config-input"
              placeholder="数据库监控平台"
            />
            <span class="config-desc">{{ t('settings.systemTitleDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.notifSound') }}</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="notifSoundEnabled" class="toggle-input" @change="onNotifSoundToggle" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ notifSoundEnabled ? t('common.enabled') : t('common.disabled') }}</span>
            </label>
            <span class="config-desc">{{ t('settings.notifSoundDesc') }}</span>
          </div>
          <div class="config-item brand-logo-item">
            <label class="config-label">{{ t('settings.logo') }}</label>
            <div class="logo-upload-area">
              <div class="logo-preview" v-if="logoPreviewUrl">
                <img :src="logoPreviewUrl" alt="Logo" class="logo-preview-img" />
              </div>
              <div class="logo-preview logo-placeholder" v-else>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#bfbfbf" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                <span>{{ t('settings.noCustomLogo') }}</span>
              </div>
              <div class="logo-actions">
                <label class="btn btn-sm btn-upload">
                  <input type="file" accept="image/png,image/jpeg,image/svg+xml,image/webp" @change="onLogoUpload" hidden />
                  {{ logoPreviewUrl ? t('settings.replaceLogo') : t('settings.uploadLogo') }}
                </label>
                <button v-if="logoPreviewUrl" class="btn btn-sm btn-danger" @click="onDeleteLogo">{{ t('settings.restoreDefault') }}</button>
                <span class="config-desc">{{ t('settings.logoDesc') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 模型配置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.aiConfig') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">{{ t('settings.aiProvider') }}</label>
            <select v-model="aiConfigs.ai_provider" class="config-select" @change="onProviderChange">
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
              <option value="xiaomi">Xiaomi MiMo</option>
              <option value="custom">自定义（OpenAI 兼容）</option>
            </select>
            <span class="config-desc">选择 AI 服务提供商</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.aiKey') }}</label>
            <input
              type="password"
              v-model="aiConfigs.ai_api_key"
              class="config-input"
              placeholder="API Key"
            />
            <span class="config-desc">{{ t('settings.aiKeyDesc', { provider: providerName }) }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.aiModel') }}</label>
            <select v-if="currentModels.length" v-model="aiConfigs.ai_model" class="config-select">
              <option v-for="m in currentModels" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
            <input v-else v-model="aiConfigs.ai_model" class="config-input" placeholder="输入模型名称" />
            <span class="config-desc">{{ t('settings.aiModelDesc') }}</span>
          </div>
          <div class="config-item" v-if="aiConfigs.ai_provider === 'custom'">
            <label class="config-label">{{ t('settings.aiBaseUrl') }}</label>
            <input
              type="text"
              v-model="aiConfigs.ai_base_url"
              class="config-input"
              placeholder="https://your-api.com"
            />
            <span class="config-desc">{{ t('settings.aiBaseUrlDesc') }}</span>
          </div>
        </div>
      </div>

      <!-- 系统设置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.system') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">{{ t('settings.timezone') }}</label>
            <select v-model="timezone" class="config-select">
              <option value="Asia/Shanghai">Asia/Shanghai (UTC+8) - 北京时间</option>
              <option value="Asia/Tokyo">Asia/Tokyo (UTC+9) - 东京时间</option>
              <option value="America/New_York">America/New_York (UTC-5) - 纽约时间</option>
              <option value="America/Los_Angeles">America/Los_Angeles (UTC-8) - 洛杉矶时间</option>
              <option value="Europe/London">Europe/London (UTC+0) - 伦敦时间</option>
              <option value="Europe/Berlin">Europe/Berlin (UTC+1) - 柏林时间</option>
              <option value="UTC">UTC (UTC+0)</option>
            </select>
            <span class="config-desc">{{ t('settings.timezoneDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.dataRetention') }}</label>
            <input
              type="number"
              v-model="dataRetentionDays"
              class="config-input"
              min="7"
              max="3650"
              placeholder="90"
            />
            <span class="config-desc">{{ t('settings.dataRetentionDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.frontendUrl') }}</label>
            <input
              type="text"
              v-model="frontendUrl"
              class="config-input"
              placeholder="https://monitor.example.com"
            />
            <span class="config-desc">{{ t('settings.frontendUrlDesc') }}</span>
          </div>
        </div>
      </div>

      <!-- SQL Server 连接配置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.sqlServerConfig') }}</h3>
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
        <h3 class="section-title">{{ t('settings.pgConfig') }}</h3>
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
        <h3 class="section-title">{{ t('settings.collectConfig') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">{{ t('settings.multiInstance') }}</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="collectConfigs.mssql_instances_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ collectConfigs.mssql_instances_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
            </label>
            <span class="config-desc">{{ t('settings.multiInstanceDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.interval') }}</label>
            <input
              type="number"
              v-model="collectConfigs.scheduler_interval_seconds"
              class="config-input"
              min="10"
              max="3600"
              placeholder="60"
            />
            <span class="config-desc">{{ t('settings.intervalDesc') }}</span>
          </div>
        </div>
      </div>

      <!-- 告警规则配置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.alertConfig') }}</h3>
        <div class="config-grid">
          <div class="config-item">
            <label class="config-label">{{ t('settings.memoryThreshold') }}</label>
            <input
              type="number"
              v-model="alertConfigs.memory_alert_threshold_pct"
              class="config-input"
              min="50"
              max="100"
              placeholder="85"
            />
            <span class="config-desc">{{ t('settings.memoryThresholdDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.memoryDuration') }}</label>
            <input
              type="number"
              v-model="alertConfigs.memory_alert_duration_minutes"
              class="config-input"
              min="1"
              max="60"
              placeholder="5"
            />
            <span class="config-desc">{{ t('settings.memoryDurationDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.deadlockAlert') }}</label>
            <label class="toggle-label">
              <input type="checkbox" v-model="alertConfigs.deadlock_alert_enabled" class="toggle-input" />
              <span class="toggle-switch"></span>
              <span class="toggle-text">{{ alertConfigs.deadlock_alert_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
            </label>
            <span class="config-desc">{{ t('settings.deadlockAlertDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.interruptThreshold') }}</label>
            <input
              type="number"
              v-model="alertConfigs.collection_interrupt_threshold"
              class="config-input"
              min="1"
              max="10"
              placeholder="3"
            />
            <span class="config-desc">{{ t('settings.interruptThresholdDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.cooldown') }}</label>
            <input
              type="number"
              v-model="alertConfigs.alert_cooldown_minutes"
              class="config-input"
              min="5"
              max="1440"
              placeholder="30"
            />
            <span class="config-desc">{{ t('settings.cooldownDesc') }}</span>
          </div>
          <div class="config-item">
            <label class="config-label">{{ t('settings.recipients') }}</label>
            <input
              type="text"
              v-model="alertConfigs.smtp_recipients"
              class="config-input"
              placeholder="user1@example.com, user2@example.com"
            />
            <span class="config-desc">{{ t('settings.recipientsDesc') }}</span>
          </div>
        </div>
      </div>

      <!-- 通知渠道配置 -->
      <div class="config-section">
        <h3 class="section-title">{{ t('settings.notifyChannel') }}</h3>
        <div class="channel-grid">
          <div class="channel-card" @click="openChannelModal('wecom')">
            <div class="channel-icon wecom-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div class="channel-info">
              <span class="channel-name">{{ t('settings.wecomChannel') }}</span>
              <span class="channel-status" :class="notifyConfigs.wecom_enabled === 'true' ? 'on' : 'off'">
                {{ notifyConfigs.wecom_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}
              </span>
            </div>
            <div class="channel-arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>

          <div class="channel-card" @click="openChannelModal('feishu_app')">
            <div class="channel-icon feishu-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1.27a2 2 0 0 1-3.46 0H6.73a2 2 0 0 1-3.46 0H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/></svg>
            </div>
            <div class="channel-info">
              <span class="channel-name">{{ t('settings.feishuAppChannel') }}</span>
              <span class="channel-status" :class="feishuAppConfigs.feishu_app_enabled === 'true' ? 'on' : 'off'">
                {{ feishuAppConfigs.feishu_app_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}
              </span>
            </div>
            <div class="channel-arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>

          <div class="channel-card" @click="openChannelModal('smtp')">
            <div class="channel-icon smtp-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
            <div class="channel-info">
              <span class="channel-name">{{ t('settings.smtpChannel') }}</span>
              <span class="channel-status" :class="smtpConfigs.smtp_enabled === 'true' ? 'on' : 'off'">
                {{ smtpConfigs.smtp_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}
              </span>
            </div>
            <div class="channel-arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>

          <div class="channel-card" @click="openChannelModal('feishu')">
            <div class="channel-icon feishu-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            </div>
            <div class="channel-info">
              <span class="channel-name">{{ t('settings.feishuWebhookChannel') }}</span>
              <span class="channel-status" :class="feishuConfigs.feishu_enabled === 'true' ? 'on' : 'off'">
                {{ feishuConfigs.feishu_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}
              </span>
            </div>
            <div class="channel-arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知渠道配置弹窗 -->
    <div v-if="channelModalVisible" class="modal-overlay" @click.self="closeChannelModal">
      <div class="channel-modal">
        <div class="modal-header">
          <h3>{{ channelModalTitle }}</h3>
          <button class="modal-close" @click="closeChannelModal">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <!-- 企业微信 -->
          <template v-if="currentChannel === 'wecom'">
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.wecomToggle') }}</label>
              <label class="toggle-label">
                <input type="checkbox" v-model="notifyConfigs.wecom_enabled" class="toggle-input" />
                <span class="toggle-switch"></span>
                <span class="toggle-text">{{ notifyConfigs.wecom_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
              </label>
              <span class="modal-desc">{{ t('settings.wecomToggleDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.wecomWebhook') }}</label>
              <input type="text" v-model="notifyConfigs.wecom_webhook_url" class="modal-input" placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx" />
              <span class="modal-desc">{{ t('settings.wecomWebhookDesc') }}</span>
            </div>
          </template>

          <!-- 飞书应用通知 -->
          <template v-if="currentChannel === 'feishu_app'">
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuAppToggle') }}</label>
              <label class="toggle-label">
                <input type="checkbox" v-model="feishuAppConfigs.feishu_app_enabled" class="toggle-input" />
                <span class="toggle-switch"></span>
                <span class="toggle-text">{{ feishuAppConfigs.feishu_app_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
              </label>
              <span class="modal-desc">{{ t('settings.feishuAppToggleDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuAppId') }}</label>
              <input type="text" v-model="feishuAppConfigs.feishu_app_id" class="modal-input" placeholder="cli_xxxxxxxxxxxx" />
              <span class="modal-desc">{{ t('settings.feishuAppIdDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuAppSecret') }}</label>
              <input type="password" v-model="feishuAppConfigs.feishu_app_secret" class="modal-input" placeholder="应用密钥" />
              <span class="modal-desc">{{ t('settings.feishuAppSecretDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuOpenId') }}</label>
              <input type="text" v-model="feishuAppConfigs.feishu_receive_open_id" class="modal-input" placeholder="ou_xxxxxxxxxxxx" />
              <span class="modal-desc">{{ t('settings.feishuOpenIdDesc') }}</span>
            </div>
            <div class="modal-field modal-actions-row">
              <button class="btn btn-sm btn-test" @click="testFeishu" :disabled="feishuTesting">
                {{ feishuTesting ? t('common.submit') : t('settings.feishuSendTest') }}
              </button>
              <span v-if="feishuTestResult" :class="['smtp-test-result', feishuTestOk ? 'ok' : 'fail']">
                {{ feishuTestResult }}
              </span>
            </div>
          </template>

          <!-- SMTP 邮件 -->
          <template v-if="currentChannel === 'smtp'">
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.smtpToggle') }}</label>
              <label class="toggle-label">
                <input type="checkbox" v-model="smtpConfigs.smtp_enabled" class="toggle-input" />
                <span class="toggle-switch"></span>
                <span class="toggle-text">{{ smtpConfigs.smtp_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
              </label>
              <span class="modal-desc">{{ t('settings.smtpToggleDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.smtpServer') }}</label>
              <input type="text" v-model="smtpConfigs.smtp_server" class="modal-input" placeholder="smtp.example.com" />
              <span class="modal-desc">{{ t('settings.smtpServerDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.smtpPort') }}</label>
              <input type="number" v-model="smtpConfigs.smtp_port" class="modal-input" placeholder="587" />
              <span class="modal-desc">{{ t('settings.smtpPortDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.smtpUser') }}</label>
              <input type="text" v-model="smtpConfigs.smtp_user" class="modal-input" placeholder="alert@example.com" />
              <span class="modal-desc">{{ t('settings.smtpUserDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.smtpPassword') }}</label>
              <input type="password" v-model="smtpConfigs.smtp_password" class="modal-input" placeholder="密码或授权码" />
              <span class="modal-desc">{{ t('settings.smtpPasswordDesc') }}</span>
            </div>
            <div class="modal-field modal-actions-row">
              <button class="btn btn-sm btn-test" @click="testSmtp" :disabled="smtpTesting">
                {{ smtpTesting ? t('common.submit') : t('settings.sendTest') }}
              </button>
              <span v-if="smtpTestResult" :class="['smtp-test-result', smtpTestOk ? 'ok' : 'fail']">
                {{ smtpTestResult }}
              </span>
            </div>
          </template>

          <!-- 飞书 Webhook -->
          <template v-if="currentChannel === 'feishu'">
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuToggle') }}</label>
              <label class="toggle-label">
                <input type="checkbox" v-model="feishuConfigs.feishu_enabled" class="toggle-input" />
                <span class="toggle-switch"></span>
                <span class="toggle-text">{{ feishuConfigs.feishu_enabled === 'true' ? t('common.enabled') : t('common.disabled') }}</span>
              </label>
              <span class="modal-desc">{{ t('settings.feishuToggleDesc') }}</span>
            </div>
            <div class="modal-field">
              <label class="modal-label">{{ t('settings.feishuWebhook') }}</label>
              <input type="text" v-model="feishuConfigs.feishu_webhook_url" class="modal-input" placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/xxx" />
              <span class="modal-desc">{{ t('settings.feishuWebhookDesc') }}</span>
            </div>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="closeChannelModal">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="saveChannelConfig">{{ t('common.save') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import request, { getConfigs, updateConfig, getAiProviders, getLogoUrl, uploadLogo, deleteLogo } from '@/api'
import { setTimezone } from '@/utils/datetime'

const { t } = useI18n()

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
const frontendUrl = ref('')
const message = ref('')
const messageType = ref('success')
const smtpTesting = ref(false)
const smtpTestResult = ref('')
const smtpTestOk = ref(false)
let toastTimer = null

// 通知渠道弹窗
const channelModalVisible = ref(false)
const currentChannel = ref('')
const channelModalTitle = ref('')
const channelTitles = {
  wecom: () => t('settings.wecomChannel'),
  feishu_app: () => t('settings.feishuAppChannel'),
  smtp: () => t('settings.smtpChannel'),
  feishu: () => t('settings.feishuWebhookChannel'),
}
function openChannelModal(channel) {
  currentChannel.value = channel
  channelModalTitle.value = channelTitles[channel]()
  channelModalVisible.value = true
}
function closeChannelModal() { channelModalVisible.value = false; currentChannel.value = '' }
async function saveChannelConfig() {
  // 收集当前渠道相关的配置项并保存
  const channelKeys = {
    wecom: ['wecom_enabled', 'wecom_webhook_url'],
    feishu_app: ['feishu_app_enabled', 'feishu_app_id', 'feishu_app_secret', 'feishu_receive_open_id'],
    smtp: ['smtp_enabled', 'smtp_server', 'smtp_port', 'smtp_user', 'smtp_password'],
    feishu: ['feishu_enabled', 'feishu_webhook_url'],
  }
  const configMap = {
    wecom_enabled: notifyConfigs.wecom_enabled,
    wecom_webhook_url: notifyConfigs.wecom_webhook_url,
    feishu_app_enabled: feishuAppConfigs.feishu_app_enabled,
    feishu_app_id: feishuAppConfigs.feishu_app_id,
    feishu_app_secret: feishuAppConfigs.feishu_app_secret,
    feishu_receive_open_id: feishuAppConfigs.feishu_receive_open_id,
    smtp_enabled: smtpConfigs.smtp_enabled,
    smtp_server: smtpConfigs.smtp_server,
    smtp_port: smtpConfigs.smtp_port,
    smtp_user: smtpConfigs.smtp_user,
    smtp_password: smtpConfigs.smtp_password,
    feishu_enabled: feishuConfigs.feishu_enabled,
    feishu_webhook_url: feishuConfigs.feishu_webhook_url,
  }
  const keys = channelKeys[currentChannel.value] || []
  const changed = keys.filter(key => originalConfigs.value[key] !== String(configMap[key] ?? ''))
  if (changed.length === 0) {
    closeChannelModal()
    return
  }
  try {
    const results = await Promise.allSettled(
      changed.map(key => updateConfig(key, String(configMap[key])))
    )
    const failures = results.map((r, i) => r.status === 'rejected' ? changed[i] : null).filter(Boolean)
    if (failures.length > 0) {
      message.value = `${t('settings.saveFailed')} ${failures.join(', ')}`
      messageType.value = 'error'
    } else {
      message.value = t('settings.saveSuccess', { count: changed.length })
      messageType.value = 'success'
      await fetchConfigs()
      closeChannelModal()
    }
  } catch (e) {
    message.value = t('settings.saveFailed') + ' ' + (e?.response?.data?.detail || e.message)
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 3000)
  }
}

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

// 飞书应用通知配置（关键错误）
const feishuAppConfigs = reactive({
  feishu_app_enabled: 'false',
  feishu_app_id: '',
  feishu_app_secret: '',
  feishu_receive_open_id: '',
})
const feishuTesting = ref(false)
const feishuTestResult = ref('')
const feishuTestOk = ref(false)

// 飞书 Webhook 配置
const feishuConfigs = reactive({
  feishu_enabled: 'false',
  feishu_webhook_url: '',
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
    mssql_host: { labelKey: 'common.serverAddress', password: false },
    mssql_port: { labelKey: 'common.port', password: false },
    mssql_user: { labelKey: 'common.account', password: false },
    mssql_password: { labelKey: 'common.password', password: true },
    mssql_database: { labelKey: 'common.database', password: false },
  }
  return filterAndMap(configList.value, map)
})

const pgConfigs = computed(() => {
  const map = {
    pg_host: { labelKey: 'common.serverAddress', password: false },
    pg_port: { labelKey: 'common.port', password: false },
    pg_database: { labelKey: 'settings.dbName', password: false },
    pg_user: { labelKey: 'common.account', password: false },
    pg_password: { labelKey: 'common.password', password: true },
  }
  return filterAndMap(configList.value, map)
})

function filterAndMap(list, map) {
  return list
    .filter(cfg => map[cfg.config_key])
    .map(cfg => ({
      key: cfg.config_key,
      label: t(map[cfg.config_key].labelKey),
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
    frontendUrl.value = find('frontend_url') || ''
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

    // 飞书应用通知配置
    feishuAppConfigs.feishu_app_enabled = find('feishu_app_enabled') || 'false'
    feishuAppConfigs.feishu_app_id = find('feishu_app_id')
    feishuAppConfigs.feishu_app_secret = find('feishu_app_secret')
    feishuAppConfigs.feishu_receive_open_id = find('feishu_receive_open_id')

    // 飞书 Webhook 配置
    feishuConfigs.feishu_enabled = find('feishu_enabled') || 'false'
    feishuConfigs.feishu_webhook_url = find('feishu_webhook_url') || ''

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
    { key: 'frontend_url', value: frontendUrl.value },
    { key: 'mssql_instances_enabled', value: collectConfigs.mssql_instances_enabled },
    { key: 'scheduler_interval_seconds', value: collectConfigs.scheduler_interval_seconds },
    { key: 'memory_alert_threshold_pct', value: alertConfigs.memory_alert_threshold_pct },
    { key: 'memory_alert_duration_minutes', value: alertConfigs.memory_alert_duration_minutes },
    { key: 'deadlock_alert_enabled', value: alertConfigs.deadlock_alert_enabled },
    { key: 'collection_interrupt_threshold', value: alertConfigs.collection_interrupt_threshold },
    { key: 'alert_cooldown_minutes', value: alertConfigs.alert_cooldown_minutes },
    { key: 'wecom_webhook_url', value: notifyConfigs.wecom_webhook_url },
    { key: 'wecom_enabled', value: notifyConfigs.wecom_enabled },
    { key: 'feishu_app_enabled', value: feishuAppConfigs.feishu_app_enabled },
    { key: 'feishu_app_id', value: feishuAppConfigs.feishu_app_id },
    { key: 'feishu_app_secret', value: feishuAppConfigs.feishu_app_secret },
    { key: 'feishu_receive_open_id', value: feishuAppConfigs.feishu_receive_open_id },
    { key: 'feishu_enabled', value: feishuConfigs.feishu_enabled },
    { key: 'feishu_webhook_url', value: feishuConfigs.feishu_webhook_url },
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
    message.value = t('settings.noConfigChange')
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
      message.value = `${t('settings.saveFailed')} ${failures.join(', ')} 配置项保存异常`
      messageType.value = 'error'
      return
    }
    message.value = t('settings.saveSuccess', { count: changedConfigs.length })
    messageType.value = 'success'
    setTimezone(timezone.value)
    await fetchConfigs()
  } catch (e) {
    message.value = t('settings.saveFailed') + ' ' + (e?.response?.data?.detail || e.message || t('settings.unknownError'))
    messageType.value = 'error'
  } finally {
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { message.value = '' }, 5000)
  }
}

async function testConnection() {
  message.value = t('settings.testingConnection')
  messageType.value = 'success'
  try {
    const host = mssqlConfigs.value.find(c => c.key === 'mssql_host')?.value
    const portRaw = mssqlConfigs.value.find(c => c.key === 'mssql_port')?.value || '1433'
    const user = mssqlConfigs.value.find(c => c.key === 'mssql_user')?.value
    const password = mssqlConfigs.value.find(c => c.key === 'mssql_password')?.value
    const database = mssqlConfigs.value.find(c => c.key === 'mssql_database')?.value || 'master'

    if (!host || !user) {
      message.value = t('settings.fillRequired')
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
      message.value = t('settings.testSuccess', { host, port: portRaw })
      messageType.value = 'success'
    } else {
      message.value = t('settings.connectFailed') + ' ' + (result?.error || t('settings.unknownError'))
      messageType.value = 'error'
    }
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.response?.data?.error || e.message
    message.value = t('settings.testFailed') + ' ' + detail
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
    smtpTestResult.value = result?.message || result?.error || t('settings.unknownResult')
  } catch (e) {
    smtpTestOk.value = false
    smtpTestResult.value = t('settings.smtpTestFailed') + ' ' + (e?.response?.data?.detail || e.message)
  } finally {
    smtpTesting.value = false
  }
}

async function testFeishu() {
  if (feishuTesting.value) return
  feishuTesting.value = true
  feishuTestResult.value = ''
  try {
    const result = await request.post('/feishu/test', {
      app_id: feishuAppConfigs.feishu_app_id,
      app_secret: feishuAppConfigs.feishu_app_secret,
      receive_open_id: feishuAppConfigs.feishu_receive_open_id,
    })
    feishuTestOk.value = !!result?.success
    feishuTestResult.value = result?.message || result?.error || t('settings.unknownResult')
  } catch (e) {
    feishuTestOk.value = false
    feishuTestResult.value = t('settings.feishuTestFailed') + ' ' + (e?.response?.data?.detail || e.message)
  } finally {
    feishuTesting.value = false
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
    message.value = t('settings.logoUploadSuccess')
    messageType.value = 'success'
  } catch (err) {
    message.value = t('settings.logoUploadFailed') + ' ' + (err?.response?.data?.detail || err.message)
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
    message.value = t('settings.logoRestored')
    messageType.value = 'success'
  } catch (err) {
    message.value = t('settings.logoDeleteFailed') + ' ' + (err?.response?.data?.detail || err.message)
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
.btn-cancel {
  background: #fff;
  color: #666;
  border: 1px solid #d9d9d9;
}
.btn-cancel:hover {
  color: #1890ff;
  border-color: #1890ff;
}

/* 通知渠道卡片 */
.channel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 12px;
}
.channel-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.channel-card:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24,144,255,0.15);
}
.channel-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  flex-shrink: 0;
}
.wecom-icon {
  background: #e6f7ff;
  color: #1890ff;
}
.feishu-icon {
  background: #f0f5ff;
  color: #2f54eb;
}
.smtp-icon {
  background: #f6ffed;
  color: #52c41a;
}
.channel-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.channel-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
.channel-status {
  font-size: 12px;
}
.channel-status.on {
  color: #52c41a;
}
.channel-status.off {
  color: #999;
}
.channel-arrow {
  display: flex;
  align-items: center;
  color: #bfbfbf;
  flex-shrink: 0;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.channel-modal {
  background: var(--bg-card);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}
.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.modal-close {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}
.modal-close:hover {
  background: var(--bg-hover);
  color: #666;
}
.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.modal-field {
  margin-bottom: 16px;
}
.modal-field:last-child {
  margin-bottom: 0;
}
.modal-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.modal-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 13px;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.2s;
}
.modal-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
}
.modal-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.modal-actions-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid var(--border-color);
}
.config-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.config-section {
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.section-title {
  margin: 0 0 10px;
  font-size: 15px;
  color: #1890ff;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 6px;
}
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 10px 14px;
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
