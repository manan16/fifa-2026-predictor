import { FixtureMatchStatsResponse } from "../types";

interface Props {
  homeTeam: string;
  awayTeam: string;
  stats: FixtureMatchStatsResponse | null;
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

export default function StatsPanel({ homeTeam, awayTeam, stats }: Props) {
  const home = stats?.home ?? null;
  const away = stats?.away ?? null;
  if (!home && !away) return null;

  const pick = (side: Side, key: keyof NonNullable<typeof home>): number | null => {
    const row = side === "home" ? home : away;
    return row ? numeric(row[key] as number | null) : null;
  };

  const possessionHome = pick("home", "possession");
  const possessionAway = pick("away", "possession");

  const rows = [
    { label: "Goals", home: pick("home", "goals_for"), away: pick("away", "goals_for"), suffix: "" },
    { label: "Shots", home: pick("home", "shots"), away: pick("away", "shots"), suffix: "" },
    { label: "On target", home: pick("home", "shots_on_target"), away: pick("away", "shots_on_target"), suffix: "" },
    { label: "Corners", home: pick("home", "corners"), away: pick("away", "corners"), suffix: "" },
    { label: "Yellow cards", home: pick("home", "yellow_cards"), away: pick("away", "yellow_cards"), suffix: "" },
    { label: "Red cards", home: pick("home", "red_cards"), away: pick("away", "red_cards"), suffix: "" },
    { label: "xG", home: pick("home", "xg"), away: pick("away", "xg"), suffix: "" }
  ];

  const visibleRows = rows.filter((row) => row.home != null || row.away != null);
  const hasPossession = possessionHome != null && possessionAway != null;
  if (!hasPossession && visibleRows.length === 0) return null;

  return (
    <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
      <p className="text-sm font-black uppercase tracking-[0.16em] text-slate-300">Match stats</p>
      <div className="mt-3 flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">
        <span className="font-black text-gold">{homeTeam}</span>
        <span className="font-black text-sky-300">{awayTeam}</span>
      </div>
      <div className="mt-2 divide-y divide-white/5">
        <PossessionBar home={possessionHome} away={possessionAway} />
        {visibleRows.map((row) => (
          <PairedRow key={row.label} label={row.label} home={row.home} away={row.away} suffix={row.suffix} />
        ))}
      </div>
      <p className="mt-4 font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Stats via Wikipedia (CC BY-SA).
      </p>
    </section>
  );
}
