// ZmartChart - Professional Crypto Charts using Recharts (based on zmart-charts-kit)
// Supports any symbol with live data from Binance + EMA overlays + Golden/Death Cross markers
// ---------------------------------------------------------------------------------

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

// Type definitions (for reference)
// RangeKey = "7D" | "30D" | "90D" | "180D" | "1Y" | "ALL"
// Row = { date: string; close: number; volume?: number }
// Marker = { date: string; value: number; kind: "bull" | "bear" }

const RANGE_TO_LIMIT = {
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

function iso(ts) {
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) {
      console.warn('Invalid timestamp:', ts);
      return '1970-01-01'; // Fallback date
    }
    const y = d.getUTCFullYear();
    const m = String(d.getUTCMonth() + 1).padStart(2, "0");
    const day = String(d.getUTCDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  } catch (error) {
    console.error('Error in iso function:', error);
    return '1970-01-01'; // Fallback date
  }
}

function fmtDay(isoDate) { 
  try {
    return format(parseISO(isoDate), "MMM d"); 
  } catch (error) {
    console.error('Error in fmtDay function:', error);
    return 'Jan 1';
  }
}

function fmtFull(isoDate) { 
  try {
    return format(parseISO(isoDate), "yyyy-MM-dd (EEE)"); 
  } catch (error) {
    console.error('Error in fmtFull function:', error);
    return '1970-01-01 (Thu)';
  }
}
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

async function fetchBinanceData(symbol, range) {
  const limit = RANGE_TO_LIMIT[range] === "max" ? 1000 : RANGE_TO_LIMIT[range];
  
  // Use 1h intervals for more real-time data (better for main chart)
  const interval = range === "7D" ? "1h" : "1d";
  const adjustedLimit = range === "7D" ? 168 : limit; // 7 days * 24 hours = 168
  
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${adjustedLimit}`;
  
      // Reduced logging to prevent console spam
    if (process.env.NODE_ENV === 'development') {
      console.log(`📊 Fetching real-time data for ${symbol}: ${interval} intervals, ${adjustedLimit} points`);
    }
  
  const res = await fetch(url, { 
    headers: { 
      accept: "application/json",
      'Cache-Control': 'no-cache' // Ensure fresh data
    } 
  });
  
  if (!res.ok) throw new Error(`Binance HTTP ${res.status}`);
  const arr = await res.json();
  
  const data = arr.map((k) => {
    try {
      return {
        date: iso(k[0]), 
        close: Number(k[4]) || 0, 
        volume: Number(k[5]) || 0,
        timestamp: k[0] || Date.now() // Keep timestamp for real-time updates
      };
    } catch (error) {
      console.error('Error processing data point:', error, k);
      return {
        date: '1970-01-01',
        close: 0,
        volume: 0,
        timestamp: Date.now()
      };
    }
  }).filter(item => item.close > 0); // Filter out invalid data points
  
      // Reduced logging to prevent console spam
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ Real-time data loaded for ${symbol}: ${data.length} points, latest: $${data[data.length - 1]?.close}`);
    }
  return data;
}

