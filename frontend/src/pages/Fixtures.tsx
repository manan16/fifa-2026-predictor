import { useEffect, useMemo, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import FixtureRow from "../components/FixtureRow";
import { statusKind } from "../lib/match";
import { getFixtures } from "../services/api";
import { Fixture } from "../types";

function isCompleted(fixture: Fixture): boolean {
  return (
    statusKind(fixture.status) === "done" ||
    (fixture.actual_home_score != null && fixture.actual_away_score != null)
  );
}

function groupByStage(fixtures: Fixture[]) {
  const order: string[] = [];
  const map = new Map<string, Fixture[]>();
  fixtures.forEach((fixture) => {
    if (!map.has(fixture.stage)) {
      map.set(fixture.stage, []);
      order.push(fixture.stage);
    }
    map.get(fixture.stage)!.push(fixture);
  });
  return order.map((key) => [key, map.get(key)!] as const);
}

export default function Fixtures() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [stage, setStage] = useState("All");
  const [error, setError] = useState("");

  useEffect(() => {
    getFixtures()
      .then(setFixtures)
      .catch(() => setError("Unable to load fixtures."));
  }, []);

  const stages = useMemo(
    () => ["All", ...Array.from(new Set(fixtures.map((fixture) => fixture.stage)))],
    [fixtures]
  );
  const filtered = stage === "All" ? fixtures : fixtures.filter((fixture) => fixture.stage === stage);
  const completedGroups = useMemo(() => groupByStage(filtered.filter(isCompleted)), [filtered]);
  const upcomingGroups = useMemo(() => groupByStage(filtered.filter((fixture) => !isCompleted(fixture))), [filtered]);

  return (
    <AnimatedPage className="space-y-6">
      <header className="pt-2">
        <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
          Matchday board
          <span className="h-px w-14 bg-line" />
        </p>
        <h1 className="mt-3 font-display text-[clamp(30px,5vw,46px)] font-extrabold uppercase leading-[0.95] text-chalk">
          Knockout fixtures
        </h1>
        <p className="mt-2.5 max-w-[560px] text-chalk-dim">
          Every tie on the schedule, with the desk's pick and the market line on each. Filter by round; tap a
          match for the full read.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        {stages.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setStage(item)}
            className={`rounded-sm border px-3.5 py-2 font-mono text-[11px] uppercase tracking-[0.1em] transition ${
              stage === item
                ? "border-gold bg-gold font-bold text-pitch"
                : "border-line text-chalk-dim hover:border-gold/40 hover:text-chalk"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {error && <div className="rounded border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <section>
        <div className="mb-3 mt-5 flex flex-wrap items-end justify-between gap-2 border-b border-line pb-2">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-gold">Completed</p>
            <p className="mt-1 text-sm text-chalk-dim">Final scores and completed knockout ties.</p>
          </div>
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-chalk-dim">{filtered.filter(isCompleted).length} matches</span>
        </div>
        {completedGroups.length > 0 ? (
          completedGroups.map(([stageName, rows]) => (
            <section key={`completed-${stageName}`}>
              <p className="mb-2.5 mt-4 font-mono text-[11px] uppercase tracking-[0.16em] text-chalk-dim">{stageName}</p>
              {rows.map((fixture) => (
                <FixtureRow key={fixture.id} fixture={fixture} />
              ))}
            </section>
          ))
        ) : (
          <p className="rounded border border-line bg-turf/35 p-4 font-mono text-xs uppercase tracking-[0.1em] text-chalk-dim">
            No completed fixtures yet.
          </p>
        )}
      </section>

      <section>
        <div className="mb-3 mt-7 flex flex-wrap items-end justify-between gap-2 border-b border-line pb-2">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-gold">Upcoming</p>
            <p className="mt-1 text-sm text-chalk-dim">Scheduled and live fixtures still to be decided.</p>
          </div>
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-chalk-dim">{filtered.filter((fixture) => !isCompleted(fixture)).length} matches</span>
        </div>
        {upcomingGroups.length > 0 ? (
          upcomingGroups.map(([stageName, rows]) => (
            <section key={`upcoming-${stageName}`}>
              <p className="mb-2.5 mt-4 font-mono text-[11px] uppercase tracking-[0.16em] text-chalk-dim">{stageName}</p>
              {rows.map((fixture) => (
                <FixtureRow key={fixture.id} fixture={fixture} />
              ))}
            </section>
          ))
        ) : (
          <p className="rounded border border-line bg-turf/35 p-4 font-mono text-xs uppercase tracking-[0.1em] text-chalk-dim">
            No upcoming fixtures for this filter.
          </p>
        )}
      </section>

      {!error && fixtures.length === 0 && (
        <p className="font-mono text-xs uppercase tracking-[0.12em] text-chalk-dim">Loading fixtures…</p>
      )}

      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Kickoff times shown in GMT. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
