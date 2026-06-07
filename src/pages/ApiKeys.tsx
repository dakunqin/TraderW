import { useEffect, useState } from 'react'
import { Copy, Plus, ShieldOff, Trash2 } from 'lucide-react'

import AppShell from '@/components/AppShell'
import PageHeader from '@/components/PageHeader'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'
import type { ApiKeyCreateResponse, ApiKeyItem } from '@/types/apiKey'
import { apiRequest } from '@/utils/api'

export default function ApiKeys() {
  const accessToken = useAuthStore((s) => s.tokens?.accessToken ?? null)
  const logout = useAuthStore((s) => s.logout)

  const [items, setItems] = useState<ApiKeyItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [createdKey, setCreatedKey] = useState<ApiKeyCreateResponse | null>(null)

  const reload = () => {
    setLoading(true)
    setError(null)
    apiRequest<ApiKeyItem[]>('/api/v1/api-keys', { accessToken })
      .then(setItems)
      .catch((e: any) => {
        if (e?.status === 401) logout()
        setError(e?.message ?? '加载失败')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    reload()
  }, [])

  return (
    <AppShell>
      <PageHeader
        title="API Key"
        subtitle="用于 EA 同步与执行指令。Key 只在创建时显示一次，请妥善保存。"
        right={
          <button
            className={cn('rounded-xl bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-white')}
            onClick={async () => {
              setError(null)
              try {
                const res = await apiRequest<ApiKeyCreateResponse>('/api/v1/api-keys', { method: 'POST', accessToken })
                setCreatedKey(res)
                reload()
              } catch (e: any) {
                if (e?.status === 401) logout()
                setError(e?.message ?? '创建失败')
              }
            }}
          >
            <span className="inline-flex items-center gap-2">
              <Plus className="h-4 w-4" />
              生成 Key
            </span>
          </button>
        }
      />

      {error ? <div className="mb-4 rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

      {createdKey ? (
        <div className="mb-6 rounded-2xl border border-emerald-900/60 bg-emerald-950/30 p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-sm font-semibold text-emerald-100">已生成 API Key（只显示一次）</div>
              <div className="mt-1 text-xs text-emerald-200/70">prefix: {createdKey.prefix}</div>
            </div>
            <div className="flex items-center gap-2">
              <button
                className="rounded-xl border border-emerald-900/60 bg-emerald-950 px-3 py-2 text-xs text-emerald-100 hover:bg-emerald-900/20"
                onClick={async () => {
                  await navigator.clipboard.writeText(createdKey.api_key)
                }}
              >
                <span className="inline-flex items-center gap-2">
                  <Copy className="h-4 w-4" />
                  复制
                </span>
              </button>
              <button
                className="rounded-xl border border-emerald-900/60 bg-emerald-950 px-3 py-2 text-xs text-emerald-100 hover:bg-emerald-900/20"
                onClick={() => setCreatedKey(null)}
              >
                关闭
              </button>
            </div>
          </div>
          <div className="mt-3 rounded-xl border border-emerald-900/60 bg-emerald-950 px-3 py-2 font-mono text-xs text-emerald-50">
            {createdKey.api_key}
          </div>
        </div>
      ) : null}

      <div className="overflow-hidden rounded-2xl border border-zinc-800">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-zinc-950">
            <tr className="border-b border-zinc-800 text-xs text-zinc-500">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Prefix</th>
              <th className="px-4 py-3 font-medium">状态</th>
              <th className="px-4 py-3 font-medium">创建时间</th>
              <th className="px-4 py-3 font-medium">最后使用</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody className="bg-zinc-950/40">
            {loading ? (
              <tr>
                <td className="px-4 py-6 text-zinc-400" colSpan={6}>
                  加载中…
                </td>
              </tr>
            ) : items.length ? (
              items.map((k) => (
                <tr key={k.id} className="border-b border-zinc-800 last:border-b-0">
                  <td className="px-4 py-3 text-zinc-200">{k.id}</td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-300">{k.prefix}</td>
                  <td className="px-4 py-3">
                    <span className={cn('rounded-lg border px-2 py-1 text-xs', k.is_active ? 'border-emerald-900/60 text-emerald-200' : 'border-zinc-800 text-zinc-500')}>
                      {k.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-zinc-400">{new Date(k.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3 text-zinc-400">{k.last_used_at ? new Date(k.last_used_at).toLocaleString() : '—'}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 hover:bg-zinc-900 disabled:opacity-60"
                        disabled={!k.is_active}
                        onClick={async () => {
                          setError(null)
                          try {
                            await apiRequest(`/api/v1/api-keys/${k.id}/disable`, { method: 'POST', accessToken })
                            reload()
                          } catch (e: any) {
                            if (e?.status === 401) logout()
                            setError(e?.message ?? '操作失败')
                          }
                        }}
                      >
                        <span className="inline-flex items-center gap-2">
                          <ShieldOff className="h-4 w-4" />
                          禁用
                        </span>
                      </button>
                      <button
                        className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 hover:bg-zinc-900"
                        onClick={async () => {
                          setError(null)
                          try {
                            await apiRequest(`/api/v1/api-keys/${k.id}`, { method: 'DELETE', accessToken })
                            reload()
                          } catch (e: any) {
                            if (e?.status === 401) logout()
                            setError(e?.message ?? '删除失败')
                          }
                        }}
                      >
                        <span className="inline-flex items-center gap-2">
                          <Trash2 className="h-4 w-4" />
                          删除
                        </span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-6 text-zinc-400" colSpan={6}>
                  暂无 API Key
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  )
}

