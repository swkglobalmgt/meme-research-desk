from desk import strategies
from desk.config import STRATEGIES
from desk.sources.geckoterminal import parse_pool


def snap(**kw):
    base = {"pool_address": "P", "token_mint": "M", "liquidity_usd": 80_000, "vol_m5": 5_000,
            "vol_h1": 60_000, "vol_h24": 500_000, "chg_m5": 1.0, "chg_h1": 25.0, "chg_h6": 10.0,
            "chg_h24": 40.0, "buys_h1": 300, "sells_h1": 200, "txns_h24": 3000}
    base.update(kw)
    return base


def test_momentum():
    p = STRATEGIES["momentum"].params
    assert strategies.momentum(snap(), p)
    assert not strategies.momentum(snap(chg_h1=10), p)
    assert not strategies.momentum(snap(chg_m5=-1), p)
    assert not strategies.momentum(snap(buys_h1=100, sells_h1=200), p)
    assert not strategies.momentum(snap(chg_h1=None), p)


def test_volume_breakout():
    p = STRATEGIES["volume_breakout"].params
    assert strategies.volume_breakout(snap(vol_h1=60_000, vol_m5=15_000, chg_m5=4), p)
    assert not strategies.volume_breakout(snap(vol_h1=60_000, vol_m5=10_000, chg_m5=4), p)
    assert not strategies.volume_breakout(snap(vol_h1=60_000, vol_m5=15_000, chg_m5=1), p)


def test_pullback():
    p = STRATEGIES["pullback"].params
    assert strategies.pullback(snap(chg_h6=80, chg_h1=-15, chg_m5=1), p)
    assert not strategies.pullback(snap(chg_h6=80, chg_h1=-30, chg_m5=1), p)
    assert not strategies.pullback(snap(chg_h6=30, chg_h1=-15, chg_m5=1), p)


def test_founder_screen_ranks_and_filters():
    p = STRATEGIES["founder_screen"].params
    snaps = [snap(pool_address=str(i), chg_h24=float(i)) for i in range(1, 9)]
    snaps.append(snap(pool_address="thin", chg_h24=999, liquidity_usd=10_000))
    snaps.append(snap(pool_address="quiet", chg_h24=998, txns_h24=10))
    got = [s["pool_address"] for s in strategies.founder_screen(snaps, p)]
    assert got == ["8", "7", "6", "5", "4"]


def test_select_dispatch():
    out = strategies.select(STRATEGIES["momentum"], [snap(), snap(chg_h1=0)])
    assert len(out) == 1


def test_parse_geckoterminal_pool():
    obj = {"id": "solana_POOL", "attributes": {
        "address": "POOL", "name": "DOGE2 / SOL", "pool_created_at": "2026-11-02T10:00:00Z",
        "base_token_price_usd": "0.00123", "reserve_in_usd": "65432.1", "fdv_usd": "1000000",
        "volume_usd": {"m5": "100", "h1": "2000", "h6": "9000", "h24": "50000"},
        "price_change_percentage": {"m5": "1.5", "h1": "-3", "h6": "20", "h24": "120"},
        "transactions": {"h1": {"buys": 50, "sells": 40, "buyers": 30, "sellers": 25},
                         "h24": {"buys": 900, "sells": 700}}},
        "relationships": {"base_token": {"data": {"id": "solana_MINT123"}},
                          "dex": {"data": {"id": "pumpswap"}}}}
    p = parse_pool(obj)
    assert p["token_mint"] == "MINT123" and p["symbol"] == "DOGE2" and p["dex"] == "pumpswap"
    assert p["liquidity_usd"] == 65432.1 and p["chg_h1"] == -3.0 and p["txns_h24"] == 1600
    assert parse_pool({"attributes": {}}) is None
