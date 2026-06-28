interface Props {
  homeLabel: string;
  awayLabel: string;
  homeProbability?: number | null;
  awayProbability?: number | null;
  marketHomeProbability?: number | null;
}

function pct(value?: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

export default function ProbabilityTugOfWar({ homeLabel, awayLabel, homeProbability, awayProbability, marketHomeProbability }: Props) {
  const model = Math.round((homeProbability ?? 0.5) * 100);
  const market = Math.round((marketHomeProbability ?? homeProbability ?? 0.5) * 100);

  return (
    <div className="mt-8">
      <div className="mb-3 flex items-center justify-between gap-3 text-xs font-black uppercase tracking-[0.14em] text-slate-400">
        <span>Advance probability — <b className="text-white">MODEL CALL</b></span>
        <span className="text-sky-300">Market line</span>
      </div>
      <div className="relative h-16">
        <div className="absolute left-0 right-0 top-1/2 border-t-2 border-dashed border-white/15" />
        <div className="absolute left-0 top-1/2 h-1 -translate-y-1/2 animate-bar-fill rounded bg-gradient-to-r from-yellow-400/20 to-yellow-300" style={{ width: `${model}%` }} />
        <div className="absolute top-1/2 h-10 w-0.5 -translate-y-1/2 bg-sky-300 opacity-95 transition-opacity duration-700" style={{ left: `${market}%` }}>
          <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-black uppercase tracking-[0.16em] text-sky-300">Market</span>
        </div>
        <div className="absolute top-1/2 h-7 w-7 -translate-x-1/2 -translate-y-1/2 animate-number-pop rounded-full bg-yellow-300 shadow-gold" style={{ left: `${model}%` }} />
        <span className="absolute bottom-0 left-0 text-xs font-black text-yellow-300">{pct(homeProbability)} {homeLabel}</span>
        <span className="absolute bottom-0 right-0 text-xs font-black text-slate-300">{awayLabel} {pct(awayProbability)}</span>
      </div>
    </div>
  );
}
