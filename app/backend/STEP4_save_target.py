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


def _repo_root() -> Path:
    """The directory that contains both pyproject.toml and helpers/."""
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "helpers").is_dir():
            return candidate
    raise DatabaseError("Could not find the repo root, so .env could not be loaded.")


def database_url() -> str:
    """The Postgres URL from the repo-root .env. Nothing else is used to connect."""
    env_file = _repo_root() / ".env"
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=True)
    except ModuleNotFoundError:
        pass
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseError(
            "DATABASE_URL is missing. Add it to the repo-root .env and try again."
        )
    return url


def connect() -> psycopg.Connection:
    """Open one connection. The caller closes it by using the connection as a context."""
    try:
        return psycopg.connect(database_url(), row_factory=dict_row)
    except psycopg.OperationalError as exc:
        raise DatabaseError(
            "Could not reach the database. Check DATABASE_URL in the repo-root .env "
            "and that Postgres is running."
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
