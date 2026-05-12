import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'

import { Film, Settings2 } from 'lucide-react'

type AppShellProps = {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-6 lg:px-10">
        <header className="mb-10 flex items-center justify-between rounded-full border border-[var(--line)] bg-white/75 px-6 py-4 shadow-[0_8px_30px_rgba(30,41,59,0.06)] backdrop-blur">
          <Link className="flex items-center gap-3" to="/">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--ink)] text-[var(--paper)]">
              <Film size={18} />
            </div>
            <div>
              <p className="font-serif text-xl font-semibold tracking-[0.08em]">VideoMind</p>
              <p className="text-xs uppercase tracking-[0.32em] text-[var(--muted)]">
                Editorial Downloader
              </p>
            </div>
          </Link>

          <nav className="flex items-center gap-2 text-sm">
            <NavLink
              className={({ isActive }) =>
                `rounded-full px-4 py-2 transition ${
                  isActive ? 'bg-[var(--ink)] text-[var(--paper)]' : 'text-[var(--muted)]'
                }`
              }
              to="/"
            >
              工作台
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                `inline-flex items-center gap-2 rounded-full px-4 py-2 transition ${
                  isActive ? 'bg-[var(--ink)] text-[var(--paper)]' : 'text-[var(--muted)]'
                }`
              }
              to="/settings"
            >
              <Settings2 size={14} />
              设置
            </NavLink>
          </nav>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
