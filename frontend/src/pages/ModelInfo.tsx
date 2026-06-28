import { CSSProperties, useEffect, useMemo, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import ScoreHeatmap from "../components/ScoreHeatmap";
import { getFixtures } from "../services/api";
import { Fixture } from "../types";
import { shortCode } from "../lib/match";

const pipeline = [
  { n: "01 · Inputs", h: "Ratings", p: "Live Elo blended with FIFA ranking for each nation." },
  { n: "02 · Strength", h: "The gap", p: "One strength number per side; the difference drives everything." },
  { n: "03 · Goals", h: "Supremacy", p: "The gap becomes expected-goal supremacy over a stage-aware total." },
  { n: "04 · Grid", h: "Poisson + DC", p: "A score grid with a Dixon-Coles correction for low-scoring draws." },
  { n: "05 · Output", h: "Probabilities", p: "Win, draw, advance — then optionally blended toward the market." }
];

const ignores = [
  "Live squads, injuries and suspensions",
  "Rest days, travel and altitude",
  "Tactical matchups and game state",
  "In-tournament form and momentum"
];

const stageWeight: Record<string, number> = {
  Final: 50,
  "Semi-final": 40,
  "Quarter-final": 30,
  "Round of 16": 20,
  "Round of 32": 10
};

export default function ModelInfo() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);

  useEffect(() => {
    getFixtures()
      .then(setFixtures)
      .catch(() => setFixtures([]));
  }, []);

  // Illustrate the score grid with a real fixture that has expected goals.
  const sample = useMemo(() => {
    const withXg = fixtures.filter(
      (f) =>
        (f.expected_home_goals ?? f.predicted_home_goals) != null &&
        (f.expected_away_goals ?? f.predicted_away_goals) != null
    );
    const best = withXg.sort((a, b) => (stageWeight[b.stage] ?? 0) - (stageWeight[a.stage] ?? 0))[0];
    if (!best) return { homeXg: 1.8, awayXg: 1.2, homeCode: "HOME", awayCode: "AWAY" };
    return {
      homeXg: best.expected_home_goals ?? best.predicted_home_goals ?? 1.8,
      awayXg: best.expected_away_goals ?? best.predicted_away_goals ?? 1.2,
      homeCode: shortCode(best.home_team_code, best.home_team_name),
      awayCode: shortCode(best.away_team_code, best.away_team_name)
    };
  }, [fixtures]);

  return (
    <AnimatedPage className="space-y-6">
      <header className="pt-2">
        <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
          How the desk thinks
          <span className="h-px w-14 bg-line" />
        </p>
        <h1 className="mt-3 font-display text-[clamp(30px,5vw,46px)] font-extrabold uppercase leading-[0.95] text-chalk">
          The model
        </h1>
        <p className="mt-2.5 max-w-[560px] text-chalk-dim">
          A transparent pipeline you can argue with — every step is a deliberate, inspectable choice, not a
          black box.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-2.5 md:grid-cols-5">
        {pipeline.map((stage, index) => (
          <div
            key={stage.n}
            className="animate-tie-pop rounded border border-line border-t-[3px] border-t-gold bg-turf/40 px-3.5 py-4"
            style={{ animationDelay: `${0.05 + index * 0.15}s` } as CSSProperties}
          >
            <span className="font-mono text-[10px] tracking-[0.12em] text-gold">{stage.n}</span>
            <h4 className="mb-1.5 mt-2 font-display text-[17px] font-bold uppercase text-chalk">{stage.h}</h4>
            <p className="text-[13px] leading-snug text-chalk-dim">{stage.p}</p>
          </div>
        ))}
      </div>

      <div className="grid items-start gap-[18px] md:grid-cols-[1.1fr_0.9fr]">
        <ScoreHeatmap
          homeXg={sample.homeXg}
          awayXg={sample.awayXg}
          homeCode={sample.homeCode}
          awayCode={sample.awayCode}
        />

        <div>
          <h4 className="mb-3 font-display text-[19px] font-bold uppercase text-chalk">What it ignores</h4>
          <ul className="list-none p-0">
            {ignores.map((item) => (
              <li
                key={item}
                className="relative border-b border-line py-2.5 pl-[22px] text-sm text-chalk-dim before:absolute before:left-0 before:font-bold before:text-coral before:content-['×']"
              >
                {item}
              </li>
            ))}
          </ul>
          <div className="mt-[18px] rounded border border-gold/30 bg-gold/[0.06] px-4 py-3.5">
            <b className="font-display uppercase tracking-[0.02em] text-chalk">On the roadmap</b>
            <p className="mt-1.5 text-[13px] text-chalk-dim">
              xG-based features, historical-match training, Brier-score evaluation, and Monte Carlo bracket
              simulation.
            </p>
          </div>
        </div>
      </div>

      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Baseline supremacy-and-Poisson model with a Dixon-Coles correction. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
