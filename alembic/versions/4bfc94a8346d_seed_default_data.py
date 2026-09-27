"""seed default data

Revision ID: 4bfc94a8346d
Revises: 8bc5f29a38ca
Create Date: 2026-09-27 14:10:41.879441

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text as sa_text

# revision identifiers, used by Alembic.
revision: str = '4bfc94a8346d'
down_revision: Union[str, None] = '8bc5f29a38ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INSTRUMENTS = [
    ("BTCUSDT", "BTC", "USDT", False),
    ("ETHUSDT", "ETH", "USDT", True),
    ("SOLUSDT", "SOL", "USDT", True),
]

# (symbol, risk_mult) — walk-forward validated: ETH full risk, SOL half risk,
# BTC monitored only (risk_mult irrelevant since is_active_trading=False blocks trades)
STRATEGY_RISK_MULT = {
    "BTCUSDT": 0.0,
    "ETHUSDT": 1.0,
    "SOLUSDT": 0.5,
}


def upgrade() -> None:
    conn = op.get_bind()

    for symbol, base_asset, quote_asset, is_active in INSTRUMENTS:
        conn.execute(
            sa_text(
                "INSERT INTO instruments (symbol, base_asset, quote_asset, is_active_trading) "
                "VALUES (:symbol, :base_asset, :quote_asset, :is_active) "
                "ON CONFLICT (symbol) DO NOTHING"
            ),
            {
                "symbol": symbol,
                "base_asset": base_asset,
                "quote_asset": quote_asset,
                "is_active": is_active,
            },
        )

    conn.execute(
        sa_text(
            "INSERT INTO risk_config "
            "(risk_pct_per_trade, max_concurrent_positions, daily_drawdown_limit_pct, "
            " weekly_drawdown_limit_pct, scalp_max_consecutive_losses) "
            "SELECT 0.01, 3, 0.05, 0.10, 3 "
            "WHERE NOT EXISTS (SELECT 1 FROM risk_config)"
        )
    )

    for symbol, risk_mult in STRATEGY_RISK_MULT.items():
        conn.execute(
            sa_text(
                "INSERT INTO strategy_profiles "
                "(instrument_id, mode, ema_fast, ema_slow, rsi_period, macd_fast, macd_slow, "
                " macd_signal, atr_period, sl_atr_mult, tp_atr_mult, weight_ta, weight_candles, "
                " weight_elliott, signal_threshold, commission_pct, risk_mult, is_active) "
                "SELECT id, 'swing', 50, 200, 14, 12, 26, 9, 14, 1.5, 3.0, 0.60, 0.30, 0.10, "
                "       0.35, 0.0004, :risk_mult, true "
                "FROM instruments WHERE symbol = :symbol "
                "ON CONFLICT (instrument_id, mode) DO NOTHING"
            ),
            {"symbol": symbol, "risk_mult": risk_mult},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa_text("DELETE FROM strategy_profiles"))
    conn.execute(sa_text("DELETE FROM risk_config"))
    conn.execute(
        sa_text("DELETE FROM instruments WHERE symbol IN ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')")
    )
