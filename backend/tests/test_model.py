from collections import Counter

import pytest

from app.db.seed import ACTUAL_RESULTS, BRACKET_PROGRESSION, FIXTURES, ROUND_OF_32, THIRD_PLACE, TEAMS
from app.ml.model import (
    FORM_ADJUSTMENT_CAP,
    calculate_confidence,
    calculate_form_adjustment,
    calculate_team_strength,
    predict_extra_time_and_penalties,
    predict_match,
)


def _form_row(side, actual_home, actual_away, predicted_home, predicted_away):
    """A single get_recent_tournament_form-shaped row for form tests."""
    return {
        "side": side,
        "actual_home_score": actual_home,
        "actual_away_score": actual_away,
        "predicted_home_goals": predicted_home,
        "predicted_away_goals": predicted_away,
    }

REQUIRED_STATS_FIELDS = {
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
}

PROBABILITY_STATS_FIELDS = {
    "home_red_card_probability",
    "away_red_card_probability",
    "both_teams_to_score_probability",
    "over_2_5_goals_probability",
    "clean_sheet_home_probability",
    "clean_sheet_away_probability",
}

ARGENTINA = {"name": "Argentina", "fifa_ranking": 1, "elo_rating": 2145}
CAPE_VERDE = {"name": "Cape Verde", "fifa_ranking": 65, "elo_rating": 1590}


def test_predict_match_returns_valid_probabilities():
    prediction = predict_match(
        {"name": "Brazil", "fifa_ranking": 6, "elo_rating": 2130},
        {"name": "Japan", "fifa_ranking": 18, "elo_rating": 1875},
    )

    total = (
        prediction["home_win_probability"]
        + prediction["draw_probability"]
        + prediction["away_win_probability"]
    )
    assert round(total, 6) == 1
    assert prediction["predicted_home_goals"] >= 0
    assert prediction["predicted_away_goals"] >= 0
    assert prediction["confidence"] in {"Low", "Medium", "High"}


def test_neutral_scoreline_and_probabilities_are_slot_symmetric():
    home_prediction = predict_match(ARGENTINA, CAPE_VERDE, stage="Round of 32", neutral_venue=True)
    away_prediction = predict_match(CAPE_VERDE, ARGENTINA, stage="Round of 32", neutral_venue=True)

    assert home_prediction["predicted_home_goals"] == away_prediction["predicted_away_goals"]
    assert home_prediction["predicted_away_goals"] == away_prediction["predicted_home_goals"]
    assert home_prediction["home_win_probability"] == away_prediction["away_win_probability"]
    assert home_prediction["away_win_probability"] == away_prediction["home_win_probability"]
    assert home_prediction["draw_probability"] == away_prediction["draw_probability"]


def test_severe_mismatch_produces_large_favourite_margin_regardless_of_slot():
    home_prediction = predict_match(ARGENTINA, CAPE_VERDE, stage="Round of 32", neutral_venue=True)
    away_prediction = predict_match(CAPE_VERDE, ARGENTINA, stage="Round of 32", neutral_venue=True)

    assert home_prediction["predicted_home_goals"] >= 3
    assert home_prediction["predicted_home_goals"] - home_prediction["predicted_away_goals"] >= 3
    assert away_prediction["predicted_away_goals"] >= 3
    assert away_prediction["predicted_away_goals"] - away_prediction["predicted_home_goals"] >= 3


def test_even_match_does_not_create_spurious_blowout():
    team_a = {"name": "Team A", "fifa_ranking": 12, "elo_rating": 1900}
    team_b = {"name": "Team B", "fifa_ranking": 13, "elo_rating": 1895}
    prediction = predict_match(team_a, team_b, stage="Quarter-final", neutral_venue=True)

    margin = abs(prediction["predicted_home_goals"] - prediction["predicted_away_goals"])
    assert margin <= 1


