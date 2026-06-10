/**
 * 时间格式化工具 - 支持可配置时区
 * 后端存储 UTC 时间，前端根据系统设置的时区转换后显示
 */

// 时区名称到 UTC 偏移量（分钟）的映射
const TIMEZONE_OFFSETS = {
  'UTC': 0,
  'Asia/Shanghai': 8 * 60,
  'Asia/Tokyo': 9 * 60,
  'Asia/Kolkata': 5.5 * 60,
  'Asia/Dubai': 4 * 60,
  'Europe/Moscow': 3 * 60,
  'Europe/Berlin': 1 * 60,
  'Europe/London': 0,
  'America/New_York': -5 * 60,
  'America/Chicago': -6 * 60,
  'America/Denver': -7 * 60,
  'America/Los_Angeles': -8 * 60,
  'Pacific/Auckland': 12 * 60,
  'Australia/Sydney': 10 * 60,
}

// 当前使用的时区偏移量（分钟），默认 UTC+8
let _offsetMinutes = 8 * 60

/**
 * 设置时区偏移量
 * @param {string} timezone - IANA 时区名称，如 'Asia/Shanghai'
 */
export function setTimezone(timezone) {
  if (TIMEZONE_OFFSETS[timezone] !== undefined) {
    _offsetMinutes = TIMEZONE_OFFSETS[timezone]
  }
}

/**
 * 获取当前时区偏移量（毫秒）
 */
function getOffsetMs() {
  return _offsetMinutes * 60 * 1000
}

function parseAsUTC(d) {
  if (!d) return null
  if (typeof d === 'number') return new Date(d)
  const str = String(d).trim()
  if (str.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(str)) {
    return new Date(str)
  }
  return new Date(str + 'Z')
}

function toLocalDate(d) {
  const utc = parseAsUTC(d)
  if (!utc || isNaN(utc.getTime())) return null
  return new Date(utc.getTime() + getOffsetMs())
}

export function formatDateTime(d, options = {}) {
  if (!d && d !== 0) return '-'
  const local = toLocalDate(d)
  if (!local) return '-'

  const {
    year = true,
    month = true,
    day = true,
    hour = true,
    minute = true,
    second = false,
  } = options

  const yyyy = local.getUTCFullYear()
  const MM = String(local.getUTCMonth() + 1).padStart(2, '0')
  const dd = String(local.getUTCDate()).padStart(2, '0')
  const hh = String(local.getUTCHours()).padStart(2, '0')
  const mm = String(local.getUTCMinutes()).padStart(2, '0')
  const ss = String(local.getUTCSeconds()).padStart(2, '0')

  const dateParts = []
  if (year) dateParts.push(yyyy)
  if (month) dateParts.push(MM)
  if (day) dateParts.push(dd)
  const dateStr = dateParts.join('-')

  const timeParts = []
  if (hour) timeParts.push(hh)
  if (minute) timeParts.push(mm)
  if (second) timeParts.push(ss)

  if (timeParts.length === 0) return dateStr
  return `${dateStr} ${timeParts.join(':')}`
}

export function formatTime(d) {
  if (!d && d !== 0) return '-'
  const local = toLocalDate(d)
  if (!local) return '-'
  const hh = String(local.getUTCHours()).padStart(2, '0')
  const mm = String(local.getUTCMinutes()).padStart(2, '0')
  const ss = String(local.getUTCSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

export function toLocalISOString(d) {
  if (!d && d !== 0) return ''
  const local = toLocalDate(d)
  if (!local) return ''
  const yyyy = local.getUTCFullYear()
  const MM = String(local.getUTCMonth() + 1).padStart(2, '0')
  const dd = String(local.getUTCDate()).padStart(2, '0')
  const hh = String(local.getUTCHours()).padStart(2, '0')
  const mm = String(local.getUTCMinutes()).padStart(2, '0')
  const ss = String(local.getUTCSeconds()).padStart(2, '0')
  return `${yyyy}-${MM}-${dd}T${hh}:${mm}:${ss}`
}

// 向后兼容
export const toBeijingISOString = toLocalISOString
