from flask import Blueprint, jsonify, request

from app.db import queries
from app.ml.model import predict_match

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.get("/predictions")
def get_predictions():
    return jsonify(queries.get_all_predictions())


@predictions_bp.get("/predictions/<int:fixture_id>")
def get_prediction(fixture_id: int):
    prediction = queries.get_prediction_by_fixture_id(fixture_id)
    if prediction is not None:
        return jsonify(prediction)

    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404

    home_team = queries.get_team_by_id(fixture["home_team_id"])
    away_team = queries.get_team_by_id(fixture["away_team_id"])
    prediction = predict_match(home_team, away_team, stage=fixture["stage"], neutral_venue=True)
    saved = queries.insert_prediction({"fixture_id": fixture_id, **prediction})
    return jsonify(saved), 201


@predictions_bp.post("/predict")
def predict_custom_match():
    payload = request.get_json(silent=True) or {}
    missing_fields = [field for field in ("home_team", "away_team") if not payload.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    home_team = queries.get_team_by_name(payload["home_team"])
    away_team = queries.get_team_by_name(payload["away_team"])
    if home_team is None or away_team is None:
        return jsonify({"error": "Both teams must exist in the database"}), 404

    prediction = predict_match(
        home_team,
        away_team,
        stage=payload.get("stage", "group"),
        neutral_venue=payload.get("neutral_venue", True),
    )
    return jsonify(prediction)

