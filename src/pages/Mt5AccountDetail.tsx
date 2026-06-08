import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, XCircle } from 'lucide-react'

import AppShell from '@/components/AppShell'
import PageHeader from '@/components/PageHeader'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'
import type { Mt5Account, Mt5Order, Mt5Position } from '@/types/mt5'
import { apiRequest } from '@/utils/api'

type Tab = 'positions' | 'orders'

export default function Mt5AccountDetail() {
  const params = useParams()
  const mt5AccountId = Number(params.id)

  const accessToken = useAuthStore((s) => s.tokens?.accessToken ?? null)
  const logout = useAuthStore((s) => s.logout)

  const [account, setAccount] = useState<Mt5Account | null>(null)
  const [orders, setOrders] = useState<Mt5Order[]>([])
  const [positions, setPositions] = useState<Mt5Position[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('positions')
  const [actionMsg, setActionMsg] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    let inFlight = false
    const refreshMs = 5000

    const load = async (showLoading: boolean) => {
      if (inFlight) return
      inFlight = true
      if (showLoading) setLoading(true)
      setError(null)
      if (showLoading) setActionMsg(null)

      try {
        const [accounts, os, ps] = await Promise.all([
          apiRequest<Mt5Account[]>('/api/v1/mt5-accounts', { accessToken }),
          apiRequest<Mt5Order[]>(`/api/v1/mt5-accounts/${mt5AccountId}/orders`, { accessToken }),
          apiRequest<Mt5Position[]>(`/api/v1/mt5-accounts/${mt5AccountId}/positions`, { accessToken }),
        ])
        if (!mounted) return
        setAccount(accounts.find((a) => a.id === mt5AccountId) ?? null)
        setOrders(os)
        setPositions(ps)
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
  }, [accessToken, logout, mt5AccountId])

  const subtitle = useMemo(() => {
    if (!account) return '—'
    const sync = account.last_sync_at ? new Date(account.last_sync_at).toLocaleString() : '—'
    const p = (account.platform || 'mt5').toUpperCase()
    return `${p} · ${account.mt5_login} · ${account.mt5_server} · 最近同步 ${sync}`
  }, [account])

  const moneySummary = useMemo(() => {
    if (!account) return null
    const cur = account.currency || ''
    const parts = [
      `余额: ${account.balance.toFixed(2)} ${cur}`,
      `净值: ${account.equity.toFixed(2)} ${cur}`,
      `已用预付款: ${account.margin.toFixed(2)} ${cur}`,
      `可用预付款: ${account.margin_free.toFixed(2)} ${cur}`,
      `预付款比例: ${account.margin_level.toFixed(2)}%`,
      `浮动盈亏: ${account.profit.toFixed(2)} ${cur}`,
    ]
    return parts.join('  ·  ')
  }, [account])

  return (
    <AppShell>
      <PageHeader
        title="账号详情"
        subtitle={subtitle}
        right={
          <Link className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900" to="/mt5-accounts">
            <span className="inline-flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              返回
            </span>
          </Link>
        }
      />

      {error ? <div className="mb-4 rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}
      {actionMsg ? <div className="mb-4 rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-200">{actionMsg}</div> : null}
      {moneySummary ? <div className="mb-4 rounded-xl border border-zinc-800 bg-zinc-950/40 px-3 py-2 text-xs text-zinc-300">{moneySummary}</div> : null}

      <div className="mb-4 flex items-center gap-2">
        <button
          className={cn(
            'rounded-xl border px-3 py-2 text-sm',
            tab === 'positions' ? 'border-zinc-700 bg-zinc-900 text-zinc-50' : 'border-zinc-800 bg-zinc-950 text-zinc-400 hover:bg-zinc-900',
          )}
          onClick={() => setTab('positions')}
        >
          持仓 ({positions.length})
        </button>
        <button
          className={cn(
            'rounded-xl border px-3 py-2 text-sm',
            tab === 'orders' ? 'border-zinc-700 bg-zinc-900 text-zinc-50' : 'border-zinc-800 bg-zinc-950 text-zinc-400 hover:bg-zinc-900',
          )}
          onClick={() => setTab('orders')}
        >
          挂单 ({orders.length})
        </button>
      </div>

      {loading ? (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-6 text-sm text-zinc-400">加载中…</div>
      ) : tab === 'positions' ? (
        <div className="overflow-x-auto rounded-2xl border border-zinc-800">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-zinc-950">
              <tr className="border-b border-zinc-800 text-xs text-zinc-500">
                <th className="px-4 py-3 font-medium">订单</th>
                <th className="px-4 py-3 font-medium">时间</th>
                <th className="px-4 py-3 font-medium">类型</th>
                <th className="px-4 py-3 font-medium">手数</th>
                <th className="px-4 py-3 font-medium">交易品种</th>
                <th className="px-4 py-3 font-medium">开仓价</th>
                <th className="px-4 py-3 font-medium">止损</th>
                <th className="px-4 py-3 font-medium">止盈</th>
                <th className="px-4 py-3 font-medium">当前价</th>
                <th className="px-4 py-3 font-medium">手续费</th>
                <th className="px-4 py-3 font-medium">库存费</th>
                <th className="px-4 py-3 font-medium">获利</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="bg-zinc-950/40">
              {positions.length ? (
                positions.map((p) => (
                  <tr key={p.id} className="border-b border-zinc-800 last:border-b-0">
                    <td className="px-4 py-3 font-mono text-xs text-zinc-200">{p.ticket}</td>
                    <td className="px-4 py-3 text-zinc-400">{p.time_open ? new Date(p.time_open).toLocaleString() : '—'}</td>
                    <td className="px-4 py-3 text-zinc-400">{p.position_type}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.volume}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.symbol}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.price_open}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.sl}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.tp}</td>
                    <td className="px-4 py-3 text-zinc-200">{p.price_current}</td>
                    <td className={cn('px-4 py-3', p.commission >= 0 ? 'text-zinc-200' : 'text-red-300')}>{p.commission.toFixed(2)}</td>
                    <td className={cn('px-4 py-3', p.swap >= 0 ? 'text-zinc-200' : 'text-red-300')}>{p.swap.toFixed(2)}</td>
                    <td className={cn('px-4 py-3', p.profit >= 0 ? 'text-emerald-300' : 'text-red-300')}>{p.profit.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end">
                        <button
                          className="rounded-xl bg-red-500/90 px-3 py-2 text-xs font-semibold text-zinc-950 hover:bg-red-400"
                          onClick={async () => {
                            setError(null)
                            setActionMsg(null)
                            try {
                              const res = await apiRequest<{ id: number; status: string }>(`/api/v1/positions/${p.id}/close`, { method: 'POST', accessToken })
                              setActionMsg(`已发起平仓指令：action #${res.id}（状态 ${res.status}）`)
                            } catch (e: any) {
                              if (e?.status === 401) logout()
                              setError(e?.message ?? '操作失败')
                            }
                          }}
                        >
                          <span className="inline-flex items-center gap-2">
                            <XCircle className="h-4 w-4" />
                            平仓
                          </span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="px-4 py-6 text-zinc-400" colSpan={13}>
                    暂无持仓
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-zinc-800">
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-zinc-950">
              <tr className="border-b border-zinc-800 text-xs text-zinc-500">
                <th className="px-4 py-3 font-medium">订单</th>
                <th className="px-4 py-3 font-medium">时间</th>
                <th className="px-4 py-3 font-medium">类型</th>
                <th className="px-4 py-3 font-medium">手数</th>
                <th className="px-4 py-3 font-medium">交易品种</th>
                <th className="px-4 py-3 font-medium">挂单价</th>
                <th className="px-4 py-3 font-medium">止损</th>
                <th className="px-4 py-3 font-medium">止盈</th>
                <th className="px-4 py-3 font-medium">当前价</th>
                <th className="px-4 py-3 font-medium">手续费</th>
                <th className="px-4 py-3 font-medium">库存费</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="bg-zinc-950/40">
              {orders.length ? (
                orders.map((o) => (
                  <tr key={o.id} className="border-b border-zinc-800 last:border-b-0">
                    <td className="px-4 py-3 font-mono text-xs text-zinc-200">{o.ticket}</td>
                    <td className="px-4 py-3 text-zinc-400">{o.time_setup ? new Date(o.time_setup).toLocaleString() : '—'}</td>
                    <td className="px-4 py-3 text-zinc-400">{o.order_type}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.volume}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.symbol}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.price_open}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.sl}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.tp}</td>
                    <td className="px-4 py-3 text-zinc-200">{o.price_current}</td>
                    <td className={cn('px-4 py-3', o.commission >= 0 ? 'text-zinc-200' : 'text-red-300')}>{o.commission.toFixed(2)}</td>
                    <td className={cn('px-4 py-3', o.swap >= 0 ? 'text-zinc-200' : 'text-red-300')}>{o.swap.toFixed(2)}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end">
                        <button
                          className="rounded-xl bg-red-500/90 px-3 py-2 text-xs font-semibold text-zinc-950 hover:bg-red-400"
                          onClick={async () => {
                            setError(null)
                            setActionMsg(null)
                            try {
                              const res = await apiRequest<{ id: number; status: string }>(`/api/v1/orders/${o.id}/close`, { method: 'POST', accessToken })
                              setActionMsg(`已发起撤单/平仓指令：action #${res.id}（状态 ${res.status}）`)
                            } catch (e: any) {
                              if (e?.status === 401) logout()
                              setError(e?.message ?? '操作失败')
                            }
                          }}
                        >
                          <span className="inline-flex items-center gap-2">
                            <XCircle className="h-4 w-4" />
                            取消
                          </span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="px-4 py-6 text-zinc-400" colSpan={12}>
                    暂无挂单
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  )
}
