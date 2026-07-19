from app.db.connection import get_connection
from app.db.queries import get_recent_tournament_form
from app.ml.model import predict_match
from psycopg.types.json import Jsonb

# Seed data reflects the REAL 2026 FIFA World Cup knockout stage (Round of 32
# through the Final). Fixtures, pairings and scores were sourced from the
# openfootball/worldcup.json feed and cross-verified against Wikipedia's
# "2026 FIFA World Cup knockout stage" article and match reports (FIFA.com,
# NBC, Al Jazeera, ESPN) in July 2026. Kickoff times are stored as UTC.
#
# The 32 teams below are the real Round-of-32 participants. fifa_code and
# confederation are accurate; fifa_ranking and elo_rating are APPROXIMATE
# illustrative values on a descending scale (they feed the prediction model
# but were not the focus of this data refresh — refine against an official
# FIFA ranking / Elo source for more accurate predictions).
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

# venue/city are used across the app as the single-source-of-truth markers that
# scope every fixtures/bracket query (see DEMO_FIXTURE_VENUE/CITY in queries.py),
# so they stay as these stable marker strings rather than per-match stadium names.
KNOCKOUT_VENUE = "Knockout bracket"
KNOCKOUT_CITY = "World Cup 2026"

# Real Round of 32 pairings (the 16 opening knockout ties). Slots 1-8 are the
# left half of the bracket (they feed Semi-final 29), slots 9-16 the right half
# (they feed Semi-final 30). Every later round is *derived* from these results
# by chaining winners forward, so a team that loses can never reappear.
# Home/away orientation follows the official match listing.
# Tuple shape: (match_number, group_name, home_team, away_team, kickoff_time_utc)
ROUND_OF_32 = [
    # Left half
    (1, "Left bracket", "Germany", "Paraguay", "2026-06-29 20:30:00"),
    (2, "Left bracket", "France", "Sweden", "2026-06-30 21:00:00"),
    (3, "Left bracket", "South Africa", "Canada", "2026-06-28 19:00:00"),
    (4, "Left bracket", "Netherlands", "Morocco", "2026-06-30 01:00:00"),
    (5, "Left bracket", "Portugal", "Croatia", "2026-07-02 23:00:00"),
    (6, "Left bracket", "Spain", "Austria", "2026-07-02 19:00:00"),
    (7, "Left bracket", "USA", "Bosnia-Herz", "2026-07-02 00:00:00"),
    (8, "Left bracket", "Belgium", "Senegal", "2026-07-01 20:00:00"),
    # Right half
    (9, "Right bracket", "Brazil", "Japan", "2026-06-29 17:00:00"),
    (10, "Right bracket", "Ivory Coast", "Norway", "2026-06-30 17:00:00"),
    (11, "Right bracket", "Mexico", "Ecuador", "2026-07-01 01:00:00"),
    (12, "Right bracket", "England", "Congo DR", "2026-07-01 16:00:00"),
    (13, "Right bracket", "Argentina", "Cape Verde", "2026-07-03 22:00:00"),
    (14, "Right bracket", "Australia", "Egypt", "2026-07-03 18:00:00"),
    (15, "Right bracket", "Switzerland", "Algeria", "2026-07-03 03:00:00"),
    (16, "Right bracket", "Colombia", "Ghana", "2026-07-04 01:30:00"),
]

