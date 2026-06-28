import { CSSProperties } from "react";
import CrestPip from "./CrestPip";

interface Props {
  /** Predicted winners per round, bottom (widest) to top (narrowest). */
  rows: string[][];
  /** Predicted champion code, igniting last at the apex. */
  champion: string;
}

const PAD = 10;

/**
 * Landing hero: rounds climb bottom → top to a gold champion that ignites last,
 * with chalk connectors drawing in between rows.
 */
export default function ChampionFunnel({ rows, champion }: Props) {
  // Top → bottom for rendering: champion sits above the narrowest round.
  const stack: string[][] = [[champion], ...[...rows].reverse()];
  const count = stack.length;
  const yOf = (rowIdx: number) => PAD + (rowIdx * (100 - 2 * PAD)) / Math.max(1, count - 1);
  const xOf = (i: number, n: number) => ((i + 0.5) / n) * 100;

  // Connectors: each lower item joins its parent in the row above.
  const connectors: { x1: number; y1: number; x2: number; y2: number; band: number }[] = [];
  for (let k = 0; k < count - 1; k += 1) {
    const upper = stack[k];
    const lower = stack[k + 1];
    const yU = yOf(k);
    const yL = yOf(k + 1);
    lower.forEach((_, i) => {
      const parent = Math.floor((i * upper.length) / lower.length);
      connectors.push({
        x1: xOf(i, lower.length),
        y1: yL,
        x2: xOf(parent, upper.length),
        y2: yU,
        band: count - 1 - k // bottom bands draw first
      });
    });
  }

  return (
    <div className="relative min-h-[340px] w-full" aria-label="Predicted road to the champion">
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="pointer-events-none absolute inset-0 h-full w-full"
        aria-hidden="true"
      >
        {connectors.map((c, i) => (
          <line
            key={i}
            data-chalk
            x1={c.x1}
            y1={c.y1}
            x2={c.x2}
            y2={c.y2}
            stroke="#ecf4ed"
            strokeWidth={0.4}
            opacity={0.18}
            className="animate-chalk-draw"
            style={{ strokeDasharray: 120, strokeDashoffset: 120, animationDelay: `${0.15 + c.band * 0.3}s` }}
          />
        ))}
      </svg>

      {stack.map((row, rowIdx) => {
        const isChamp = rowIdx === 0;
        return (
          <div
            key={rowIdx}
            className="absolute inset-x-0 flex -translate-y-1/2 items-end justify-around"
            style={{ top: `${yOf(rowIdx)}%` }}
          >
            {row.map((code, i) => {
              const delay = isChamp ? 1.1 : 0.15 + (count - 1 - rowIdx) * 0.18 + i * 0.05;
              if (isChamp) {
                return (
                  <div key={i} className="text-center">
                    <span className="mb-2 block font-mono text-[10px] uppercase tracking-[0.18em] text-gold">
                      Predicted champion
                    </span>
                    <span className="animate-ignite inline-block" style={{ animationDelay: `${delay}s` }}>
                      <CrestPip code={code} variant="gold" className="mx-auto h-20 w-[70px] text-xl" />
                    </span>
                  </div>
                );
              }
              return (
                <span
                  key={i}
                  className="animate-tie-pop"
                  style={{ animationDelay: `${delay}s` } as CSSProperties}
                >
                  <CrestPip code={code} className="h-[46px] w-10 text-xs" />
                </span>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
