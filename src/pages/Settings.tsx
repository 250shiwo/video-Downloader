import type { ReactNode } from 'react'
import { useEffect, useMemo, useState } from 'react'

import { Save } from 'lucide-react'

import { AppShell } from '@/components/AppShell'
import { useAppStore } from '@/store/useAppStore'
import type { AppSettings } from '@/types'

export default function Settings() {
  const { loadSettings, saveSettings, settings } = useAppStore()
  const [draft, setDraft] = useState<AppSettings | null>(null)

  useEffect(() => {
    loadSettings().catch(() => undefined)
  }, [loadSettings])

  useEffect(() => {
    if (settings) {
      setDraft(settings)
    }
  }, [settings])

  const ready = useMemo(() => Boolean(draft), [draft])

  const update = (path: string, value: string | boolean) => {
    setDraft((current) => {
      if (!current) return current

      if (path === 'download_dir') {
        return { ...current, download_dir: value as string }
      }
      if (path === 'browser_cookies') {
        return { ...current, browser_cookies: value as string }
      }
      if (path === 'cookies_file') {
        return { ...current, cookies_file: value as string }
      }
      if (path.startsWith('ai.')) {
        const key = path.replace('ai.', '') as keyof AppSettings['ai']
        return {
          ...current,
          ai: { ...current.ai, [key]: value },
        }
      }

      const key = path.replace('default_items.', '') as keyof AppSettings['default_items']
      return {
        ...current,
        default_items: { ...current.default_items, [key]: value as boolean },
      }
    })
  }

  return (
    <AppShell>
      <section className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-[30px] border border-[var(--line)] bg-[var(--card)] p-8">
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--muted)]">Settings</p>
          <h1 className="mt-3 font-serif text-5xl leading-tight">把下载目录和模型配置收进同一套工作参数。</h1>
          <p className="mt-5 text-sm leading-7 text-[var(--muted)]">
            首版不做数据库，设置会直接保存到本地文件。你可以在这里指定下载目录、默认下载项，以及兼容 OpenAI 风格的 AI 服务配置。
          </p>
        </div>

        <div className="rounded-[30px] border border-[var(--line)] bg-white p-8 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
          {ready && draft ? (
            <div className="space-y-8">
              <FormGroup title="下载设置">
                <Field label="下载目录">
                  <input
                    className="field-input"
                    value={draft.download_dir}
                    onChange={(event) => update('download_dir', event.target.value)}
                  />
                </Field>

                <div className="grid gap-3 md:grid-cols-2">
                  {(
                    Object.entries(draft.default_items) as Array<
                      [keyof AppSettings['default_items'], boolean]
                    >
                  ).map(([key, checked]) => (
                    <label
                      key={key}
                      className="flex items-center justify-between rounded-[20px] bg-[var(--paper)] px-4 py-4 text-sm"
                    >
                      <span>{labelMap[key]}</span>
                      <input
                        checked={checked}
                        type="checkbox"
                        onChange={(event) => update(`default_items.${key}`, event.target.checked)}
                      />
                    </label>
                  ))}
                </div>
              </FormGroup>

              <FormGroup title="AI 服务配置">
                <Field label="Base URL">
                  <input
                    className="field-input"
                    placeholder="https://api.openai.com/v1"
                    value={draft.ai.base_url}
                    onChange={(event) => update('ai.base_url', event.target.value)}
                  />
                </Field>
                <Field label="API Key">
                  <input
                    className="field-input"
                    placeholder="sk-..."
                    type="password"
                    value={draft.ai.api_key}
                    onChange={(event) => update('ai.api_key', event.target.value)}
                  />
                </Field>
                <Field label="Model">
                  <input
                    className="field-input"
                    placeholder="gpt-4o-mini / deepseek-chat"
                    value={draft.ai.model}
                    onChange={(event) => update('ai.model', event.target.value)}
                  />
                </Field>
              </FormGroup>

              <FormGroup title="站点访问辅助">
                <Field label="浏览器 Cookie 来源">
                  <input
                    className="field-input"
                    placeholder="例如 chrome、edge、firefox 或 chrome:Default"
                    value={draft.browser_cookies}
                    onChange={(event) => update('browser_cookies', event.target.value)}
                  />
                </Field>
                <Field label="Cookie 文件路径">
                  <input
                    className="field-input"
                    placeholder="可选，填写 Netscape 格式 cookies.txt 的绝对路径"
                    value={draft.cookies_file}
                    onChange={(event) => update('cookies_file', event.target.value)}
                  />
                </Field>
                <p className="rounded-[20px] bg-[var(--paper)] px-4 py-4 text-sm leading-7 text-[var(--muted)]">
                  如果 B站 出现 `HTTP Error 412`，通常是风控导致。推荐优先填写“浏览器 Cookie
                  来源”，例如 `chrome` 或 `edge`，并确保对应浏览器里已经登录 B站。若两项都填写，系统会优先使用浏览器
                  Cookie。
                </p>
              </FormGroup>

              <button
                className="button-primary"
                onClick={() => draft && saveSettings(draft).catch(() => undefined)}
              >
                <Save size={16} />
                保存设置
              </button>
            </div>
          ) : (
            <div className="rounded-[24px] border border-dashed border-[var(--line)] px-5 py-8 text-sm text-[var(--muted)]">
              正在加载设置...
            </div>
          )}
        </div>
      </section>
    </AppShell>
  )
}

function FormGroup({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <section>
      <p className="mb-4 text-xs uppercase tracking-[0.2em] text-[var(--muted)]">{title}</p>
      <div className="space-y-4">{children}</div>
    </section>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm text-[var(--muted)]">{label}</span>
      {children}
    </label>
  )
}

const labelMap = {
  video: '默认下载视频',
  audio: '默认下载音频',
  subtitles: '默认下载字幕',
  thumbnail: '默认下载封面',
}
