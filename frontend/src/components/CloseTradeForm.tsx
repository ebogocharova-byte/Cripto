import { useState } from 'react';
import { api } from '../api/client';
import type { Trade } from '../types';
import { buttonStyle, fieldStyle, labelStyle, rowStyle } from './formStyles';

function nowLocal(): string {
  const d = new Date();
  d.setSeconds(0, 0);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export function CloseTradeForm({
  trade,
  onClosed,
  onCancel,
}: {
  trade: Trade;
  onClosed: (trade: Trade) => void;
  onCancel: () => void;
}) {
  const [exitPrice, setExitPrice] = useState('');
  const [exitTime, setExitTime] = useState(nowLocal());
  const [exitReason, setExitReason] = useState('manual_close');
  const [commission, setCommission] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const updated = await api.closeTrade(trade.id, {
        status: 'closed',
        exit_price: Number(exitPrice),
        exit_time: new Date(exitTime).toISOString(),
        exit_reason: exitReason,
        ...(commission ? { commission_paid: Number(commission) } : {}),
      });
      onClosed(updated);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
        Closing {trade.symbol} {trade.direction} @ {trade.entry_price}
      </p>

      <div style={rowStyle}>
        <label style={labelStyle}>Exit price</label>
        <input style={fieldStyle} type="number" step="any" required value={exitPrice} onChange={(e) => setExitPrice(e.target.value)} />
      </div>

      <div style={rowStyle}>
        <label style={labelStyle}>Exit time</label>
        <input style={fieldStyle} type="datetime-local" required value={exitTime} onChange={(e) => setExitTime(e.target.value)} />
      </div>

      <div style={rowStyle}>
        <label style={labelStyle}>Exit reason</label>
        <select style={fieldStyle} value={exitReason} onChange={(e) => setExitReason(e.target.value)}>
          <option value="tp_hit">tp_hit</option>
          <option value="sl_hit">sl_hit</option>
          <option value="manual_close">manual_close</option>
          <option value="other">other</option>
        </select>
      </div>

      <div style={rowStyle}>
        <label style={labelStyle}>Commission (optional)</label>
        <input style={fieldStyle} type="number" step="any" value={commission} onChange={(e) => setCommission(e.target.value)} />
      </div>

      {error && <div style={{ color: 'var(--critical)', fontSize: 13, marginBottom: 10 }}>{error}</div>}

      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" onClick={onCancel} style={{ ...buttonStyle, background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
          Cancel
        </button>
        <button type="submit" disabled={submitting} style={buttonStyle}>
          {submitting ? 'Closing…' : 'Close trade'}
        </button>
      </div>
    </form>
  );
}