def test_stronger_favourite_does_not_lose_goals_or_win_probability():
    favourite = {"name": "Brazil", "fifa_ranking": 6, "elo_rating": 2130}
    stronger_favourite = {"name": "Brazil", "fifa_ranking": 1, "elo_rating": 2250}
    underdog = {"name": "Japan", "fifa_ranking": 18, "elo_rating": 1875}

    base_prediction = predict_match(favourite, underdog, stage="Round of 32", neutral_venue=True)
    stronger_prediction = predict_match(stronger_favourite, underdog, stage="Round of 32", neutral_venue=True)

    assert stronger_prediction["predicted_home_goals"] >= base_prediction["predicted_home_goals"]
    assert stronger_prediction["home_win_probability"] >= base_prediction["home_win_probability"]


def test_seeded_fixture_scorelines_do_not_collapse_to_one_result():
    teams = {
        name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo}
        for name, _code, _confederation, ranking, elo in TEAMS
    }
    scorelines = []
    for _match_number, stage, _group, home_name, away_name, *_rest in FIXTURES:
        prediction = predict_match(teams[home_name], teams[away_name], stage=stage, neutral_venue=True)
        scorelines.append(f"{prediction['predicted_home_goals']}-{prediction['predicted_away_goals']}")

    _scoreline, count = Counter(scorelines).most_common(1)[0]
    assert count / len(scorelines) <= 0.40


def test_predicted_match_stats_return_required_fields_and_constraints():
    prediction = predict_match(
        {"name": "Brazil", "fifa_ranking": 6, "elo_rating": 2130},
        {"name": "Japan", "fifa_ranking": 18, "elo_rating": 1875},
        stage="Round of 32",
    )
    stats = prediction["predicted_stats"]

    assert REQUIRED_STATS_FIELDS.issubset(stats)
    assert round(stats["home_possession"] + stats["away_possession"], 6) == 100
    assert stats["home_shots_on_target"] <= stats["home_shots"]
    assert stats["away_shots_on_target"] <= stats["away_shots"]
    for field in PROBABILITY_STATS_FIELDS:
        assert 0 <= stats[field] <= 1


def _expected_winner(stage, home_name, away_name, match_number, teams):
    """Independently recompute the advancing team, mirroring the seed's rule."""
    result = ACTUAL_RESULTS.get(match_number)
    if result is not None:
        home_score, away_score = result["actual_home_score"], result["actual_away_score"]
        if home_score != away_score:
            return home_name if home_score > away_score else away_name
        return result["winner_team_name"]
    prediction = predict_match(teams[home_name], teams[away_name], stage=stage, neutral_venue=True)
    home_advance = prediction.get("home_advance_probability")
    away_advance = prediction.get("away_advance_probability")
    if home_advance is not None and away_advance is not None and home_advance != away_advance:
        return home_name if home_advance > away_advance else away_name
    if prediction["home_win_probability"] != prediction["away_win_probability"]:
        return home_name if prediction["home_win_probability"] > prediction["away_win_probability"] else away_name
    return home_name


def test_bracket_is_chained_and_consistent_round_to_round():
    teams = {
        name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo}
        for name, _code, _confederation, ranking, elo in TEAMS
    }
    fixtures_by_number = {fx[0]: fx for fx in FIXTURES}

    # Winner of every slot, recomputed independently of the seed's bookkeeping.
    winners = {}
    for match_number, _group, home_name, away_name, _kickoff in ROUND_OF_32:
        winners[match_number] = _expected_winner("Round of 32", home_name, away_name, match_number, teams)

    round_32_entrants = {name for _n, _g, home, away, _k in ROUND_OF_32 for name in (home, away)}

    for match_number, stage, _group, home_source, away_source, _kickoff in BRACKET_PROGRESSION:
        _n, _stage, _grp, home_name, away_name, _venue, _city, _kick = fixtures_by_number[match_number]

        # Each team in a later round must be the advancing team of its feeding match.
        assert home_name == winners[home_source], (
            f"match {match_number} home {home_name!r} != winner of match {home_source}"
        )
        assert away_name == winners[away_source], (
            f"match {match_number} away {away_name!r} != winner of match {away_source}"
        )
        winners[match_number] = _expected_winner(stage, home_name, away_name, match_number, teams)

    # No team appears in any round unless it originally entered in the Round of 32.
    for _n, _stage, _grp, home_name, away_name, _venue, _city, _kick in FIXTURES:
        assert home_name in round_32_entrants
        assert away_name in round_32_entrants


