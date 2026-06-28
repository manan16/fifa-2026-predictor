from flask import Blueprint, jsonify

from app.db import queries
from app.services.sync_service import run_full_sync

sync_bp = Blueprint("sync", __name__)


@sync_bp.get("/sync/status")
def get_sync_status():
    runs = queries.get_latest_sync_runs()
    return jsonify(
        {
            "latest_runs": runs,
            "last_run": runs[0] if runs else None,
        }
    )


@sync_bp.post("/sync/run")
def run_sync():
    # TODO: Require admin authentication before exposing this outside local/dev deployments.
    return jsonify(run_full_sync())
