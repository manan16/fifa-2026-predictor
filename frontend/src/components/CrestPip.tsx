import { CSSProperties } from "react";
import { flagUrl } from "../lib/flags";

interface Props {
  /** Three-letter country code shown inside the crest. */
  code: string;
  variant?: "default" | "gold";
  /** Tailwind sizing/spacing overrides (width, height, font-size). */
  className?: string;
}

const HEX_CLIP = "polygon(50% 0, 100% 22%, 100% 78%, 50% 100%, 0 78%, 0 22%)";

/**
 * Hexagon country crest. Shows the team's flag when the code maps to one;
 * falls back to the three-letter code otherwise (e.g. "TBD" slots).
 * `gold` marks the model's favourite / champion via a glowing ring rather
 * than a fill, since the flag now owns the fill.
 */
export default function CrestPip({ code, variant = "default", className = "" }: Props) {
  const flag = flagUrl(code);
  const style: CSSProperties = {
    clipPath: HEX_CLIP,
    ...(flag ? { backgroundImage: `url(${flag})`, backgroundSize: "cover", backgroundPosition: "center" } : {}),
  };
  const tone =
    variant === "gold"
      ? "text-pitch ring-2 ring-gold shadow-[0_0_14px_rgba(244,196,48,0.55)]"
      : "text-chalk border border-line";
  const fallbackTone =
    variant === "gold"
      ? "bg-[radial-gradient(circle_at_38%_30%,#fff3c4,#f4c430_62%)]"
      : "bg-[linear-gradient(160deg,rgba(236,244,237,0.13),rgba(236,244,237,0.03))]";

  return (
    <span
      aria-hidden="true"
      style={style}
      className={`grid place-items-center font-display font-bold uppercase tracking-wide ${tone} ${
        flag ? "" : fallbackTone
      } ${className || "h-11 w-[38px] text-xs"}`}
    >
      {!flag && code}
    </span>
  );
}