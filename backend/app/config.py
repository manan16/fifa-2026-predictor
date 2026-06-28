import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://fifa_user:fifa_password@localhost:5432/fifa_predictor",
    )
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True