def test_round_of_16_teams_all_won_in_round_of_32():
    round_32_numbers = {n for n, *_ in ROUND_OF_32}
    round_of_16 = [fx for fx in FIXTURES if fx[1] == "Round of 16"]
    assert len(round_of_16) == 8

    # Losing side of every Round of 32 match, keyed by the eliminated team name.
    teams = {
        name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo}
        for name, _code, _confederation, ranking, elo in TEAMS
    }
    eliminated = set()
    for match_number, _group, home_name, away_name, _kickoff in ROUND_OF_32:
        winner = _expected_winner("Round of 32", home_name, away_name, match_number, teams)
        eliminated.add(away_name if winner == home_name else home_name)

    for _n, _stage, _grp, home_name, away_name, *_rest in round_of_16:
        assert home_name not in eliminated
        assert away_name not in eliminated
    assert round_32_numbers  # sanity: fixtures were actually built


def test_third_place_play_off_is_contested_by_semifinal_losers():
    fixtures_by_number = {fx[0]: fx for fx in FIXTURES}
    teams = {
        name: {"name": name, "fifa_ranking": ranking, "elo_rating": elo}
        for name, _code, _confederation, ranking, elo in TEAMS
    }
    tp_number, _group, home_semi, away_semi, _kickoff = THIRD_PLACE
    third_place = fixtures_by_number[tp_number]
    assert third_place[1] == "Third-place play-off"

    def loser(semi_number):
        _n, stage, _grp, home_name, away_name, *_rest = fixtures_by_number[semi_number]
        winner = _expected_winner(stage, home_name, away_name, semi_number, teams)
        return away_name if winner == home_name else home_name

    # The third-place teams are exactly the two semi-final losers.
    assert third_place[3] == loser(home_semi)
    assert third_place[4] == loser(away_semi)


def test_advance_breakdown_components_sum_to_advance_probability():
    # Two closely-matched sides give a genuinely non-degenerate three-way split.
    home = {"name": "Portugal", "fifa_ranking": 5, "elo_rating": 2025}
    away = {"name": "Spain", "fifa_ranking": 2, "elo_rating": 2100}
    prediction = predict_match(home, away, stage="Quarter-final", neutral_venue=True)

    for side in ("home", "away"):
        components = (
            prediction[f"{side}_win_in_90_probability"]
            + prediction[f"{side}_win_in_et_probability"]
            + prediction[f"{side}_win_on_penalties_probability"]
        )
        assert abs(components - prediction[f"{side}_advance_probability"]) < 1e-3

    assert abs(prediction["home_advance_probability"] + prediction["away_advance_probability"] - 1.0) < 1e-3
    # Not degenerate: the in-ET and on-penalties paths carry meaningful weight.
    assert prediction["home_win_in_et_probability"] > 0.01
    assert prediction["home_win_on_penalties_probability"] > 0.01


def test_penalty_probability_stays_near_coin_flip_for_any_strength_gap():
    for home_strength, away_strength in [(3000.0, 1000.0), (1000.0, 3000.0), (2200.0, 1400.0)]:
        et_pen = predict_extra_time_and_penalties(home_strength, away_strength, 0.3, stage="Final")
        assert 0.42 <= et_pen["penalty_home_win_probability"] <= 0.58
        assert 0.42 <= et_pen["penalty_away_win_probability"] <= 0.58
        assert round(et_pen["penalty_home_win_probability"] + et_pen["penalty_away_win_probability"], 4) == 1.0

    # The largest strength gap in the current roster (Argentina vs Ghana) is still capped.
    strong = calculate_team_strength({"fifa_ranking": 1, "elo_rating": 2145})
    weak = calculate_team_strength({"fifa_ranking": 73, "elo_rating": 1565})
    biggest_gap = predict_extra_time_and_penalties(strong, weak, 0.3, stage="Round of 32")
    assert 0.42 <= biggest_gap["penalty_home_win_probability"] <= 0.58


