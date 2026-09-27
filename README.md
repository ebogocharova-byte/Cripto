# Cripto — Swing/Scalp Trading Backend (BTC/ETH/SOL)

FastAPI + PostgreSQL backend for a walk-forward-validated swing/scalp trading
system on Binance. Signal computation (TA + candlestick patterns + Elliott
wave heuristic) lives entirely in this backend; n8n is a pure 4h cron trigger
that calls `POST /signals/compute` and relays the returned Telegram text.

## Validated defaults baked into the seed migration

- **ETH** (`ETHUSDT`): full risk (`risk_mult=1.0`), momentum strategy, PF 2.87 out-of-sample.
- **SOL** (`SOLUSDT`): half risk (`risk_mult=0.5`), weaker/unstable signal.
- **BTC** (`BTCUSDT`): monitor-only. `POST /trades` and `POST /risk/position-size`
  return `422` for BTC ("excluded from active trading per backtest validation").
  Signals are still accepted and stored via the webhook/compute endpoints.

Strategy formula (same for all symbols, risk scaled by `risk_mult`):
`ema 50/200 (4h)`, `rsi 14`, `macd 12/26/9`, `atr 14`, `sl=1.5×ATR`,
`tp=3.0×ATR`, weights `TA .60 / candles .30 / elliott .10`, `threshold .35`,
`commission 0.04%` taker/side.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
cp .env.example .env   # adjust DATABASE_URL if needed
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

## Run with Docker

```bash
docker compose up --build
```

## Tests

Tests run against a real Postgres database (`trading_test`); no sqlite/mocked DB.

```bash
createdb trading_test  # once
DATABASE_URL=postgresql+psycopg2://trading:trading@localhost:5432/trading_test \
    .venv/bin/pytest
```

## Project layout

```
app/
  core/       settings, exceptions
  db/         SQLAlchemy engine/session, declarative base
  models/     ORM models (instruments, risk_config, strategy_profiles,
              signals, elliott_labels, trades, scalp_sessions, equity_snapshots)
  schemas/    Pydantic request/response schemas
  services/   binance_client, ta_indicators, candle_patterns, elliott,
              scoring, signal_engine, risk_service, metrics_service
  middleware/ circuit_breaker dependency (blocks POST /trades on BTC / risk breach)
  api/v1/     endpoint routers
alembic/      migrations (schema + seed data for BTC/ETH/SOL + risk_config)
tests/        pytest suite (config, signals, trades, metrics, risk, circuit breaker)
```

## Known gap

The Elliott wave scoring (`app/services/elliott.py`) is a from-scratch zigzag
heuristic reconstruction — the original n8n JS reference implementation
wasn't available to port 1:1. Its weight in the final score is only 0.10 by
design, so this is a low-impact approximation; swap it out if you can supply
the original logic.
