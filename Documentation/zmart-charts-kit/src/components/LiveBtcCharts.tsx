// Live BTC Charts with EMA + Volume (React + Recharts)
// ----------------------------------------------------
// Install deps:
//   npm i recharts date-fns clsx
// (Tailwind optional but styles assume a dark UI.)
//
// What’s inside this single file:
//   1) useBtcSeries() — fetches live BTC-USD daily data + volume from CoinGecko
//   2) TrendCardLive — pretty price chart with EMA(9/21) overlays + range chips
//   3) PriceVolumeCard — area (price) + bars (volume) with dual axes
//   4) Example Page demo
//
// Or import components:
//   import { TrendCardLive, PriceVolumeCard } from "@/components/LiveBtcCharts";

import React, { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
  Bar,
  ComposedChart,
} from "recharts";
import { format, parseISO } from "date-fns";
import clsx from "clsx";

export type OHLCPoint = { date: string; close: number; volume: number; };
export type RangeKey = "7D" | "30D" | "90D" | "180D" | "1Y" | "ALL";

const RANGE_TO_DAYS: Record<RangeKey, number | "max"> = {
  "7D": 7, "30D": 30, "90D": 90, "180D": 180, "1Y": 365, "ALL": "max",
};

function isoDateFromMillis(ms: number) {
  const d = new Date(ms);
  const y = d.getUTCFullYear(); const m = String(d.getUTCMonth() + 1).padStart(2, "0"); const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}
function fmtDateLabel(iso: string) { return format(parseISO(iso), "MMM d"); }
function fmtFullDate(iso: string) { return format(parseISO(iso), "yyyy-MM-dd (EEE)"); }
function fmt(v: number, unit = "$", precision = 0) {
  const n = new Intl.NumberFormat(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision }).format(v);
  return unit ? `${unit}${n}` : n;
}
function ema(values: number[], period: number) {
  if (values.length === 0) return [] as number[];
  const k = 2 / (period + 1); const out: number[] = new Array(values.length).fill(NaN);
  const seed = values.slice(0, period).reduce((a, b) => a + b, 0) / period; let prev = seed; out[period - 1] = seed;
  for (let i = period; i < values.length; i++) { const v = values[i] * k + prev * (1 - k); out[i] = v; prev = v; }
  return out;
}

export function useBtcSeries(range: RangeKey) {
  const [data, setData] = useState<OHLCPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        setLoading(true); setError(null);
        const days = RANGE_TO_DAYS[range];
        const url = `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=${days}&interval=daily`;
        const res = await fetch(url, { headers: { accept: "application/json" } });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        const prices: [number, number][] = json?.prices || [];
        const vols: [number, number][] = json?.total_volumes || [];
        const byDateVol = new Map<string, number>(); for (const [ts, v] of vols) byDateVol.set(isoDateFromMillis(ts), v || 0);
        const series: OHLCPoint[] = prices.map(([ts, p]) => ({ date: isoDateFromMillis(ts), close: Number(p), volume: Number(byDateVol.get(isoDateFromMillis(ts)) || 0) }));
        if (!cancelled) setData(series);
      } catch (e: any) { if (!cancelled) setError(e?.message || String(e)); }
      finally { if (!cancelled) setLoading(false); }
    }
    run(); return () => { cancelled = true; };
  }, [range]);
  return { data, loading, error };
}

