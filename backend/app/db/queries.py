from typing import Any

from app.db.connection import get_connection, get_dict_cursor
from psycopg.types.json import Jsonb

KNOCKOUT_STAGES = (
    "Round of 32",
    "Round of 16",
    "Quarter-final",
    "Semi-final",
    "Final",
)

PREDICTED_STATS_COLUMNS = (
    "expected_home_goals",
    "expected_away_goals",
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
    "home_red_card_probability",
    "away_red_card_probability",
    "both_teams_to_score_probability",
    "over_2_5_goals_probability",
    "clean_sheet_home_probability",
    "clean_sheet_away_probability",
)


PREDICTED_STATS_SELECT = """
    ps.expected_home_goals::float AS expected_home_goals,
    ps.expected_away_goals::float AS expected_away_goals,
    ps.home_shots,
    ps.away_shots,
    ps.home_shots_on_target,
    ps.away_shots_on_target,
    ps.home_possession::float AS home_possession,
    ps.away_possession::float AS away_possession,
    ps.home_corners,
    ps.away_corners,
    ps.home_yellow_cards,
    ps.away_yellow_cards,
    ps.home_red_card_probability::float AS home_red_card_probability,
    ps.away_red_card_probability::float AS away_red_card_probability,
    ps.both_teams_to_score_probability::float AS both_teams_to_score_probability,
    ps.over_2_5_goals_probability::float AS over_2_5_goals_probability,
    ps.clean_sheet_home_probability::float AS clean_sheet_home_probability,
    ps.clean_sheet_away_probability::float AS clean_sheet_away_probability
"""

