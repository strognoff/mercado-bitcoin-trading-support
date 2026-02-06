import { useEffect, useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import './App.css';

const numberFormat = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 });
const intFormat = new Intl.NumberFormat('en-GB');

function fmtNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return numberFormat.format(value);
}

function fmtInt(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return intFormat.format(value);
}

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—';
  return `${value.toFixed(1)}%`;
}

function fmtTimestamp(ms) {
  if (!ms) return '—';
  const date = new Date(ms);
  return date.toLocaleString('en-GB', { timeZone: 'Europe/London', hour: '2-digit', minute: '2-digit', day: '2-digit', month: 'short' });
}

function NovaFace({ status = 'idle' }) {
  const glow = status === 'error' ? 'shadow-[0_0_32px_rgba(248,113,113,0.7)]' : status === 'loading' ? 'shadow-[0_0_32px_rgba(59,130,246,0.7)]' : 'shadow-[0_0_42px_rgba(34,211,238,0.7)]';
  return (
    <div className="flex items-center gap-4">
      <div className={`relative w-24 h-24 md:w-32 md:h-32 rounded-2xl border border-sky-400/50 bg-slate-950/80 ${glow} overflow-hidden`}>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(34,211,238,0.45),transparent_55%),radial-gradient(circle_at_80%_100%,rgba(129,140,248,0.35),transparent_50%)]" />
        <div className="relative grid grid-cols-5 grid-rows-5 gap-1 p-3 h-full">
          {Array.from({ length: 25 }).map((_, idx) => (
            <span
              key={idx}
              className={`rounded-sm ${idx === 6 || idx === 8 ? 'bg-sky-300' : idx === 16 || idx === 18 ? 'bg-sky-400' : idx === 12 ? 'bg-slate-100' : 'bg-slate-800/60'}`}
            />
          ))}
        </div>
      </div>
      <div className="flex flex-col text-xs md:text-sm text-slate-300">
        <span className="uppercase tracking-[0.3em] text-slate-400">Nova</span>
        <span className="font-semibold text-sky-300">Futuristic Pixel Core</span>
        <span className="text-slate-400">Risk-first BTC short/scalp posture</span>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, accent = 'text-sky-300' }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 flex flex-col gap-1">
      <span className="text-[11px] uppercase tracking-[0.28em] text-slate-500">{label}</span>
      <span className={`text-xl font-semibold ${accent}`}>{value}</span>
      {sub && <span className="text-[11px] text-slate-400">{sub}</span>}
    </div>
  );
}

function App() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function refresh() {
    try {
      setLoading(true);
      setError('');
      const res = await fetch('/api/insights');
      const json = await res.json();
      if (!json?.ok) throw new Error(json?.error || 'failed to load');
      setInsights(json);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 60_000);
    return () => clearInterval(id);
  }, []);

  const status = loading ? 'loading' : error ? 'error' : 'idle';
  const jobs = insights?.jobs || [];
  const profitLoss = insights?.profitLoss || {};
  const tokens = insights?.tokens || {};
  const tokenHistory = insights?.tokenHistory || [];
  const openTrades = insights?.openTrades || [];

  const nextRun = useMemo(() => {
    if (!jobs.length) return null;
    const sorted = [...jobs].sort((a, b) => (a.nextRunAtMs || 0) - (b.nextRunAtMs || 0));
    return sorted[0];
  }, [jobs]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-6 md:py-10 flex flex-col gap-6">
        <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Nova Command Deck</h1>
            <p className="text-xs md:text-sm text-slate-400">Live trading + system telemetry, powered by OpenClaw.</p>
          </div>
          <NovaFace status={status} />
        </header>

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            label="Total P/L"
            value={`$${fmtNumber(profitLoss.totalPnl)}`}
            sub={`Trades ${fmtInt(profitLoss.trades)} · Win rate ${fmtPct(profitLoss.winRate)}`}
            accent={profitLoss.totalPnl >= 0 ? 'text-emerald-300' : 'text-rose-300'}
          />
          <StatCard
            label="Tokens (total)"
            value={fmtInt(tokens.totalTokens)}
            sub={insights?.tokenChangePercent === null ? 'No change data yet' : `Δ ${fmtPct(insights.tokenChangePercent)} vs prev day`}
          />
          <StatCard
            label="Next cron"
            value={nextRun?.name || '—'}
            sub={nextRun ? `${nextRun.scheduleKind || ''} ${nextRun.scheduleExpr || ''} · ${fmtTimestamp(nextRun.nextRunAtMs)}` : 'No jobs detected'}
          />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-[0.28em] text-slate-500">Token usage</span>
              <button
                type="button"
                onClick={refresh}
                className="text-xs px-3 py-1 rounded-full border border-sky-400/60 text-sky-300 hover:bg-sky-500/10"
              >
                Refresh
              </button>
            </div>
            {error && <div className="text-xs text-rose-400">Error: {error}</div>}
            {!error && tokenHistory.length === 0 && <div className="text-xs text-slate-400">No token history yet.</div>}
            {tokenHistory.length > 0 && (
              <div className="h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={tokenHistory} margin={{ left: -12, right: 12 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                    <YAxis stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
                      formatter={(value) => [`${fmtInt(value)} tokens`, 'Usage']}
                    />
                    <Bar dataKey="tokens" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-3">
            <span className="text-xs uppercase tracking-[0.28em] text-slate-500">Next exit</span>
            <div className="text-sm text-slate-200">
              🎯 Target {fmtNumber(insights?.nextExit?.target)} USD
            </div>
            <div className="text-xs text-slate-400">
              Entry {fmtNumber(insights?.nextExit?.entryPrice)} · Trail {fmtNumber(insights?.nextExit?.trailingStart)}
            </div>
            {insights?.nextExit?.note && (
              <div className="text-[11px] text-slate-500">{insights.nextExit.note}</div>
            )}
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-3">
            <span className="text-xs uppercase tracking-[0.28em] text-slate-500">Open trades</span>
            {openTrades.length === 0 && <div className="text-xs text-slate-400">No open trades.</div>}
            {openTrades.length > 0 && (
              <div className="flex flex-col gap-2">
                {openTrades.map(trade => (
                  <div key={trade.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{trade.asset || 'BTC-USD'}</div>
                      <div className="text-[11px] text-slate-500">{trade.id.slice(0, 10)}…</div>
                    </div>
                    <div className="text-right text-[11px] text-slate-400">
                      <div>Entry {fmtNumber(trade.entryPrice)} USD</div>
                      <div>{trade.timestamp || '—'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-3">
            <span className="text-xs uppercase tracking-[0.28em] text-slate-500">Cron jobs</span>
            {jobs.length === 0 && <div className="text-xs text-slate-400">No cron jobs detected.</div>}
            {jobs.length > 0 && (
              <div className="flex flex-col gap-2">
                {jobs.slice(0, 4).map(job => (
                  <div key={job.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-slate-200">{job.name || job.id}</span>
                      <span className={`text-[11px] ${job.enabled ? 'text-emerald-300' : 'text-slate-500'}`}>
                        {job.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500">Next: {fmtTimestamp(job.nextRunAtMs)} · Last: {fmtTimestamp(job.lastRunAtMs)}</div>
                    {job.lastError && <div className="text-[11px] text-rose-400">{job.lastError}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
