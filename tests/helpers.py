from datetime import datetime, timezone


def trade_payload(symbol: str = "ETHUSDT", mode: str = "swing", **overrides) -> dict:
    payload = {
        "symbol": symbol,
        "mode": mode,
        "direction": "long",
        "entry_price": 3000.0,
        "entry_time": datetime.now(timezone.utc).isoformat(),
        "stop_loss": 2900.0,
        "take_profit": 3300.0,
        "position_size": 1.0,
        "risk_amount": 100.0,
    }
    payload.update(overrides)
    return payload
