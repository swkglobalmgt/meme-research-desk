"""Polite HTTP client: per-host rate limiting, retries with backoff."""
from __future__ import annotations

import time
from urllib.parse import urlparse

import requests

_last_call: dict[str, float] = {}
_min_interval: dict[str, float] = {}
_session = requests.Session()
_session.headers["User-Agent"] = "meme-research-desk/0.1 (paper-trading research)"


def set_rate(host: str, min_interval_s: float) -> None:
    _min_interval[host] = min_interval_s


class FetchError(RuntimeError):
    pass


def _wait(host: str) -> None:
    gap = _min_interval.get(host, 0.3)
    elapsed = time.monotonic() - _last_call.get(host, 0.0)
    if elapsed < gap:
        time.sleep(gap - elapsed)
    _last_call[host] = time.monotonic()


def get_json(url: str, params: dict | None = None, retries: int = 3, timeout: float = 20.0,
             headers: dict | None = None):
    host = urlparse(url).netloc
    last_err = None
    for attempt in range(retries):
        _wait(host)
        try:
            r = _session.get(url, params=params, timeout=timeout, headers=headers)
            if r.status_code == 429:
                time.sleep(10 * (attempt + 1))
                last_err = FetchError(f"429 rate limited: {url}")
                continue
            if r.status_code == 404:
                return None
            if r.status_code >= 500:
                last_err = FetchError(f"{r.status_code} from {url}")
                time.sleep(2 * (attempt + 1))
                continue
            if r.status_code >= 400:
                raise FetchError(f"{r.status_code} from {url}: {r.text[:200]}")
            return r.json()
        except (requests.ConnectionError, requests.Timeout) as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise FetchError(str(last_err))


def post_json(url: str, payload: dict, retries: int = 3, timeout: float = 20.0,
              headers: dict | None = None):
    host = urlparse(url).netloc
    last_err = None
    for attempt in range(retries):
        _wait(host)
        try:
            r = _session.post(url, json=payload, timeout=timeout, headers=headers)
            if r.status_code == 429 or r.status_code >= 500:
                last_err = FetchError(f"{r.status_code} from {url}")
                time.sleep(3 * (attempt + 1))
                continue
            if r.status_code >= 400:
                raise FetchError(f"{r.status_code} from {url}: {r.text[:200]}")
            return r.json()
        except (requests.ConnectionError, requests.Timeout) as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise FetchError(str(last_err))
