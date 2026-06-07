export type Mt5Account = {
  id: number
  platform: string
  mt5_login: string
  mt5_server: string
  mt5_company: string
  currency: string
  balance: number
  equity: number
  margin: number
  margin_free: number
  margin_level: number
  profit: number
  last_sync_at: string | null
}

export type Mt5Order = {
  id: number
  ticket: number
  symbol: string
  order_type: string
  volume: number
  price_open: number
  price_current: number
  sl: number
  tp: number
  commission: number
  swap: number
  time_setup: string | null
  time_done: string | null
  updated_at: string
}

export type Mt5Position = {
  id: number
  ticket: number
  symbol: string
  position_type: string
  volume: number
  price_open: number
  price_current: number
  sl: number
  tp: number
  commission: number
  swap: number
  profit: number
  time_open: string | null
  updated_at: string
}
