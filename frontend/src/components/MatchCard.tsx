import { Link } from "react-router-dom";
import { Fixture } from "../types";
import CrestPip from "./CrestPip";
import SupremacyMeter from "./SupremacyMeter";
import { favouritesDisagree, shortCode, twoWayShare } from "../lib/match";

function statusKind(status: string): "live" | "done" | "scheduled" {
  const s = status.toLowerCase();
  if (["live", "in_play", "playing"].includes(s)) return "live";
  if (["completed", "finished", "done", "ft", "full_time"].includes(s)) return "done";
  return "scheduled";
}

function formatKickoff(value?: string): string {
  if (!value) return "Kickoff TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export default function MatchCard({ fixture }: { fixture: Fixture }) {
  const homeCode = shortCode(fixture.home_team_code, fixture.home_team_name);
  const awayCode = shortCode(fixture.away_team_code, fixture.away_team_name);
  const modelShare = twoWayShare(fixture.home_win_probability, fixture.away_win_probability);
  const marketShare =
    fixture.market_home_probability != null || fixture.market_away_probability != null
      ? twoWayShare(fixture.market_home_probability, fixture.market_away_probability)
      : null;

  const kind = statusKind(fixture.status);
  const completed = kind === "done";
  const homeLead = modelShare >= 0.5;

  const upset = completed
    ? fixture.actual_winner != null && fixture.predicted_winner != null && fixture.predicted_winner !== fixture.actual_winner
    : favouritesDisagree(modelShare, marketShare);

  const score = completed
    ? `${fixture.actual_home_score ?? "–"}–${fixture.actual_away_score ?? "–"}`
    : fixture.predicted_home_goals != null && fixture.predicted_away_goals != null
      ? `${fixture.predicted_home_goals}–${fixture.predicted_away_goals}`
      : "–";

  const dot =
    kind === "live"
      ? "live-dot text-coral"
      : kind === "scheduled"
        ? "live-dot text-gold"
        : "inline-block h-2 w-2 rounded-full bg-chalk-faint";

  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="group block rounded border border-line bg-turf/45 p-4 transition duration-300 hover:-translate-y-1 hover:border-gold/40 hover:shadow-broadcast focus-visible:-translate-y-1"
    >
      <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.12em] text-chalk-dim">
        <span className="flex items-center gap-2">
          <span className={dot} style={{ backgroundColor: "currentColor" }} />
          <span className="text-gold">{fixture.stage}</span>
        </span>
        <span>{completed ? "FT" : formatKickoff(fixture.kickoff_time)}</span>
      </div>

      <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <div className="flex items-center gap-2.5">
          <CrestPip code={homeCode} variant={homeLead ? "gold" : "default"} />
          <span className={`font-display text-lg font-bold uppercase leading-none ${homeLead ? "text-gold" : "text-chalk"}`}>
            {homeCode}
          </span>
        </div>
        <span className="font-display text-2xl font-extrabold tracking-wide text-chalk font-tabular">{score}</span>
        <div className="flex items-center justify-end gap-2.5">
          <span className={`font-display text-lg font-bold uppercase leading-none ${!homeLead ? "text-gold" : "text-chalk"}`}>
            {awayCode}
          </span>
          <CrestPip code={awayCode} variant={!homeLead ? "gold" : "default"} />
        </div>
      </div>

      <SupremacyMeter
        size="mini"
        className="mt-4"
        homeCode={homeCode}
        awayCode={awayCode}
        modelProb={modelShare}
        marketProb={marketShare}
      />

      <div className="mt-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.08em] text-chalk-dim">
        <span>
          desk <span className="font-bold text-gold">{Math.round(modelShare * 100)}%</span>
          {marketShare != null && (
            <>
              {" "}· mkt <span className="font-bold text-sky">{Math.round(marketShare * 100)}%</span>
            </>
          )}
        </span>
        {upset ? (
          <span className="text-coral">{completed ? "result beat the desk" : "market disagrees"}</span>
        ) : (
          fixture.confidence && <span>conf {fixture.confidence}</span>
        )}
      </div>
    </Link>
  );
}
