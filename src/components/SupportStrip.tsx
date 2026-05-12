const platforms = [
  { name: 'B站', detail: '长视频 / 收藏归档' },
  { name: 'YouTube', detail: '全球内容 / 字幕丰富' },
  { name: 'TikTok', detail: '短视频 / 国际平台' },
  { name: '抖音', detail: '短视频 / 中文内容' },
]

export function SupportStrip() {
  return (
    <section className="mt-8 grid gap-4 md:grid-cols-4">
      {platforms.map((platform) => (
        <article
          key={platform.name}
          className="rounded-[24px] border border-[var(--line)] bg-white/70 px-5 py-5 shadow-[0_10px_30px_rgba(15,23,42,0.04)]"
        >
          <p className="font-serif text-2xl text-[var(--ink)]">{platform.name}</p>
          <p className="mt-1 text-sm text-[var(--muted)]">{platform.detail}</p>
        </article>
      ))}
    </section>
  )
}
