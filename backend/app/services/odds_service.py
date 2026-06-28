from __future__ import annotations

import json
import math
import os
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from app.db.connection import get_connection, get_dict_cursor

TEAM_ALIASES = {
    "united states": "usa",
    "u.s.a.": "usa",
    "dr congo": "congo dr",
    "congo dr": "congo dr",
    "democratic republic of congo": "congo dr",
    "bosnia and herzegovina": "bosnia-herz",
    "bosnia-herzegovina": "bosnia-herz",
    "cote d'ivoire": "ivory coast",
    "côte d’ivoire": "ivory coast",
    "côte d'ivoire": "ivory coast",
}

DEMO_BOOKMAKERS = [
    ("bet365", "Bet365", "uk"),
    ("skybet", "Sky Bet", "uk"),
    ("paddypower", "Paddy Power", "uk"),
    ("betfair", "Betfair", "uk"),
    ("williamhill", "William Hill", "uk"),
    ("unibet", "Unibet", "eu"),
    ("pinnacle", "Pinnacle", "eu"),
    ("draftkings", "DraftKings", "us"),
]


def decimal_to_implied_probability(decimal_price: float | int | None) -> float | None:
    if decimal_price is None or decimal_price <= 0:
        return None
    return round(1 / float(decimal_price), 6)


def remove_overround(probabilities: dict[str, float | None]) -> dict[str, float | None]:
    valid_total = sum(value for value in probabilities.values() if value is not None)
    if valid_total <= 0:
        return {key: None for key in probabilities}
    normalized = {
        key: round(value / valid_total, 6) if value is not None else None
        for key, value in probabilities.items()
    }
    valid_keys = [key for key, value in normalized.items() if value is not None]
    if valid_keys:
        delta = round(1 - sum(normalized[key] for key in valid_keys), 6)
        normalized[valid_keys[-1]] = round(normalized[valid_keys[-1]] + delta, 6)
    return normalized


def _normalize_team_name(name: str | None) -> str:
    normalized = (name or "").lower().replace(".", "").strip()
    normalized = TEAM_ALIASES.get(normalized, normalized)
    return normalized


def fetch_odds_from_the_odds_api() -> list[dict[str, Any]]:
    api_key = os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return []

    base_url = os.getenv("ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4").rstrip("/")
    sport_key = os.getenv("ODDS_API_SPORT_KEY", "soccer_fifa_world_cup")
    params = urlencode(
        {
            "apiKey": api_key,
            "regions": os.getenv("ODDS_API_REGIONS", "uk,eu,us"),
            "markets": os.getenv("ODDS_API_MARKETS", "h2h"),
            "oddsFormat": "decimal",
        }
    )
    url = f"{base_url}/sports/{sport_key}/odds?{params}"

    try:
        with urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"Odds API fetch failed: {exc}")
        return []


def match_external_odds_to_fixture(
    external_event: dict[str, Any], fixtures: list[dict[str, Any]]
) -> dict[str, Any] | None:
    external_home = _normalize_team_name(external_event.get("home_team"))
    external_away = _normalize_team_name(external_event.get("away_team"))

    for fixture in fixtures:
        home = _normalize_team_name(fixture.get("home_team_name"))
        away = _normalize_team_name(fixture.get("away_team_name"))
        if {external_home, external_away} == {home, away}:
            return fixture
    return None


def _upsert_bookmaker(cur, bookmaker: dict[str, Any]) -> int:
    cur.execute(
        """
        INSERT INTO bookmakers (key, name, region)
        VALUES (%s, %s, %s)
        ON CONFLICT (key) DO UPDATE SET
            name = EXCLUDED.name,
            region = EXCLUDED.region
        RETURNING id;
        """,
        (bookmaker["key"], bookmaker["name"], bookmaker.get("region")),
    )
    return cur.fetchone()["id"]


