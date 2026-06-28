from app.db.connection import get_connection
from app.ml.model import predict_match
from psycopg.types.json import Jsonb

TEAMS = [
    ("Brazil", "BRA", "CONMEBOL", 5, 2130),
    ("Japan", "JPN", "AFC", 18, 1875),
    ("England", "ENG", "UEFA", 4, 2055),
    ("DR Congo", "COD", "CAF", 60, 1620),
    ("Argentina", "ARG", "CONMEBOL", 1, 2145),
    ("Cape Verde", "CPV", "CAF", 65, 1590),
    ("Germany", "GER", "UEFA", 10, 1980),
    ("Paraguay", "PAR", "CONMEBOL", 48, 1715),
    ("France", "FRA", "UEFA", 2, 2110),
    ("Sweden", "SWE", "UEFA", 28, 1810),
    ("Portugal", "POR", "UEFA", 6, 2025),
    ("Croatia", "CRO", "UEFA", 12, 1955),
    ("Spain", "ESP", "UEFA", 3, 2100),
    ("Austria", "AUT", "UEFA", 22, 1840),
    ("Netherlands", "NED", "UEFA", 7, 2015),
    ("Morocco", "MAR", "CAF", 13, 1900),
]

FIXTURES = [
    (1, "Group stage", "Sample A", "Brazil", "Japan", "MetLife Stadium", "East Rutherford", "2026-06-13 20:00:00"),
    (2, "Group stage", "Sample B", "Germany", "Paraguay", "BC Place", "Vancouver", "2026-06-14 18:00:00"),
    (3, "Group stage", "Sample C", "Netherlands", "Morocco", "Lumen Field", "Seattle", "2026-06-15 19:00:00"),
    (4, "Group stage", "Sample D", "France", "Sweden", "SoFi Stadium", "Inglewood", "2026-06-16 20:00:00"),
    (5, "Group stage", "Sample E", "England", "DR Congo", "AT&T Stadium", "Arlington", "2026-06-17 18:00:00"),
    (6, "Group stage", "Sample F", "Spain", "Austria", "Levi's Stadium", "Santa Clara", "2026-06-18 21:00:00"),
    (7, "Round of 32", None, "Portugal", "Croatia", "Mercedes-Benz Stadium", "Atlanta", "2026-06-29 20:00:00"),
    (8, "Round of 32", None, "Argentina", "Cape Verde", "Hard Rock Stadium", "Miami", "2026-06-30 20:00:00"),
]


def seed_database() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for team in TEAMS:
                cur.execute(
                    """
                    INSERT INTO teams (name, fifa_code, confederation, fifa_ranking, elo_rating)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    team,
                )

            for fixture in FIXTURES:
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
                    )
                    ON CONFLICT (match_number) DO NOTHING;
                    """,
                    fixture,
                )

            cur.execute(
                """
                SELECT f.id AS fixture_id, f.stage, ht.*, at.name AS away_name,
                       at.fifa_code AS away_fifa_code, at.confederation AS away_confederation,
                       at.fifa_ranking AS away_fifa_ranking, at.elo_rating AS away_elo_rating
                FROM fixtures f
                JOIN teams ht ON f.home_team_id = ht.id
                JOIN teams at ON f.away_team_id = at.id
                WHERE NOT EXISTS (
                    SELECT 1 FROM predictions p WHERE p.fixture_id = f.id
                );
                """
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
                    VALUES (%s, 'elo-baseline-v1', %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        row["fixture_id"],
                        prediction["home_win_probability"],
                        prediction["draw_probability"],
                        prediction["away_win_probability"],
                        prediction["predicted_home_goals"],
                        prediction["predicted_away_goals"],
                        prediction["confidence"],
                        Jsonb(prediction["explanation"]),
                    ),
                )

        conn.commit()
        print("Seed data loaded")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
