import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import enUS from './en-US'

const savedLang = localStorage.getItem('app_language') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: savedLang,
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

export function setLocale(lang) {
  i18n.global.locale.value = lang
  localStorage.setItem('app_language', lang)
}

export function getLocale() {
  return i18n.global.locale.value
}

export default i18n
