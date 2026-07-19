import math
from typing import Any

MODEL_VERSION = "elo-symmetric-etp-form-v5"

ELO_REFERENCE = 1500.0
ELO_WEIGHT = 0.7
RANKING_WEIGHT = 1.0 - ELO_WEIGHT

# --- Tournament-form adjustment ---
# Form is measured as performance *relative to the model's own pre-match
# expectation*: for each completed tournament match a team has played, the
# residual is (actual goal difference - predicted goal difference) from that
# team's perspective. The mean residual (in goals/game) is scaled into an
# Elo-equivalent nudge and hard-capped. The cap is deliberately small relative
# to the ~150-300 point gaps that separate strong and weak teams here, so form
# nudges the baseline rather than dominating it. A team with no completed
# tournament matches (e.g. its very first match) gets exactly 0.0.
FORM_ADJUSTMENT_SCALE = 32.0  # Elo-equivalent points per goal of mean residual.
FORM_ADJUSTMENT_CAP = 50.0    # Maximum swing in either direction.
# Only mention the adjustment in the plain-language explanation once it is large
# enough to matter (Elo-equivalent magnitude), so it doesn't appear on every tie.
FORM_EXPLANATION_THRESHOLD = 8.0

SCORELINE_BASE_XG = 1.30
SCORELINE_SLOPE = 0.95
SCORELINE_DIVISOR = 330.0
SCORELINE_FLOOR_XG = 0.25
SCORELINE_CAP_XG = 4.20
HOME_ADVANTAGE_STRENGTH = 55.0
HOME_ADVANTAGE_GOALS = (HOME_ADVANTAGE_STRENGTH / SCORELINE_DIVISOR) * SCORELINE_SLOPE
DIXON_COLES_RHO = -0.08

STAGE_TOTAL_GOALS = {
    "group": 2.65,
    "round of 32": 2.55,
    "round of 16": 2.50,
    "quarter-final": 2.45,
    "quarter-finals": 2.45,
    "quarter finals": 2.45,
    "semi-final": 2.40,
    "semi-finals": 2.40,
    "semi finals": 2.40,
    "final": 2.35,
}
DEFAULT_TOTAL_GOALS = 2.55

# --- Extra-time and penalty-shootout sub-model (knockout ties only) ---
# Extra time is a 30-minute period, but it is played far more cautiously than
# regulation, so its goal rate is well below a straight time-proportional scale
# (30/90 of ~2.5 would be ~0.83). We use a lower baseline (~a quarter to a third
# of the regulation total) to reflect that conservatism.
ET_TOTAL_GOALS = 0.75
# Fatigue and caution also compress the gap between sides in extra time, so the
# strength-driven supremacy term is dampened relative to regulation.
ET_SUPREMACY_DAMPENING = 0.55
ET_FLOOR_XG = 0.05
# Penalty shootouts are close to a coin flip and are not reliably predicted by
# team strength (well documented in football analytics). We apply only a small,
# hard-capped nudge off 50/50 for the stronger side: even the largest realistic
# strength gap stays inside roughly 58/42.
PENALTY_STRENGTH_DIVISOR = 4000.0
PENALTY_MAX_EDGE = 0.07
# The third-place play-off does not use extra time under FIFA rules — a draw
# after 90 minutes goes straight to a shootout. Matched (lower-cased) against the
# frontend THIRD_PLACE_STAGE constant in frontend/src/lib/probability.ts.
THIRD_PLACE_STAGE = "third-place play-off"

# Response-only fields added for knockout ties (never persisted to the
# predictions table — surfaced by recomputing from team strength at read time).
KNOCKOUT_BREAKDOWN_FIELDS = (
    "home_win_in_90_probability",
    "away_win_in_90_probability",
    "home_win_in_et_probability",
    "away_win_in_et_probability",
    "home_win_on_penalties_probability",
    "away_win_on_penalties_probability",
    "home_advance_probability",
    "away_advance_probability",
    "et_predicted_home_goals",
    "et_predicted_away_goals",
    "et_home_win_probability",
    "et_draw_probability",
    "et_away_win_probability",
    "penalty_home_win_probability",
    "penalty_away_win_probability",
)


def _ranking_to_elo(ranking: float) -> float:
    ranking = max(1.0, ranking)
    return ELO_REFERENCE + 600.0 * math.exp(-(ranking - 1.0) / 22.0) - 60.0


