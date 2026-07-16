<template>
  <div class="setup-page">
    <div class="setup-container">
      <!-- 左侧品牌区 -->
      <div class="setup-left">
        <div class="left-content">
          <img src="/LOGO.png" alt="Logo" class="left-logo" />
          <h1 class="left-title">{{ t('setup.platformTitle') }}</h1>
          <p class="left-desc">{{ t('setup.platformDesc') }}</p>
          <div class="step-indicator">
            <div
              v-for="(step, idx) in steps"
              :key="idx"
              class="step-item"
              :class="{ active: currentStep === idx, completed: currentStep > idx }"
            >
              <div class="step-number">
                <span v-if="currentStep > idx">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                </span>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <div class="step-text">
                <div class="step-label">{{ step.label }}</div>
                <div class="step-desc">{{ step.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="setup-right">
        <div class="setup-card">
          <transition name="fade-slide" mode="out-in">
            <!-- Step 1: 欢迎页 -->
            <div v-if="currentStep === 0" key="welcome" class="step-content">
              <div class="welcome-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#1890ff" stroke-width="1.5">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  <polyline points="9 12 11 14 15 10" stroke="#52c41a"/>
                </svg>
              </div>
              <h2 class="welcome-title">{{ t('setup.welcomeTitle') }}</h2>
              <p class="welcome-desc">
                {{ t('setup.welcomeDesc1') }}<br />
                {{ t('setup.welcomeDesc2') }}<br />
                {{ t('setup.welcomeDesc3') }}
              </p>
              <div class="feature-list">
                <div class="feature-row">
                  <span class="feature-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#52c41a"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </span>
                  <span>{{ t('setup.feature1') }}</span>
                </div>
                <div class="feature-row">
                  <span class="feature-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#52c41a"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </span>
                  <span>{{ t('setup.feature2') }}</span>
                </div>
                <div class="feature-row">
                  <span class="feature-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#52c41a"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </span>
                  <span>{{ t('setup.feature3') }}</span>
                </div>
                <div class="feature-row">
                  <span class="feature-check">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#52c41a"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                  </span>
                  <span>{{ t('setup.feature4') }}</span>
                </div>
              </div>
              <button class="btn-primary btn-large" @click="nextStep">
                {{ t('setup.startInstall') }}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                </svg>
              </button>
            </div>

            <!-- Step 2: 创建管理员 -->
            <div v-if="currentStep === 1" key="admin" class="step-content">
              <h2 class="step-title">{{ t('setup.createAdmin') }}</h2>
              <p class="step-subtitle">{{ t('setup.createAdminDesc') }}</p>

              <div class="form-group">
                <label class="form-label">{{ t('setup.username') }} <span class="required">*</span></label>
                <input
                  v-model="adminForm.username"
                  type="text"
                  class="form-input"
                  :placeholder="t('setup.usernamePlaceholder')"
                  :class="{ error: errors.username }"
                />
                <span v-if="errors.username" class="form-error">{{ errors.username }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('setup.displayName') }}</label>
                <input
                  v-model="adminForm.fullName"
                  type="text"
                  class="form-input"
                  :placeholder="t('setup.displayNamePlaceholder')"
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">{{ t('setup.password') }} <span class="required">*</span></label>
                  <input
                    v-model="adminForm.password"
                    type="password"
                    class="form-input"
                    :placeholder="t('setup.passwordPlaceholder')"
                    :class="{ error: errors.password }"
                  />
                  <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
                </div>
                <div class="form-group">
                  <label class="form-label">{{ t('setup.confirmPassword') }} <span class="required">*</span></label>
                  <input
                    v-model="adminForm.confirmPassword"
                    type="password"
                    class="form-input"
                    :placeholder="t('setup.confirmPasswordPlaceholder')"
                    :class="{ error: errors.confirmPassword }"
                  />
                  <span v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</span>
                </div>
              </div>

              <div v-if="setupError" class="error-msg">{{ setupError }}</div>

              <div class="form-actions">
                <button class="btn-default" @click="prevStep">{{ t('setup.prevStep') }}</button>
                <button class="btn-primary" @click="submitAdmin" :disabled="loading">
                  <span v-if="loading" class="btn-spinner"></span>
                  {{ loading ? t('setup.creating') : t('setup.createAndContinue') }}
                </button>
              </div>
            </div>

            <!-- Step 3: 基础配置 -->
            <div v-if="currentStep === 2" key="config" class="step-content">
              <h2 class="step-title">{{ t('setup.basicConfig') }}</h2>
              <p class="step-subtitle">{{ t('setup.basicConfigDesc') }}</p>

              <div class="form-group">
                <label class="form-label">{{ t('setup.timezone') }}</label>
                <select v-model="configForm.timezone" class="form-select">
                  <option value="Asia/Shanghai">Asia/Shanghai (UTC+8) - {{ t('setup.beijing') }}</option>
                  <option value="Asia/Tokyo">Asia/Tokyo (UTC+9) - {{ t('setup.tokyo') }}</option>
                  <option value="America/New_York">America/New_York (UTC-5) - {{ t('setup.newyork') }}</option>
                  <option value="America/Los_Angeles">America/Los_Angeles (UTC-8) - {{ t('setup.losangeles') }}</option>
                  <option value="Europe/London">Europe/London (UTC+0) - {{ t('setup.london') }}</option>
                  <option value="UTC">UTC (UTC+0)</option>
                </select>
                <span class="form-desc">{{ t('setup.timezoneDesc') }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('setup.dataRetention') }}</label>
                <input
                  v-model.number="configForm.dataRetentionDays"
                  type="number"
                  class="form-input"
                  min="7"
                  max="3650"
                />
                <span class="form-desc">{{ t('setup.dataRetentionDesc') }}</span>
              </div>

              <div v-if="configError" class="error-msg">{{ configError }}</div>

              <div class="form-actions">
                <button class="btn-default" @click="prevStep">{{ t('setup.prevStep') }}</button>
                <button class="btn-primary" @click="submitConfig" :disabled="saving">
                  <span v-if="saving" class="btn-spinner"></span>
                  {{ saving ? t('setup.saving') : t('setup.saveAndFinish') }}
                </button>
              </div>
            </div>

            <!-- Step 4: 完成 -->
            <div v-if="currentStep === 3" key="complete" class="step-content">
              <div class="complete-icon">
                <svg width="72" height="72" viewBox="0 0 24 24" fill="#52c41a">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <h2 class="complete-title">{{ t('setup.installComplete') }}</h2>
              <p class="complete-desc">
                {{ t('setup.completeDesc1') }}<br />
                {{ t('setup.completeDesc2') }}
              </p>

              <div class="summary-card">
                <div class="summary-item">
                  <span class="summary-label">{{ t('setup.adminAccount') }}</span>
                  <span class="summary-value">{{ adminForm.username }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">{{ t('setup.adminTimeZone') }}</span>
                  <span class="summary-value">{{ configForm.timezone }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">{{ t('setup.dataRetentionLabel') }}</span>
                  <span class="summary-value">{{ configForm.dataRetentionDays }} {{ t('common.day') }}</span>
                </div>
              </div>

              <button class="btn-primary btn-large" @click="goToLogin">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>
                </svg>
                {{ t('setup.loginNow') }}
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { createSetupAdmin, saveSetupConfig } from '@/api'

const { t } = useI18n()
const router = useRouter()

const steps = [
  { label: t('setup.steps.welcome'), desc: t('setup.steps.intro') },
  { label: t('setup.steps.admin'), desc: t('setup.steps.createAccount') },
  { label: t('setup.steps.config'), desc: t('setup.steps.systemSettings') },
  { label: t('setup.steps.complete'), desc: t('setup.steps.installComplete') },
]

const currentStep = ref(0)
const loading = ref(false)
const saving = ref(false)
const setupError = ref('')
const configError = ref('')

const adminForm = reactive({
  username: 'admin',
  fullName: '超级管理员',
  password: '',
  confirmPassword: '',
})

const configForm = reactive({
  timezone: 'Asia/Shanghai',
  dataRetentionDays: 90,
})

const errors = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

function clearErrors() {
  errors.username = ''
  errors.password = ''
  errors.confirmPassword = ''
  setupError.value = ''
  configError.value = ''
}

function nextStep() {
  clearErrors()
  currentStep.value++
}

function prevStep() {
  clearErrors()
  currentStep.value--
}

function validateAdmin() {
  clearErrors()
  let valid = true

  if (!adminForm.username.trim()) {
    errors.username = t('setup.usernameRequired')
    valid = false
  } else if (adminForm.username.trim().length < 2) {
    errors.username = t('setup.usernameMin')
    valid = false
  }

  if (!adminForm.password) {
    errors.password = t('setup.passwordRequired')
    valid = false
  } else if (adminForm.password.length < 6) {
    errors.password = t('setup.passwordMin')
    valid = false
  }

  if (!adminForm.confirmPassword) {
    errors.confirmPassword = t('setup.confirmRequired')
    valid = false
  } else if (adminForm.password !== adminForm.confirmPassword) {
    errors.confirmPassword = t('setup.passwordMismatch')
    valid = false
  }

  return valid
}

async function submitAdmin() {
  if (!validateAdmin()) return
  loading.value = true
  try {
    await createSetupAdmin({
      username: adminForm.username.trim(),
      password: adminForm.password,
      full_name: adminForm.fullName.trim() || '',
    })
    nextStep()
  } catch (e) {
    setupError.value = e?.response?.data?.detail || e.message || t('setup.createAdminFailed')
  } finally {
    loading.value = false
  }
}

async function submitConfig() {
  saving.value = true
  try {
    await saveSetupConfig({
      timezone: configForm.timezone,
      data_retention_days: configForm.dataRetentionDays,
    })
    nextStep()
  } catch (e) {
    configError.value = e?.response?.data?.detail || e.message || t('setup.saveConfigFailed')
  } finally {
    saving.value = false
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
.setup-page {
  height: 100vh;
  display: flex;
  overflow: hidden;
  background: #f0f2f5;
}

.setup-container {
  display: flex;
  width: 100%;
  height: 100%;
  min-height: 100vh;
}

/* ---- 左侧品牌区 ---- */
.setup-left {
  width: 380px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.left-content {
  padding: 0 40px;
  width: 100%;
}

.left-logo {
  max-width: 180px;
  max-height: 60px;
  object-fit: contain;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.left-title {
  font-size: 22px;
  font-weight: 700;
  color: #f0f4ff;
  margin: 0 0 6px;
  letter-spacing: 1px;
}

.left-desc {
  font-size: 13px;
  color: rgba(148, 163, 184, 0.8);
  margin: 0 0 40px;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 14px;
  opacity: 0.4;
  transition: all 0.3s;
}

.step-item.active {
  opacity: 1;
}

.step-item.completed {
  opacity: 0.7;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
  transition: all 0.3s;
}

.step-item.active .step-number {
  border-color: #60a5fa;
  background: #60a5fa;
  color: #fff;
}

.step-item.completed .step-number {
  border-color: #52c41a;
  background: #52c41a;
  color: #fff;
}

.step-text {
  min-width: 0;
}

.step-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.step-desc {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.7);
  margin-top: 2px;
}

/* ---- 右侧内容区 ---- */
.setup-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 40px;
}

.setup-card {
  width: 520px;
  max-width: 100%;
  background: #fff;
  border-radius: 12px;
  padding: 48px 44px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 欢迎页 */
.welcome-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0;
}

.welcome-desc {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  line-height: 1.8;
  margin: 0;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px 20px;
}

.feature-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #475569;
}

.feature-check {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

/* 标题 */
.step-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.step-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: -8px 0 4px;
}

/* 表单项 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.required {
  color: #dc2626;
}

.form-input,
.form-select {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #dc2626;
}

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.form-error {
  font-size: 12px;
  color: #dc2626;
}

.form-desc {
  font-size: 12px;
  color: #94a3b8;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.error-msg {
  color: #dc2626;
  font-size: 13px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 10px 14px;
  border-radius: 8px;
}

/* 按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 42px;
  padding: 0 24px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-default {
  display: inline-flex;
  align-items: center;
  height: 42px;
  padding: 0 24px;
  background: #fff;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-default:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-large {
  height: 48px;
  padding: 0 32px;
  font-size: 15px;
  justify-content: center;
  width: 100%;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 完成页 */
.complete-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.complete-title {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0;
}

.complete-desc {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  line-height: 1.8;
  margin: 0;
}

.summary-card {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 13px;
  color: #64748b;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式 */
@media (max-width: 768px) {
  .setup-left {
    display: none;
  }
  .setup-right {
    padding: 20px;
  }
  .setup-card {
    padding: 32px 24px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
