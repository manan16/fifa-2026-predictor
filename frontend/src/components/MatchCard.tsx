import { Link } from "react-router-dom";
import { Fixture } from "../types";

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
  return (
    <Link
      to={`/fixtures/${fixture.id}`}
      className="block border border-ink/10 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold text-ink/60">{fixture.stage}</p>
        <span className="bg-pitch/10 px-2 py-1 text-xs font-bold text-pitch">
          Match {fixture.match_number}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <p className="text-lg font-bold">{fixture.home_team_name}</p>
        <span className="text-sm font-semibold text-ink/45">vs</span>
        <p className="text-right text-lg font-bold">{fixture.away_team_name}</p>
      </div>
      <p className="mt-4 text-sm font-semibold text-pitch">{formatKickoff(fixture.kickoff_time)}</p>
      <p className="mt-1 text-sm text-ink/60">
        {fixture.city} · {fixture.venue}
      </p>
    </Link>
  );
}
