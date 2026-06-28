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
      className="group block w-72 overflow-hidden border border-white/15 bg-slate-900/90 p-4 text-slate-100 shadow-broadcast transition duration-300 hover:-translate-y-1 hover:border-yellow-300/60 hover:shadow-yellow-500/10"
    >
      <div className="mb-3 flex items-center justify-between gap-2 text-[11px] font-bold uppercase text-slate-300">
        <span className="flex items-center gap-2">
          <FootballPulse status={fixture.status} />
          Match {fixture.match_number}
        </span>
        <span>{formatKickoff(fixture.kickoff_time)}</span>
      </div>

      <p className="mb-3 text-xs font-black uppercase text-emerald-300">{fixture.stage}</p>
      <div className={`space-y-2 border-l-4 pl-3 ${homeWins || actualHomeWins ? "border-yellow-400 bg-yellow-400/10 py-2 pr-2" : "border-white/15"}`}>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className={`font-bold ${homeWins || actualHomeWins ? "text-yellow-300" : "text-white"}`}>{fixture.home_team_name}</p>
            <p className="text-xs text-slate-400">{fixture.home_team_code}</p>
          </div>
          <p className="text-sm font-black text-white">{formatProbability(homeProbability)}</p>
        </div>
      </div>

      <div className={`space-y-2 border-l-4 pl-3 ${awayWins || actualAwayWins ? "border-yellow-400 bg-yellow-400/10 py-2 pr-2" : "border-white/15"}`}>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className={`font-bold ${awayWins || actualAwayWins ? "text-yellow-300" : "text-white"}`}>{fixture.away_team_name}</p>
            <p className="text-xs text-slate-400">{fixture.away_team_code}</p>
          </div>
          <p className="text-sm font-black text-white">{formatProbability(awayProbability)}</p>
        </div>
      </div>

      <div className="mt-3 space-y-2 border-t border-white/10 pt-3 text-xs text-slate-300">
        <div className="space-y-2">
          <ProbabilityBar label={`Model: ${fixture.predicted_winner}`} value={modelWinnerProbability} variant="model" />
          <ProbabilityBar label={`Market: ${fixture.predicted_winner}`} value={marketWinnerProbability} variant="market" />
        </div>
        <p>
          Predicted: {fixture.home_team_name} {fixture.predicted_home_goals ?? "-"}-
          {fixture.predicted_away_goals ?? "-"} {fixture.away_team_name}
        </p>
        {fixture.home_shots != null && fixture.away_shots != null && (
          <p>
            Stats preview: shots {fixture.home_shots}-{fixture.away_shots}, corners {fixture.home_corners ?? "-"}-
            {fixture.away_corners ?? "-"}
          </p>
        )}
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
        <span className="inline-flex bg-white/10 px-2 py-1 font-bold text-white ring-1 ring-white/10">{fixture.confidence ?? "TBD"}</span>
      </div>
    </Link>
  );
}
