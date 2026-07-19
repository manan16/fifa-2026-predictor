import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatsPanel from "./StatsPanel";
import { ActualMatchStats } from "../types";

// A completed-match actual stats row where both sides took zero cards. Before
// the guard, these zeros rendered for a scheduled fixture as a fake 0-0 result.
const ZERO_CARD_STATS: ActualMatchStats = {
  fixture_id: 1,
  home_shots: 12,
  away_shots: 9,
  home_shots_on_target: 5,
  away_shots_on_target: 3,
  home_possession: 55,
  away_possession: 45,
  home_corners: 6,
  away_corners: 4,
  home_yellow_cards: 0,
  away_yellow_cards: 0,
  home_red_cards: 0,
  away_red_cards: 0,
  source: "demo_synthetic"
};

describe("StatsPanel actual-stats guard", () => {
  it("shows a not-played placeholder for a scheduled fixture even if a zero stats row exists", () => {
    render(
      <StatsPanel
        homeTeam="Croatia"
        awayTeam="Morocco"
        stats={null}
        actualStats={ZERO_CARD_STATS}
        hasActualScore={false}
        status="scheduled"
      />
    );

    expect(screen.getByText(/not available yet — match not played/i)).toBeInTheDocument();
    // No numeric rows — the misleading zeros must not appear.
    expect(screen.queryByText("Yellow cards")).not.toBeInTheDocument();
    expect(screen.queryByText("Red cards")).not.toBeInTheDocument();
    expect(screen.queryByText("Possession")).not.toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("shows a not-played placeholder for a live fixture with no stats yet", () => {
    render(
      <StatsPanel homeTeam="Croatia" awayTeam="Morocco" stats={null} actualStats={null} hasActualScore={false} status="live" />
    );
    expect(screen.getByText(/not available yet — match not played/i)).toBeInTheDocument();
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("renders numeric rows for a completed fixture with real stats", () => {
    render(
      <StatsPanel
        homeTeam="Croatia"
        awayTeam="Morocco"
        stats={null}
        actualStats={ZERO_CARD_STATS}
        hasActualScore
        status="completed"
      />
    );

    expect(screen.queryByText(/not available yet/i)).not.toBeInTheDocument();
    expect(screen.getByText("Yellow cards")).toBeInTheDocument();
    expect(screen.getByText("Red cards")).toBeInTheDocument();
    expect(screen.getByText("Shots")).toBeInTheDocument();
    // Genuine recorded zeros are allowed once the match is completed.
    expect(screen.getAllByText("0").length).toBeGreaterThan(0);
  });

  it("shows a score-but-no-detail message when completed without stats data", () => {
    render(
      <StatsPanel homeTeam="Croatia" awayTeam="Morocco" stats={null} actualStats={null} hasActualScore status="completed" />
    );
    expect(screen.getByText(/final score available — detailed match stats not available yet/i)).toBeInTheDocument();
  });
});
