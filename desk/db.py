"""Tiny database layer: Postgres (Neon) in production, SQLite for tests/local.

SQL is written with `?` placeholders and translated for Postgres.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id {pk}, started_at TEXT NOT NULL, finished_at TEXT, kind TEXT, stats TEXT, errors TEXT
);
CREATE TABLE IF NOT EXISTS pools (
    pool_address TEXT PRIMARY KEY, token_mint TEXT NOT NULL, name TEXT, symbol TEXT, dex TEXT,
    pool_created_at TEXT, first_seen_at TEXT NOT NULL, last_snapshot_at TEXT,
    source TEXT, active INTEGER NOT NULL DEFAULT 1, missing_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS pools_token ON pools(token_mint);
CREATE TABLE IF NOT EXISTS snapshots (
    id {pk}, pool_address TEXT NOT NULL, ts TEXT NOT NULL, price_usd REAL, liquidity_usd REAL,
    fdv_usd REAL, vol_m5 REAL, vol_h1 REAL, vol_h6 REAL, vol_h24 REAL,
    chg_m5 REAL, chg_h1 REAL, chg_h6 REAL, chg_h24 REAL,
    buys_h1 INTEGER, sells_h1 INTEGER, buyers_h1 INTEGER, sellers_h1 INTEGER, txns_h24 INTEGER
);
CREATE INDEX IF NOT EXISTS snapshots_pool_ts ON snapshots(pool_address, ts);
CREATE TABLE IF NOT EXISTS safety_checks (
    id {pk}, token_mint TEXT NOT NULL, pool_address TEXT, ts TEXT NOT NULL, passed INTEGER NOT NULL,
    reasons TEXT, details TEXT
);
CREATE INDEX IF NOT EXISTS safety_token_ts ON safety_checks(token_mint, ts);
CREATE TABLE IF NOT EXISTS signals (
    id {pk}, strategy TEXT NOT NULL, pool_address TEXT NOT NULL, token_mint TEXT NOT NULL,
    symbol TEXT, ts TEXT NOT NULL, signal_price REAL, liquidity_usd REAL, details TEXT,
    status TEXT NOT NULL, status_reason TEXT, leader TEXT
);
CREATE TABLE IF NOT EXISTS positions (
    id {pk}, strategy TEXT NOT NULL, signal_id INTEGER, pool_address TEXT NOT NULL,
    token_mint TEXT NOT NULL, symbol TEXT, size_usd REAL NOT NULL,
    signal_ts TEXT, signal_price REAL, entry_ts TEXT, entry_price REAL, entry_liquidity REAL,
    entry_slippage_pct REAL, tokens REAL, status TEXT NOT NULL,
    take_profit_price REAL, stop_loss_price REAL, max_hold_until TEXT, last_candle_ts INTEGER,
    exit_ts TEXT, exit_price REAL, exit_liquidity REAL, exit_slippage_pct REAL, exit_reason TEXT,
    is_rug INTEGER DEFAULT 0, proceeds_usd REAL, fixed_costs_usd REAL, net_pnl_usd REAL, net_return REAL,
    leader TEXT, cost_adj_pct REAL
);
CREATE TABLE IF NOT EXISTS leaders (
    wallet TEXT PRIMARY KEY, source TEXT, selected_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
    stats TEXT, last_sig TEXT, last_checked TEXT, deactivated_at TEXT
);
CREATE TABLE IF NOT EXISTS leader_screens (
    id {pk}, ts TEXT NOT NULL, candidates INTEGER, selected INTEGER, rows TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS leader_trades (
    sig TEXT PRIMARY KEY, wallet TEXT NOT NULL, block_time TEXT NOT NULL, mint TEXT NOT NULL,
    side TEXT NOT NULL, quote_delta REAL, token_delta REAL, seen_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS leader_trades_wallet ON leader_trades(wallet, mint, block_time);
CREATE INDEX IF NOT EXISTS positions_strategy ON positions(strategy, status);
"""


