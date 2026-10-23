-- One row is one company PDF the deal team has screened.
-- recommendation is one of: look further, pass, need more info.

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