WATCH_LINK_SELECT = """
    id,
    fixture_id,
    region,
    provider_name,
    provider_type,
    url,
    is_official,
    note,
    created_at,
    updated_at
"""


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
                f.id,
                f.match_number,
                f.stage,
                f.group_name,
                f.home_team_id,
                f.away_team_id,
                f.venue,
                f.city,
                to_char(f.kickoff_time, 'YYYY-MM-DD"T"HH24:MI:SS') AS kickoff_time,
                f.status,
                COALESCE(f.actual_home_score, f.home_score) AS actual_home_score,
                COALESCE(f.actual_away_score, f.away_score) AS actual_away_score,
                f.home_penalties,
                f.away_penalties,
                f.winner_team_id,
                wt.name AS actual_winner,
                f.last_odds_sync,
                f.last_result_sync,
                ht.name AS home_team_name,
                ht.fifa_code AS home_team_code,
                ht.elo_rating AS home_team_elo,
                at.name AS away_team_name,
                at.fifa_code AS away_team_code,
                at.elo_rating AS away_team_elo,
                p.predicted_home_goals,
                p.predicted_away_goals,
                p.home_win_probability::float AS home_win_probability,
                p.draw_probability::float AS draw_probability,
                p.away_win_probability::float AS away_win_probability,
                p.confidence,
                p.model_version,
                p.created_at AS prediction_created_at,
                oc.home_probability::float AS market_home_probability,
                oc.draw_probability::float AS market_draw_probability,
                oc.away_probability::float AS market_away_probability,
                oc.average_home_odds::float AS average_home_odds,
                oc.average_draw_odds::float AS average_draw_odds,
                oc.average_away_odds::float AS average_away_odds,
                oc.best_home_odds::float AS best_home_odds,
                oc.best_draw_odds::float AS best_draw_odds,
                oc.best_away_odds::float AS best_away_odds,
                oc.bookmaker_count,
                ps.expected_home_goals::float AS expected_home_goals,
                ps.expected_away_goals::float AS expected_away_goals,
                ps.home_shots,
                ps.away_shots,
                ps.home_shots_on_target,
                ps.away_shots_on_target,
                ps.home_possession::float AS home_possession,
                ps.away_possession::float AS away_possession,
                ps.home_corners,
                ps.away_corners,
                ps.home_yellow_cards,
                ps.away_yellow_cards,
                ps.home_red_card_probability::float AS home_red_card_probability,
                ps.away_red_card_probability::float AS away_red_card_probability,
                ps.both_teams_to_score_probability::float AS both_teams_to_score_probability,
                ps.over_2_5_goals_probability::float AS over_2_5_goals_probability,
                ps.clean_sheet_home_probability::float AS clean_sheet_home_probability,
                ps.clean_sheet_away_probability::float AS clean_sheet_away_probability
            FROM fixtures f
            LEFT JOIN teams ht ON f.home_team_id = ht.id
            LEFT JOIN teams at ON f.away_team_id = at.id
            LEFT JOIN teams wt ON f.winner_team_id = wt.id
            LEFT JOIN LATERAL (
                SELECT *
                FROM predictions p
                WHERE p.fixture_id = f.id
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT 1
            ) p ON true
            LEFT JOIN LATERAL (
                SELECT *
                FROM odds_consensus oc
                WHERE oc.fixture_id = f.id AND oc.market_key = 'h2h'
                ORDER BY oc.calculated_at DESC, oc.id DESC
                LIMIT 1
            ) oc ON true
            LEFT JOIN LATERAL (
                SELECT *
                FROM predicted_match_stats ps
                WHERE ps.fixture_id = f.id
                ORDER BY ps.created_at DESC, ps.id DESC
                LIMIT 1
            ) ps ON true
            ORDER BY f.kickoff_time, f.match_number;
            """
        )
        return list(cur.fetchall())


def get_fixture_by_id(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            WITH latest_predictions AS (
                SELECT DISTINCT ON (fixture_id)
                    fixture_id,
                    home_win_probability::float AS home_win_probability,
                    draw_probability::float AS draw_probability,
                    away_win_probability::float AS away_win_probability,
                    predicted_home_goals,
                    predicted_away_goals,
                    confidence,
                    created_at
                FROM predictions
                WHERE fixture_id = %s
                ORDER BY fixture_id, created_at DESC, id DESC
            ),
            latest_consensus AS (
                SELECT DISTINCT ON (fixture_id, market_key)
                    fixture_id,
                    market_key,
                    home_probability::float AS market_home_probability,
                    draw_probability::float AS market_draw_probability,
                    away_probability::float AS market_away_probability,
                    bookmaker_count,
                    average_home_odds::float AS average_home_odds,
                    average_draw_odds::float AS average_draw_odds,
                    average_away_odds::float AS average_away_odds,
                    best_home_odds::float AS best_home_odds,
                    best_draw_odds::float AS best_draw_odds,
                    best_away_odds::float AS best_away_odds,
                    source AS odds_source,
                    calculated_at
                FROM odds_consensus
                WHERE fixture_id = %s AND market_key = 'h2h'
                ORDER BY fixture_id, market_key, calculated_at DESC, id DESC
            ),
            latest_stats AS (
                SELECT DISTINCT ON (fixture_id)
                    *
                FROM predicted_match_stats
                WHERE fixture_id = %s
                ORDER BY fixture_id, created_at DESC, id DESC
            )
            SELECT
                f.id,
                f.match_number,
                f.stage,
                f.group_name,
                f.home_team_id,
                f.away_team_id,
                f.venue,
                f.city,
                to_char(f.kickoff_time, 'YYYY-MM-DD"T"HH24:MI:SS') AS kickoff_time,
                f.status,
                COALESCE(f.actual_home_score, f.home_score) AS actual_home_score,
                COALESCE(f.actual_away_score, f.away_score) AS actual_away_score,
                f.home_penalties,
                f.away_penalties,
                f.winner_team_id,
                wt.name AS actual_winner,
                f.last_odds_sync,
                f.last_result_sync,
                ht.name AS home_team_name,
                ht.fifa_code AS home_team_code,
                ht.fifa_ranking AS home_team_ranking,
                ht.elo_rating AS home_team_elo,
                at.name AS away_team_name,
                at.fifa_code AS away_team_code,
                at.fifa_ranking AS away_team_ranking,
                at.elo_rating AS away_team_elo,
                lp.predicted_home_goals,
                lp.predicted_away_goals,
                lp.confidence,
                lp.home_win_probability,
                lp.draw_probability,
                lp.away_win_probability,
                lc.market_home_probability,
                lc.market_draw_probability,
                lc.market_away_probability,
                lc.average_home_odds,
                lc.average_draw_odds,
                lc.average_away_odds,
                lc.best_home_odds,
                lc.best_draw_odds,
                lc.best_away_odds,
                lc.bookmaker_count,
                lc.calculated_at AS odds_calculated_at,
                ps.expected_home_goals::float AS expected_home_goals,
                ps.expected_away_goals::float AS expected_away_goals,
                ps.home_shots,
                ps.away_shots,
                ps.home_shots_on_target,
                ps.away_shots_on_target,
                ps.home_possession::float AS home_possession,
                ps.away_possession::float AS away_possession,
                ps.home_corners,
                ps.away_corners,
                ps.home_yellow_cards,
                ps.away_yellow_cards,
                ps.home_red_card_probability::float AS home_red_card_probability,
                ps.away_red_card_probability::float AS away_red_card_probability,
                ps.both_teams_to_score_probability::float AS both_teams_to_score_probability,
                ps.over_2_5_goals_probability::float AS over_2_5_goals_probability,
                ps.clean_sheet_home_probability::float AS clean_sheet_home_probability,
                ps.clean_sheet_away_probability::float AS clean_sheet_away_probability
            FROM fixtures f
            LEFT JOIN teams ht ON f.home_team_id = ht.id
            LEFT JOIN teams at ON f.away_team_id = at.id
            LEFT JOIN teams wt ON f.winner_team_id = wt.id
            LEFT JOIN latest_predictions lp ON lp.fixture_id = f.id
            LEFT JOIN latest_consensus lc ON lc.fixture_id = f.id
            LEFT JOIN latest_stats ps ON ps.fixture_id = f.id
            WHERE f.id = %s;
            """,
            (fixture_id, fixture_id, fixture_id, fixture_id),
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


