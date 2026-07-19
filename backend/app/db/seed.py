from app.db.connection import get_connection
from app.ml.model import predict_match
from psycopg.types.json import Jsonb

# Seed data mirrors the demo knockout bracket screenshot.
# FIFA rankings are from the official FIFA/Coca-Cola Men's World Ranking
# published on 11 June 2026.
# Kickoff times are stored as London-local timestamps for display in the MVP.
TEAMS = [
    ("Argentina", "ARG", "CONMEBOL", 1, 2145),
    ("France", "FRA", "UEFA", 3, 2110),
    ("Spain", "ESP", "UEFA", 2, 2100),
    ("England", "ENG", "UEFA", 4, 2055),
    ("Brazil", "BRA", "CONMEBOL", 6, 2130),
    ("Portugal", "POR", "UEFA", 5, 2025),
    ("Netherlands", "NED", "UEFA", 8, 2015),
    ("Belgium", "BEL", "UEFA", 9, 1990),
    ("Germany", "GER", "UEFA", 10, 1980),
    ("Croatia", "CRO", "UEFA", 11, 1955),
    ("Morocco", "MAR", "CAF", 7, 1900),
    ("Switzerland", "SUI", "UEFA", 19, 1885),
    ("Japan", "JPN", "AFC", 18, 1875),
    ("USA", "USA", "CONCACAF", 17, 1850),
    ("Austria", "AUT", "UEFA", 24, 1840),
    ("Sweden", "SWE", "UEFA", 38, 1810),
    ("Senegal", "SEN", "CAF", 15, 1800),
    ("Colombia", "COL", "CONMEBOL", 13, 1795),
    ("Ecuador", "ECU", "CONMEBOL", 23, 1785),
    ("Canada", "CAN", "CONCACAF", 30, 1765),
    ("Australia", "AUS", "AFC", 27, 1745),
    ("Paraguay", "PAR", "CONMEBOL", 41, 1715),
    ("Ivory Coast", "CIV", "CAF", 33, 1705),
    ("Norway", "NOR", "UEFA", 31, 1700),
    ("Algeria", "ALG", "CAF", 28, 1695),
    ("Mexico", "MEX", "CONCACAF", 14, 1685),
    ("Egypt", "EGY", "CAF", 29, 1680),
    ("South Africa", "RSA", "CAF", 60, 1645),
    ("Congo DR", "COD", "CAF", 46, 1620),
    ("Cape Verde", "CPV", "CAF", 67, 1590),
    ("Bosnia-Herz", "BIH", "UEFA", 64, 1575),
    ("Ghana", "GHA", "CAF", 73, 1565),
]

KNOCKOUT_VENUE = "Knockout bracket"
KNOCKOUT_CITY = "World Cup 2026"

# Round of 32 entrants are fixed — these are the teams that qualified for the
# knockout stage. Every later round is *derived* from these results, never
# hardcoded, so a team that loses can never reappear in a later round.
# Tuple shape: (match_number, group_name, home_team, away_team, kickoff_time)
ROUND_OF_32 = [
    (1, "Left bracket", "South Africa", "Canada", "2026-06-28 20:00:00"),
    (2, "Right bracket", "Brazil", "Japan", "2026-06-29 18:00:00"),
    (3, "Left bracket", "Germany", "Paraguay", "2026-06-29 21:30:00"),
    (4, "Left bracket", "Netherlands", "Morocco", "2026-06-30 02:00:00"),
    (5, "Right bracket", "Ivory Coast", "Norway", "2026-06-30 18:00:00"),
    (6, "Left bracket", "France", "Sweden", "2026-06-30 22:00:00"),
    (7, "Right bracket", "Mexico", "Ecuador", "2026-07-01 02:00:00"),
    (8, "Right bracket", "England", "Congo DR", "2026-07-01 17:00:00"),
    (9, "Left bracket", "Belgium", "Senegal", "2026-07-01 21:00:00"),
    (10, "Left bracket", "USA", "Bosnia-Herz", "2026-07-02 01:00:00"),
    (11, "Left bracket", "Spain", "Austria", "2026-07-02 20:00:00"),
    (12, "Left bracket", "Portugal", "Croatia", "2026-07-03 00:00:00"),
    (13, "Right bracket", "Switzerland", "Algeria", "2026-07-03 04:00:00"),
    (14, "Right bracket", "Australia", "Egypt", "2026-07-03 19:00:00"),
    (15, "Right bracket", "Argentina", "Cape Verde", "2026-07-03 23:00:00"),
    (16, "Right bracket", "Colombia", "Ghana", "2026-07-04 02:30:00"),
]

