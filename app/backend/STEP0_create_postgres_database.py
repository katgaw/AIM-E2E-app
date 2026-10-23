"""Start PostgreSQL in Docker and create the targets table.

Run from the repo root:

    uv run python 17_E2E_Application/app/backend/STEP0_create_postgres_database.py

The table itself is app/schema.sql. This script only starts the database and
applies that file. Running it again does not wipe rows already saved.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

CONTAINER = "pe-targets-db"
SCHEMA = Path(__file__).resolve().parents[1] / "schema.sql"


def docker(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run one docker command. Return the result so the caller can read it."""
    try:
        return subprocess.run(
            ["docker", *args],
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        raise SystemExit("Docker is not installed or not on PATH.") from None


def require_docker() -> None:
    """Stop early when the Docker daemon is not running."""
    info = docker("info")
    if info.returncode != 0:
        raise SystemExit("Docker is not running. Open Docker, then run this script again.")


def container_exists() -> bool:
    """True when a container with our exact name is already on this machine."""
    listed = docker("ps", "-a", "--format", "{{.Names}}")
    if listed.returncode != 0:
        raise SystemExit(listed.stderr.strip() or "Could not list Docker containers.")
    names = {line.strip() for line in listed.stdout.splitlines()}
    return CONTAINER in names


def start_database() -> None:
    """Start the existing container, or create it the first time."""
    if container_exists():
        started = docker("start", CONTAINER)
        if started.returncode != 0:
            raise SystemExit(started.stderr.strip() or f"Could not start {CONTAINER}.")
        print(f"Started existing container {CONTAINER}.")
        return

    created = docker(
        "run",
        "-d",
        "--name",
        CONTAINER,
        "-e",
        "POSTGRES_USER=pe",
        "-e",
        "POSTGRES_PASSWORD=pe",
        "-e",
        "POSTGRES_DB=targets",
        "-p",
        "5433:5432",
        "postgres:16",
    )
    if created.returncode != 0:
        raise SystemExit(created.stderr.strip() or "Could not start Postgres.")
    print(f"Created container {CONTAINER}.")


def wait_until_ready() -> None:
    """Give Postgres a moment to accept connections after the container starts."""
    for _ in range(60):
        ready = docker("exec", CONTAINER, "pg_isready", "-U", "pe", "-d", "targets")
        if ready.returncode == 0:
            return
        time.sleep(1)
    raise SystemExit("Postgres did not become ready. Check `docker logs pe-targets-db`.")


def apply_schema() -> None:
    """Run schema.sql inside the database. CREATE TABLE IF NOT EXISTS keeps old rows."""
    if not SCHEMA.is_file():
        raise SystemExit(f"Schema file not found: {SCHEMA}")
    applied = docker(
        "exec",
        "-i",
        CONTAINER,
        "psql",
        "-U",
        "pe",
        "-d",
        "targets",
        "-v",
        "ON_ERROR_STOP=1",
        input_text=SCHEMA.read_text(),
    )
    if applied.returncode != 0:
        raise SystemExit(applied.stderr.strip() or "Could not create the targets table.")


def main() -> None:
    require_docker()
    start_database()
    wait_until_ready()
    apply_schema()
    print("Postgres is running. The targets table is ready.")
    print("Check it with:")
    print('  docker exec -it pe-targets-db psql -U pe -d targets -c "SELECT * FROM targets;"')


if __name__ == "__main__":
    main()
