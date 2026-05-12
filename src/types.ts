export type DownloadItems = {
  video: boolean
  audio: boolean
  subtitles: boolean
  thumbnail: boolean
}

export type AISettings = {
  base_url: string
  api_key: string
  model: string
}

export type AppSettings = {
  download_dir: string
  default_items: DownloadItems
  ai: AISettings
  browser_cookies: string
  cookies_file: string
}

export type ParseResponse = {
  platform: string
  title: string
  uploader?: string
  duration?: number
  thumbnail?: string
  webpage_url: string
  has_subtitles: boolean
  formats: string[]
}

export type TaskSummary = {
  id: string
  title: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
}

export type TaskDetail = TaskSummary & {
  url: string
  logs: string[]
  output_files: string[]
  error?: string
  subtitle_path?: string
}

export type SummaryResponse = {
  summary: string
  bullets: string[]
  tags: string[]
}