const ZmartChart = ({ 
  symbol, 
  unit = "$", 
  precision = 2, 
  initialRange = "30D", 
  height = 120,
  showEMAs = true,
  showCrosses = true,
  showGrid = true,
  showTooltip = true,
  chartType = "candlestick",
  autoRefresh = false,
  refreshInterval = 30000 // 30 seconds
}) => {
  const [range, setRange] = useState(initialRange);
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true); 
      setError(null);
      const data = await fetchBinanceData(symbol, range);
      setRows(data);
      setLastUpdate(new Date());
    } catch (e) { 
      setError(e?.message || String(e)); 
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => {
    let cancelled = false;
    fetchData();
    return () => { cancelled = true; };
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

  const min = useMemo(() => (data.length ? Math.min(...data.map((d) => d.value)) : 0), [data]);
  const max = useMemo(() => (data.length ? Math.max(...data.map((d) => d.value)) : 0), [data]);
  const last = data.at(-1)?.value ?? 0;
  const first = data[0]?.value ?? 0;
  const change = first ? ((last - first) / first) * 100 : 0;

  if (loading) {
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
    <div className="w-full rounded-lg border border-white/10 bg-slate-950 p-3 shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="text-slate-200 text-sm font-semibold">{symbol}</div>
          {lastUpdate && (
            <div className="text-slate-400 text-xs">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchData}
            disabled={loading}
            className="bg-slate-800 border border-white/10 rounded px-2 py-1 text-slate-200 text-xs hover:bg-slate-700 disabled:opacity-50"
            title="Refresh data"
          >
            {loading ? '🔄' : '🔄'}
          </button>
          <select 
            value={range} 
            onChange={(e) => setRange(e.target.value)} 
            className="bg-slate-900 border border-white/10 rounded px-2 py-1 text-slate-200 text-xs"
          >
            <option value="7D">7D</option>
            <option value="30D">30D</option>
            <option value="90D">90D</option>
            <option value="180D">180D</option>
            <option value="1Y">1Y</option>
            <option value="ALL">MAX</option>
          </select>
        </div>
      </div>

      <div className="flex items-baseline gap-2 mb-2">
        <div className="text-lg font-bold text-slate-100">{fmtNum(last, unit, precision)}</div>
        <div className={clsx("text-sm font-medium", change >= 0 ? "text-emerald-400" : "text-rose-400")}>
          {change >= 0 ? "+" : ""}{change.toFixed(2)}%
        </div>
      </div>

      <div style={{ height: height - 80 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            {showGrid && <CartesianGrid stroke={COLORS.grid} vertical={false} />}
            <XAxis 
              dataKey={(d) => fmtDay(d.date)} 
              tick={{ fill: "#cbd5e1", fontSize: 10 }} 
              axisLine={{ stroke: COLORS.axis }} 
              tickLine={false} 
              minTickGap={20}
              hide={height < 150}
            />
            <YAxis 
              width={50} 
              tick={{ fill: "#cbd5e1", fontSize: 10 }} 
              axisLine={{ stroke: COLORS.axis }} 
              tickLine={false} 
              tickFormatter={(v) => fmtNum(v, unit, precision)}
              hide={height < 150}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={COLORS.price} 
              strokeWidth={chartType === "basic" ? 1.5 : 2} 
              dot={chartType === "basic"} 
              activeDot={{ r: 3 }} 
              name="Price" 
            />
            {showEMAs && chartType !== "basic" && (
              <>
                <Line type="monotone" dataKey="ema9" stroke={COLORS.ema9} strokeWidth={1} dot={false} isAnimationActive={false} name="EMA 9" />
                <Line type="monotone" dataKey="ema21" stroke={COLORS.ema21} strokeWidth={1} dot={false} isAnimationActive={false} name="EMA 21" />
                {chartType === "candlestick" && (
                  <>
                    <Line type="monotone" dataKey="ema50" stroke={COLORS.ema50} strokeWidth={1.5} dot={false} isAnimationActive={false} name="EMA 50" />
                    <Line type="monotone" dataKey="ema200" stroke={COLORS.ema200} strokeWidth={1.5} dot={false} isAnimationActive={false} name="EMA 200" />
                  </>
                )}
              </>
            )}
            {showCrosses && chartType === "candlestick" && markers.length > 0 && (
              <Scatter
                data={markers.map((m) => ({ ...m }))}
                shape={(props) => {
                  const { cx, cy, payload } = props;
                  const up = payload.kind === "bull"; 
                  const size = 6;
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
                    <div className="rounded-lg border border-white/10 bg-slate-900/95 p-2 shadow-xl backdrop-blur">
                      <div className="text-xs text-slate-400">{fmtFull(label)}</div>
                      <div className="mt-1 text-sm font-semibold" style={{ color: COLORS.price }}>
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
                    </div>
                  );
                }} 
                cursor={{ stroke: "#233148", strokeDasharray: "3 3" }} 
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ZmartChart;