def calculate_team_strength(team: dict[str, Any], form_adjustment: float = 0.0) -> float:
    elo = float(team.get("elo_rating") or ELO_REFERENCE)
    ranking = float(team.get("fifa_ranking") or 50)
    # The form adjustment is a clearly separate additive term on top of the
    # static Elo/ranking blend — never blended into it — so it can be reasoned
    # about, disabled, or tuned independently.
    return ELO_WEIGHT * elo + RANKING_WEIGHT * _ranking_to_elo(ranking) + form_adjustment


def _form_residuals(recent_matches: list[dict[str, Any]] | None) -> list[float]:
    """Per-match (actual - predicted) goal-difference residuals, team's perspective.

    Each row comes from ``queries.get_recent_tournament_form``: a ``side``
    ("home"/"away"), the fixture's ``actual_home_score``/``actual_away_score`` and
    the stored prediction's ``predicted_home_goals``/``predicted_away_goals``.
    Positive = the team beat the model's own pre-match expectation. Rows missing
    an actual score or a stored prediction are skipped.
    """
    residuals: list[float] = []
    for match in recent_matches or []:
        actual_home = match.get("actual_home_score")
        actual_away = match.get("actual_away_score")
        predicted_home = match.get("predicted_home_goals")
        predicted_away = match.get("predicted_away_goals")
        if None in (actual_home, actual_away, predicted_home, predicted_away):
            continue
        actual_diff = actual_home - actual_away
        predicted_diff = predicted_home - predicted_away
        if match.get("side") == "away":
            actual_diff = -actual_diff
            predicted_diff = -predicted_diff
        residuals.append(float(actual_diff - predicted_diff))
    return residuals


def calculate_form_adjustment(recent_matches: list[dict[str, Any]]) -> float:
    """Bounded Elo-equivalent strength nudge from recent tournament form.

    Averages the (actual - predicted) goal-difference residuals over the provided
    matches (the caller passes only the most recent N, so recency is already
    handled — no extra recency weighting here), scales the mean into Elo points
    and hard-caps it. Returns ``0.0`` for an empty list (no completed matches yet).
    """
    residuals = _form_residuals(recent_matches)
    if not residuals:
        return 0.0
    mean_residual = sum(residuals) / len(residuals)
    return _clamp(mean_residual * FORM_ADJUSTMENT_SCALE, -FORM_ADJUSTMENT_CAP, FORM_ADJUSTMENT_CAP)


def _clamp(value: float, floor: float, cap: float) -> float:
    return max(floor, min(cap, value))


def _round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))


def _poisson_pmf(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam**goals) / math.factorial(goals)


def _dixon_coles_tau(home_goals: int, away_goals: int, home_xg: float, away_xg: float, rho: float) -> float:
    if home_goals == 0 and away_goals == 0:
        return 1.0 - home_xg * away_xg * rho
    if home_goals == 0 and away_goals == 1:
        return 1.0 + home_xg * rho
    if home_goals == 1 and away_goals == 0:
        return 1.0 + away_xg * rho
    if home_goals == 1 and away_goals == 1:
        return 1.0 - rho
    return 1.0


def _goal_matrix(home_xg: float, away_xg: float, max_goals: int = 8, rho: float = DIXON_COLES_RHO) -> tuple[float, float, float]:
    home_win = draw = away_win = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = _poisson_pmf(home_xg, h) * _poisson_pmf(away_xg, a)
            if h <= 1 and a <= 1:
                p *= _dixon_coles_tau(h, a, home_xg, away_xg, rho)
            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p
    total = home_win + draw + away_win
    return home_win / total, draw / total, away_win / total


def _poisson_score_probabilities(home_xg: float, away_xg: float, max_goals: int = 8) -> dict[str, float]:
    both_teams_to_score = over_2_5 = clean_sheet_home = clean_sheet_away = total = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = _poisson_pmf(home_xg, h) * _poisson_pmf(away_xg, a)
            if h <= 1 and a <= 1:
                p *= _dixon_coles_tau(h, a, home_xg, away_xg, DIXON_COLES_RHO)
            total += p
            if h > 0 and a > 0:
                both_teams_to_score += p
            if h + a > 2:
                over_2_5 += p
            if a == 0:
                clean_sheet_home += p
            if h == 0:
                clean_sheet_away += p
    total = max(total, 1e-9)
    return {
        "both_teams_to_score_probability": round(_clamp(both_teams_to_score / total, 0.0, 1.0), 4),
        "over_2_5_goals_probability": round(_clamp(over_2_5 / total, 0.0, 1.0), 4),
        "clean_sheet_home_probability": round(_clamp(clean_sheet_home / total, 0.0, 1.0), 4),
        "clean_sheet_away_probability": round(_clamp(clean_sheet_away / total, 0.0, 1.0), 4),
    }


