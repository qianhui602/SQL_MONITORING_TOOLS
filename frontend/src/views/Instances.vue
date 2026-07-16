<template>
  <div class="instances-page">
    <div class="page-header">
      <h2>{{ t('instances.title') }}</h2>
      <button class="btn btn-primary" @click="openCreateDialog">{{ t('instances.addInstance') }}</button>
    </div>

    <div class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ t('instances.instanceName') }}</th>
            <th>{{ t('instances.serverAddress') }}</th>
            <th>{{ t('instances.port') }}</th>
            <th>{{ t('instances.connectionStatus') }}</th>
            <th>{{ t('instances.lastConnectTime') }}</th>
            <th>{{ t('instances.lastCollectTime') }}</th>
            <th>{{ t('common.operation') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="empty-cell">{{ t('common.loading') }}</td>
          </tr>
          <tr v-else-if="instances.length === 0">
            <td colspan="7" class="empty-cell">{{ t('instances.noInstances') }}</td>
          </tr>
          <tr v-for="inst in instances" :key="inst.id">
            <td>{{ inst.name }}</td>
            <td>{{ inst.host }}</td>
            <td>{{ inst.port }}</td>
            <td>
              <span v-if="inst.is_active" :class="['status-indicator', inst.is_connected ? 'status-active' : 'status-error']"
                    :title="inst.is_connected ? '' : (inst.connection_error || t('common.connectError'))">
                <span class="status-dot"></span>
                {{ inst.is_connected ? t('common.online') : t('common.offline') }}
              </span>
              <span v-else class="status-inactive">
                <span class="status-dot"></span>
                {{ t('common.disabledStatus') }}
              </span>
            </td>
            <td>{{ inst.last_connected_at ? formatDate(inst.last_connected_at) : '-' }}</td>
            <td>{{ formatDate(inst.last_collect_at) }}</td>
            <td>
              <button class="btn-text" @click="openEditDialog(inst)">{{ t('common.edit') }}</button>
              <button class="btn-text btn-test" @click="onTestConnection(inst)">{{ t('instances.testConnection') }}</button>
              <button class="btn-text btn-danger" @click="onDelete(inst)">{{ t('common.delete') }}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Toast 消息 -->
    <div v-if="toast.visible" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showDialog" class="modal-mask" @click.self="closeDialog">
      <div class="modal">
        <div class="modal-header">
          {{ dialogMode === 'create' ? t('instances.addTitle') : t('instances.editTitle') }}
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>{{ t('instances.instanceName') }} <span class="required">*</span></label>
            <input v-model="form.name" :placeholder="t('instances.namePlaceholder')" />
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('instances.hostAddress') }} <span class="required">*</span></label>
              <input v-model="form.host" :placeholder="t('instances.hostPlaceholder')" />
            </div>
            <div class="form-row">
              <label>{{ t('instances.port') }}</label>
              <input v-model.number="form.port" type="number" placeholder="1433" />
            </div>
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('instances.username') }}</label>
              <input v-model="form.username" :placeholder="t('instances.usernamePlaceholder')" />
            </div>
            <div class="form-row">
              <label>{{ t('instances.password') }}</label>
              <input v-model="form.password" type="password" :placeholder="dialogMode === 'edit' ? t('instances.passwordPlaceholder') : t('instances.password')" />
            </div>
          </div>
          <div class="form-row">
            <label>{{ t('instances.database') }}</label>
            <input v-model="form.database" :placeholder="t('instances.dbPlaceholder')" />
          </div>
          <div class="form-row">
            <label>{{ t('alertRules.description') }}</label>
            <input v-model="form.description" :placeholder="t('common.optional')" />
          </div>
          <div class="form-row" v-if="dialogMode === 'edit'">
            <label>{{ t('instances.enableStatus') }}</label>
            <select v-model="form.is_active">
              <option :value="true">{{ t('common.enable') }}</option>
              <option :value="false">{{ t('common.disable') }}</option>
            </select>
          </div>
          <div v-if="dialogError" class="error-msg">{{ dialogError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="closeDialog">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="onSubmit" :disabled="submitting">
            {{ submitting ? t('common.submit') : t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getInstances, createInstance, updateInstance, deleteInstance, testInstanceConnection } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const { t } = useI18n()

const instances = ref([])
const loading = ref(false)
const showDialog = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const dialogError = ref('')
const editingId = ref(null)

const form = reactive({
  name: '',
  host: '',
  port: 1433,
  username: '',
  password: '',
  database: 'master',
  description: '',
  is_active: true
})

const toast = reactive({
  visible: false,
  message: '',
  type: 'success'
})

let toastTimer = null

function formatDate(d) {
  return formatDateTime(d, { second: true })
}

function showToast(message, type = 'success') {
  toast.visible = true
  toast.message = message
  toast.type = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.visible = false }, 4000)
}

async function fetchInstances() {
  loading.value = true
  try {
    const data = await getInstances()
    instances.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    console.error('获取实例列表失败', e)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    name: '',
    host: '',
    port: 1433,
    username: '',
    password: '',
    database: 'master',
    description: '',
    is_active: true
  })
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingId.value = null
  resetForm()
  dialogError.value = ''
  showDialog.value = true
}