# Later-round slots, matching the REAL bracket tree. Home/away teams are NOT
# hardcoded — each is the advancing team from a prior-round match.
# ``home_source``/``away_source`` are the match_numbers whose winners feed this
# slot. Ordering + Left/Right groups reproduce the real path to the Final.
# Tuple shape: (match_number, stage, group_name, home_source, away_source, kickoff_time_utc)
BRACKET_PROGRESSION = [
    # Round of 16 (left half feeds SF 29, right half feeds SF 30)
    (17, "Round of 16", "Left bracket", 1, 2, "2026-07-04 21:00:00"),
    (18, "Round of 16", "Left bracket", 3, 4, "2026-07-04 17:00:00"),
    (19, "Round of 16", "Left bracket", 5, 6, "2026-07-06 19:00:00"),
    (20, "Round of 16", "Left bracket", 7, 8, "2026-07-07 00:00:00"),
    (21, "Round of 16", "Right bracket", 9, 10, "2026-07-05 20:00:00"),
    (22, "Round of 16", "Right bracket", 11, 12, "2026-07-06 00:00:00"),
    (23, "Round of 16", "Right bracket", 13, 14, "2026-07-07 16:00:00"),
    (24, "Round of 16", "Right bracket", 15, 16, "2026-07-07 20:00:00"),
    # Quarter-finals
    (25, "Quarter-final", "Left bracket", 17, 18, "2026-07-09 20:00:00"),
    (26, "Quarter-final", "Left bracket", 19, 20, "2026-07-10 19:00:00"),
    (27, "Quarter-final", "Right bracket", 21, 22, "2026-07-11 21:00:00"),
    (28, "Quarter-final", "Right bracket", 23, 24, "2026-07-12 01:00:00"),
    # Semi-finals
    (29, "Semi-final", "Left bracket", 25, 26, "2026-07-14 19:00:00"),
    (30, "Semi-final", "Right bracket", 27, 28, "2026-07-15 19:00:00"),
    # Final
    (31, "Final", "Champion pick", 29, 30, "2026-07-19 19:00:00"),
]

# The third-place play-off is contested by the two semi-final LOSERS (not
# winners), so it sits outside BRACKET_PROGRESSION's winner-chaining and is
# handled separately. Its stage is intentionally not in queries.KNOCKOUT_STAGES,
# so it appears on the Fixtures list but not inside the bracket tree.
# Tuple shape: (match_number, group_name, home_semi_source, away_semi_source, kickoff_time_utc)
THIRD_PLACE = (32, "Third place", 29, 30, "2026-07-18 21:00:00")

_TEAM_FEATURES = {name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo} for name, _code, _conf, ranking, elo in TEAMS}

