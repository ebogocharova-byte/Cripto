def test_get_risk_config_creates_default(client):
    resp = client.get("/config/risk")
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_pct_per_trade"] == 0.01
    assert data["max_concurrent_positions"] == 3
    assert data["daily_drawdown_limit_pct"] == 0.05
    assert data["weekly_drawdown_limit_pct"] == 0.10
    assert data["base_equity"] == 10000.0


def test_update_risk_config(client):
    resp = client.put(
        "/config/risk", json={"risk_pct_per_trade": 0.008, "max_concurrent_positions": 2}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_pct_per_trade"] == 0.008
    assert data["max_concurrent_positions"] == 2


def test_strategy_profiles_list_filters_by_symbol(client, seed_instruments):
    resp = client.get("/config/strategy-profiles", params={"symbol": "ETHUSDT", "mode": "swing"})
    assert resp.status_code == 200
    profiles = resp.json()
    assert len(profiles) == 1
    assert profiles[0]["risk_mult"] == 1.0
    assert profiles[0]["ema_fast"] == 50
    assert profiles[0]["ema_slow"] == 200
    assert profiles[0]["signal_threshold"] == 0.35


def test_strategy_profiles_sol_half_risk(client, seed_instruments):
    resp = client.get("/config/strategy-profiles", params={"symbol": "SOLUSDT", "mode": "swing"})
    assert resp.json()[0]["risk_mult"] == 0.5


def test_strategy_profile_update(client, seed_instruments):
    profile_id = client.get(
        "/config/strategy-profiles", params={"symbol": "ETHUSDT", "mode": "swing"}
    ).json()[0]["id"]

    resp = client.put(f"/config/strategy-profiles/{profile_id}", json={"signal_threshold": 0.4})
    assert resp.status_code == 200
    assert resp.json()["signal_threshold"] == 0.4


def test_strategy_profile_update_missing_404(client):
    resp = client.put("/config/strategy-profiles/999", json={"signal_threshold": 0.4})
    assert resp.status_code == 404