def get_bracket_fixtures() -> list[dict[str, Any]]:
    return get_bracket_fixtures_with_odds_results()


def get_bracket_fixtures_with_odds_results() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            WITH latest_predictions AS (
                SELECT DISTINCT ON (fixture_id)
                    fixture_id,
                    home_win_probability::float AS home_win_probability,
                    draw_probability::float AS draw_probability,
                    away_win_probability::float AS away_win_probability,
                    predicted_home_goals,
                    predicted_away_goals,
                    confidence,
                    created_at
                FROM predictions
                ORDER BY fixture_id, created_at DESC, id DESC
            ),
            latest_consensus AS (
                SELECT DISTINCT ON (fixture_id, market_key)
                    fixture_id,
                    market_key,
                    home_probability::float AS market_home_probability,
                    draw_probability::float AS market_draw_probability,
                    away_probability::float AS market_away_probability,
                    bookmaker_count,
                    average_home_odds::float AS average_home_odds,
                    average_draw_odds::float AS average_draw_odds,
                    average_away_odds::float AS average_away_odds,
                    best_home_odds::float AS best_home_odds,
                    best_draw_odds::float AS best_draw_odds,
                    best_away_odds::float AS best_away_odds,
                    source AS odds_source,
                    calculated_at
                FROM odds_consensus
                WHERE market_key = 'h2h'
                ORDER BY fixture_id, market_key, calculated_at DESC, id DESC
            ),
            latest_stats AS (
                SELECT DISTINCT ON (fixture_id)
                    *
                FROM predicted_match_stats
                ORDER BY fixture_id, created_at DESC, id DESC
            )
            SELECT
                f.id,
                f.match_number,
                f.stage,
                f.group_name,
                f.status,
                COALESCE(f.actual_home_score, f.home_score) AS actual_home_score,
                COALESCE(f.actual_away_score, f.away_score) AS actual_away_score,
                f.home_penalties,
                f.away_penalties,
                f.winner_team_id,
                wt.name AS actual_winner,
                f.last_odds_sync,
                f.last_result_sync,
                ht.name AS home_team_name,
                at.name AS away_team_name,
                ht.fifa_code AS home_team_code,
                at.fifa_code AS away_team_code,
                to_char(f.kickoff_time, 'YYYY-MM-DD"T"HH24:MI:SS') AS kickoff_time,
                lp.home_win_probability,
                lp.draw_probability,
                lp.away_win_probability,
                CASE
                    WHEN lp.home_win_probability IS NULL
                        OR lp.away_win_probability IS NULL
                        OR COALESCE(lp.home_win_probability + lp.away_win_probability, 0) = 0
                    THEN NULL
                    ELSE (
                        lp.home_win_probability
                        + COALESCE(lp.draw_probability, 0)
                        * (lp.home_win_probability / (lp.home_win_probability + lp.away_win_probability))
                    )::float
                END AS home_advance_probability,
                CASE
                    WHEN lp.home_win_probability IS NULL
                        OR lp.away_win_probability IS NULL
                        OR COALESCE(lp.home_win_probability + lp.away_win_probability, 0) = 0
                    THEN NULL
                    ELSE (
                        lp.away_win_probability
                        + COALESCE(lp.draw_probability, 0)
                        * (lp.away_win_probability / (lp.home_win_probability + lp.away_win_probability))
                    )::float
                END AS away_advance_probability,
                lp.predicted_home_goals,
                lp.predicted_away_goals,
                lp.confidence,
                lc.market_home_probability,
                lc.market_draw_probability,
                lc.market_away_probability,
                lc.average_home_odds,
                lc.average_draw_odds,
                lc.average_away_odds,
                lc.best_home_odds,
                lc.best_draw_odds,
                lc.best_away_odds,
                lc.bookmaker_count,
                lc.calculated_at AS odds_calculated_at,
                ps.expected_home_goals::float AS expected_home_goals,
                ps.expected_away_goals::float AS expected_away_goals,
                ps.home_shots,
                ps.away_shots,
                ps.home_shots_on_target,
                ps.away_shots_on_target,
                ps.home_possession::float AS home_possession,
                ps.away_possession::float AS away_possession,
                ps.home_corners,
                ps.away_corners,
                ps.home_yellow_cards,
                ps.away_yellow_cards,
                ps.home_red_card_probability::float AS home_red_card_probability,
                ps.away_red_card_probability::float AS away_red_card_probability,
                ps.both_teams_to_score_probability::float AS both_teams_to_score_probability,
                ps.over_2_5_goals_probability::float AS over_2_5_goals_probability,
                ps.clean_sheet_home_probability::float AS clean_sheet_home_probability,
                ps.clean_sheet_away_probability::float AS clean_sheet_away_probability
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            LEFT JOIN teams wt ON f.winner_team_id = wt.id
            LEFT JOIN latest_predictions lp ON lp.fixture_id = f.id
            LEFT JOIN latest_consensus lc ON lc.fixture_id = f.id
            LEFT JOIN latest_stats ps ON ps.fixture_id = f.id
            WHERE f.stage = ANY(%s)
            ORDER BY
                CASE f.stage
                    WHEN 'Round of 32' THEN 1
                    WHEN 'Round of 16' THEN 2
                    WHEN 'Quarter-final' THEN 3
                    WHEN 'Semi-final' THEN 4
                    WHEN 'Final' THEN 5
                    ELSE 99
                END,
                f.match_number;
            """,
            (list(KNOCKOUT_STAGES),),
        )
        return list(cur.fetchall())


def get_fixture_odds(fixture_id: int) -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            WITH latest_odds AS (
                SELECT DISTINCT ON (fo.bookmaker_id, fo.outcome_type)
                    fo.*,
                    b.name AS bookmaker,
                    b.region
                FROM fixture_odds fo
                JOIN bookmakers b ON fo.bookmaker_id = b.id
                WHERE fo.fixture_id = %s AND fo.market_key = 'h2h'
                ORDER BY fo.bookmaker_id, fo.outcome_type, fo.fetched_at DESC, fo.id DESC
            )
            SELECT
                bookmaker,
                region,
                market_key,
                outcome_name,
                outcome_type,
                decimal_price::float AS decimal_price,
                implied_probability::float AS implied_probability,
                normalized_probability::float AS normalized_probability,
                last_update,
                fetched_at,
                source
            FROM latest_odds
            ORDER BY bookmaker, outcome_type;
            """,
            (fixture_id,),
        )
        return list(cur.fetchall())


