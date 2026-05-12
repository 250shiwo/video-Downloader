import { create } from 'zustand'

import { api } from '@/utils/api'
import type {
  AppSettings,
  DownloadItems,
  DownloadTaskResponse,
  ParseResponse,
  SummaryResponse,
  TaskDetail,
  TaskSummary,
} from '@/types'

type StoreState = {
  url: string
  metadata: ParseResponse | null
  tasks: TaskSummary[]
  taskDetail: TaskDetail | null
  summary: SummaryResponse | null
  settings: AppSettings | null
  downloadItems: DownloadItems
  error: string
  busy: boolean
  setUrl: (url: string) => void
  setDownloadItem: (key: keyof DownloadItems, value: boolean) => void
  loadSettings: () => Promise<void>
  saveSettings: (settings: AppSettings) => Promise<void>
  parseUrl: () => Promise<void>
  startDownload: () => Promise<void>
  loadTasks: () => Promise<void>
  inspectTask: (taskId: string) => Promise<void>
  summarizeTask: (taskId: string) => Promise<void>
  clearMessage: () => void
}

const defaultItems: DownloadItems = {
  video: true,
  audio: true,
  subtitles: true,
  thumbnail: true,
}

export const useAppStore = create<StoreState>((set, get) => ({
  url: '',
  metadata: null,
  tasks: [],
  taskDetail: null,
  summary: null,
  settings: null,
  downloadItems: defaultItems,
  error: '',
  busy: false,
  setUrl: (url) => set({ url }),
  setDownloadItem: (key, value) =>
    set((state) => ({
      downloadItems: {
        ...state.downloadItems,
        [key]: value,
      },
    })),
  clearMessage: () => set({ error: '' }),
  loadSettings: async () => {
    const settings = await api.get<AppSettings>('/api/settings')
    set({
      settings,
      downloadItems: settings.default_items,
    })
  },
  saveSettings: async (settings) => {
    const saved = await api.put<AppSettings>('/api/settings', settings)
    set({
      settings: saved,
      downloadItems: saved.default_items,
      error: '',
    })
  },
  parseUrl: async () => {
    const { url } = get()
    if (!url.trim()) {
      set({ error: '请先输入视频链接。' })
      return
    }

    set({ busy: true, error: '', summary: null })
    try {
      const metadata = await api.post<ParseResponse>('/api/parse', { url })
      set({ metadata })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '解析失败', metadata: null })
    } finally {
      set({ busy: false })
    }
  },
  startDownload: async () => {
    const { url, downloadItems, loadTasks, inspectTask } = get()
    set({ busy: true, error: '' })
    try {
      const result = await api.post<DownloadTaskResponse>('/api/tasks/download', {
        url,
        items: downloadItems,
      })
      await loadTasks()
      await inspectTask(result.task_id)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '创建任务失败' })
    } finally {
      set({ busy: false })
    }
  },
  loadTasks: async () => {
    const tasks = await api.get<TaskSummary[]>('/api/tasks')
    set((state) => ({
      tasks,
      taskDetail:
        state.taskDetail && tasks.every((task) => task.id !== state.taskDetail?.id)
          ? null
          : state.taskDetail,
    }))
  },
  inspectTask: async (taskId) => {
    try {
      const detail = await api.get<TaskDetail>(`/api/tasks/${taskId}`)
      set({ taskDetail: detail })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '获取任务详情失败' })
    }
  },
  summarizeTask: async (taskId) => {
    set({ busy: true, error: '' })
    try {
      const summary = await api.post<SummaryResponse>('/api/summary', { taskId })
      set({ summary })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '总结失败' })
    } finally {
      set({ busy: false })
    }
  },
}))
