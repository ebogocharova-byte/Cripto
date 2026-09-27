import type { MetricsSummary } from '../types';
import { StatTile } from './StatTile';

export function MetricsRow({ metrics }: { metrics: MetricsSummary }) {
  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      <StatTile label="Trades" value={String(metrics.total_trades)} />
      <StatTile
        label="Winrate"
        value={`${(metrics.winrate * 100).toFixed(0)}%`}
        tone={metrics.winrate >= 0.5 ? 'good' : 'critical'}
      />
      <StatTile
        label="Profit factor"
        value={metrics.profit_factor !== null ? metrics.profit_factor.toFixed(2) : '—'}
        tone={metrics.profit_factor !== null && metrics.profit_factor >= 1 ? 'good' : 'neutral'}
      />
      <StatTile
        label="Avg R"
        value={metrics.avg_r_multiple !== null ? metrics.avg_r_multiple.toFixed(2) : '—'}
        tone={metrics.avg_r_multiple !== null && metrics.avg_r_multiple >= 0 ? 'good' : 'critical'}
      />
      <StatTile
        label="Max DD"
        value={metrics.max_drawdown_pct !== null ? `${(metrics.max_drawdown_pct * 100).toFixed(1)}%` : '—'}
      />
      <StatTile
        label="Total PnL"
        value={metrics.total_pnl.toFixed(2)}
        tone={metrics.total_pnl >= 0 ? 'good' : 'critical'}
      />
    </div>
  );
}
