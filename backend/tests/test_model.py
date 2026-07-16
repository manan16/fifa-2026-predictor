from collections import Counter

from app.db.seed import FIXTURES, TEAMS
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


def test_confidence_is_expected_label():
    assert calculate_confidence({"home": 0.5, "draw": 0.27, "away": 0.23}) in {
        "Low",
        "Medium",
        "High",
    }
