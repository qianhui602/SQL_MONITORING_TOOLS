/**
 * 时间格式化工具 - 统一使用北京时间 (UTC+8)
 * 后端存储 UTC 时间，前端统一转换为北京时间显示
 */

const BEIJING_OFFSET = 8 * 60 * 60 * 1000

function parseAsUTC(d) {
  if (!d) return null
  if (typeof d === 'number') return new Date(d)
  const str = String(d).trim()
  if (str.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(str)) {
    return new Date(str)
  }
  return new Date(str + 'Z')
}

function beijingDate(d) {
  const utc = parseAsUTC(d)
  if (!utc || isNaN(utc.getTime())) return null
  return new Date(utc.getTime() + BEIJING_OFFSET)
}

export function formatDateTime(d, options = {}) {
  if (!d && d !== 0) return '-'
  const bj = beijingDate(d)
  if (!bj) return '-'

  const {
    year = true,
    month = true,
    day = true,
    hour = true,
    minute = true,
    second = false,
  } = options

  const yyyy = bj.getUTCFullYear()
  const MM = String(bj.getUTCMonth() + 1).padStart(2, '0')
  const dd = String(bj.getUTCDate()).padStart(2, '0')
  const hh = String(bj.getUTCHours()).padStart(2, '0')
  const mm = String(bj.getUTCMinutes()).padStart(2, '0')
  const ss = String(bj.getUTCSeconds()).padStart(2, '0')

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
  const bj = beijingDate(d)
  if (!bj) return '-'
  const hh = String(bj.getUTCHours()).padStart(2, '0')
  const mm = String(bj.getUTCMinutes()).padStart(2, '0')
  const ss = String(bj.getUTCSeconds()).padStart(2, '0')
  return `${hh}:${mm}:${ss}`
}

export function toBeijingISOString(d) {
  if (!d && d !== 0) return ''
  const bj = beijingDate(d)
  if (!bj) return ''
  const yyyy = bj.getUTCFullYear()
  const MM = String(bj.getUTCMonth() + 1).padStart(2, '0')
  const dd = String(bj.getUTCDate()).padStart(2, '0')
  const hh = String(bj.getUTCHours()).padStart(2, '0')
  const mm = String(bj.getUTCMinutes()).padStart(2, '0')
  const ss = String(bj.getUTCSeconds()).padStart(2, '0')
  return `${yyyy}-${MM}-${dd}T${hh}:${mm}:${ss}`
}
