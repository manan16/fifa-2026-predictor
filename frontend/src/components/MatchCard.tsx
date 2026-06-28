import { Link } from "react-router-dom";
import { Fixture } from "../types";
import FootballPulse from "./FootballPulse";
import ScoreDisplay from "./ScoreDisplay";

function formatKickoff(value?: string) {
  if (!value) return "Kickoff TBC";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export default function MatchCard({ fixture }: { fixture: Fixture }) {
  const homeModel = fixture.home_win_probability ?? 0;
  const awayModel = fixture.away_win_probability ?? 0;
  const modelFavourite = homeModel >= awayModel ? fixture.home_team_name : fixture.away_team_name;
  const modelProbability = Math.max(homeModel, awayModel);
  const marketFavourite =
    (fixture.market_home_probability ?? 0) >= (fixture.market_away_probability ?? 0)
      ? fixture.home_team_name
      : fixture.away_team_name;
  const hasStats =
    fixture.home_shots != null &&
    fixture.away_shots != null &&
    fixture.home_possession != null &&
    fixture.away_possession != null;

  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="group block overflow-hidden border border-white/15 bg-slate-900/85 p-4 text-slate-100 shadow-broadcast transition duration-300 hover:-translate-y-1 hover:border-yellow-300/60 hover:shadow-yellow-500/10"
    >
      <div className="flex items-center justify-between gap-3">
        <p className="flex items-center gap-2 text-sm font-bold text-emerald-300">
          <FootballPulse status={fixture.status} />
          {fixture.stage}
        </p>
        <span className="border border-yellow-300/40 bg-yellow-400/10 px-2 py-1 text-xs font-black text-yellow-300">
          Match {fixture.match_number}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <p className="text-lg font-black text-white">{fixture.home_team_name}</p>
        <span className="rounded-full border border-white/40 px-2 py-1 text-xs font-black text-white">vs</span>
        <p className="text-right text-lg font-black text-white">{fixture.away_team_name}</p>
      </div>
      <div className="mt-4 bg-stadium/45 p-3">
        <ScoreDisplay
          homeTeam={fixture.home_team_name}
          awayTeam={fixture.away_team_name}
          predictedHome={fixture.predicted_home_goals}
          predictedAway={fixture.predicted_away_goals}
          actualHome={fixture.actual_home_score}
          actualAway={fixture.actual_away_score}
          homePenalties={fixture.home_penalties}
          awayPenalties={fixture.away_penalties}
          actualWinner={fixture.actual_winner}
          status={fixture.status}
        />
      </div>
      <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
        <div className="bg-white/10 p-2">
          <p className="text-slate-400">Model favourite</p>
          <p className="font-black text-white">{modelProbability ? `${modelFavourite} ${Math.round(modelProbability * 100)}%` : "Prediction loading"}</p>
        </div>
        <div className="bg-white/10 p-2">
          <p className="text-slate-400">Market favours</p>
          <p className="font-black text-blue-300">{fixture.market_home_probability || fixture.market_away_probability ? marketFavourite : "Market loading"}</p>
        </div>
      </div>
      {hasStats && (
        <div className="mt-3 grid grid-cols-3 gap-2 border-t border-white/10 pt-3 text-xs">
          <div>
            <p className="text-slate-400">Shots</p>
            <p className="font-black text-white">{fixture.home_shots}-{fixture.away_shots}</p>
          </div>
          <div>
            <p className="text-slate-400">SOT</p>
            <p className="font-black text-white">{fixture.home_shots_on_target}-{fixture.away_shots_on_target}</p>
          </div>
          <div>
            <p className="text-slate-400">Poss</p>
            <p className="font-black text-white">{fixture.home_possession}%/{fixture.away_possession}%</p>
          </div>
        </div>
      )}
      <p className="mt-4 text-sm font-bold text-yellow-300">{formatKickoff(fixture.kickoff_time)}</p>
      <p className="mt-1 text-sm text-slate-300">
        {fixture.city} · {fixture.venue}
      </p>
    </Link>
  );
}
