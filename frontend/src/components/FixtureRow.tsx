import { Link } from "react-router-dom";
import { Fixture } from "../types";
import SupremacyMeter from "./SupremacyMeter";
import { favouritesDisagree, shortCode, statusKind, twoWayShare } from "../lib/match";

function kickoffTime(value?: string): string {
  if (!value) return "TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "TBC";
  return `${new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" }).format(date)} GMT`;
}

export default function FixtureRow({ fixture }: { fixture: Fixture }) {
  const homeName = fixture.home_team_name;
  const awayName = fixture.away_team_name;
  const homeCode = shortCode(fixture.home_team_code, homeName);
  const awayCode = shortCode(fixture.away_team_code, awayName);
  const modelShare = twoWayShare(fixture.home_win_probability, fixture.away_win_probability);
  const marketShare =
    fixture.market_home_probability != null || fixture.market_away_probability != null
      ? twoWayShare(fixture.market_home_probability, fixture.market_away_probability)
      : null;
  const kind = statusKind(fixture.status);
  const homeLead = modelShare >= 0.5;
  const completed = kind === "done";

  const dotClass =
    kind === "live"
      ? "live-dot text-coral"
      : kind === "scheduled"
        ? "live-dot text-gold"
        : "inline-block h-2 w-2 rounded-full bg-chalk-faint";
  const statusLabel = kind === "live" ? "Live" : completed ? "FT" : kickoffTime(fixture.kickoff_time);

  const venue = [fixture.venue, fixture.city].filter(Boolean).join(", ");
  const resultUpset =
    completed && fixture.actual_winner != null && fixture.predicted_winner != null
      ? fixture.predicted_winner !== fixture.actual_winner
      : false;
  const metaExtra = completed
    ? fixture.actual_home_score != null
      ? ` · ${fixture.actual_home_score}–${fixture.actual_away_score}${resultUpset ? " · result beat the desk" : ""}`
      : ""
    : favouritesDisagree(modelShare, marketShare)
      ? " · upset watch"
      : "";

  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="animate-tie-pop mb-2.5 flex items-center gap-4 rounded border border-line bg-turf/45 px-4 py-3.5 transition hover:-translate-y-0.5 hover:border-gold/40 hover:shadow-broadcast"
    >
      <div className="flex w-[72px] flex-none flex-col items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.08em] text-chalk-dim">
        <span className={dotClass} style={{ backgroundColor: "currentColor" }} />
        {statusLabel}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2.5 font-display text-[17px] font-bold uppercase">
          <span className={homeLead ? "text-gold" : "text-chalk"}>{homeName}</span>
          <span className="font-mono text-xs text-chalk-dim">v</span>
          <span className={!homeLead ? "text-gold" : "text-chalk"}>{awayName}</span>
        </div>
        <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.06em] text-chalk-dim">
          {venue || "Venue TBC"}
          {metaExtra}
        </div>
      </div>

      <div className="hidden w-[150px] flex-none sm:block">
        <div className="flex justify-between font-mono text-[11px] font-bold font-tabular">
          <span className="text-gold">desk {Math.round(modelShare * 100)}%</span>
          {marketShare != null && <span className="text-sky">mkt {Math.round(marketShare * 100)}%</span>}
        </div>
        <SupremacyMeter
          size="mini"
          className="mt-1.5"
          homeCode={homeCode}
          awayCode={awayCode}
          modelProb={modelShare}
          marketProb={marketShare}
        />
      </div>

      <span className="flex-none font-mono text-base text-chalk-dim">›</span>
    </Link>
  );
}
