import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ProbabilityTugOfWar from "./ProbabilityTugOfWar";
import { probabilityMetric } from "../lib/probability";

/**
 * Renders the model-call slider exactly as MatchCentreDetail does: the metric
 * (label + which probability to read) is derived from the fixture's stage.
 */
function renderForStage(stage: string) {
  const metric = probabilityMetric(stage);
  return render(
    <ProbabilityTugOfWar
      homeLabel="ARG"
      awayLabel="FRA"
      homeProbability={0.6}
      awayProbability={0.4}
      metricLabel={metric.label}
    />
  );
}

describe("probabilityMetric", () => {
  it.each(["Round of 16", "Quarter-final", "Semi-final", "Final"])(
    "uses advance probability for %s",
    (stage) => {
      expect(probabilityMetric(stage)).toEqual({ label: "Advance probability", useAdvance: true });
    }
  );

  it("uses win probability for the third-place play-off", () => {
    expect(probabilityMetric("Third-place play-off")).toEqual({ label: "Win probability", useAdvance: false });
    // Case/whitespace tolerant, since stage strings arrive from the API.
    expect(probabilityMetric("  third-place play-off  ")).toEqual({ label: "Win probability", useAdvance: false });
  });
});

describe("ProbabilityTugOfWar label switches on fixture stage", () => {
  it.each(["Round of 16", "Quarter-final", "Semi-final", "Final"])(
    "shows ADVANCE PROBABILITY for %s",
    (stage) => {
      renderForStage(stage);
      expect(screen.getByText(/advance probability/i)).toBeInTheDocument();
      expect(screen.queryByText(/win probability/i)).not.toBeInTheDocument();
    }
  );

  it("shows WIN PROBABILITY for the third-place play-off", () => {
    renderForStage("Third-place play-off");
    expect(screen.getByText(/win probability/i)).toBeInTheDocument();
    expect(screen.queryByText(/advance probability/i)).not.toBeInTheDocument();
  });
});

describe("ProbabilityTugOfWar model + market markers", () => {
  it("renders both a gold MODEL marker and a sky-blue MARKET marker", () => {
    render(
      <ProbabilityTugOfWar
        homeLabel="ARG"
        awayLabel="FRA"
        homeProbability={0.62}
        awayProbability={0.38}
        marketHomeProbability={0.45}
      />
    );

    const model = screen.getByText(/^Model$/);
    const market = screen.getByText(/^Market$/);
    expect(model).toBeInTheDocument();
    expect(market).toBeInTheDocument();
    // Matchnight colour grammar: model = gold, market = sky blue.
    expect(model.className).toContain("text-yellow-300");
    expect(market.className).toContain("text-sky-300");
    // Positioned at their respective probability values.
    expect(model).toHaveStyle({ left: "62%" });
    expect(market).toHaveStyle({ left: "45%" });
  });

  it("keeps labels on the same row when model and market are far apart", () => {
    render(
      <ProbabilityTugOfWar homeLabel="ARG" awayLabel="FRA" homeProbability={0.6} marketHomeProbability={0.3} />
    );
    expect(screen.getByText(/^Model$/)).toHaveStyle({ top: "2px" });
    expect(screen.getByText(/^Market$/)).toHaveStyle({ top: "2px" });
  });

  it("offsets the market label vertically when within ~3% of the model", () => {
    render(
      <ProbabilityTugOfWar homeLabel="ARG" awayLabel="FRA" homeProbability={0.61} marketHomeProbability={0.6} />
    );
    const model = screen.getByText(/^Model$/);
    const market = screen.getByText(/^Market$/);
    expect(model).toHaveStyle({ top: "2px" });
    // Dropped below the track so the two don't collide.
    expect(market).not.toHaveStyle({ top: "2px" });
    expect(market).toHaveStyle({ top: "58px" });
  });
});
