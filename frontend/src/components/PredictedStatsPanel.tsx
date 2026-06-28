import { PredictedMatchStats } from "../types";

interface Props {
  homeTeam: string;
  awayTeam: string;
  stats: PredictedMatchStats | null;
}

function percent(value?: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

function Bar({ label, home, away, suffix = "" }: { label: string; home?: number | null; away?: number | null; suffix?: string }) {
  const total = Math.max(1, (home ?? 0) + (away ?? 0));
  return (
    <div>
      <div className="mb-2 flex justify-between text-xs font-black uppercase tracking-wide text-slate-400">
        <span>{label}</span>
        <span>{home ?? "-"}{suffix} · {away ?? "-"}{suffix}</span>
      </div>
      <div className="grid h-3 grid-cols-2 overflow-hidden bg-white/10">
        <span className="ml-auto block h-full animate-bar-fill bg-yellow-300" style={{ width: `${home == null ? 0 : Math.max(8, (home / total) * 100)}%` }} />
        <span className="block h-full animate-bar-fill bg-sky-300" style={{ width: `${away == null ? 0 : Math.max(8, (away / total) * 100)}%` }} />
      </div>
    </div>
  );
}

export default function PredictedStatsPanel({ homeTeam, awayTeam, stats }: Props) {
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <p className="text-sm font-black uppercase tracking-[0.16em] text-yellow-300">Predicted stats</p>
      <p className="mt-1 text-sm font-bold text-slate-300">Stats are model-generated estimates, not official data.</p>
      {stats ? (
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-5">
            <Bar label="Expected goals" home={stats.expected_home_goals} away={stats.expected_away_goals} />
            <Bar label="Shots" home={stats.home_shots} away={stats.away_shots} />
            <Bar label="Shots on target" home={stats.home_shots_on_target} away={stats.away_shots_on_target} />
            <Bar label="Possession" home={stats.home_possession} away={stats.away_possession} suffix="%" />
            <Bar label="Corners" home={stats.home_corners} away={stats.away_corners} />
          </div>
          <div className="grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-1">
            <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Cards</p><p className="font-black text-white">{stats.home_yellow_cards}-{stats.away_yellow_cards} yellows</p></div>
            <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Red card probability</p><p className="font-black text-white">{percent(stats.home_red_card_probability)} / {percent(stats.away_red_card_probability)}</p></div>
            <div className="bg-white/[0.06] p-3"><p className="text-slate-400">BTTS / Over 2.5</p><p className="font-black text-white">{percent(stats.both_teams_to_score_probability)} / {percent(stats.over_2_5_goals_probability)}</p></div>
            <div className="bg-white/[0.06] p-3"><p className="text-slate-400">Clean sheet</p><p className="font-black text-white">{homeTeam} {percent(stats.clean_sheet_home_probability)} · {awayTeam} {percent(stats.clean_sheet_away_probability)}</p></div>
          </div>
        </div>
      ) : (
        <p className="mt-5 bg-white/[0.06] p-4 font-bold text-slate-300">Predicted stats are not available yet.</p>
      )}
    </section>
  );
}
