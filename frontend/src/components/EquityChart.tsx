import { useMemo, useState } from 'react';
import type { EquityCurvePoint } from '../types';

const WIDTH = 640;
const HEIGHT = 220;
const PAD_LEFT = 56;
const PAD_RIGHT = 12;
const PAD_TOP = 16;
const PAD_BOTTOM = 28;

export function EquityChart({ points }: { points: EquityCurvePoint[] }) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const { path, xForIndex, yForValue, minValue, maxValue } = useMemo(() => {
    const values = points.map((p) => p.equity_value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;
    const innerWidth = WIDTH - PAD_LEFT - PAD_RIGHT;
    const innerHeight = HEIGHT - PAD_TOP - PAD_BOTTOM;

    const xForIndex = (i: number) =>
      PAD_LEFT + (points.length <= 1 ? 0 : (i / (points.length - 1)) * innerWidth);
    const yForValue = (v: number) => PAD_TOP + innerHeight - ((v - minValue) / range) * innerHeight;

    const path = points
      .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xForIndex(i).toFixed(1)} ${yForValue(p.equity_value).toFixed(1)}`)
      .join(' ');

    return { path, xForIndex, yForValue, minValue, maxValue };
  }, [points]);

  if (points.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>No equity data yet.</div>;
  }

  const hovered = hoverIndex !== null ? points[hoverIndex] : null;

  function handleMouseMove(e: React.MouseEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const relX = ((e.clientX - rect.left) / rect.width) * WIDTH;
    const innerWidth = WIDTH - PAD_LEFT - PAD_RIGHT;
    const ratio = Math.min(1, Math.max(0, (relX - PAD_LEFT) / innerWidth));
    const index = Math.round(ratio * (points.length - 1));
    setHoverIndex(index);
  }

  return (
    <div style={{ position: 'relative' }}>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoverIndex(null)}
      >
        <line
          x1={PAD_LEFT}
          y1={HEIGHT - PAD_BOTTOM}
          x2={WIDTH - PAD_RIGHT}
          y2={HEIGHT - PAD_BOTTOM}
          stroke="var(--baseline)"
          strokeWidth={1}
        />
        <text x={4} y={PAD_TOP + 4} fontSize={10} fill="var(--text-muted)">
          {maxValue.toFixed(0)}
        </text>
        <text x={4} y={HEIGHT - PAD_BOTTOM} fontSize={10} fill="var(--text-muted)">
          {minValue.toFixed(0)}
        </text>
        {points.length === 1 ? (
          <circle cx={xForIndex(0)} cy={yForValue(points[0].equity_value)} r={4} fill="var(--series-1)" />
        ) : (
          <path d={path} fill="none" stroke="var(--series-1)" strokeWidth={2} strokeLinecap="round" />
        )}
        {hoverIndex !== null && (
          <>
            <line
              x1={xForIndex(hoverIndex)}
              y1={PAD_TOP}
              x2={xForIndex(hoverIndex)}
              y2={HEIGHT - PAD_BOTTOM}
              stroke="var(--gridline)"
              strokeWidth={1}
            />
            <circle
              cx={xForIndex(hoverIndex)}
              cy={yForValue(points[hoverIndex].equity_value)}
              r={4}
              fill="var(--series-1)"
            />
          </>
        )}
      </svg>
      {hovered && (
        <div
          style={{
            position: 'absolute',
            top: 4,
            right: 4,
            background: 'var(--surface-1)',
            border: '1px solid var(--border)',
            borderRadius: 6,
            padding: '6px 10px',
            fontSize: 12,
            pointerEvents: 'none',
          }}
        >
          <div style={{ color: 'var(--text-muted)' }}>
            {new Date(hovered.snapshot_time).toLocaleString()}
          </div>
          <div style={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
            {hovered.equity_value.toFixed(2)}
          </div>
        </div>
      )}
    </div>
  );
}
