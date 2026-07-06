<template>
  <div class="login-page">
    <div class="login-left">
      <div class="left-content">
        <img :src="customLogoUrl || '/LOGO.png'" :alt="brandTitle" class="left-logo" />
        <h1 class="left-title">{{ brandTitle }}</h1>
        <p class="left-desc">实时监控 · 智能告警 · 深度分析</p>
        <div class="left-features">
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>
            </span>
            <span>全方位性能指标监控</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </span>
            <span>智能告警与多渠道通知</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <span>AI 驱动的分析报告</span>
          </div>
        </div>
      </div>
      <div class="left-footer">太阳谷信息技术部 &copy; 2026</div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <h2 class="login-title">重置密码</h2>
        <p class="login-subtitle">请设置您的新密码</p>

        <template v-if="!success">
          <form v-if="token" class="login-form" @submit.prevent="onSubmit">
            <div class="form-item">
              <label>新密码</label>
              <div class="input-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="请输入新密码（至少 6 位）"
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
              <label>确认新密码</label>
              <div class="input-wrap">
                <span class="input-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  v-model="form.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="请再次输入新密码"
                  :disabled="loading"
                  required
                  minlength="6"
                />
                <button type="button" class="toggle-pwd" @click="showConfirmPassword = !showConfirmPassword">
                  <svg v-if="!showConfirmPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
            </div>

            <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading" class="btn-spinner"></span>
              {{ loading ? '重置中...' : '确认重置' }}
            </button>

            <p class="form-footer">
              <router-link to="/login" class="link">返回登录</router-link>
            </p>
          </form>

          <div v-else class="error-state">
            <div class="error-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
            <h3 class="error-title">无效的重置链接</h3>
            <p class="error-desc">
              重置链接无效或已过期。<br>
              请重新申请密码重置。
            </p>
            <button class="login-btn" @click="goToForgotPassword">重新申请</button>
          </div>
        </template>

        <div v-else class="success-state">
          <div class="success-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h3 class="success-title">密码重置成功</h3>
          <p class="success-desc">
            您的密码已成功重置。<br>
            请使用新密码重新登录系统。
          </p>
          <button class="login-btn" @click="goToLogin">立即登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { resetPassword, getConfig, getLogoUrl } from '@/api'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const errorMsg = ref('')
const success = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const brandTitle = ref('数据库监控平台')
const customLogoUrl = ref('')

const token = ref(route.query.token || '')

const form = reactive({
  password: '',
  confirmPassword: ''
})

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

async function onSubmit() {
  if (loading.value) return

  if (form.password.length < 6) {
    errorMsg.value = '密码长度不能少于 6 位'
    return
  }

  if (form.password !== form.confirmPassword) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  errorMsg.value = ''
  loading.value = true
  try {
    await resetPassword(token.value, form.password)
    success.value = true
  } catch (e) {
    errorMsg.value =
      e?.response?.data?.detail || e.message || '重置失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.replace('/login')
}

function goToForgotPassword() {
  router.replace('/forgot-password')
}

onMounted(fetchBrandConfig)
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

.success-state,
.error-state {
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

.error-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fee2e2;
  color: #dc2626;
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

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 12px;
}

.success-desc,
.error-desc {
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
