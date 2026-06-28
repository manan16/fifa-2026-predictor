import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import MatchCard from "../components/MatchCard";
import { getFixtures, getPredictions } from "../services/api";
import { Fixture, Prediction } from "../types";

export default function Home() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [error, setError] = useState("");

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
    <div className="space-y-8">
      <section className="grid gap-6 md:grid-cols-[1.5fr_1fr] md:items-end">
        <div>
          <p className="text-sm font-bold uppercase tracking-normal text-coral">World Cup 2026 knockout analytics</p>
          <h1 className="mt-3 text-4xl font-black tracking-normal sm:text-5xl">
            Predict the full knockout bracket from Round of 32 to the final.
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-ink/70">
            Explore the demo bracket fixtures, compare Elo-style win probabilities, and inspect why the MVP model leans toward each knockout pick.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {[
            ["Teams", "32"],
            ["Fixtures", "31"],
            ["Bracket", "v1"]
          ].map(([label, value]) => (
            <div key={label} className="bg-white p-4 text-center shadow-sm">
              <p className="text-2xl font-black text-pitch">{value}</p>
              <p className="text-xs font-bold uppercase text-ink/55">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Opening knockout ties</h2>
          <Link to="/fixtures" className="font-semibold text-pitch">
            View bracket fixtures
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {fixtures.slice(0, 4).map((fixture) => (
            <MatchCard key={fixture.id} fixture={fixture} />
          ))}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {favourites.map((prediction) => {
          const favourite =
            prediction.home_win_probability >= prediction.away_win_probability
              ? prediction.home_team || prediction.home_team_name
              : prediction.away_team || prediction.away_team_name;
          const probability = Math.max(prediction.home_win_probability, prediction.away_win_probability);
          return (
            <div key={`${prediction.fixture_id}-${favourite}`} className="bg-white p-5 shadow-sm">
              <p className="text-sm font-semibold text-ink/60">Strongest knockout favourite</p>
              <p className="mt-2 text-xl font-bold">{favourite}</p>
              <p className="mt-3 text-3xl font-black text-pitch">{Math.round(probability * 100)}%</p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ["/fixtures", "Knockout fixtures", "Browse the demo bracket from Round of 32 through the final."],
          ["/teams", "Teams", "Compare ranking, confederation, and Elo rating inputs."],
          ["/model", "Model info", "Understand assumptions, limitations, and roadmap."]
        ].map(([to, title, text]) => (
          <Link key={to} to={to} className="bg-pitch p-5 text-white shadow-sm hover:bg-pitch/90">
            <h3 className="text-xl font-bold">{title}</h3>
            <p className="mt-2 text-sm text-white/80">{text}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
