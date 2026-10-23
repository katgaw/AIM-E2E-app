"""Save one screened company, and list the companies already saved.

Run from the repo root, after STEP0:

    uv run python 17_E2E_Application/app/backend/STEP4_save_target.py

That inserts one sample row so the database can be checked before the model is involved.
The backend calls save_target() and list_targets() instead.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


class DatabaseError(Exception):
    """Postgres could not be reached or the write failed. The message is safe to show."""


def _load_local_env() -> None:
    """Fill in variables from a .env file when one exists.

    Render sets DATABASE_URL in the environment and has no .env file. A missing
    file is normal there. Locally, the file is the repo-root .env, and it only
    fills variables the environment does not already have.
    """
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        env_file = candidate / ".env"
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            return


def database_url() -> str:
    """The Postgres URL. The environment wins, then a local .env file."""
    _load_local_env()
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseError(
            "DATABASE_URL is missing. On Render, set it as an environment variable. "
            "Locally, put it in the repo-root .env."
        )
    return url


def connect() -> psycopg.Connection:
    """Open one connection. The caller closes it by using the connection as a context."""
    try:
        return psycopg.connect(database_url(), row_factory=dict_row)
    except psycopg.OperationalError as exc:
        raise DatabaseError(
            "Could not reach the database. Check DATABASE_URL and that Postgres is running."
        ) from exc


def _as_text(row: dict) -> dict:
    """Turn the timestamp into text so print() and the page can both show it."""
    ready = dict(row)
    created = ready.get("created_at")
    if isinstance(created, datetime):
        ready["created_at"] = created.isoformat()
    return ready


def save_target(
    *,
    company_name: str,
    industry: str,
    summary: str,
    recommendation: str,
    reason: str,
    source_file: str,
) -> dict:
    """Insert one row and return it, including the new id and created_at."""
    sql = """
        INSERT INTO targets (
            company_name, industry, summary, recommendation, reason, source_file
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, company_name, industry, summary, recommendation,
                  reason, source_file, created_at
    """
    values = (company_name, industry, summary, recommendation, reason, source_file)
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                row = cur.fetchone()
            conn.commit()
    except DatabaseError:
        raise
    except psycopg.Error as exc:
        raise DatabaseError("Could not save the target.") from exc
    return _as_text(row)


def list_targets() -> list[dict]:
    """Every saved target, newest first."""
    sql = """
        SELECT id, company_name, industry, summary, recommendation,
               reason, source_file, created_at
        FROM targets
        ORDER BY created_at DESC, id DESC
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
    except DatabaseError:
        raise
    except psycopg.Error as exc:
        raise DatabaseError("Could not read the targets.") from exc
    return [_as_text(row) for row in rows]


def main() -> None:
    """Insert a made-up company, then print the whole table."""
    try:
        save_target(
            company_name="Northwind Analytics",
            industry="Software",
            summary=(
                "Sells workflow software to mid-market manufacturers. "
                "Recurring revenue, about 40 people, founder still runs it."
            ),
            recommendation="look further",
            reason="Recurring revenue and a narrow customer base are enough to look.",
            source_file="northwind-teaser.pdf",
        )
        for row in list_targets():
            print(
                f"{row['id']:>3}  {row['company_name']}  "
                f"[{row['recommendation']}]  {row['source_file']}"
            )
    except DatabaseError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
