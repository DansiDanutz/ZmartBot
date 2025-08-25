// BTC Live Chart — Binance/Kraken source + EMA(9/21/50/200) + Crossover markers
// Cursor-ready React component styled for a dark "Zmart" look (neon accents)
// ---------------------------------------------------------------------------------
// Install deps:
//   npm i recharts date-fns clsx
// (Tailwind optional but the classes here assume a dark UI.)
//
// Features
//   • Data source switcher: Binance (default) or Kraken
//   • Ranges: 7D · 30D · 90D · 180D · 1Y · MAX
//   • EMA overlays: 9, 21, 50, 200
//   • Golden/Death cross markers (EMA50 vs EMA200)
//   • Nice tooltip, grid, gradient, and KPI header
//
// Usage
//   import BTCProChart from "@/components/BTCProChart";
//   export default function Page(){
//     return <div className="p-6 bg-slate-950 min-h-screen text-slate-100"><BTCProChart /></div>
//   }

import React, { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Scatter,
} from "recharts";
import { format, parseISO } from "date-fns";
import clsx from "clsx";

type RangeKey = "7D" | "30D" | "90D" | "180D" | "1Y" | "ALL";
type Row = { date: string; close: number; volume?: number };
type Marker = { date: string; value: number; kind: "bull" | "bear" };

const RANGE_TO_LIMIT: Record<RangeKey, number | "max"> = {
  "7D": 7, "30D": 30, "90D": 90, "180D": 180, "1Y": 365, "ALL": "max",
};

const COLORS = {
  price: "#22c55e",
  ema9: "#60a5fa",
  ema21: "#fbbf24",
  ema50: "#a78bfa",
  ema200: "#eab308",
  grid: "#1f2a44",
  axis: "#243047",
  crossUp: "#10b981",
  crossDown: "#ef4444",
};

function iso(ts: number) {
  const d = new Date(ts);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function fmtDay(isoDate: string) { return format(parseISO(isoDate), "MMM d"); }
function fmtFull(isoDate: string) { return format(parseISO(isoDate), "yyyy-MM-dd (EEE)"); }
function fmtNum(v: number, unit = "$", precision = 0) {
  const n = new Intl.NumberFormat(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision }).format(v);
  return unit ? `${unit}${n}` : n;
}

function ema(values: number[], period: number) {
  if (!values.length) return [] as number[];
  const k = 2 / (period + 1);
  const out = new Array(values.length).fill(NaN);
  const seed = values.slice(0, period).reduce((a, b) => a + b, 0) / period;
  let prev = seed; out[period - 1] = seed;
  for (let i = period; i < values.length; i++) { const v = values[i] * k + prev * (1 - k); out[i] = v; prev = v; }
  return out;
}

async function fetchBinance(range: RangeKey): Promise<Row[]> {
  const limit = RANGE_TO_LIMIT[range] === "max" ? 1000 : (RANGE_TO_LIMIT[range] as number);
  const url = `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=${limit}`;
  const res = await fetch(url, { headers: { accept: "application/json" } });
  if (!res.ok) throw new Error(`Binance HTTP ${res.status}`);
  const arr: any[] = await res.json();
  return arr.map((k) => ({ date: iso(k[0]), close: Number(k[4]), volume: Number(k[5]) }));
}

async function fetchKraken(range: RangeKey): Promise<Row[]> {
  const url = `https://api.kraken.com/0/public/OHLC?pair=XXBTZUSD&interval=1440`;
  const res = await fetch(url, { headers: { accept: "application/json" } });
  if (!res.ok) throw new Error(`Kraken HTTP ${res.status}`);
  const json = await res.json();
  const series: any[] = json?.result?.XXBTZUSD || [];
  const rows = series.map((r) => ({ date: iso(r[0] * 1000), close: Number(r[4]) } as Row));
  const limit = RANGE_TO_LIMIT[range];
  return limit === "max" ? rows : rows.slice(-Number(limit));
}

