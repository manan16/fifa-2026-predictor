"""In-process background scheduler for automatic sync.

When ``ENABLE_AUTO_SYNC`` is true the Flask app starts a daemon thread that runs
a full sync shortly after boot and then repeats on ``SYNC_INTERVAL_MINUTES``.
This removes the need for a manual "Run sync" button or a separate worker
container for everyday use, while the worker profile remains available for
heavier deployments.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

logger = logging.getLogger(__name__)

# Module-level guard so the loop is only ever started once per process, even if
# the app factory is called multiple times (tests, debuggers, etc.).
_scheduler_started = False
_lock = threading.Lock()


def _run_once() -> None:
    # Imported lazily so importing this module never triggers a DB connection.
    from app.services.sync_service import run_full_sync

    try:
        result = run_full_sync()
        logger.info("Auto-sync completed with status=%s", result.get("status"))
    except Exception:  # pragma: no cover - defensive, must never kill the thread
        logger.exception("Auto-sync run failed")


def _loop(interval_seconds: float, initial_delay_seconds: float) -> None:
    stop = threading.Event()
    # Small initial delay so the first sync doesn't race app startup / migrations.
    if not stop.wait(initial_delay_seconds):
        _run_once()
    while not stop.wait(interval_seconds):
        _run_once()


def start_scheduler(app: "Flask") -> None:
    """Start the background sync loop if auto-sync is enabled.

    Safe to call more than once; only the first call has an effect. The thread
    is a daemon so it never blocks process shutdown.
    """
    global _scheduler_started

    if not app.config.get("ENABLE_AUTO_SYNC"):
        return

    # Avoid double-starting under the Werkzeug auto-reloader, which runs the
    # app in two processes during development.
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return

    with _lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    interval_minutes = max(1, int(app.config.get("SYNC_INTERVAL_MINUTES", 15)))
    interval_seconds = interval_minutes * 60.0

    thread = threading.Thread(
        target=_loop,
        kwargs={"interval_seconds": interval_seconds, "initial_delay_seconds": 5.0},
        name="auto-sync-scheduler",
        daemon=True,
    )
    thread.start()
    logger.info("Auto-sync scheduler started (every %s minute(s))", interval_minutes)
