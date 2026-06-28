from flask import Blueprint, jsonify

from app.db import queries

fixtures_bp = Blueprint("fixtures", __name__)


@fixtures_bp.get("")
def get_fixtures():
    return jsonify(queries.get_all_fixtures())


@fixtures_bp.get("/<int:fixture_id>")
def get_fixture(fixture_id: int):
    fixture = queries.get_fixture_by_id(fixture_id)
    if fixture is None:
        return jsonify({"error": "Fixture not found"}), 404
    return jsonify(fixture)

