import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://fifa_user:fifa_password@localhost:5432/fifa_predictor",
    )
    ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
    ODDS_API_BASE_URL = os.getenv("ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4")
    ODDS_API_SPORT_KEY = os.getenv("ODDS_API_SPORT_KEY", "soccer_fifa_world_cup")
    ODDS_API_REGIONS = os.getenv("ODDS_API_REGIONS", "uk,eu,us")
    ODDS_API_MARKETS = os.getenv("ODDS_API_MARKETS", "h2h")
    RESULTS_API_KEY = os.getenv("RESULTS_API_KEY", "")
    RESULTS_API_BASE_URL = os.getenv("RESULTS_API_BASE_URL", "")
    # Auto-sync is on by default now that the app runs the loop in-process.
    ENABLE_AUTO_SYNC = os.getenv("ENABLE_AUTO_SYNC", "true").lower() == "true"
    # Wikipedia match-stats sync runs as a third step of the full sync.
    ENABLE_STATS_SYNC = os.getenv("ENABLE_STATS_SYNC", "true").lower() == "true"
    SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES", "15"))
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True
    # Keep the background scheduler out of the test process.
    ENABLE_AUTO_SYNC = False
    # Don't reach out to Wikipedia from the test process.
    ENABLE_STATS_SYNC = False
