import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import MatchCentre from "../components/MatchCentre";
import { getFixture, getFixtureOdds, getPrediction } from "../services/api";
import { Fixture, OddsConsensus, Prediction } from "../types";

export default function MatchPrediction() {
  const { fixtureId } = useParams();
  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [consensus, setConsensus] = useState<OddsConsensus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!fixtureId) return;
    const id = Number(fixtureId);
    Promise.all([getFixture(id), getPrediction(id), getFixtureOdds(id)])
      .then(([fixtureData, predictionData, oddsData]) => {
        setFixture(fixtureData);
        setPrediction(predictionData);
        setConsensus(oddsData.consensus);
      })
      .catch(() => setError("Unable to load this match centre."));
  }, [fixtureId]);

  if (error) {
    return <div className="rounded border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>;
  }

  if (!fixture || !prediction) {
    return (
      <div className="rounded border border-line bg-turf/50 p-6 font-mono text-xs uppercase tracking-[0.12em] text-chalk-dim">
        Loading match centre…
      </div>
    );
  }

  return (
    <AnimatedPage className="space-y-5">
      <Link
        to="/fixtures"
        className="inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.12em] text-chalk-dim transition hover:text-gold"
      >
        ‹ Back to fixtures
      </Link>
      <MatchCentre fixture={fixture} prediction={prediction} consensus={consensus} />
      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Model vs market analytics. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
