import { BracketFixture } from "../types";

export default function ChampionCard({ finalFixture }: { finalFixture?: BracketFixture }) {
  if (!finalFixture) {
    return (
      <div className="w-72 border border-yellow-300/40 bg-slate-900/85 p-5 text-center text-white">
        <p className="text-sm font-bold uppercase text-yellow-300">Predicted Champion</p>
        <p className="mt-3 text-2xl font-black">TBD</p>
      </div>
    );
  }

  return (
    <div className="animate-gold-glow w-72 border border-yellow-300/60 bg-slate-900/90 p-5 text-center text-white shadow-gold">
      <p className="text-sm font-bold uppercase text-yellow-300">Trophy Pick</p>
      <div className="mx-auto mt-3 grid h-12 w-12 place-items-center rounded-full border border-gold/40 bg-gold/15 text-2xl">🏆</div>
      <p className="mt-3 text-3xl font-black">{finalFixture.predicted_winner}</p>
      <p className="mt-3 text-sm text-slate-300">
        Final: {finalFixture.home_team_name} vs {finalFixture.away_team_name}
      </p>
      <p className="mt-3 inline-flex bg-white/10 px-3 py-1 text-xs font-bold text-white">
        Confidence: {finalFixture.confidence ?? "TBD"}
      </p>
    </div>
  );
}
