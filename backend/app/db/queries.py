from typing import Any

from app.db.connection import get_connection, get_dict_cursor
from psycopg.types.json import Jsonb


def get_all_teams() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute("SELECT * FROM teams ORDER BY fifa_ranking NULLS LAST, name;")
        return list(cur.fetchall())


def get_team_by_id(team_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute("SELECT * FROM teams WHERE id = %s;", (team_id,))
        return cur.fetchone()


def get_team_by_name(name: str) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute("SELECT * FROM teams WHERE LOWER(name) = LOWER(%s);", (name,))
        return cur.fetchone()


def get_all_fixtures() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                f.*,
                ht.name AS home_team_name,
                ht.fifa_code AS home_team_code,
                ht.elo_rating AS home_team_elo,
                at.name AS away_team_name,
                at.fifa_code AS away_team_code,
                at.elo_rating AS away_team_elo
            FROM fixtures f
            LEFT JOIN teams ht ON f.home_team_id = ht.id
            LEFT JOIN teams at ON f.away_team_id = at.id
            ORDER BY f.kickoff_time, f.match_number;
            """
        )
        return list(cur.fetchall())


def get_fixture_by_id(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                f.*,
                ht.name AS home_team_name,
                ht.fifa_code AS home_team_code,
                ht.fifa_ranking AS home_team_ranking,
                ht.elo_rating AS home_team_elo,
                at.name AS away_team_name,
                at.fifa_code AS away_team_code,
                at.fifa_ranking AS away_team_ranking,
                at.elo_rating AS away_team_elo
            FROM fixtures f
            LEFT JOIN teams ht ON f.home_team_id = ht.id
            LEFT JOIN teams at ON f.away_team_id = at.id
            WHERE f.id = %s;
            """,
            (fixture_id,),
        )
        return cur.fetchone()


def get_all_predictions() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                p.id,
                p.fixture_id,
                p.model_version,
                p.home_win_probability::float AS home_win_probability,
                p.draw_probability::float AS draw_probability,
                p.away_win_probability::float AS away_win_probability,
                p.predicted_home_goals,
                p.predicted_away_goals,
                p.confidence,
                p.explanation_json,
                p.created_at,
                f.match_number,
                ht.name AS home_team_name,
                at.name AS away_team_name
            FROM predictions p
            JOIN fixtures f ON p.fixture_id = f.id
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            ORDER BY f.match_number;
            """
        )
        return list(cur.fetchall())


def get_prediction_by_fixture_id(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                p.id,
                p.fixture_id,
                p.model_version,
                p.home_win_probability::float AS home_win_probability,
                p.draw_probability::float AS draw_probability,
                p.away_win_probability::float AS away_win_probability,
                p.predicted_home_goals,
                p.predicted_away_goals,
                p.confidence,
                p.explanation_json,
                p.created_at,
                f.stage,
                ht.name AS home_team_name,
                at.name AS away_team_name
            FROM predictions p
            JOIN fixtures f ON p.fixture_id = f.id
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            WHERE p.fixture_id = %s
            ORDER BY p.created_at DESC
            LIMIT 1;
            """,
            (fixture_id,),
        )
        return cur.fetchone()


def insert_prediction(prediction_data: dict[str, Any]) -> dict[str, Any]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO predictions (
                fixture_id,
                model_version,
                home_win_probability,
                draw_probability,
                away_win_probability,
                predicted_home_goals,
                predicted_away_goals,
                confidence,
                explanation_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                prediction_data["fixture_id"],
                prediction_data.get("model_version", "elo-baseline-v1"),
                prediction_data["home_win_probability"],
                prediction_data["draw_probability"],
                prediction_data["away_win_probability"],
                prediction_data["predicted_home_goals"],
                prediction_data["predicted_away_goals"],
                prediction_data["confidence"],
                Jsonb(prediction_data["explanation"]),
            ),
        )
        result = cur.fetchone()
    conn.commit()
    return result
