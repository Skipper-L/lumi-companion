const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const STORAGE_PUBLIC_URL = (import.meta.env.VITE_STORAGE_PUBLIC_URL || '').replace(/\/$/, '')

export function resolveImageUrl(imageUrl) {
  if (!imageUrl) return ''
  if (/^https?:\/\//i.test(imageUrl)) return imageUrl

  // 旧数据保存的是本机 /uploads/... 路径；现有文件已放在 Storage 桶根目录。
  if (STORAGE_PUBLIC_URL && imageUrl.startsWith('/uploads/')) {
    const fileName = imageUrl.split('/').pop()
    return `${STORAGE_PUBLIC_URL}/${encodeURIComponent(fileName)}`
  }

  return `${API_BASE_URL}${imageUrl}`
}
