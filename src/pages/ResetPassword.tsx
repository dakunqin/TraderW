import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { apiRequest } from '@/utils/api'

export default function ResetPassword() {
  const navigate = useNavigate()
  const [params] = useSearchParams()

  const token = useMemo(() => params.get('token') ?? '', [params])
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState(false)

  return (
    <div className="min-h-screen bg-zinc-950 px-4 py-10 text-zinc-100">
      <div className="mx-auto w-full max-w-md rounded-3xl border border-zinc-800 bg-zinc-950/40 p-6 backdrop-blur">
        <div className="text-lg font-semibold tracking-wide">重置密码</div>
        <div className="mt-1 text-sm text-zinc-400">设置一个新密码。</div>

        <form
          className="mt-6 space-y-4"
          onSubmit={async (e) => {
            e.preventDefault()
            setLoading(true)
            setError(null)
            try {
              await apiRequest('/api/v1/auth/reset-password', { method: 'POST', body: { token, new_password: newPassword } })
              setDone(true)
              setTimeout(() => navigate('/login', { replace: true }), 600)
            } catch (err: any) {
              setError(err?.message ?? '重置失败')
            } finally {
              setLoading(false)
            }
          }}
        >
          <label className="block">
            <div className="text-xs text-zinc-400">Token</div>
            <input
              className={cn(
                'mt-2 w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 font-mono text-xs text-zinc-200 outline-none',
                'focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700/40',
              )}
              value={token}
              readOnly
            />
          </label>

          <label className="block">
            <div className="text-xs text-zinc-400">新密码</div>
            <input
              className={cn(
                'mt-2 w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm outline-none',
                'focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700/40',
              )}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="至少 8 位"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
            />
          </label>

          {done ? <div className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-200">已重置，正在跳转到登录…</div> : null}
          {error ? <div className="rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

          <button
            disabled={loading || !token}
            className={cn(
              'w-full rounded-xl bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950',
              'hover:bg-white disabled:cursor-not-allowed disabled:opacity-60',
            )}
            type="submit"
          >
            {loading ? '提交中…' : '重置密码'}
          </button>
        </form>

        <div className="mt-6 text-sm text-zinc-400">
          <Link className="text-zinc-100 underline decoration-zinc-600 underline-offset-4 hover:decoration-zinc-200" to="/login">
            返回登录
          </Link>
        </div>
      </div>
    </div>
  )
}

