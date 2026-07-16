import { Link } from "react-router-dom";
import { BookmakerOdds, Fixture, FixtureMatchStatsResponse, FixtureStatsResponse, FixtureWatchResponse, OddsConsensus, Prediction } from "../types";
import MatchCentreHeader from "./MatchCentreHeader";
import MarketSummaryCard from "./MarketSummaryCard";
import PredictedStatsPanel from "./PredictedStatsPanel";
import ProbabilityTugOfWar from "./ProbabilityTugOfWar";
import ScoreDisplay from "./ScoreDisplay";
import StatsComparisonTable from "./StatsComparisonTable";
import StatsPanel from "./StatsPanel";
import TeamPanel from "./TeamPanel";
import WhereToWatchCard from "./WhereToWatchCard";

interface Props {
  fixture: Fixture;
  prediction: Prediction;
  consensus: OddsConsensus | null;
  bookmakerOdds: BookmakerOdds[];
  stats: FixtureStatsResponse | null;
  matchStats: FixtureMatchStatsResponse | null;
  watch: FixtureWatchResponse | null;
}

export default function MatchCentreDetail({ fixture, prediction, consensus, bookmakerOdds, stats, matchStats, watch }: Props) {
  const modelFavourite = prediction.home_win_probability >= prediction.away_win_probability ? fixture.home_team_name : fixture.away_team_name;
  const marketFavourite = (consensus?.home_probability ?? 0) >= (consensus?.away_probability ?? 0) ? fixture.home_team_name : fixture.away_team_name;
  const hasActualScore = fixture.actual_home_score != null && fixture.actual_away_score != null;
  const modelMarketMessage = consensus
    ? modelFavourite === marketFavourite
      ? `Model and market both lean toward ${modelFavourite}.`
      : `Model favours ${modelFavourite}, while the market favours ${marketFavourite}.`
    : "Market consensus is not available yet.";

  return (
    <div className="mx-auto w-full max-w-[1500px] space-y-6">
      <Link to="/fixtures" className="font-bold text-yellow-300">Back to fixtures</Link>

      <section className="relative overflow-hidden border border-white/15 bg-[linear-gradient(180deg,rgba(18,42,30,0.94),rgba(7,17,31,0.96))] p-5 shadow-broadcast sm:p-8">
        <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-30" viewBox="0 0 1000 360" preserveAspectRatio="none" aria-hidden="true">
          <line x1="500" y1="0" x2="500" y2="360" stroke="white" strokeOpacity="0.22" />
          <circle cx="500" cy="180" r="70" fill="none" stroke="white" strokeOpacity="0.22" />
          <path d="M0 78 L130 78 L130 282 L0 282" fill="none" stroke="white" strokeOpacity="0.22" />
          <path d="M1000 78 L870 78 L870 282 L1000 282" fill="none" stroke="white" strokeOpacity="0.22" />
        </svg>
        <div className="relative">
          <MatchCentreHeader stage={fixture.stage} kickoff={fixture.kickoff_time} venue={fixture.venue} city={fixture.city} status={fixture.status} />
          <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_auto_1fr] lg:items-center">
            <TeamPanel side="home" name={fixture.home_team_name} code={fixture.home_team_code} ranking={fixture.home_team_ranking} elo={fixture.home_team_elo} />
            <ScoreDisplay
              homeTeam={fixture.home_team_name}
              awayTeam={fixture.away_team_name}
              predictedHome={prediction.predicted_home_goals}
              predictedAway={prediction.predicted_away_goals}
              actualHome={fixture.actual_home_score}
              actualAway={fixture.actual_away_score}
              homePenalties={fixture.home_penalties}
              awayPenalties={fixture.away_penalties}
              actualWinner={fixture.actual_winner}
              status={fixture.status}
            />
            <TeamPanel side="away" name={fixture.away_team_name} code={fixture.away_team_code} ranking={fixture.away_team_ranking} elo={fixture.away_team_elo} />
          </div>
          <ProbabilityTugOfWar
            homeLabel={fixture.home_team_code ?? fixture.home_team_name}
            awayLabel={fixture.away_team_code ?? fixture.away_team_name}
            homeProbability={prediction.home_advance_probability ?? prediction.home_win_probability}
            awayProbability={prediction.away_advance_probability ?? prediction.away_win_probability}
            marketHomeProbability={consensus?.home_probability}
          />
          <div className="mt-5 flex flex-wrap gap-2 text-xs font-black uppercase tracking-wide">
            <span className="border border-yellow-300/40 bg-yellow-400/10 px-3 py-2 text-yellow-300">Model pick {modelFavourite}</span>
            <span className="border border-sky-300/40 bg-sky-400/10 px-3 py-2 text-sky-300">Market favours {marketFavourite}</span>
            <span className="border border-white/15 bg-white/10 px-3 py-2 text-white">Confidence {prediction.confidence}</span>
            <span className="border border-white/15 bg-white/10 px-3 py-2 text-white">Best market odds {consensus?.best_home_odds?.toFixed(2) ?? "-"}</span>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
          <p className="text-sm font-black uppercase tracking-[0.16em] text-slate-300">Prediction Summary</p>
          <h2 className="mt-2 text-2xl font-black text-white">MODEL CALL: {modelFavourite}</h2>
          <p className="mt-3 text-slate-300">{modelMarketMessage}</p>
          <ul className="mt-4 space-y-2 text-slate-300">{prediction.explanation.map((item) => <li key={item}>• {item}</li>)}</ul>
        </section>
        <MarketSummaryCard prediction={prediction} consensus={consensus} message={modelMarketMessage} />
      </section>

      <StatsPanel
        homeTeam={fixture.home_team_name}
        awayTeam={fixture.away_team_name}
        stats={matchStats}
        actualStats={stats?.actual ?? stats?.actual_stats ?? null}
        hasActualScore={hasActualScore}
      />
      <PredictedStatsPanel homeTeam={fixture.home_team_name} awayTeam={fixture.away_team_name} stats={stats?.predicted ?? stats?.predicted_stats ?? null} />
      <StatsComparisonTable predicted={stats?.predicted ?? stats?.predicted_stats ?? null} actual={stats?.actual ?? stats?.actual_stats ?? null} />

      <section className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <WhereToWatchCard links={watch?.links ?? []} />
        <section className="border border-white/15 bg-slate-900/85 p-5 shadow-broadcast">
          <h2 className="text-lg font-black text-white">Market line by bookmaker</h2>
          <p className="mt-2 text-sm text-slate-300">Market data is shown for analytics only. Not betting advice.</p>
          <div className="mt-4 grid gap-2 text-sm md:grid-cols-2 xl:grid-cols-3">
            {bookmakerOdds.slice(0, 9).map((item) => (
              <div key={`${item.bookmaker}-${item.outcome_type}`} className="bg-white/[0.06] p-3">
                <p className="font-black text-white">{item.bookmaker}</p>
                <p className="text-slate-300">{item.outcome_type}: {item.decimal_price?.toFixed(2) ?? "-"}</p>
              </div>
            ))}
          </div>
        </section>
      </section>
    </div>
  );
}
