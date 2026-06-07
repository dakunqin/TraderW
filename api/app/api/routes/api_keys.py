from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import generate_api_key
from app.db.models import ApiKey, User
from app.db.session import get_db
from app.schemas.api_key import ApiKeyCreateResponse, ApiKeyItem

router = APIRouter()


@router.get("", response_model=list[ApiKeyItem])
def list_api_keys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.id.desc())).all()
    return [
        ApiKeyItem(
            id=r.id,
            prefix=r.prefix,
            is_active=r.is_active,
            created_at=r.created_at,
            last_used_at=r.last_used_at,
        )
        for r in rows
    ]


@router.post("", response_model=ApiKeyCreateResponse)
def create_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plaintext, prefix, key_hash = generate_api_key()
    existing = db.scalar(select(ApiKey).where(ApiKey.key_hash == key_hash))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="API key collision, retry")
    row = ApiKey(user_id=user.id, key_hash=key_hash, prefix=prefix, is_active=True)
    db.add(row)
    db.commit()
    db.refresh(row)
    return ApiKeyCreateResponse(id=row.id, prefix=row.prefix, api_key=plaintext)


@router.post("/{api_key_id}/disable", response_model=ApiKeyItem)
def disable_api_key(api_key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user.id))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    row.is_active = False
    db.add(row)
    db.commit()
    db.refresh(row)
    return ApiKeyItem(
        id=row.id,
        prefix=row.prefix,
        is_active=row.is_active,
        created_at=row.created_at,
        last_used_at=row.last_used_at,
    )


@router.delete("/{api_key_id}")
def delete_api_key(api_key_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user.id))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