# Real completed results, keyed by match_number. actual_home_score/away_score
# hold the decisive final score: for penalty shoot-outs that is the level
# 90'/extra-time score with home_penalties/away_penalties recorded; for matches
# won in extra time it is the after-extra-time scoreline. Only the Final (31)
# is absent — it had not kicked off at seeding time, so it stays scheduled with
# no score. openfootball scores don't include per-match detail stats (shots,
# possession, cards), so no fabricated actual stats are attached here.
ACTUAL_RESULTS = {
    # Round of 32
    1: {"actual_home_score": 1, "actual_away_score": 1, "winner_team_name": "Paraguay", "home_penalties": 3, "away_penalties": 4},
    2: {"actual_home_score": 3, "actual_away_score": 0, "winner_team_name": "France", "home_penalties": None, "away_penalties": None},
    3: {"actual_home_score": 0, "actual_away_score": 1, "winner_team_name": "Canada", "home_penalties": None, "away_penalties": None},
    4: {"actual_home_score": 1, "actual_away_score": 1, "winner_team_name": "Morocco", "home_penalties": 2, "away_penalties": 3},
    5: {"actual_home_score": 2, "actual_away_score": 1, "winner_team_name": "Portugal", "home_penalties": None, "away_penalties": None},
    6: {"actual_home_score": 3, "actual_away_score": 0, "winner_team_name": "Spain", "home_penalties": None, "away_penalties": None},
    7: {"actual_home_score": 2, "actual_away_score": 0, "winner_team_name": "USA", "home_penalties": None, "away_penalties": None},
    8: {"actual_home_score": 3, "actual_away_score": 2, "winner_team_name": "Belgium", "home_penalties": None, "away_penalties": None},  # a.e.t.
    9: {"actual_home_score": 2, "actual_away_score": 1, "winner_team_name": "Brazil", "home_penalties": None, "away_penalties": None},
    10: {"actual_home_score": 1, "actual_away_score": 2, "winner_team_name": "Norway", "home_penalties": None, "away_penalties": None},
    11: {"actual_home_score": 2, "actual_away_score": 0, "winner_team_name": "Mexico", "home_penalties": None, "away_penalties": None},
    12: {"actual_home_score": 2, "actual_away_score": 1, "winner_team_name": "England", "home_penalties": None, "away_penalties": None},
    13: {"actual_home_score": 3, "actual_away_score": 2, "winner_team_name": "Argentina", "home_penalties": None, "away_penalties": None},  # a.e.t.
    14: {"actual_home_score": 1, "actual_away_score": 1, "winner_team_name": "Egypt", "home_penalties": 2, "away_penalties": 4},
    15: {"actual_home_score": 2, "actual_away_score": 0, "winner_team_name": "Switzerland", "home_penalties": None, "away_penalties": None},
    16: {"actual_home_score": 1, "actual_away_score": 0, "winner_team_name": "Colombia", "home_penalties": None, "away_penalties": None},
    # Round of 16
    17: {"actual_home_score": 0, "actual_away_score": 1, "winner_team_name": "France", "home_penalties": None, "away_penalties": None},
    18: {"actual_home_score": 0, "actual_away_score": 3, "winner_team_name": "Morocco", "home_penalties": None, "away_penalties": None},
    19: {"actual_home_score": 0, "actual_away_score": 1, "winner_team_name": "Spain", "home_penalties": None, "away_penalties": None},
    20: {"actual_home_score": 1, "actual_away_score": 4, "winner_team_name": "Belgium", "home_penalties": None, "away_penalties": None},
    21: {"actual_home_score": 1, "actual_away_score": 2, "winner_team_name": "Norway", "home_penalties": None, "away_penalties": None},
    22: {"actual_home_score": 2, "actual_away_score": 3, "winner_team_name": "England", "home_penalties": None, "away_penalties": None},
    23: {"actual_home_score": 3, "actual_away_score": 2, "winner_team_name": "Argentina", "home_penalties": None, "away_penalties": None},
    24: {"actual_home_score": 0, "actual_away_score": 0, "winner_team_name": "Switzerland", "home_penalties": 4, "away_penalties": 3},
    # Quarter-finals
    25: {"actual_home_score": 2, "actual_away_score": 0, "winner_team_name": "France", "home_penalties": None, "away_penalties": None},
    26: {"actual_home_score": 2, "actual_away_score": 1, "winner_team_name": "Spain", "home_penalties": None, "away_penalties": None},
    27: {"actual_home_score": 1, "actual_away_score": 2, "winner_team_name": "England", "home_penalties": None, "away_penalties": None},  # a.e.t.
    28: {"actual_home_score": 3, "actual_away_score": 1, "winner_team_name": "Argentina", "home_penalties": None, "away_penalties": None},  # a.e.t.
    # Semi-finals
    29: {"actual_home_score": 0, "actual_away_score": 2, "winner_team_name": "Spain", "home_penalties": None, "away_penalties": None},
    30: {"actual_home_score": 1, "actual_away_score": 2, "winner_team_name": "Argentina", "home_penalties": None, "away_penalties": None},
    # Final (31) not yet played at seeding time — intentionally absent.
    # Third-place play-off
    32: {"actual_home_score": 4, "actual_away_score": 6, "winner_team_name": "England", "home_penalties": None, "away_penalties": None},
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
    """Winner of a slot: the real result if the match was played, else the model.

    Only the Final has no real result at seeding time; the model's predicted
    advancer stands in for it (and is not a source for any downstream slot).
    """
    result = ACTUAL_RESULTS.get(match_number)
    if result is not None:
        return _actual_winner(result, home_name, away_name)
    prediction = predict_match(
        _TEAM_FEATURES[home_name], _TEAM_FEATURES[away_name], stage=stage, neutral_venue=True
    )
    return _predicted_winner(prediction, home_name, away_name)


def build_chained_fixtures() -> list[tuple]:
    """Build the full knockout bracket by chaining real results forward.

    Round of 32 entrants are fixed; every later round's home/away team is the
    advancing team of the prior-round match that feeds that slot (the real
    winner where a result exists, otherwise the model's pick). The third-place
    play-off is fed by the two semi-final LOSERS. Deterministic, so re-running
    the seed reproduces the identical bracket.
    """
    winners: dict[int, str] = {}
    losers: dict[int, str] = {}
    fixtures: list[tuple] = []

    def record(match_number: int, stage: str, group: str, home_name: str, away_name: str, kickoff: str) -> None:
        fixtures.append(
            (match_number, stage, group, home_name, away_name, KNOCKOUT_VENUE, KNOCKOUT_CITY, kickoff)
        )
        winner = _resolve_winner(match_number, stage, home_name, away_name)
        winners[match_number] = winner
        losers[match_number] = away_name if winner == home_name else home_name

    for match_number, group, home_name, away_name, kickoff in ROUND_OF_32:
        record(match_number, "Round of 32", group, home_name, away_name, kickoff)

    for match_number, stage, group, home_source, away_source, kickoff in BRACKET_PROGRESSION:
        record(match_number, stage, group, winners[home_source], winners[away_source], kickoff)

    # Third-place play-off: contested by the two semi-final losers.
    tp_number, tp_group, home_semi, away_semi, tp_kickoff = THIRD_PLACE
    record(tp_number, "Third-place play-off", tp_group, losers[home_semi], losers[away_semi], tp_kickoff)

    return fixtures


# Chained bracket used for seeding and consumed by tests. Tuple shape:
# (match_number, stage, group, home, away, venue, city, kickoff).
FIXTURES = build_chained_fixtures()


def _completed_result_for(match_number: int, stage: str, home_name: str, away_name: str) -> dict | None:
    """Real completed-match payload for a slot, or None if it is still scheduled.

    Every knockout match that has been played has a real entry in
    ACTUAL_RESULTS; matches not yet played (only the Final) return None so they
    stay scheduled with no score.
    """
    return ACTUAL_RESULTS.get(match_number)


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
                SELECT f.id AS fixture_id, f.match_number, f.stage,
                       f.home_team_id, f.away_team_id, f.kickoff_time,
                       ht.*, at.name AS away_name,
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

            # Commit the fixture reset / prediction wipe before generating any
            # predictions, so each fixture's tournament-form lookup (which reads
            # via a separate cursor/connection) sees a consistent, up-to-date view
            # of prior fixtures and predictions rather than stale pre-reseed data.
            conn.commit()

            # Fixtures are processed in match_number order, which follows the real
            # bracket chronology (Round of 32 before Round of 16, etc.), so by the
            # time a fixture is predicted every earlier-kickoff match it could draw
            # form from has already had its prediction and actual score committed.
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
                # Form is drawn only from matches that kicked off before this one
                # (no lookahead). A team's very first tournament match returns no
                # rows here, so its form adjustment is exactly 0.0.
                home_form = get_recent_tournament_form(row["home_team_id"], row["kickoff_time"])
                away_form = get_recent_tournament_form(row["away_team_id"], row["kickoff_time"])
                prediction = predict_match(
                    home_team,
                    away_team,
                    stage=row["stage"],
                    neutral_venue=True,
                    home_form=home_form,
                    away_form=away_form,
                )
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

                result = _completed_result_for(
                    row["match_number"], row["stage"], row["name"], row["away_name"]
                )
                if result:
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
                            result_source = 'openfootball',
                            last_result_sync = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                        """,
                        (
                            result["actual_home_score"],
                            result["actual_away_score"],
                            result["actual_home_score"],
                            result["actual_away_score"],
                            result["home_penalties"],
                            result["away_penalties"],
                            result["winner_team_name"],
                            row["fixture_id"],
                        ),
                    )
                # Real results carry the score only; detailed match stats (shots,
                # possession, cards) are not available from this source and are
                # left to the Wikipedia stats-binding path, so nothing fabricated
                # is written here. Kept guarded in case a source later supplies them.
                if result and result.get("stats"):
                    actual_stats = result["stats"]
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
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'openfootball', CURRENT_TIMESTAMP);
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

                # Commit this fixture's prediction and actual result before moving
                # on, so the next fixture's tournament-form lookup can see it.
                conn.commit()

        conn.commit()
        print(f"Seed data loaded: {len(TEAMS)} teams, {len(FIXTURES)} knockout fixtures")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
