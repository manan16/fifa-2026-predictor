import { CSSProperties } from "react";
import CountUp from "./CountUp";
import { useEnter } from "../lib/motion";

interface Props {
  homeCode: string;
  awayCode: string;
  /** Model's home-side share, 0..1 (advance prob in knockouts, else win prob). */
  modelProb: number;
  /** Market's home-side share, 0..1. Omitted when no market line exists. */
  marketProb?: number | null;
  size?: "full" | "mini";
  className?: string;
}

const clampPct = (v: number) => Math.max(0, Math.min(100, Math.round(v * 100)));

/**
 * THE signature element: a rope between two nations. The gold knot sits at the
 * model's split; the thin sky line marks the market; the space between them is
 * the edge.
 */
export default function SupremacyMeter({
  homeCode,
  awayCode,
  modelProb,
  marketProb,
  size = "full",
  className = ""
}: Props) {
  const ready = useEnter();
  const homePct = clampPct(modelProb);
  const awayPct = 100 - homePct;
  const hasMarket = marketProb !== null && marketProb !== undefined;
  const marketPct = hasMarket ? clampPct(marketProb as number) : null;
  const edge = marketPct !== null ? homePct - marketPct : null;
  const favCode = modelProb >= 0.5 ? homeCode : awayCode;

  if (size === "mini") {
    return (
      <div className={`relative h-1 rounded-sm bg-chalk-faint ${className}`}>
        <span
          className="animate-bar-fill absolute inset-y-0 left-0 rounded-sm"
          style={{
            width: `${homePct}%`,
            background: "linear-gradient(90deg, rgba(244,196,48,0.25), #f4c430)"
          }}
        />
        {marketPct !== null && (
          <span
            className={`absolute -top-1 -bottom-1 w-0.5 bg-sky transition-opacity duration-300 ${
              ready ? "opacity-90" : "opacity-0"
            }`}
            style={{ left: `${marketPct}%` }}
            title={`Market ${marketPct}%`}
          />
        )}
      </div>
    );
  }

  const knotStyle: CSSProperties = {
    left: `${ready ? homePct : 50}%`,
    transition: "left 1.1s cubic-bezier(0.2,0.85,0.25,1), opacity 0.4s ease 0.6s, transform 0.4s ease 0.6s"
  };

  return (
    <div className={className}>
      <div className="mb-3 flex items-baseline justify-between font-mono text-[11px] uppercase tracking-[0.14em] text-chalk-dim">
        <span>
          Advance split — <b className="font-bold text-chalk">the desk's call</b>
        </span>
        {hasMarket && <span>vs market line</span>}
      </div>

      <div className="relative h-14">
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 border-t-2 border-dashed border-line" />
        <div
          className="animate-bar-fill absolute left-0 top-1/2 h-1 -translate-y-1/2 rounded-sm"
          style={{
            width: `${homePct}%`,
            background: "linear-gradient(90deg, rgba(244,196,48,0.15), #f4c430)"
          }}
        />
        {marketPct !== null && (
          <span
            className={`absolute w-0.5 bg-sky transition-opacity duration-500 ${
              ready ? "opacity-90" : "opacity-0"
            }`}
            style={{ left: `${marketPct}%`, top: "calc(50% - 20px)", height: "40px" }}
          >
            <span className="absolute -top-4 left-1/2 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] uppercase tracking-[0.16em] text-sky">
              Market
            </span>
          </span>
        )}
        <span
          aria-hidden="true"
          style={knotStyle}
          className={`absolute top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-gold ${
            ready ? "scale-100 opacity-100" : "scale-50 opacity-0"
          }`}
        >
          <span
            className="block h-full w-full rounded-full"
            style={{ background: "radial-gradient(circle at 35% 30%, #fff3c4, #f4c430 60%)" }}
          />
        </span>
        <span className="absolute -bottom-1.5 left-0 font-mono text-xs font-bold tracking-wide text-gold font-tabular">
          <CountUp value={homePct} suffix="%" /> {homeCode}
        </span>
        <span className="absolute -bottom-1.5 right-0 font-mono text-xs font-bold tracking-wide text-chalk-dim font-tabular">
          {awayCode} <CountUp value={awayPct} suffix="%" />
        </span>
      </div>

      {edge !== null && (
        <span className="mt-5 inline-flex items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.1em] text-gold">
          {edge === 0 ? (
            <>Desk and market agree on {favCode}</>
          ) : (
            <>
              Edge to the desk{" "}
              <b className="font-bold">
                {edge > 0 ? "+" : ""}
                {edge} pts
              </b>{" "}
              on {favCode}
            </>
          )}
        </span>
      )}
    </div>
  );
}