# Later-round slots. Home/away teams are NOT hardcoded — each is the advancing
# team from a prior-round match. ``home_source``/``away_source`` are the
# match_numbers whose winners feed this slot, preserving the bracket tree.
# Tuple shape: (match_number, stage, group_name, home_source, away_source, kickoff_time)
BRACKET_PROGRESSION = [
    # Round of 16
    (17, "Round of 16", "Left bracket", 1, 4, "2026-07-04 18:00:00"),
    (18, "Round of 16", "Left bracket", 3, 6, "2026-07-04 22:00:00"),
    (19, "Round of 16", "Right bracket", 2, 5, "2026-07-05 21:00:00"),
    (20, "Round of 16", "Right bracket", 7, 8, "2026-07-06 01:00:00"),
    (21, "Round of 16", "Left bracket", 12, 11, "2026-07-06 20:00:00"),
    (22, "Round of 16", "Left bracket", 10, 9, "2026-07-07 01:00:00"),
    (23, "Round of 16", "Right bracket", 15, 14, "2026-07-07 17:00:00"),
    (24, "Round of 16", "Right bracket", 13, 16, "2026-07-07 21:00:00"),
    # Quarter-finals
    (25, "Quarter-final", "Left bracket", 18, 17, "2026-07-09 21:00:00"),
    (26, "Quarter-final", "Left bracket", 21, 22, "2026-07-10 20:00:00"),
    (27, "Quarter-final", "Right bracket", 19, 20, "2026-07-11 22:00:00"),
    (28, "Quarter-final", "Right bracket", 23, 24, "2026-07-12 02:00:00"),
    # Semi-finals
    (29, "Semi-final", "Left bracket", 25, 26, "2026-07-14 20:00:00"),
    (30, "Semi-final", "Right bracket", 27, 28, "2026-07-15 20:00:00"),
    # Final
    (31, "Final", "Champion pick", 29, 30, "2026-07-19 20:00:00"),
]

_TEAM_FEATURES = {name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo} for name, _code, _conf, ranking, elo in TEAMS}

DEMO_ACTUAL_RESULTS = {
    1: {
        "actual_home_score": 0,
        "actual_away_score": 1,
        "winner_team_name": "Canada",
        "home_penalties": None,
        "away_penalties": None,
        "stats": {
            "home_shots": 10,
            "away_shots": 13,
            "home_shots_on_target": 3,
            "away_shots_on_target": 6,
            "home_possession": 47,
            "away_possession": 53,
            "home_corners": 4,
            "away_corners": 6,
            "home_yellow_cards": 2,
            "away_yellow_cards": 1,
            "home_red_cards": 0,
            "away_red_cards": 0,
        },
    },
    2: {
        "actual_home_score": 2,
        "actual_away_score": 1,
        "winner_team_name": "Brazil",
        "home_penalties": None,
        "away_penalties": None,
        "stats": {
            "home_shots": 17,
            "away_shots": 9,
            "home_shots_on_target": 8,
            "away_shots_on_target": 3,
            "home_possession": 59,
            "away_possession": 41,
            "home_corners": 7,
            "away_corners": 3,
            "home_yellow_cards": 1,
            "away_yellow_cards": 2,
            "home_red_cards": 0,
            "away_red_cards": 0,
        },
    },
}


def _predicted_winner(prediction: dict, home_name: str, away_name: str) -> str:
    """Advancing team by prediction, mirroring bracket._predicted_winner().

    Advance probability decides first (it folds the draw share into a shoot-out
    split); win probability is the fallback. Ties resolve to the home slot so
    the forward bracket is always deterministic.
    """
    home_advance = prediction.get("home_advance_probability")
    away_advance = prediction.get("away_advance_probability")
    if home_advance is not None and away_advance is not None and home_advance != away_advance:
        return home_name if home_advance > away_advance else away_name

    home_win = prediction.get("home_win_probability")
    away_win = prediction.get("away_win_probability")
    if home_win is not None and away_win is not None and home_win != away_win:
        return home_name if home_win > away_win else away_name

    return home_name


