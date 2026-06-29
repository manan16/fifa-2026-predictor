from app.db import queries
from app.services import stats_service

SAMPLE_FOOTBALL_BOX = """
{{Football box
|team1=Brazil
|team2=DR Congo
|score=2–1
|goals1={{goal|12}}{{goal|34}} {{yel|45}}
|goals2={{goal|78}} {{sent off|81}}
|stadium=MetLife Stadium
}}
"""


def test_extract_and_parse_football_box_goals_and_cards():
    boxes = stats_service.extract_football_boxes(SAMPLE_FOOTBALL_BOX)
    assert len(boxes) == 1

    parsed = stats_service.parse_football_box(boxes[0])
    assert parsed is not None
    assert parsed["team1"] == "Brazil"
    assert parsed["team2"] == "Congo DR"
    # Score 2–1 splits onto the two sides.
    assert parsed["team1_goals_for"] == 2
    assert parsed["team1_goals_against"] == 1
    assert parsed["team2_goals_for"] == 1
    assert parsed["team2_goals_against"] == 2
    # Cards: one yellow for team1, one red (sent off) for team2.
    assert parsed["team1_yellow_cards"] == 1
    assert parsed["team1_red_cards"] == 0
    assert parsed["team2_yellow_cards"] == 0
    assert parsed["team2_red_cards"] == 1


def test_absent_metrics_left_null():
    boxes = stats_service.extract_football_boxes(SAMPLE_FOOTBALL_BOX)
    parsed = stats_service.parse_football_box(boxes[0])
    fixture = {
        "id": 7,
        "home_team_id": 1,
        "away_team_id": 2,
        "home_team_name": "Brazil",
        "away_team_name": "Congo DR",
    }
    home_stats, away_stats = stats_service.build_team_stats(parsed, fixture)
    # Goals/cards are carried…
    assert home_stats["goals_for"] == 2
    assert away_stats["red_cards"] == 1
    # …but metrics Wikipedia doesn't supply stay NULL, never fabricated.
    for absent in ("shots", "shots_on_target", "corners", "corners_conceded", "possession", "xg"):
        assert home_stats[absent] is None
        assert away_stats[absent] is None


def test_team_name_normalizer_resolves_tricky_names():
    assert stats_service.normalize_team_name("DR Congo") == "Congo DR"
    assert stats_service.normalize_team_name("Democratic Republic of the Congo") == "Congo DR"
    assert stats_service.normalize_team_name("United States") == "USA"
    assert stats_service.normalize_team_name("Bosnia and Herzegovina") == "Bosnia-Herz"
    assert stats_service.normalize_team_name("Côte d'Ivoire") == "Ivory Coast"
    # Ordinary names pass through untouched.
    assert stats_service.normalize_team_name("Brazil") == "Brazil"


def test_upsert_team_match_stats_is_idempotent(monkeypatch):
    store: list[dict] = []

    class FakeCursor:
        def execute(self, sql, params=None):
            params = params or ()
            if sql.strip().upper().startswith("DELETE"):
                fixture_id = params[0]
                store[:] = [row for row in store if row["fixture_id"] != fixture_id]
            elif "INSERT" in sql.upper():
                store.append(dict(zip(stats_service._STATS_COLUMNS, params)))

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            return None

    monkeypatch.setattr(stats_service, "get_connection", lambda: FakeConnection())

    home = {"team_id": 1, "goals_for": 2, "goals_against": 1, "yellow_cards": 1, "red_cards": 0, **stats_service._ABSENT_METRICS}
    away = {"team_id": 2, "goals_for": 1, "goals_against": 2, "yellow_cards": 0, "red_cards": 1, **stats_service._ABSENT_METRICS}

    stats_service.upsert_team_match_stats(7, home, away)
    stats_service.upsert_team_match_stats(7, home, away)

    # Running twice still leaves exactly one pair of rows for the fixture.
    assert len([row for row in store if row["fixture_id"] == 7]) == 2


def test_match_stats_endpoint_returns_shape(client, monkeypatch):
    monkeypatch.setattr(queries, "get_fixture_by_id", lambda _id: {"id": 5})
    monkeypatch.setattr(
        queries,
        "get_fixture_match_stats",
        lambda _id: {
            "home": {"team_name": "Brazil", "goals_for": 2, "possession": None},
            "away": {"team_name": "Congo DR", "goals_for": 1, "possession": None},
        },
    )

    response = client.get("/api/fixtures/5/match-stats")
    assert response.status_code == 200
    body = response.get_json()
    assert body["home"]["team_name"] == "Brazil"
    assert body["away"]["goals_for"] == 1
    assert "CC BY-SA" in body["source_note"]


def test_match_stats_endpoint_null_when_none(client, monkeypatch):
    monkeypatch.setattr(queries, "get_fixture_by_id", lambda _id: {"id": 5})
    monkeypatch.setattr(queries, "get_fixture_match_stats", lambda _id: {"home": None, "away": None})

    response = client.get("/api/fixtures/5/match-stats")
    assert response.status_code == 200
    body = response.get_json()
    assert body["home"] is None
    assert body["away"] is None


def test_match_stats_endpoint_404_for_missing_fixture(client, monkeypatch):
    monkeypatch.setattr(queries, "get_fixture_by_id", lambda _id: None)

    response = client.get("/api/fixtures/999/match-stats")
    assert response.status_code == 404
