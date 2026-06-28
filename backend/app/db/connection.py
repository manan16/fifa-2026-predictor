from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from flask import current_app, g, has_app_context
from psycopg.rows import dict_row


def get_connection() -> psycopg.Connection:
    if has_app_context():
        if "db" not in g:
            g.db = psycopg.connect(current_app.config["DATABASE_URL"], row_factory=dict_row)
        return g.db

    from app.config import Config

    return psycopg.connect(Config.DATABASE_URL, row_factory=dict_row)


@contextmanager
def get_dict_cursor() -> Iterator[psycopg.Cursor]:
    conn = get_connection()
    with conn.cursor(row_factory=dict_row) as cur:
        yield cur


def close_connection(error: Exception | None = None) -> None:
    db = g.pop("db", None) if has_app_context() else None
    if db is not None:
        db.close()

