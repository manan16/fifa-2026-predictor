/** Country code, falling back to the first letters of the name. */
export function shortCode(code: string | null | undefined, name: string): string {
  if (code) return code.toUpperCase();
  return (name ?? "").replace(/[^A-Za-z]/g, "").slice(0, 3).toUpperCase() || "—";
}

/** Two-way home share from home/away probabilities (draw excluded). 0..1. */
export function twoWayShare(home?: number | null, away?: number | null): number {
  const h = home ?? 0;
  const a = away ?? 0;
  const total = h + a;
  return total > 0 ? h / total : 0.5;
}

export type StatusKind = "live" | "done" | "scheduled";

/** Coarse status bucket driving the desk's status dot. */
export function statusKind(status: string): StatusKind {
  const s = (status ?? "").toLowerCase();
  if (["live", "in_play", "playing"].includes(s)) return "live";
  if (["completed", "finished", "done", "ft", "full_time"].includes(s)) return "done";
  return "scheduled";
}

/** Is the favourite from one set of probabilities different from the other? */
export function favouritesDisagree(
  modelHome: number | undefined | null,
  marketHome: number | undefined | null
): boolean {
  if (modelHome == null || marketHome == null) return false;
  return modelHome >= 0.5 !== marketHome >= 0.5;
}
