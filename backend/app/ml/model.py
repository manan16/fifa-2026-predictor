import math
from typing import Any

MODEL_VERSION = "elo-baseline-v1"


def calculate_team_strength(team: dict[str, Any]) -> float:
    elo = float(team.get("elo_rating") or 1500)
    ranking = float(team.get("fifa_ranking") or 75)
    ranking_bonus = max(0.0, (100.0 - ranking) * 2.2)
    return elo + ranking_bonus


def _poisson_pmf(lam: float, goals: int) -> float:
    return math.exp(-lam) * (lam**goals) / math.factorial(goals)


def _goal_matrix(home_xg: float, away_xg: float, max_goals: int = 7) -> tuple[float, float, float]:
    home_win = draw = away_win = 0.0
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            p = _poisson_pmf(home_xg, h) * _poisson_pmf(away_xg, a)
            if h > a:
                home_win += p
            elif h == a:
                draw += p
            else:
                away_win += p
    total = home_win + draw + away_win
    return home_win / total, draw / total, away_win / total


def predict_scoreline(home_strength: float, away_strength: float) -> tuple[int, int, float, float]:
    diff = (home_strength - away_strength) / 400.0
    home_xg = min(3.2, max(0.45, 1.35 + diff * 0.9))
    away_xg = min(3.2, max(0.45, 1.15 - diff * 0.75))
    return round(home_xg), round(away_xg), home_xg, away_xg


def calculate_confidence(probabilities: dict[str, float]) -> str:
    top_probability = max(probabilities.values())
    spread = top_probability - sorted(probabilities.values())[-2]
    if top_probability >= 0.62 and spread >= 0.22:
        return "High"
    if top_probability >= 0.48 and spread >= 0.12:
        return "Medium"
    return "Low"


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
        explanations.append(f"{home_name} rate higher on the combined Elo and FIFA ranking baseline.")
    elif features["strength_diff"] < -80:
        explanations.append(f"{away_name} rate higher on the combined Elo and FIFA ranking baseline.")
    else:
        explanations.append("The teams are close on the current strength baseline, so the result is uncertain.")

    if probabilities["draw"] >= 0.25:
        explanations.append("The model keeps a meaningful draw probability because neutral tournament matches are often tight.")

    if features["home_xg"] > features["away_xg"] + 0.35:
        explanations.append(f"{home_name} project for the stronger attacking output.")
    elif features["away_xg"] > features["home_xg"] + 0.35:
        explanations.append(f"{away_name} project for the stronger attacking output.")
    else:
        explanations.append("Expected goals are relatively close, limiting confidence in a clear winner.")

    return explanations


def predict_match(
    home_team: dict[str, Any],
    away_team: dict[str, Any],
    stage: str = "group",
    neutral_venue: bool = True,
) -> dict[str, Any]:
    home_strength = calculate_team_strength(home_team)
    away_strength = calculate_team_strength(away_team)
    if not neutral_venue:
        home_strength += 55

    predicted_home_goals, predicted_away_goals, home_xg, away_xg = predict_scoreline(
        home_strength, away_strength
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

    response: dict[str, Any] = {
        "home_team": home_team["name"],
        "away_team": away_team["name"],
        "home_win_probability": probabilities["home"],
        "draw_probability": probabilities["draw"],
        "away_win_probability": probabilities["away"],
        "predicted_home_goals": predicted_home_goals,
        "predicted_away_goals": predicted_away_goals,
        "confidence": calculate_confidence(probabilities),
        "explanation": generate_explanation(
            home_team,
            away_team,
            {
                "strength_diff": home_strength - away_strength,
                "home_xg": home_xg,
                "away_xg": away_xg,
            },
            probabilities,
        ),
        "model_version": MODEL_VERSION,
    }

    if stage.lower() != "group":
        no_draw_home_share = probabilities["home"] / max(0.01, probabilities["home"] + probabilities["away"])
        response["home_advance_probability"] = round(probabilities["home"] + probabilities["draw"] * no_draw_home_share, 4)
        response["away_advance_probability"] = round(1.0 - response["home_advance_probability"], 4)

    return response

