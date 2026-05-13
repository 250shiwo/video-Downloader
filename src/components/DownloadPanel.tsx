import type { ReactNode } from 'react'
import { Download, FileAudio, FileImage, FileText, Film } from 'lucide-react'

import type { DownloadItems } from '@/types'

type DownloadPanelProps = {
  items: DownloadItems
  busy: boolean
  onToggle: (key: keyof DownloadItems, value: boolean) => void
  onStart: () => void
}

const choices: Array<{
  key: keyof DownloadItems
  title: string
  detail: string
  icon: ReactNode
}> = [
  {
    key: 'video',
    title: '视频文件',
    detail: '保留原始观看体验',
    icon: <Film size={18} />,
  },
  {
    key: 'audio',
    title: '音频文件',
    detail: '适合播客式收听',
    icon: <FileAudio size={18} />,
  },
  {
    key: 'subtitles',
    title: '字幕文件',
    detail: '为 AI 总结提供基础材料',
    icon: <FileText size={18} />,
  },
  {
    key: 'thumbnail',
    title: '封面缩略图',
    detail: '用于整理与归档封面资产',
    icon: <FileImage size={18} />,
  },
]

export function DownloadPanel({ items, busy, onToggle, onStart }: DownloadPanelProps) {
  return (
    <section className="rounded-[30px] border border-[var(--line)] bg-[var(--card)] p-6">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted)]">下载组合</p>
          <h2 className="mt-2 font-serif text-3xl">按资产类型自由组合</h2>
        </div>
        <button className="button-primary" disabled={busy} onClick={onStart}>
          <Download size={16} />
          创建下载任务
        </button>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {choices.map((choice) => (
          <label
            key={choice.key}
            className={`cursor-pointer rounded-[24px] border px-5 py-5 transition ${
              items[choice.key]
                ? 'border-[var(--accent)] bg-white shadow-[0_10px_30px_rgba(22,36,60,0.08)]'
                : 'border-[var(--line)] bg-[var(--paper)]'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-sm font-medium text-[var(--ink)]">
                  {choice.icon}
                  {choice.title}
                </div>
                <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{choice.detail}</p>
              </div>
              <input
                checked={items[choice.key]}
                className="mt-1 h-4 w-4 accent-[var(--accent)]"
                type="checkbox"
                onChange={(event) => onToggle(choice.key, event.target.checked)}
              />
            </div>
          </label>
        ))}
      </div>
    </section>
  )
}
