interface Props {
  leftLabel: string;
  rightLabel: string;
  leftProbability?: number | null;
  rightProbability?: number | null;
  marketProbability?: number | null;
}

function pct(value?: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

export default function ProbabilityLine({ leftLabel, rightLabel, leftProbability, rightProbability, marketProbability }: Props) {
  const leftPct = Math.max(0, Math.min(100, Math.round((leftProbability ?? 0) * 100)));
  const marketPct = Math.max(0, Math.min(100, Math.round((marketProbability ?? 0) * 100)));

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4 text-xs font-black uppercase text-slate-300">
        <span className="text-yellow-300">{leftLabel}: {pct(leftProbability)}</span>
        <span>{rightLabel}: {pct(rightProbability)}</span>
      </div>
      <div className="relative h-3 overflow-hidden rounded-full bg-slate-800 ring-1 ring-white/10">
        <div className="h-full rounded-full bg-gradient-to-r from-yellow-300 to-emerald-400 animate-bar-fill" style={{ width: `${leftPct}%` }} />
        {marketProbability != null && (
          <div className="absolute top-0 h-full w-0.5 bg-blue-400 shadow-[0_0_12px_rgba(96,165,250,0.8)]" style={{ left: `${marketPct}%` }} />
        )}
      </div>
      {marketProbability != null && <p className="mt-2 text-xs text-blue-300">Market marker: {pct(marketProbability)}</p>}
    </div>
  );
}

