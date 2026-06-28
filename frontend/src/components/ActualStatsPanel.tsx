import { ActualMatchStats } from "../types";

export default function ActualStatsPanel({ stats }: { stats: ActualMatchStats | null }) {
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <p className="text-sm font-black uppercase tracking-[0.16em] text-slate-300">Actual stats</p>
      {stats ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Shots</p><p className="font-black text-white">{stats.home_shots}-{stats.away_shots}</p></div>
          <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Possession</p><p className="font-black text-white">{stats.home_possession}% / {stats.away_possession}%</p></div>
          <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Cards</p><p className="font-black text-white">{stats.home_yellow_cards}-{stats.away_yellow_cards} yellows</p></div>
        </div>
      ) : (
        <p className="mt-4 bg-white/[0.06] p-4 font-bold text-slate-300">Actual stats not available yet</p>
      )}
    </section>
  );
}
