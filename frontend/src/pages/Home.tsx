import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import ChampionFunnel from "../components/ChampionFunnel";
import EdgeTicker, { EdgeItem } from "../components/EdgeTicker";
import SyncIndicator from "../components/SyncIndicator";
import { useAutoSync } from "../hooks/useAutoSync";
import { getBracket, getFixtures } from "../services/api";
import { BracketFixture, BracketResponse, Fixture } from "../types";
import { favouritesDisagree, shortCode, twoWayShare } from "../lib/match";

const emptyBracket: BracketResponse = {
  round_of_32: [],
  round_of_16: [],
  quarter_finals: [],
  semi_finals: [],
  final: []
};

function winnerCode(f: BracketFixture): string {
  const homeAdv = f.home_advance_probability ?? 0;
  const awayAdv = f.away_advance_probability ?? 0;
  return homeAdv >= awayAdv ? f.home_team_code : f.away_team_code;
}

const pillars = [
  {
    accent: "border-t-gold",
    kClass: "text-gold",
    k: "The model",
    h: "Our read",
    p: "Elo blended with FIFA ranking, a supremacy-and-Poisson scoreline, and a Dixon-Coles draw correction. Transparent enough to argue with."
  },
  {
    accent: "border-t-sky",
    kClass: "text-sky",
    k: "The market",
    h: "The crowd's read",
    p: "Live bookmaker consensus, de-margined into clean probabilities. The market's number sits next to ours on every single tie."
  },
  {
    accent: "border-t-coral",
    kClass: "text-coral",
    k: "The upsets",
    h: "Where they part",
    p: "Every match where the desk and the market disagree, flagged — so you know which favourites are shakier than the price suggests."
  }
];

