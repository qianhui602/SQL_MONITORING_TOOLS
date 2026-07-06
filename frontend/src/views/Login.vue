<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
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

    <!-- 右侧登录区 -->
    <div class="login-right">
      <div class="login-card">
        <h2 class="login-title">欢迎登录</h2>
        <p class="login-subtitle">请使用您的账号登录系统</p>

        <form class="login-form" @submit.prevent="onSubmit">
          <div class="form-item">
            <label>用户名</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </span>
              <input
                v-model="form.username"
                type="text"
                autocomplete="username"
                placeholder="请输入用户名"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <div class="form-item">
            <label>密码</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              </span>
              <input
                v-model="form.password"
                type="password"
                autocomplete="current-password"
                placeholder="请输入密码"
                :disabled="loading"
                required
              />
            </div>
          </div>

          <div class="forgot-password-row">
            <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
          </div>

          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authStore } from '@/stores/auth'
import { getConfig, getLogoUrl } from '@/api'

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
      e?.response?.data?.detail || e.message || '登录失败，请稍后再试'
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

/* ---- 右侧登录区 ---- */
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

.input-wrap input {
  width: 100%;
  height: 44px;
  padding: 0 14px 0 40px;
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

.forgot-password-row {
  text-align: right;
  margin-top: -8px;
}

.forgot-link {
  font-size: 13px;
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
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
