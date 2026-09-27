import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { EquityChart } from '../components/EquityChart';
import { MetricsRow } from '../components/MetricsRow';
import { SignalsFeed } from '../components/SignalsFeed';
import type { EquityCurveResponse, MetricsSummary, Signal } from '../types';

export function Dashboard() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [equity, setEquity] = useState<EquityCurveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.listSignals({ mode: 'swing', limit: 20 }),
      api.getMetricsSummary('swing'),
      api.getEquityCurve('combined'),
    ])
      .then(([signalsRes, metricsRes, equityRes]) => {
        setSignals(signalsRes);
        setMetrics(metricsRes);
        setEquity(equityRes);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <div style={{ color: 'var(--critical)' }}>{error}</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <section>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>Equity curve</h2>
        {equity ? <EquityChart points={equity.points} /> : null}
      </section>

      <section>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>Metrics — swing</h2>
        {metrics ? <MetricsRow metrics={metrics} /> : null}
      </section>

      <section>
        <h2 style={{ fontSize: 16, marginBottom: 8 }}>Recent signals</h2>
        <SignalsFeed signals={signals} />
      </section>
    </div>
  );
}
