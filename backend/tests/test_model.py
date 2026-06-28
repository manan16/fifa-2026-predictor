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


def test_predict_match_returns_valid_probabilities():
    prediction = predict_match(
        {"name": "Brazil", "fifa_ranking": 5, "elo_rating": 2130},
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


def test_predicted_match_stats_return_required_fields_and_constraints():
    prediction = predict_match(
        {"name": "Brazil", "fifa_ranking": 5, "elo_rating": 2130},
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
