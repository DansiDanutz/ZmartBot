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
