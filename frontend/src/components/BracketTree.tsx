import { CSSProperties } from "react";
import { BracketFixture, BracketResponse } from "../types";
import CrestPip from "./CrestPip";
import SupremacyMeter from "./SupremacyMeter";
import { favouritesDisagree, shortCode, twoWayShare } from "../lib/match";

interface Derived {
  homeCode: string;
  awayCode: string;
  modelShare: number;
  marketShare: number | null;
  homeWins: boolean;
  upset: boolean;
}

function derive(f: BracketFixture): Derived {
  const homeAdv = f.home_advance_probability;
  const awayAdv = f.away_advance_probability;
  const modelShare =
    homeAdv != null && awayAdv != null
      ? twoWayShare(homeAdv, awayAdv)
      : twoWayShare(f.home_win_probability, f.away_win_probability);
  const marketShare =
    f.market_home_probability != null || f.market_away_probability != null
      ? twoWayShare(f.market_home_probability, f.market_away_probability)
      : null;
  const resultUpset =
    f.actual_winner != null && f.predicted_winner != null && f.actual_winner !== f.predicted_winner;
  return {
    homeCode: shortCode(f.home_team_code, f.home_team_name),
    awayCode: shortCode(f.away_team_code, f.away_team_name),
    modelShare,
    marketShare,
    homeWins: modelShare >= 0.5,
    upset: resultUpset || favouritesDisagree(modelShare, marketShare)
  };
}

function Side({ code, pct, win }: { code: string; pct: number; win: boolean }) {
  return (
    <div
      className={`flex items-center justify-between gap-1.5 py-0.5 font-display text-[13px] font-bold uppercase ${
        win ? "text-gold" : "text-chalk"
      }`}
    >
      <span>{code}</span>
      <span className={`font-mono text-[11px] font-bold font-tabular ${win ? "text-gold" : "text-chalk-dim"}`}>
        {pct}
      </span>
    </div>
  );
}

export function Tie({ f, delay = 0 }: { f: BracketFixture; delay?: number }) {
  const d = derive(f);
  const homePct = Math.round(d.modelShare * 100);
  return (
    <div
      className="animate-tie-pop my-1.5 rounded-sm border border-line bg-turf2/70 px-2 py-1.5"
      style={{ animationDelay: `${delay}s` } as CSSProperties}
    >
      <Side code={d.homeCode} pct={homePct} win={d.homeWins} />
      <SupremacyMeter
        size="mini"
        className="my-1.5"
        homeCode={d.homeCode}
        awayCode={d.awayCode}
        modelProb={d.modelShare}
        marketProb={d.marketShare}
      />
      <Side code={d.awayCode} pct={100 - homePct} win={!d.homeWins} />
      {d.upset && (
        <span className="mt-0.5 inline-block font-mono text-[8px] uppercase tracking-[0.1em] text-coral">
          market disagrees
        </span>
      )}
    </div>
  );
}

// Pin each tie to the 8-row coordinate system the CONNECTORS array assumes:
// span=2 (R16) → centers at 12.5/37.5/62.5/87.5%, span=4 (QF) → 25/75%,
// span=8 (SF) → 50%. Content is centered within its row span so extra-height
// cards (e.g. a "market disagrees" badge) grow around the center, not off it.
function Column({ ties, span, delayBase }: {
  ties: BracketFixture[];
  span: number;
  delayBase: number;
}) {
  return (
    <div className="z-10 grid px-1.5" style={{ gridTemplateRows: "repeat(8, 1fr)" }}>
      {ties.map((f, i) => (
        <div
          key={f.id}
          className="flex flex-col justify-center"
          style={{ gridRow: `${i * span + 1} / span ${span}` }}
        >
          <Tie f={f} delay={delayBase + i * 0.08} />
        </div>
      ))}
    </div>
  );
}

// Round labels rendered in a separate header row (one per grid column) so their
// height can never shift the tie vertical positions below. Index 3 (champion
// column) is intentionally blank.
const ROUND_LABELS = ["Round of 16", "Quarter", "Semi", "", "Semi", "Quarter", "Round of 16"];

