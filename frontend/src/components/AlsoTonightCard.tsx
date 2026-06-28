import { Link } from "react-router-dom";
import { Fixture } from "../types";
import ProbabilityBar from "./ProbabilityBar";

function favourite(fixture: Fixture) {
  const home = fixture.home_win_probability ?? 0;
  const away = fixture.away_win_probability ?? 0;
  return home >= away
    ? { name: fixture.home_team_name, probability: home, market: fixture.market_home_probability }
    : { name: fixture.away_team_name, probability: away, market: fixture.market_away_probability };
}

export default function AlsoTonightCard({ fixture }: { fixture: Fixture }) {
  const pick = favourite(fixture);
  const marketDisagrees = pick.market != null && Math.abs((pick.probability ?? 0) - pick.market) >= 0.08;

  return (
    <Link to={`/fixtures/${fixture.id}`} className="block border border-white/15 bg-slate-900/85 p-4 shadow-broadcast transition hover:-translate-y-1 hover:border-yellow-300/60">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-black uppercase text-emerald-300">{fixture.stage}</p>
        {marketDisagrees && <span className="bg-orange-500/15 px-2 py-1 text-[10px] font-black uppercase text-orange-300">Model edge</span>}
      </div>
      <p className="mt-3 text-lg font-black text-white">{pick.name}</p>
      <p className="text-sm text-slate-300">vs {pick.name === fixture.home_team_name ? fixture.away_team_name : fixture.home_team_name}</p>
      <div className="mt-4">
        <ProbabilityBar label="Model probability" value={pick.probability} />
      </div>
    </Link>
  );
}

