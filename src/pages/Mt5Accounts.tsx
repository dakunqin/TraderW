import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'

import AppShell from '@/components/AppShell'
import PageHeader from '@/components/PageHeader'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'
import type { Mt5Account } from '@/types/mt5'
import { apiRequest } from '@/utils/api'

export default function Mt5Accounts() {
  const accessToken = useAuthStore((s) => s.tokens?.accessToken ?? null)
  const logout = useAuthStore((s) => s.logout)

  const [items, setItems] = useState<Mt5Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    let inFlight = false
    const refreshMs = 5000

    const load = async (showLoading: boolean) => {
      if (inFlight) return
      inFlight = true
      if (showLoading) setLoading(true)
      setError(null)
      try {
        const res = await apiRequest<Mt5Account[]>('/api/v1/mt5-accounts', { accessToken })
        if (!mounted) return
        setItems(res)
      } catch (e: any) {
        if (!mounted) return
        if (e?.status === 401) logout()
        setError(e?.message ?? '加载失败')
      } finally {
        inFlight = false
        if (!mounted) return
        if (showLoading) setLoading(false)
      }
    }

    void load(true)
    const timer = setInterval(() => void load(false), refreshMs)
    return () => {
      mounted = false
      clearInterval(timer)
    }
  }, [accessToken, logout])

  return (
    <AppShell>
      <PageHeader title="终端账号" subtitle="按账号聚合订单与持仓。点击进入可对单个 ticket 发起平仓。" />

      {error ? <div className="mb-4 rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

      <div className="overflow-hidden rounded-2xl border border-zinc-800">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-zinc-950">
            <tr className="border-b border-zinc-800 text-xs text-zinc-500">
              <th className="px-4 py-3 font-medium">终端</th>
              <th className="px-4 py-3 font-medium">登录号</th>
              <th className="px-4 py-3 font-medium">服务器</th>
              <th className="px-4 py-3 font-medium">净值</th>
              <th className="px-4 py-3 font-medium">余额</th>
              <th className="px-4 py-3 font-medium">保证金</th>
              <th className="px-4 py-3 font-medium">可用保证金</th>
              <th className="px-4 py-3 font-medium">亏损</th>
              <th className="px-4 py-3 font-medium">最近同步</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody className="bg-zinc-950/40">
            {loading ? (
              <tr>
                <td className="px-4 py-6 text-zinc-400" colSpan={10}>
                  加载中…
                </td>
              </tr>
            ) : items.length ? (
              items.map((a) => (
                <tr key={a.id} className="border-b border-zinc-800 last:border-b-0">
                  <td className="px-4 py-3 text-zinc-300">{(a.platform || 'mt5').toUpperCase()}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-200">{a.mt5_login}</td>
                  <td className="px-4 py-3 text-zinc-300">{a.mt5_server}</td>
                  <td className="px-4 py-3 text-zinc-200">{a.equity.toFixed(2)}</td>
                  <td className="px-4 py-3 text-zinc-200">{a.balance.toFixed(2)}</td>
                  <td className="px-4 py-3 text-zinc-200">{a.margin.toFixed(2)}</td>
                  <td className="px-4 py-3 text-zinc-200">{a.margin_free.toFixed(2)}</td>
                  <td className={cn('px-4 py-3', a.profit < 0 ? 'text-red-300' : 'text-zinc-200')}>{(a.profit < 0 ? -a.profit : 0).toFixed(2)}</td>
                  <td className="px-4 py-3 text-zinc-400">{a.last_sync_at ? new Date(a.last_sync_at).toLocaleString() : '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end">
                      <Link
                        className={cn('inline-flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 hover:bg-zinc-900')}
                        to={`/mt5-accounts/${a.id}`}
                      >
                        查看
                        <ChevronRight className="h-4 w-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-6 text-zinc-400" colSpan={10}>
                  暂无数据。先在 API Key 页面生成 Key，并让 EA 正常同步。
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  )
}
