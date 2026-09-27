import type { Signal } from '../types';
import { DirectionBadge } from './DirectionBadge';

export function SignalsFeed({ signals }: { signals: Signal[] }) {
  if (signals.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>No signals yet.</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {signals.map((s) => (
        <div
          key={s.id}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--surface-1)',
            border: '1px solid var(--border)',
            borderRadius: 8,
            padding: '10px 14px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <strong>{s.symbol}</strong>
            <DirectionBadge direction={s.direction} />
            <span style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
              score {s.score_total.toFixed(2)} / {s.threshold_used.toFixed(2)}
            </span>
          </div>
          <div style={{ textAlign: 'right', fontSize: 13, color: 'var(--text-secondary)' }}>
            <div style={{ fontVariantNumeric: 'tabular-nums' }}>
              px {s.price_at_signal.toFixed(2)}
              {s.sl_price && s.tp_price ? ` · SL ${s.sl_price.toFixed(2)} · TP ${s.tp_price.toFixed(2)}` : ''}
            </div>
            <div style={{ color: 'var(--text-muted)' }}>
              {new Date(s.candle_open_time).toLocaleString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
