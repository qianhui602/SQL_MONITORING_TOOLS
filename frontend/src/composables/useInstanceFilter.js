import { ref, onMounted } from 'vue'
import { getInstances } from '@/api'

/**
 * 实例筛选 composable
 * 提供实例列表获取和选择逻辑，供各监控页面复用
 */
export function useInstanceFilter() {
  const instances = ref([])
  const selectedInstance = ref('')
  const loadingInstances = ref(false)

  async function fetchInstances() {
    try {
      loadingInstances.value = true
      const data = await getInstances()
      instances.value = Array.isArray(data) ? data : (data.items || [])
    } catch (e) {
      console.error('获取实例列表失败', e)
    } finally {
      loadingInstances.value = false
    }
  }

  /**
   * 获取当前选中的实例标识
   * 格式: "实例名(host:port)"
   */
  function getServerAddress() {
    return selectedInstance.value || undefined
  }

  onMounted(() => {
    fetchInstances()
  })

  return {
    instances,
    selectedInstance,
    loadingInstances,
    fetchInstances,
    getServerAddress,
  }
}
