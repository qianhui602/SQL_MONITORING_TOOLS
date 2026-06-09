import { reactive, computed } from 'vue'

const state = reactive({
  theme: localStorage.getItem('sql_monitor_theme') || 'light'
})

export function useTheme() {
  const theme = computed(() => state.theme)
  const isDark = computed(() => state.theme === 'dark')

  function applyTheme(val) {
    document.documentElement.setAttribute('data-theme', val)
    localStorage.setItem('sql_monitor_theme', val)
  }

  function toggleTheme() {
    const next = state.theme === 'light' ? 'dark' : 'light'
    state.theme = next
    applyTheme(next)
  }

  // 初始应用已保存的主题
  applyTheme(state.theme)

  return {
    theme,
    toggleTheme,
    isDark
  }
}
