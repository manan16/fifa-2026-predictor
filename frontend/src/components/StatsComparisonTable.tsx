import { ActualMatchStats, PredictedMatchStats } from "../types";

export default function StatsComparisonTable({ predicted, actual }: { predicted: PredictedMatchStats | null; actual: ActualMatchStats | null }) {
  if (!predicted || !actual) return null;
  const rows = [
    ["Shots", `${predicted.home_shots}-${predicted.away_shots}`, `${actual.home_shots}-${actual.away_shots}`],
    ["Shots on target", `${predicted.home_shots_on_target}-${predicted.away_shots_on_target}`, `${actual.home_shots_on_target}-${actual.away_shots_on_target}`],
    ["Possession", `${predicted.home_possession}-${predicted.away_possession}`, `${actual.home_possession}-${actual.away_possession}`],
    ["Corners", `${predicted.home_corners}-${predicted.away_corners}`, `${actual.home_corners}-${actual.away_corners}`],
  ];
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <h2 className="text-lg font-black text-white">Predicted vs Actual Comparison</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-sm">
          <thead className="bg-emerald-700 text-white"><tr><th className="px-3 py-2">Stat</th><th className="px-3 py-2">Model projection</th><th className="px-3 py-2">Actual stats</th></tr></thead>
          <tbody>{rows.map(([label, model, real]) => <tr key={label} className="border-b border-white/10 text-slate-300"><td className="px-3 py-2 font-bold text-white">{label}</td><td className="px-3 py-2">{model}</td><td className="px-3 py-2">{real}</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}
