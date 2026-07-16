<template>
  <div class="alert-rules-page">
    <div class="page-header">
      <h2>{{ t('alertRules.title') }}</h2>
      <button class="btn btn-primary" @click="openCreateDialog">{{ t('alertRules.addRule') }}</button>
    </div>

    <div class="card">
      <table class="data-table">
        <thead>
          <tr>
            <th>{{ t('alertRules.ruleName') }}</th>
            <th>{{ t('alertRules.metricCategory') }}</th>
            <th>{{ t('alertRules.metricName') }}</th>
            <th>{{ t('alertRules.condition') }}</th>
            <th>{{ t('alertRules.severity') }}</th>
            <th>{{ t('alertRules.notifyMethod') }}</th>
            <th>{{ t('alertRules.status') }}</th>
            <th>{{ t('common.operation') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8" class="empty-cell">{{ t('common.loading') }}</td>
          </tr>
          <tr v-else-if="rules.length === 0">
            <td colspan="8" class="empty-cell">{{ t('alertRules.noRules') }}</td>
          </tr>
          <tr v-for="rule in rules" :key="rule.id" @click="openEditDialog(rule)" style="cursor:pointer">
            <td>{{ rule.name }}</td>
            <td>
              <span class="tag tag-blue">{{ rule.metric_category }}</span>
            </td>
            <td class="col-break">{{ rule.metric_name }}</td>
            <td>
              <span class="condition-text">
                {{ operatorLabel(rule.operator) }} {{ rule.threshold }}
              </span>
            </td>
            <td>
              <span class="severity-tag" :class="severityClass(rule.severity)">
                {{ rule.severity }}
              </span>
            </td>
            <td>
              <div class="notify-tags">
                <span v-for="m in (rule.notification_method || [])" :key="m" class="tag tag-gray">
                  {{ notifyLabel(m) }}
                </span>
                <span v-if="!rule.notification_method || rule.notification_method.length === 0" class="tag tag-gray">-</span>
              </div>
            </td>
            <td @click.stop>
              <label class="switch">
                <input
                  type="checkbox"
                  :checked="rule.is_active"
                  @change="onToggle(rule)"
                />
                <span class="switch-slider"></span>
              </label>
            </td>
            <td @click.stop>
              <button class="btn-text btn-danger" @click="onDelete(rule)">{{ t('common.delete') }}</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑对话框 -->
    <div v-if="showDialog" class="modal-mask" @click.self="closeDialog">
      <div class="modal modal-wide">
        <div class="modal-header">
          {{ dialogMode === 'create' ? t('alertRules.addTitle') : t('alertRules.editTitle') }}
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label>{{ t('alertRules.ruleName') }} <span class="required">*</span></label>
            <input v-model="form.name" :placeholder="t('alertRules.namePlaceholder')" />
          </div>
          <div class="form-row">
            <label>{{ t('alertRules.description') }}</label>
            <textarea v-model="form.description" :placeholder="t('common.optional')" rows="2"></textarea>
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('alertRules.metricCategory') }} <span class="required">*</span></label>
              <select v-model="form.metric_category">
                <option value="">{{ t('alertRules.pleaseSelect') }}</option>
                <option value="performance">{{ t('alertRules.performance') }}</option>
                <option value="memory">{{ t('alertRules.memory') }}</option>
                <option value="disk">{{ t('alertRules.disk') }}</option>
                <option value="deadlock">{{ t('alertRules.deadlock') }}</option>
                <option value="connection">{{ t('alertRules.connection') }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>{{ t('alertRules.metricName') }} <span class="required">*</span></label>
              <input v-model="form.metric_name" :placeholder="t('alertRules.metricPlaceholder')" />
            </div>
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('alertRules.operator') }}</label>
              <select v-model="form.operator">
                <option value="gt">{{ t('alertRules.gt') }}</option>
                <option value="lt">{{ t('alertRules.lt') }}</option>
                <option value="gte">{{ t('alertRules.gte') }}</option>
                <option value="lte">{{ t('alertRules.lte') }}</option>
                <option value="eq">{{ t('alertRules.eq') }}</option>
              </select>
            </div>
            <div class="form-row">
              <label>{{ t('alertRules.threshold') }} <span class="required">*</span></label>
              <input v-model.number="form.threshold" type="number" :placeholder="t('alertRules.threshold')" />
            </div>
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('alertRules.severity') }} <span class="required">*</span></label>
              <select v-model="form.severity">
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div class="form-row">
              <label>{{ t('alertRules.cooldown') }}</label>
              <input v-model.number="form.cooldown_minutes" type="number" min="0" placeholder="0" />
            </div>
          </div>
          <div class="form-row">
            <label>{{ t('alertRules.notifyMethod') }}</label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" value="email" v-model="form.notification_method" />
                <span>{{ t('alertRules.email') }}</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" value="dingtalk" v-model="form.notification_method" />
                <span>{{ t('alertRules.dingtalk') }}</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" value="wechat" v-model="form.notification_method" />
                <span>{{ t('alertRules.wecom') }}</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" value="feishu" v-model="form.notification_method" />
                <span>{{ t('alertRules.feishu') }}</span>
              </label>
            </div>
          </div>
          <div class="form-row-2col">
            <div class="form-row">
              <label>{{ t('alertRules.silentStart') }}</label>
              <input type="time" v-model="form.silent_start" />
            </div>
            <div class="form-row">
              <label>{{ t('alertRules.silentEnd') }}</label>
              <input type="time" v-model="form.silent_end" />
            </div>
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
import { getAlertRules, createAlertRule, updateAlertRule, deleteAlertRule, toggleAlertRule } from '@/api'

