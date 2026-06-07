import { create } from 'zustand'

import { apiRequest } from '@/utils/api'

type Tokens = {
  accessToken: string
  refreshToken: string
}

type AuthState = {
  tokens: Tokens | null
  setTokens: (tokens: Tokens | null) => void
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
}

const storageKey = 'auth_tokens'

function loadTokens(): Tokens | null {
  try {
    const raw = localStorage.getItem(storageKey)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Tokens
    if (!parsed.accessToken || !parsed.refreshToken) return null
    return parsed
  } catch {
    return null
  }
}

export const useAuthStore = create<AuthState>((set, get) => ({
  tokens: loadTokens(),
  setTokens: (tokens) => {
    if (!tokens) {
      localStorage.removeItem(storageKey)
      set({ tokens: null })
      return
    }
    localStorage.setItem(storageKey, JSON.stringify(tokens))
    set({ tokens })
  },
  login: async (email, password) => {
    const res = await apiRequest<{ access_token: string; refresh_token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    get().setTokens({ accessToken: res.access_token, refreshToken: res.refresh_token })
  },
  register: async (email, password) => {
    await apiRequest('/api/v1/auth/register', { method: 'POST', body: { email, password } })
    await get().login(email, password)
  },
  logout: () => {
    get().setTokens(null)
  },
}))

