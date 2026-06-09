import { reactive, computed } from 'vue'
import {
  getStoredUser,
  setStoredUser,
  setToken,
  clearAuth,
  login as apiLogin,
  getMe
} from '@/api'

const state = reactive({
  user: getStoredUser()
})

export const authStore = {
  state,

  isAuthenticated: computed(() => !!state.user),

  isAdmin: computed(
    () =>
      state.user &&
      (state.user.role === 'admin' || state.user.role === 'super_admin')
  ),

  isSuperAdmin: computed(
    () => state.user && state.user.role === 'super_admin'
  ),

  isViewer: computed(() => state.user && state.user.role === 'viewer'),

  roleLabel: computed(() => {
    if (!state.user) return ''
    const map = {
      super_admin: '超级管理员',
      admin: '管理员',
      viewer: '只读用户'
    }
    return map[state.user.role] || state.user.role
  }),

  async login(username, password) {
    const data = await apiLogin(username, password)
    setToken(data.access_token)
    setStoredUser(data.user)
    state.user = data.user
    return data.user
  },

  async refreshMe() {
    try {
      const me = await getMe()
      setStoredUser(me)
      state.user = me
      return me
    } catch (e) {
      this.logout()
      return null
    }
  },

  logout() {
    clearAuth()
    state.user = null
  }
}
