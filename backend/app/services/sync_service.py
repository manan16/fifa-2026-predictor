from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.db.connection import get_connection, get_dict_cursor
from app.services import odds_service, results_service


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


def run_full_sync() -> dict[str, Any]:
    result_sync = run_results_sync()
    odds_sync = run_odds_sync()
    results_service.advance_winners_in_bracket()
    return {
        "status": "success" if result_sync["status"] == odds_sync["status"] == "success" else "partial",
        "results": result_sync,
        "odds": odds_sync,
    }