def test_third_place_play_off_skips_extra_time():
    strong = calculate_team_strength({"fifa_ranking": 3, "elo_rating": 2110})
    weak = calculate_team_strength({"fifa_ranking": 15, "elo_rating": 1800})
    et_pen = predict_extra_time_and_penalties(strong, weak, 0.3, stage="Third-place play-off")
    # Extra time is skipped entirely: a level match goes straight to penalties.
    assert et_pen["et_draw_probability"] == 1.0
    assert et_pen["et_home_win_probability"] == 0.0
    assert et_pen["et_away_win_probability"] == 0.0

    prediction = predict_match(
        {"name": "France", "fifa_ranking": 3, "elo_rating": 2110},
        {"name": "Senegal", "fifa_ranking": 15, "elo_rating": 1800},
        stage="Third-place play-off",
    )
    assert prediction["home_win_in_et_probability"] == 0.0
    assert prediction["away_win_in_et_probability"] == 0.0
    # The whole 90' draw share resolves on penalties instead.
    assert prediction["home_win_on_penalties_probability"] > 0.0


def test_group_stage_has_no_knockout_resolution_fields():
    prediction = predict_match(
        {"name": "Brazil", "fifa_ranking": 6, "elo_rating": 2130},
        {"name": "Japan", "fifa_ranking": 18, "elo_rating": 1875},
        stage="group",
    )
    knockout_keys = [
        key
        for key in prediction
        if "advance" in key or key.startswith("et_") or "penalt" in key or "_in_90" in key or "_in_et" in key
    ]
    assert knockout_keys == []


def test_form_adjustment_is_zero_for_no_completed_matches():
    # A team's very first tournament match has no prior form and must be unaffected.
    assert calculate_form_adjustment([]) == 0.0


def test_form_adjustment_positive_and_capped_when_consistently_overperforming():
    # Team (home) keeps winning by more than the model predicted: residual +3/game.
    overperformer = [
        _form_row("home", 4, 0, 1, 0),
        _form_row("home", 3, 0, 1, 1),  # actual diff +3, predicted diff 0 -> +3
        _form_row("away", 0, 3, 1, 1),  # away perspective: actual +3, predicted -1 -> +4
    ]
    adjustment = calculate_form_adjustment(overperformer)
    assert adjustment > 0
    assert adjustment == FORM_ADJUSTMENT_CAP  # mean residual scales well past the cap

    # An intentionally extreme residual is still clamped to exactly the cap.
    extreme = [_form_row("home", 100, 0, 0, 0)]
    assert calculate_form_adjustment(extreme) == FORM_ADJUSTMENT_CAP


def test_form_adjustment_negative_and_capped_when_consistently_underperforming():
    underperformer = [
        _form_row("home", 0, 4, 1, 0),  # actual diff -4, predicted +1 -> -5
        _form_row("away", 4, 0, 1, 1),  # away perspective: actual -4, predicted 0 -> -4
    ]
    adjustment = calculate_form_adjustment(underperformer)
    assert adjustment < 0
    assert adjustment == -FORM_ADJUSTMENT_CAP

    extreme = [_form_row("away", 100, 0, 0, 0)]
    assert calculate_form_adjustment(extreme) == -FORM_ADJUSTMENT_CAP


def test_team_strength_adds_form_adjustment_exactly():
    team = {"name": "Test", "fifa_ranking": 12, "elo_rating": 1900}
    baseline = calculate_team_strength(team)
    with_form = calculate_team_strength(team, 25.0)
    assert with_form - baseline == 25.0
    assert calculate_team_strength(team, -18.5) - baseline == -18.5


def test_predict_match_without_form_matches_baseline():
    baseline = predict_match(ARGENTINA, CAPE_VERDE, stage="Round of 16", neutral_venue=True)
    # Passing empty/None form must be a no-op relative to the pre-form baseline.
    with_empty_form = predict_match(
        ARGENTINA, CAPE_VERDE, stage="Round of 16", neutral_venue=True, home_form=[], away_form=None
    )
    assert baseline == with_empty_form
    assert baseline["home_form_adjustment"] == 0.0
    assert baseline["away_form_adjustment"] == 0.0


