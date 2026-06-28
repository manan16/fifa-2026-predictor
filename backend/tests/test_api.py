from app.routes import bracket as bracket_route
from app.routes import fixtures as fixtures_route
from app.routes import odds as odds_route
from app.routes import predictions as predictions_route
from app.routes import sync as sync_route
from app.routes import teams as teams_route

TEAM = {
    "id": 1,
    "name": "Brazil",
    "fifa_code": "BRA",
    "confederation": "CONMEBOL",
    "fifa_ranking": 5,
    "elo_rating": 2130,
}

AWAY_TEAM = {
    "id": 2,
    "name": "Japan",
    "fifa_code": "JPN",
    "confederation": "AFC",
    "fifa_ranking": 18,
    "elo_rating": 1875,
}

FIXTURE = {
    "id": 1,
    "match_number": 1,
    "stage": "Group stage",
    "home_team_id": 1,
    "away_team_id": 2,
    "home_team_name": "Brazil",
    "away_team_name": "Japan",
    "venue": "MetLife Stadium",
    "city": "East Rutherford",
}

PREDICTED_STATS = {
    "fixture_id": 1,
    "model_version": "elo-supremacy-dc-v2",
    "expected_home_goals": 1.85,
    "expected_away_goals": 0.95,
    "home_shots": 14,
    "away_shots": 9,
    "home_shots_on_target": 5,
    "away_shots_on_target": 3,
    "home_possession": 57.0,
    "away_possession": 43.0,
    "home_corners": 6,
    "away_corners": 4,
    "home_yellow_cards": 1,
    "away_yellow_cards": 2,
    "home_red_card_probability": 0.04,
    "away_red_card_probability": 0.05,
    "both_teams_to_score_probability": 0.48,
    "over_2_5_goals_probability": 0.51,
    "clean_sheet_home_probability": 0.39,
    "clean_sheet_away_probability": 0.16,
}


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "fifa-2026-predictor-api"}


def test_teams_endpoint_returns_data(client, monkeypatch):
    monkeypatch.setattr(teams_route.queries, "get_all_teams", lambda: [TEAM, AWAY_TEAM])
    response = client.get("/api/teams")
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Brazil"


def test_fixtures_endpoint_returns_data(client, monkeypatch):
    monkeypatch.setattr(fixtures_route.queries, "get_all_fixtures", lambda: [FIXTURE])
    response = client.get("/api/fixtures")
    assert response.status_code == 200
    assert response.get_json()[0]["home_team_name"] == "Brazil"


def test_prediction_endpoint_returns_expected_fields(client, monkeypatch):
    monkeypatch.setattr(predictions_route.queries, "get_prediction_by_fixture_id", lambda fixture_id: None)
    monkeypatch.setattr(predictions_route.queries, "get_fixture_by_id", lambda fixture_id: FIXTURE)
    monkeypatch.setattr(
        predictions_route.queries,
        "get_team_by_id",
        lambda team_id: TEAM if team_id == 1 else AWAY_TEAM,
    )
    monkeypatch.setattr(predictions_route.queries, "insert_prediction", lambda data: data)

    response = client.get("/api/predictions/1")
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["home_team"] == "Brazil"
    assert payload["away_team"] == "Japan"
    assert "confidence" in payload


