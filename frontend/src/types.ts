export type Mode = 'swing' | 'scalp';
export type Direction = 'long' | 'short' | 'neutral';
export type TradeStatus = 'open' | 'closed' | 'cancelled';

export interface Instrument {
  id: number;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  is_active_trading: boolean;
}

export interface Signal {
  id: number;
  instrument_id: number;
  symbol: string;
  mode: Mode;
  timeframe: string;
  candle_open_time: string;
  direction: Direction;
  score_total: number;
  score_ta: number;
  score_candles: number;
  score_elliott: number;
  threshold_used: number;
  price_at_signal: number;
  atr_value: number;
  sl_price: number | null;
  tp_price: number | null;
  source: string;
  created_at: string;
}

export interface Trade {
  id: number;
  instrument_id: number;
  symbol: string;
  signal_id: number | null;
  mode: Mode;
  direction: 'long' | 'short';
  status: TradeStatus;
  entry_price: number;
  entry_time: string;
  exit_price: number | null;
  exit_time: string | null;
  stop_loss: number;
  take_profit: number;
  position_size: number;
  risk_amount: number;
  realized_pnl: number | null;
  r_multiple: number | null;
  commission_paid: number | null;
  exit_reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface TradeCreate {
  symbol: string;
  mode: Mode;
  direction: 'long' | 'short';
  entry_price: number;
  entry_time: string;
  stop_loss: number;
  take_profit: number;
  position_size: number;
  risk_amount: number;
  notes?: string;
}

export interface TradeClose {
  status: 'closed';
  exit_price: number;
  exit_time: string;
  commission_paid?: number;
  exit_reason?: string;
}

export interface MetricsSummary {
  mode: string;
  instrument: string | null;
  total_trades: number;
  wins: number;
  losses: number;
  winrate: number;
  profit_factor: number | null;
  avg_r_multiple: number | null;
  max_drawdown_pct: number | null;
  total_pnl: number;
}

export interface EquityCurvePoint {
  snapshot_time: string;
  equity_value: number;
  drawdown_pct: number | null;
}

export interface EquityCurveResponse {
  mode: string;
  points: EquityCurvePoint[];
}
