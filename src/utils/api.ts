export type ApiError = {
  status: number
  message: string
}

export async function apiRequest<T>(
  path: string,
  opts: {
    method?: string
    body?: unknown
    accessToken?: string | null
    headers?: Record<string, string>
  } = {},
): Promise<T> {
  const envBaseUrl = (import.meta.env.VITE_API_BASE as string | undefined)?.trim()
  const inferredBaseUrl =
    typeof window !== 'undefined'
      ? `${window.location.protocol}//${window.location.hostname}`
      : 'http://localhost'
  const baseUrl = (envBaseUrl && envBaseUrl.length > 0 ? envBaseUrl : inferredBaseUrl).replace(/\/+$/, '')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(opts.headers ?? {}),
  }
  if (opts.accessToken) {
    headers.Authorization = `Bearer ${opts.accessToken}`
  }

  let res: Response
  try {
    res = await fetch(`${baseUrl}${path}`, {
      method: opts.method ?? (opts.body ? 'POST' : 'GET'),
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    })
  } catch (e: any) {
    const err: ApiError = {
      status: 0,
      message: `Failed to fetch: ${baseUrl}${path}${e?.message ? ` (${e.message})` : ''}`,
    }
    throw err
  }

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const data = await res.json()
      if (typeof data?.detail === 'string') message = data.detail
    } catch {
      void 0
    }
    const err: ApiError = { status: res.status, message }
    throw err
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}