def predict_scoreline(home_strength: float, away_strength: float, total_goals: float = DEFAULT_TOTAL_GOALS, home_advantage: float = 0.0) -> tuple[int, int, float, float]:
    base_xg = SCORELINE_BASE_XG + (total_goals - DEFAULT_TOTAL_GOALS) * 0.25
    supremacy = ((home_strength - away_strength) / SCORELINE_DIVISOR) * SCORELINE_SLOPE + home_advantage
    home_xg = _clamp(base_xg + supremacy, SCORELINE_FLOOR_XG, SCORELINE_CAP_XG)
    away_xg = _clamp(base_xg - supremacy, SCORELINE_FLOOR_XG, SCORELINE_CAP_XG)
    return _round_half_up(home_xg), _round_half_up(away_xg), home_xg, away_xg


def calculate_confidence(probabilities: dict[str, float]) -> str:
    top_probability = max(probabilities.values())
    spread = top_probability - sorted(probabilities.values())[-2]
    if top_probability >= 0.62 and spread >= 0.22:
        return "High"
    if top_probability >= 0.48 and spread >= 0.12:
        return "Medium"
    return "Low"


def generate_predicted_match_stats(home_team: dict[str, Any], away_team: dict[str, Any], home_xg: float, away_xg: float, home_strength: float, away_strength: float, stage: str = "group") -> dict[str, Any]:
    pressure = _clamp((home_strength - away_strength) / 420.0, -1.0, 1.0)
    stage_pressure = 0.25 if stage.strip().lower() != "group" else 0.0
    home_possession = round(_clamp(50.0 + pressure * 13.0, 35.0, 65.0), 1)
    away_possession = round(100.0 - home_possession, 1)
    home_shots = max(5, _round_half_up(5.8 + home_xg * 4.7 + max(0.0, pressure) * 2.0))
    away_shots = max(5, _round_half_up(5.8 + away_xg * 4.7 + max(0.0, -pressure) * 2.0))
    home_shots_on_target = min(home_shots, max(1, _round_half_up(home_shots * (0.31 + min(0.08, home_xg / 30.0)))))
    away_shots_on_target = min(away_shots, max(1, _round_half_up(away_shots * (0.31 + min(0.08, away_xg / 30.0)))))
    home_corners = max(2, _round_half_up(2.2 + home_shots * 0.22 + max(0.0, pressure) * 1.2))
    away_corners = max(2, _round_half_up(2.2 + away_shots * 0.22 + max(0.0, -pressure) * 1.2))
    home_yellow_cards = _round_half_up(1.4 + stage_pressure + max(0.0, -pressure) * 1.2)
    away_yellow_cards = _round_half_up(1.4 + stage_pressure + max(0.0, pressure) * 1.2)
    score_probs = _poisson_score_probabilities(home_xg, away_xg)
    return {
        "expected_home_goals": round(home_xg, 2),
        "expected_away_goals": round(away_xg, 2),
        "home_shots": home_shots,
        "away_shots": away_shots,
        "home_shots_on_target": home_shots_on_target,
        "away_shots_on_target": away_shots_on_target,
        "home_possession": home_possession,
        "away_possession": away_possession,
        "home_corners": home_corners,
        "away_corners": away_corners,
        "home_yellow_cards": home_yellow_cards,
        "away_yellow_cards": away_yellow_cards,
        "home_red_card_probability": round(_clamp(0.035 + stage_pressure * 0.025 + max(0.0, -pressure) * 0.025, 0.015, 0.12), 4),
        "away_red_card_probability": round(_clamp(0.035 + stage_pressure * 0.025 + max(0.0, pressure) * 0.025, 0.015, 0.12), 4),
        **score_probs,
    }


def blend_model_and_market_probabilities(model_probs: dict[str, float], market_probs: dict[str, float] | None, market_weight: float = 0.3) -> dict[str, float]:
    if not market_probs:
        return model_probs
    model_weight = 1 - market_weight
    blended = {key: round(model_probs[key] * model_weight + market_probs[key] * market_weight, 4) for key in ("home", "draw", "away")}
    blended["draw"] = round(blended["draw"] + round(1 - sum(blended.values()), 4), 4)
    return blended


