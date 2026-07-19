from typing import Any

from flask import Blueprint, jsonify

from app.db import queries
from app.ml import model

bracket_bp = Blueprint("bracket", __name__)

ROUND_KEYS = {
    "Round of 32": "round_of_32",
    "Round of 16": "round_of_16",
    "Quarter-final": "quarter_finals",
    "Semi-final": "semi_finals",
    "Final": "final",
}


def _predicted_winner(fixture: dict[str, Any]) -> str:
    home_advance = fixture.get("home_advance_probability")
    away_advance = fixture.get("away_advance_probability")
    if home_advance is not None and away_advance is not None and home_advance != away_advance:
        return fixture["home_team_name"] if home_advance > away_advance else fixture["away_team_name"]

    home_win = fixture.get("home_win_probability")
    away_win = fixture.get("away_win_probability")
    if home_win is not None and away_win is not None and home_win != away_win:
        return fixture["home_team_name"] if home_win > away_win else fixture["away_team_name"]

    return "TBD"


def _round_probability(value: float | None) -> float | None:
    return round(value, 4) if value is not None else None


@bracket_bp.get("/bracket")
def get_bracket():
    grouped: dict[str, list[dict[str, Any]]] = {key: [] for key in ROUND_KEYS.values()}

    for fixture in queries.get_bracket_fixtures():
        stage_key = ROUND_KEYS.get(fixture["stage"])
        if stage_key is None:
            continue

        normalized = {
            **fixture,
            "home_win_probability": _round_probability(fixture.get("home_win_probability")),
            "draw_probability": _round_probability(fixture.get("draw_probability")),
            "away_win_probability": _round_probability(fixture.get("away_win_probability")),
            "home_advance_probability": _round_probability(fixture.get("home_advance_probability")),
            "away_advance_probability": _round_probability(fixture.get("away_advance_probability")),
        }
        # Surface the extra-time/penalty breakdown (and a model-consistent advance
        # probability) by recomputing from the row's 90' probabilities and team
        # strengths. No-ops for rows without team strengths, keeping the SQL-derived
        # advance in that case.
        normalized.update(model.advance_breakdown_for_row(normalized))
        normalized["predicted_winner"] = _predicted_winner(normalized)
        grouped[stage_key].append(normalized)

    return jsonify(grouped)