def get_predicted_match_stats(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                fixture_id,
                model_version,
                expected_home_goals::float AS expected_home_goals,
                expected_away_goals::float AS expected_away_goals,
                home_shots,
                away_shots,
                home_shots_on_target,
                away_shots_on_target,
                home_possession::float AS home_possession,
                away_possession::float AS away_possession,
                home_corners,
                away_corners,
                home_yellow_cards,
                away_yellow_cards,
                home_red_card_probability::float AS home_red_card_probability,
                away_red_card_probability::float AS away_red_card_probability,
                both_teams_to_score_probability::float AS both_teams_to_score_probability,
                over_2_5_goals_probability::float AS over_2_5_goals_probability,
                clean_sheet_home_probability::float AS clean_sheet_home_probability,
                clean_sheet_away_probability::float AS clean_sheet_away_probability,
                explanation_json,
                created_at
            FROM predicted_match_stats
            WHERE fixture_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 1;
            """,
            (fixture_id,),
        )
        return cur.fetchone()


def get_actual_match_stats(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                fixture_id,
                home_shots,
                away_shots,
                home_shots_on_target,
                away_shots_on_target,
                home_possession::float AS home_possession,
                away_possession::float AS away_possession,
                home_corners,
                away_corners,
                home_yellow_cards,
                away_yellow_cards,
                home_red_cards,
                away_red_cards,
                source,
                last_sync,
                created_at
            FROM actual_match_stats
            WHERE fixture_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 1;
            """,
            (fixture_id,),
        )
        return cur.fetchone()


