from datetime import datetime

from pydantic import BaseModel


class ActionCreateResponse(BaseModel):
    id: int
    status: str


class ActionDispatchItem(BaseModel):
    id: int
    action_type: str
    target_kind: str
    ticket: int
    symbol: str
    volume: float
    requested_at: datetime


class ActionsDispatchResponse(BaseModel):
    actions: list[ActionDispatchItem]


class ActionResultCreateRequest(BaseModel):
    action_id: int
    status: str
    error_code: int | None = None
    error_message: str | None = None
    executed_at: str
