from datetime import datetime

from pydantic import BaseModel


class Mt5AccountPayload(BaseModel):
    platform: str = "mt5"
    mt5_login: str
    mt5_server: str
    mt5_company: str = ""
    currency: str = ""
    balance: float = 0
    equity: float = 0
    margin: float = 0
    margin_free: float = 0
    margin_level: float = 0
    profit: float = 0


class Mt5OrderPayload(BaseModel):
    ticket: int
    symbol: str
    order_type: str
    volume: float = 0
    price_open: float = 0
    price_current: float = 0
    sl: float = 0
    tp: float = 0
    commission: float = 0
    swap: float = 0
    time_setup: datetime | None = None
    time_done: datetime | None = None


class Mt5PositionPayload(BaseModel):
    ticket: int
    symbol: str
    position_type: str
    volume: float = 0
    price_open: float = 0
    price_current: float = 0
    sl: float = 0
    tp: float = 0
    commission: float = 0
    swap: float = 0
    profit: float = 0
    time_open: datetime | None = None


class Mt5SyncRequest(BaseModel):
    mt5_account: Mt5AccountPayload
    orders: list[Mt5OrderPayload] = []
    positions: list[Mt5PositionPayload] = []
    sent_at: str


class Mt5AccountItem(BaseModel):
    id: int
    platform: str
    mt5_login: str
    mt5_server: str
    mt5_company: str
    currency: str
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    profit: float
    orders_count: int
    positions_count: int
    last_sync_at: datetime | None


class Mt5OrderItem(BaseModel):
    id: int
    ticket: int
    symbol: str
    order_type: str
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    commission: float
    swap: float
    time_setup: datetime | None
    time_done: datetime | None
    updated_at: datetime


class Mt5PositionItem(BaseModel):
    id: int
    ticket: int
    symbol: str
    position_type: str
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    commission: float
    swap: float
    profit: float
    time_open: datetime | None
    updated_at: datetime
