# STEP4_save_target

File: `app/backend/STEP4_save_target.py`

Write one evaluation into `targets`, and read the table back. [STEP0_create_postgres_database](STEP0_create_postgres_database.md) has to be running first.

Connect with `DATABASE_URL` from the repo-root `.env`. For the local Docker database that value is `postgresql://pe:pe@localhost:5433/targets`.

Two functions the backend will call:

- `save_target(...)` inserts one row and returns it, including the new `id` and `created_at`.
- `list_targets()` returns every row, newest first.

Also let us run the file on its own with a made-up company, so we can check the database before the model is involved:

```bash
uv run python 17_E2E_Application/app/backend/STEP4_save_target.py
```

That run inserts one sample row (`Northwind Analytics`, recommendation `look further`) and prints every row.

Done when: the sample row shows up in `targets`, and running the script again adds another row rather than wiping the table.
