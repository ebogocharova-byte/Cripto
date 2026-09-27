import { useState } from 'react';
import { api } from '../api/client';
import type { Instrument, Mode, Trade, TradeCreate } from '../types';
import { buttonStyle, fieldStyle, labelStyle, rowStyle } from './formStyles';

function nowLocal(): string {
  const d = new Date();
  d.setSeconds(0, 0);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export function CreateTradeForm({
  instruments,
  onCreated,
  onCancel,
}: {
  instruments: Instrument[];
  onCreated: (trade: Trade) => void;
  onCancel: () => void;
}) {
  const tradable = instruments.filter((i) => i.is_active_trading);
  const [symbolOverride, setSymbolOverride] = useState<string | null>(null);
  const symbol = symbolOverride ?? tradable[0]?.symbol ?? '';
  const setSymbol = setSymbolOverride;
  const [mode, setMode] = useState<Mode>('swing');
  const [direction, setDirection] = useState<'long' | 'short'>('long');
  const [entryPrice, setEntryPrice] = useState('');
  const [entryTime, setEntryTime] = useState(nowLocal());
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [positionSize, setPositionSize] = useState('');
  const [riskAmount, setRiskAmount] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const payload: TradeCreate = {
      symbol,
      mode,
      direction,
      entry_price: Number(entryPrice),
      entry_time: new Date(entryTime).toISOString(),
      stop_loss: Number(stopLoss),
      take_profit: Number(takeProfit),
      position_size: Number(positionSize),
      risk_amount: Number(riskAmount),
    };
    try {
      const trade = await api.createTrade(payload);
      onCreated(trade);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div style={rowStyle}>
        <label style={labelStyle}>Symbol</label>
        <select style={fieldStyle} value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          {tradable.map((i) => (
            <option key={i.id} value={i.symbol}>
              {i.symbol}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Mode</label>
          <select style={fieldStyle} value={mode} onChange={(e) => setMode(e.target.value as Mode)}>
            <option value="swing">swing</option>
            <option value="scalp">scalp</option>
          </select>
        </div>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Direction</label>
          <select style={fieldStyle} value={direction} onChange={(e) => setDirection(e.target.value as 'long' | 'short')}>
            <option value="long">long</option>
            <option value="short">short</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Entry price</label>
          <input style={fieldStyle} type="number" step="any" required value={entryPrice} onChange={(e) => setEntryPrice(e.target.value)} />
        </div>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Entry time</label>
          <input style={fieldStyle} type="datetime-local" required value={entryTime} onChange={(e) => setEntryTime(e.target.value)} />
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Stop loss</label>
          <input style={fieldStyle} type="number" step="any" required value={stopLoss} onChange={(e) => setStopLoss(e.target.value)} />
        </div>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Take profit</label>
          <input style={fieldStyle} type="number" step="any" required value={takeProfit} onChange={(e) => setTakeProfit(e.target.value)} />
        </div>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Position size</label>
          <input style={fieldStyle} type="number" step="any" required value={positionSize} onChange={(e) => setPositionSize(e.target.value)} />
        </div>
        <div style={{ ...rowStyle, flex: 1 }}>
          <label style={labelStyle}>Risk amount ($)</label>
          <input style={fieldStyle} type="number" step="any" required value={riskAmount} onChange={(e) => setRiskAmount(e.target.value)} />
        </div>
      </div>

      {error && <div style={{ color: 'var(--critical)', fontSize: 13, marginBottom: 10 }}>{error}</div>}

      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" onClick={onCancel} style={{ ...buttonStyle, background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
          Cancel
        </button>
        <button type="submit" disabled={submitting || !symbol} style={buttonStyle}>
          {submitting ? 'Creating…' : 'Create trade'}
        </button>
      </div>
    </form>
  );
}