export default function Home() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [bracket, setBracket] = useState<BracketResponse>(emptyBracket);
  const [error, setError] = useState("");

  const { status: syncStatus, phase: syncPhase } = useAutoSync();

  useEffect(() => {
    Promise.all([getFixtures(), getBracket()])
      .then(([fixtureData, bracketData]) => {
        setFixtures(fixtureData);
        setBracket(bracketData);
      })
      .catch(() => setError("Unable to load the desk. Start the backend and seed the database."));
  }, []);

  const funnel = useMemo(() => {
    const rows = [bracket.round_of_16, bracket.quarter_finals, bracket.semi_finals]
      .map((round) => round.map(winnerCode).filter(Boolean))
      .filter((row) => row.length > 0);
    const champion =
      bracket.final[0] != null
        ? winnerCode(bracket.final[0])
        : bracket.semi_finals[0] != null
          ? winnerCode(bracket.semi_finals[0])
          : "";
    return { rows, champion };
  }, [bracket]);

  const edges = useMemo<EdgeItem[]>(
    () =>
      fixtures
        .filter((f) => f.market_home_probability != null && f.home_win_probability != null)
        .map((f) => {
          const model = twoWayShare(f.home_win_probability, f.away_win_probability);
          const market = twoWayShare(f.market_home_probability, f.market_away_probability);
          return {
            homeCode: shortCode(f.home_team_code, f.home_team_name),
            awayCode: shortCode(f.away_team_code, f.away_team_name),
            edge: Math.round((model - market) * 100),
            disagree: favouritesDisagree(model, market)
          };
        })
        .sort((a, b) => Math.abs(b.edge) - Math.abs(a.edge))
        .slice(0, 10),
    [fixtures]
  );

  const nations = new Set(
    fixtures.flatMap((f) => [f.home_team_name, f.away_team_name]).filter(Boolean)
  ).size;

  return (
    <AnimatedPage>
      <section className="grid items-center gap-10 py-8 md:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
            World Cup 2026 · knockout desk
            <span className="h-px w-14 bg-line" />
          </p>
          <h1 className="mt-4 font-display text-[clamp(40px,6.4vw,76px)] font-extrabold uppercase leading-[0.9] text-chalk">
            Every tie,
            <br />
            called <span className="text-gold">two ways.</span>
          </h1>
          <p className="mt-5 max-w-[460px] text-[17px] leading-relaxed text-chalk-dim">
            A transparent prediction model and the live betting market, side by side — from the Round of
            32 to the final at MetLife. See where the desk and the market disagree, and where the upsets
            hide.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              to="/bracket"
              className="rounded-sm bg-gold px-5 py-3 font-mono text-[13px] font-bold uppercase tracking-[0.08em] text-pitch transition hover:-translate-y-0.5 hover:shadow-broadcast"
            >
              Open the bracket
            </Link>
            <Link
              to="/model"
              className="rounded-sm border border-line px-5 py-3 font-mono text-[13px] uppercase tracking-[0.08em] text-chalk transition hover:border-gold/50"
            >
              How the model works
            </Link>
          </div>
          <div className="mt-7 flex gap-7 font-mono text-xs tracking-[0.06em] text-chalk-dim">
            <span>
              <b className="font-bold text-chalk">{nations || 32}</b> nations
            </span>
            <span>
              <b className="font-bold text-chalk">{fixtures.length || 31}</b> knockout ties
            </span>
            <span>
              <b className="font-bold text-chalk">2</b> reads per match
            </span>
          </div>
        </div>

        <div className="order-first md:order-none">
          {funnel.champion ? (
            <ChampionFunnel rows={funnel.rows} champion={funnel.champion} />
          ) : (
            <div className="grid min-h-[340px] place-items-center rounded border border-line bg-turf/40 font-mono text-xs uppercase tracking-[0.12em] text-chalk-dim">
              Building the road to the champion…
            </div>
          )}
        </div>
      </section>

      {error && <div className="mb-6 rounded border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <div className="-mx-5">
        <EdgeTicker items={edges} />
      </div>

      <section className="grid gap-4 pt-14 md:grid-cols-3">
        {pillars.map((pillar) => (
          <div
            key={pillar.k}
            className={`rounded border border-line border-t-[3px] ${pillar.accent} bg-turf/40 p-6`}
          >
            <span className={`font-mono text-[11px] uppercase tracking-[0.16em] ${pillar.kClass}`}>
              {pillar.k}
            </span>
            <h3 className="mb-2.5 mt-2.5 font-display text-2xl font-bold uppercase text-chalk">{pillar.h}</h3>
            <p className="text-[15px] leading-relaxed text-chalk-dim">{pillar.p}</p>
          </div>
        ))}
      </section>

      <section className="mt-12 grid gap-4 md:grid-cols-[1.6fr_1fr]">
        <div className="relative overflow-hidden rounded border border-line bg-gradient-to-b from-turf/80 to-turf2/90 p-12 text-center">
          <div className="font-display text-[clamp(28px,4.5vw,46px)] font-extrabold uppercase leading-[0.95] text-chalk">
            Win or go home.
            <br />
            <span className="text-gold">See the whole bracket.</span>
          </div>
          <p className="mx-auto mt-3.5 max-w-[460px] text-chalk-dim">
            Thirty-one ties from the Round of 32 to the final. One predicted path to the trophy.
          </p>
          <Link
            to="/bracket"
            className="mt-6 inline-block rounded-sm bg-gold px-6 py-3.5 font-mono text-[13px] font-bold uppercase tracking-[0.08em] text-pitch transition hover:-translate-y-0.5 hover:shadow-broadcast"
          >
            Open the bracket
          </Link>
        </div>
        <div className="rounded border border-line bg-turf/40 p-6">
          <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-chalk-dim">Data feed</p>
          <p className="mt-1 text-sm text-chalk-dim">
            Odds and results refresh automatically in the background.
          </p>
          <div className="mt-4">
            <SyncIndicator status={syncStatus} phase={syncPhase} />
          </div>
        </div>
      </section>

      <footer className="mt-10 flex flex-wrap justify-between gap-2.5 border-t border-line pt-6 font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        <span>Matchnight · World Cup 2026 knockout desk</span>
        <span>Model vs market analytics. Not betting advice.</span>
      </footer>
    </AnimatedPage>
  );
}