def upsert_actual_match_stats(
    fixture_id: int,
    stats: dict[str, Any],
    source: str = "manual_demo",
) -> dict[str, Any]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH latest AS (
                SELECT id
                FROM actual_match_stats
                WHERE fixture_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT 1
            ),
            updated AS (
                UPDATE actual_match_stats
                SET home_shots = %s,
                    away_shots = %s,
                    home_shots_on_target = %s,
                    away_shots_on_target = %s,
                    home_possession = %s,
                    away_possession = %s,
                    home_corners = %s,
                    away_corners = %s,
                    home_yellow_cards = %s,
                    away_yellow_cards = %s,
                    home_red_cards = %s,
                    away_red_cards = %s,
                    source = %s,
                    last_sync = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM latest)
                RETURNING id
            )
            INSERT INTO actual_match_stats (
                fixture_id,
                home_shots,
                away_shots,
                home_shots_on_target,
                away_shots_on_target,
                home_possession,
                away_possession,
                home_corners,
                away_corners,
                home_yellow_cards,
                away_yellow_cards,
                home_red_cards,
                away_red_cards,
                source,
                last_sync
            )
            SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM updated);
            """,
            (
                fixture_id,
                stats["home_shots"],
                stats["away_shots"],
                stats["home_shots_on_target"],
                stats["away_shots_on_target"],
                stats["home_possession"],
                stats["away_possession"],
                stats["home_corners"],
                stats["away_corners"],
                stats["home_yellow_cards"],
                stats["away_yellow_cards"],
                stats["home_red_cards"],
                stats["away_red_cards"],
                source,
                fixture_id,
                stats["home_shots"],
                stats["away_shots"],
                stats["home_shots_on_target"],
                stats["away_shots_on_target"],
                stats["home_possession"],
                stats["away_possession"],
                stats["home_corners"],
                stats["away_corners"],
                stats["home_yellow_cards"],
                stats["away_yellow_cards"],
                stats["home_red_cards"],
                stats["away_red_cards"],
                source,
            ),
        )
    conn.commit()
    return get_actual_match_stats(fixture_id)


insert_or_update_actual_match_stats = upsert_actual_match_stats


def get_fixture_match_stats(fixture_id: int) -> dict[str, Any]:
    """Return the Wikipedia-sourced team_match_stats rows for a fixture.

    Shaped as ``{"home": {...}|None, "away": {...}|None}``, each row joined to its
    team name and oriented onto the fixture's home/away sides. ``None`` on a side
    when no row exists yet — callers render nothing rather than an empty panel.
    """
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                tms.team_id,
                tms.fixture_id,
                t.name AS team_name,
                tms.goals_for,
                tms.goals_against,
                tms.shots,
                tms.shots_on_target,
                tms.corners,
                tms.corners_conceded,
                tms.possession::float AS possession,
                tms.yellow_cards,
                tms.red_cards,
                tms.xg::float AS xg,
                CASE
                    WHEN tms.team_id = f.home_team_id THEN 'home'
                    WHEN tms.team_id = f.away_team_id THEN 'away'
                END AS side
            FROM team_match_stats tms
            JOIN fixtures f ON tms.fixture_id = f.id
            JOIN teams t ON tms.team_id = t.id
            WHERE tms.fixture_id = %s;
            """,
            (fixture_id,),
        )
        rows = list(cur.fetchall())

    result: dict[str, Any] = {"home": None, "away": None}
    for row in rows:
        side = row.pop("side", None)
        if side in ("home", "away"):
            result[side] = row
    return result


def get_watch_links(fixture_id: int) -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            f"""
            SELECT {WATCH_LINK_SELECT}
            FROM watch_links
            WHERE fixture_id = %s
            ORDER BY is_official DESC, region, provider_name;
            """,
            (fixture_id,),
        )
        return list(cur.fetchall())


