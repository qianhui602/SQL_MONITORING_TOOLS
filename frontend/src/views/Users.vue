<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <button class="btn btn-primary" @click="openCreateDialog">+ 新建用户</button>
    </div>

    <div class="card">
      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>姓名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9" class="empty">加载中...</td>
          </tr>
          <tr v-else-if="users.length === 0">
            <td colspan="9" class="empty">暂无用户</td>
          </tr>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.full_name || '-' }}</td>
            <td>{{ u.email || '-' }}</td>
            <td>
              <span class="tag" :class="roleClass(u.role)">{{ roleLabel(u.role) }}</span>
            </td>
            <td>
              <span class="tag" :class="u.is_active ? 'tag-success' : 'tag-error'">
                {{ u.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ formatDate(u.last_login_at) }}</td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <button
                class="btn-text"
                @click="openEditDialog(u)"
                :disabled="!canEdit(u)"
              >
                编辑
              </button>
              <button
                v-if="authStore.isSuperAdmin.value"
                class="btn-text btn-danger"
                @click="onDelete(u)"
                :disabled="!canDelete(u)"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 编辑/新建对话框 -->
    <div v-if="showDialog" class="modal-mask" @click.self="closeDialog">
      <div class="modal">
        <div class="modal-header">
          {{ dialogMode === 'create' ? '新建用户' : '编辑用户' }}
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>用户名</label>
            <input
              v-model="form.username"
              :disabled="dialogMode === 'edit'"
              placeholder="2-50 字符"
            />
          </div>
          <div class="form-row">
            <label>姓名</label>
            <input v-model="form.full_name" placeholder="可选" />
          </div>
          <div class="form-row">
            <label>邮箱（用于接收欢迎邮件和告警通知）</label>
            <input v-model="form.email" type="email" placeholder="user@example.com" />
          </div>
          <div class="form-row">
            <label>{{ dialogMode === 'create' ? '密码' : '重置密码（留空则不修改）' }}</label>
            <input v-model="form.password" type="password" placeholder="至少 6 位" />
          </div>
          <div class="form-row">
            <label>角色</label>
            <select v-model="form.role" :disabled="!authStore.isSuperAdmin.value && form.role !== 'viewer'">
              <option value="viewer">只读用户</option>
              <option value="admin" :disabled="!authStore.isSuperAdmin.value">管理员</option>
              <option v-if="dialogMode === 'edit' && form.role === 'super_admin'" value="super_admin" disabled>
                超级管理员
              </option>
            </select>
          </div>
          <div class="form-row" v-if="dialogMode === 'edit' && form.role !== 'super_admin'">
            <label>状态</label>
            <select v-model="form.is_active">
              <option :value="true">启用</option>
              <option :value="false">禁用</option>
            </select>
          </div>
          <div v-if="dialogError" class="error-msg">{{ dialogError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeDialog">取消</button>
          <button class="btn btn-primary" @click="onSubmit" :disabled="submitting">
            {{ submitting ? '提交中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  listUsers,
  createUser,
  updateUser,
  deleteUser
} from '@/api'
import { authStore } from '@/stores/auth'
import { formatDateTime } from '@/utils/datetime'

const users = ref([])
const loading = ref(false)
const showDialog = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const dialogError = ref('')
const editingId = ref(null)

const form = reactive({
  username: '',
  password: '',
  full_name: '',
  email: '',
  role: 'viewer',
  is_active: true
})

function roleLabel(role) {
  return (
    { super_admin: '超级管理员', admin: '管理员', viewer: '只读用户' }[role] ||
    role
  )
}

function roleClass(role) {
  return {
    super_admin: 'tag-purple',
    admin: 'tag-blue',
    viewer: 'tag-gray'
  }[role] || 'tag-gray'
}

function formatDate(d) {
  return formatDateTime(d, { second: true })
}

function canEdit(u) {
  // 超级管理员不可被普通管理员编辑
  if (u.role === 'super_admin' && !authStore.isSuperAdmin.value) return false
  return true
}

function canDelete(u) {
  if (u.role === 'super_admin') return false
  if (authStore.state.user && u.id === authStore.state.user.id) return false
  return true
}

async function loadUsers() {
  loading.value = true
  try {
    users.value = await listUsers()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingId.value = null
  Object.assign(form, {
    username: '',
    password: '',
    full_name: '',
    email: '',
    role: 'viewer',
    is_active: true
  })
  dialogError.value = ''
  showDialog.value = true
}

function openEditDialog(u) {
  dialogMode.value = 'edit'
  editingId.value = u.id
  Object.assign(form, {
    username: u.username,
    password: '',
    full_name: u.full_name || '',
    email: u.email || '',
    role: u.role,
    is_active: u.is_active
  })
  dialogError.value = ''
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

async function onSubmit() {
  dialogError.value = ''
  if (dialogMode.value === 'create') {
    if (!form.username || form.username.length < 2) {
      dialogError.value = '用户名至少 2 个字符'
      return
    }
    if (!form.password || form.password.length < 6) {
      dialogError.value = '密码至少 6 位'
      return
    }
  } else if (form.password && form.password.length < 6) {
    dialogError.value = '新密码至少 6 位'
    return
  }

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createUser({
        username: form.username,
        password: form.password,
        role: form.role,
        full_name: form.full_name || null,
        email: form.email || null
      })
    } else {
      const payload = {
        role: form.role,
        full_name: form.full_name || null,
        email: form.email || null,
        is_active: form.is_active
      }
      if (form.password) payload.password = form.password
      await updateUser(editingId.value, payload)
    }
    showDialog.value = false
    await loadUsers()
  } catch (e) {
    dialogError.value = e?.response?.data?.detail || '操作失败'
  } finally {
    submitting.value = false
  }
}

async function onDelete(u) {
  if (!confirm(`确定要删除用户 "${u.username}" 吗？`)) return
  try {
    await deleteUser(u.id)
    await loadUsers()
  } catch (e) {
    alert(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.users-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  font-size: 20px;
  color: #001529;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 16px;
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.user-table th,
.user-table td {
  text-align: left;
  padding: 12px 14px;
  border-bottom: 1px solid #f0f0f0;
}

.user-table thead th {
  background: #fafafa;
  font-weight: 600;
  color: #555;
}

.user-table tbody tr:hover {
  background: #f9fbff;
}

.empty {
  text-align: center;
  color: #999;
  padding: 32px 0;
}

.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  border: 1px solid transparent;
}
.tag-purple { background:#f9f0ff; color:#722ed1; border-color:#d3adf7; }
.tag-blue   { background:#e6f4ff; color:#1677ff; border-color:#91caff; }
.tag-gray   { background:#f5f5f5; color:#666;    border-color:#d9d9d9; }
.tag-success{ background:#f6ffed; color:#52c41a; border-color:#b7eb8f; }
.tag-error  { background:#fff1f0; color:#ff4d4f; border-color:#ffa39e; }

.btn,
.btn-text {
  border: none;
  cursor: pointer;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 4px;
  background: #f5f5f5;
  color: #333;
  margin-right: 6px;
}

.btn-text {
  background: transparent;
  color: #1890ff;
  padding: 0 6px;
}
.btn-text:hover:not(:disabled) { text-decoration: underline; }
.btn-text:disabled { color:#ccc; cursor:not-allowed; }

.btn-primary {
  background: #1890ff;
  color: #fff;
}
.btn-primary:hover:not(:disabled) { background: #096dd9; }

.btn-danger { color: #ff4d4f; }
.btn:disabled, .btn-primary:disabled { opacity:0.6; cursor:not-allowed; }

/* ---- Modal ---- */
.modal-mask {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex; align-items:center; justify-content:center;
  z-index: 1000;
}
.modal {
  background: #fff;
  border-radius: 8px;
  width: 460px;
  max-width: 92vw;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
.modal-header {
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
}
.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.form-row label {
  display:block;
  font-size: 13px;
  color: #555;
  margin-bottom: 6px;
}
.form-row input,
.form-row select {
  width: 100%;
  height: 36px;
  padding: 0 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  background: #fff;
}
.form-row input:focus,
.form-row select:focus {
  border-color: #1890ff;
}
.form-row input:disabled,
.form-row select:disabled {
  background: #f5f5f5; color:#999;
}

.error-msg {
  color: #ff4d4f;
  font-size: 13px;
  background: #fff1f0;
  border: 1px solid #ffa39e;
  border-radius: 4px;
  padding: 6px 10px;
}
</style>