def _actual_winner(demo: dict, home_name: str, away_name: str) -> str:
    """Advancing team from a completed result, decided by score then penalties."""
    home_score = demo["actual_home_score"]
    away_score = demo["actual_away_score"]
    if home_score != away_score:
        return home_name if home_score > away_score else away_name
    home_pens = demo.get("home_penalties")
    away_pens = demo.get("away_penalties")
    if home_pens is not None and away_pens is not None and home_pens != away_pens:
        return home_name if home_pens > away_pens else away_name
    return demo.get("winner_team_name") or home_name


def _resolve_winner(match_number: int, stage: str, home_name: str, away_name: str) -> str:
    """Winner of a slot: actual result takes precedence over the prediction."""
    demo = DEMO_ACTUAL_RESULTS.get(match_number)
    if demo is not None:
        return _actual_winner(demo, home_name, away_name)
    prediction = predict_match(
        _TEAM_FEATURES[home_name], _TEAM_FEATURES[away_name], stage=stage, neutral_venue=True
    )
    return _predicted_winner(prediction, home_name, away_name)


def build_chained_fixtures() -> list[tuple]:
    """Build the full knockout bracket by chaining winners forward.

    Round of 32 entrants are fixed; every later round's home/away team is the
    advancing team (actual result if the feeding match is completed, otherwise
    predicted) of the prior-round match that feeds that slot. Deterministic, so
    re-running the seed reproduces the identical bracket.
    """
    winners: dict[int, str] = {}
    fixtures: list[tuple] = []

    for match_number, group, home_name, away_name, kickoff in ROUND_OF_32:
        fixtures.append(
            (match_number, "Round of 32", group, home_name, away_name, KNOCKOUT_VENUE, KNOCKOUT_CITY, kickoff)
        )
        winners[match_number] = _resolve_winner(match_number, "Round of 32", home_name, away_name)

    for match_number, stage, group, home_source, away_source, kickoff in BRACKET_PROGRESSION:
        home_name = winners[home_source]
        away_name = winners[away_source]
        fixtures.append(
            (match_number, stage, group, home_name, away_name, KNOCKOUT_VENUE, KNOCKOUT_CITY, kickoff)
        )
        winners[match_number] = _resolve_winner(match_number, stage, home_name, away_name)

    return fixtures


# Chained bracket used for seeding and consumed by tests. Same tuple shape as the
# legacy hardcoded list: (match_number, stage, group, home, away, venue, city, kickoff).
FIXTURES = build_chained_fixtures()

# Honest-demo (Option A): the Round of 32 is played through so the "Completed"
# view has content; later rounds stay as scheduled predictions. Results and
# stats for completed ties are synthetic and generated from the same model as
# the predictions — we never bind Wikipedia (or any live source) onto these
# fixtures, because they don't correspond to real matches.
DEMO_COMPLETED_STAGES = ("Round of 32",)


def _synthetic_actual_result(stage: str, home_name: str, away_name: str) -> dict:
    """A plausible completed result derived from the same model as the prediction.

    The scoreline is the model's predicted scoreline and the advancing side is
    the model's predicted winner, so a synthetic result never contradicts the
    forward bracket. A level knockout scoreline is resolved with a synthetic
    penalty shoot-out for the winner. Stats mirror the predicted match stats, so
    the actual-vs-predicted comparison stays internally consistent.
    """
    prediction = predict_match(
        _TEAM_FEATURES[home_name], _TEAM_FEATURES[away_name], stage=stage, neutral_venue=True
    )
    home_score = prediction["predicted_home_goals"]
    away_score = prediction["predicted_away_goals"]
    winner_name = _predicted_winner(prediction, home_name, away_name)

    home_penalties = away_penalties = None
    if home_score == away_score:
        home_penalties, away_penalties = (4, 3) if winner_name == home_name else (3, 4)
    elif (home_score > away_score) != (winner_name == home_name):
        # Keep the scoreline and the advancing side in agreement.
        winner_name = home_name if home_score > away_score else away_name

    stats = prediction["predicted_stats"]
    home_possession = round(stats["home_possession"])
    return {
        "actual_home_score": home_score,
        "actual_away_score": away_score,
        "winner_team_name": winner_name,
        "home_penalties": home_penalties,
        "away_penalties": away_penalties,
        "stats": {
            "home_shots": stats["home_shots"],
            "away_shots": stats["away_shots"],
            "home_shots_on_target": stats["home_shots_on_target"],
            "away_shots_on_target": stats["away_shots_on_target"],
            "home_possession": home_possession,
            "away_possession": 100 - home_possession,
            "home_corners": stats["home_corners"],
            "away_corners": stats["away_corners"],
            "home_yellow_cards": stats["home_yellow_cards"],
            "away_yellow_cards": stats["away_yellow_cards"],
            "home_red_cards": 0,
            "away_red_cards": 0,
        },
    }


