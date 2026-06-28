from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "fifa-2026-predictor-api"})

