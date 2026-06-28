from app.routes import fixtures as fixtures_route
from app.routes import predictions as predictions_route
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

