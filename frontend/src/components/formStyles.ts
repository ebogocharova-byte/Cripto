import type { CSSProperties } from 'react';

export const fieldStyle: CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  borderRadius: 6,
  border: '1px solid var(--border)',
  background: 'var(--page)',
  color: 'var(--text-primary)',
  fontSize: 14,
};

export const labelStyle: CSSProperties = {
  display: 'block',
  fontSize: 12,
  color: 'var(--text-secondary)',
  marginBottom: 4,
};

export const rowStyle: CSSProperties = { marginBottom: 10 };

export const buttonStyle: CSSProperties = {
  padding: '8px 16px',
  borderRadius: 6,
  border: 'none',
  background: 'var(--series-1)',
  color: '#fff',
  fontWeight: 600,
  cursor: 'pointer',
};
