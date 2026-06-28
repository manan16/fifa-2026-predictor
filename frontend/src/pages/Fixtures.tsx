import { useEffect, useMemo, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import FixtureRow from "../components/FixtureRow";
import { getFixtures } from "../services/api";
import { Fixture } from "../types";

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

  // Preserve stage order as it first appears in the data, then group.
  const grouped = useMemo(() => {
    const order: string[] = [];
    const map = new Map<string, Fixture[]>();
    filtered.forEach((fixture) => {
      if (!map.has(fixture.stage)) {
        map.set(fixture.stage, []);
        order.push(fixture.stage);
      }
      map.get(fixture.stage)!.push(fixture);
    });
    return order.map((key) => [key, map.get(key)!] as const);
  }, [filtered]);

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

      {grouped.map(([stageName, rows]) => (
        <section key={stageName}>
          <p className="mb-2.5 mt-5 font-mono text-[11px] uppercase tracking-[0.16em] text-gold">{stageName}</p>
          {rows.map((fixture) => (
            <FixtureRow key={fixture.id} fixture={fixture} />
          ))}
        </section>
      ))}

      {!error && fixtures.length === 0 && (
        <p className="font-mono text-xs uppercase tracking-[0.12em] text-chalk-dim">Loading fixtures…</p>
      )}

      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Kickoff times shown local. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
