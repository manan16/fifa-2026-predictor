/** The knockout stage whose result decides nothing downstream. */
export const THIRD_PLACE_STAGE = "Third-place play-off";

export interface ProbabilityMetric {
  /** Human label for the slider, e.g. "Advance probability". */
  label: string;
  /**
   * Whether to read home/away *advance* probability (win + shoot-out share of
   * the draw). False means fall back to the raw 90-minute win probability.
   */
  useAdvance: boolean;
}

/**
 * Choose the probability metric for a fixture's model-call slider.
 *
 * Every knockout tie that leads somewhere reports an advance probability, so it
 * gets the "Advance probability" label backed by home/away_advance_probability.
 * The third-place play-off is not an advance scenario — nobody progresses from
 * it — so it shows a plain "Win probability" backed by the win probabilities.
 */
export function probabilityMetric(stage: string | null | undefined): ProbabilityMetric {
  const normalized = (stage ?? "").trim().toLowerCase();
  if (normalized === THIRD_PLACE_STAGE.toLowerCase()) {
    return { label: "Win probability", useAdvance: false };
  }
  return { label: "Advance probability", useAdvance: true };
}
