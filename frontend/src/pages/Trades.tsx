import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { CloseTradeForm } from '../components/CloseTradeForm';
import { CreateTradeForm } from '../components/CreateTradeForm';
import { Modal } from '../components/Modal';
import { buttonStyle } from '../components/formStyles';
import { TradesTable } from '../components/TradesTable';
import type { Instrument, Trade } from '../types';

export function Trades() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [closingTrade, setClosingTrade] = useState<Trade | null>(null);

  function refresh() {
    Promise.all([api.listTrades(), api.listInstruments()])
      .then(([t, i]) => {
        setTrades(t);
        setInstruments(i);
      })
      .catch((e: Error) => setError(e.message));
  }

  useEffect(refresh, []);

  if (error) return <div style={{ color: 'var(--critical)' }}>{error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ fontSize: 16, margin: 0 }}>Trades</h2>
        <button style={buttonStyle} onClick={() => setShowCreate(true)}>
          + New trade
        </button>
      </div>

      <TradesTable trades={trades} onCloseClick={setClosingTrade} />

      {showCreate && (
        <Modal title="New trade" onClose={() => setShowCreate(false)}>
          <CreateTradeForm
            instruments={instruments}
            onCancel={() => setShowCreate(false)}
            onCreated={() => {
              setShowCreate(false);
              refresh();
            }}
          />
        </Modal>
      )}

      {closingTrade && (
        <Modal title="Close trade" onClose={() => setClosingTrade(null)}>
          <CloseTradeForm
            trade={closingTrade}
            onCancel={() => setClosingTrade(null)}
            onClosed={() => {
              setClosingTrade(null);
              refresh();
            }}
          />
        </Modal>
      )}
    </div>
  );
}
