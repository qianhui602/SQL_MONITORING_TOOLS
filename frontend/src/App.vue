<template>
  <div id="app-root">
    <Layout v-if="showLayout">
      <router-view />
    </Layout>
    <router-view v-else />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useTheme } from '@/stores/theme'
import { setTimezone } from '@/utils/datetime'
import { getConfig } from '@/api'

// 在组件挂载时应用已保存的主题
useTheme()

// 初始化时区设置
onMounted(async () => {
  try {
    const cfg = await getConfig('timezone')
    if (cfg && cfg.config_value) {
      setTimezone(cfg.config_value)
    }
  } catch (e) {
    // 使用默认时区 UTC+8
  }
})

const route = useRoute()

const showLayout = computed(() => {
  return route.meta?.layout !== false
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
}

#app, #app-root {
  height: 100%;
}

/* ===== 主题 CSS 变量 ===== */

/* 浅色主题（默认） */
:root {
  --bg-primary: #f0f2f5;
  --bg-secondary: #fff;
  --bg-card: #fff;
  --text-primary: #333;
  --text-secondary: #666;
  --text-muted: #999;
  --border-color: #e8e8e8;
  --sidebar-bg: #2b2b2b;
  --sidebar-text: rgba(255,255,255,0.75);
  --topbar-bg: #fff;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.1);
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --input-bg: #fff;
  --input-border: #d9d9d9;
  --hover-bg: rgba(0,0,0,0.04);
  --table-stripe: #fafafa;
  --table-hover: #f5f5f5;
}

/* 暗色主题 */
[data-theme="dark"] {
  --bg-primary: #0f0f1a;
  --bg-secondary: #1a1a2e;
  --bg-card: #1e2a45;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --text-muted: #7a7a7a;
  --border-color: #2a3a5e;
  --sidebar-bg: #0d0d17;
  --sidebar-text: rgba(255,255,255,0.7);
  --topbar-bg: #1a1a2e;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.4);
  --shadow: 0 2px 8px rgba(0,0,0,0.35);
  --input-bg: #16213e;
  --input-border: #2a3a5e;
  --hover-bg: rgba(255,255,255,0.05);
  --table-stripe: #1a1a2e;
  --table-hover: #243352;
}

:root,
[data-theme="dark"] {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}
</style>
