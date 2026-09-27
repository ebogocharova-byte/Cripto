from datetime import datetime, timezone

from app.services.signal_engine import ComputedSignal


def _fake_computed_signal() -> ComputedSignal:
    return ComputedSignal(
        direction="long",
        score_total=0.42,
        score_ta=0.3,
        score_candles=0.6,
        score_elliott=0.3,
        threshold_used=0.35,
        price_at_signal=3050.0,
        atr_value=45.0,
        sl_price=2982.5,
        tp_price=3185.0,
        candle_open_time=datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc),
        elliott_labels=[(10, 3000.0, "3", "up")],
    )


def test_compute_signal_endpoint(client, seed_instruments, monkeypatch):
    import app.api.v1.endpoints.signals as signals_module

    monkeypatch.setattr(
        signals_module, "compute_signal", lambda profile, symbol: _fake_computed_signal()
    )

    resp = client.post("/signals/compute", json={"symbol": "ETHUSDT", "mode": "swing"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["signal"]["direction"] == "long"
    assert data["signal"]["source"] == "backend_compute"
    assert "LONG" in data["telegram_text"]


def test_compute_signal_idempotent_on_same_candle(client, seed_instruments, monkeypatch):
    import app.api.v1.endpoints.signals as signals_module

    monkeypatch.setattr(
        signals_module, "compute_signal", lambda profile, symbol: _fake_computed_signal()
    )

    first = client.post("/signals/compute", json={"symbol": "ETHUSDT", "mode": "swing"})
    second = client.post("/signals/compute", json={"symbol": "ETHUSDT", "mode": "swing"})
    assert first.json()["signal"]["id"] == second.json()["signal"]["id"]

    listed = client.get("/signals", params={"instrument": "ETHUSDT", "mode": "swing"}).json()
    assert len(listed) == 1


def test_compute_signal_unknown_symbol_404(client, seed_instruments):
    resp = client.post("/signals/compute", json={"symbol": "DOGEUSDT", "mode": "swing"})
    assert resp.status_code == 404


def test_webhook_ingest_signal(client, seed_instruments):
    payload = {
        "symbol": "ETHUSDT",
        "mode": "swing",
        "timeframe": "4h",
        "candle_open_time": "2026-09-27T12:00:00Z",
        "direction": "short",
        "score_total": -0.4,
        "score_ta": -0.3,
        "score_candles": -0.5,
        "score_elliott": -0.2,
        "threshold_used": 0.35,
        "price_at_signal": 2990.0,
        "atr_value": 40.0,
        "sl_price": 3050.0,
        "tp_price": 2870.0,
    }
    resp = client.post("/webhooks/n8n/signal", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "n8n_webhook"
    assert data["direction"] == "short"


def test_webhook_ingest_btc_monitor_only_allowed(client, seed_instruments):
    payload = {
        "symbol": "BTCUSDT",
        "mode": "swing",
        "candle_open_time": "2026-09-27T08:00:00Z",
        "direction": "neutral",
        "score_total": 0.1,
        "score_ta": 0.1,
        "score_candles": 0.0,
        "score_elliott": 0.0,
        "threshold_used": 0.35,
        "price_at_signal": 60000.0,
        "atr_value": 500.0,
    }
    first = client.post("/webhooks/n8n/signal", json=payload)
    assert first.status_code == 200
    second = client.post("/webhooks/n8n/signal", json=payload)
    assert first.json()["id"] == second.json()["id"]


def test_list_signals_filters_by_mode_and_instrument(client, seed_instruments):
    client.post(
        "/webhooks/n8n/signal",
        json={
            "symbol": "ETHUSDT",
            "mode": "swing",
            "candle_open_time": "2026-09-27T12:00:00Z",
            "direction": "long",
            "score_total": 0.5,
            "score_ta": 0.4,
            "score_candles": 0.1,
            "score_elliott": 0.0,
            "threshold_used": 0.35,
            "price_at_signal": 3000.0,
            "atr_value": 40.0,
        },
    )
    resp = client.get("/signals", params={"mode": "swing", "instrument": "ETHUSDT"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