def compare_model_to_market(model_probs: dict[str, float], market_probs: dict[str, float] | None) -> dict[str, Any]:
    if not market_probs:
        return {"disagreement": False, "message": "No market consensus is available yet."}
    labels = {"home": "home team", "draw": "draw", "away": "away team"}
    model_pick = max(model_probs, key=model_probs.get)
    market_pick = max(market_probs, key=market_probs.get)
    if model_pick != market_pick:
        return {"disagreement": True, "message": f"Model favours {labels[model_pick]} while the market favours {labels[market_pick]}."}
    gap = model_probs[model_pick] - market_probs[market_pick]
    if abs(gap) >= 0.08:
        direction = "more strongly" if gap > 0 else "less strongly"
        return {"disagreement": True, "message": f"Model favours the {labels[model_pick]} {direction} than the market."}
    return {"disagreement": False, "message": "Model and market broadly agree on the favourite."}


def generate_explanation(home_team: dict[str, Any], away_team: dict[str, Any], features: dict[str, float], probabilities: dict[str, float]) -> list[str]:
    home_name = home_team["name"]
    away_name = away_team["name"]
    explanations: list[str] = []
    if features["strength_diff"] > 80:
        explanations.append(f"{home_name} rate higher on the blended Elo and FIFA ranking baseline.")
    elif features["strength_diff"] < -80:
        explanations.append(f"{away_name} rate higher on the blended Elo and FIFA ranking baseline.")
    else:
        explanations.append("The teams are close on the current strength baseline, so the result is uncertain.")
    supremacy = features["home_xg"] - features["away_xg"]
    if abs(supremacy) >= 0.6:
        leader = home_name if supremacy > 0 else away_name
        explanations.append(f"{leader} project for roughly {abs(supremacy):.1f} more expected goals over 90 minutes.")
    else:
        explanations.append("Expected goals are close, limiting confidence in a clear winner.")
    if features.get("home_advantage", 0) > 0:
        explanations.append(f"{home_name} carry a venue edge because the match is not at a neutral ground.")
    for prefix, name in (("home", home_name), ("away", away_name)):
        adjustment = features.get(f"{prefix}_form_adjustment", 0.0)
        residual = features.get(f"{prefix}_form_residual", 0.0)
        if abs(adjustment) >= FORM_EXPLANATION_THRESHOLD:
            verb = "outperformed" if adjustment > 0 else "underperformed"
            explanations.append(
                f"{name} have {verb} the model's own pre-match expectations by "
                f"{abs(residual):.1f} goals per game so far this tournament."
            )
    if probabilities["draw"] >= 0.25:
        explanations.append("A meaningful draw probability remains because tight tournament matches often finish level.")
    return explanations


def _is_third_place(stage: str) -> bool:
    return (stage or "").strip().lower() == THIRD_PLACE_STAGE


