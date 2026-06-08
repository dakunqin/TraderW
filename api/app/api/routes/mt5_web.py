from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Action, Mt5Account, Mt5Order, Mt5Position, User
from app.db.session import get_db
from app.schemas.actions import ActionCreateResponse
from app.schemas.mt5 import Mt5AccountItem, Mt5OrderItem, Mt5PositionItem

router = APIRouter()


@router.get("/mt5-accounts", response_model=list[Mt5AccountItem])
def list_accounts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Mt5Account).where(Mt5Account.user_id == user.id).order_by(Mt5Account.id.desc())).all()
    acc_ids = [r.id for r in rows]
    order_counts: dict[int, int] = {}
    position_counts: dict[int, int] = {}
    if acc_ids:
        order_counts = dict(
            db.execute(
                select(Mt5Order.mt5_account_id, func.count(Mt5Order.id))
                .where(Mt5Order.mt5_account_id.in_(acc_ids))
                .group_by(Mt5Order.mt5_account_id)
            ).all()
        )
        position_counts = dict(
            db.execute(
                select(Mt5Position.mt5_account_id, func.count(Mt5Position.id))
                .where(Mt5Position.mt5_account_id.in_(acc_ids))
                .group_by(Mt5Position.mt5_account_id)
            ).all()
        )
    return [
        Mt5AccountItem(
            id=r.id,
            platform=r.platform,
            mt5_login=r.mt5_login,
            mt5_server=r.mt5_server,
            mt5_company=r.mt5_company,
            currency=r.currency,
            balance=r.balance,
            equity=r.equity,
            margin=r.margin,
            margin_free=r.margin_free,
            margin_level=r.margin_level,
            profit=r.profit,
            orders_count=order_counts.get(r.id, 0),
            positions_count=position_counts.get(r.id, 0),
            last_sync_at=r.last_sync_at,
        )
        for r in rows
    ]


@router.get("/mt5-accounts/{mt5_account_id}/orders", response_model=list[Mt5OrderItem])
def list_orders(mt5_account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.get(Mt5Account, mt5_account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    rows = db.scalars(select(Mt5Order).where(Mt5Order.mt5_account_id == acc.id).order_by(Mt5Order.id.desc())).all()
    return [
        Mt5OrderItem(
            id=r.id,
            ticket=r.ticket,
            symbol=r.symbol,
            order_type=r.order_type,
            volume=r.volume,
            price_open=r.price_open,
            price_current=r.price_current,
            sl=r.sl,
            tp=r.tp,
            commission=r.commission,
            swap=r.swap,
            time_setup=r.time_setup,
            time_done=r.time_done,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.get("/mt5-accounts/{mt5_account_id}/positions", response_model=list[Mt5PositionItem])
def list_positions(mt5_account_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.get(Mt5Account, mt5_account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    rows = db.scalars(select(Mt5Position).where(Mt5Position.mt5_account_id == acc.id).order_by(Mt5Position.id.desc())).all()
    return [
        Mt5PositionItem(
            id=r.id,
            ticket=r.ticket,
            symbol=r.symbol,
            position_type=r.position_type,
            volume=r.volume,
            price_open=r.price_open,
            price_current=r.price_current,
            sl=r.sl,
            tp=r.tp,
            commission=r.commission,
            swap=r.swap,
            profit=r.profit,
            time_open=r.time_open,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("/orders/{order_id}/close", response_model=ActionCreateResponse)
def close_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.get(Mt5Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    acc = db.get(Mt5Account, order.mt5_account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    existing = db.scalar(
        select(Action).where(
            Action.user_id == user.id,
            Action.mt5_account_id == acc.id,
            Action.action_type == "close",
            Action.target_kind == "order",
            Action.ticket == order.ticket,
            Action.status.in_(["pending", "dispatched"]),
        )
    )
    if existing:
        return ActionCreateResponse(id=existing.id, status=existing.status)
    action = Action(
        user_id=user.id,
        mt5_account_id=acc.id,
        action_type="close",
        target_kind="order",
        ticket=order.ticket,
        symbol=order.symbol,
        volume=order.volume,
        status="pending",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return ActionCreateResponse(id=action.id, status=action.status)


@router.post("/positions/{position_id}/close", response_model=ActionCreateResponse)
def close_position(position_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    position = db.get(Mt5Position, position_id)
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    acc = db.get(Mt5Account, position.mt5_account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    existing = db.scalar(
        select(Action).where(
            Action.user_id == user.id,
            Action.mt5_account_id == acc.id,
            Action.action_type == "close",
            Action.target_kind == "position",
            Action.ticket == position.ticket,
            Action.status.in_(["pending", "dispatched"]),
        )
    )
    if existing:
        return ActionCreateResponse(id=existing.id, status=existing.status)
    action = Action(
        user_id=user.id,
        mt5_account_id=acc.id,
        action_type="close",
        target_kind="position",
        ticket=position.ticket,
        symbol=position.symbol,
        volume=position.volume,
        status="pending",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return ActionCreateResponse(id=action.id, status=action.status)
