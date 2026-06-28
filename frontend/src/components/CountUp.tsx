import { useCountUp } from "../hooks/useCountUp";

interface Props {
  /** The final value to animate to. */
  value: number;
  /** Multiply the value before formatting (e.g. 100 to turn 0.61 into 61). */
  scale?: number;
  /** Decimal places to show. */
  decimals?: number;
  /** Suffix appended after the number, e.g. "%". */
  suffix?: string;
  /** Animation duration in ms. */
  durationMs?: number;
  className?: string;
}

/**
 * Renders a number that animates up to its value on mount / when it changes.
 */
export default function CountUp({
  value,
  scale = 1,
  decimals = 0,
  suffix = "",
  durationMs = 900,
  className
}: Props) {
  const animated = useCountUp(value * scale, durationMs);
  return (
    <span key={value} className={`animate-number-pop ${className ?? ""}`}>
      {animated.toFixed(decimals)}
      {suffix}
    </span>
  );
}
