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
  const [consensus, setConsensus] = useState<OddsConsensus | null>(null);
  const [bookmakerOdds, setBookmakerOdds] = useState<BookmakerOdds[]>([]);
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
        setConsensus(oddsData.consensus);
        setBookmakerOdds(oddsData.odds);
        setStats(statsData);
        setWatch(watchData);
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
      <MatchCentreDetail
        fixture={fixture}
        prediction={prediction}
        consensus={consensus}
        bookmakerOdds={bookmakerOdds}
        stats={stats}
        watch={watch}
      />
      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Model vs market analytics. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
