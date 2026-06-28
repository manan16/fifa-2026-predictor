import { useEffect, useState } from "react";
import AnimatedPage from "../components/AnimatedPage";
import KnockoutBracket from "../components/KnockoutBracket";
import PitchBackground from "../components/PitchBackground";
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
      .then((data) => setBracket(data))
      .catch(() => setError("Unable to load the knockout bracket. Start the backend and seed the database."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AnimatedPage className="-mx-4 -my-8 min-h-[calc(100vh-73px)] sm:-mx-6 lg:-mx-8">
      <PitchBackground className="min-h-[calc(100vh-73px)] px-4 py-8 sm:px-6 lg:px-8">
        <section className="mx-auto mb-8 max-w-6xl">
          <p className="text-sm font-black uppercase text-gold">Tournament wall</p>
          <h1 className="mt-3 text-4xl font-black sm:text-5xl">Predicted Bracket</h1>
          <p className="mt-4 max-w-3xl text-line/65">
            Follow the seeded demo knockout path from Round of 32 through the final, with model probabilities, market consensus, scorelines, and actual results.
          </p>
        </section>

        {loading && (
          <div className="mx-auto grid max-w-6xl gap-4 md:grid-cols-4">
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="pitch-skeleton relative h-36 overflow-hidden border border-line/10 bg-line/[0.06]">
                <div className="m-4 h-3 w-24 bg-line/10" />
                <div className="mx-4 mt-8 h-4 w-40 bg-line/10" />
                <div className="mx-4 mt-3 h-4 w-32 bg-line/10" />
              </div>
            ))}
          </div>
        )}
        {error && <div className="mx-auto max-w-6xl border border-coral/40 bg-coral/15 p-6 text-coral">{error}</div>}
        {!loading && !error && <KnockoutBracket bracket={bracket} />}
      </PitchBackground>
    </AnimatedPage>
  );
}
