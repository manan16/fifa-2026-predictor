import FootballPulse from "./FootballPulse";

interface Props {
  stage: string;
  kickoff?: string;
  venue: string;
  city: string;
  status: string;
}

function formatKickoff(value?: string) {
  if (!value) return "Kickoff TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";
  return new Intl.DateTimeFormat("en-GB", { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(date);
}

function formatGmtKickoff(value?: string) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return `${new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" }).format(date)} GMT`;
}

export default function MatchCentreHeader({ stage, kickoff, venue, city, status }: Props) {
  const gmtKickoff = formatGmtKickoff(kickoff);

  return (
    <div className="flex flex-col gap-3 border-b border-white/10 pb-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-xs font-black uppercase tracking-[0.24em] text-yellow-300">Match Centre</p>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs font-bold uppercase tracking-[0.14em] text-slate-300">
          <span className="text-yellow-300">{stage}</span>
          <span>{formatKickoff(kickoff)}{gmtKickoff ? ` / ${gmtKickoff}` : ""}</span>
          <span>{venue}, {city}</span>
          <span className="text-emerald-300">Win or go home</span>
        </div>
      </div>
      <div className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.14em] text-slate-300">
        <FootballPulse status={status} />
        {status}
      </div>
    </div>
  );
}
