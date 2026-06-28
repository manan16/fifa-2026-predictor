from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.fixtures import fixtures_bp
from app.routes.health import health_bp
from app.routes.predictions import predictions_bp
from app.routes.teams import teams_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(teams_bp, url_prefix="/api/teams")
    app.register_blueprint(fixtures_bp, url_prefix="/api/fixtures")
    app.register_blueprint(predictions_bp, url_prefix="/api")

    return app

