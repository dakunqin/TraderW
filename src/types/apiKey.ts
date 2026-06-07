export type ApiKeyItem = {
  id: number
  prefix: string
  is_active: boolean
  created_at: string
  last_used_at: string | null
}

export type ApiKeyCreateResponse = {
  id: number
  prefix: string
  api_key: string
}