def predict_extra_time_and_penalties(home_strength: float, away_strength: float, draw_probability: float, stage: str = "group") -> dict[str, Any]:
    """Resolve a knockout tie that is level after 90 minutes.

    Two stages: 30 minutes of extra time, and — if still level — a penalty
    shootout. Returns the outcome split *conditional on the match being level
    after 90*, so the probabilities are independent of ``draw_probability``
    itself (it is accepted for call-site symmetry).

    Extra time uses a reduced total-goals baseline (``ET_TOTAL_GOALS``) and a
    dampened strength gap (``ET_SUPREMACY_DAMPENING``) because the period is
    short, cautious and fatigued. Penalties are treated as near-random: a small,
    hard-capped nudge off 50/50 for the stronger side. The third-place play-off
    skips extra time (FIFA rules) — a draw after 90 goes straight to penalties,
    so ``et_draw_probability`` is 1.0.
    """
    strength_diff = home_strength - away_strength

    # Penalties: heavily regressed toward a coin flip, then hard-capped.
    penalty_edge = _clamp(strength_diff / PENALTY_STRENGTH_DIVISOR, -PENALTY_MAX_EDGE, PENALTY_MAX_EDGE)
    penalty_home = round(0.5 + penalty_edge, 4)
    penalty_away = round(1.0 - penalty_home, 4)

    if _is_third_place(stage):
        return {
            "et_predicted_home_goals": 0,
            "et_predicted_away_goals": 0,
            "et_home_win_probability": 0.0,
            "et_draw_probability": 1.0,
            "et_away_win_probability": 0.0,
            "penalty_home_win_probability": penalty_home,
            "penalty_away_win_probability": penalty_away,
        }

    supremacy = (strength_diff / SCORELINE_DIVISOR) * SCORELINE_SLOPE * ET_SUPREMACY_DAMPENING
    base_xg = ET_TOTAL_GOALS / 2.0
    et_home_xg = _clamp(base_xg + supremacy, ET_FLOOR_XG, SCORELINE_CAP_XG)
    et_away_xg = _clamp(base_xg - supremacy, ET_FLOOR_XG, SCORELINE_CAP_XG)
    et_home_win, et_draw, et_away_win = _goal_matrix(et_home_xg, et_away_xg)
    return {
        "et_predicted_home_goals": _round_half_up(et_home_xg),
        "et_predicted_away_goals": _round_half_up(et_away_xg),
        "et_home_win_probability": round(et_home_win, 4),
        "et_draw_probability": round(et_draw, 4),
        "et_away_win_probability": round(et_away_win, 4),
        "penalty_home_win_probability": penalty_home,
        "penalty_away_win_probability": penalty_away,
    }


def resolve_advance_and_shootout(home_strength: float, away_strength: float, home_win_probability: float, draw_probability: float, away_win_probability: float, stage: str) -> dict[str, Any]:
    """Compose advance probability from three additive, disjoint paths per team.

    A team advances by winning in 90, winning in extra time (only reachable via
    a 90' draw), or winning the shootout (a draw after 90 *and* after ET). The
    three per-team contributions sum to that team's advance probability, and the
    two teams' advance probabilities sum to 1 (up to rounding).
    """
    et_pen = predict_extra_time_and_penalties(home_strength, away_strength, draw_probability, stage=stage)
    home_in_90 = home_win_probability
    away_in_90 = away_win_probability
    home_in_et = draw_probability * et_pen["et_home_win_probability"]
    away_in_et = draw_probability * et_pen["et_away_win_probability"]
    to_penalties = draw_probability * et_pen["et_draw_probability"]
    home_on_pens = to_penalties * et_pen["penalty_home_win_probability"]
    away_on_pens = to_penalties * et_pen["penalty_away_win_probability"]
    return {
        "home_win_in_90_probability": round(home_in_90, 4),
        "away_win_in_90_probability": round(away_in_90, 4),
        "home_win_in_et_probability": round(home_in_et, 4),
        "away_win_in_et_probability": round(away_in_et, 4),
        "home_win_on_penalties_probability": round(home_on_pens, 4),
        "away_win_on_penalties_probability": round(away_on_pens, 4),
        "home_advance_probability": round(home_in_90 + home_in_et + home_on_pens, 4),
        "away_advance_probability": round(away_in_90 + away_in_et + away_on_pens, 4),
        "et_predicted_home_goals": et_pen["et_predicted_home_goals"],
        "et_predicted_away_goals": et_pen["et_predicted_away_goals"],
        "et_home_win_probability": et_pen["et_home_win_probability"],
        "et_draw_probability": et_pen["et_draw_probability"],
        "et_away_win_probability": et_pen["et_away_win_probability"],
        "penalty_home_win_probability": et_pen["penalty_home_win_probability"],
        "penalty_away_win_probability": et_pen["penalty_away_win_probability"],
    }


def advance_breakdown_for_row(row: dict[str, Any]) -> dict[str, Any]:
    """Recompute the knockout advance/ET/penalty breakdown for a stored row.

    Used by the bracket and prediction endpoints to surface the response-only
    breakdown fields without persisting them. Returns ``{}`` for the group stage
    or when the 90' probabilities or team strengths are unavailable, so callers
    can merge unconditionally without clobbering existing values.
    """
    if (row.get("stage") or "").strip().lower() == "group":
        return {}
    home_win = row.get("home_win_probability")
    draw = row.get("draw_probability")
    away_win = row.get("away_win_probability")
    if home_win is None or draw is None or away_win is None:
        return {}
    strengths = (
        row.get("home_team_ranking"),
        row.get("home_team_elo"),
        row.get("away_team_ranking"),
        row.get("away_team_elo"),
    )
    if any(value is None for value in strengths):
        # No team-strength inputs (e.g. mocked rows) — leave existing advance as-is.
        return {}
    home_strength = calculate_team_strength({"fifa_ranking": row["home_team_ranking"], "elo_rating": row["home_team_elo"]})
    away_strength = calculate_team_strength({"fifa_ranking": row["away_team_ranking"], "elo_rating": row["away_team_elo"]})
    return resolve_advance_and_shootout(home_strength, away_strength, home_win, draw, away_win, row.get("stage") or "")


