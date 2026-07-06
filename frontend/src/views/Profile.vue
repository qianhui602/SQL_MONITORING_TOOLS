<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人设置</h2>
    </div>

    <div v-if="message" :class="['message-toast', messageType === 'error' ? 'error' : 'success']">
      {{ message }}
    </div>

    <div class="profile-content">
      <!-- 基本信息 -->
      <div class="profile-card">
        <div class="card-header">
          <h3>基本信息</h3>
        </div>
        <div class="card-body">
          <div class="info-row">
            <div class="info-item">
              <label class="info-label">用户名</label>
              <div class="info-value readonly">{{ userInfo.username }}</div>
            </div>
            <div class="info-item">
              <label class="info-label">角色</label>
              <div class="info-value readonly">
                <span class="role-tag" :class="roleClass">{{ roleLabel }}</span>
              </div>
            </div>
          </div>

          <div class="form-divider"></div>

          <div class="form-group">
            <label class="form-label">姓名</label>
            <input
              type="text"
              v-model="form.full_name"
              class="form-input"
              placeholder="请输入姓名"
              maxlength="100"
            />
            <span class="form-hint">显示在顶部栏和邮件通知中</span>
          </div>

          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input
              type="email"
              v-model="form.email"
              class="form-input"
              placeholder="请输入邮箱地址"
              maxlength="200"
            />
            <span class="form-hint">用于接收告警通知和密码重置邮件</span>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
              {{ saving ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="profile-card">
        <div class="card-header">
          <h3>修改密码</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input
              :type="showOldPassword ? 'text' : 'password'"
              v-model="passwordForm.old_password"
              class="form-input"
              placeholder="请输入当前密码"
              autocomplete="current-password"
            />
          </div>

          <div class="form-group">
            <label class="form-label">新密码</label>
            <input
              :type="showNewPassword ? 'text' : 'password'"
              v-model="passwordForm.new_password"
              class="form-input"
              placeholder="请输入新密码（至少 6 位）"
              autocomplete="new-password"
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              v-model="passwordForm.confirm_password"
              class="form-input"
              placeholder="请再次输入新密码"
              autocomplete="new-password"
              minlength="6"
            />
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="changePassword" :disabled="pwdSaving">
              {{ pwdSaving ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getMe, updateProfile, changePassword as changePasswordApi } from '@/api'
import { authStore } from '@/stores/auth'

const userInfo = ref({
  id: 0,
  username: '',
  role: '',
  full_name: '',
  email: '',
  is_active: true,
  last_login_at: null
})

const form = reactive({
  full_name: '',
  email: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const saving = ref(false)
const pwdSaving = ref(false)
const message = ref('')
const messageType = ref('success')
let messageTimer = null

const roleLabel = computed(() => {
  const map = {
    super_admin: '超级管理员',
    admin: '管理员',
    viewer: '只读用户'
  }
  return map[userInfo.value.role] || userInfo.value.role
})

const roleClass = computed(() => {
  const r = userInfo.value.role
  return {
    super_admin: 'role-purple',
    admin: 'role-blue',
    viewer: 'role-gray'
  }[r] || 'role-gray'
})

function showMessage(msg, type = 'success') {
  message.value = msg
  messageType.value = type
  if (messageTimer) clearTimeout(messageTimer)
  messageTimer = setTimeout(() => { message.value = '' }, 3000)
}

async function fetchProfile() {
  try {
    const data = await getMe()
    userInfo.value = data
    form.full_name = data.full_name || ''
    form.email = data.email || ''
  } catch (e) {
    console.error('获取个人信息失败', e)
  }
}

async function saveProfile() {
  if (saving.value) return
  saving.value = true
  try {
    const data = await updateProfile({
      full_name: form.full_name.trim() || null,
      email: form.email.trim() || null
    })
    userInfo.value = data
    if (authStore.state.user) {
      authStore.state.user.full_name = data.full_name
      authStore.state.user.email = data.email
    }
    showMessage('个人信息已更新')
  } catch (e) {
    showMessage(e?.response?.data?.detail || e.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  if (pwdSaving.value) return

  if (!passwordForm.old_password) {
    showMessage('请输入当前密码', 'error')
    return
  }
  if (passwordForm.new_password.length < 6) {
    showMessage('新密码长度不能少于 6 位', 'error')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    showMessage('两次输入的新密码不一致', 'error')
    return
  }

  pwdSaving.value = true
  try {
    await changePasswordApi(passwordForm.old_password, passwordForm.new_password)
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    showMessage('密码修改成功')
  } catch (e) {
    showMessage(e?.response?.data?.detail || e.message || '修改失败', 'error')
  } finally {
    pwdSaving.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-page {
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

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 720px;
}

.profile-card {
  background: var(--bg-card);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  font-size: 15px;
  color: #1890ff;
  font-weight: 600;
}

.card-body {
  padding: 20px;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.info-value.readonly {
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

.role-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid transparent;
}

.role-purple { background: #f9f0ff; color: #722ed1; border-color: #d3adf7; }
.role-blue   { background: #e6f4ff; color: #1677ff; border-color: #91caff; }
.role-gray   { background: #f5f5f5; color: #666;    border-color: #d9d9d9; }

.form-divider {
  height: 1px;
  background: var(--border-color);
  margin: 20px 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.form-hint {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.form-actions {
  margin-top: 24px;
}

.btn {
  padding: 8px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #096dd9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Dark theme */
[data-theme='dark'] .profile-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

[data-theme='dark'] .card-header {
  border-bottom-color: #334155;
}

[data-theme='dark'] .card-header h3 {
  color: #60a5fa;
}

[data-theme='dark'] .form-input {
  background: #0f172a;
  border-color: #334155;
  color: #e2e8f0;
}

[data-theme='dark'] .form-input:focus {
  border-color: #60a5fa;
}

[data-theme='dark'] .form-divider {
  background: #334155;
}

/* Responsive */
@media (max-width: 768px) {
  .info-row {
    grid-template-columns: 1fr;
  }
  .profile-content {
    max-width: 100%;
  }
}
</style>
