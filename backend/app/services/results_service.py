from __future__ import annotations

import os
from typing import Any

from app.db.connection import get_connection


def fetch_latest_results() -> list[dict[str, Any]]:
    if not os.getenv("RESULTS_API_KEY") or not os.getenv("RESULTS_API_BASE_URL"):
        return []
    # TODO: Integrate API-Football or another licensed results provider here.
    return []


def determine_knockout_winner(fixture: dict[str, Any]) -> int | None:
    home_score = fixture.get("actual_home_score")
    away_score = fixture.get("actual_away_score")
    if home_score is None or away_score is None:
        return None
    if home_score > away_score:
        return fixture.get("home_team_id")
    if away_score > home_score:
        return fixture.get("away_team_id")

    home_penalties = fixture.get("home_penalties")
    away_penalties = fixture.get("away_penalties")
    if home_penalties is not None and away_penalties is not None:
        if home_penalties > away_penalties:
            return fixture.get("home_team_id")
        if away_penalties > home_penalties:
            return fixture.get("away_team_id")
    return None


def update_fixture_result(
    fixture_id: int,
    actual_home_score: int,
    actual_away_score: int,
    status: str,
    winner_team_name: str | None = None,
    home_penalties: int | None = None,
    away_penalties: int | None = None,
) -> dict[str, Any] | None:
    conn = get_connection()
    with conn.cursor() as cur:
        winner_expr = "(SELECT id FROM teams WHERE LOWER(name) = LOWER(%s))" if winner_team_name else "NULL"
        cur.execute(
            f"""
            UPDATE fixtures
            SET actual_home_score = %s,
                actual_away_score = %s,
                home_score = %s,
                away_score = %s,
                home_penalties = %s,
                away_penalties = %s,
                status = %s,
                winner_team_id = {winner_expr},
                result_source = 'manual_or_api',
                last_result_sync = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *;
            """,
            (
                actual_home_score,
                actual_away_score,
                actual_home_score,
                actual_away_score,
                home_penalties,
                away_penalties,
                status,
                *( [winner_team_name] if winner_team_name else [] ),
                fixture_id,
            ),
        )
        result = cur.fetchone()
    conn.commit()
    return result


def advance_winners_in_bracket() -> int:
    # TODO: Build dynamic bracket mutation once future-round placeholders are modelled explicitly.
    return 0
