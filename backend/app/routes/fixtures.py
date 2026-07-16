from typing import Any

from flask import Blueprint, current_app, jsonify, request

from app.db import queries
from app.services import results_service, stats_prediction_service, stats_service

fixtures_bp = Blueprint("fixtures", __name__)

ACTUAL_STATS_FIELDS = (
    "home_shots",
    "away_shots",
    "home_shots_on_target",
    "away_shots_on_target",
    "home_possession",
    "away_possession",
    "home_corners",
    "away_corners",
    "home_yellow_cards",
    "away_yellow_cards",
    "home_red_cards",
    "away_red_cards",
)


def _number_payload_error(payload: dict[str, Any], fields: tuple[str, ...]) -> str | None:
    for field in fields:
        if field not in payload:
            return f"Missing required field: {field}"
        if payload[field] is None:
            return f"{field} is required"
        if not isinstance(payload[field], (int, float)):
            return f"{field} must be numeric"
    return None


def _validate_actual_stats(payload: dict[str, Any]) -> str | None:
    numeric_error = _number_payload_error(payload, ACTUAL_STATS_FIELDS)
    if numeric_error:
        return numeric_error

    if round(float(payload["home_possession"]) + float(payload["away_possession"]), 6) != 100:
        return "home_possession and away_possession must add up to 100"

    if payload["home_shots_on_target"] > payload["home_shots"]:
        return "home_shots_on_target cannot exceed home_shots"
    if payload["away_shots_on_target"] > payload["away_shots"]:
        return "away_shots_on_target cannot exceed away_shots"

    for field in ("home_yellow_cards", "away_yellow_cards", "home_red_cards", "away_red_cards"):
        if payload[field] < 0:
            return f"{field} cannot be negative"

    return None


@fixtures_bp.get("")
def get_fixtures():
    fixtures = queries.get_all_fixtures()
    has_completed = any(
        fixture.get("actual_home_score") is not None and fixture.get("actual_away_score") is not None
        for fixture in fixtures
    )
    if not has_completed and not current_app.config.get("TESTING"):
        try:
            stats_service.sync_wikipedia_match_stats()
            fixtures = queries.get_all_fixtures()
        except Exception as exc:
            print(f"Wikipedia fixture refresh failed: {exc}")
    return jsonify(fixtures)


@fixtures_bp.get("/<int:fixture_id>")
def get_fixture(fixture_id: int):
    fixture = queries.get_fixture_with_prediction_odds_and_result(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify(fixture)


@fixtures_bp.get("/<int:fixture_id>/odds")
def get_fixture_odds(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify(
        {
            "fixture": fixture,
            "odds": queries.get_fixture_odds(fixture_id),
            "consensus": queries.get_odds_consensus_by_fixture_id(fixture_id),
        }
    )


@fixtures_bp.get("/<int:fixture_id>/stats")
def get_fixture_stats(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    predicted = stats_prediction_service.get_predicted_match_stats(fixture_id)
    actual = stats_prediction_service.get_actual_match_stats(fixture_id)
    return jsonify(
        {
            "fixture_id": fixture_id,
            "predicted": predicted,
            "actual": actual,
            "predicted_stats": predicted,
            "actual_stats": actual,
            "note": "Stats are model-generated estimates, not official data.",
        }
    )


@fixtures_bp.get("/<int:fixture_id>/match-stats")
def get_fixture_match_stats(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    stats = queries.get_fixture_match_stats(fixture_id)
    return jsonify(
        {
            "home": stats["home"],
            "away": stats["away"],
            "source": "Wikipedia",
            "source_note": "Match stats via Wikipedia (CC BY-SA).",
        }
    )


@fixtures_bp.post("/<int:fixture_id>/actual-stats")
def upsert_actual_match_stats(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404

    payload = request.get_json(silent=True) or {}
    validation_error = _validate_actual_stats(payload)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    stats = {field: payload[field] for field in ACTUAL_STATS_FIELDS}
    source = payload.get("source") or "manual_demo"
    saved = queries.upsert_actual_match_stats(fixture_id, stats, source)
    return jsonify(saved), 201


@fixtures_bp.post("/<int:fixture_id>/result")
def update_fixture_result(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404

    payload = request.get_json(silent=True) or {}
    numeric_error = _number_payload_error(payload, ("actual_home_score", "actual_away_score"))
    if numeric_error:
        return jsonify({"error": numeric_error}), 400

    updated = results_service.update_fixture_result(
        fixture_id=fixture_id,
        actual_home_score=int(payload["actual_home_score"]),
        actual_away_score=int(payload["actual_away_score"]),
        status=payload.get("status") or "completed",
        winner_team_name=payload.get("winner_team_name"),
        home_penalties=payload.get("home_penalties"),
        away_penalties=payload.get("away_penalties"),
    )
    if updated is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify(updated)


@fixtures_bp.get("/<int:fixture_id>/watch")
def get_fixture_watch_links(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify({"fixture_id": fixture_id, "links": queries.get_watch_links(fixture_id)})
