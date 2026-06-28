from typing import Any

from app.db import queries
from app.ml.model import calculate_team_strength, generate_predicted_match_stats as generate_model_stats


def generate_predicted_match_stats(
    home_team: dict[str, Any],
    away_team: dict[str, Any],
    prediction: dict[str, Any],
    stage: str,
) -> dict[str, Any]:
    home_strength = calculate_team_strength(home_team)
    away_strength = calculate_team_strength(away_team)
    home_xg = prediction.get("home_xg", prediction.get("expected_home_goals", prediction.get("predicted_home_goals", 1.0)))
    away_xg = prediction.get("away_xg", prediction.get("expected_away_goals", prediction.get("predicted_away_goals", 1.0)))
    stats = generate_model_stats(home_team, away_team, float(home_xg), float(away_xg), home_strength, away_strength, stage)
    validate_predicted_match_stats(stats)
    return stats


def validate_predicted_match_stats(stats: dict[str, Any]) -> None:
    if round(stats["home_possession"] + stats["away_possession"], 6) != 100:
        raise ValueError("Predicted possession must sum to 100")
    if stats["home_shots_on_target"] > stats["home_shots"] or stats["away_shots_on_target"] > stats["away_shots"]:
        raise ValueError("Predicted shots on target cannot exceed total shots")

    probability_fields = (
        "home_red_card_probability",
        "away_red_card_probability",
        "both_teams_to_score_probability",
        "over_2_5_goals_probability",
        "clean_sheet_home_probability",
        "clean_sheet_away_probability",
    )
    for field in probability_fields:
        if not 0 <= stats[field] <= 1:
            raise ValueError(f"{field} must be between 0 and 1")


def save_predicted_match_stats(
    fixture_id: int,
    stats: dict[str, Any],
    model_version: str = "elo-baseline-v1",
    explanation: list[str] | None = None,
) -> dict[str, Any]:
    validate_predicted_match_stats(stats)
    return queries.insert_predicted_match_stats(fixture_id, stats, model_version, explanation)


def get_predicted_match_stats(fixture_id: int) -> dict[str, Any] | None:
    return queries.get_predicted_match_stats(fixture_id)


def get_actual_match_stats(fixture_id: int) -> dict[str, Any] | None:
    return queries.get_actual_match_stats(fixture_id)