def test_predict_match_surfaces_form_and_mentions_it_when_large():
    strong_form = [_form_row("home", 4, 0, 1, 0), _form_row("home", 3, 0, 1, 1)]
    prediction = predict_match(
        CAPE_VERDE, ARGENTINA, stage="Round of 16", neutral_venue=True, home_form=strong_form
    )
    assert prediction["home_form_adjustment"] > 0
    assert any("outperformed" in line for line in prediction["explanation"])
    # A team with no form data draws no form line in the explanation.
    quiet = predict_match(CAPE_VERDE, ARGENTINA, stage="Round of 16", neutral_venue=True)
    assert not any(
        "outperformed" in line or "underperformed" in line for line in quiet["explanation"]
    )


def test_confidence_is_expected_label():
    assert calculate_confidence({"home": 0.5, "draw": 0.27, "away": 0.23}) in {
        "Low",
        "Medium",
        "High",
    }


def test_get_recent_tournament_form_respects_kickoff_and_completion(app):
    """Integration test against the DB: only completed fixtures strictly before
    the cutoff are returned, most-recent first, with the stored prediction joined.

    Inserts a small controlled set of teams/fixtures/predictions inside the test
    transaction and rolls it all back, so it neither depends on nor mutates the
    seeded data. Skips when no database is reachable.
    """
    import psycopg

    from app.db import queries
    from app.db.connection import get_connection

    with app.app_context():
        try:
            conn = get_connection()
        except psycopg.OperationalError:
            pytest.skip("No database available for the tournament-form integration test.")

        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO teams (name) VALUES ('FormTest United') RETURNING id;")
                team_id = cur.fetchone()["id"]
                cur.execute("INSERT INTO teams (name) VALUES ('FormTest Rovers') RETURNING id;")
                opp_id = cur.fetchone()["id"]

                def add_fixture(match_number, kickoff, home, away, home_score, away_score, ph, pa):
                    cur.execute(
                        """
                        INSERT INTO fixtures (
                            match_number, stage, home_team_id, away_team_id,
                            venue, city, kickoff_time, status,
                            actual_home_score, actual_away_score
                        )
                        VALUES (%s, 'Round of 32', %s, %s, 'Test', 'Test', %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (
                            match_number,
                            home,
                            away,
                            kickoff,
                            "completed" if home_score is not None else "scheduled",
                            home_score,
                            away_score,
                        ),
                    )
                    fixture_id = cur.fetchone()["id"]
                    cur.execute(
                        """
                        INSERT INTO predictions (
                            fixture_id, model_version, predicted_home_goals, predicted_away_goals
                        )
                        VALUES (%s, 'test', %s, %s);
                        """,
                        (fixture_id, ph, pa),
                    )
                    return fixture_id

                # Earliest completed (team at home), then a later completed (team away).
                add_fixture(900001, "2026-06-20T18:00:00", team_id, opp_id, 2, 1, 1, 1)
                add_fixture(900002, "2026-06-25T18:00:00", opp_id, team_id, 0, 3, 1, 1)
                # Unplayed fixture before the cutoff -> excluded (null actual score).
                add_fixture(900003, "2026-06-28T18:00:00", team_id, opp_id, None, None, 1, 0)
                # Completed but AFTER the cutoff -> excluded (would be lookahead).
                add_fixture(900004, "2026-07-05T18:00:00", team_id, opp_id, 5, 0, 1, 0)

            form = queries.get_recent_tournament_form(team_id, "2026-07-01T00:00:00")

            # Only the two completed, pre-cutoff fixtures, most-recent first.
            assert len(form) == 2
            assert form[0]["side"] == "away"  # 2026-06-25 fixture, team was away
            assert form[0]["actual_home_score"] == 0
            assert form[0]["actual_away_score"] == 3
            assert form[0]["predicted_home_goals"] == 1
            assert form[1]["side"] == "home"  # 2026-06-20 fixture, team was home
            assert form[1]["actual_home_score"] == 2
        finally:
            conn.rollback()