def _is_connection_error(e: Exception) -> bool:
    name = type(e).__name__
    return name in ("OperationalError", "InterfaceError", "IdleInTransactionSessionTimeout",
                    "AdminShutdown", "ConnectionTimeout") or "connection" in str(e).lower()


NO_ID_TABLES = {"pools", "leaders", "leader_trades"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


class DB:
    def __init__(self, url: str | None = None):
        url = url or os.environ.get("DATABASE_URL") or "sqlite:///desk.sqlite3"
        self.url = url
        if url.startswith(("postgres://", "postgresql://")):
            self.kind = "pg"
            self._connect_pg()
        else:
            self.kind = "sqlite"
            path = url.replace("sqlite:///", "", 1) if url.startswith("sqlite:///") else url
            self.conn = sqlite3.connect(path)
            self.conn.row_factory = sqlite3.Row

    def _connect_pg(self) -> None:
        # Autocommit: every write is saved at once. Runs spend minutes calling outside
        # APIs between writes, and Neon closes connections left idle inside a transaction.
        import psycopg  # only needed in production
        self.conn = psycopg.connect(self.url, autocommit=True, connect_timeout=30)

    # -- helpers -----------------------------------------------------------
    def _sql(self, sql: str) -> str:
        return sql.replace("?", "%s") if self.kind == "pg" else sql

    def init(self) -> None:
        pk = "BIGSERIAL PRIMARY KEY" if self.kind == "pg" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        for stmt in SCHEMA.format(pk=pk).split(";"):
            if stmt.strip():
                self.execute(stmt)
        self.commit()
        self._add_column("positions", "cost_adj_pct", "REAL")
        self.commit()

    def _add_column(self, table: str, col: str, typ: str) -> None:
        """Add a column to a table created by an older version."""
        if self.kind == "pg":
            self.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {typ}")
        elif col not in [r[1] for r in self.conn.execute(f"PRAGMA table_info({table})").fetchall()]:
            self.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")

    def execute(self, sql: str, params: tuple | list = ()):
        try:
            cur = self.conn.cursor()
            cur.execute(self._sql(sql), tuple(params))
            return cur
        except Exception as e:
            if self.kind != "pg" or not _is_connection_error(e):
                raise
            self._connect_pg()  # Neon dropped us (idle timeout / compute suspended): reconnect once
            cur = self.conn.cursor()
            cur.execute(self._sql(sql), tuple(params))
            return cur

    def insert(self, table: str, row: dict) -> int:
        cols = ", ".join(row)
        qs = ", ".join("?" for _ in row)
        vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in row.values()]
        if self.kind == "pg":
            if table in NO_ID_TABLES:
                self.execute(f"INSERT INTO {table} ({cols}) VALUES ({qs})", vals)
                return 0
            cur = self.execute(f"INSERT INTO {table} ({cols}) VALUES ({qs}) RETURNING id", vals)
            return cur.fetchone()[0]
        cur = self.execute(f"INSERT INTO {table} ({cols}) VALUES ({qs})", vals)
        return cur.lastrowid

    def update(self, table: str, key: str, key_val, row: dict) -> None:
        sets = ", ".join(f"{c} = ?" for c in row)
        vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in row.values()]
        self.execute(f"UPDATE {table} SET {sets} WHERE {key} = ?", [*vals, key_val])

    def all(self, sql: str, params: tuple | list = ()) -> list[dict]:
        cur = self.execute(sql, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def one(self, sql: str, params: tuple | list = ()) -> dict | None:
        rows = self.all(sql, params)
        return rows[0] if rows else None

    def upsert_pool(self, row: dict) -> bool:
        """Insert a pool if new. Returns True if it was new."""
        if self.one("SELECT pool_address FROM pools WHERE pool_address = ?", [row["pool_address"]]):
            return False
        self.insert("pools", row)
        return True

    def commit(self) -> None:
        if self.kind != "pg":
            self.conn.commit()

    def rollback(self) -> None:
        if self.kind != "pg":
            self.conn.rollback()

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass


@contextmanager
def connect(url: str | None = None):
    db = DB(url)
    try:
        db.init()
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
