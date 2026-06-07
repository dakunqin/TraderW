from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    api_keys: Mapped[list[ApiKey]] = relationship(back_populates="user", cascade="all, delete-orphan")
    mt5_accounts: Mapped[list[Mt5Account]] = relationship(back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="api_keys")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (Index("ix_prt_user", "user_id"), Index("ix_prt_expires", "expires_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)



class Mt5Account(Base):
    __tablename__ = "mt5_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(8), nullable=False, default="mt5")
    mt5_login: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    mt5_server: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    mt5_company: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    equity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin_free: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin_level: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    profit: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="mt5_accounts")
    orders: Mapped[list[Mt5Order]] = relationship(back_populates="mt5_account", cascade="all, delete-orphan")
    positions: Mapped[list[Mt5Position]] = relationship(back_populates="mt5_account", cascade="all, delete-orphan")
    actions: Mapped[list[Action]] = relationship(back_populates="mt5_account", cascade="all, delete-orphan")


class Mt5Order(Base):
    __tablename__ = "mt5_orders"
    __table_args__ = (UniqueConstraint("mt5_account_id", "ticket", name="uq_order_ticket"), Index("ix_order_ticket", "ticket"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mt5_account_id: Mapped[int] = mapped_column(ForeignKey("mt5_accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    ticket: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    price_open: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    price_current: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    sl: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    tp: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    commission: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    swap: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    time_setup: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_done: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    mt5_account: Mapped[Mt5Account] = relationship(back_populates="orders")


class Mt5Position(Base):
    __tablename__ = "mt5_positions"
    __table_args__ = (UniqueConstraint("mt5_account_id", "ticket", name="uq_position_ticket"), Index("ix_position_ticket", "ticket"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mt5_account_id: Mapped[int] = mapped_column(ForeignKey("mt5_accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    ticket: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    position_type: Mapped[str] = mapped_column(String(32), nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    price_open: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    price_current: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    sl: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    tp: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    commission: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    swap: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    profit: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    time_open: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    mt5_account: Mapped[Mt5Account] = relationship(back_populates="positions")


class Action(Base):
    __tablename__ = "actions"
    __table_args__ = (
        Index("ix_action_status_mt5", "status", "mt5_account_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    mt5_account_id: Mapped[int] = mapped_column(ForeignKey("mt5_accounts.id", ondelete="CASCADE"), index=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    ticket: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    volume: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    mt5_account: Mapped[Mt5Account] = relationship(back_populates="actions")
    results: Mapped[list[ActionResult]] = relationship(back_populates="action", cascade="all, delete-orphan")


class ActionResult(Base):
    __tablename__ = "action_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[int] = mapped_column(ForeignKey("actions.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    error_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    action: Mapped[Action] = relationship(back_populates="results")
