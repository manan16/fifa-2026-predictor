import { Link } from "react-router-dom";
import { Fixture } from "../types";
import FootballPulse from "./FootballPulse";

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
  const completed = fixture.status === "completed" || fixture.actual_winner != null;
  const predictedScore =
    fixture.predicted_home_goals != null && fixture.predicted_away_goals != null
      ? `${fixture.predicted_home_goals}-${fixture.predicted_away_goals}`
      : "TBD";

  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="group block overflow-hidden border border-line/10 bg-gradient-to-br from-white/[0.12] to-white/[0.05] p-4 text-line shadow-broadcast transition duration-300 hover:-translate-y-1 hover:border-gold/60 hover:shadow-gold"
    >
      <div className="flex items-center justify-between gap-3">
        <p className="flex items-center gap-2 text-sm font-bold text-line/65">
          <FootballPulse status={fixture.status} />
          {fixture.stage}
        </p>
        <span className="border border-gold/30 bg-gold/10 px-2 py-1 text-xs font-black text-gold">
          Match {fixture.match_number}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <p className="text-lg font-black">{fixture.home_team_name}</p>
        <span className="rounded-full border border-line/15 px-2 py-1 text-xs font-black text-line/55">vs</span>
        <p className="text-right text-lg font-black">{fixture.away_team_name}</p>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="bg-stadium/45 p-3">
          <p className="text-line/45">Predicted</p>
          <p className="text-xl font-black text-gold">{predictedScore}</p>
        </div>
        <div className="bg-stadium/45 p-3">
          <p className="text-line/45">Actual</p>
          <p className="text-xl font-black">{completed ? `${fixture.actual_home_score}-${fixture.actual_away_score}` : "TBD"}</p>
        </div>
      </div>
      <p className="mt-4 text-sm font-bold text-gold">{formatKickoff(fixture.kickoff_time)}</p>
      <p className="mt-1 text-sm text-line/55">
        {fixture.city} · {fixture.venue}
      </p>
    </Link>
  );
}
