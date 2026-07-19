import { useEffect, useMemo, useRef, useState } from "react";

interface Props {
  /** Expected home goals (xG). */
  homeXg: number;
  /** Expected away goals (xG). */
  awayXg: number;
  homeCode?: string;
  awayCode?: string;
  /** Grid dimension (scorelines 0..n-1). */
  size?: number;
}

function poisson(lambda: number, k: number): number {
  let factorial = 1;
  for (let i = 2; i <= k; i += 1) factorial *= i;
  return (Math.exp(-lambda) * Math.pow(lambda, k)) / factorial;
}

/**
 * Poisson score grid. Cells shade gold by likelihood; the draw diagonal is
 * outlined in sky and the modal (most likely) scoreline in gold.
 */
export default function ScoreHeatmap({ homeXg, awayXg, homeCode = "HOME", awayCode = "AWAY", size = 6 }: Props) {
  const { cells, max, modal } = useMemo(() => {
    let maxP = 0;
    let modalCell = { h: 0, a: 0 };
    const grid: { h: number; a: number; p: number }[] = [];
    for (let h = 0; h < size; h += 1) {
      for (let a = 0; a < size; a += 1) {
        const p = poisson(homeXg, h) * poisson(awayXg, a);
        if (p > maxP) {
          maxP = p;
          modalCell = { h, a };
        }
        grid.push({ h, a, p });
      }
    }
    return { cells: grid, max: maxP, modal: modalCell };
  }, [homeXg, awayXg, size]);

  const axes = Array.from({ length: size }, (_, i) => i);

  // The grid is a square-celled block that can grow taller than the viewport.
  // Rather than letting it clip silently, cap its height and scroll inside —
  // surfacing a fade + hint only while there is genuinely more below.
  const scrollRef = useRef<HTMLDivElement>(null);
  const [overflowing, setOverflowing] = useState(false);
  const [atBottom, setAtBottom] = useState(false);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const measure = () => {
      const scrollable = el.scrollHeight - el.clientHeight;
      setOverflowing(scrollable > 1);
      setAtBottom(scrollable - el.scrollTop <= 1);
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [size, homeXg, awayXg]);

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    setAtBottom(el.scrollHeight - el.clientHeight - el.scrollTop <= 1);
  };

  const showAffordance = overflowing && !atBottom;

  return (
    <div className="rounded border border-line bg-turf2/55 p-[18px]">
      <div className="mb-3 flex justify-between font-mono text-[10px] uppercase tracking-[0.12em] text-chalk-dim">
        <span>
          Score grid · {homeCode} xG {homeXg.toFixed(1)} — {awayCode} xG {awayXg.toFixed(1)}
        </span>
        <span>
          most likely {modal.h}–{modal.a}
        </span>
      </div>

      <div className="relative">
        <div ref={scrollRef} onScroll={handleScroll} className="max-h-[56vh] overflow-y-auto overflow-x-hidden">
          <div
            className="grid gap-[3px]"
            style={{ gridTemplateColumns: `18px repeat(${size}, 1fr)` }}
            role="img"
            aria-label={`Most likely scoreline ${modal.h} to ${modal.a}`}
          >
            <div />
            {axes.map((a) => (
              <div key={`top-${a}`} className="grid place-items-center font-mono text-[9px] text-chalk-dim">
                {a}
              </div>
            ))}
            {axes.map((h) => (
              <div key={`row-${h}`} className="contents">
                <div className="grid place-items-center font-mono text-[9px] text-chalk-dim">{h}</div>
                {axes.map((a) => {
                  const cell = cells[h * size + a];
                  const t = cell.p / max;
                  const isDiag = h === a;
                  const isModal = h === modal.h && a === modal.a;
                  return (
                    <div
                      key={`${h}-${a}`}
                      className={`grid aspect-square place-items-center rounded-sm font-mono text-[9px] ${
                        isModal
                          ? "outline outline-2 -outline-offset-1 outline-gold"
                          : isDiag
                            ? "outline outline-1 -outline-offset-1 outline-sky/50"
                            : ""
                      }`}
                      style={{
                        background: `rgba(244,196,48,${(0.06 + t * 0.85).toFixed(3)})`,
                        color: t > 0.35 ? "rgba(10,26,20,0.85)" : "transparent"
                      }}
                    >
                      {t > 0.35 ? (cell.p * 100).toFixed(0) : ""}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Scroll affordance: only while more of the grid remains below the fold. */}
        <div
          className={`pointer-events-none absolute inset-x-0 bottom-0 flex h-14 items-end justify-center bg-gradient-to-t from-turf2 to-transparent transition-opacity duration-300 ${
            showAffordance ? "opacity-100" : "opacity-0"
          }`}
          aria-hidden="true"
        >
          <span className="mb-1 animate-bounce font-mono text-[9px] uppercase tracking-[0.14em] text-chalk-dim">
            scroll for more ↓
          </span>
        </div>
      </div>

      <div className="mt-3 flex gap-4 font-mono text-[10px] uppercase tracking-[0.06em] text-chalk-dim">
        <span className="flex items-center gap-1.5">
          <i className="inline-block h-2.5 w-2.5 rounded-sm bg-gold" /> likelier
        </span>
        <span className="flex items-center gap-1.5">
          <i className="inline-block h-2.5 w-2.5 rounded-sm outline outline-1 -outline-offset-1 outline-sky" /> draw
        </span>
        <span className="flex items-center gap-1.5">
          <i className="inline-block h-2.5 w-2.5 rounded-sm outline outline-2 -outline-offset-1 outline-gold" /> model pick
        </span>
      </div>
    </div>
  );
}
