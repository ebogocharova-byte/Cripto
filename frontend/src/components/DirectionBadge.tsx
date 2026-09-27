import type { Direction } from '../types';

const LABELS: Record<Direction, string> = { long: 'LONG', short: 'SHORT', neutral: 'NEUTRAL' };
const COLORS: Record<Direction, string> = {
  long: 'var(--good)',
  short: 'var(--critical)',
  neutral: 'var(--text-muted)',
};

export function DirectionBadge({ direction }: { direction: Direction }) {
  const color = COLORS[direction];
  return (
    <span
      style={{
        color,
        border: `1px solid ${color}`,
        borderRadius: 4,
        padding: '2px 8px',
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: 0.3,
      }}
    >
      {LABELS[direction]}
    </span>
  );
}
