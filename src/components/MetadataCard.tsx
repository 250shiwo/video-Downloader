import type { ReactNode } from 'react'
import { Clock3, Languages, Link2, UserRound } from 'lucide-react'

import type { ParseResponse } from '@/types'

type MetadataCardProps = {
  metadata: ParseResponse | null
}

function formatDuration(duration?: number) {
  if (!duration) return '未知'
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes} 分 ${seconds} 秒`
}

export function MetadataCard({ metadata }: MetadataCardProps) {
  return (
    <section className="rounded-[30px] border border-[var(--line)] bg-white p-6 shadow-[0_18px_40px_rgba(15,23,42,0.05)]">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted)]">解析结果</p>
          <h2 className="mt-2 font-serif text-3xl">视频信息预览</h2>
        </div>
        <span className="rounded-full border border-[var(--line)] px-3 py-1 text-xs uppercase tracking-[0.16em] text-[var(--accent)]">
          {metadata?.platform ?? '等待解析'}
        </span>
      </div>

      {metadata ? (
        <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
          <div className="overflow-hidden rounded-[24px] bg-[var(--paper)]">
            {metadata.thumbnail ? (
              <img
                alt={metadata.title}
                className="h-full min-h-[240px] w-full object-cover"
                src={metadata.thumbnail}
              />
            ) : (
              <div className="flex min-h-[240px] items-center justify-center text-sm text-[var(--muted)]">
                暂无封面
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="font-serif text-3xl leading-tight">{metadata.title}</h3>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <InfoItem icon={<UserRound size={16} />} label="作者" value={metadata.uploader ?? '未知'} />
              <InfoItem icon={<Clock3 size={16} />} label="时长" value={formatDuration(metadata.duration)} />
              <InfoItem
                icon={<Languages size={16} />}
                label="字幕能力"
                value={metadata.has_subtitles ? '可用' : '当前未检测到'}
              />
              <InfoItem icon={<Link2 size={16} />} label="原始链接" value={metadata.webpage_url} />
            </div>

            <div>
              <p className="mb-2 text-xs uppercase tracking-[0.2em] text-[var(--muted)]">可用格式摘要</p>
              <div className="flex flex-wrap gap-2">
                {metadata.formats.length ? (
                  metadata.formats.map((format) => (
                    <span
                      key={format}
                      className="rounded-full bg-[var(--paper)] px-3 py-1 text-xs text-[var(--muted)]"
                    >
                      {format}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-[var(--muted)]">解析成功后会显示格式摘要。</span>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-[24px] border border-dashed border-[var(--line)] px-6 py-10 text-sm leading-7 text-[var(--muted)]">
          暂无解析结果。输入视频链接后，这里会展示封面、标题、作者、时长和字幕可用性，帮助用户先看内容，再决定如何下载。
        </div>
      )}
    </section>
  )
}

type InfoItemProps = {
  icon: ReactNode
  label: string
  value: string
}

function InfoItem({ icon, label, value }: InfoItemProps) {
  return (
    <div className="rounded-[20px] bg-[var(--paper)] px-4 py-4">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
        {icon}
        {label}
      </div>
      <p className="mt-3 line-clamp-2 text-sm leading-6 text-[var(--ink)]">{value}</p>
    </div>
  )
}
