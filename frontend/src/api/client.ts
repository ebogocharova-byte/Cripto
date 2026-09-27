import type {
  EquityCurveResponse,
  Instrument,
  MetricsSummary,
  Signal,
  Trade,
  TradeClose,
  TradeCreate,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  listInstruments: () => request<Instrument[]>('/instruments'),

  listSignals: (params: { mode?: string; instrument?: string; limit?: number } = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][],
    );
    return request<Signal[]>(`/signals?${query.toString()}`);
  },

  listTrades: (params: { mode?: string; instrument?: string; status?: string } = {}) => {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][],
    );
    return request<Trade[]>(`/trades?${query.toString()}`);
  },

  createTrade: (payload: TradeCreate) =>
    request<Trade>('/trades', { method: 'POST', body: JSON.stringify(payload) }),

  closeTrade: (id: number, payload: TradeClose) =>
    request<Trade>(`/trades/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  getMetricsSummary: (mode: string, instrument?: string) => {
    const query = new URLSearchParams({ mode, ...(instrument ? { instrument } : {}) });
    return request<MetricsSummary>(`/metrics/summary?${query.toString()}`);
  },

  getEquityCurve: (mode = 'combined') =>
    request<EquityCurveResponse>(`/metrics/equity-curve?mode=${mode}`),
};
