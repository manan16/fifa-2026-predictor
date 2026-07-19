from collections import Counter

from app.db.seed import BRACKET_PROGRESSION, DEMO_ACTUAL_RESULTS, FIXTURES, ROUND_OF_32, TEAMS
from app.ml.model import calculate_confidence, predict_match

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
    demo = DEMO_ACTUAL_RESULTS.get(match_number)
    if demo is not None:
        home_score, away_score = demo["actual_home_score"], demo["actual_away_score"]
        if home_score != away_score:
            return home_name if home_score > away_score else away_name
        return demo["winner_team_name"]
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


def test_confidence_is_expected_label():
    assert calculate_confidence({"home": 0.5, "draw": 0.27, "away": 0.23}) in {
        "Low",
        "Medium",
        "High",
    }
