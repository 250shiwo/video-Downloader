import { Sparkles } from 'lucide-react'

import type { SummaryResponse, TaskDetail } from '@/types'

type SummaryCardProps = {
  taskDetail: TaskDetail | null
  summary: SummaryResponse | null
  busy: boolean
  onSummarize: (taskId: string) => void
}

export function SummaryCard({ taskDetail, summary, busy, onSummarize }: SummaryCardProps) {
  const canSummarize = Boolean(taskDetail?.subtitle_path)

  return (
    <section className="rounded-[30px] border border-[var(--line)] bg-white p-6">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted)]">AI 总结</p>
          <h2 className="mt-2 font-serif text-3xl">用字幕生成内容摘要</h2>
        </div>
        <button
          className="button-secondary"
          disabled={!canSummarize || busy || !taskDetail}
          onClick={() => taskDetail && onSummarize(taskDetail.id)}
        >
          <Sparkles size={16} />
          生成摘要
        </button>
      </div>

      {summary ? (
        <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_0.8fr]">
          <article className="rounded-[24px] bg-[var(--paper)] px-5 py-5">
            <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">摘要</p>
            <p className="mt-3 text-sm leading-7 text-[var(--ink)]">{summary.summary}</p>
          </article>
          <article className="grid gap-4">
            <div className="rounded-[24px] bg-[var(--paper)] px-5 py-5">
              <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">核心要点</p>
              <ul className="mt-3 space-y-2 text-sm leading-7 text-[var(--ink)]">
                {summary.bullets.map((bullet) => (
                  <li key={bullet}>- {bullet}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-[24px] bg-[var(--paper)] px-5 py-5">
              <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">标签</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {summary.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-white px-3 py-1 text-xs text-[var(--accent)]">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </article>
        </div>
      ) : (
        <div className="mt-6 rounded-[24px] border border-dashed border-[var(--line)] px-5 py-8 text-sm leading-7 text-[var(--muted)]">
          {canSummarize
            ? '当前任务已具备字幕文件。点击上方按钮即可调用已配置的大模型生成摘要、要点和标签。'
            : 'AI 总结依赖字幕文件。请先下载包含字幕的任务，并在设置页中填写兼容 OpenAI 的模型配置。'}
        </div>
      )}
    </section>
  )
}
