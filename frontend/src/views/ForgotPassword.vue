<template>
  <div class="login-page">
    <div class="login-left">
      <div class="left-content">
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="left-logo" />
        <h1 class="left-title">{{ brandTitle }}</h1>
        <p class="left-desc">{{ t('login.slogan') }}</p>
        <div class="left-features">
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
            </span>
            <span>{{ t('login.feature1') }}</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </span>
            <span>{{ t('login.feature2') }}</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <span>{{ t('login.feature3') }}</span>
          </div>
        </div>
      </div>
      <div class="left-footer">{{ t('login.copyright') }} &copy; 2026</div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <!-- 步骤 1：输入邮箱 -->
        <template v-if="step === 1">
          <h2 class="login-title">{{ t('forgotPassword.title') }}</h2>
          <p class="login-subtitle">{{ t('forgotPassword.subtitle') }}</p>

          <form class="login-form" @submit.prevent="sendCode">
            <div class="form-item">
              <label>{{ t('forgotPassword.email') }}</label>
              <div class="input-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                </span>
                <input
                  v-model="email"
                  type="email"
                  autocomplete="email"
                  :placeholder="t('forgotPassword.emailPlaceholder')"
                  :disabled="loading"
                  required
                />
              </div>
            </div>

            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? t('forgotPassword.sending') : t('forgotPassword.sendCode') }}
            </button>

            <p class="form-footer">
              {{ t('forgotPassword.rememberPassword') }}
              <router-link to="/login" class="link">{{ t('forgotPassword.backToLogin') }}</router-link>
            </p>
          </form>
        </template>

        <!-- 步骤 2：输入验证码和新密码 -->
        <template v-else-if="step === 2">
          <h2 class="login-title">{{ t('forgotPassword.resetTitle') }}</h2>
          <p class="login-subtitle">{{ t('forgotPassword.codeSentTo') }} <strong>{{ email }}</strong></p>

          <form class="login-form" @submit.prevent="onReset">
            <div class="form-item">
              <label>{{ t('forgotPassword.code') }}</label>
              <div class="input-wrap code-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4"/><path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/></svg>
                </span>
                <input
                  v-model="code"
                  type="text"
                  inputmode="numeric"
                  maxlength="6"
                  :placeholder="t('forgotPassword.codePlaceholder')"
                  :disabled="loading"
                  required
                  class="code-input"
                />
                <button type="button" class="resend-btn" :disabled="countdown > 0 || loading" @click="sendCode">
                  {{ countdown > 0 ? `${countdown}s` : t('forgotPassword.resend') }}
                </button>
              </div>
            </div>

            <div class="form-item">
              <label>{{ t('forgotPassword.newPassword') }}</label>
              <div class="input-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  :placeholder="t('forgotPassword.newPasswordPlaceholder')"
                  :disabled="loading"
                  required
                  minlength="6"
                />
                <button type="button" class="toggle-pwd" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <div class="form-item">
              <label>{{ t('forgotPassword.confirmPassword') }}</label>
              <div class="input-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  v-model="confirmPassword"
                  :type="showConfirm ? 'text' : 'password'"
                  autocomplete="new-password"
                  :placeholder="t('forgotPassword.confirmPasswordPlaceholder')"
                  :disabled="loading"
                  required
                  minlength="6"
                />
                <button type="button" class="toggle-pwd" @click="showConfirm = !showConfirm">
                  <svg v-if="!showConfirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? t('forgotPassword.resetting') : t('forgotPassword.confirmReset') }}
            </button>

            <p class="form-footer">
              <a href="#" class="link" @click.prevent="step = 1">{{ t('forgotPassword.backToPrev') }}</a>
            </p>
          </form>
        </template>

        <!-- 步骤 3：成功 -->
        <div v-else class="success-state">
          <div class="success-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h3 class="success-title">{{ t('forgotPassword.resetSuccess') }}</h3>
          <p class="success-desc">
            {{ t('forgotPassword.resetSuccessDesc1') }}<br>
            {{ t('forgotPassword.resetSuccessDesc2') }}
          </p>
          <button class="login-btn" @click="goToLogin">{{ t('forgotPassword.loginNow') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { forgotPassword, resetPassword, getConfig, getLogoUrl } from '@/api'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const errorMsg = ref('')
const step = ref(1)

const email = ref('')
const code = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirm = ref(false)
const countdown = ref(0)
let countdownTimer = null

const brandTitle = ref('数据库监控平台')
const customLogoUrl = ref('')

async function fetchBrandConfig() {
  try {
    const title = await getConfig('brand_title')
    if (title) brandTitle.value = title

    const logoUrl = getLogoUrl()
    const resp = await fetch(logoUrl, { method: 'HEAD' })
    if (resp.ok) {
      customLogoUrl.value = logoUrl + '?t=' + Date.now()
    }
  } catch (e) {
    console.debug('品牌配置获取失败')
  }
}

function startCountdown() {
  countdown.value = 60
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

async function sendCode() {
  if (loading.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    await forgotPassword(email.value.trim())
    step.value = 2
    startCountdown()
  } catch (e) {
    errorMsg.value =
      e?.response?.data?.detail || e.message || t('forgotPassword.sendFailed')
  } finally {
    loading.value = false
  }
}

async function onReset() {
  if (loading.value) return

  if (!/^\d{6}$/.test(code.value)) {
    errorMsg.value = t('forgotPassword.codeRequired')
    return
  }
  if (password.value.length < 6) {
    errorMsg.value = t('forgotPassword.passwordMin')
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMsg.value = t('forgotPassword.passwordMismatch')
    return
  }

  errorMsg.value = ''
  loading.value = true
  try {
    await resetPassword(email.value.trim(), code.value.trim(), password.value)
    step.value = 3
  } catch (e) {
    errorMsg.value =
      e?.response?.data?.detail || e.message || t('forgotPassword.resetFailed')
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.replace('/login')
}

onMounted(fetchBrandConfig)

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
})
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

.login-left {
  width: 45%;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: transparent;
  pointer-events: none;
}

.left-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 48px;
}

.left-logo {
  max-width: 220px;
  max-height: 80px;
  object-fit: contain;
  margin-bottom: 24px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.left-title {
  font-size: 28px;
  font-weight: 700;
  color: #f0f4ff;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.left-desc {
  font-size: 14px;
  color: rgba(148, 163, 184, 0.9);
  margin: 0 0 40px;
  letter-spacing: 4px;
}

.left-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(203, 213, 225, 0.85);
  font-size: 14px;
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  flex-shrink: 0;
}

.left-footer {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.4);
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.login-card {
  width: 420px;
  background: #fff;
  border-radius: 8px;
  padding: 48px 40px 40px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px;
}

.login-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0 0 32px;
}

