import { ActualMatchStats, FixtureMatchStatsResponse } from "../types";
import { statusKind } from "../lib/match";

interface Props {
  homeTeam: string;
  awayTeam: string;
  stats: FixtureMatchStatsResponse | null;
  actualStats?: ActualMatchStats | null;
  hasActualScore?: boolean;
  /** Fixture status string; used to gate actual stats behind a played match. */
  status?: string;
}

type Side = "home" | "away";

function numeric(value: number | null | undefined): number | null {
  return typeof value === "number" && !Number.isNaN(value) ? value : null;
}

/**
 * Head-to-head comparison row. Renders nothing unless at least one side has a
 * value — graceful degradation, a missing metric simply doesn't appear.
 */
function PairedRow({ label, home, away, suffix = "" }: { label: string; home: number | null; away: number | null; suffix?: string }) {
  if (home == null && away == null) return null;
  const homeText = home == null ? "–" : `${home}${suffix}`;
  const awayText = away == null ? "–" : `${away}${suffix}`;
  const homeLead = home != null && away != null && home > away;
  const awayLead = home != null && away != null && away > home;
  return (
    <div className="grid grid-cols-[3rem_1fr_3rem] items-center gap-2 py-1.5 text-sm">
      <span className={`text-right font-black tabular-nums ${homeLead ? "text-gold" : "text-white"}`}>{homeText}</span>
      <span className="text-center font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">{label}</span>
      <span className={`text-left font-black tabular-nums ${awayLead ? "text-sky-300" : "text-white"}`}>{awayText}</span>
    </div>
  );
}

/** Possession as a split bar summing to 100%. Renders nothing if either side absent. */
function PossessionBar({ home, away }: { home: number | null; away: number | null }) {
  if (home == null || away == null) return null;
  const total = home + away;
  const homePct = total > 0 ? Math.round((home / total) * 100) : 50;
  return (
    <div className="py-1.5">
      <div className="mb-1 flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">
        <span className="font-black text-white">{home}%</span>
        <span>Possession</span>
        <span className="font-black text-white">{away}%</span>
      </div>
      <div className="flex h-2 overflow-hidden rounded-full bg-white/10">
        <div className="h-full bg-gradient-to-r from-grass to-gold" style={{ width: `${homePct}%` }} />
        <div className="h-full bg-gradient-to-r from-sky-400 to-line" style={{ width: `${100 - homePct}%` }} />
      </div>
    </div>
  );
}

export default function StatsPanel({ homeTeam, awayTeam, stats, actualStats = null, hasActualScore = false, status = "" }: Props) {
  const home = stats?.home ?? null;
  const away = stats?.away ?? null;

  // Actual stats only mean anything once the match has been played. A scheduled
  // or live fixture must never render numeric rows — otherwise absent data (or a
  // stray all-zero row) reads as a real 0-0 result. Completion is a finished
  // status or a recorded final score.
  const played = statusKind(status) === "done" || hasActualScore;

  const pick = (side: Side, key: keyof NonNullable<typeof home>): number | null => {
    const row = side === "home" ? home : away;
    return row ? numeric(row[key] as number | null) : null;
  };

  const pickActual = (homeKey: keyof ActualMatchStats, awayKey: keyof ActualMatchStats): { home: number | null; away: number | null } => ({
    home: actualStats ? numeric(actualStats[homeKey] as number | null) : null,
    away: actualStats ? numeric(actualStats[awayKey] as number | null) : null
  });

  const shots = home || away ? { home: pick("home", "shots"), away: pick("away", "shots") } : pickActual("home_shots", "away_shots");
  const shotsOnTarget =
    home || away ? { home: pick("home", "shots_on_target"), away: pick("away", "shots_on_target") } : pickActual("home_shots_on_target", "away_shots_on_target");
  const corners = home || away ? { home: pick("home", "corners"), away: pick("away", "corners") } : pickActual("home_corners", "away_corners");
  const yellows =
    home || away ? { home: pick("home", "yellow_cards"), away: pick("away", "yellow_cards") } : pickActual("home_yellow_cards", "away_yellow_cards");
  const reds = home || away ? { home: pick("home", "red_cards"), away: pick("away", "red_cards") } : pickActual("home_red_cards", "away_red_cards");

  const possession =
    home || away ? { home: pick("home", "possession"), away: pick("away", "possession") } : pickActual("home_possession", "away_possession");

  const rows = [
    { label: "Goals", home: home || away ? pick("home", "goals_for") : null, away: home || away ? pick("away", "goals_for") : null, suffix: "" },
    { label: "Shots", home: shots.home, away: shots.away, suffix: "" },
    { label: "On target", home: shotsOnTarget.home, away: shotsOnTarget.away, suffix: "" },
    { label: "Corners", home: corners.home, away: corners.away, suffix: "" },
    { label: "Yellow cards", home: yellows.home, away: yellows.away, suffix: "" },
    { label: "Red cards", home: reds.home, away: reds.away, suffix: "" },
    { label: "xG", home: home || away ? pick("home", "xg") : null, away: home || away ? pick("away", "xg") : null, suffix: "" }
  ];

  const visibleRows = rows.filter((row) => row.home != null || row.away != null);
  const hasPossession = possession.home != null && possession.away != null;
  // Only surface numbers for a played match that actually has stats data.
  const showStats = played && (hasPossession || visibleRows.length > 0);
  const sourceNote = stats?.source_note ?? "Illustrative demo data — synthetic, model-generated. Not official results.";

  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <p className="text-sm font-black uppercase tracking-[0.16em] text-slate-300">Actual match stats</p>
      <div className="mt-3 flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">
        <span className="font-black text-gold">{homeTeam}</span>
        <span className="font-black text-sky-300">{awayTeam}</span>
      </div>
      {showStats ? (
        <div className="mt-2 divide-y divide-white/5">
          <PossessionBar home={possession.home} away={possession.away} />
          {visibleRows.map((row) => (
            <PairedRow key={row.label} label={row.label} home={row.home} away={row.away} suffix={row.suffix} />
          ))}
        </div>
      ) : (
        <p className="mt-4 bg-white/[0.06] p-4 font-bold text-slate-300">
          {played ? "Final score available — detailed match stats not available yet." : "Not available yet — match not played."}
        </p>
      )}
      <p className="mt-4 font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        {sourceNote}
      </p>
    </section>
  );
}
