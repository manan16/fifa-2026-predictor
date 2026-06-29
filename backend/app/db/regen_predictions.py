from app.db.seed import seed_database


def regenerate_predictions() -> None:
    """Refresh seeded fixture predictions without creating duplicates.

    The seed step already deletes and recreates generated prediction/stat rows for
    seeded fixtures, so this provides a clear command name for model refreshes.
    """
    seed_database()


if __name__ == "__main__":
    regenerate_predictions()
    print("Regenerated seeded fixture predictions")
