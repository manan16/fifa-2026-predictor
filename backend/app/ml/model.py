import math
from typing import Any

MODEL_VERSION = "elo-supremacy-dc-v2"

# --- Tunable constants -------------------------------------------------------
# Average Elo of a "reference" national team. Ratings are interpreted relative
# to this anchor when blending with FIFA ranking.
ELO_REFERENCE = 1500.0

# Weight given to the live Elo rating vs. the FIFA-ranking-derived Elo when
# blending the two correlated-but-distinct strength signals.
ELO_WEIGHT = 0.7
RANKING_WEIGHT = 1.0 - ELO_WEIGHT

# Extra expected goals handed to the home side when the match is NOT at a
# neutral venue. Expressed directly in goal space (interpretable) rather than
# as an opaque Elo bump.
HOME_ADVANTAGE_GOALS = 0.35

# Dixon-Coles low-score correction. A small negative rho lifts the probability
# of 0-0 and 1-1 (and trims 1-0 / 0-1), which independent Poisson understates.
DIXON_COLES_RHO = -0.08

# Expected total goals by stage. Knockout football trends lower and tighter as
# the stakes rise, so later rounds carry a smaller goal budget.
STAGE_TOTAL_GOALS = {
    "group": 2.65,
    "round of 32": 2.55,
    "round of 16": 2.50,
    "quarter-finals": 2.45,
    "quarter finals": 2.45,
    "semi-finals": 2.40,
    "semi finals": 2.40,
    "final": 2.35,
}
DEFAULT_TOTAL_GOALS = 2.55

# Converts an Elo gap into an expected goal supremacy. ~0.34 goals per 100 Elo,
# clamped so extreme mismatches stay realistic.
GOALS_PER_100_ELO = 0.34
MAX_SUPREMACY = 2.6


def _ranking_to_elo(ranking: float) -> float:
    """Map a FIFA ranking (1 = best) onto an Elo-like scale.

    Rank 1 lands around 2090, rank 50 near the 1500 reference, and the curve
    flattens for weaker sides instead of running away linearly.
    """
    ranking = max(1.0, ranking)
    return ELO_REFERENCE + 600.0 * math.exp(-(ranking - 1.0) / 22.0) - 60.0


def calculate_team_strength(team: dict[str, Any]) -> float:
    """Blend live Elo with a ranking-derived Elo into one strength number.

    Replaces the old capped additive bonus, which double-counted strong teams
    and ignored everything past FIFA rank 100.
    """
    elo = float(team.get("elo_rating") or ELO_REFERENCE)
    ranking = float(team.get("fifa_ranking") or 50)
    ranking_elo = _ranking_to_elo(ranking)
    return ELO_WEIGHT * elo + RANKING_WEIGHT * ranking_elo


def _poisson_pmf(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam**goals) / math.factorial(goals)


def _dixon_coles_tau(home_goals: int, away_goals: int, home_xg: float, away_xg: float, rho: float) -> float:
    """Dixon-Coles dependence adjustment for low-scoring scorelines."""
    if home_goals == 0 and away_goals == 0:
        return 1.0 - home_xg * away_xg * rho
    if home_goals == 0 and away_goals == 1:
        return 1.0 + home_xg * rho
    if home_goals == 1 and away_goals == 0:
        return 1.0 + away_xg * rho
    if home_goals == 1 and away_goals == 1:
        return 1.0 - rho
    return 1.0


