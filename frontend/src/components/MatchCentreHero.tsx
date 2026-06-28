import { Link } from "react-router-dom";
import { Fixture } from "../types";
import FootballPulse from "./FootballPulse";
import ProbabilityLine from "./ProbabilityLine";
import ScoreDisplay from "./ScoreDisplay";

function formatDate(value?: string) {
  if (!value) return "Kickoff TBC";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kickoff TBC";
  return new Intl.DateTimeFormat("en-GB", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function favourite(fixture: Fixture) {
  const home = fixture.home_win_probability ?? 0;
  const away = fixture.away_win_probability ?? 0;
  return home >= away
    ? {
        name: fixture.home_team_name,
        probability: fixture.home_win_probability,
        market: fixture.market_home_probability,
        odds: fixture.best_home_odds ?? fixture.average_home_odds
      }
    : {
        name: fixture.away_team_name,
        probability: fixture.away_win_probability,
        market: fixture.market_away_probability,
        odds: fixture.best_away_odds ?? fixture.average_away_odds
      };
}

export default function MatchCentreHero({ fixture }: { fixture?: Fixture }) {
  if (!fixture) {
    return (
      <section className="border border-white/15 bg-slate-900/85 p-8 shadow-broadcast">
        <p className="text-sm font-black uppercase text-yellow-300">Match Centre</p>
        <h1 className="mt-3 text-4xl font-black text-white">Simulate the road to the final.</h1>
        <p className="mt-4 text-slate-300">Fixture data is loading from the predictor API.</p>
      </section>
    );
  }

  const pick = favourite(fixture);
  const marketFavourite =
    (fixture.market_home_probability ?? 0) >= (fixture.market_away_probability ?? 0)
      ? fixture.home_team_name
      : fixture.away_team_name;
  const underdogProbability =
    pick.name === fixture.home_team_name ? fixture.away_win_probability : fixture.home_win_probability;

  return (
    <section className="relative overflow-hidden border border-white/15 bg-slate-950/70 p-5 shadow-broadcast sm:p-7 xl:p-9">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(250,204,21,0.14),transparent_34rem)]" />
      <div className="relative">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <p className="flex items-center gap-2 text-sm font-black uppercase text-yellow-300">
              <FootballPulse status={fixture.status} />
              Match of the night · {fixture.stage}
            </p>
            <h1 className="mt-3 text-4xl font-black text-white sm:text-6xl">Simulate the road to the final.</h1>
            <p className="mt-4 max-w-3xl text-lg text-slate-300">
              Compare model prediction, market odds, and actual results across the full tournament bracket.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/bracket" className="bg-yellow-400 px-5 py-3 text-sm font-black text-slate-950 shadow-gold transition hover:-translate-y-0.5">View knockout bracket</Link>
            <Link to="/fixtures" className="border border-white/40 bg-slate-950/40 px-5 py-3 text-sm font-black text-white transition hover:border-yellow-300 hover:text-yellow-300">Browse fixtures</Link>
          </div>
        </div>

        <div className="mt-8 grid gap-6 xl:grid-cols-[1fr_1.2fr_1fr] xl:items-center">
          {[{ name: fixture.home_team_name, code: fixture.home_team_code, elo: fixture.home_team_elo }, { name: fixture.away_team_name, code: fixture.away_team_code, elo: fixture.away_team_elo }].map((team, index) => (
            <div key={team.name} className={`border border-white/10 bg-emerald-950/55 p-5 ${index === 1 ? "xl:text-right" : ""}`}>
              <span className="inline-flex border border-yellow-300/40 bg-yellow-400/10 px-3 py-1 text-xs font-black text-yellow-300">{team.code ?? "TBD"}</span>
              <p className="mt-4 text-4xl font-black text-white">{team.name}</p>
              <p className="mt-2 text-sm text-slate-300">Elo {team.elo ?? "TBD"}</p>
            </div>
          ))}

          <div className="xl:col-start-2 xl:row-start-1">
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
            <p className="mt-4 text-center text-sm text-slate-300">{fixture.stage} · {formatDate(fixture.kickoff_time)} · {fixture.venue}, {fixture.city}</p>
          </div>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <div className="border border-white/10 bg-slate-900/70 p-4">
            <ProbabilityLine
              leftLabel={`Model ${pick.name}`}
              rightLabel="Underdog"
              leftProbability={pick.probability}
              rightProbability={underdogProbability}
              marketProbability={pick.market}
            />
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
            <div className="bg-white/10 p-3"><p className="text-slate-400">MODEL PICK</p><p className="mt-1 font-black text-white">{pick.name}</p></div>
            <div className="bg-white/10 p-3"><p className="text-slate-400">MARKET FAVOURS</p><p className="mt-1 font-black text-blue-300">{marketFavourite}</p></div>
            <div className="bg-white/10 p-3"><p className="text-slate-400">CONFIDENCE</p><p className="mt-1 font-black text-yellow-300">{fixture.confidence ?? "TBD"}</p></div>
            <div className="bg-white/10 p-3"><p className="text-slate-400">BEST MARKET ODDS</p><p className="mt-1 font-black text-white">{pick.odds?.toFixed(2) ?? "-"}</p></div>
          </div>
        </div>
        <p className="mt-4 text-xs text-slate-400">Model vs market analytics for demonstration. Not betting advice.</p>
      </div>
    </section>
  );
}
