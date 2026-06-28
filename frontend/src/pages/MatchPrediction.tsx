import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import AnimatedPage from "../components/AnimatedPage";
import ConfidenceBadge from "../components/ConfidenceBadge";
import FootballPulse from "../components/FootballPulse";
import PitchBackground from "../components/PitchBackground";
import ProbabilityBar from "../components/ProbabilityBar";
import { getFixture, getFixtureOdds, getPrediction } from "../services/api";
import { BookmakerOdds, Fixture, OddsConsensus, Prediction } from "../types";

function percent(value: number | null | undefined) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

function odds(value: number | null | undefined) {
  return value == null ? "-" : value.toFixed(2);
}

export default function MatchPrediction() {
  const { fixtureId } = useParams();
  const [fixture, setFixture] = useState<Fixture | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [bookmakerOdds, setBookmakerOdds] = useState<BookmakerOdds[]>([]);
  const [consensus, setConsensus] = useState<OddsConsensus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!fixtureId) return;
    Promise.all([getFixture(Number(fixtureId)), getPrediction(Number(fixtureId)), getFixtureOdds(Number(fixtureId))])
      .then(([fixtureData, predictionData, oddsData]) => {
        setFixture(fixtureData);
        setPrediction(predictionData);
        setBookmakerOdds(oddsData.odds);
        setConsensus(oddsData.consensus);
      })
      .catch(() => setError("Unable to load this match prediction."));
  }, [fixtureId]);

  if (error) {
    return <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>;
  }

  if (!fixture || !prediction) {
    return <div className="bg-white p-6 shadow-sm">Loading prediction...</div>;
  }

  const completed = fixture.status === "completed" || fixture.actual_winner != null;
  const modelFavourite =
    prediction.home_win_probability >= prediction.away_win_probability ? fixture.home_team_name : fixture.away_team_name;
  const marketFavourite =
    consensus && (consensus.home_probability ?? 0) >= (consensus.away_probability ?? 0)
      ? fixture.home_team_name
      : fixture.away_team_name;
  const modelMarketMessage = consensus
    ? modelFavourite === marketFavourite
      ? `Model and market both lean toward ${modelFavourite}.`
      : `Model favours ${modelFavourite}, while the market favours ${marketFavourite}.`
    : "Market consensus is not available yet.";
  const oddsByBookmaker = bookmakerOdds.reduce<Record<string, Partial<Record<BookmakerOdds["outcome_type"], BookmakerOdds>>>>(
    (acc, item) => {
      acc[item.bookmaker] = acc[item.bookmaker] ?? {};
      acc[item.bookmaker][item.outcome_type] = item;
      return acc;
    },
    {}
  );

  return (
    <AnimatedPage className="space-y-6">
      <Link to="/fixtures" className="font-bold text-gold">
        Back to fixtures
      </Link>

      <PitchBackground className="p-6 shadow-broadcast">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="flex items-center gap-2 text-sm font-black uppercase text-line/55">
              <FootballPulse status={fixture.status} />
              {fixture.stage} · Match {fixture.match_number}
            </p>
            <h1 className="mt-3 text-4xl font-black">
              {fixture.home_team_name} vs {fixture.away_team_name}
            </h1>
            <p className="mt-3 text-line/65">
              {fixture.city} · {fixture.venue}
            </p>
          </div>
          <ConfidenceBadge confidence={prediction.confidence} />
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="bg-stadium/50 p-4">
            <p className="text-xs font-bold uppercase text-line/50">Predicted score</p>
            <p className="mt-2 text-4xl font-black text-gold">{prediction.predicted_home_goals} - {prediction.predicted_away_goals}</p>
          </div>
          <div className="bg-stadium/50 p-4">
            <p className="text-xs font-bold uppercase text-line/50">Actual score</p>
            <p className="mt-2 text-4xl font-black">{completed ? `${fixture.actual_home_score} - ${fixture.actual_away_score}` : "TBD"}</p>
          </div>
          <div className="bg-stadium/50 p-4">
            <p className="text-xs font-bold uppercase text-line/50">Status</p>
            <p className="mt-2 text-2xl font-black text-line">{fixture.status}</p>
          </div>
        </div>
      </PitchBackground>

      <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
        <div className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
          <p className="text-sm font-black uppercase text-line/60">Model prediction</p>
          <div className="mt-5 space-y-4">
            <ProbabilityBar label={`${fixture.home_team_name} win`} value={prediction.home_win_probability} variant="model" />
            <ProbabilityBar label="Draw" value={prediction.draw_probability} variant="blended" />
            <ProbabilityBar label={`${fixture.away_team_name} win`} value={prediction.away_win_probability} variant="model" />
          </div>
          {prediction.home_advance_probability && prediction.away_advance_probability && (
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="bg-stadium/50 p-3 text-line">
                <p className="font-bold">{fixture.home_team_name} advances</p>
                <p>{Math.round(prediction.home_advance_probability * 100)}%</p>
              </div>
              <div className="bg-stadium/50 p-3 text-line">
                <p className="font-bold">{fixture.away_team_name} advances</p>
                <p>{Math.round(prediction.away_advance_probability * 100)}%</p>
              </div>
            </div>
          )}
          <h2 className="mt-6 text-lg font-bold text-line">Key factors</h2>
          <ul className="mt-3 space-y-2 text-line/70">
            {prediction.explanation.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
        <div className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
          <h2 className="text-lg font-black text-line">Market odds</h2>
          <p className="mt-3 text-sm text-line/55">Market data for analytics only, not betting advice.</p>
          <div className="mt-5 space-y-4">
            <ProbabilityBar label="Market home" value={consensus?.home_probability} variant="market" />
            <ProbabilityBar label="Market draw" value={consensus?.draw_probability} variant="market" />
            <ProbabilityBar label="Market away" value={consensus?.away_probability} variant="market" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <div className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
          <h2 className="text-lg font-black text-line">Actual Result</h2>
          <p className="mt-3 text-line/70">
            {completed
              ? `${fixture.home_team_name} ${fixture.actual_home_score}-${fixture.actual_away_score} ${fixture.away_team_name}`
              : "Actual: Not played yet"}
          </p>
          {fixture.home_penalties != null && fixture.away_penalties != null && (
            <p className="mt-2 text-ink/70">
              Penalties: {fixture.home_penalties}-{fixture.away_penalties}
            </p>
          )}
          <p className="mt-2 text-sm text-line/55">Status: {fixture.status}</p>
          <p className="mt-2 font-bold text-line">Actual winner: {fixture.actual_winner ?? "TBD"}</p>
        </div>

        <div className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
          <h2 className="text-lg font-black text-line">Average Odds</h2>
          <p className="mt-3 text-sm text-line/55">Market data for analytics only, not betting advice.</p>
          <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
            <div className="bg-stadium/50 p-3 text-line">
              <p className="font-bold">Home</p>
              <p>{percent(consensus?.home_probability)}</p>
              <p>{odds(consensus?.average_home_odds)}</p>
            </div>
            <div className="bg-stadium/50 p-3 text-line">
              <p className="font-bold">Draw</p>
              <p>{percent(consensus?.draw_probability)}</p>
              <p>{odds(consensus?.average_draw_odds)}</p>
            </div>
            <div className="bg-stadium/50 p-3 text-line">
              <p className="font-bold">Away</p>
              <p>{percent(consensus?.away_probability)}</p>
              <p>{odds(consensus?.average_away_odds)}</p>
            </div>
          </div>
          <p className="mt-3 text-sm text-line/60">{consensus?.bookmaker_count ?? 0} bookmakers</p>
        </div>

        <div className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
          <h2 className="text-lg font-black text-line">Model vs Market</h2>
          <p className="mt-3 text-line/70">{modelMarketMessage}</p>
          <p className="mt-4 text-sm text-line/55">
            Best odds: {odds(consensus?.best_home_odds)} / {odds(consensus?.best_draw_odds)} /{" "}
            {odds(consensus?.best_away_odds)}
          </p>
        </div>
      </section>

      <section className="border border-line/10 bg-line/[0.06] p-5 shadow-broadcast">
        <h2 className="text-lg font-black text-line">Bookmaker Table</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="bg-pitch text-line">
              <tr>
                <th className="px-3 py-2">Bookmaker</th>
                <th className="px-3 py-2">Home odds</th>
                <th className="px-3 py-2">Draw odds</th>
                <th className="px-3 py-2">Away odds</th>
                <th className="px-3 py-2">Last updated</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(oddsByBookmaker).map(([bookmaker, row]) => (
                <tr key={bookmaker} className="border-b border-line/10 text-line/75">
                  <td className="px-3 py-2 font-bold">{bookmaker}</td>
                  <td className="px-3 py-2">{odds(row.home?.decimal_price)}</td>
                  <td className="px-3 py-2">{odds(row.draw?.decimal_price)}</td>
                  <td className="px-3 py-2">{odds(row.away?.decimal_price)}</td>
                  <td className="px-3 py-2">{row.home?.last_update ?? row.draw?.last_update ?? row.away?.last_update ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AnimatedPage>
  );
}