def predict_match(home_team: dict[str, Any], away_team: dict[str, Any], stage: str = "group", neutral_venue: bool = True, market_probs: dict[str, float] | None = None, home_form: list[dict[str, Any]] | None = None, away_form: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    # Tournament-form adjustment: 0.0 when no form data is supplied, so existing
    # callers (tests, the hypothetical-matchup /api/predict endpoint) are
    # unaffected. ``*_form`` are the ``get_recent_tournament_form`` rows.
    home_residuals = _form_residuals(home_form)
    away_residuals = _form_residuals(away_form)
    home_form_adjustment = calculate_form_adjustment(home_form or [])
    away_form_adjustment = calculate_form_adjustment(away_form or [])
    home_form_residual = sum(home_residuals) / len(home_residuals) if home_residuals else 0.0
    away_form_residual = sum(away_residuals) / len(away_residuals) if away_residuals else 0.0
    home_strength = calculate_team_strength(home_team, home_form_adjustment)
    away_strength = calculate_team_strength(away_team, away_form_adjustment)
    home_advantage = 0.0
    if not neutral_venue:
        home_strength += HOME_ADVANTAGE_STRENGTH
        home_advantage = HOME_ADVANTAGE_GOALS
    total_goals = STAGE_TOTAL_GOALS.get(stage.strip().lower(), DEFAULT_TOTAL_GOALS)
    predicted_home_goals, predicted_away_goals, home_xg, away_xg = predict_scoreline(home_strength, away_strength, total_goals=total_goals)
    home_win, draw, away_win = _goal_matrix(home_xg, away_xg)
    total = home_win + draw + away_win
    probabilities = {"home": round(home_win / total, 4), "draw": round(draw / total, 4), "away": round(away_win / total, 4)}
    probabilities["draw"] = round(probabilities["draw"] + round(1.0 - sum(probabilities.values()), 4), 4)
    market_comparison = compare_model_to_market(probabilities, market_probs)
    output_probs = blend_model_and_market_probabilities(probabilities, market_probs)
    response: dict[str, Any] = {
        "home_team": home_team["name"],
        "away_team": away_team["name"],
        "home_win_probability": output_probs["home"],
        "draw_probability": output_probs["draw"],
        "away_win_probability": output_probs["away"],
        "model_home_win_probability": probabilities["home"],
        "model_draw_probability": probabilities["draw"],
        "model_away_win_probability": probabilities["away"],
        "predicted_home_goals": predicted_home_goals,
        "predicted_away_goals": predicted_away_goals,
        "home_xg": round(home_xg, 2),
        "away_xg": round(away_xg, 2),
        "home_form_adjustment": round(home_form_adjustment, 2),
        "away_form_adjustment": round(away_form_adjustment, 2),
        "predicted_stats": generate_predicted_match_stats(home_team, away_team, home_xg, away_xg, home_strength, away_strength, stage=stage),
        "confidence": calculate_confidence(output_probs),
        "market_comparison": market_comparison,
        "explanation": generate_explanation(
            home_team,
            away_team,
            {
                "strength_diff": home_strength - away_strength,
                "home_xg": home_xg,
                "away_xg": away_xg,
                "home_advantage": home_advantage,
                "home_form_adjustment": home_form_adjustment,
                "away_form_adjustment": away_form_adjustment,
                "home_form_residual": home_form_residual,
                "away_form_residual": away_form_residual,
            },
            output_probs,
        ),
        "model_version": MODEL_VERSION,
    }
    if stage.strip().lower() != "group":
        # Two-stage knockout resolution: 90' win, else extra time, else shootout.
        # home_strength/away_strength already include any home-advantage bump.
        response.update(
            resolve_advance_and_shootout(
                home_strength,
                away_strength,
                output_probs["home"],
                output_probs["draw"],
                output_probs["away"],
                stage,
            )
        )
    return response
