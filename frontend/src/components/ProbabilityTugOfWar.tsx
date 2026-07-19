interface Props {
  homeLabel: string;
  awayLabel: string;
  homeProbability?: number | null;
  awayProbability?: number | null;
  marketHomeProbability?: number | null;
  /** Metric name shown before "MODEL CALL", e.g. "Advance probability". */
  metricLabel?: string;
}

function pct(value?: number | null) {
  return value == null ? "TBD" : `${Math.round(value * 100)}%`;
}

export default function ProbabilityTugOfWar({ homeLabel, awayLabel, homeProbability, awayProbability, marketHomeProbability, metricLabel = "Advance probability" }: Props) {
  const model = Math.round((homeProbability ?? 0.5) * 100);
  const market = Math.round((marketHomeProbability ?? homeProbability ?? 0.5) * 100);
  // When the two calls sit within ~3% their labels would overlap horizontally.
  // Keep the gold MODEL label above the track and drop the MARKET label below
  // it so both stay legible instead of stacking on the same spot.
  const close = Math.abs(model - market) <= 3;
  const modelLabelTop = "2px";
  const marketLabelTop = close ? "58px" : "2px";

  return (
    <div className="mt-8">
      <div className="mb-3 flex items-center justify-between gap-3 text-xs font-black uppercase tracking-[0.14em] text-slate-400">
        <span>{metricLabel} — <b className="text-white">MODEL CALL</b></span>
        <span className="text-sky-300">Market line</span>
      </div>
      <div className="relative h-20">
        <div className="absolute left-0 right-0 top-1/2 border-t-2 border-dashed border-white/15" />
        <div className="absolute left-0 top-1/2 h-1 -translate-y-1/2 animate-bar-fill rounded-l bg-gradient-to-r from-yellow-400/20 to-yellow-300" style={{ width: `${model}%` }}/>

        {/* Market marker (sky blue) — taller than the model line/knot so a sliver
            always pokes out above and below even when directly behind them. */}
        <div
          className="absolute top-1/2 z-10 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-pitch transition-all duration-700"
          style={{ left: `${market}%`, backgroundColor: "#7dd3fc", boxShadow: "0 0 8px rgba(56,189,248,0.6)" }}
        />
        <span
          className="absolute -translate-x-1/2 whitespace-nowrap text-[10px] font-black uppercase tracking-[0.16em] text-sky-300 transition-all duration-700"
          style={{ left: `${market}%`, top: marketLabelTop }}
        >
          Market
        </span>

        {/* Model marker (gold) — the desk's call, mirroring the market marker */}
        <div
          className="absolute top-1/2 h-10 w-0.5 -translate-x-1/2 -translate-y-1/2 bg-yellow-300 opacity-90 transition-all duration-700"
          style={{ left: `${model}%` }}
        />
        <span
          className="absolute -translate-x-1/2 whitespace-nowrap text-[10px] font-black uppercase tracking-[0.16em] text-yellow-300 transition-all duration-700"
          style={{ left: `${model}%`, top: modelLabelTop }}
        >
          Model
        </span>

        <span className="absolute bottom-0 left-0 text-xs font-black text-yellow-300">{pct(homeProbability)} {homeLabel}</span>
        <span className="absolute bottom-0 right-0 text-xs font-black text-slate-300">{awayLabel} {pct(awayProbability)}</span>
      </div>
    </div>
  );
}
