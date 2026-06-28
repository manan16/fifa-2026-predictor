import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import ConfidenceBadge from "../components/ConfidenceBadge";
import ProbabilityCard from "../components/ProbabilityCard";
import ProbabilityChart from "../components/ProbabilityChart";
import { getFixture, getPrediction } from "../services/api";
import { Fixture, Prediction } from "../types";

export default function MatchPrediction() {
  const { fixtureId } = useParams();
  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!fixtureId) return;
    Promise.all([getFixture(Number(fixtureId)), getPrediction(Number(fixtureId))])
      .then(([fixtureData, predictionData]) => {
        setFixture(fixtureData);
        setPrediction(predictionData);
      })
      .catch(() => setError("Unable to load this match prediction."));
  }, [fixtureId]);

  if (error) {
    return <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>;
  }

  if (!fixture || !prediction) {
    return <div className="bg-white p-6 shadow-sm">Loading prediction...</div>;
  }

  return (
    <div className="space-y-6">
      <Link to="/fixtures" className="font-semibold text-pitch">
        Back to fixtures
      </Link>

      <section className="bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-bold uppercase text-ink/55">
              {fixture.stage} · Match {fixture.match_number}
            </p>
            <h1 className="mt-3 text-4xl font-black">
              {fixture.home_team_name} vs {fixture.away_team_name}
            </h1>
            <p className="mt-3 text-ink/65">
              {fixture.city} · {fixture.venue}
            </p>
          </div>
          <ConfidenceBadge confidence={prediction.confidence} />
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <ProbabilityCard label={`${fixture.home_team_name} win`} value={prediction.home_win_probability} tone="home" />
        <ProbabilityCard label="Draw" value={prediction.draw_probability} tone="draw" />
        <ProbabilityCard label={`${fixture.away_team_name} win`} value={prediction.away_win_probability} tone="away" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
        <div className="bg-white p-5 shadow-sm">
          <p className="text-sm font-semibold text-ink/60">Predicted scoreline</p>
          <p className="mt-3 text-5xl font-black text-pitch">
            {prediction.predicted_home_goals} - {prediction.predicted_away_goals}
          </p>
          {prediction.home_advance_probability && prediction.away_advance_probability && (
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="bg-sand p-3">
                <p className="font-bold">{fixture.home_team_name} advances</p>
                <p>{Math.round(prediction.home_advance_probability * 100)}%</p>
              </div>
              <div className="bg-sand p-3">
                <p className="font-bold">{fixture.away_team_name} advances</p>
                <p>{Math.round(prediction.away_advance_probability * 100)}%</p>
              </div>
            </div>
          )}
          <h2 className="mt-6 text-lg font-bold">Key factors</h2>
          <ul className="mt-3 space-y-2 text-ink/70">
            {prediction.explanation.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
        <ProbabilityChart
          homeTeam={fixture.home_team_name}
          awayTeam={fixture.away_team_name}
          home={prediction.home_win_probability}
          draw={prediction.draw_probability}
          away={prediction.away_win_probability}
        />
      </section>
    </div>
  );
}