function Chip({ active, children, onClick }: { active?: boolean; children: React.ReactNode; onClick?: () => void }) {
  return (
    <button onClick={onClick} className={clsx("px-3 py-1 rounded-full text-sm border transition", active ? "bg-emerald-500/15 border-emerald-500/50 text-emerald-300" : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10")}>
      {children}
    </button>
  );
}
function NiceTooltip({ active, payload, label, unit = "$", precision = 0 }: any) {
  if (!active || !payload?.length) return null; const p = payload[0];
  return (
    <div className="rounded-xl border border-white/10 bg-slate-900/90 p-3 shadow-2xl backdrop-blur">
      <div className="text-xs text-slate-400">{fmtFullDate(label)}</div>
      <div className="mt-0.5 text-base font-semibold">{fmt(p.value, unit, precision)}</div>
    </div>
  );
}

export function TrendCardLive({ title = "BTC / USD", unit = "$", precision = 0, initialRange = "30D", height = 360 }: { title?: string; unit?: string; precision?: number; initialRange?: RangeKey; height?: number; }) {
  const [range, setRange] = useState<RangeKey>(initialRange);
  const { data, loading, error } = useBtcSeries(range);
  const values = useMemo(() => data.map((d) => d.close), [data]);
  const ema9 = useMemo(() => ema(values, 9), [values]);
  const ema21 = useMemo(() => ema(values, 21), [values]);
  const merged = useMemo(() => data.map((d, i) => ({ date: d.date, value: d.close, ema9: ema9[i], ema21: ema21[i] })), [data, ema9, ema21]);
  const last = merged.at(-1)?.value ?? 0; const first = merged[0]?.value ?? 0; const change = first ? ((last - first) / first) * 100 : 0;
  return (
    <div className="w-full rounded-2xl border border-white/10 bg-slate-950 p-4 shadow-2xl">
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[180px]"><div className="text-slate-200 text-lg font-semibold">{title}</div><div className="text-slate-400 text-sm">Live from CoinGecko • Range {range}</div></div>
        <div className="flex items-center gap-2">{(["7D","30D","90D","180D","1Y","ALL"] as RangeKey[]).map((r) => (<Chip key={r} active={r === range} onClick={() => setRange(r)}>{r === "ALL" ? "MAX" : r}</Chip>))}</div>
      </div>
      <div className="mt-3 flex items-baseline gap-4"><div className="text-2xl font-bold text-slate-100">{fmt(last, unit, precision)}</div><div className={clsx("text-sm font-medium", change >= 0 ? "text-emerald-400" : "text-rose-400")}>{change >= 0 ? "+" : ""}{change.toFixed(2)}%</div>{loading && <div className="text-xs text-slate-400">Loading…</div>}{error && <div className="text-xs text-rose-400">{error}</div>}</div>
      <div style={{ height }} className="mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={merged} margin={{ top: 10, right: 14, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="#1f2a44" vertical={false} />
            <XAxis dataKey={(d: any) => fmtDateLabel(d.date)} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: "#243047" }} tickLine={false} minTickGap={24} />
            <YAxis width={64} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: "#243047" }} tickLine={false} tickFormatter={(v) => fmt(v as number, unit, precision)} />
            <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2.4} dot={false} activeDot={{ r: 4 }} />
            <Line type="monotone" dataKey="ema9" stroke="#60a5fa" strokeWidth={1.6} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="ema21" stroke="#fbbf24" strokeWidth={1.6} dot={false} isAnimationActive={false} />
            <Tooltip content={<NiceTooltip unit={unit} precision={precision} />} cursor={{ stroke: "#233148", strokeDasharray: "3 3" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function PriceVolumeCard({ title = "BTC Price & Volume", unit = "$", precision = 0, initialRange = "30D", height = 360 }: { title?: string; unit?: string; precision?: number; initialRange?: RangeKey; height?: number; }) {
  const [range, setRange] = useState<RangeKey>(initialRange);
  const { data, loading, error } = useBtcSeries(range);
  const last = data.at(-1)?.close ?? 0;
  return (
    <div className="w-full rounded-2xl border border-white/10 bg-slate-950 p-4 shadow-2xl">
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[180px]"><div className="text-slate-200 text-lg font-semibold">{title}</div><div className="text-slate-400 text-sm">Live from CoinGecko • Range {range}</div></div>
        <div className="flex items-center gap-2">{(["7D","30D","90D","180D","1Y","ALL"] as RangeKey[]).map((r) => (<Chip key={r} active={r === range} onClick={() => setRange(r)}>{r === "ALL" ? "MAX" : r}</Chip>))}</div>
      </div>
      <div className="mt-3 text-2xl font-bold text-slate-100">{fmt(last, unit, precision)}</div>{loading && <div className="text-xs text-slate-400">Loading…</div>}{error && <div className="text-xs text-rose-400">{error}</div>}
      <div style={{ height }} className="mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 14, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="#1f2a44" vertical={false} />
            <XAxis dataKey={(d: any) => fmtDateLabel(d.date)} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: "#243047" }} tickLine={false} minTickGap={24} />
            <YAxis yAxisId="price" width={64} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: "#243047" }} tickLine={false} tickFormatter={(v) => fmt(v as number, unit, precision)} />
            <YAxis yAxisId="volume" orientation="right" width={60} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={{ stroke: "#243047" }} tickLine={false} tickFormatter={(v) => new Intl.NumberFormat().format(v as number)} />
            <defs><linearGradient id="pvGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#22c55e" stopOpacity={0.45} /><stop offset="100%" stopColor="#22c55e" stopOpacity={0} /></linearGradient></defs>
            <Area yAxisId="price" type="monotone" dataKey="close" stroke="#22c55e" fill="url(#pvGrad)" strokeWidth={2.2} dot={false} />
            <Bar yAxisId="volume" dataKey="volume" fill="#475569" opacity={0.8} barSize={6} />
            <Tooltip content={({ active, payload, label }: any) => {
              if (!active || !payload?.length) return null;
              const priceP = payload.find((p: any) => p.dataKey === "close");
              const volP = payload.find((p: any) => p.dataKey === "volume");
              return (
                <div className="rounded-xl border border-white/10 bg-slate-900/90 p-3 shadow-2xl backdrop-blur">
                  <div className="text-xs text-slate-400">{fmtFullDate(label)}</div>
                  <div className="mt-0.5 text-base font-semibold">{fmt(priceP?.value ?? 0, unit, precision)}</div>
                  <div className="text-xs text-slate-400">Vol: {new Intl.NumberFormat().format(volP?.value ?? 0)}</div>
                </div>
              );
            }} cursor={{ stroke: "#233148", strokeDasharray: "3 3" }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
