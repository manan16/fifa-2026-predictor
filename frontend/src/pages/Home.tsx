import { CSSProperties, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import CountUp from "../components/CountUp";
import MatchCard from "../components/MatchCard";
import PitchBackground from "../components/PitchBackground";
import SyncIndicator from "../components/SyncIndicator";
import { useAutoSync } from "../hooks/useAutoSync";
import { getFixtures, getPredictions } from "../services/api";
import { Fixture, Prediction } from "../types";

const favouriteRankLabel = ["Top knockout favourite", "2nd favourite", "3rd favourite"];

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

  return (
    <AnimatedPage className="space-y-8">
      <PitchBackground className="animate-pitch-drift rounded-none border border-line/10 p-6 shadow-broadcast sm:p-8">
        <section className="grid gap-8 md:grid-cols-[1.45fr_0.9fr] md:items-center">
          <div>
            <p className="text-sm font-black uppercase tracking-normal text-gold">World Cup 2026 knockout analytics</p>
            <h1 className="mt-4 text-4xl font-black tracking-normal sm:text-6xl">
              Simulate the road to the final.
            </h1>
            <p className="mt-5 max-w-2xl text-lg text-line/72">
              Compare model prediction, market odds, and actual results across the full tournament bracket.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link to="/bracket" className="bg-gold px-5 py-3 text-sm font-black text-stadium shadow-gold transition hover:-translate-y-0.5">
                View knockout bracket
              </Link>
              <Link to="/fixtures" className="border border-line/20 bg-line/10 px-5 py-3 text-sm font-black text-line transition hover:border-gold/70">
                Browse fixtures
              </Link>
            </div>
          </div>
          <div className="border border-line/10 bg-stadium/45 p-5 shadow-broadcast">
            <p className="text-sm font-black uppercase text-line/55">Road to the Final</p>
            <div className="mt-5 space-y-3">
              {["Round of 32", "Round of 16", "Quarter-finals", "Semi-finals", "Final"].map((round, index) => (
                <div key={round} className="flex items-center gap-3">
                  <span className="grid h-8 w-8 place-items-center rounded-full border border-gold/40 bg-gold/10 text-xs font-black text-gold">
                    {index + 1}
                  </span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-line/10">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-grass to-gold animate-bar-fill"
                      style={{ width: `${100 - index * 13}%`, animationDelay: `${index * 90}ms` }}
                    />
                  </div>
                  <span className="w-28 text-right text-xs font-bold text-line/70">{round}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </PitchBackground>

      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <section className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-black text-line">Data feed</h2>
            <p className="mt-1 text-sm text-line/60">Odds and results refresh automatically in the background.</p>
          </div>
          <SyncIndicator status={syncStatus} phase={syncPhase} />
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-black text-line">Opening knockout ties</h2>
          <Link to="/fixtures" className="font-bold text-gold">
            View bracket fixtures
          </Link>
        </div>
        <div className="stagger-children grid gap-4 md:grid-cols-2">
          {fixtures.slice(0, 4).map((fixture, index) => (
            <div key={fixture.id} className="animate-card-in" style={{ "--i": index } as CSSProperties}>
              <MatchCard fixture={fixture} />
            </div>
          ))}
        </div>
      </section>

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
              className="animate-card-in border border-line/10 bg-line/[0.06] p-5 shadow-broadcast transition hover:-translate-y-1 hover:border-gold/40"
              style={{ "--i": index } as CSSProperties}
            >
              <p className="text-sm font-bold text-line/55">{favouriteRankLabel[index] ?? "Favourite"}</p>
              <p className="mt-2 text-xl font-black text-line">{favourite}</p>
              <p className="mt-3 text-3xl font-black text-gold">
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
          <Link key={to} to={to} className="border border-line/10 bg-pitch/80 p-5 text-line shadow-broadcast transition hover:-translate-y-1 hover:border-gold/60">
            <h3 className="text-xl font-black">{title}</h3>
            <p className="mt-2 text-sm text-line/70">{text}</p>
          </Link>
        ))}
      </section>
    </AnimatedPage>
  );
}