// Elbow connectors generated for the symmetric 4→2→1 tree (viewBox 0..100).
const CONNECTORS = [
  // R16L -> QFL
  { d: "M13,12.5 H17.8 V25 H21", band: 1 },
  { d: "M13,37.5 H17.8 V25 H21", band: 1 },
  { d: "M13,62.5 H17.8 V75 H21", band: 1 },
  { d: "M13,87.5 H17.8 V75 H21", band: 1 },
  // QFL -> SFL
  { d: "M27,25 H32 V50 H35", band: 2 },
  { d: "M27,75 H32 V50 H35", band: 2 },
  // SFL -> FINAL
  { d: "M41,50 H49", band: 3 },
  // R16R -> QFR
  { d: "M87,12.5 H82.2 V25 H79", band: 1 },
  { d: "M87,37.5 H82.2 V25 H79", band: 1 },
  { d: "M87,62.5 H82.2 V75 H79", band: 1 },
  { d: "M87,87.5 H82.2 V75 H79", band: 1 },
  // QFR -> SFR
  { d: "M73,25 H68 V50 H65", band: 2 },
  { d: "M73,75 H68 V50 H65", band: 2 },
  // SFR -> FINAL
  { d: "M59,50 H51", band: 3 }
];

export default function BracketTree({ bracket }: { bracket: BracketResponse }) {
  const r16 = bracket.round_of_16;
  const qf = bracket.quarter_finals;
  const sf = bracket.semi_finals;
  const finalTie = bracket.final[0];

  // Prefer the explicit Left/Right bracket labels; fall back to halves.
  const split = (arr: BracketFixture[]) => {
    const left = arr.filter((f) => (f.group_name ?? "").toLowerCase().includes("left"));
    const right = arr.filter((f) => (f.group_name ?? "").toLowerCase().includes("right"));
    if (left.length && right.length) return [left, right] as const;
    const mid = Math.ceil(arr.length / 2);
    return [arr.slice(0, mid), arr.slice(mid)] as const;
  };
  const [r16L, r16R] = split(r16);
  const [qfL, qfR] = split(qf);
  const [sfL, sfR] = split(sf);

  const championCode = finalTie ? derive(finalTie).homeWins
    ? shortCode(finalTie.home_team_code, finalTie.home_team_name)
    : shortCode(finalTie.away_team_code, finalTie.away_team_name)
    : "";
  const championName = finalTie
    ? derive(finalTie).homeWins
      ? finalTie.home_team_name
      : finalTie.away_team_name
    : "";

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[860px]">
        <div className="grid grid-cols-7">
          {ROUND_LABELS.map((label, i) => (
            <div
              key={i}
              className="px-1.5 pb-1.5 text-center font-mono text-[9px] uppercase tracking-[0.12em] text-chalk-dim"
            >
              {label}
            </div>
          ))}
        </div>
        <div className="relative grid min-h-[460px] grid-cols-7">
          <svg
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            className="pointer-events-none absolute inset-0 h-full w-full"
            aria-hidden="true"
          >
            {CONNECTORS.map((c, i) => (
              <path
                key={i}
                data-chalk
                d={c.d}
                fill="none"
                stroke="#ecf4ed"
                strokeWidth={0.35}
                opacity={0.2}
                className="animate-chalk-draw"
                style={{ strokeDasharray: 60, strokeDashoffset: 60, animationDelay: `${0.2 + c.band * 0.3}s` }}
              />
            ))}
          </svg>

          <Column ties={r16L} span={2} delayBase={0.1} />
          <Column ties={qfL} span={4} delayBase={0.3} />
          <Column ties={sfL} span={8} delayBase={0.5} />
          <div className="z-10 flex flex-col items-center justify-center px-1.5">
            {championCode && (
              <div className="text-center">
                <span className="mb-2 block font-mono text-[9px] uppercase tracking-[0.16em] text-gold">
                  Predicted champion
                </span>
                <span className="animate-ignite inline-block" style={{ animationDelay: "1.1s" }}>
                  <CrestPip code={championCode} variant="gold" className="mx-auto h-[74px] w-16 text-lg" />
                </span>
                <div className="mt-2.5 font-display text-lg font-extrabold uppercase text-chalk">{championName}</div>
              </div>
            )}
          </div>
          <Column ties={sfR} span={8} delayBase={0.5} />
          <Column ties={qfR} span={4} delayBase={0.3} />
          <Column ties={r16R} span={2} delayBase={0.1} />
        </div>
      </div>
    </div>
  );
}
