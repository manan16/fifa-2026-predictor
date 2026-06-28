import { CSSProperties, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import AlsoTonightCard from "../components/AlsoTonightCard";
import CountUp from "../components/CountUp";
import MatchCentreHero from "../components/MatchCentreHero";
import PitchBackground from "../components/PitchBackground";
import RoadToFinalProgress from "../components/RoadToFinalProgress";
import SyncIndicator from "../components/SyncIndicator";
import { useAutoSync } from "../hooks/useAutoSync";
import { getFixtures, getPredictions } from "../services/api";
import { Fixture, Prediction } from "../types";

const favouriteRankLabel = ["Top knockout favourite", "2nd favourite", "3rd favourite"];
const stageWeight: Record<string, number> = {
  Final: 50,
  "Semi-final": 40,
  "Quarter-final": 30,
  "Round of 16": 20,
  "Round of 32": 10
};

export default function Home() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [error, setError] = useState("");

  // Sync now runs automatically in the background — no button.
  const { status: syncStatus, phase: syncPhase } = useAutoSync();

  useEffect(() => {
    Promise.all([getFixtures(), getPredictions()])
      .then(([fixtureData, predictionData]) => {
        setFixtures(fixtureData);
        setPredictions(predictionData);
      })
      .catch(() => setError("Unable to load dashboard data. Start the backend and seed the database."));
  }, []);

  const favourites = useMemo(
    () =>
      [...predictions]
        .sort(
          (a, b) =>
            Math.max(b.home_win_probability, b.away_win_probability) -
            Math.max(a.home_win_probability, a.away_win_probability)
        )
        .slice(0, 3),
    [predictions]
  );

  const featuredFixture = useMemo(
    () =>
      [...fixtures].sort(
        (a, b) => (stageWeight[b.stage] ?? 0) - (stageWeight[a.stage] ?? 0) || a.match_number - b.match_number
      )[0],
    [fixtures]
  );

  const alsoTonight = useMemo(
    () => fixtures.filter((fixture) => fixture.id !== featuredFixture?.id).slice(0, 3),
    [fixtures, featuredFixture]
  );

  return (
    <AnimatedPage className="mx-auto w-full max-w-[1600px] space-y-8">
      <PitchBackground className="animate-pitch-drift border border-white/10 p-4 shadow-broadcast sm:p-6 xl:p-8">
        <MatchCentreHero fixture={featuredFixture} />
      </PitchBackground>

      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <section className="grid gap-4 xl:grid-cols-[1.1fr_1.6fr]">
        <div className="border border-white/15 bg-slate-900/80 p-5 shadow-broadcast">
          <div>
            <h2 className="text-xl font-black text-white">Data feed</h2>
            <p className="mt-1 text-sm text-slate-300">Odds and results refresh automatically in the background.</p>
          </div>
          <div className="mt-4">
          <SyncIndicator status={syncStatus} phase={syncPhase} />
          </div>
        </div>

        <div>
          <h2 className="mb-4 text-2xl font-black text-white">Also Tonight</h2>
          <div className="grid gap-4 lg:grid-cols-3">
            {alsoTonight.map((fixture) => (
              <AlsoTonightCard key={fixture.id} fixture={fixture} />
            ))}
          </div>
        </div>
      </section>

      <RoadToFinalProgress currentStage={featuredFixture?.stage} />

      <section className="stagger-children grid gap-4 md:grid-cols-3">
        {favourites.map((prediction, index) => {
          const favourite =
            prediction.home_win_probability >= prediction.away_win_probability
              ? prediction.home_team || prediction.home_team_name
              : prediction.away_team || prediction.away_team_name;
          const probability = Math.max(prediction.home_win_probability, prediction.away_win_probability);
          return (
            <div
              key={`${prediction.fixture_id}-${favourite}`}
              className="animate-card-in border border-white/15 bg-slate-900/80 p-5 shadow-broadcast transition hover:-translate-y-1 hover:border-yellow-300/50"
              style={{ "--i": index } as CSSProperties}
            >
              <p className="text-sm font-bold text-slate-300">{favouriteRankLabel[index] ?? "Favourite"}</p>
              <p className="mt-2 text-xl font-black text-white">{favourite}</p>
              <p className="mt-3 text-3xl font-black text-yellow-300">
                <CountUp value={probability} scale={100} suffix="%" />
              </p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["/bracket", "Knockout bracket", "View the full predicted path from Round of 32 to the final."],
          ["/fixtures", "Knockout fixtures", "Browse the demo bracket from Round of 32 through the final."],
          ["/teams", "Teams", "Compare ranking, confederation, and Elo rating inputs."],
          ["/model", "Model info", "Understand assumptions, limitations, and roadmap."]
        ].map(([to, title, text]) => (
          <Link key={to} to={to} className="border border-white/15 bg-emerald-950/80 p-5 text-white shadow-broadcast transition hover:-translate-y-1 hover:border-yellow-300/60">
            <h3 className="text-xl font-black">{title}</h3>
            <p className="mt-2 text-sm text-slate-300">{text}</p>
          </Link>
        ))}
      </section>
    </AnimatedPage>
  );
}
