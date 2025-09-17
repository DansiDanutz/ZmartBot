// RealTimeChart - Main chart component with enhanced real-time Binance data
// Optimized for main chart usage with auto-refresh and real-time features
// ---------------------------------------------------------------------------------

import React, { useState, useEffect, useMemo } from "react";
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

const RANGE_TO_LIMIT = {
  "7D": 168, "30D": 30, "90D": 90, "180D": 180, "1Y": 365, "ALL": 1000,
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

function iso(ts) {
  const d = new Date(ts);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function fmtDay(isoDate) { return format(parseISO(isoDate), "MMM d"); }
function fmtTime(isoDate) { return format(parseISO(isoDate), "HH:mm"); }
function fmtFull(isoDate) { return format(parseISO(isoDate), "yyyy-MM-dd HH:mm"); }
function fmtNum(v, unit = "$", precision = 0) {
  const n = new Intl.NumberFormat(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision }).format(v);
  return unit ? `${unit}${n}` : n;
}

function ema(values, period) {
  if (!values.length) return [];
  const k = 2 / (period + 1);
  const out = new Array(values.length).fill(NaN);
  const seed = values.slice(0, period).reduce((a, b) => a + b, 0) / period;
  let prev = seed; out[period - 1] = seed;
  for (let i = period; i < values.length; i++) { const v = values[i] * k + prev * (1 - k); out[i] = v; prev = v; }
  return out;
}

async function fetchRealTimeData(symbol, range) {
  const limit = RANGE_TO_LIMIT[range];
  
  // Use optimal intervals for real-time data
  let interval, adjustedLimit;
  if (range === "7D") {
    interval = "1h";
    adjustedLimit = 168; // 7 days * 24 hours
  } else if (range === "30D") {
    interval = "4h";
    adjustedLimit = 180; // 30 days * 6 intervals per day
  } else {
    interval = "1d";
    adjustedLimit = limit;
  }
  
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${adjustedLimit}`;
  
  console.log(`🔄 Real-time data for ${symbol}: ${interval} intervals, ${adjustedLimit} points`);
  
  const res = await fetch(url, { 
    headers: { 
      accept: "application/json",
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache'
    } 
  });
  
  if (!res.ok) throw new Error(`Binance HTTP ${res.status}`);
  const arr = await res.json();
  
  const data = arr.map((k) => ({ 
    date: iso(k[0]), 
    time: new Date(k[0]).toISOString(),
    close: Number(k[4]), 
    volume: Number(k[5]),
    timestamp: k[0],
    open: Number(k[1]),
    high: Number(k[2]),
    low: Number(k[3])
  }));
  
  console.log(`✅ Real-time data loaded for ${symbol}: ${data.length} points, latest: $${data[data.length - 1]?.close}`);
  return data;
}

const RealTimeChart = ({ 
  symbol, 
  unit = "$", 
  precision = 2, 
  initialRange = "7D", 
  height = 300,
  showEMAs = true,
  showCrosses = true,
  showGrid = true,
  showTooltip = true,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
  isMainChart = false
}) => {
  const [range, setRange] = useState(initialRange);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);

  const fetchData = async () => {
    try {
      setLoading(true); 
      setError(null);
      const data = await fetchRealTimeData(symbol, range);
      setRows(data);
      setLastUpdate(new Date());
      setRefreshCount(prev => prev + 1);
    } catch (e) { 
      setError(e?.message || String(e)); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => {
    fetchData();
  }, [range, symbol]);

  // Auto-refresh for real-time data
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchData();
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, symbol, range]);

  const closes = useMemo(() => rows.map((r) => r.close), [rows]);
  const ema9 = useMemo(() => ema(closes, 9), [closes]);
  const ema21 = useMemo(() => ema(closes, 21), [closes]);
  const ema50 = useMemo(() => ema(closes, 50), [closes]);
  const ema200 = useMemo(() => ema(closes, 200), [closes]);

  const data = useMemo(() => rows.map((r, i) => ({
    date: r.date, 
    time: r.time,
    value: r.close, 
    ema9: ema9[i], 
    ema21: ema21[i], 
    ema50: ema50[i], 
    ema200: ema200[i],
  })), [rows, ema9, ema21, ema50, ema200]);

  const markers = useMemo(() => {
    if (!showCrosses) return [];
    const out = [];
    for (let i = 1; i < data.length; i++) {
      const p = data[i-1], c = data[i];
      if (!isFinite(p.ema50) || !isFinite(p.ema200) || !isFinite(c.ema50) || !isFinite(c.ema200)) continue;
      if (p.ema50 < p.ema200 && c.ema50 >= c.ema200) out.push({ date: c.date, value: c.value, kind: "bull" });
      if (p.ema50 > p.ema200 && c.ema50 <= c.ema200) out.push({ date: c.date, value: c.value, kind: "bear" });
    }
    return out;
  }, [data, showCrosses]);

  const last = data.at(-1)?.value ?? 0;
  const first = data[0]?.value ?? 0;
  const change = first ? ((last - first) / first) * 100 : 0;

  if (loading && rows.length === 0) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-slate-950 rounded-lg">
        <div className="text-slate-400 text-sm">Loading {symbol}...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-slate-950 rounded-lg">
        <div className="text-red-400 text-sm">Error: {error}</div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-slate-950 rounded-lg">
        <div className="text-slate-400 text-sm">No data for {symbol}</div>
      </div>
    );
  }

  return (
    <div className="w-full rounded-lg border border-white/10 bg-slate-950 p-4 shadow-lg">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="text-slate-200 text-lg font-semibold">{symbol}</div>
          {isMainChart && (
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold text-slate-100">{fmtNum(last, unit, precision)}</div>
              <div className={clsx("text-sm font-medium", change >= 0 ? "text-emerald-400" : "text-rose-400")}>
                {change >= 0 ? "+" : ""}{change.toFixed(2)}%
              </div>
            </div>
          )}
          {lastUpdate && (
            <div className="text-slate-400 text-xs">
              Updated: {lastUpdate.toLocaleTimeString()}
              {autoRefresh && <span className="ml-1">🔄</span>}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            disabled={loading}
            className="bg-slate-800 border border-white/10 rounded px-3 py-1 text-slate-200 text-sm hover:bg-slate-700 disabled:opacity-50"
            title="Refresh data"
          >
            {loading ? '🔄' : '🔄'} Refresh
          </button>
          <select 
            value={range} 
            onChange={(e) => setRange(e.target.value)} 
            className="bg-slate-900 border border-white/10 rounded px-3 py-1 text-slate-200 text-sm"
          >
            <option value="7D">7D (1h)</option>
            <option value="30D">30D (4h)</option>
            <option value="90D">90D</option>
            <option value="180D">180D</option>
            <option value="1Y">1Y</option>
            <option value="ALL">MAX</option>
          </select>
        </div>
      </div>

      <div style={{ height: height - 80 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
            {showGrid && <CartesianGrid stroke={COLORS.grid} vertical={false} />}
            <XAxis 
              dataKey={(d) => range === "7D" ? fmtTime(d.time) : fmtDay(d.date)} 
              tick={{ fill: "#cbd5e1", fontSize: 11 }} 
              axisLine={{ stroke: COLORS.axis }} 
              tickLine={false} 
              minTickGap={30}
            />
            <YAxis 
              width={70} 
              tick={{ fill: "#cbd5e1", fontSize: 11 }} 
              axisLine={{ stroke: COLORS.axis }} 
              tickLine={false} 
              tickFormatter={(v) => fmtNum(v, unit, precision)}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={COLORS.price} 
              strokeWidth={isMainChart ? 3 : 2} 
              dot={false} 
              activeDot={{ r: 5 }} 
              name="Price" 
            />
            {showEMAs && (
              <>
                <Line type="monotone" dataKey="ema9" stroke={COLORS.ema9} strokeWidth={1.5} dot={false} isAnimationActive={false} name="EMA 9" />
                <Line type="monotone" dataKey="ema21" stroke={COLORS.ema21} strokeWidth={1.5} dot={false} isAnimationActive={false} name="EMA 21" />
                {range !== "7D" && (
                  <>
                    <Line type="monotone" dataKey="ema50" stroke={COLORS.ema50} strokeWidth={2} dot={false} isAnimationActive={false} name="EMA 50" />
                    <Line type="monotone" dataKey="ema200" stroke={COLORS.ema200} strokeWidth={2} dot={false} isAnimationActive={false} name="EMA 200" />
                  </>
                )}
              </>
            )}
            {showCrosses && markers.length > 0 && (
              <Scatter
                data={markers.map((m) => ({ ...m }))}
                shape={(props) => {
                  const { cx, cy, payload } = props;
                  const up = payload.kind === "bull"; 
                  const size = 8;
                  const path = up
                    ? `M ${cx} ${cy - size} L ${cx - size} ${cy + size} L ${cx + size} ${cy + size} Z`
                    : `M ${cx} ${cy + size} L ${cx - size} ${cy - size} L ${cx + size} ${cy - size} Z`;
                  return <path d={path} fill={up ? COLORS.crossUp : COLORS.crossDown} opacity={0.9} stroke="#000" strokeWidth={0.5} />;
                }}
              />
            )}
            {showTooltip && (
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  const byKey = {}; 
                  for (const p of payload) byKey[p.dataKey] = p;
                  return (
                    <div className="rounded-lg border border-white/10 bg-slate-900/95 p-3 shadow-xl backdrop-blur">
                      <div className="text-xs text-slate-400">{fmtFull(label)}</div>
                      <div className="mt-1 text-base font-semibold" style={{ color: COLORS.price }}>
                        Price: {fmtNum(byKey.value?.value ?? 0, unit, precision)}
                      </div>
                      {showEMAs && isFinite(byKey.ema9?.value) && (
                        <div className="text-xs" style={{ color: COLORS.ema9 }}>
                          EMA9: {fmtNum(byKey.ema9.value, unit, precision)}
                        </div>
                      )}
                      {showEMAs && isFinite(byKey.ema21?.value) && (
                        <div className="text-xs" style={{ color: COLORS.ema21 }}>
                          EMA21: {fmtNum(byKey.ema21.value, unit, precision)}
                        </div>
                      )}
                      {showEMAs && range !== "7D" && isFinite(byKey.ema50?.value) && (
                        <div className="text-xs" style={{ color: COLORS.ema50 }}>
                          EMA50: {fmtNum(byKey.ema50.value, unit, precision)}
                        </div>
                      )}
                    </div>
                  );
                }} 
                cursor={{ stroke: "#233148", strokeDasharray: "3 3" }} 
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {isMainChart && (
        <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-400">
          {[
            { c: COLORS.price, t: "Price" }, 
            { c: COLORS.ema9, t: "EMA 9" }, 
            { c: COLORS.ema21, t: "EMA 21" },
            { c: COLORS.ema50, t: "EMA 50" }, 
            { c: COLORS.ema200, t: "EMA 200" },
            { c: COLORS.crossUp, t: "Golden Cross" }, 
            { c: COLORS.crossDown, t: "Death Cross" },
          ].map((i) => (
            <div key={i.t} className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full" style={{ background: i.c }} /> 
              {i.t}
            </div>
          ))}
          <div className="opacity-70 ml-auto">
            Powered by Binance • Real-time • Refresh #{refreshCount}
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeChart;
