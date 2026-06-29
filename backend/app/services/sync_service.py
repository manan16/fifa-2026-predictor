from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from flask import current_app, has_app_context

from app.config import Config
from app.db import queries
from app.db.connection import get_connection, get_dict_cursor
from app.ml.model import predict_match
from app.services import odds_service, results_service, stats_service


def _start_sync_run(job_name: str) -> int:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO sync_runs (job_name, status) VALUES (%s, 'running') RETURNING id;",
            (job_name,),
        )
        sync_id = cur.fetchone()["id"]
    conn.commit()
    return sync_id


def _finish_sync_run(sync_id: int, status: str, message: str, records_processed: int = 0) -> None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE sync_runs
            SET status = %s,
                finished_at = %s,
                message = %s,
                records_processed = %s
            WHERE id = %s;
            """,
            (status, datetime.now(UTC), message, records_processed, sync_id),
        )
    conn.commit()


def run_odds_sync() -> dict[str, Any]:
    sync_id = _start_sync_run("odds_sync")
    try:
        events = odds_service.fetch_odds_from_the_odds_api()
        if not events:
            records = odds_service.seed_demo_odds()
            message = "Seeded demo odds because no odds API key/data was available."
            _finish_sync_run(sync_id, "success", message, records)
            return {"status": "success", "message": message, "records_processed": records}

        with get_dict_cursor() as cur:
            cur.execute(
                """
                SELECT f.*, ht.name AS home_team_name, at.name AS away_team_name
                FROM fixtures f
                JOIN teams ht ON f.home_team_id = ht.id
                JOIN teams at ON f.away_team_id = at.id;
                """
            )
            fixtures = list(cur.fetchall())

        records = 0
        for event in events:
            fixture = odds_service.match_external_odds_to_fixture(event, fixtures)
            if not fixture:
                continue
            payload = []
            for bookmaker in event.get("bookmakers", []):
                markets = bookmaker.get("markets", [])
                h2h_market = next((market for market in markets if market.get("key") == "h2h"), None)
                if not h2h_market:
                    continue
                outcomes = []
                for outcome in h2h_market.get("outcomes", []):
                    outcome_name = outcome.get("name", "")
                    normalized = outcome_name.lower()
                    if normalized == fixture["home_team_name"].lower():
                        outcome_type = "home"
                    elif normalized == fixture["away_team_name"].lower():
                        outcome_type = "away"
                    elif normalized == "draw":
                        outcome_type = "draw"
                    else:
                        continue
                    outcomes.append(
                        {
                            "outcome_name": outcome_name,
                            "outcome_type": outcome_type,
                            "decimal_price": outcome.get("price"),
                            "last_update": bookmaker.get("last_update"),
                        }
                    )
                payload.append(
                    {
                        "key": bookmaker.get("key"),
                        "name": bookmaker.get("title", bookmaker.get("key", "Unknown")),
                        "region": None,
                        "source": "the-odds-api",
                        "market_key": "h2h",
                        "outcomes": outcomes,
                    }
                )
            records += odds_service.save_fixture_odds(fixture["id"], payload)
            odds_service.calculate_market_consensus(fixture["id"])

        message = "Fetched odds from The Odds API."
        _finish_sync_run(sync_id, "success", message, records)
        return {"status": "success", "message": message, "records_processed": records}
    except Exception as exc:
        _finish_sync_run(sync_id, "failed", str(exc), 0)
        return {"status": "failed", "message": str(exc), "records_processed": 0}


def run_results_sync() -> dict[str, Any]:
    sync_id = _start_sync_run("results_sync")
    try:
        results = results_service.fetch_latest_results()
        records = len(results)
        message = "No external results API configured." if records == 0 else "Fetched latest results."
        _finish_sync_run(sync_id, "success", message, records)
        return {"status": "success", "message": message, "records_processed": records}
    except Exception as exc:
        _finish_sync_run(sync_id, "failed", str(exc), 0)
        return {"status": "failed", "message": str(exc), "records_processed": 0}


def run_prediction_stats_sync() -> dict[str, Any]:
    sync_id = _start_sync_run("prediction_stats_sync")
    try:
        with get_dict_cursor() as cur:
            cur.execute(
                """
                SELECT
                    f.id AS fixture_id,
                    f.stage,
                    ht.name AS home_name,
                    ht.fifa_ranking AS home_fifa_ranking,
                    ht.elo_rating AS home_elo_rating,
                    at.name AS away_name,
                    at.fifa_ranking AS away_fifa_ranking,
                    at.elo_rating AS away_elo_rating
                FROM fixtures f
                JOIN teams ht ON f.home_team_id = ht.id
                JOIN teams at ON f.away_team_id = at.id
                ORDER BY f.match_number;
                """
            )
            rows = list(cur.fetchall())

        records = 0
        for row in rows:
            home_team = {
                "name": row["home_name"],
                "fifa_ranking": row["home_fifa_ranking"],
                "elo_rating": row["home_elo_rating"],
            }
            away_team = {
                "name": row["away_name"],
                "fifa_ranking": row["away_fifa_ranking"],
                "elo_rating": row["away_elo_rating"],
            }
            prediction = predict_match(home_team, away_team, stage=row["stage"], neutral_venue=True)
            queries.insert_predicted_match_stats(
                row["fixture_id"],
                prediction["predicted_stats"],
                prediction["model_version"],
                prediction["explanation"],
            )
            records += 1

        message = "Regenerated predicted match stats."
        _finish_sync_run(sync_id, "success", message, records)
        return {"status": "success", "message": message, "records_processed": records}
    except Exception as exc:
        _finish_sync_run(sync_id, "failed", str(exc), 0)
        return {"status": "failed", "message": str(exc), "records_processed": 0}


def _stats_sync_enabled() -> bool:
    if has_app_context():
        return bool(current_app.config.get("ENABLE_STATS_SYNC", Config.ENABLE_STATS_SYNC))
    return Config.ENABLE_STATS_SYNC


def run_match_stats_sync() -> dict[str, Any]:
    """Pull Wikipedia match stats into team_match_stats. Never fatal to the run."""
    if not _stats_sync_enabled():
        return {"status": "skipped", "message": "ENABLE_STATS_SYNC is off.", "records_processed": 0}

    sync_id = _start_sync_run("match_stats_sync")
    try:
        records = stats_service.sync_wikipedia_match_stats()
        message = (
            "No Wikipedia match stats matched current fixtures."
            if records == 0
            else "Synced Wikipedia match stats."
        )
        _finish_sync_run(sync_id, "success", message, records)
        return {"status": "success", "message": message, "records_processed": records}
    except Exception as exc:
        _finish_sync_run(sync_id, "failed", str(exc), 0)
        return {"status": "failed", "message": str(exc), "records_processed": 0}


def run_full_sync() -> dict[str, Any]:
    result_sync = run_results_sync()
    odds_sync = run_odds_sync()
    match_stats_sync = run_match_stats_sync()
    results_service.advance_winners_in_bracket()
    stats_sync = run_prediction_stats_sync()
    return {
        "status": "success"
        if result_sync["status"] == odds_sync["status"] == stats_sync["status"] == "success"
        else "partial",
        "results": result_sync,
        "odds": odds_sync,
        "match_stats": match_stats_sync,
        "predicted_stats": stats_sync,
    }
