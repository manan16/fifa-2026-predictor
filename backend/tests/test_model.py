from app.ml.model import calculate_confidence, predict_match


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


def test_confidence_is_expected_label():
    assert calculate_confidence({"home": 0.5, "draw": 0.27, "away": 0.23}) in {
        "Low",
        "Medium",
        "High",
    }