def test_custom_predict_endpoint(client, monkeypatch):
    monkeypatch.setattr(
        predictions_route.queries,
        "get_team_by_name",
        lambda name: TEAM if name == "Brazil" else AWAY_TEAM,
    )

    response = client.post(
        "/api/predict",
        json={
            "home_team": "Brazil",
            "away_team": "Japan",
            "neutral_venue": True,
            "stage": "group",
        },
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert {"home_win_probability", "draw_probability", "away_win_probability"}.issubset(payload)
    assert round(
        payload["home_win_probability"] + payload["draw_probability"] + payload["away_win_probability"],
        6,
    ) == 1


def test_bracket_endpoint_returns_grouped_rounds(client, monkeypatch):
    bracket_rows = [
        {
            "id": 1,
            "match_number": 1,
            "stage": "Round of 32",
            "group_name": "Left bracket",
            "home_team_name": "Germany",
            "away_team_name": "Paraguay",
            "home_team_code": "GER",
            "away_team_code": "PAR",
            "kickoff_time": "2026-06-29T21:30:00",
            "home_win_probability": 0.61,
            "draw_probability": 0.22,
            "away_win_probability": 0.17,
            "home_advance_probability": 0.68,
            "away_advance_probability": 0.32,
            "predicted_home_goals": 2,
            "predicted_away_goals": 1,
            "confidence": "Medium",
            "actual_home_score": None,
            "actual_away_score": None,
            "home_penalties": None,
            "away_penalties": None,
            "actual_winner": None,
            "market_home_probability": 0.6,
            "market_draw_probability": 0.24,
            "market_away_probability": 0.16,
            "average_home_odds": 1.75,
            "average_draw_odds": 4.1,
            "average_away_odds": 5.8,
            "bookmaker_count": 8,
        },
        {
            "id": 31,
            "match_number": 31,
            "stage": "Final",
            "group_name": "Champion pick",
            "home_team_name": "France",
            "away_team_name": "Argentina",
            "home_team_code": "FRA",
            "away_team_code": "ARG",
            "kickoff_time": "2026-07-19T20:00:00",
            "home_win_probability": 0.36,
            "draw_probability": 0.27,
            "away_win_probability": 0.37,
            "home_advance_probability": 0.49,
            "away_advance_probability": 0.51,
            "predicted_home_goals": 1,
            "predicted_away_goals": 2,
            "confidence": "Low",
            "actual_home_score": None,
            "actual_away_score": None,
            "home_penalties": None,
            "away_penalties": None,
            "actual_winner": None,
            "market_home_probability": 0.36,
            "market_draw_probability": 0.27,
            "market_away_probability": 0.37,
            "average_home_odds": 2.75,
            "average_draw_odds": 3.7,
            "average_away_odds": 2.68,
            "bookmaker_count": 8,
        },
    ]
    monkeypatch.setattr(bracket_route.queries, "get_bracket_fixtures", lambda: bracket_rows)

    response = client.get("/api/bracket")
    payload = response.get_json()

    assert response.status_code == 200
    assert set(payload.keys()) == {
        "round_of_32",
        "round_of_16",
        "quarter_finals",
        "semi_finals",
        "final",
    }
    assert payload["final"][0]["home_team_name"] == "France"
    assert payload["final"][0]["away_team_name"] == "Argentina"
    assert payload["final"][0]["predicted_winner"] == "Argentina"

    fixture = payload["round_of_32"][0]
    assert {
        "predicted_winner",
        "home_win_probability",
        "draw_probability",
        "away_win_probability",
        "home_advance_probability",
        "away_advance_probability",
        "stage",
        "home_team_name",
        "away_team_name",
        "predicted_home_goals",
        "predicted_away_goals",
        "actual_home_score",
        "actual_away_score",
        "market_home_probability",
        "bookmaker_count",
    }.issubset(fixture)


def test_fixture_odds_endpoint_returns_consensus(client, monkeypatch):
    monkeypatch.setattr(fixtures_route.queries, "get_fixture_by_id", lambda fixture_id: FIXTURE)
    monkeypatch.setattr(
        fixtures_route.queries,
        "get_fixture_odds",
        lambda fixture_id: [{"bookmaker": "Bet365", "outcome_type": "home", "decimal_price": 1.82}],
    )
    monkeypatch.setattr(
        fixtures_route.queries,
        "get_odds_consensus_by_fixture_id",
        lambda fixture_id: {"home_probability": 0.55, "bookmaker_count": 8},
    )

    response = client.get("/api/fixtures/1/odds")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["consensus"]["home_probability"] == 0.55
    assert payload["odds"][0]["bookmaker"] == "Bet365"


def test_fixture_stats_endpoint_returns_expected_fields(client, monkeypatch):
    monkeypatch.setattr(fixtures_route.queries, "get_fixture_by_id", lambda fixture_id: FIXTURE)
    monkeypatch.setattr(fixtures_route.stats_prediction_service, "get_predicted_match_stats", lambda fixture_id: PREDICTED_STATS)
    monkeypatch.setattr(fixtures_route.stats_prediction_service, "get_actual_match_stats", lambda fixture_id: None)

    response = client.get("/api/fixtures/1/stats")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["fixture_id"] == 1
    assert payload["predicted"]["home_shots"] == 14
    assert payload["predicted_stats"]["home_shots"] == 14
    assert payload["actual"] is None
    assert {
        "expected_home_goals",
        "expected_away_goals",
        "home_possession",
        "away_possession",
        "over_2_5_goals_probability",
    }.issubset(payload["predicted_stats"])


def test_fixture_watch_endpoint_returns_links(client, monkeypatch):
    monkeypatch.setattr(fixtures_route.queries, "get_fixture_by_id", lambda fixture_id: FIXTURE)
    monkeypatch.setattr(
        fixtures_route.queries,
        "get_watch_links",
        lambda fixture_id: [
            {
                "region": "UK",
                "provider_name": "Official FIFA Match Centre",
                "provider_type": "official_match_centre",
                "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026",
                "is_official": True,
                "note": "Replace with confirmed broadcaster once available.",
            }
        ],
    )

    response = client.get("/api/fixtures/1/watch")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["fixture_id"] == 1
    assert payload["links"][0]["provider_name"] == "Official FIFA Match Centre"
    assert payload["links"][0]["is_official"] is True


def test_odds_endpoint_returns_latest_consensus(client, monkeypatch):
    monkeypatch.setattr(
        odds_route.queries,
        "get_latest_odds",
        lambda: [{"fixture_id": 1, "market_home_probability": 0.55, "bookmaker_count": 8}],
    )

    response = client.get("/api/odds")
    assert response.status_code == 200
    assert {"market_home_probability", "bookmaker_count"}.issubset(response.get_json()[0])


def test_sync_status_endpoint_works(client, monkeypatch):
    monkeypatch.setattr(
        sync_route.queries,
        "get_latest_sync_runs",
        lambda: [{"job_name": "odds_sync", "status": "success"}],
    )

    response = client.get("/api/sync/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["last_run"]["job_name"] == "odds_sync"
