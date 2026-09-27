export function StatTile({
  label,
  value,
  tone = 'neutral',
}: {
  label: string;
  value: string;
  tone?: 'good' | 'critical' | 'neutral';
}) {
  const color =
    tone === 'good' ? 'var(--good-text)' : tone === 'critical' ? 'var(--critical)' : 'var(--text-primary)';
  return (
    <div
      style={{
        background: 'var(--surface-1)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: '12px 16px',
        minWidth: 120,
      }}
    >
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 600, color, fontVariantNumeric: 'tabular-nums' }}>
        {value}
      </div>
    </div>
  );
}
