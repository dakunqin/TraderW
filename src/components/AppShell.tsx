import type { PropsWithChildren, ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { KeyRound, LayoutDashboard, LogOut, Server, Wallet } from 'lucide-react'

import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'

function SideLink(props: { to: string; icon: ReactNode; label: string }) {
  return (
    <NavLink
      to={props.to}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition',
          isActive ? 'bg-zinc-900 text-zinc-50 shadow-sm' : 'text-zinc-400 hover:bg-zinc-900/60 hover:text-zinc-100',
        )
      }
    >
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-zinc-950/60 text-zinc-200">{props.icon}</span>
      <span className="truncate">{props.label}</span>
    </NavLink>
  )
}

export default function AppShell({ children }: PropsWithChildren) {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 md:grid-cols-[260px_1fr]">
        <aside className="rounded-2xl border border-zinc-800 bg-zinc-950/40 p-4 backdrop-blur">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-zinc-900 text-zinc-50">
                <Wallet className="h-5 w-5" />
              </div>
              <div className="leading-tight">
                <div className="text-sm font-semibold tracking-wide">TraderW Relay</div>
                <div className="text-xs text-zinc-500">Orders · Actions · Audit</div>
              </div>
            </div>
            <button
              className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-300 hover:bg-zinc-900"
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >
              <span className="inline-flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                退出
              </span>
            </button>
          </div>

          <div className="mt-4 space-y-2">
            <SideLink to="/dashboard" icon={<LayoutDashboard className="h-4 w-4" />} label="概览" />
            <SideLink to="/mt5-accounts" icon={<Server className="h-4 w-4" />} label="终端账号" />
            <SideLink to="/api-keys" icon={<KeyRound className="h-4 w-4" />} label="API Key" />
          </div>

          <div className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-3 text-xs text-zinc-400">
            EA 通过 X-API-Key 鉴权同步数据；平仓由 EA 拉取指令后执行。
          </div>
        </aside>

        <main className="min-h-[70vh] rounded-2xl border border-zinc-800 bg-zinc-950/40 p-4 backdrop-blur md:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