const { t } = useI18n()

const rules = ref([])
const loading = ref(false)
const showDialog = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const dialogError = ref('')
const editingId = ref(null)

const form = reactive({
  name: '',
  description: '',
  metric_category: '',
  metric_name: '',
  operator: 'gt',
  threshold: null,
  severity: 'medium',
  cooldown_minutes: 0,
  notification_method: [],
  silent_start: '',
  silent_end: ''
})

function operatorLabel(op) {
  const map = { gt: '>', lt: '<', gte: '>=', lte: '<=', eq: '=' }
  return map[op] || op
}

function notifyLabel(m) {
  const map = { email: t('alertRules.email'), dingtalk: t('alertRules.dingtalk'), wechat: t('alertRules.wecom'), feishu: t('alertRules.feishu') }
  return map[m] || m
}

function severityClass(s) {
  const map = { critical: 'sev-critical', high: 'sev-high', medium: 'sev-medium', low: 'sev-low' }
  return map[s] || ''
}

async function fetchRules() {
  loading.value = true
  try {
    const data = await getAlertRules()
    rules.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    console.error('获取告警规则失败', e)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    name: '',
    description: '',
    metric_category: '',
    metric_name: '',
    operator: 'gt',
    threshold: null,
    severity: 'medium',
    cooldown_minutes: 0,
    notification_method: [],
    silent_start: '',
    silent_end: ''
  })
}

function openCreateDialog() {
  dialogMode.value = 'create'
  editingId.value = null
  resetForm()
  dialogError.value = ''
  showDialog.value = true
}

function openEditDialog(rule) {
  dialogMode.value = 'edit'
  editingId.value = rule.id
  Object.assign(form, {
    name: rule.name,
    description: rule.description || '',
    metric_category: rule.metric_category,
    metric_name: rule.metric_name,
    operator: rule.operator,
    threshold: rule.threshold,
    severity: rule.severity,
    cooldown_minutes: rule.cooldown_minutes || 0,
    notification_method: rule.notification_method || [],
    silent_start: rule.silent_start || '',
    silent_end: rule.silent_end || ''
  })
  dialogError.value = ''
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

async function onSubmit() {
  dialogError.value = ''
  if (!form.name) { dialogError.value = t('alertRules.nameRequired'); return }
  if (!form.metric_category) { dialogError.value = t('alertRules.categoryRequired'); return }
  if (!form.metric_name) { dialogError.value = t('alertRules.metricRequired'); return }
  if (form.threshold === null || form.threshold === '') { dialogError.value = t('alertRules.thresholdRequired'); return }

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createAlertRule({ ...form })
    } else {
      await updateAlertRule(editingId.value, { ...form })
    }
    showDialog.value = false
    await fetchRules()
  } catch (e) {
    dialogError.value = e?.response?.data?.detail || t('common.operationFailed')
  } finally {
    submitting.value = false
  }
}

async function onToggle(rule) {
  try {
    const data = await toggleAlertRule(rule.id)
    rule.is_active = data.is_active !== undefined ? data.is_active : !rule.is_active
  } catch (e) {
    console.error('切换规则状态失败', e)
  }
}

async function onDelete(rule) {
  if (!confirm(t('common.confirmDelete', { name: rule.name }))) return
  try {
    await deleteAlertRule(rule.id)
    await fetchRules()
  } catch (e) {
    alert(e?.response?.data?.detail || t('common.deleteFailed'))
  }
}

onMounted(fetchRules)
</script>

<style scoped>
.alert-rules-page {
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

.col-break {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-cell {
  text-align: center;
  padding: 40px 16px !important;
  color: #999;
}

.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 12px;
  border: 1px solid transparent;
  margin: 1px;
}

.tag-blue {
  background: #e6f4ff;
  color: #1677ff;
  border-color: #91caff;
}

.tag-gray {
  background: #f5f5f5;
  color: #666;
  border-color: #d9d9d9;
}

.severity-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.sev-critical { background: #fff1f0; color: #cf1322; }
.sev-high { background: #fff7e6; color: #d46b08; }
.sev-medium { background: #fffbe6; color: #d4b106; }
.sev-low { background: #e6f7ff; color: #096dd9; }

.condition-text {
  font-family: monospace;
  font-weight: 600;
  color: #333;
}

.notify-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* Switch toggle */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: #ccc;
  border-radius: 11px;
  transition: 0.3s;
}

.switch-slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background: #fff;
  border-radius: 50%;
  transition: 0.3s;
}

.switch input:checked + .switch-slider {
  background: #1890ff;
}

.switch input:checked + .switch-slider::before {
  transform: translateX(18px);
}

/* Buttons */
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

.btn:disabled, .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

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
  width: 460px;
  max-width: 92vw;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.modal-wide {
  width: 580px;
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
.form-row select,
.form-row textarea {
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

.form-row textarea {
  height: auto;
  padding: 8px 10px;
  resize: vertical;
  font-family: inherit;
}

.form-row input:focus,
.form-row select:focus,
.form-row textarea:focus {
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

.checkbox-group {
  display: flex;
  gap: 16px;
  padding: 6px 0;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
}

.checkbox-item input[type="checkbox"] {
  width: auto;
  height: auto;
  cursor: pointer;
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
