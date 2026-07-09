<template>
  <div class="help-page">
    <div class="help-search">
      <div class="search-box">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchText" type="text" placeholder="搜索帮助内容..." class="search-input" />
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
          <p>没有找到匹配的内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const searchText = ref('')
const activeSection = ref('overview')
const contentRef = ref(null)

const sections = [
  { id: 'overview', title: '系统概述', content: '<p>SQL Server 监控系统是一套企业级数据库监控平台，用于实时监控 SQL Server 实例的性能指标、健康状态和安全事件。</p>' },
  { id: 'dashboard', title: '总览仪表盘', content: '<p>总览页面提供系统运行状态的全局视图，包含统计卡片、性能趋势图、数据库连接状态和最近告警等区域。</p>' },
  { id: 'performance', title: '性能趋势', content: '<p>性能趋势页面以折线图形式展示 CPU、内存、磁盘 I/O、连接数等指标的历史变化趋势。</p>' },
  { id: 'deadlocks', title: '死锁监控', content: '<p>实时检测 SQL Server 中的死锁事件，展示受害者会话 ID、涉及对象和死锁图。</p>' },
  { id: 'alerts', title: '告警管理', content: '<p>展示系统触发的所有告警记录，支持按严重级别和时间范围筛选。</p>' },
  { id: 'slow-queries', title: '慢查询分析', content: '<p>自动捕获执行时间超过阈值的慢查询，提供 SQL 文本、执行计划和优化建议。</p>' },
  { id: 'blocking', title: '阻塞进程', content: '<p>实时监控 SQL Server 中的进程阻塞链，展示阻塞者和被阻塞者的关系。</p>' },
  { id: 'disk', title: '磁盘空间', content: '<p>监控数据库文件和日志文件的磁盘使用情况，空间不足时自动触发告警。</p>' },
  { id: 'indexes', title: '索引分析', content: '<p>分析数据库索引使用情况，推荐缺失索引、识别冗余索引。</p>' },
  { id: 'alert-rules', title: '告警规则', content: '<p>自定义告警规则，配置指标分类、条件、阈值、严重级别和通知方式。</p>' },
  { id: 'instances', title: '实例管理', content: '<p>管理 SQL Server 实例，支持添加、连接测试、状态监控和启用/禁用。</p>' },
  { id: 'report', title: '系统报告', content: '<p>生成日报、周报、月报等系统运行报告，包含性能趋势和告警统计。</p>' },
  { id: 'settings', title: '系统设置', content: '<p>管理员可配置品牌设置、告警配置、通知渠道和数据采集参数。</p>' },
  { id: 'users', title: '用户管理', content: '<p>管理系统用户账号和权限，支持创建用户、分配角色和启用/禁用账号。</p>' },
  { id: 'faq', title: '常见问题', content: '<p>包含连接问题、告警通知、数据更新、密码修改和深色模式等常见问题解答。</p>' },
  { id: 'contact', title: '联系我们', content: '<p>遇到问题请联系太阳谷信息技术部。</p>' }
]

const filteredSections = computed(() => {
  if (!searchText.value.trim()) return sections
  const kw = searchText.value.trim().toLowerCase()
  return sections.filter(s => s.title.toLowerCase().includes(kw) || s.content.toLowerCase().includes(kw))
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