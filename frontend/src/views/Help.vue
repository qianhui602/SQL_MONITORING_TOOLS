<template>
  <div class="help-page">
    <div class="help-search">
      <div class="search-box">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchText" type="text" :placeholder="t('help.searchPlaceholder')" class="search-input" />
      </div>
    </div>
    <div class="help-layout">
      <nav class="help-nav">
        <div v-for="section in filteredSections" :key="section.id" class="nav-item" :class="{ active: activeSection === section.id }" @click="scrollTo(section.id)">{{ section.title }}</div>
      </nav>
      <div class="help-content" ref="contentRef">
        <div v-for="section in filteredSections" :key="section.id" :id="section.id" class="help-section">
          <h2 class="section-title">{{ section.title }}</h2>
          <div v-html="section.content" class="section-body"></div>
        </div>
        <div v-if="filteredSections.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <p>{{ t('help.noMatch') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const searchText = ref('')
const activeSection = ref('overview')
const contentRef = ref(null)

const sections = computed(() => [
  { id: 'overview', title: t('layout.menu.dashboard'), content: t('help.sections.overview') },
  { id: 'dashboard', title: t('layout.menu.dashboard'), content: t('help.sections.dashboard') },
  { id: 'performance', title: t('layout.menu.trends'), content: t('help.sections.performance') },
  { id: 'deadlocks', title: t('layout.menu.deadlocks'), content: t('help.sections.deadlocks') },
  { id: 'alerts', title: t('layout.menu.alerts'), content: t('help.sections.alerts') },
  { id: 'slow-queries', title: t('layout.menu.slowQueries'), content: t('help.sections["slow-queries"]') },
  { id: 'blocking', title: t('layout.menu.blocking'), content: t('help.sections.blocking') },
  { id: 'disk', title: t('layout.menu.disk'), content: t('help.sections.disk') },
  { id: 'indexes', title: t('layout.menu.indexes'), content: t('help.sections.indexes') },
  { id: 'alert-rules', title: t('layout.menu.alertRules'), content: t('help.sections["alert-rules"]') },
  { id: 'instances', title: t('layout.menu.instances'), content: t('help.sections.instances') },
  { id: 'report', title: t('layout.menu.report'), content: t('help.sections.report') },
  { id: 'settings', title: t('layout.menu.settings'), content: t('help.sections.settings') },
  { id: 'users', title: t('layout.menu.users'), content: t('help.sections.users') },
  { id: 'faq', title: t('help.faq'), content: t('help.sections.faq') },
  { id: 'contact', title: t('help.contact'), content: t('help.sections.contact') },
])

const filteredSections = computed(() => {
  if (!searchText.value.trim()) return sections.value
  const kw = searchText.value.trim().toLowerCase()
  return sections.value.filter(s => s.title.toLowerCase().includes(kw) || s.content.toLowerCase().includes(kw))
})

function scrollTo(id) {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

let observer = null

onMounted(() => {
  nextTick(() => {
    observer = new IntersectionObserver((entries) => {
      for (const entry of entries) { if (entry.isIntersecting) activeSection.value = entry.target.id }
    }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 })
    const container = contentRef.value
    if (container) container.querySelectorAll('.help-section').forEach(el => observer.observe(el))
  })
})

onBeforeUnmount(() => { if (observer) observer.disconnect() })
</script>

<style scoped>
.help-page { display: flex; flex-direction: column; gap: 16px; height: calc(100vh - 140px); }
.help-search { flex-shrink: 0; }
.search-box { display: flex; align-items: center; gap: 8px; background: var(--bg-card); border-radius: 8px; padding: 10px 16px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); }
.search-icon { color: #999; flex-shrink: 0; }
.search-input { flex: 1; border: none; outline: none; font-size: 14px; background: transparent; color: var(--text-primary); }
.search-input::placeholder { color: #bbb; }
.help-layout { display: flex; gap: 16px; flex: 1; min-height: 0; }
.help-nav { width: 180px; flex-shrink: 0; background: var(--bg-card); border-radius: 8px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); padding: 8px; overflow-y: auto; align-self: flex-start; position: sticky; top: 0; }
.nav-item { padding: 8px 12px; border-radius: 6px; font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.active { background: #1890ff; color: #fff; }
.help-content { flex: 1; overflow-y: auto; padding-right: 8px; }
.help-section { background: var(--bg-card); border-radius: 8px; box-shadow: var(--shadow-card); border: 1px solid var(--border-color); padding: 24px 28px; margin-bottom: 12px; scroll-margin-top: 8px; }
.section-title { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px 0; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.section-body { font-size: 14px; line-height: 1.8; color: var(--text-secondary); }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; color: #bbb; gap: 12px; }
.empty-state p { font-size: 14px; }
@media (max-width: 768px) {
  .help-layout { flex-direction: column; }
  .help-nav { width: 100%; position: static; display: flex; flex-wrap: wrap; gap: 4px; padding: 8px; }
  .nav-item { padding: 6px 10px; font-size: 12px; }
}
</style>