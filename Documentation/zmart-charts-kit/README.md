# Zmart Charts Kit (Cursor-Ready)

Beautiful, production-quality crypto charts for React (and Next.js) using **Recharts**.  
Includes live BTC data sources, EMAs, crossover markers, and price+volume layouts.

## Features
- Live data from **Binance** or **Kraken** (toggle at runtime)
- Optional **CoinGecko** implementation (price + volume) 
- **EMA(9/21/50/200)** overlays
- **Golden/Death Cross** markers (EMA50 vs EMA200)
- Modern dark styling (Tailwind-friendly) with smooth tooltips & grid
- Drop-in components for Cursor

## Quick Start (React / Next.js)

1. **Install dependencies**
```bash
npm i recharts date-fns clsx
# Tailwind optional but recommended for styling
```

2. **Copy components** (from `src/components/`):
   - `BTCProChart.tsx` — Live from Binance/Kraken + EMA(9/21/50/200) + Crossovers
   - `LiveBtcCharts.tsx` — CoinGecko + Price/Volume + EMA(9/21)

3. **Use in a page**
```tsx
// app/page.tsx or pages/index.tsx (Next.js)
// or any React route/page
import BTCProChart from "@/components/BTCProChart";
import { TrendCardLive, PriceVolumeCard } from "@/components/LiveBtcCharts";

export default function Page() {
  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100 space-y-8">
      <h1 className="text-2xl font-semibold">Zmart Live Charts</h1>
      <BTCProChart />
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <TrendCardLive />
        <PriceVolumeCard />
      </div>
    </div>
  );
}
```

> If you don't use Tailwind, just replace the classNames with your CSS.

## Component Props

### `BTCProChart`
```ts
type Props = {
  unit?: string;         // default "$"
  precision?: number;    // decimals for labels
  initialRange?: "7D"|"30D"|"90D"|"180D"|"1Y"|"ALL"; // default "30D"
  initialSource?: "binance"|"kraken"; // default "binance"
  height?: number;       // chart height in px, default 420
};
```

### `TrendCardLive` (CoinGecko + EMA)
```ts
type Props = {
  title?: string; unit?: string; precision?: number;
  initialRange?: "7D"|"30D"|"90D"|"180D"|"1Y"|"ALL";
  height?: number;
};
```

### `PriceVolumeCard` (CoinGecko: price area + volume bars)
```ts
type Props = {
  title?: string; unit?: string; precision?: number;
  initialRange?: "7D"|"30D"|"90D"|"180D"|"1Y"|"ALL";
  height?: number;
};
```

## Notes & Tips
- **Rate limits**: Public endpoints may throttle — avoid frequent rapid refreshes.
- **CORS**: These public APIs usually allow browser fetch. If you hit CORS blocks, proxy the requests via your server.
- **Timezone**: Labels are daily/UTC based on provider timestamps.
- **Design**: Tuned for dark UIs. Adjust colors to your Zmart palette easily (see constants in files).

## License
MIT — use freely in your projects.
