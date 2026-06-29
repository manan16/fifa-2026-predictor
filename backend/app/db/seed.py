from app.db.connection import get_connection
from app.ml.model import predict_match
from psycopg.types.json import Jsonb

# Seed data mirrors the demo knockout bracket screenshot.
# Kickoff times are stored as London-local timestamps for display in the MVP.
TEAMS = [
    ("Argentina", "ARG", "CONMEBOL", 1, 2145),
    ("France", "FRA", "UEFA", 2, 2110),
    ("Spain", "ESP", "UEFA", 3, 2100),
    ("England", "ENG", "UEFA", 4, 2055),
    ("Brazil", "BRA", "CONMEBOL", 5, 2130),
    ("Portugal", "POR", "UEFA", 6, 2025),
    ("Netherlands", "NED", "UEFA", 7, 2015),
    ("Belgium", "BEL", "UEFA", 8, 1990),
    ("Germany", "GER", "UEFA", 10, 1980),
    ("Croatia", "CRO", "UEFA", 12, 1955),
    ("Morocco", "MAR", "CAF", 13, 1900),
    ("Switzerland", "SUI", "UEFA", 16, 1885),
    ("Japan", "JPN", "AFC", 18, 1875),
    ("USA", "USA", "CONCACAF", 20, 1850),
    ("Austria", "AUT", "UEFA", 22, 1840),
    ("Sweden", "SWE", "UEFA", 28, 1810),
    ("Senegal", "SEN", "CAF", 30, 1800),
    ("Colombia", "COL", "CONMEBOL", 31, 1795),
    ("Ecuador", "ECU", "CONMEBOL", 32, 1785),
    ("Canada", "CAN", "CONCACAF", 35, 1765),
    ("Australia", "AUS", "AFC", 38, 1745),
    ("Paraguay", "PAR", "CONMEBOL", 48, 1715),
    ("Ivory Coast", "CIV", "CAF", 49, 1705),
    ("Norway", "NOR", "UEFA", 50, 1700),
    ("Algeria", "ALG", "CAF", 51, 1695),
    ("Mexico", "MEX", "CONCACAF", 54, 1685),
    ("Egypt", "EGY", "CAF", 55, 1680),
    ("South Africa", "RSA", "CAF", 58, 1645),
    ("Congo DR", "COD", "CAF", 60, 1620),
    ("Cape Verde", "CPV", "CAF", 65, 1590),
    ("Bosnia-Herz", "BIH", "UEFA", 70, 1575),
    ("Ghana", "GHA", "CAF", 72, 1565),
]

