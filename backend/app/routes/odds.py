from flask import Blueprint, jsonify

from app.db import queries

odds_bp = Blueprint("odds", __name__)


@odds_bp.get("/odds")
def get_odds():
    return jsonify(queries.get_latest_odds())
