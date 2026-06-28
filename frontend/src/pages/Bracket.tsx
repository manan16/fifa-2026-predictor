import { useEffect, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import BracketTree, { Tie } from "../components/BracketTree";
import { getBracket } from "../services/api";
import { BracketResponse } from "../types";

const emptyBracket: BracketResponse = {
  round_of_32: [],
  round_of_16: [],
  quarter_finals: [],
  semi_finals: [],
  final: []
};

export default function Bracket() {
  const [bracket, setBracket] = useState<BracketResponse>(emptyBracket);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getBracket()
      .then(setBracket)
      .catch(() => setError("Unable to load the knockout bracket. Start the backend and seed the database."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AnimatedPage className="space-y-6">
      <header className="pt-2">
        <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
          Tournament wall
          <span className="h-px w-14 bg-line" />
        </p>
        <h1 className="mt-3 font-display text-[clamp(30px,5vw,46px)] font-extrabold uppercase leading-[0.95] text-chalk">
          Predicted bracket
        </h1>
        <p className="mt-2.5 max-w-[560px] text-chalk-dim">
          The desk's path from the Round of 16 to the trophy. Gold marks who advances; the sky tick is the
          market's line; coral flags a tie where the two disagree.
        </p>
      </header>

      {error && <div className="rounded border border-coral/30 bg-coral/10 p-4 text-coral">{error}</div>}

      {loading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="pitch-skeleton relative h-28 overflow-hidden rounded border border-line bg-turf/50" />
          ))}
        </div>
      )}

      {!loading && !error && (
        <>
          {bracket.round_of_32.length > 0 && (
            <section>
              <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.12em] text-chalk-dim">
                ‹ Round of 32 · scroll to expand
              </p>
              <div className="overflow-x-auto">
                <div className="flex min-w-max gap-3 pb-2">
                  {bracket.round_of_32.map((f) => (
                    <div key={f.id} className="w-[150px] shrink-0">
                      <Tie f={f} />
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}

          <BracketTree bracket={bracket} />
        </>
      )}

      <p className="font-mono text-[11px] tracking-[0.06em] text-chalk-dim">
        Demo bracket from seeded data. Model vs market analytics. Not betting advice.
      </p>
    </AnimatedPage>
  );
}