def save_fixture_odds(fixture_id: int, odds_payload: list[dict[str, Any]]) -> int:
    conn = get_connection()
    records = 0
    with conn.cursor() as cur:
        for bookmaker in odds_payload:
            bookmaker_id = _upsert_bookmaker(cur, bookmaker)
            outcomes = bookmaker.get("outcomes", [])
            implied = {
                outcome["outcome_type"]: decimal_to_implied_probability(outcome.get("decimal_price"))
                for outcome in outcomes
            }
            normalized = remove_overround(implied)

            for outcome in outcomes:
                outcome_type = outcome["outcome_type"]
                cur.execute(
                    """
                    INSERT INTO fixture_odds (
                        fixture_id,
                        bookmaker_id,
                        source,
                        market_key,
                        outcome_name,
                        outcome_type,
                        decimal_price,
                        implied_probability,
                        normalized_probability,
                        last_update
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        fixture_id,
                        bookmaker_id,
                        bookmaker.get("source", "demo"),
                        bookmaker.get("market_key", "h2h"),
                        outcome["outcome_name"],
                        outcome_type,
                        outcome.get("decimal_price"),
                        implied.get(outcome_type),
                        normalized.get(outcome_type),
                        outcome.get("last_update"),
                    ),
                )
                records += 1

        cur.execute("UPDATE fixtures SET last_odds_sync = CURRENT_TIMESTAMP WHERE id = %s;", (fixture_id,))
    conn.commit()
    return records


def calculate_market_consensus(fixture_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH latest_odds AS (
                SELECT DISTINCT ON (bookmaker_id, outcome_type)
                    bookmaker_id,
                    outcome_type,
                    decimal_price,
                    normalized_probability,
                    source,
                    fetched_at
                FROM fixture_odds
                WHERE fixture_id = %s AND market_key = 'h2h'
                ORDER BY bookmaker_id, outcome_type, fetched_at DESC, id DESC
            )
            SELECT * FROM latest_odds;
            """,
            (fixture_id,),
        )
        rows = cur.fetchall()

        by_bookmaker: dict[int, dict[str, dict[str, float]]] = {}
        for row in rows:
            by_bookmaker.setdefault(row["bookmaker_id"], {})[row["outcome_type"]] = {
                "odds": float(row["decimal_price"]) if row["decimal_price"] is not None else None,
                "probability": float(row["normalized_probability"]) if row["normalized_probability"] is not None else None,
            }

        complete = [
            values
            for values in by_bookmaker.values()
            if {"home", "draw", "away"}.issubset(values)
        ]
        if not complete:
            return None

        def avg_probability(outcome_type: str) -> float:
            return sum(values[outcome_type]["probability"] for values in complete) / len(complete)

        def avg_odds(outcome_type: str) -> float:
            return sum(values[outcome_type]["odds"] for values in complete) / len(complete)

        def best_odds(outcome_type: str) -> float:
            return max(values[outcome_type]["odds"] for values in complete)

        consensus = {
            "fixture_id": fixture_id,
            "market_key": "h2h",
            "home_probability": round(avg_probability("home"), 6),
            "draw_probability": round(avg_probability("draw"), 6),
            "away_probability": round(avg_probability("away"), 6),
            "bookmaker_count": len(complete),
            "average_home_odds": round(avg_odds("home"), 3),
            "average_draw_odds": round(avg_odds("draw"), 3),
            "average_away_odds": round(avg_odds("away"), 3),
            "best_home_odds": round(best_odds("home"), 3),
            "best_draw_odds": round(best_odds("draw"), 3),
            "best_away_odds": round(best_odds("away"), 3),
            "source": "demo" if any(row.get("source") == "demo" for row in rows) else "api",
        }
        cur.execute(
            """
            INSERT INTO odds_consensus (
                fixture_id,
                market_key,
                home_probability,
                draw_probability,
                away_probability,
                bookmaker_count,
                average_home_odds,
                average_draw_odds,
                average_away_odds,
                best_home_odds,
                best_draw_odds,
                best_away_odds,
                source
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                consensus["fixture_id"],
                consensus["market_key"],
                consensus["home_probability"],
                consensus["draw_probability"],
                consensus["away_probability"],
                consensus["bookmaker_count"],
                consensus["average_home_odds"],
                consensus["average_draw_odds"],
                consensus["average_away_odds"],
                consensus["best_home_odds"],
                consensus["best_draw_odds"],
                consensus["best_away_odds"],
                consensus["source"],
            ),
        )
        saved = cur.fetchone()
    conn.commit()
    return saved


def _fair_odds(probability: float, margin_multiplier: float) -> float:
    return round(max(1.05, 1 / min(0.92, probability * margin_multiplier)), 2)


def _demo_prices(fixture: dict[str, Any], bookmaker_index: int) -> tuple[float, float, float]:
    home_elo = float(fixture.get("home_team_elo") or 1800)
    away_elo = float(fixture.get("away_team_elo") or 1800)
    home_rating = 1 / (1 + math.pow(10, (away_elo - home_elo) / 400))
    draw_probability = max(0.18, min(0.31, 0.27 - abs(home_rating - 0.5) * 0.1))
    home_probability = (1 - draw_probability) * home_rating
    away_probability = 1 - draw_probability - home_probability
    skew = 1 + (bookmaker_index - 3.5) * 0.006
    margin = 1.055 + bookmaker_index * 0.004
    return (
        _fair_odds(home_probability * skew, margin),
        _fair_odds(draw_probability, margin),
        _fair_odds(away_probability / skew, margin),
    )


def seed_demo_odds() -> int:
    with get_dict_cursor() as cur:
        cur.execute(
            """
            SELECT
                f.id,
                f.home_team_id,
                f.away_team_id,
                ht.name AS home_team_name,
                at.name AS away_team_name,
                ht.elo_rating AS home_team_elo,
                at.elo_rating AS away_team_elo
            FROM fixtures f
            JOIN teams ht ON f.home_team_id = ht.id
            JOIN teams at ON f.away_team_id = at.id
            ORDER BY f.match_number;
            """
        )
        fixtures = list(cur.fetchall())

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM fixture_odds
            WHERE source = 'demo'
              AND fixture_id IN (SELECT id FROM fixtures);
            """
        )
    conn.commit()

    records = 0
    now = datetime.now(UTC).replace(microsecond=0).isoformat()
    for fixture in fixtures:
        payload = []
        for index, (key, name, region) in enumerate(DEMO_BOOKMAKERS):
            home_odds, draw_odds, away_odds = _demo_prices(fixture, index)
            payload.append(
                {
                    "key": key,
                    "name": name,
                    "region": region,
                    "source": "demo",
                    "market_key": "h2h",
                    "outcomes": [
                        {
                            "outcome_name": fixture["home_team_name"],
                            "outcome_type": "home",
                            "decimal_price": home_odds,
                            "last_update": now,
                        },
                        {
                            "outcome_name": "Draw",
                            "outcome_type": "draw",
                            "decimal_price": draw_odds,
                            "last_update": now,
                        },
                        {
                            "outcome_name": fixture["away_team_name"],
                            "outcome_type": "away",
                            "decimal_price": away_odds,
                            "last_update": now,
                        },
                    ],
                }
            )
        records += save_fixture_odds(fixture["id"], payload)
        calculate_market_consensus(fixture["id"])
    return records