def _goal_matrix(
    home_xg: float,
    away_xg: float,
    max_goals: int = 8,
    rho: float = DIXON_COLES_RHO,
) -> tuple[float, float, float]:
    """Win / draw / loss probabilities from a Dixon-Coles adjusted Poisson grid."""
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
    both_teams_to_score = 0.0
    over_2_5 = 0.0
    clean_sheet_home = 0.0
    clean_sheet_away = 0.0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = _poisson_pmf(home_xg, h) * _poisson_pmf(away_xg, a)
            if h <= 1 and a <= 1:
                p *= _dixon_coles_tau(h, a, home_xg, away_xg, DIXON_COLES_RHO)
            if h > 0 and a > 0:
                both_teams_to_score += p
            if h + a > 2:
                over_2_5 += p
            if a == 0:
                clean_sheet_home += p
            if h == 0:
                clean_sheet_away += p

    return {
        "both_teams_to_score_probability": round(max(0.0, min(1.0, both_teams_to_score)), 4),
        "over_2_5_goals_probability": round(max(0.0, min(1.0, over_2_5)), 4),
        "clean_sheet_home_probability": round(max(0.0, min(1.0, clean_sheet_home)), 4),
        "clean_sheet_away_probability": round(max(0.0, min(1.0, clean_sheet_away)), 4),
    }


def predict_scoreline(
    home_strength: float,
    away_strength: float,
    total_goals: float = DEFAULT_TOTAL_GOALS,
    home_advantage: float = 0.0,
) -> tuple[int, int, float, float]:
    """Split a strength gap into expected goals via a supremacy / total model.

    ``total_goals`` is the expected goals in the match (stage dependent) and
    ``home_advantage`` is added directly to the home supremacy in goal space.
    """
    diff = home_strength - away_strength
    supremacy = (diff / 100.0) * GOALS_PER_100_ELO + home_advantage
    supremacy = max(-MAX_SUPREMACY, min(MAX_SUPREMACY, supremacy))

    home_xg = max(0.25, (total_goals + supremacy) / 2.0)
    away_xg = max(0.25, (total_goals - supremacy) / 2.0)
    return round(home_xg), round(away_xg), home_xg, away_xg


def calculate_confidence(probabilities: dict[str, float]) -> str:
    top_probability = max(probabilities.values())
    spread = top_probability - sorted(probabilities.values())[-2]
    if top_probability >= 0.62 and spread >= 0.22:
        return "High"
    if top_probability >= 0.48 and spread >= 0.12:
        return "Medium"
    return "Low"


def generate_predicted_match_stats(
    home_team: dict[str, Any],
    away_team: dict[str, Any],
    home_xg: float,
    away_xg: float,
    home_strength: float,
    away_strength: float,
    stage: str = "group",
) -> dict[str, Any]:
    strength_diff = home_strength - away_strength
    pressure = max(-1.0, min(1.0, strength_diff / 420.0))
    stage_pressure = 0.25 if stage.strip().lower() != "group" else 0.0

    home_possession = round(max(35.0, min(65.0, 50.0 + pressure * 13.0)), 1)
    away_possession = round(100.0 - home_possession, 1)

    home_shots = max(5, round(5.8 + home_xg * 4.7 + max(0.0, pressure) * 2.0))
    away_shots = max(5, round(5.8 + away_xg * 4.7 + max(0.0, -pressure) * 2.0))
    home_shots_on_target = min(home_shots, max(1, round(home_shots * (0.31 + min(0.08, home_xg / 30.0)))))
    away_shots_on_target = min(away_shots, max(1, round(away_shots * (0.31 + min(0.08, away_xg / 30.0)))))

    home_corners = max(2, round(2.2 + home_shots * 0.22 + max(0.0, pressure) * 1.2))
    away_corners = max(2, round(2.2 + away_shots * 0.22 + max(0.0, -pressure) * 1.2))

    home_yellow_cards = round(1.4 + stage_pressure + max(0.0, -pressure) * 1.2)
    away_yellow_cards = round(1.4 + stage_pressure + max(0.0, pressure) * 1.2)

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
        "home_red_card_probability": round(max(0.015, min(0.12, 0.035 + stage_pressure * 0.025 + max(0.0, -pressure) * 0.025)), 4),
        "away_red_card_probability": round(max(0.015, min(0.12, 0.035 + stage_pressure * 0.025 + max(0.0, pressure) * 0.025)), 4),
        **score_probs,
    }


