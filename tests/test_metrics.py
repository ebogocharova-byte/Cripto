from datetime import datetime, timezone

import pytest

from tests.helpers import trade_payload


def test_metrics_summary_no_trades(client, seed_instruments):
    resp = client.get("/metrics/summary", params={"mode": "swing"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_trades"] == 0
    assert data["winrate"] == 0
    assert data["profit_factor"] is None
    assert data["avg_r_multiple"] is None


def _open_and_close(client, exit_price, entry_price=3000.0, risk_amount=100.0):
    create_resp = client.post(
        "/trades", json=trade_payload(entry_price=entry_price, risk_amount=risk_amount)
    )
    trade_id = create_resp.json()["id"]
    client.patch(
        f"/trades/{trade_id}",
        json={
            "status": "closed",
            "exit_price": exit_price,
            "exit_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    return trade_id


def test_metrics_summary_after_win_and_loss(client, seed_instruments):
    _open_and_close(client, exit_price=3200.0)  # +200 win
    _open_and_close(client, exit_price=2900.0)  # -100 loss

    resp = client.get("/metrics/summary", params={"mode": "swing", "instrument": "ETHUSDT"})
    data = resp.json()
    assert data["total_trades"] == 2
    assert data["wins"] == 1
    assert data["losses"] == 1
    assert data["winrate"] == 0.5
    assert data["profit_factor"] == pytest.approx(200 / 100)
    assert data["total_pnl"] == pytest.approx(100)


def test_equity_curve_tracks_each_close(client, seed_instruments):
    _open_and_close(client, exit_price=3200.0)
    _open_and_close(client, exit_price=2900.0)

    resp = client.get("/metrics/equity-curve", params={"mode": "combined"})
    points = resp.json()["points"]
    assert len(points) == 2
    assert points[0]["equity_value"] == pytest.approx(10200)
    assert points[1]["equity_value"] == pytest.approx(10100)
