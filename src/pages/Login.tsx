import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth'

export default function Login() {
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const tokens = useAuthStore((s) => s.tokens)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (tokens) return <Navigate to="/dashboard" replace />

  return (
    <div className="min-h-screen bg-zinc-950 px-4 py-10 text-zinc-100">
      <div className="mx-auto w-full max-w-md rounded-3xl border border-zinc-800 bg-zinc-950/40 p-6 backdrop-blur">
        <div className="text-lg font-semibold tracking-wide">登录</div>
        <div className="mt-1 text-sm text-zinc-400">登录后可查看已同步的 MT5 账号与订单，并发起平仓指令</div>

        <form
          className="mt-6 space-y-4"
          onSubmit={async (e) => {
            e.preventDefault()
            setLoading(true)
            setError(null)
            try {
              await login(email.trim(), password)
              navigate('/dashboard', { replace: true })
            } catch (err: any) {
              setError(err?.message ?? '登录失败')
            } finally {
              setLoading(false)
            }
          }}
        >
          <label className="block">
            <div className="text-xs text-zinc-400">邮箱</div>
            <input
              className={cn(
                'mt-2 w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm outline-none',
                'focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700/40',
              )}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              type="email"
              autoComplete="email"
              required
            />
          </label>

          <label className="block">
            <div className="text-xs text-zinc-400">密码</div>
            <input
              className={cn(
                'mt-2 w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm outline-none',
                'focus:border-zinc-600 focus:ring-2 focus:ring-zinc-700/40',
              )}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="至少 8 位"
              type="password"
              autoComplete="current-password"
              required
              minLength={8}
            />
          </label>

          {error ? <div className="rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

          <button
            disabled={loading}
            className={cn(
              'w-full rounded-xl bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950',
              'hover:bg-white disabled:cursor-not-allowed disabled:opacity-60',
            )}
            type="submit"
          >
            {loading ? '登录中…' : '登录'}
          </button>
        </form>

        <div className="mt-3 text-sm text-zinc-400">
          <Link className="text-zinc-100 underline decoration-zinc-600 underline-offset-4 hover:decoration-zinc-200" to="/forgot-password">
            忘记密码
          </Link>
        </div>

        <div className="mt-6 text-sm text-zinc-400">
          还没有账号？{' '}
          <Link className="text-zinc-100 underline decoration-zinc-600 underline-offset-4 hover:decoration-zinc-200" to="/register">
            去注册
          </Link>
        </div>
      </div>
    </div>
  )
}
