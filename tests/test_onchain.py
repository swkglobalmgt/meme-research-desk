import pytest

from desk.sources import http, onchain


@pytest.fixture(autouse=True)
def sol_price(monkeypatch):
    monkeypatch.setitem(onchain._sol_price, "p", 150.0)


def test_quote_valued_in_usd_via_sol(monkeypatch):
    monkeypatch.setattr(http, "get_json", lambda *a, **k: {"outAmount": str(int(0.64 * 1e9)), "routePlan": [1]})
    assert onchain.jupiter_sell_quote("MINT", 6, 1000)["out_usd"] == pytest.approx(96.0)


def test_real_no_route_is_none(monkeypatch):
    def boom(*a, **k):
        raise http.FetchError('400 from x: {"errorCode":"COULD_NOT_FIND_ANY_ROUTE"}')
    monkeypatch.setattr(http, "get_json", boom)
    assert onchain.jupiter_sell_quote("MINT", 6, 1000) is None


def test_token_itself_not_tradable_is_none(monkeypatch):
    def boom(*a, **k):
        raise http.FetchError('400 from x: {"error":"The token MINT is not tradable"}')
    monkeypatch.setattr(http, "get_json", boom)
    assert onchain.jupiter_sell_quote("MINT", 6, 1000) is None


def test_other_failures_raise_not_honeypot(monkeypatch):
    """The Nov 2026 bug: Jupiter refused USDC; that must be an error, not 'no route'."""
    def boom(*a, **k):
        raise http.FetchError('400 from x: {"error":"The token EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr is not tradable"}')
    monkeypatch.setattr(http, "get_json", boom)
    with pytest.raises(http.FetchError):
        onchain.jupiter_sell_quote("MINT", 6, 1000)
