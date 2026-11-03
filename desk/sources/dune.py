"""Dune Analytics API (free plan): run SQL, wait, fetch rows. Read-only."""
from __future__ import annotations

import os
import time
from pathlib import Path

from . import http

BASE = "https://api.dune.com/api/v1"
SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


class DuneError(RuntimeError):
    pass


def _headers() -> dict:
    key = os.environ.get("DUNE_API_KEY")
    if not key:
        raise DuneError("DUNE_API_KEY is not set")
    return {"X-DUNE-API-KEY": key, "Content-Type": "application/json"}


def render(name: str, **params) -> str:
    sql = (SQL_DIR / name).read_text()
    for k, v in params.items():
        sql = sql.replace("{" + k + "}", str(v))
    return sql


def run_sql(sql: str, timeout_s: int = 900, poll_s: int = 10) -> list[dict]:
    h = _headers()
    resp = http.post_json(f"{BASE}/sql/execute", {"sql": sql, "performance": "medium"}, headers=h, timeout=60)
    exec_id = (resp or {}).get("execution_id")
    if not exec_id:
        raise DuneError(f"no execution id: {resp}")
    deadline = time.monotonic() + timeout_s
    while True:
        st = http.get_json(f"{BASE}/execution/{exec_id}/status", headers=h) or {}
        state = st.get("state", "")
        if state == "QUERY_STATE_COMPLETED":
            break
        if state in ("QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED", "QUERY_STATE_EXPIRED"):
            raise DuneError(f"query {state}: {st.get('error')}")
        if time.monotonic() > deadline:
            raise DuneError("query timed out")
        time.sleep(poll_s)
    rows, offset = [], 0
    while True:
        res = http.get_json(f"{BASE}/execution/{exec_id}/results",
                            params={"limit": 1000, "offset": offset}, headers=h) or {}
        batch = (res.get("result") or {}).get("rows") or []
        rows += batch
        nxt = res.get("next_offset")
        if not nxt or not batch:
            return rows
        offset = nxt
