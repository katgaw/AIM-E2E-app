"""Create the targets table and load the sample companies.

Render does not copy the database when it deploys this repo. Run this script
against an empty Postgres, including the database Render gives the app:

    python 17_E2E_Application/init_db.py

It reads DATABASE_URL from the environment, or from the repo-root .env when
that file exists. Running it again does not insert a second copy of a sample
company.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "app" / "backend"))

from STEP4_save_target import DatabaseError, connect

SCHEMA = HERE / "app" / "schema.sql"

# Same three companies the page shows when it is opened as a file.
SAMPLES = [
    (
        "Northwind Analytics",
        "Software",
        "Sells workflow software to mid-market manufacturers. "
        "Recurring revenue, about 40 people, founder still runs it.",
        "look further",
        "Recurring revenue and a narrow customer base are enough to look.",
        "northwind-teaser.pdf",
    ),
    (
        "Harbor Freight Logistics",
        "Transportation",
        "Regional trucking firm. A few large customers, and the fleet is aging.",
        "pass",
        "Customer concentration and an aging fleet are enough to pass on this PDF.",
        "harbor-one-pager.pdf",
    ),
    (
        "Lumen Glass",
        "Industrials",
        "A two-page note. It names the company and says it makes specialty glass. Little else.",
        "need more info",
        "The PDF does not say enough about customers or how the business makes money.",
        "lumen-note.pdf",
    ),
]


def main() -> None:
    if not SCHEMA.is_file():
        raise SystemExit(f"Schema file not found: {SCHEMA}")
    insert = """
        INSERT INTO targets (
            company_name, industry, summary, recommendation, reason, source_file
        )
        SELECT %s, %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM targets WHERE company_name = %s
        )
    """
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA.read_text())
                for company in SAMPLES:
                    cur.execute(insert, (*company, company[0]))
            conn.commit()
    except DatabaseError as exc:
        raise SystemExit(str(exc)) from exc
    print("Database initialized!")


if __name__ == "__main__":
    main()
