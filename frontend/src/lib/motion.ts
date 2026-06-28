import { useEffect, useState } from "react";

/** True when the user has asked for reduced motion. Safe during SSR. */
export function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true
  );
}

/**
 * Returns false on the first paint, then true on the next frame — used to drive
 * one orchestrated CSS-transition entrance per surface (bar fills, knot settle).
 * Resolves immediately to the final state when reduced motion is requested.
 */
export function useEnter(): boolean {
  const [ready, setReady] = useState(() => prefersReducedMotion());

  useEffect(() => {
    if (prefersReducedMotion()) {
      setReady(true);
      return;
    }
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setReady(true)));
    return () => cancelAnimationFrame(id);
  }, []);

  return ready;
}
