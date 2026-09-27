def test_list_instruments(client, seed_instruments):
    resp = client.get("/instruments")
    assert resp.status_code == 200
    data = resp.json()
    symbols = {row["symbol"]: row["is_active_trading"] for row in data}
    assert symbols == {"BTCUSDT": False, "ETHUSDT": True, "SOLUSDT": True}
