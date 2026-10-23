# STEP0_create_postgres_database

File: `app/backend/STEP0_create_postgres_database.py`

The table is defined in `app/schema.sql`. The script starts Postgres and applies that file.

Start PostgreSQL in Docker and create the one table we need.

Use these settings. Later scripts connect with the same values. They are for a laptop demo.

| Setting | Value |
| --- | --- |
| Container name | `pe-targets-db` |
| Image | `postgres:16` |
| Host | `localhost` |
| Port | `5433` on the laptop, `5432` inside the container |
| Database | `targets` |
| User | `pe` |
| Password | `pe` |

The script should:

1. Start a container named `pe-targets-db` from `postgres:16`, with the settings above, published on port `5433`.
2. If that container already exists, start it instead of creating a second one.
3. Wait until Postgres is accepting connections.
4. Create the `targets` table if it is not there yet.

```sql
CREATE TABLE IF NOT EXISTS targets (
    id              SERIAL PRIMARY KEY,
    company_name    TEXT NOT NULL,
    industry        TEXT,
    summary         TEXT,
    recommendation  TEXT,
    reason          TEXT,
    source_file     TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

`recommendation` will only ever be one of `look further`, `pass`, or `need more info`.

One row is one uploaded PDF. We keep the note, not the PDF file. The filename is enough to know where the note came from.

Done when: the container is running, and `SELECT * FROM targets;` returns an empty table with those columns.
