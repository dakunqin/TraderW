import { useState } from 'react'
import { Link } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { apiRequest } from '@/utils/api'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sent, setSent] = useState(false)

  return (
    <div className="min-h-screen bg-zinc-950 px-4 py-10 text-zinc-100">
      <div className="mx-auto w-full max-w-md rounded-3xl border border-zinc-800 bg-zinc-950/40 p-6 backdrop-blur">
        <div className="text-lg font-semibold tracking-wide">找回密码</div>
        <div className="mt-1 text-sm text-zinc-400">输入注册邮箱，我们会发送重置链接。</div>

        <form
          className="mt-6 space-y-4"
          onSubmit={async (e) => {
            e.preventDefault()
            setLoading(true)
            setError(null)
            try {
              await apiRequest('/api/v1/auth/forgot-password', { method: 'POST', body: { email: email.trim() } })
              setSent(true)
            } catch (err: any) {
              setError(err?.message ?? '发送失败')
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

          {sent ? <div className="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-200">如果邮箱存在，重置邮件已发送。</div> : null}
          {error ? <div className="rounded-xl border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div> : null}

          <button
            disabled={loading}
            className={cn(
              'w-full rounded-xl bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-950',
              'hover:bg-white disabled:cursor-not-allowed disabled:opacity-60',
            )}
            type="submit"
          >
            {loading ? '发送中…' : '发送重置邮件'}
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

