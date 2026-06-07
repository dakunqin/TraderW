from __future__ import annotations

import hashlib
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.config import settings

_PW_ALG = "pbkdf2_sha256"
_PW_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PW_ITERATIONS)
    salt_b64 = urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    dk_b64 = urlsafe_b64encode(dk).decode("ascii").rstrip("=")
    return f"{_PW_ALG}${_PW_ITERATIONS}${salt_b64}${dk_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        alg, iters_s, salt_b64, dk_b64 = password_hash.split("$", 3)
        if alg != _PW_ALG:
            return False
        iters = int(iters_s)
        salt = urlsafe_b64decode(salt_b64 + "==")
        expected = urlsafe_b64decode(dk_b64 + "==")
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters)
    return secrets.compare_digest(actual, expected)


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "type": "access", "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.refresh_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "type": "refresh", "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def generate_api_key() -> tuple[str, str, str]:
    secret = secrets.token_urlsafe(32)
    prefix = secret[:8]
    plaintext = f"ak_{prefix}_{secret}"
    return plaintext, prefix, hash_api_key(plaintext)


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
