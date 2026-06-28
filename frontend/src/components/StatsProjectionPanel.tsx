import { ActualMatchStats, PredictedMatchStats } from "../types";

interface Props {
  homeTeam: string;
  awayTeam: string;
  predictedStats: PredictedMatchStats | null;
  actualStats: ActualMatchStats | null;
}

function numberValue(value: number | null | undefined, suffix = "") {
  return value == null ? "TBD" : `${value}${suffix}`;
}

function probability(value: number | null | undefined) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

function StatBar({
  label,
  homeLabel,
  awayLabel,
  home,
  away,
  suffix = "",
  max
}: {
  label: string;
  homeLabel: string;
  awayLabel: string;
  home: number | null | undefined;
  away: number | null | undefined;
  suffix?: string;
  max?: number;
}) {
  const total = max ?? Math.max(1, (home ?? 0) + (away ?? 0));
  const homeWidth = home == null ? 0 : Math.max(8, Math.min(100, (home / total) * 100));
  const awayWidth = away == null ? 0 : Math.max(8, Math.min(100, (away / total) * 100));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-xs font-black uppercase text-slate-400">
        <span>{label}</span>
        <span className="text-slate-500">Model projection</span>
      </div>
      <div className="grid grid-cols-[64px_1fr_64px] items-center gap-3 text-sm font-black text-white">
        <span>{numberValue(home, suffix)}</span>
        <div className="grid h-3 grid-cols-2 overflow-hidden bg-white/10">
          <div className="flex justify-end bg-transparent">
            <span
              className="h-full animate-bar-fill bg-emerald-400 transition-all duration-700 ease-out"
              style={{ width: `${homeWidth}%` }}
              title={homeLabel}
            />
          </div>
          <div className="bg-transparent">
            <span
              className="block h-full animate-bar-fill bg-sky-400 transition-all duration-700 ease-out"
              style={{ width: `${awayWidth}%` }}
              title={awayLabel}
            />
          </div>
        </div>
        <span className="text-right">{numberValue(away, suffix)}</span>
      </div>
      <div className="flex items-center justify-between text-[11px] font-bold uppercase text-slate-500">
        <span>{homeLabel}</span>
        <span>{awayLabel}</span>
      </div>
    </div>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-white/10 bg-white/[0.06] p-3">
      <p className="text-xs font-bold uppercase text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-black text-white">{value}</p>
    </div>
  );
}

export default function StatsProjectionPanel({ homeTeam, awayTeam, predictedStats, actualStats }: Props) {
  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-black uppercase text-emerald-300">Predicted stats</p>
          <h2 className="mt-1 text-2xl font-black text-white">Model projection</h2>
        </div>
        <p className="max-w-xl text-sm font-bold text-slate-300">Stats are model-generated estimates, not official data.</p>
      </div>

      {predictedStats ? (
        <>
          <div className="mt-5 grid gap-4 lg:grid-cols-[1.3fr_1fr]">
            <div className="space-y-5 bg-stadium/45 p-4">
              <StatBar
                label="Possession"
                homeLabel={homeTeam}
                awayLabel={awayTeam}
                home={predictedStats.home_possession}
                away={predictedStats.away_possession}
                suffix="%"
                max={100}
              />
              <StatBar label="Shots" homeLabel={homeTeam} awayLabel={awayTeam} home={predictedStats.home_shots} away={predictedStats.away_shots} />
              <StatBar
                label="Shots on target"
                homeLabel={homeTeam}
                awayLabel={awayTeam}
                home={predictedStats.home_shots_on_target}
                away={predictedStats.away_shots_on_target}
              />
              <StatBar label="Corners" homeLabel={homeTeam} awayLabel={awayTeam} home={predictedStats.home_corners} away={predictedStats.away_corners} />
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              <Tile label="Expected goals" value={`${predictedStats.expected_home_goals.toFixed(2)} - ${predictedStats.expected_away_goals.toFixed(2)}`} />
              <Tile label="Both teams to score" value={probability(predictedStats.both_teams_to_score_probability)} />
              <Tile label="Over 2.5 goals" value={probability(predictedStats.over_2_5_goals_probability)} />
              <Tile label="Clean sheet" value={`${homeTeam}: ${probability(predictedStats.clean_sheet_home_probability)} · ${awayTeam}: ${probability(predictedStats.clean_sheet_away_probability)}`} />
              <Tile label="Cards" value={`${predictedStats.home_yellow_cards}-${predictedStats.away_yellow_cards} yellows · RC ${probability(predictedStats.home_red_card_probability)}/${probability(predictedStats.away_red_card_probability)}`} />
            </div>
          </div>
        </>
      ) : (
        <p className="mt-5 bg-white/[0.06] p-4 font-bold text-slate-300">Predicted stats are not available yet.</p>
      )}

      <div className="mt-5 border-t border-white/10 pt-5">
        <p className="text-sm font-black uppercase text-slate-300">Actual stats</p>
        {actualStats ? (
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            <div className="border border-white/10 bg-white/[0.06] p-3">
              <p className="font-black text-white">{homeTeam}</p>
              <p className="mt-2 text-sm text-slate-300">
                Shots {numberValue(actualStats.home_shots)} · SOT {numberValue(actualStats.home_shots_on_target)} · Possession {numberValue(actualStats.home_possession, "%")}
              </p>
            </div>
            <div className="border border-white/10 bg-white/[0.06] p-3">
              <p className="font-black text-white">{awayTeam}</p>
              <p className="mt-2 text-sm text-slate-300">
                Shots {numberValue(actualStats.away_shots)} · SOT {numberValue(actualStats.away_shots_on_target)} · Possession {numberValue(actualStats.away_possession, "%")}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-3 bg-white/[0.06] p-4 font-bold text-slate-300">Not available yet</p>
        )}
      </div>
    </section>
  );
}