def insert_watch_link(
    fixture_id: int,
    region: str,
    provider_name: str,
    provider_type: str,
    url: str,
    is_official: bool,
    note: str,
) -> dict[str, Any]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO watch_links (
                fixture_id, region, provider_name, provider_type, url, is_official, note
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fixture_id, region, provider_name)
            DO UPDATE SET
                provider_type = EXCLUDED.provider_type,
                url = EXCLUDED.url,
                is_official = EXCLUDED.is_official,
                note = EXCLUDED.note,
                updated_at = CURRENT_TIMESTAMP
            RETURNING {WATCH_LINK_SELECT};
            """,
            (fixture_id, region, provider_name, provider_type, url, is_official, note),
        )
        result = cur.fetchone()
    conn.commit()
    return result


def get_odds_consensus_by_fixture_id(fixture_id: int) -> dict[str, Any] | None:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                fixture_id,
                market_key,
                home_probability::float AS home_probability,
                draw_probability::float AS draw_probability,
                away_probability::float AS away_probability,
                bookmaker_count,
                average_home_odds::float AS average_home_odds,
                average_draw_odds::float AS average_draw_odds,
                average_away_odds::float AS average_away_odds,
                best_home_odds::float AS best_home_odds,
                best_draw_odds::float AS best_draw_odds,
                best_away_odds::float AS best_away_odds,
                source,
                calculated_at
            FROM odds_consensus
            WHERE fixture_id = %s AND market_key = 'h2h'
            ORDER BY calculated_at DESC, id DESC
            LIMIT 1;
            """,
            (fixture_id,),
        )
        return cur.fetchone()


def get_latest_odds() -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            WITH latest_consensus AS (
                SELECT DISTINCT ON (fixture_id, market_key)
                    *
                FROM odds_consensus
                WHERE market_key = 'h2h'
                ORDER BY fixture_id, market_key, calculated_at DESC, id DESC
            )
            SELECT
                lc.fixture_id,
                f.match_number,
                f.stage,
                ht.name AS home_team_name,
                at.name AS away_team_name,
                lc.home_probability::float AS market_home_probability,
                lc.draw_probability::float AS market_draw_probability,
                lc.away_probability::float AS market_away_probability,
                lc.average_home_odds::float AS average_home_odds,
                lc.average_draw_odds::float AS average_draw_odds,
                lc.average_away_odds::float AS average_away_odds,
                lc.best_home_odds::float AS best_home_odds,
                lc.best_draw_odds::float AS best_draw_odds,
                lc.best_away_odds::float AS best_away_odds,
                lc.bookmaker_count,
                lc.source,
                lc.calculated_at
            FROM latest_consensus lc
            JOIN fixtures f ON lc.fixture_id = f.id
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            ORDER BY f.match_number;
            """
        )
        return list(cur.fetchall())


def get_latest_sync_runs(limit: int = 10) -> list[dict[str, Any]]:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT * FROM sync_runs
            ORDER BY started_at DESC, id DESC
            LIMIT %s;
            """,
            (limit,),
        )
        return list(cur.fetchall())


def get_fixture_with_prediction_odds_and_result(fixture_id: int) -> dict[str, Any] | None:
    return get_fixture_by_id(fixture_id)


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
    if prediction_data.get("predicted_stats"):
        insert_predicted_match_stats(
            prediction_data["fixture_id"],
            prediction_data["predicted_stats"],
            prediction_data.get("model_version", "elo-baseline-v1"),
            prediction_data.get("explanation"),
        )
    return result


def insert_predicted_match_stats(
    fixture_id: int,
    stats: dict[str, Any],
    model_version: str = "elo-baseline-v1",
    explanation: list[str] | None = None,
) -> dict[str, Any]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO predicted_match_stats (
                fixture_id,
                model_version,
                expected_home_goals,
                expected_away_goals,
                home_shots,
                away_shots,
                home_shots_on_target,
                away_shots_on_target,
                home_possession,
                away_possession,
                home_corners,
                away_corners,
                home_yellow_cards,
                away_yellow_cards,
                home_red_card_probability,
                away_red_card_probability,
                both_teams_to_score_probability,
                over_2_5_goals_probability,
                clean_sheet_home_probability,
                clean_sheet_away_probability,
                explanation_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                fixture_id,
                model_version,
                stats["expected_home_goals"],
                stats["expected_away_goals"],
                stats["home_shots"],
                stats["away_shots"],
                stats["home_shots_on_target"],
                stats["away_shots_on_target"],
                stats["home_possession"],
                stats["away_possession"],
                stats["home_corners"],
                stats["away_corners"],
                stats["home_yellow_cards"],
                stats["away_yellow_cards"],
                stats["home_red_card_probability"],
                stats["away_red_card_probability"],
                stats["both_teams_to_score_probability"],
                stats["over_2_5_goals_probability"],
                stats["clean_sheet_home_probability"],
                stats["clean_sheet_away_probability"],
                Jsonb(explanation or stats.get("explanation", [])),
            ),
        )
        result = cur.fetchone()
    conn.commit()
    return result
