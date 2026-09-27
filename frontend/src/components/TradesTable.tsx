import type { Trade } from '../types';
import { DirectionBadge } from './DirectionBadge';

export function TradesTable({ trades, onCloseClick }: { trades: Trade[]; onCloseClick: (trade: Trade) => void }) {
  if (trades.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>No trades yet.</div>;
  }

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
      <thead>
        <tr style={{ textAlign: 'left', color: 'var(--text-muted)', borderBottom: '1px solid var(--gridline)' }}>
          <th style={{ padding: '6px 8px' }}>Symbol</th>
          <th style={{ padding: '6px 8px' }}>Dir</th>
          <th style={{ padding: '6px 8px' }}>Mode</th>
          <th style={{ padding: '6px 8px' }}>Entry</th>
          <th style={{ padding: '6px 8px' }}>Exit</th>
          <th style={{ padding: '6px 8px' }}>PnL</th>
          <th style={{ padding: '6px 8px' }}>R</th>
          <th style={{ padding: '6px 8px' }}>Status</th>
          <th style={{ padding: '6px 8px' }} />
        </tr>
      </thead>
      <tbody>
        {trades.map((t) => (
          <tr key={t.id} style={{ borderBottom: '1px solid var(--gridline)' }}>
            <td style={{ padding: '6px 8px', fontWeight: 600 }}>{t.symbol}</td>
            <td style={{ padding: '6px 8px' }}>
              <DirectionBadge direction={t.direction} />
            </td>
            <td style={{ padding: '6px 8px' }}>{t.mode}</td>
            <td style={{ padding: '6px 8px' }}>{t.entry_price.toFixed(2)}</td>
            <td style={{ padding: '6px 8px' }}>{t.exit_price !== null ? t.exit_price.toFixed(2) : '—'}</td>
            <td
              style={{
                padding: '6px 8px',
                color: t.realized_pnl === null ? 'var(--text-muted)' : t.realized_pnl >= 0 ? 'var(--good-text)' : 'var(--critical)',
              }}
            >
              {t.realized_pnl !== null ? t.realized_pnl.toFixed(2) : '—'}
            </td>
            <td style={{ padding: '6px 8px' }}>{t.r_multiple !== null ? t.r_multiple.toFixed(2) : '—'}</td>
            <td style={{ padding: '6px 8px' }}>{t.status}</td>
            <td style={{ padding: '6px 8px' }}>
              {t.status === 'open' && (
                <button
                  onClick={() => onCloseClick(t)}
                  style={{ fontSize: 12, padding: '4px 10px', borderRadius: 6, border: '1px solid var(--border)', background: 'transparent', color: 'var(--text-primary)', cursor: 'pointer' }}
                >
                  Close
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
