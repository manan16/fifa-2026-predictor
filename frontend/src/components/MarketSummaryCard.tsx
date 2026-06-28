import { OddsConsensus, Prediction } from "../types";

function percent(value?: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

function odds(value?: number | null) {
  return value == null ? "-" : value.toFixed(2);
}

export default function MarketSummaryCard({ prediction, consensus, message }: { prediction: Prediction; consensus: OddsConsensus | null; message: string }) {
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <h2 className="text-lg font-black text-white">Market Summary</h2>
      <p className="mt-2 text-sm text-slate-300">{message}</p>
      <div className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
        <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Model probability</p><p className="font-black text-yellow-300">{percent(Math.max(prediction.home_win_probability, prediction.away_win_probability))}</p></div>
        <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Market line</p><p className="font-black text-sky-300">{percent(Math.max(consensus?.home_probability ?? 0, consensus?.away_probability ?? 0))}</p></div>
        <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Bookmakers</p><p className="font-black text-white">{consensus?.bookmaker_count ?? 0}</p></div>
      </div>
      <p className="mt-4 text-sm text-slate-300">Best market odds: {odds(consensus?.best_home_odds)} / {odds(consensus?.best_draw_odds)} / {odds(consensus?.best_away_odds)}</p>
      <p className="mt-3 text-xs font-bold uppercase tracking-wide text-slate-400">Market data is shown for analytics only. Not betting advice.</p>
    </section>
  );
}
