# STEP5_run_backend

File: `app/backend/STEP5_run_backend.py`

The small server that connects the page to the other scripts. FastAPI is already in this repo.

It uses:

- [STEP1_build_frontend](STEP1_build_frontend.md) for the page
- [STEP2_read_pdf](STEP2_read_pdf.md) to get the text
- [STEP3_evaluate_target](STEP3_evaluate_target.md) for the model call
- [STEP4_save_target](STEP4_save_target.md) to write and list rows

[STEP0_create_postgres_database](STEP0_create_postgres_database.md) has to be running, and the repo-root `.env` has to be filled in. The model comes from that `.env` through `helpers.llm_call`.

On startup the server serves `STEP1_build_frontend.html`.

| Route | What it does |
| --- | --- |
| `GET /` | The page. |
| `GET /targets` | Every saved target, newest first, from STEP4. |
| `POST /targets` | Accepts one PDF upload. STEP2 reads it, STEP3 evaluates it, STEP4 saves it, and the route returns the new row. |

The page should load the list when it opens, and after a successful upload it should put the new card at the top without a full reload.

Failures the page already knows how to show:

- No file, or a file that is not a PDF: `Upload a PDF.`
- A PDF with no text: a short message that says the PDF had no readable text.
- The model or the database failed: a short message, not a stack trace.

Run it from the repo root:

```bash
uv run python 17_E2E_Application/app/backend/STEP5_run_backend.py
```

Open `http://localhost:8000`.

Done when: uploading a company PDF adds a card, and refreshing the page shows that same card still there.
