import { ArrowRight, Sparkles } from 'lucide-react'

type HeroPanelProps = {
  url: string
  busy: boolean
  error: string
  onUrlChange: (value: string) => void
  onParse: () => void
  onDownload: () => void
}

export function HeroPanel({
  url,
  busy,
  error,
  onUrlChange,
  onParse,
  onDownload,
}: HeroPanelProps) {
  return (
    <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
      <div className="rounded-[32px] border border-[var(--line)] bg-[var(--card)] p-8 shadow-[0_20px_60px_rgba(45,55,72,0.08)]">
        <p className="mb-4 text-xs uppercase tracking-[0.38em] text-[var(--accent)]">
          Unified Capture Desk
        </p>
        <h1 className="max-w-3xl font-serif text-4xl leading-tight text-[var(--ink)] md:text-5xl">
          用一条链接，把多平台视频整理成可下载、可归档、可总结的内容资产。
        </h1>
        <p className="mt-5 max-w-2xl text-sm leading-7 text-[var(--muted)] md:text-base">
          面向 B站、YouTube、TikTok、抖音的本地下载工作台。先解析，再选择视频、音频、字幕与封面，最后把字幕交给模型生成摘要。
        </p>

        <div className="mt-8 rounded-[28px] border border-[var(--line)] bg-white p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
          <label className="sr-only" htmlFor="video-url">
            视频链接
          </label>
          <input
            className="w-full rounded-[22px] border border-transparent bg-[var(--paper)] px-5 py-4 text-sm text-[var(--ink)] outline-none transition focus:border-[var(--accent)]"
            id="video-url"
            placeholder="粘贴视频链接，系统会自动识别平台与字幕能力"
            value={url}
            onChange={(event) => onUrlChange(event.target.value)}
          />
          <div className="mt-3 flex flex-wrap gap-3">
            <button className="button-primary" disabled={busy} onClick={onParse}>
              解析视频
              <ArrowRight size={16} />
            </button>
            <button className="button-secondary" disabled={busy} onClick={onDownload}>
              快速下载默认项
            </button>
          </div>
        </div>

        {error ? (
          <div className="mt-4 rounded-2xl border border-[var(--danger-line)] bg-[var(--danger-bg)] px-4 py-3 text-sm text-[var(--danger-text)]">
            {error}
          </div>
        ) : null}
      </div>

      <aside className="grid gap-4 rounded-[32px] border border-[var(--line)] bg-[var(--card-strong)] p-8">
        <div>
          <p className="mb-2 text-xs uppercase tracking-[0.3em] text-[var(--muted)]">产品重点</p>
          <div className="space-y-3 text-sm leading-7 text-[var(--muted)]">
            <p>解析结果优先展示标题、作者、时长、封面和字幕可用性。</p>
            <p>下载任务按工作流拆分，既能拿到视频，也能拿到音频、字幕与缩略图。</p>
            <p>AI 总结走可插拔接口，不绑死单一模型供应商。</p>
          </div>
        </div>

        <div className="rounded-[28px] border border-[var(--line)] bg-white px-5 py-5">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-[var(--paper)] px-3 py-1 text-xs uppercase tracking-[0.18em] text-[var(--accent)]">
            <Sparkles size={14} />
            AI 摘要入口
          </div>
          <p className="font-serif text-2xl leading-tight">字幕优先、失败可降级、不影响下载主流程。</p>
        </div>
      </aside>
    </section>
  )
}
