from functools import lru_cache

import re
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _normalize_sqlite_url(url: str) -> str:
    if url == "sqlite:///:memory:":
        return url
    if not url.startswith("sqlite:///"):
        return url
    raw = url[len("sqlite:///") :]
    if re.match(r"^[A-Za-z]:[\\/]", raw) or re.match(r"^[A-Za-z]:/", raw):
        return "sqlite:///" + raw.replace("\\", "/")
    base = Path(__file__).resolve().parents[2]
    abs_path = (base / raw).resolve()
    return "sqlite:///" + abs_path.as_posix()


@lru_cache
def get_engine():
    url = settings.database_url
    if url.startswith("sqlite:"):
        url = _normalize_sqlite_url(url)
        if url == "sqlite:///:memory:":
            return create_engine(
                url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    db: Session = get_session_local()()
    try:
        yield db
    finally:
        db.close()
