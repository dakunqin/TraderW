from sqlalchemy import Engine, text


def _sqlite_columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return {str(r[1]) for r in rows}


def _sqlite_add_column(engine: Engine, table: str, col: str, sql_type: str, default_sql: str) -> None:
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {sql_type} NOT NULL DEFAULT {default_sql}"))
        conn.commit()


def migrate(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return

    accounts = _sqlite_columns(engine, "mt5_accounts")
    if "platform" not in accounts:
        _sqlite_add_column(engine, "mt5_accounts", "platform", "TEXT", "'mt5'")
    if "margin_free" not in accounts:
        _sqlite_add_column(engine, "mt5_accounts", "margin_free", "REAL", "0")
    if "margin_level" not in accounts:
        _sqlite_add_column(engine, "mt5_accounts", "margin_level", "REAL", "0")
    if "profit" not in accounts:
        _sqlite_add_column(engine, "mt5_accounts", "profit", "REAL", "0")

    orders = _sqlite_columns(engine, "mt5_orders")
    if "price_current" not in orders:
        _sqlite_add_column(engine, "mt5_orders", "price_current", "REAL", "0")
    if "commission" not in orders:
        _sqlite_add_column(engine, "mt5_orders", "commission", "REAL", "0")
    if "swap" not in orders:
        _sqlite_add_column(engine, "mt5_orders", "swap", "REAL", "0")

    positions = _sqlite_columns(engine, "mt5_positions")
    if "price_current" not in positions:
        _sqlite_add_column(engine, "mt5_positions", "price_current", "REAL", "0")
    if "commission" not in positions:
        _sqlite_add_column(engine, "mt5_positions", "commission", "REAL", "0")
    if "swap" not in positions:
        _sqlite_add_column(engine, "mt5_positions", "swap", "REAL", "0")
