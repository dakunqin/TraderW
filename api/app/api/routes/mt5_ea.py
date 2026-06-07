import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_api_key_user
from app.db.models import Action, ActionResult, Mt5Account, Mt5Order, Mt5Position, User, utcnow
from app.db.session import get_db
from app.schemas.actions import ActionResultCreateRequest, ActionsDispatchResponse, ActionDispatchItem
from app.schemas.mt5 import Mt5SyncRequest

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


def _parse_dt(value: str) -> datetime:
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.now(timezone.utc)


@router.post("/sync")
def sync(payload: Mt5SyncRequest, request: Request, user: User = Depends(get_api_key_user), db: Session = Depends(get_db)):
    platform = (payload.mt5_account.platform or "mt5").lower()
    logger.info(
        "SYNC user_id=%s ip=%s platform=%s login=%s server=%s",
        user.id,
        request.client.host if request.client else None,
        platform,
        payload.mt5_account.mt5_login,
        payload.mt5_account.mt5_server,
    )
    acc = db.scalar(
        select(Mt5Account).where(
            Mt5Account.user_id == user.id,
            Mt5Account.platform == platform,
            Mt5Account.mt5_login == payload.mt5_account.mt5_login,
            Mt5Account.mt5_server == payload.mt5_account.mt5_server,
        )
    )
    if not acc:
        acc = Mt5Account(
            user_id=user.id,
            platform=platform,
            mt5_login=payload.mt5_account.mt5_login,
            mt5_server=payload.mt5_account.mt5_server,
        )
        db.add(acc)
        db.commit()
        db.refresh(acc)

    acc.platform = platform
    acc.mt5_company = payload.mt5_account.mt5_company
    acc.currency = payload.mt5_account.currency
    acc.balance = payload.mt5_account.balance
    acc.equity = payload.mt5_account.equity
    acc.margin = payload.mt5_account.margin
    acc.margin_free = payload.mt5_account.margin_free
    acc.margin_level = payload.mt5_account.margin_level
    acc.profit = payload.mt5_account.profit
    acc.last_sync_at = datetime.now(timezone.utc)
    db.add(acc)
    db.commit()

    existing_orders = {o.ticket: o for o in db.scalars(select(Mt5Order).where(Mt5Order.mt5_account_id == acc.id)).all()}
    seen_orders: set[int] = set()
    for o in payload.orders:
        seen_orders.add(o.ticket)
        item = existing_orders.get(o.ticket)
        if not item:
            item = Mt5Order(mt5_account_id=acc.id, ticket=o.ticket)
            db.add(item)
        item.symbol = o.symbol
        item.order_type = o.order_type
        item.volume = o.volume
        item.price_open = o.price_open
        item.price_current = o.price_current
        item.sl = o.sl
        item.tp = o.tp
        item.commission = o.commission
        item.swap = o.swap
        item.time_setup = o.time_setup
        item.time_done = o.time_done
        item.updated_at = utcnow()

    if seen_orders:
        db.execute(delete(Mt5Order).where(Mt5Order.mt5_account_id == acc.id, ~Mt5Order.ticket.in_(seen_orders)))
    else:
        db.execute(delete(Mt5Order).where(Mt5Order.mt5_account_id == acc.id))

    existing_positions = {p.ticket: p for p in db.scalars(select(Mt5Position).where(Mt5Position.mt5_account_id == acc.id)).all()}
    seen_positions: set[int] = set()
    for p in payload.positions:
        seen_positions.add(p.ticket)
        item = existing_positions.get(p.ticket)
        if not item:
            item = Mt5Position(mt5_account_id=acc.id, ticket=p.ticket)
            db.add(item)
        item.symbol = p.symbol
        item.position_type = p.position_type
        item.volume = p.volume
        item.price_open = p.price_open
        item.price_current = p.price_current
        item.sl = p.sl
        item.tp = p.tp
        item.commission = p.commission
        item.swap = p.swap
        item.profit = p.profit
        item.time_open = p.time_open
        item.updated_at = utcnow()

    if seen_positions:
        db.execute(delete(Mt5Position).where(Mt5Position.mt5_account_id == acc.id, ~Mt5Position.ticket.in_(seen_positions)))
    else:
        db.execute(delete(Mt5Position).where(Mt5Position.mt5_account_id == acc.id))

    db.commit()
    return {"ok": True}


@router.get("/actions", response_model=ActionsDispatchResponse)
def fetch_actions(
    mt5_login: str,
    mt5_server: str,
    platform: str | None = None,
    user: User = Depends(get_api_key_user),
    db: Session = Depends(get_db),
):
    q = select(Mt5Account).where(Mt5Account.user_id == user.id, Mt5Account.mt5_login == mt5_login, Mt5Account.mt5_server == mt5_server)
    if platform:
        q = q.where(Mt5Account.platform == platform.lower())
    acc = db.scalar(q)
    if not acc:
        return ActionsDispatchResponse(actions=[])
    actions = db.scalars(select(Action).where(Action.mt5_account_id == acc.id, Action.status == "pending").order_by(Action.id.asc())).all()
    now = datetime.now(timezone.utc)
    resp = [
        ActionDispatchItem(
            id=a.id,
            action_type=a.action_type,
            target_kind=a.target_kind,
            ticket=a.ticket,
            symbol=a.symbol,
            volume=a.volume,
            requested_at=a.requested_at,
        )
        for a in actions
    ]
    for a in actions:
        a.status = "dispatched"
        a.dispatched_at = now
        db.add(a)
    db.commit()
    return ActionsDispatchResponse(actions=resp)


@router.post("/action-results")
def action_result(payload: ActionResultCreateRequest, user: User = Depends(get_api_key_user), db: Session = Depends(get_db)):
    action = db.get(Action, payload.action_id)
    if not action or action.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    if payload.status not in {"success", "failed"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    res = ActionResult(
        action_id=action.id,
        status=payload.status,
        error_code=payload.error_code,
        error_message=payload.error_message,
        executed_at=_parse_dt(payload.executed_at),
    )
    db.add(res)
    action.status = "succeeded" if payload.status == "success" else "failed"
    action.completed_at = datetime.now(timezone.utc)
    db.add(action)
    db.commit()
    return {"ok": True}