function openEditDialog(inst) {
  dialogMode.value = 'edit'
  editingId.value = inst.id
  Object.assign(form, {
    name: inst.name,
    host: inst.host,
    port: inst.port,
    username: inst.username || '',
    password: '',
    database: inst.database || 'master',
    description: inst.description || '',
    is_active: inst.is_active
  })
  dialogError.value = ''
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

async function onSubmit() {
  dialogError.value = ''
  if (!form.name) { dialogError.value = t('instances.nameRequired'); return }
  if (!form.host) { dialogError.value = t('instances.hostRequired'); return }

  submitting.value = true
  try {
    const payload = {
      name: form.name,
      host: form.host,
      port: form.port,
      username: form.username || null,
      database: form.database || 'master',
      description: form.description || null,
      is_active: form.is_active
    }
    if (form.password) payload.password = form.password

    if (dialogMode.value === 'create') {
      await createInstance(payload)
    } else {
      await updateInstance(editingId.value, payload)
    }
    showDialog.value = false
    await fetchInstances()
  } catch (e) {
    dialogError.value = e?.response?.data?.detail || t('common.operationFailed')
  } finally {
    submitting.value = false
  }
}

async function onDelete(inst) {
  if (!confirm(t('common.confirmDelete', { name: inst.name }))) return
  try {
    await deleteInstance(inst.id)
    await fetchInstances()
  } catch (e) {
    alert(e?.response?.data?.detail || t('common.deleteFailed'))
  }
}

async function onTestConnection(inst) {
  try {
    const data = await testInstanceConnection(inst.id)
    if (data && data.success !== false) {
      showToast(t('instances.connectSuccess') + `${inst.name} (${inst.host}:${inst.port})`, 'success')
    } else {
      showToast(t('instances.connectFailed') + ` ${data?.error || t('instances.unknownError')}`, 'error')
    }
  } catch (e) {
    const detail = e?.response?.data?.detail || e?.response?.data?.error || e.message
    showToast(t('instances.connectFailed') + ` ${detail}`, 'error')
  }
}

onMounted(fetchInstances)
</script>

<style scoped>
.instances-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #001529;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  background: #fafafa;
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.data-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #f0f0f0;
  color: #555;
}

.data-table tbody tr:hover {
  background: #f9fbff;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: #999;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-active .status-dot {
  background: #52c41a;
  box-shadow: 0 0 4px rgba(82, 196, 26, 0.5);
}

.status-inactive .status-dot {
  background: #d9d9d9;
}

.status-active {
  color: #52c41a;
}

.status-error .status-dot {
  background: #ff4d4f;
  box-shadow: 0 0 4px rgba(255, 77, 79, 0.5);
}

.status-error {
  color: #ff4d4f;
}

.status-inactive {
  color: #999;
}

.btn, .btn-text {
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

.btn-primary {
  background: #1890ff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) { background: #096dd9; }

.btn-danger { color: #ff4d4f; }

.btn-test { color: #52c41a; }

.btn:disabled, .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

/* Toast */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 14px;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.toast.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #f5222d;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* Modal */
.modal-mask {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 92vw;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
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
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.form-row label {
  display: block;
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
  box-sizing: border-box;
}

.form-row input:focus,
.form-row select:focus {
  border-color: #1890ff;
}

.form-row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.required {
  color: #ff4d4f;
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
