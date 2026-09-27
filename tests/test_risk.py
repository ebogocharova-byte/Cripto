import pytest


def test_position_size_eth_full_risk(client, seed_instruments):
    resp = client.post(
        "/risk/position-size",
        json={
            "symbol": "ETHUSDT",
            "mode": "swing",
            "entry_price": 3000,
            "stop_loss_price": 2900,
            "equity": 10000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    # risk_amount = 10000 * 0.01 * 1.0 = 100; sl_distance = 100 -> position_size = 1.0
    assert data["risk_amount"] == pytest.approx(100.0)
    assert data["position_size"] == pytest.approx(1.0)
    assert data["risk_mult_used"] == pytest.approx(1.0)


def test_position_size_sol_half_risk(client, seed_instruments):
    resp = client.post(
        "/risk/position-size",
        json={
            "symbol": "SOLUSDT",
            "mode": "swing",
            "entry_price": 150,
            "stop_loss_price": 145,
            "equity": 10000,
        },
    )
    data = resp.json()
    # risk_amount = 10000 * 0.01 * 0.5 = 50; sl_distance = 5 -> position_size = 10
    assert data["risk_amount"] == pytest.approx(50.0)
    assert data["position_size"] == pytest.approx(10.0)
    assert data["risk_mult_used"] == pytest.approx(0.5)


def test_position_size_btc_rejected_422(client, seed_instruments):
    resp = client.post(
        "/risk/position-size",
        json={
            "symbol": "BTCUSDT",
            "mode": "swing",
            "entry_price": 60000,
            "stop_loss_price": 59000,
            "equity": 10000,
        },
    )
    assert resp.status_code == 422
    assert "excluded from active trading" in resp.json()["detail"]


def test_position_size_invalid_stop_loss(client, seed_instruments):
    resp = client.post(
        "/risk/position-size",
        json={
            "symbol": "ETHUSDT",
            "mode": "swing",
            "entry_price": 3000,
            "stop_loss_price": 3000,
            "equity": 10000,
        },
    )
    assert resp.status_code == 422
