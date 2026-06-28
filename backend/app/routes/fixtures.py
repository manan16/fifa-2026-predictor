from flask import Blueprint, jsonify

from app.db import queries
from app.services import stats_prediction_service

fixtures_bp = Blueprint("fixtures", __name__)


@fixtures_bp.get("")
def get_fixtures():
    return jsonify(queries.get_all_fixtures())


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


@fixtures_bp.get("/<int:fixture_id>/watch")
def get_fixture_watch_links(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify({"fixture_id": fixture_id, "links": queries.get_watch_links(fixture_id)})