def blend_model_and_market_probabilities(
    model_probs: dict[str, float],
    market_probs: dict[str, float] | None,
    market_weight: float = 0.3,
) -> dict[str, float]:
    if not market_probs:
        return model_probs
    model_weight = 1 - market_weight
    blended = {
        key: round(model_probs[key] * model_weight + market_probs[key] * market_weight, 4)
        for key in ("home", "draw", "away")
    }
    delta = round(1 - sum(blended.values()), 4)
    blended["draw"] = round(blended["draw"] + delta, 4)
    return blended


def compare_model_to_market(
    model_probs: dict[str, float],
    market_probs: dict[str, float] | None,
) -> dict[str, Any]:
    if not market_probs:
        return {"disagreement": False, "message": "No market consensus is available yet."}

    labels = {"home": "home team", "draw": "draw", "away": "away team"}
    model_pick = max(model_probs, key=model_probs.get)
    market_pick = max(market_probs, key=market_probs.get)
    if model_pick != market_pick:
        return {
            "disagreement": True,
            "message": f"Model favours {labels[model_pick]} while the market favours {labels[market_pick]}.",
        }

    gap = model_probs[model_pick] - market_probs[market_pick]
    if abs(gap) >= 0.08:
        direction = "more strongly" if gap > 0 else "less strongly"
        return {
            "disagreement": True,
            "message": f"Model favours the {labels[model_pick]} {direction} than the betting market.",
        }
    return {"disagreement": False, "message": "Model and market broadly agree on the favourite."}


def generate_explanation(
    home_team: dict[str, Any],
    away_team: dict[str, Any],
    features: dict[str, float],
    probabilities: dict[str, float],
) -> list[str]:
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
        explanations.append(
            f"{leader} project for roughly {abs(supremacy):.1f} more expected goals over 90 minutes."
        )
    else:
        explanations.append("Expected goals are close, limiting confidence in a clear winner.")

    if features.get("home_advantage", 0) > 0:
        explanations.append(f"{home_name} carry a venue edge because the match is not at a neutral ground.")

    if probabilities["draw"] >= 0.25:
        explanations.append("A meaningful draw probability remains because tight tournament matches often finish level.")

    return explanations


def predict_match(
    home_team: dict[str, Any],
    away_team: dict[str, Any],
    stage: str = "group",
    neutral_venue: bool = True,
    market_probs: dict[str, float] | None = None,
) -> dict[str, Any]:
    home_strength = calculate_team_strength(home_team)
    away_strength = calculate_team_strength(away_team)

    total_goals = STAGE_TOTAL_GOALS.get(stage.strip().lower(), DEFAULT_TOTAL_GOALS)
    home_advantage = 0.0 if neutral_venue else HOME_ADVANTAGE_GOALS

    predicted_home_goals, predicted_away_goals, home_xg, away_xg = predict_scoreline(
        home_strength, away_strength, total_goals=total_goals, home_advantage=home_advantage
    )
    home_win, draw, away_win = _goal_matrix(home_xg, away_xg)
    total = home_win + draw + away_win
    probabilities = {
        "home": round(home_win / total, 4),
        "draw": round(draw / total, 4),
        "away": round(away_win / total, 4),
    }
    rounding_delta = round(1.0 - sum(probabilities.values()), 4)
    probabilities["draw"] = round(probabilities["draw"] + rounding_delta, 4)

    # Optionally fold in betting-market consensus without discarding the model.
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
        "predicted_stats": generate_predicted_match_stats(
            home_team,
            away_team,
            home_xg,
            away_xg,
            home_strength,
            away_strength,
            stage=stage,
        ),
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
            },
            output_probs,
        ),
        "model_version": MODEL_VERSION,
    }

    if stage.strip().lower() != "group":
        no_draw_home_share = output_probs["home"] / max(0.01, output_probs["home"] + output_probs["away"])
        response["home_advance_probability"] = round(
            output_probs["home"] + output_probs["draw"] * no_draw_home_share, 4
        )
        response["away_advance_probability"] = round(1.0 - response["home_advance_probability"], 4)

    return response
