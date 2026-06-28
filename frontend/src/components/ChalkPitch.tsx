interface Props {
  /** Extra classes (opacity / positioning overrides). */
  className?: string;
}

/**
 * Chalk tactical lines drawn into a card backdrop (stroke-dashoffset). Absolute
 * fill — place inside a `relative` surface. Decorative only.
 */
export default function ChalkPitch({ className = "" }: Props) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 1000 320"
      preserveAspectRatio="none"
      className={`pointer-events-none absolute inset-0 h-full w-full ${className}`}
    >
      <g
        data-chalk
        fill="none"
        stroke="#ecf4ed"
        strokeWidth={1}
        opacity={0.16}
        className="animate-chalk-draw"
        style={{ strokeDasharray: 1400, strokeDashoffset: 1400 }}
      >
        <line x1="500" y1="0" x2="500" y2="320" />
        <circle cx="500" cy="160" r="64" />
        <path d="M0 70 L120 70 L120 250 L0 250" />
        <path d="M1000 70 L880 70 L880 250 L1000 250" />
      </g>
    </svg>
  );
}