.login-subtitle strong {
  color: #2563eb;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  pointer-events: none;
}

.toggle-pwd {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
}

.toggle-pwd:hover {
  color: #3b82f6;
}

.input-wrap input {
  width: 100%;
  height: 44px;
  padding: 0 40px 0 40px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  transition: all 0.2s;
}

.input-wrap input::placeholder {
  color: #cbd5e1;
}

.input-wrap input:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.code-wrap input {
  padding-right: 70px;
  letter-spacing: 4px;
  font-weight: 600;
}

.resend-btn {
  position: absolute;
  right: 8px;
  height: 30px;
  padding: 0 12px;
  border: none;
  border-radius: 4px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.resend-btn:hover:not(:disabled) {
  background: #dbeafe;
}

.resend-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  color: #dc2626;
  font-size: 13px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 10px 14px;
  border-radius: 8px;
}

.login-btn {
  height: 46px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 2px;
  width: 100%;
}

.login-btn:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
  transform: translateY(-1px);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.form-footer {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0;
}

.link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.success-state {
  text-align: center;
}

.success-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #dcfce7;
  color: #16a34a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.success-title {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 12px;
}

.success-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.8;
  margin: 0 0 24px;
}

@media (max-width: 900px) {
  .login-left {
    display: none;
  }
  .login-right {
    width: 100%;
    background: #0f172a;
  }
  .login-card {
    width: 90%;
    max-width: 400px;
  }
}
</style>
