from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.bracket import bracket_bp
from app.routes.fixtures import fixtures_bp
from app.routes.health import health_bp
from app.routes.odds import odds_bp
from app.routes.predictions import predictions_bp
from app.routes.sync import sync_bp
from app.routes.teams import teams_bp
from app.services.scheduler import start_scheduler


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(teams_bp, url_prefix="/api/teams")
    app.register_blueprint(fixtures_bp, url_prefix="/api/fixtures")
    app.register_blueprint(predictions_bp, url_prefix="/api")
    app.register_blueprint(bracket_bp, url_prefix="/api")
    app.register_blueprint(odds_bp, url_prefix="/api")
    app.register_blueprint(sync_bp, url_prefix="/api")

    # Kick off the in-process automatic sync loop when enabled. No-op under
    # TestConfig (auto-sync defaults to false) and safe to call repeatedly.
    start_scheduler(app)

    return app