def _completed_result_for(match_number: int, stage: str, home_name: str, away_name: str) -> dict | None:
    """Completed-match payload for a slot, or None if the tie is still scheduled.

    Curated demo results (DEMO_ACTUAL_RESULTS) take precedence; otherwise every
    Round-of-32 tie is filled with a synthetic, model-derived result.
    """
    curated = DEMO_ACTUAL_RESULTS.get(match_number)
    if curated is not None:
        return curated
    if stage in DEMO_COMPLETED_STAGES:
        return _synthetic_actual_result(stage, home_name, away_name)
    return None


def seed_database() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for team in TEAMS:
                cur.execute(
                    """
                    INSERT INTO teams (name, fifa_code, confederation, fifa_ranking, elo_rating)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        fifa_code = EXCLUDED.fifa_code,
                        confederation = EXCLUDED.confederation,
                        fifa_ranking = EXCLUDED.fifa_ranking,
                        elo_rating = EXCLUDED.elo_rating,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    team,
                )

            match_numbers = [fixture[0] for fixture in FIXTURES]
            cur.execute(
                """
                UPDATE fixtures
                SET match_number = -match_number
                WHERE venue = 'Knockout bracket'
                  AND city = 'World Cup 2026'
                  AND match_number = ANY(%s);
                """,
                (match_numbers,),
            )

            for fixture in FIXTURES:
                # Match on the (negated) match_number — the stable slot identity —
                # rather than the teams, so chained team changes update the row in
                # place instead of orphaning the prior round's entrants.
                cur.execute(
                    """
                    UPDATE fixtures
                    SET match_number = %s,
                        stage = %s,
                        group_name = %s,
                        home_team_id = (SELECT id FROM teams WHERE name = %s),
                        away_team_id = (SELECT id FROM teams WHERE name = %s),
                        venue = %s,
                        city = %s,
                        kickoff_time = %s,
                        status = 'scheduled',
                        home_score = NULL,
                        away_score = NULL,
                        actual_home_score = NULL,
                        actual_away_score = NULL,
                        home_penalties = NULL,
                        away_penalties = NULL,
                        winner_team_id = NULL,
                        result_source = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE venue = 'Knockout bracket'
                      AND city = 'World Cup 2026'
                      AND match_number = %s
                    RETURNING id;
                    """,
                    (
                        fixture[0],
                        fixture[1],
                        fixture[2],
                        fixture[3],
                        fixture[4],
                        fixture[5],
                        fixture[6],
                        fixture[7],
                        -fixture[0],
                    ),
                )
                existing = cur.fetchone()
                if existing is None:
                    cur.execute(
                        """
                        INSERT INTO fixtures (
                            match_number,
                            stage,
                            group_name,
                            home_team_id,
                            away_team_id,
                            venue,
                            city,
                            kickoff_time,
                            status
                        )
                        VALUES (
                            %s, %s, %s,
                            (SELECT id FROM teams WHERE name = %s),
                            (SELECT id FROM teams WHERE name = %s),
                            %s, %s, %s, 'scheduled'
                        );
                        """,
                        fixture,
                    )

            cur.execute(
                """
                DELETE FROM predicted_match_stats
                WHERE fixture_id IN (
                    SELECT id FROM fixtures WHERE match_number = ANY(%s)
                );
                """,
                (match_numbers,),
            )
            cur.execute(
                """
                DELETE FROM actual_match_stats
                WHERE fixture_id IN (
                    SELECT id FROM fixtures WHERE match_number = ANY(%s)
                );
                """,
                (match_numbers,),
            )
            cur.execute(
                """
                DELETE FROM predictions
                WHERE fixture_id IN (
                    SELECT id FROM fixtures WHERE match_number = ANY(%s)
                );
                """,
                (match_numbers,),
            )

            cur.execute(
                """
                SELECT f.id AS fixture_id, f.match_number, f.stage, ht.*, at.name AS away_name,
                       at.fifa_code AS away_fifa_code, at.confederation AS away_confederation,
                       at.fifa_ranking AS away_fifa_ranking, at.elo_rating AS away_elo_rating
                FROM fixtures f
                JOIN teams ht ON f.home_team_id = ht.id
                JOIN teams at ON f.away_team_id = at.id
                WHERE f.match_number = ANY(%s)
                ORDER BY f.match_number;
                """,
                (match_numbers,),
            )
            rows = cur.fetchall()

            for row in rows:
                home_team = {
                    "name": row["name"],
                    "fifa_ranking": row["fifa_ranking"],
                    "elo_rating": row["elo_rating"],
                }
                away_team = {
                    "name": row["away_name"],
                    "fifa_ranking": row["away_fifa_ranking"],
                    "elo_rating": row["away_elo_rating"],
                }
                prediction = predict_match(home_team, away_team, stage=row["stage"], neutral_venue=True)
                cur.execute(
                    """
                    INSERT INTO predictions (
                        fixture_id, model_version, home_win_probability, draw_probability,
                        away_win_probability, predicted_home_goals, predicted_away_goals,
                        confidence, explanation_json
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        row["fixture_id"],
                        prediction["model_version"],
                        prediction["home_win_probability"],
                        prediction["draw_probability"],
                        prediction["away_win_probability"],
                        prediction["predicted_home_goals"],
                        prediction["predicted_away_goals"],
                        prediction["confidence"],
                        Jsonb(prediction["explanation"]),
                    ),
                )
                stats = prediction["predicted_stats"]
                cur.execute(
                    """
                    INSERT INTO predicted_match_stats (
                        fixture_id, model_version, expected_home_goals, expected_away_goals,
                        home_shots, away_shots, home_shots_on_target, away_shots_on_target,
                        home_possession, away_possession, home_corners, away_corners,
                        home_yellow_cards, away_yellow_cards, home_red_card_probability,
                        away_red_card_probability, both_teams_to_score_probability,
                        over_2_5_goals_probability, clean_sheet_home_probability,
                        clean_sheet_away_probability, explanation_json
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        row["fixture_id"],
                        prediction["model_version"],
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
                        Jsonb(prediction["explanation"]),
                    ),
                )
                cur.execute(
                    """
                    INSERT INTO watch_links (
                        fixture_id, region, provider_name, provider_type, url, is_official, note
                    )
                    VALUES (
                        %s,
                        'UK',
                        'Official FIFA Match Centre',
                        'official_match_centre',
                        'https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026',
                        true,
                        'Replace with confirmed broadcaster or official match-centre link when live data is connected.'
                    )
                    ON CONFLICT (fixture_id, region, provider_name)
                    DO UPDATE SET
                        provider_type = EXCLUDED.provider_type,
                        url = EXCLUDED.url,
                        is_official = EXCLUDED.is_official,
                        note = EXCLUDED.note,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (row["fixture_id"],),
                )

                demo_actual = _completed_result_for(
                    row["match_number"], row["stage"], row["name"], row["away_name"]
                )
                if demo_actual:
                    cur.execute(
                        """
                        UPDATE fixtures
                        SET actual_home_score = %s,
                            actual_away_score = %s,
                            home_score = %s,
                            away_score = %s,
                            home_penalties = %s,
                            away_penalties = %s,
                            status = 'completed',
                            winner_team_id = (SELECT id FROM teams WHERE name = %s),
                            result_source = 'demo_synthetic',
                            last_result_sync = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                        """,
                        (
                            demo_actual["actual_home_score"],
                            demo_actual["actual_away_score"],
                            demo_actual["actual_home_score"],
                            demo_actual["actual_away_score"],
                            demo_actual["home_penalties"],
                            demo_actual["away_penalties"],
                            demo_actual["winner_team_name"],
                            row["fixture_id"],
                        ),
                    )
                    actual_stats = demo_actual["stats"]
                    cur.execute(
                        """
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
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'demo_synthetic', CURRENT_TIMESTAMP);
                        """,
                        (
                            row["fixture_id"],
                            actual_stats["home_shots"],
                            actual_stats["away_shots"],
                            actual_stats["home_shots_on_target"],
                            actual_stats["away_shots_on_target"],
                            actual_stats["home_possession"],
                            actual_stats["away_possession"],
                            actual_stats["home_corners"],
                            actual_stats["away_corners"],
                            actual_stats["home_yellow_cards"],
                            actual_stats["away_yellow_cards"],
                            actual_stats["home_red_cards"],
                            actual_stats["away_red_cards"],
                        ),
                    )

        conn.commit()
        print(f"Seed data loaded: {len(TEAMS)} teams, {len(FIXTURES)} knockout fixtures")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
