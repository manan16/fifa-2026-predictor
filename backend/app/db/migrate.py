from pathlib import Path

from app.db.connection import get_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def ensure_schema_migrations_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
    conn.commit()


def get_applied_migrations(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT filename FROM schema_migrations;")
        return {row["filename"] for row in cur.fetchall()}


def run_migrations() -> None:
    conn = get_connection()
    try:
        ensure_schema_migrations_table(conn)
        applied = get_applied_migrations(conn)
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            if migration_file.name in applied:
                print(f"Skipping {migration_file.name}")
                continue

            print(f"Applying {migration_file.name}")
            with conn.cursor() as cur:
                cur.execute(migration_file.read_text())
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s);",
                    (migration_file.name,),
                )
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    run_migrations()

