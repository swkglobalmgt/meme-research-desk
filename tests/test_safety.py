from desk import safety


def good_facts(**over):
    f = {
        "mint_known": True, "mint_error": None, "mint_authority": None, "freeze_authority": None,
        "transfer_fee_bps": 0, "risky_extensions": [], "rugcheck_error": None,
        "lp_locked_pct": 100.0, "top10_pct": 18.0, "rugged_flag": False,
        "liquidity_usd": 80_000, "age_hours": 3.0, "sells_h1": 150, "sellers_h1": 90,
        "sell_quote_error": None, "sell_quote_found": True, "sell_loss_pct": 3.2,
    }
    f.update(over)
    return f


def test_all_good_passes():
    r = safety.evaluate(good_facts())
    assert r.passed and r.reasons == []
    assert all(r.checks.values())


def fails(check, **over):
    r = safety.evaluate(good_facts(**over))
    assert not r.passed
    assert r.checks[check] is False
    return r


def test_mint_authority_not_revoked():
    fails("mint_authority_revoked", mint_authority="SomeWallet111")


def test_freeze_authority_not_revoked():
    fails("freeze_authority_revoked", freeze_authority="SomeWallet111")


def test_unreadable_mint_fails_both_authorities():
    r = fails("mint_authority_revoked", mint_known=False, mint_error="rpc 429")
    assert r.checks["freeze_authority_revoked"] is False
    assert "rpc 429" in r.reasons[0]


def test_lp_not_locked():
    fails("lp_locked", lp_locked_pct=40.0)


def test_lp_unknown_fails_closed():
    fails("lp_locked", lp_locked_pct=None, rugcheck_error="timeout")


def test_lp_boundary():
    assert safety.evaluate(good_facts(lp_locked_pct=90.0)).checks["lp_locked"]
    assert not safety.evaluate(good_facts(lp_locked_pct=89.9)).checks["lp_locked"]


def test_top10_too_concentrated_and_boundary():
    fails("top10_holders", top10_pct=30.0)   # rule is strictly below 30%
    assert safety.evaluate(good_facts(top10_pct=29.99)).checks["top10_holders"]


def test_top10_unknown_fails():
    fails("top10_holders", top10_pct=None)


def test_low_liquidity():
    fails("min_liquidity", liquidity_usd=49_999)
    fails("min_liquidity", liquidity_usd=None)
    assert safety.evaluate(good_facts(liquidity_usd=50_000)).checks["min_liquidity"]


def test_too_young():
    fails("min_age", age_hours=0.99)
    fails("min_age", age_hours=None)


def test_sell_tax_and_extensions():
    fails("no_sell_tax", transfer_fee_bps=100)
    fails("no_sell_tax", risky_extensions=["permanentDelegate"])
    fails("no_sell_tax", transfer_fee_bps=None)


def test_too_few_sells():
    fails("sells_observed", sells_h1=19)
    fails("sells_observed", sellers_h1=9)
    fails("sells_observed", sells_h1=None)


def test_sell_route():
    fails("sell_route", sell_quote_found=False, sell_loss_pct=None)
    fails("sell_route", sell_quote_error="jupiter 500")
    fails("sell_route", sell_loss_pct=10.5)
    assert safety.evaluate(good_facts(sell_loss_pct=10.0)).checks["sell_route"]


def test_rugged_flag():
    fails("not_rugged", rugged_flag=True)


def test_multiple_failures_all_reported():
    r = safety.evaluate(good_facts(mint_authority="x", top10_pct=60, age_hours=0.2))
    assert len(r.reasons) == 3


# --- turning raw data into facts -------------------------------------------

REPORT = {
    "markets": [
        {"pubkey": "POOL_A", "liquidityA": "VAULT_A", "liquidityB": "VAULT_B",
         "lp": {"lpLockedPct": 100, "baseUSD": 40000, "quoteUSD": 40000}},
        {"pubkey": "POOL_B", "lp": {"lpLockedPct": 10, "baseUSD": 100, "quoteUSD": 100}},
    ],
    "knownAccounts": {"LOCKER_1": {"name": "Streamflow", "type": "LOCKER"}},
    "topHolders": [
        {"address": "VAULT_A", "owner": "POOL_AUTH", "pct": 40.0},       # the pool itself
        {"address": "acc1", "owner": "1nc1nerator11111111111111111111111111111111", "pct": 10.0},  # burned
        {"address": "LOCKER_1", "owner": "x", "pct": 8.0},                 # locker
        *[{"address": f"h{i}", "owner": f"o{i}", "pct": 2.0} for i in range(12)],
    ],
}


def test_top10_excludes_pool_burn_and_lockers():
    assert safety.top10_pct_from_rugcheck(REPORT) == 20.0  # ten real holders at 2% each


def test_top10_missing_is_none():
    assert safety.top10_pct_from_rugcheck(None) is None
    assert safety.top10_pct_from_rugcheck({"markets": []}) is None


def test_lp_uses_our_pool_then_deepest():
    assert safety.lp_locked_pct_from_rugcheck(REPORT, "POOL_B") == 10.0
    assert safety.lp_locked_pct_from_rugcheck(REPORT, "UNKNOWN") == 100.0
    assert safety.lp_locked_pct_from_rugcheck({"markets": []}, "x") is None


def test_transfer_fee_and_extensions_from_mint():
    plain = {"extensions": {}}
    assert safety.transfer_fee_bps(plain) == 0
    taxed = {"extensions": {"transferFeeConfig": {
        "newerTransferFee": {"transferFeeBasisPoints": 300}, "olderTransferFee": {"transferFeeBasisPoints": 0}}}}
    assert safety.transfer_fee_bps(taxed) == 300
    assert safety.transfer_fee_bps(None) is None
    hooked = {"extensions": {"transferHook": {"authority": None, "programId": "Hook111"}}}
    assert safety.risky_extensions(hooked) == ["transferHook"]
    harmless = {"extensions": {"transferHook": {"authority": None, "programId": None}}}
    assert safety.risky_extensions(harmless) == []


def test_build_facts_end_to_end():
    f = safety.build_facts(
        snapshot={"pool_address": "POOL_A", "liquidity_usd": 80000, "sells_h1": 40, "sellers_h1": 25},
        age_hours=2.0, mint={"mint_authority": None, "freeze_authority": None, "extensions": {}},
        mint_error=None, rugcheck=REPORT, rugcheck_error=None,
        sell_quote={"out_usd": 96.0}, sell_quote_error=None, position_usd=100.0)
    assert f["sell_loss_pct"] == 4.0
    assert safety.evaluate(f).passed
