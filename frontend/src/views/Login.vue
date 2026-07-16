<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-left">
      <div class="bg-decoration"></div>
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
      <div class="bg-grid"></div>
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

    <!-- 右侧登录区 -->
    <div class="login-right">
      <div class="login-card">
        <h2 class="login-title">{{ t('login.welcome') }}</h2>
        <p class="login-subtitle">{{ t('login.subtitle') }}</p>

        <form class="login-form" @submit.prevent="onSubmit">
          <div class="form-item">
            <label>{{ t('login.username') }}</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </span>
              <input
                v-model="form.username"
                type="text"
                autocomplete="username"
                :placeholder="t('login.usernamePlaceholder')"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <div class="form-item">
            <label>{{ t('login.password') }}</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              </span>
              <input
                v-model="form.password"
                type="password"
                autocomplete="current-password"
                :placeholder="t('login.passwordPlaceholder')"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <div class="forgot-password-row">
            <router-link to="/forgot-password" class="forgot-link">{{ t('login.forgotPassword') }}</router-link>
          </div>

          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            {{ loading ? t('login.logging') : t('login.loginButton') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { authStore } from '@/stores/auth'
import { getConfig, getLogoUrl } from '@/api'

const { t } = useI18n()

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const errorMsg = ref('')

const brandTitle = ref('数据库监控平台')
const customLogoUrl = ref('')

const form = reactive({
  username: '',
  password: ''
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
    console.debug('品牌配置获取失败（首次安装或无配置）')
  }
}

async function onSubmit() {
  if (loading.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    const redirect = route.query.redirect || '/dashboard'
    router.replace(redirect)
  } catch (e) {
    errorMsg.value =
      e?.response?.data?.detail || e.message || t('login.loginFailed')
  } finally {
    loading.value = false
  }
}

onMounted(fetchBrandConfig)
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* ---- 左侧品牌区 ---- */
.login-left {
  width: 45%;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse 80% 50% at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(59, 130, 246, 0.12) 0%, transparent 50%);
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: circleFloat 20s ease-in-out infinite;
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.4) 0%, transparent 70%);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
  bottom: -80px;
  right: -80px;
  animation-delay: -7s;
}

.bg-circle-3 {
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(147, 51, 234, 0.25) 0%, transparent 70%);
  top: 50%;
  right: 20%;
  animation-delay: -14s;
}

@keyframes circleFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 30px) scale(0.95); }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.4;
}

.left-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 48px;
  animation: contentFadeIn 0.8s ease-out;
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.left-logo {
  max-width: 220px;
  max-height: 80px;
  object-fit: contain;
  margin-bottom: 28px;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.4));
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.left-title {
  font-size: 32px;
  font-weight: 800;
  color: #f8fafc;
  margin: 0 0 10px;
  letter-spacing: 3px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.left-desc {
  font-size: 14px;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 48px;
  letter-spacing: 5px;
}

.left-features {
  display: flex;
  flex-direction: column;
  gap: 18px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
  color: rgba(203, 213, 225, 0.9);
  font-size: 15px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateX(6px);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(59, 130, 246, 0.15));
  color: #818cf8;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.left-footer {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.35);
}

/* ---- 右侧登录区 ---- */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f8fafc 100%);
  position: relative;
  overflow: hidden;
}

.login-right::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.login-card {
  width: 440px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 52px 44px 44px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.6);
  position: relative;
  z-index: 1;
  animation: cardSlideIn 0.6s ease-out;
}

@keyframes cardSlideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6366f1, #3b82f6, #8b5cf6);
  border-radius: 16px 16px 0 0;
}

.login-title {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 40px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  pointer-events: none;
  transition: color 0.3s;
}

.input-wrap input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 44px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  color: #0f172a;
  background: #fafbfc;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-wrap input::placeholder {
  color: #cbd5e1;
}

.input-wrap input:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
}

.input-wrap input:focus + .input-icon {
  color: #6366f1;
}

.error-msg {
  color: #dc2626;
  font-size: 13px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 12px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-msg::before {
  content: '!';
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #dc2626;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.forgot-password-row {
  text-align: right;
  margin-top: -4px;
}

.forgot-link {
  font-size: 13px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.login-btn {
  height: 50px;
  background: linear-gradient(135deg, #6366f1 0%, #3b82f6 50%, #8b5cf6 100%);
  background-size: 200% 200%;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 2px;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.login-btn:hover:not(:disabled) {
  background-position: 100% 100%;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
  box-shadow: none;
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

/* ---- 响应式 ---- */
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
