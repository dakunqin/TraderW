import os
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.models import Mt5Account, User
from app.db.session import get_db

router = APIRouter()


@router.get("/debug/info")
def debug_info(
    mt5_login: str | None = None,
    mt5_server: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = settings.database_url
    resolved_db_path = None
    db_exists = None
    db_size = None
    if url.startswith("sqlite:///"):
        p = url[len("sqlite:///") :]
        if p.startswith("./"):
            p = os.path.join(os.getcwd(), p[2:])
        resolved_db_path = str(Path(p).resolve())
        try:
            st = Path(resolved_db_path).stat()
            db_exists = True
            db_size = st.st_size
        except FileNotFoundError:
            db_exists = False

    total = db.scalar(select(func.count()).select_from(Mt5Account).where(Mt5Account.user_id == user.id)) or 0
    match = None
    if mt5_login and mt5_server:
        acc = db.scalar(
            select(Mt5Account).where(
                Mt5Account.user_id == user.id,
                Mt5Account.mt5_login == mt5_login,
                Mt5Account.mt5_server == mt5_server,
            )
        )
        if acc:
            match = {
                "id": acc.id,
                "platform": acc.platform,
                "mt5_login": acc.mt5_login,
                "mt5_server": acc.mt5_server,
                "last_sync_at": acc.last_sync_at,
            }

    return {
        "cwd": os.getcwd(),
        "database_url": url,
        "resolved_db_path": resolved_db_path,
        "db_exists": db_exists,
        "db_size": db_size,
        "user_id": user.id,
        "total_accounts": total,
        "match": match,
    }
