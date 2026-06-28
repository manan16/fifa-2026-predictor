from flask import Blueprint, jsonify

from app.db import queries

teams_bp = Blueprint("teams", __name__)


@teams_bp.get("")
def get_teams():
    return jsonify(queries.get_all_teams())


@teams_bp.get("/<int:team_id>")
def get_team(team_id: int):
    team = queries.get_team_by_id(team_id)
    if team is None:
        return jsonify({"error": "Team not found"}), 404
    return jsonify(team)

