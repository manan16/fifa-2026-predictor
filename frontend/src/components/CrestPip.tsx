import { CSSProperties } from "react";

interface Props {
  /** Three-letter country code shown inside the crest. */
  code: string;
  variant?: "default" | "gold";
  /** Tailwind sizing/spacing overrides (width, height, font-size). */
  className?: string;
}

const HEX_CLIP = "polygon(50% 0, 100% 22%, 100% 78%, 50% 100%, 0 78%, 0 22%)";

/**
 * Hexagon country-code crest. `gold` marks the model's favourite / champion.
 */
export default function CrestPip({ code, variant = "default", className = "" }: Props) {
  const style: CSSProperties = { clipPath: HEX_CLIP };
  const tone =
    variant === "gold"
      ? "text-pitch border-transparent bg-[radial-gradient(circle_at_38%_30%,#fff3c4,#f4c430_62%)]"
      : "text-chalk border border-line bg-[linear-gradient(160deg,rgba(236,244,237,0.13),rgba(236,244,237,0.03))]";

  return (
    <span
      aria-hidden="true"
      style={style}
      className={`grid place-items-center font-display font-bold uppercase tracking-wide ${tone} ${
        className || "h-11 w-[38px] text-xs"
      }`}
    >
      {code}
    </span>
  );
}
