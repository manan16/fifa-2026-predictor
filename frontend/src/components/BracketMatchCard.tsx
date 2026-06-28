import { Link } from "react-router-dom";
import { BracketFixture } from "../types";
import FootballPulse from "./FootballPulse";
import ProbabilityBar from "./ProbabilityBar";

interface Props {
  fixture: BracketFixture;
}

function formatProbability(value: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

function formatOdds(value: number | null) {
  return value == null ? "-" : value.toFixed(2);
}

function formatKickoff(value: string) {
  if (!value) return "Kickoff TBD";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export default function BracketMatchCard({ fixture }: Props) {
  const homeWins = fixture.predicted_winner === fixture.home_team_name;
  const awayWins = fixture.predicted_winner === fixture.away_team_name;
  const completed = fixture.status === "completed" || fixture.actual_winner != null;
  const actualHomeWins = completed && fixture.actual_winner === fixture.home_team_name;
  const actualAwayWins = completed && fixture.actual_winner === fixture.away_team_name;
  const homeProbability = fixture.home_advance_probability ?? fixture.home_win_probability;
  const awayProbability = fixture.away_advance_probability ?? fixture.away_win_probability;
  const modelWinnerProbability = homeWins ? homeProbability : awayWins ? awayProbability : null;
  const marketWinnerProbability = homeWins
    ? fixture.market_home_probability
    : awayWins
      ? fixture.market_away_probability
      : fixture.market_draw_probability;
  const upset =
    completed &&
    fixture.actual_winner &&
    fixture.predicted_winner !== "TBD" &&
    fixture.predicted_winner !== fixture.actual_winner;

  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="group block w-64 overflow-hidden border border-line/10 bg-gradient-to-br from-stadium/95 via-pitch/70 to-stadium/95 p-3 text-line shadow-broadcast transition duration-300 hover:-translate-y-1 hover:border-gold/70 hover:shadow-gold"
    >
      <div className="mb-3 flex items-center justify-between gap-2 text-[11px] font-bold uppercase text-white/45">
        <span className="flex items-center gap-2">
          <FootballPulse status={fixture.status} />
          Match {fixture.match_number}
        </span>
        <span>{formatKickoff(fixture.kickoff_time)}</span>
      </div>

      <div className={`space-y-2 border-l-4 pl-3 ${homeWins || actualHomeWins ? "border-gold" : "border-white/15"}`}>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className={`font-bold ${homeWins || actualHomeWins ? "text-gold" : "text-white"}`}>{fixture.home_team_name}</p>
            <p className="text-xs text-white/45">{fixture.home_team_code}</p>
          </div>
          <p className="text-sm font-black">{formatProbability(homeProbability)}</p>
        </div>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className={`font-bold ${awayWins || actualAwayWins ? "text-gold" : "text-white"}`}>{fixture.away_team_name}</p>
            <p className="text-xs text-white/45">{fixture.away_team_code}</p>
          </div>
          <p className="text-sm font-black">{formatProbability(awayProbability)}</p>
        </div>
      </div>

      <div className="mt-3 space-y-2 border-t border-white/10 pt-3 text-xs text-white/65">
        <div className="space-y-2">
          <ProbabilityBar label={`Model: ${fixture.predicted_winner}`} value={modelWinnerProbability} variant="model" />
          <ProbabilityBar label={`Market: ${fixture.predicted_winner}`} value={marketWinnerProbability} variant="market" />
        </div>
        <p>
          Predicted: {fixture.home_team_name} {fixture.predicted_home_goals ?? "-"}-
          {fixture.predicted_away_goals ?? "-"} {fixture.away_team_name}
        </p>
        <p>
          Avg odds: {formatOdds(fixture.average_home_odds)} / {formatOdds(fixture.average_draw_odds)} /{" "}
          {formatOdds(fixture.average_away_odds)}
        </p>
        <p>{fixture.bookmaker_count ?? 0} bookmakers · market data, not betting advice</p>
        <p>
          <span className="font-bold text-white">Actual result:</span>{" "}
          {completed
            ? `${fixture.home_team_name} ${fixture.actual_home_score}-${fixture.actual_away_score} ${fixture.away_team_name}${
                fixture.home_penalties != null && fixture.away_penalties != null
                  ? `, ${fixture.actual_winner} won ${fixture.home_penalties}-${fixture.away_penalties} pens`
                  : ""
              }`
            : "Not played yet"}
        </p>
        {upset && (
          <p className="animate-card-in bg-coral/20 px-2 py-1 font-bold text-coral ring-1 ring-coral/30">
            Upset: model picked {fixture.predicted_winner}, actual winner {fixture.actual_winner}
          </p>
        )}
        <span className="inline-flex bg-white/10 px-2 py-1 font-bold text-white">{fixture.confidence ?? "TBD"}</span>
      </div>
    </Link>
  );
}
