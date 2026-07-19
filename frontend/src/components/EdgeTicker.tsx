import { CSSProperties } from "react";
import { prefersReducedMotion } from "../lib/motion";

// Fade the horizontal edges so items scrolling in/out don't hard-crop mid-code.
// Applied at both edges at every viewport width (fixed 32px fade zones).
const edgeFade: CSSProperties = {
  maskImage: "linear-gradient(to right, transparent 0, #000 32px, #000 calc(100% - 32px), transparent 100%)",
  WebkitMaskImage: "linear-gradient(to right, transparent 0, #000 32px, #000 calc(100% - 32px), transparent 100%)"
};

export interface EdgeItem {
  homeCode: string;
  awayCode: string;
  /** Model home% minus market home%, in points. */
  edge: number;
  /** Model and market favour different sides. */
  disagree: boolean;
}

interface Props {
  items: EdgeItem[];
  className?: string;
}

function Item({ item }: { item: EdgeItem }) {
  return (
    <span className="inline-flex items-center gap-2.5 border-r border-line px-6 py-3 font-mono text-xs uppercase tracking-[0.06em] text-chalk-dim">
      <b className="font-bold text-chalk">{item.homeCode}</b> v {item.awayCode} ·{" "}
      {item.disagree ? (
        <span className="text-coral">market disagrees {item.edge > 0 ? "+" : ""}{item.edge}</span>
      ) : (
        <span className="text-gold">desk {item.edge >= 0 ? "+" : ""}{item.edge}</span>
      )}
    </span>
  );
}

/**
 * Broadcast marquee of model-vs-market edges. Seamless loop (track duplicated),
 * pauses on hover; reduced motion turns it into a static, scrollable strip.
 */
export default function EdgeTicker({ items, className = "" }: Props) {
  if (items.length === 0) return null;
  const reduce = prefersReducedMotion();

  if (reduce) {
    return (
      <div
        className={`group overflow-x-auto border-y border-line bg-turf2/50 ${className}`}
        style={edgeFade}
        aria-label="Model versus market edges"
      >
        <div className="flex w-max">
          {items.map((item, i) => (
            <Item key={i} item={item} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      className={`group overflow-hidden border-y border-line bg-turf2/50 ${className}`}
      style={edgeFade}
      aria-label="Model versus market edges"
    >
      <div className="animate-marquee inline-flex whitespace-nowrap group-hover:[animation-play-state:paused]">
        {[...items, ...items].map((item, i) => (
          <Item key={i} item={item} />
        ))}
      </div>
    </div>
  );
}
