from datetime import datetime

from pydantic import BaseModel


class ApiKeyCreateResponse(BaseModel):
    id: int
    prefix: str
    api_key: str


class ApiKeyItem(BaseModel):
    id: int
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None