FIXTURES = [
    # Round of 32
    (1, "Round of 32", "Left bracket", "South Africa", "Canada", "Knockout bracket", "World Cup 2026", "2026-06-28 20:00:00"),
    (2, "Round of 32", "Right bracket", "Brazil", "Japan", "Knockout bracket", "World Cup 2026", "2026-06-29 18:00:00"),
    (3, "Round of 32", "Left bracket", "Germany", "Paraguay", "Knockout bracket", "World Cup 2026", "2026-06-29 21:30:00"),
    (4, "Round of 32", "Left bracket", "Netherlands", "Morocco", "Knockout bracket", "World Cup 2026", "2026-06-30 02:00:00"),
    (5, "Round of 32", "Right bracket", "Ivory Coast", "Norway", "Knockout bracket", "World Cup 2026", "2026-06-30 18:00:00"),
    (6, "Round of 32", "Left bracket", "France", "Sweden", "Knockout bracket", "World Cup 2026", "2026-06-30 22:00:00"),
    (7, "Round of 32", "Right bracket", "Mexico", "Ecuador", "Knockout bracket", "World Cup 2026", "2026-07-01 02:00:00"),
    (8, "Round of 32", "Right bracket", "England", "Congo DR", "Knockout bracket", "World Cup 2026", "2026-07-01 17:00:00"),
    (9, "Round of 32", "Left bracket", "Belgium", "Senegal", "Knockout bracket", "World Cup 2026", "2026-07-01 21:00:00"),
    (10, "Round of 32", "Left bracket", "USA", "Bosnia-Herz", "Knockout bracket", "World Cup 2026", "2026-07-02 01:00:00"),
    (11, "Round of 32", "Left bracket", "Spain", "Austria", "Knockout bracket", "World Cup 2026", "2026-07-02 20:00:00"),
    (12, "Round of 32", "Left bracket", "Portugal", "Croatia", "Knockout bracket", "World Cup 2026", "2026-07-03 00:00:00"),
    (13, "Round of 32", "Right bracket", "Switzerland", "Algeria", "Knockout bracket", "World Cup 2026", "2026-07-03 04:00:00"),
    (14, "Round of 32", "Right bracket", "Australia", "Egypt", "Knockout bracket", "World Cup 2026", "2026-07-03 19:00:00"),
    (15, "Round of 32", "Right bracket", "Argentina", "Cape Verde", "Knockout bracket", "World Cup 2026", "2026-07-03 23:00:00"),
    (16, "Round of 32", "Right bracket", "Colombia", "Ghana", "Knockout bracket", "World Cup 2026", "2026-07-04 02:30:00"),
    # Round of 16
    (17, "Round of 16", "Left bracket", "South Africa", "Morocco", "Knockout bracket", "World Cup 2026", "2026-07-04 18:00:00"),
    (18, "Round of 16", "Left bracket", "Germany", "France", "Knockout bracket", "World Cup 2026", "2026-07-04 22:00:00"),
    (19, "Round of 16", "Right bracket", "Brazil", "Norway", "Knockout bracket", "World Cup 2026", "2026-07-05 21:00:00"),
    (20, "Round of 16", "Right bracket", "Mexico", "England", "Knockout bracket", "World Cup 2026", "2026-07-06 01:00:00"),
    (21, "Round of 16", "Left bracket", "Portugal", "Spain", "Knockout bracket", "World Cup 2026", "2026-07-06 20:00:00"),
    (22, "Round of 16", "Left bracket", "USA", "Belgium", "Knockout bracket", "World Cup 2026", "2026-07-07 01:00:00"),
    (23, "Round of 16", "Right bracket", "Argentina", "Australia", "Knockout bracket", "World Cup 2026", "2026-07-07 17:00:00"),
    (24, "Round of 16", "Right bracket", "Switzerland", "Colombia", "Knockout bracket", "World Cup 2026", "2026-07-07 21:00:00"),
    # Quarter-finals
    (25, "Quarter-final", "Left bracket", "France", "Morocco", "Knockout bracket", "World Cup 2026", "2026-07-09 21:00:00"),
    (26, "Quarter-final", "Left bracket", "Portugal", "USA", "Knockout bracket", "World Cup 2026", "2026-07-10 20:00:00"),
    (27, "Quarter-final", "Right bracket", "Brazil", "England", "Knockout bracket", "World Cup 2026", "2026-07-11 22:00:00"),
    (28, "Quarter-final", "Right bracket", "Argentina", "Colombia", "Knockout bracket", "World Cup 2026", "2026-07-12 02:00:00"),
    # Semi-finals and final
    (29, "Semi-final", "Left bracket", "France", "Portugal", "Knockout bracket", "World Cup 2026", "2026-07-14 20:00:00"),
    (30, "Semi-final", "Right bracket", "Brazil", "Argentina", "Knockout bracket", "World Cup 2026", "2026-07-15 20:00:00"),
    (31, "Final", "Champion pick", "France", "Argentina", "Knockout bracket", "World Cup 2026", "2026-07-19 20:00:00"),
]

DEMO_ACTUAL_RESULTS = {
    1: {
        "actual_home_score": 1,
        "actual_away_score": 2,
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
        "actual_home_score": 3,
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
                cur.execute(
                    """
                    UPDATE fixtures
                    SET match_number = %s,
                        group_name = %s,
                        venue = %s,
                        city = %s,
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
                    WHERE stage = %s
                      AND home_team_id = (SELECT id FROM teams WHERE name = %s)
                      AND away_team_id = (SELECT id FROM teams WHERE name = %s)
                      AND kickoff_time = %s
                    RETURNING id;
                    """,
                    (
                        fixture[0],
                        fixture[2],
                        fixture[5],
                        fixture[6],
                        fixture[1],
                        fixture[3],
                        fixture[4],
                        fixture[7],
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

                demo_actual = DEMO_ACTUAL_RESULTS.get(row["match_number"])
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
                            result_source = 'demo_manual',
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
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'demo_manual', CURRENT_TIMESTAMP);
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
