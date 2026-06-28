import { useEffect, useMemo, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import MatchCard from "../components/MatchCard";
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

  const stages = useMemo(() => ["All", ...new Set(fixtures.map((fixture) => fixture.stage))], [fixtures]);
  const filtered = stage === "All" ? fixtures : fixtures.filter((fixture) => fixture.stage === stage);

  return (
    <AnimatedPage className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-black uppercase text-gold">Matchday board</p>
          <h1 className="mt-2 text-3xl font-black text-line">Knockout bracket fixtures</h1>
          <p className="mt-2 text-line/65">
            Demo World Cup 2026 knockout fixtures based on the bracket reference, from Round of 32 to the final.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {stages.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setStage(item)}
              className={`border px-3 py-2 text-sm font-black transition ${
                stage === item ? "border-gold bg-gold text-stadium" : "border-line/15 bg-line/10 text-line/70 hover:border-gold/60"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((fixture) => (
          <MatchCard key={fixture.id} fixture={fixture} />
        ))}
      </div>
    </AnimatedPage>
  );
}
