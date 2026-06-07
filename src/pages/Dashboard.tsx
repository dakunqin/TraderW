import type { ReactNode } from 'react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, Server, Timer } from 'lucide-react'

import AppShell from '@/components/AppShell'
import PageHeader from '@/components/PageHeader'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'
import type { Mt5Account } from '@/types/mt5'
import { apiRequest } from '@/utils/api'

function StatCard(props: { label: string; value: string; icon: ReactNode }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
      <div className="flex items-center justify-between">
        <div className="text-xs text-zinc-400">{props.label}</div>
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-zinc-900 text-zinc-100">{props.icon}</div>
      </div>
      <div className="mt-3 text-2xl font-semibold tracking-tight">{props.value}</div>
    </div>
  )
}

export default function Dashboard() {
  const accessToken = useAuthStore((s) => s.tokens?.accessToken ?? null)
  const logout = useAuthStore((s) => s.logout)

  const [accounts, setAccounts] = useState<Mt5Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    apiRequest<Mt5Account[]>('/api/v1/mt5-accounts', { accessToken })
      .then((res) => {
        if (!mounted) return
        setAccounts(res)
      })
      .catch((e: any) => {
        if (!mounted) return
        if (e?.status === 401) logout()
        setError(e?.message ?? '加载失败')
      })
      .finally(() => {
        if (!mounted) return
        setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [accessToken, logout])

  const lastSync = useMemo(() => {
    const times = accounts.map((a) => (a.last_sync_at ? Date.parse(a.last_sync_at) : 0))
    const max = Math.max(0, ...times)
    return max ? new Date(max).toLocaleString() : '—'
  }, [accounts])

  return (
    <AppShell>
      <PageHeader
        title="概览"
        subtitle="如果看不到数据，先确认 EA 已运行且已允许 WebRequest URL"
        right={
          <Link
            className={cn('rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900')}
            to="/mt5-accounts"
          >
            查看终端账号
          </Link>
        }
      />

      {error ? <div className="mb-4 rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <StatCard label="终端账号数" value={loading ? '…' : String(accounts.length)} icon={<Server className="h-5 w-5" />} />
        <StatCard label="最近同步时间" value={loading ? '…' : lastSync} icon={<Timer className="h-5 w-5" />} />
        <StatCard label="状态" value={loading ? '…' : accounts.length ? '已连接' : '等待 EA'} icon={<Activity className="h-5 w-5" />} />
      </div>

      <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-950 p-4 text-sm text-zinc-300">
        <div className="font-semibold">下一步</div>
        <ol className="mt-2 list-decimal space-y-1 pl-5 text-zinc-400">
          <li>在 API Key 页面生成一个 Key（只显示一次）</li>
          <li>在 MT4/MT5 加载 EA，填入 Server URL 与 API Key</li>
          <li>等待 EA 同步后，在“终端账号”查看订单并发起平仓</li>
        </ol>
      </div>
    </AppShell>
  )
}
