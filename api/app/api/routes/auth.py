import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.email import send_email
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.db.models import PasswordResetToken, User
from app.db.session import get_db
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, OkResponse, RefreshRequest, RegisterRequest, ResetPasswordRequest, TokenPair, UserMe

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


@router.post("/register", response_model=UserMe)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserMe(id=user.id, email=user.email)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    subject = decoded.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return TokenPair(access_token=create_access_token(subject), refresh_token=create_refresh_token(subject))


@router.get("/me", response_model=UserMe)
def me(user: User = Depends(get_current_user)):
    return UserMe(id=user.id, email=user.email)


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/forgot-password", response_model=OkResponse)
def forgot_password(payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        return OkResponse()

    token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_expire_minutes)
    db.add(PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    db.commit()

    web_base = (settings.public_web_url or str(request.base_url).rstrip("/")).rstrip("/")
    reset_link = f"{web_base}/reset-password?token={token}"
    try:
        send_email(
            to_email=user.email,
            subject="Password reset",
            text_body=f"Reset your password:\n{reset_link}\n\nIf you cannot open the link, use this token:\n{token}\n",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("forgot-password email send failed")
        msg = str(e).strip()
        if not msg:
            msg = e.__class__.__name__
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SMTP send failed: {msg}")
    return OkResponse()


@router.post("/reset-password", response_model=OkResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = _hash_reset_token(payload.token)
    row = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))
    if not row or row.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    if row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    user = db.get(User, row.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user.password_hash = hash_password(payload.new_password)
    row.used_at = datetime.now(timezone.utc)
    db.add(user)
    db.add(row)
    db.commit()
    return OkResponse()
