import { useEffect, useRef, useState } from "react";

function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true
  );
}

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

/**
 * Animates a numeric value from 0 (or a chosen start) up to `target`.
 * Respects reduced-motion by jumping straight to the final value.
 */
export function useCountUp(target: number, durationMs = 900, start = 0): number {
  const [value, setValue] = useState(prefersReducedMotion() ? target : start);
  const frameRef = useRef<number>();
  const startTimeRef = useRef<number>();

  useEffect(() => {
    if (prefersReducedMotion()) {
      setValue(target);
      return;
    }

    const from = start;
    const delta = target - from;
    startTimeRef.current = undefined;

    const tick = (now: number) => {
      if (startTimeRef.current === undefined) startTimeRef.current = now;
      const elapsed = now - startTimeRef.current;
      const progress = Math.min(1, elapsed / durationMs);
      setValue(from + delta * easeOutCubic(progress));
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(tick);
      }
    };

    frameRef.current = requestAnimationFrame(tick);
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [target, durationMs, start]);

  return value;
}
