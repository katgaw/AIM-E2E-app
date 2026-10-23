# Acquisition targets

## 🏗️ Build | 🚢 Ship | 📤 Share

### 🏗️ Build
- A PostgreSQL database, running locally in Docker, with one table of potential acquisition targets
- One page where the deal team uploads a company PDF
- One model call that writes a short first look: look further, pass, or need more info
- A small backend that reads the PDF, asks the model, and saves the note

### 🚢 Ship
Upload a teaser, a one-pager, or a few pages from a CIM. The company appears on the list with a recommendation. Refresh the page. The company is still there, because the note is in the database.

### 📤 Share
Walk the deal team through one PDF: the company name, the recommendation, the one-line reason, and the row in Postgres that holds it.

---

## What this is

A first-look screen for inbound company documents. The deal team drops in a PDF. The app reads it, asks the model for a short view, and stores the company as a potential acquisition target.

```text
deal team uploads a PDF
  -> backend reads the text
  -> model writes a short first look
  -> Postgres stores the target
  -> the page shows the company at the top of the list
```

The recommendation is one of three:

| Recommendation | Meaning |
| --- | --- |
| Look further | Worth a deeper read |
| Pass | Not a fit on what this PDF says |
| Need more info | The PDF does not say enough to judge |

The page only talks to the backend. The backend is the only piece that opens Postgres, and the only piece that calls the model. The model is whatever the repo-root `.env` already points at.

How the pieces fit together is in [architecture/architecture.md](architecture/architecture.md).

> **Why this matters to the deal team:** teasers arrive faster than anyone can read them. A written first look, stored next to the filename, is something the team can come back to after the browser is closed.

---

## Prerequisites

- Python 3.12
- Docker, running
- A repo-root `.env` with `LLM_MODEL` and the key for that model
- A virtual environment with this app's packages (`requirements.txt` below), or the shared environment from the repo root (`uv sync`)

`OPENAI_BASE_URL` is optional. Leave it blank when using OpenAI directly; set it only for a local or self-hosted OpenAI-compatible server.

---

## Setup

Docker Desktop has to be open first. This command does not start Docker. From `17_E2E_Application`:

```bash
# Start database in Docker
docker compose up -d
```

That command is the Docker step. It creates a container named `pe-targets-db` from the `postgres:16` image and publishes it on `localhost:5433` (database `targets`, user `pe`, password `pe`). Port 5432 is left free because another Postgres on this machine already uses it. The first time the container starts, Postgres runs `app/schema.sql` and creates the `targets` table. The command returns as soon as the container is up; give Postgres a few seconds before the page connects. Running it again starts the same container and keeps the rows already saved. That password is for this laptop only.

The backend reads `DATABASE_URL` from the repo-root `.env` and uses that to open Postgres. For this Docker database, set:

```bash
DATABASE_URL=postgresql://pe:pe@localhost:5433/targets
```

Then make a virtual environment for this app. A virtual environment is a folder that holds one project's packages, so they stay separate from other projects on the machine. From `17_E2E_Application`:

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

`uv venv .venv --python 3.12` creates that folder, names it `.venv`, and puts Python 3.12 inside it. `source .venv/bin/activate` points this terminal at it, so `python` means the one inside `.venv`. `uv pip install -r requirements.txt` reads `requirements.txt` and installs each package listed there into that folder. On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of `source`.

`python3.12 -m venv .venv` is the same idea, but it only works when that Python includes the `venv` module. A pyenv build sometimes does not. The message `No module named venv` means this one does not, so use the `uv venv` command above.

The prompt usually gains a `(.venv)` prefix while the environment is active. Leave that terminal open and start the page with it still active:

```bash
python app/backend/STEP5_run_backend.py
```

Open `http://localhost:8000`.

The same packages are already in the repo-wide environment. From the repo root, `uv sync` installs them, and `uv run python 17_E2E_Application/app/backend/STEP5_run_backend.py` starts the page without activating `.venv`.

---

## The loop

| Step | What happens |
| --- | --- |
| **0. Database** | Start Postgres in Docker and create the `targets` table |
| **1. Page** | Show the upload form and the list of saved targets |
| **2. Read** | Turn the PDF into plain text |
| **3. Evaluate** | One model call returns the company name, industry, summary, recommendation, and reason |
| **4. Save** | Insert that note and list what is already stored |
| **5. Serve** | Connect the page to steps 2, 3, and 4 |

The task for each step is in [individual_tasks](individual_tasks).

---

## Files

| File | What it does |
| --- | --- |
| `requirements.txt` | The Python packages for this app, installed into a virtual environment |
| `docker-compose.yml` | Starts Postgres in Docker |
| `app/schema.sql` | The one table, `targets`. Applied the first time the container starts |
| `app/backend/STEP0_create_postgres_database.py` | The same database start, written as a Python script |
| `app/frontend/STEP1_build_frontend.html` | The page |
| `app/frontend/app.js` | Uploads a PDF and draws the cards |
| `app/backend/STEP2_read_pdf.py` | PDF to plain text |
| `app/backend/STEP3_evaluate_target.py` | One model call |
| `app/backend/STEP4_save_target.py` | Insert a target and list them |
| `init_db.py` | Creates the `targets` table and loads the sample companies. Safe to run again |
| `app/backend/STEP5_run_backend.py` | The server. Port 8000 locally, or `$PORT` on Render |
| `sample/northwind-teaser.pdf` | A fictional one-page teaser to upload in the demo |
| `architecture/architecture.md` | How the page, backend, model, and database connect |
| `individual_tasks/` | The build, one task per file |

---

## Deploy on Render

GitHub does not copy the database. Render starts with an empty Postgres. `init_db.py` creates the `targets` table and inserts three sample companies. A second run leaves those rows as they are.

This app is the FastAPI server in `app/backend/STEP5_run_backend.py`, not Streamlit. In the Render web service, leave **Root Directory** blank so the repo root is included. The model call imports `helpers/` from that root.

| Setting | Value |
| --- | --- |
| Build Command | `pip install -r 17_E2E_Application/requirements.txt` |
| Start Command | `python 17_E2E_Application/init_db.py && python 17_E2E_Application/app/backend/STEP5_run_backend.py` |
| `DATABASE_URL` | The internal Postgres URL from the Render database |
| `PYTHON_VERSION` | `3.12.10` |
| `LLM_MODEL` | The same model name as in the repo-root `.env` |
| API key | The key for that model, such as `OPENAI_API_KEY` |

Render sets `PORT` itself. The server listens on `0.0.0.0` and that port. Locally, where `PORT` is unset, it still listens on port 8000.

To load the sample companies into the laptop database, from the repo root:

```bash
python 17_E2E_Application/init_db.py
```

---

## Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `Docker is not running` | Open Docker Desktop, then run `docker compose up -d` again from `17_E2E_Application` |
| `port is already allocated` | Something else is using port 5433. Stop that Postgres, then run `docker compose up -d` again |
| The page says it could not reach the database | The container is not running, or Postgres is still starting. From `17_E2E_Application`, run `docker compose up -d` and wait a few seconds |
| `Upload a PDF.` | The file is missing or is not a `.pdf` |
| The PDF had no readable text | The file is a scan with no text layer. The app does not invent a company |
| The evaluation failed | The model endpoint is unreachable or `.env` is incomplete. From the repo root, run `uv run python -m helpers.llm_call` |
