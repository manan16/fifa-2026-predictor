import { Fixture, OddsConsensus, Prediction } from "../types";
import ChalkPitch from "./ChalkPitch";
import CrestPip from "./CrestPip";
import SupremacyMeter from "./SupremacyMeter";
import { shortCode, statusKind, twoWayShare } from "../lib/match";

interface Props {
  fixture: Fixture;
  prediction: Prediction;
  consensus: OddsConsensus | null;
}

function formatKickoff(value?: string): string {
  if (!value) return "Kickoff TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";
  return new Intl.DateTimeFormat("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export default function MatchCentre({ fixture, prediction, consensus }: Props) {
  const homeName = fixture.home_team_name;
  const awayName = fixture.away_team_name;
  const homeCode = shortCode(fixture.home_team_code, homeName);
  const awayCode = shortCode(fixture.away_team_code, awayName);

  const modelProb =
    prediction.home_advance_probability ??
    twoWayShare(prediction.home_win_probability, prediction.away_win_probability);
  const marketProb = consensus
    ? twoWayShare(consensus.home_probability, consensus.away_probability)
    : fixture.market_home_probability != null
      ? twoWayShare(fixture.market_home_probability, fixture.market_away_probability)
      : null;

  const completed = statusKind(fixture.status) === "done";
  const score = completed
    ? `${fixture.actual_home_score ?? "–"}–${fixture.actual_away_score ?? "–"}`
    : `${prediction.predicted_home_goals}–${prediction.predicted_away_goals}`;

  const xgHome = prediction.predicted_stats?.expected_home_goals ?? fixture.expected_home_goals ?? prediction.predicted_home_goals;
  const xgAway = prediction.predicted_stats?.expected_away_goals ?? fixture.expected_away_goals ?? prediction.predicted_away_goals;

  const homeLead = modelProb >= 0.5;
  const modelPick = homeLead ? homeName : awayName;
  const marketFav =
    marketProb != null ? (marketProb >= 0.5 ? homeName : awayName) : null;
  const bestPrice = homeLead
    ? consensus?.best_home_odds ?? fixture.best_home_odds
    : consensus?.best_away_odds ?? fixture.best_away_odds;

  const meta = [
    fixture.stage,
    formatKickoff(fixture.kickoff_time),
    [fixture.venue, fixture.city].filter(Boolean).join(", ")
  ].filter(Boolean);

  return (
    <div className="relative overflow-hidden rounded border border-line bg-gradient-to-b from-turf/90 to-turf2/90 px-5 py-7 sm:px-10">
      <ChalkPitch className="opacity-50" />
      <div className="relative">
        <div className="mb-6 flex flex-wrap items-center gap-x-4 gap-y-2 font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">
          {meta.map((m, i) => (
            <span key={i} className={i === 0 ? "text-gold" : ""}>
              {m}
            </span>
          ))}
        </div>

        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
          <div className="flex flex-col items-center gap-3 text-center">
            <CrestPip code={homeCode} variant={homeLead ? "gold" : "default"} className="h-[70px] w-[62px] text-lg" />
            <div className="font-display text-[clamp(20px,3.4vw,30px)] font-bold uppercase leading-[0.95] text-chalk">
              {homeName}
            </div>
            <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-chalk-dim">
              {fixture.home_team_elo ? `Elo ${fixture.home_team_elo}` : `Rank ${fixture.home_team_ranking ?? "—"}`}
            </div>
          </div>

          <div className="text-center">
            <span className="font-display text-[clamp(34px,7vw,58px)] font-extrabold leading-none tracking-wide text-chalk font-tabular">
              {score}
            </span>
            {xgHome != null && xgAway != null && (
              <div className="mt-1.5 font-mono text-[11px] tracking-[0.1em] text-chalk-dim">
                xG {xgHome.toFixed(1)} — {xgAway.toFixed(1)}
              </div>
            )}
          </div>

          <div className="flex flex-col items-center gap-3 text-center">
            <CrestPip code={awayCode} variant={!homeLead ? "gold" : "default"} className="h-[70px] w-[62px] text-lg" />
            <div className="font-display text-[clamp(20px,3.4vw,30px)] font-bold uppercase leading-[0.95] text-chalk">
              {awayName}
            </div>
            <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-chalk-dim">
              {fixture.away_team_elo ? `Elo ${fixture.away_team_elo}` : `Rank ${fixture.away_team_ranking ?? "—"}`}
            </div>
          </div>
        </div>

        <SupremacyMeter
          className="mt-8"
          homeCode={homeCode}
          awayCode={awayCode}
          modelProb={modelProb}
          marketProb={marketProb}
        />

        <div className="mt-6 flex flex-wrap gap-2.5">
          <span className="flex items-center gap-2 rounded-sm border border-line px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-chalk-dim">
            <span className="h-2 w-2 rounded-sm bg-gold" /> Model pick <b className="font-bold text-chalk">{modelPick}</b>
          </span>
          {marketFav && (
            <span className="flex items-center gap-2 rounded-sm border border-line px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-chalk-dim">
              <span className="h-2 w-2 rounded-sm bg-sky" /> Market favours{" "}
              <b className="font-bold text-chalk">{marketFav}</b>
            </span>
          )}
          <span className="rounded-sm border border-line px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-chalk-dim">
            Confidence <b className="font-bold text-chalk">{prediction.confidence}</b>
          </span>
          {bestPrice != null && (
            <span className="rounded-sm border border-line px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-chalk-dim">
              Best price <b className="font-bold text-chalk font-tabular">{bestPrice.toFixed(2)}</b>
            </span>
          )}
        </div>

        {prediction.explanation.length > 0 && (
          <ul className="mt-6 grid gap-1.5 border-t border-line pt-5 text-sm text-chalk-dim sm:grid-cols-2">
            {prediction.explanation.map((line, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-gold">·</span>
                {line}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
