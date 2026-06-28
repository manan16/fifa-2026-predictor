from contextlib import contextmanager

from app.services import odds_service
from app.services.odds_service import decimal_to_implied_probability, remove_overround
from app.services.results_service import determine_knockout_winner


def test_decimal_odds_to_implied_probability():
    assert decimal_to_implied_probability(2.0) == 0.5
    assert decimal_to_implied_probability(4.0) == 0.25


def test_remove_overround_sums_to_one():
    normalized = remove_overround({"home": 0.55, "draw": 0.28, "away": 0.25})
    assert round(sum(value for value in normalized.values() if value is not None), 6) == 1


def test_completed_fixture_can_show_actual_winner():
    fixture = {
        "home_team_id": 10,
        "away_team_id": 20,
        "actual_home_score": 1,
        "actual_away_score": 1,
        "home_penalties": 5,
        "away_penalties": 4,
    }
    assert determine_knockout_winner(fixture) == 10


def test_demo_odds_seeding_creates_bookmaker_odds(monkeypatch):
    fixtures = [
        {
            "id": 1,
            "home_team_name": "Brazil",
            "away_team_name": "Japan",
            "home_team_elo": 2130,
            "away_team_elo": 1875,
        }
    ]
    saved_payloads = []

    class FakeCursor:
        def execute(self, *_args, **_kwargs):
            return None

        def fetchall(self):
            return fixtures

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            return None

    @contextmanager
    def fake_dict_cursor():
        yield FakeCursor()

    def fake_save_fixture_odds(_fixture_id, payload):
        saved_payloads.append(payload)
        return sum(len(bookmaker["outcomes"]) for bookmaker in payload)

    monkeypatch.setattr(odds_service, "get_dict_cursor", fake_dict_cursor)
    monkeypatch.setattr(odds_service, "get_connection", lambda: FakeConnection())
    monkeypatch.setattr(odds_service, "save_fixture_odds", fake_save_fixture_odds)
    monkeypatch.setattr(odds_service, "calculate_market_consensus", lambda _fixture_id: None)

    records = odds_service.seed_demo_odds()

    assert records == 24
    assert len(saved_payloads[0]) == 8
    assert saved_payloads[0][0]["source"] == "demo"
