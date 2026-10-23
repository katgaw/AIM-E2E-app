"""Serve the page and connect it to the other scripts.

Run from the repo root, after STEP0, with .env filled in:

    uv run python 17_E2E_Application/app/backend/STEP5_run_backend.py

Then open http://localhost:8000.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from STEP2_read_pdf import PdfReadError, read_pdf
from STEP3_evaluate_target import evaluate
from STEP4_save_target import DatabaseError, list_targets, save_target

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
PAGE = FRONTEND / "STEP1_build_frontend.html"
SCRIPT = FRONTEND / "app.js"

app = FastAPI(title="Acquisition targets")


@app.get("/")
def home() -> FileResponse:
    """The deal team's page."""
    return FileResponse(PAGE)


@app.get("/app.js")
def frontend_script() -> FileResponse:
    """The script the page loads. The page asks for app.js, so it has to live at this path."""
    return FileResponse(SCRIPT, media_type="text/javascript")


@app.get("/targets")
def targets() -> list[dict]:
    """Every saved target, newest first."""
    try:
        return list_targets()
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/targets")
async def upload(file: UploadFile = File(...)) -> dict:
    """Read one PDF, ask the model, save the note, and return the new row."""
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Upload a PDF.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Upload a PDF.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    try:
        note = evaluate(read_pdf(tmp_path))
        return save_target(**note, source_file=filename)
    except PdfReadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The evaluation failed. Check the model and the database, then try again.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    # Render sets PORT and reaches the process from outside the machine.
    # Locally PORT is unset, so this stays on http://localhost:8000.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
