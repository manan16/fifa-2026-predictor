import { CSSProperties, useEffect, useMemo, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import CrestPip from "../components/CrestPip";
import { getTeams } from "../services/api";
import { Team } from "../types";

export default function Teams() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getTeams()
      .then(setTeams)
      .catch(() => setError("Unable to load teams."));
  }, []);

  const { ranked, scale } = useMemo(() => {
    const sorted = [...teams].sort((a, b) => b.elo_rating - a.elo_rating);
    const elos = sorted.map((t) => t.elo_rating);
    const max = Math.max(...elos, 1);
    const min = Math.min(...elos, 0);
    const avg = elos.length ? elos.reduce((s, v) => s + v, 0) / elos.length : 0;
    // Pad the low end so even the weakest nation shows a visible bar.
    const lo = min - (max - min) * 0.25;
    const pct = (v: number) => Math.max(4, Math.min(100, ((v - lo) / (max - lo)) * 100));
    return { ranked: sorted, scale: { width: pct, avg: pct(avg) } };
  }, [teams]);

  return (
    <AnimatedPage className="space-y-6">
      <header className="pt-2">
        <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
          Strength board
          <span className="h-px w-14 bg-line" />
        </p>
        <h1 className="mt-3 font-display text-[clamp(30px,5vw,46px)] font-extrabold uppercase leading-[0.95] text-chalk">
          Power ranking
        </h1>
        <p className="mt-2.5 max-w-[560px] text-chalk-dim">
          The inputs behind every prediction — blended Elo and FIFA ranking, by nation. The chalk tick marks
          the field average.
        </p>
      </header>

      {error && <div className="rounded border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <div className="overflow-hidden rounded border border-line">
        <div className="grid grid-cols-[40px_1fr_70px] items-center gap-3.5 bg-turf2/60 px-4 py-3 font-mono text-[10px] uppercase tracking-[0.12em] text-chalk-dim sm:grid-cols-[54px_1fr_120px_1fr_80px] sm:px-[18px]">
          <span>Rank</span>
          <span>Nation</span>
          <span className="hidden sm:block">Confederation</span>
          <span className="hidden sm:block">Elo strength</span>
          <span className="text-right">FIFA</span>
        </div>

        {ranked.map((team, index) => {
          const top = index === 0;
          return (
            <div
              key={team.id}
              className={`animate-tie-pop grid grid-cols-[40px_1fr_70px] items-center gap-3.5 border-t border-line px-4 py-3 sm:grid-cols-[54px_1fr_120px_1fr_80px] sm:px-[18px] ${
                top ? "bg-gold/[0.05]" : ""
              }`}
              style={{ animationDelay: `${index * 0.04}s` } as CSSProperties}
            >
              <span
                className={`font-display text-[26px] font-extrabold leading-none font-tabular ${
                  top ? "text-gold" : "text-chalk-dim"
                }`}
              >
                {index + 1}
              </span>
              <div className="flex min-w-0 items-center gap-3">
                <CrestPip code={team.fifa_code} variant={top ? "gold" : "default"} className="h-10 w-9 text-[11px]" />
                <span className="truncate font-display text-[19px] font-bold uppercase text-chalk">{team.name}</span>
              </div>
              <span className="hidden justify-self-start rounded-sm border border-line px-2 py-1 font-mono text-[10px] uppercase tracking-[0.08em] text-chalk-dim sm:block">
                {team.confederation}
              </span>
              <div className="hidden items-center gap-3 sm:flex">
                <span className="w-[42px] font-mono text-xs font-bold font-tabular">{team.elo_rating}</span>
                <div className="relative h-1.5 flex-1 overflow-visible rounded-[3px] bg-chalk-faint">
                  <span
                    className="animate-bar-fill absolute inset-0 rounded-[3px]"
                    style={{
                      width: `${scale.width(team.elo_rating)}%`,
                      background: "linear-gradient(90deg,#6ec2ff,#f4c430)"
                    }}
                  />
                  <span
                    className="absolute -top-1 -bottom-1 w-0.5 bg-chalk/50"
                    style={{ left: `${scale.avg}%` }}
                    title="Field average"
                  />
                </div>
              </div>
              <span className="justify-self-end font-mono text-[13px] font-bold font-tabular text-chalk">
                {team.fifa_ranking}
              </span>
            </div>
          );
        })}
      </div>

      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Blended ratings. Field average across all {ranked.length || 0} knockout nations.
      </p>
    </AnimatedPage>
  );
}