export default function BTCProChart({
  unit = "$", precision = 0, initialRange = "30D", initialSource = "binance", height = 420,
}: { unit?: string; precision?: number; initialRange?: RangeKey; initialSource?: "binance"|"kraken"; height?: number; }) {
  const [range, setRange] = useState<RangeKey>(initialRange);
  const [source, setSource] = useState<"binance"|"kraken">(initialSource);
  const [rows, setRows] = useState<Row[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      try {
        setLoading(true); setError(null);
        const data = source === "binance" ? await fetchBinance(range) : await fetchKraken(range);
        if (!cancelled) setRows(data);
      } catch (e: any) { if (!cancelled) setError(e?.message || String(e)); }
      finally { if (!cancelled) setLoading(false); }
    }
    run(); return () => { cancelled = true; };
  }, [range, source]);

  const closes = useMemo(() => rows.map((r) => r.close), [rows]);
  const ema9 = useMemo(() => ema(closes, 9), [closes]);
  const ema21 = useMemo(() => ema(closes, 21), [closes]);
  const ema50 = useMemo(() => ema(closes, 50), [closes]);
  const ema200 = useMemo(() => ema(closes, 200), [closes]);

  const data = useMemo(() => rows.map((r, i) => ({
    date: r.date, value: r.close, ema9: ema9[i], ema21: ema21[i], ema50: ema50[i], ema200: ema200[i],
  })), [rows, ema9, ema21, ema50, ema200]);

  const markers = useMemo(() => {
    const out: { date: string; value: number; kind: "bull"|"bear" }[] = [];
    for (let i = 1; i < data.length; i++) {
      const p = data[i-1], c = data[i];
      if (!isFinite(p.ema50) || !isFinite(p.ema200) || !isFinite(c.ema50) || !isFinite(c.ema200)) continue;
      if (p.ema50 < p.ema200 && c.ema50 >= c.ema200) out.push({ date: c.date, value: c.value, kind: "bull" });
      if (p.ema50 > p.ema200 && c.ema50 <= c.ema200) out.push({ date: c.date, value: c.value, kind: "bear" });
    }
    return out;
  }, [data]);

  const min = useMemo(() => (data.length ? Math.min(...data.map((d) => d.value)) : 0), [data]);
  const max = useMemo(() => (data.length ? Math.max(...data.map((d) => d.value)) : 0), [data]);
  const last = data.at(-1)?.value ?? 0;
  const first = data[0]?.value ?? 0;
  const change = first ? ((last - first) / first) * 100 : 0;

  return (
    <div className="w-full rounded-2xl border border-white/10 bg-slate-950 p-4 shadow-2xl">
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-[220px]">
          <div className="text-slate-200 text-lg font-semibold">BTC / USD</div>
          <div className="text-slate-400 text-sm">Live • {source === "binance" ? "Binance" : "Kraken"} • Range {range}</div>
        </div>
        <div className="flex items-center gap-2">
          <select value={source} onChange={(e) => setSource(e.target.value as any)} className="bg-slate-900 border border-white/10 rounded px-2 py-1 text-slate-200">
            <option value="binance">Binance</option>
            <option value="kraken">Kraken</option>
          </select>
          <select value={range} onChange={(e) => setRange(e.target.value as RangeKey)} className="bg-slate-900 border border-white/10 rounded px-2 py-1 text-slate-200">
            <option value="7D">7D</option><option value="30D">30D</option><option value="90D">90D</option>
            <option value="180D">180D</option><option value="1Y">1Y</option><option value="ALL">MAX</option>
          </select>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-baseline gap-4">
        <div className="text-2xl font-bold text-slate-100">{fmtNum(last, "$", 0)}</div>
        <div className={clsx("text-sm font-medium", change >= 0 ? "text-emerald-400" : "text-rose-400")}>{change >= 0 ? "+" : ""}{change.toFixed(2)}%</div>
      </div>

      <div style={{ height }} className="mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid stroke={COLORS.grid} vertical={false} />
            <XAxis dataKey={(d: any) => fmtDay(d.date)} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: COLORS.axis }} tickLine={false} minTickGap={24} />
            <YAxis width={70} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={{ stroke: COLORS.axis }} tickLine={false} tickFormatter={(v) => fmtNum(v as number)} />
            <Line type="monotone" dataKey="value" stroke={COLORS.price} strokeWidth={2.4} dot={false} activeDot={{ r: 4 }} name="Price" />
            <Line type="monotone" dataKey="ema9" stroke={COLORS.ema9} strokeWidth={1.6} dot={false} isAnimationActive={false} name="EMA 9" />
            <Line type="monotone" dataKey="ema21" stroke={COLORS.ema21} strokeWidth={1.6} dot={false} isAnimationActive={false} name="EMA 21" />
            <Line type="monotone" dataKey="ema50" stroke={COLORS.ema50} strokeWidth={1.8} dot={false} isAnimationActive={false} name="EMA 50" />
            <Line type="monotone" dataKey="ema200" stroke={COLORS.ema200} strokeWidth={2} dot={false} isAnimationActive={false} name="EMA 200" />
            <ReferenceLine y={min} stroke="#64748b" strokeDasharray="3 3" />
            <ReferenceLine y={max} stroke="#64748b" strokeDasharray="3 3" />
            <Scatter
              data={markers.map((m) => ({ ...m }))}
              shape={(props: any) => {
                const { cx, cy, payload } = props;
                const up = payload.kind === "bull"; const size = 8;
                const path = up
                  ? `M ${cx} ${cy - size} L ${cx - size} ${cy + size} L ${cx + size} ${cy + size} Z`
                  : `M ${cx} ${cy + size} L ${cx - size} ${cy - size} L ${cx + size} ${cy - size} Z`;
                return <path d={path} fill={up ? COLORS.crossUp : COLORS.crossDown} opacity={0.9} stroke="#000" strokeWidth={0.5} />;
              }}
            />
            <Tooltip content={({ active, payload, label }: any) => {
              if (!active || !payload?.length) return null;
              const byKey: Record<string, any> = {}; for (const p of payload) byKey[p.dataKey] = p;
              return (
                <div className="rounded-xl border border-white/10 bg-slate-900/90 p-3 shadow-2xl backdrop-blur">
                  <div className="text-xs text-slate-400">{fmtFull(label)}</div>
                  <div className="mt-0.5 text-base font-semibold" style={{ color: COLORS.price }}>Price: {fmtNum(byKey.value?.value ?? 0)}</div>
                  {isFinite(byKey.ema9?.value) && <div className="text-xs" style={{ color: COLORS.ema9 }}>EMA9: {fmtNum(byKey.ema9.value)}</div>}
                  {isFinite(byKey.ema21?.value) && <div className="text-xs" style={{ color: COLORS.ema21 }}>EMA21: {fmtNum(byKey.ema21.value)}</div>}
                  {isFinite(byKey.ema50?.value) && <div className="text-xs" style={{ color: COLORS.ema50 }}>EMA50: {fmtNum(byKey.ema50.value)}</div>}
                  {isFinite(byKey.ema200?.value) && <div className="text-xs" style={{ color: COLORS.ema200 }}>EMA200: {fmtNum(byKey.ema200.value)}</div>}
                </div>
              );
            }} cursor={{ stroke: "#233148", strokeDasharray: "3 3" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-400">
        {[
          { c: COLORS.price, t: "Price" }, { c: COLORS.ema9, t: "EMA 9" }, { c: COLORS.ema21, t: "EMA 21" },
          { c: COLORS.ema50, t: "EMA 50" }, { c: COLORS.ema200, t: "EMA 200" },
          { c: COLORS.crossUp, t: "Golden Cross" }, { c: COLORS.crossDown, t: "Death Cross" },
        ].map((i) => <div key={i.t} className="flex items-center gap-1"><span className="inline-block h-2 w-2 rounded-full" style={{ background: i.c }} /> {i.t}</div>)}
        <div className="opacity-70 ml-auto">Powered by {source === "binance" ? "Binance" : "Kraken"} • Recharts</div>
      </div>
    </div>
  );
}
