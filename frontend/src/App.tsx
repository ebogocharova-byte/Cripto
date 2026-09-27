import { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { Trades } from './pages/Trades';

type Tab = 'dashboard' | 'trades';

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard');

  return (
    <div>
      <header style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24 }}>
        <h1 style={{ fontSize: 18, margin: 0 }}>Cripto</h1>
        <nav style={{ display: 'flex', gap: 4 }}>
          {(['dashboard', 'trades'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: '6px 14px',
                borderRadius: 6,
                border: 'none',
                cursor: 'pointer',
                background: tab === t ? 'var(--series-1)' : 'transparent',
                color: tab === t ? '#fff' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: 13,
                textTransform: 'capitalize',
              }}
            >
              {t}
            </button>
          ))}
        </nav>
      </header>
      {tab === 'dashboard' ? <Dashboard /> : <Trades />}
    </div>
  );
}
