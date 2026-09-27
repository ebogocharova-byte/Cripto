from datetime import datetime, timezone

import pytest

from tests.helpers import trade_payload


def test_create_trade_eth_ok(client, seed_instruments):
    resp = client.post("/trades", json=trade_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"
    assert data["mode"] == "swing"
    assert data["symbol"] == "ETHUSDT"


def test_create_trade_btc_rejected_422(client, seed_instruments):
    resp = client.post("/trades", json=trade_payload(symbol="BTCUSDT"))
    assert resp.status_code == 422
    assert "excluded from active trading" in resp.json()["detail"]


def test_create_trade_unknown_symbol_404(client, seed_instruments):
    resp = client.post("/trades", json=trade_payload(symbol="DOGEUSDT"))
    assert resp.status_code == 404


def test_list_trades_filters(client, seed_instruments):
    client.post("/trades", json=trade_payload(symbol="ETHUSDT"))
    client.post("/trades", json=trade_payload(symbol="SOLUSDT"))

    resp = client.get("/trades", params={"instrument": "ETHUSDT"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["instrument_id"] == 2


def test_circuit_breaker_max_concurrent_positions(client, seed_instruments):
    client.put("/config/risk", json={"max_concurrent_positions": 1})

    r1 = client.post("/trades", json=trade_payload(symbol="ETHUSDT"))
    assert r1.status_code == 201

    r2 = client.post("/trades", json=trade_payload(symbol="SOLUSDT"))
    assert r2.status_code == 409


def test_circuit_breaker_daily_drawdown(client, seed_instruments, db_session):
    from app.models.equity_snapshot import EquitySnapshot

    now = datetime.now(timezone.utc)
    db_session.add(EquitySnapshot(mode="combined", equity_value=10000, snapshot_time=now))
    db_session.add(EquitySnapshot(mode="combined", equity_value=9400, snapshot_time=now))
    db_session.commit()

    resp = client.post("/trades", json=trade_payload())
    assert resp.status_code == 409
    assert "Daily drawdown" in resp.json()["detail"]


def test_close_trade_computes_pnl_r_multiple_and_equity(client, seed_instruments):
    create_resp = client.post("/trades", json=trade_payload(entry_price=3000, risk_amount=100))
    trade_id = create_resp.json()["id"]

    close_resp = client.patch(
        f"/trades/{trade_id}",
        json={
            "status": "closed",
            "exit_price": 3150,
            "exit_time": datetime.now(timezone.utc).isoformat(),
            "commission_paid": 1.2,
        },
    )
    assert close_resp.status_code == 200
    data = close_resp.json()
    expected_pnl = (3150 - 3000) * 1.0 - 1.2
    assert data["realized_pnl"] == pytest.approx(expected_pnl)
    assert data["r_multiple"] == pytest.approx(expected_pnl / 100)

    curve = client.get("/metrics/equity-curve", params={"mode": "combined"}).json()
    assert len(curve["points"]) == 1
    assert curve["points"][0]["equity_value"] == pytest.approx(10000 + expected_pnl)


def test_close_short_trade_pnl_sign(client, seed_instruments):
    create_resp = client.post(
        "/trades", json=trade_payload(direction="short", entry_price=3000, stop_loss=3100, risk_amount=100)
    )
    trade_id = create_resp.json()["id"]

    close_resp = client.patch(
        f"/trades/{trade_id}",
        json={
            "status": "closed",
            "exit_price": 2800,
            "exit_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    data = close_resp.json()
    assert data["realized_pnl"] == pytest.approx((3000 - 2800) * 1.0)


def test_close_trade_missing_exit_fields_422(client, seed_instruments):
    create_resp = client.post("/trades", json=trade_payload())
    trade_id = create_resp.json()["id"]

    resp = client.patch(f"/trades/{trade_id}", json={"status": "closed"})
    assert resp.status_code == 422


def test_scalp_stops_after_three_consecutive_losses(client, seed_instruments):
    for _ in range(3):
        create_resp = client.post("/trades", json=trade_payload(mode="scalp"))
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]

        close_resp = client.patch(
            f"/trades/{trade_id}",
            json={
                "status": "closed",
                "exit_price": 2900,
                "exit_time": datetime.now(timezone.utc).isoformat(),
            },
        )
        assert close_resp.status_code == 200

    blocked = client.post("/trades", json=trade_payload(mode="scalp"))
    assert blocked.status_code == 409
    assert "consecutive losses" in blocked.json()["detail"]


def test_trade_not_found_404(client):
    resp = client.patch("/trades/999", json={"status": "closed"})
    assert resp.status_code == 404
