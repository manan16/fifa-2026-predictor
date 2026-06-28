import os
import time

from app.services.sync_service import run_full_sync


def main() -> None:
    interval = max(1, int(os.getenv("SYNC_INTERVAL_MINUTES", "15"))) * 60
    while True:
        try:
            print(run_full_sync())
        except Exception as exc:
            print(f"Sync loop error: {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
