import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import MatchCentreDetail from "../components/MatchCentreDetail";
import { getFixture, getFixtureOdds, getFixtureStats, getFixtureWatchLinks, getPrediction } from "../services/api";
import { BookmakerOdds, Fixture, FixtureStatsResponse, FixtureWatchResponse, OddsConsensus, Prediction } from "../types";

export default function MatchPrediction() {
  const { fixtureId } = useParams();
  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [bookmakerOdds, setBookmakerOdds] = useState<BookmakerOdds[]>([]);
  const [consensus, setConsensus] = useState<OddsConsensus | null>(null);
  const [stats, setStats] = useState<FixtureStatsResponse | null>(null);
  const [watch, setWatch] = useState<FixtureWatchResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!fixtureId) return;
    const id = Number(fixtureId);
    Promise.all([getFixture(id), getPrediction(id), getFixtureOdds(id), getFixtureStats(id), getFixtureWatchLinks(id)])
      .then(([fixtureData, predictionData, oddsData, statsData, watchData]) => {
        setFixture(fixtureData);
        setPrediction(predictionData);
        setBookmakerOdds(oddsData.odds);
        setConsensus(oddsData.consensus);
        setStats(statsData);
        setWatch(watchData);
      })
      .catch(() => setError("Unable to load this match centre."));
  }, [fixtureId]);

  if (error) {
    return <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>;
  }

  if (!fixture || !prediction) {
    return <div className="border border-white/15 bg-slate-900/80 p-6 text-slate-100 shadow-broadcast">Loading match centre...</div>;
  }

  return (
    <AnimatedPage>
      <MatchCentreDetail
        fixture={fixture}
        prediction={prediction}
        consensus={consensus}
        bookmakerOdds={bookmakerOdds}
        stats={stats}
        watch={watch}
      />
    </AnimatedPage>
  );
}
