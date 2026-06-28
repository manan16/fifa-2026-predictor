import { useEffect, useMemo, useState } from "react";
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
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-black">Fixtures</h1>
          <p className="mt-2 text-ink/65">Sample World Cup 2026 fixtures for the MVP predictor.</p>
        </div>
        <select
          value={stage}
          onChange={(event) => setStage(event.target.value)}
          className="border border-ink/15 bg-white px-3 py-2"
        >
          {stages.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((fixture) => (
          <MatchCard key={fixture.id} fixture={fixture} />
        ))}
      </div>
    </div>
  );
}

