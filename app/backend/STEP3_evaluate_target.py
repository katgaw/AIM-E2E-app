"""Ask the model for a short first look at one company PDF.

Run from the repo root:

    uv run python 17_E2E_Application/app/backend/STEP3_evaluate_target.py path/to/company.pdf

The model and the key come from the repo-root .env, through helpers.llm_call.
This file does not name a provider.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

# The repo root has to be importable before helpers can load.
_here = Path(__file__).resolve()
for _candidate in (_here, *_here.parents):
    if (_candidate / "pyproject.toml").exists() and (_candidate / "helpers").is_dir():
        _root = str(_candidate)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        break
else:
    raise SystemExit("Could not find the repo root (pyproject.toml and helpers/).")

from pydantic import BaseModel

from helpers.llm_call import structured

from STEP2_read_pdf import PdfReadError, read_pdf

# A long CIM is more than we need for a first look. The model sees the opening.
MAX_CHARS = 12_000

INSTRUCTIONS = """
You screen a company document for a private equity first look.
Use only the text you are given. Do not add facts from outside the document.
If the company is not named, set company_name to "Unknown".
If the industry is not stated, set industry to an empty string.
summary is two or three sentences on what the business is.
recommendation is exactly one of: look further, pass, need more info.
If the text is too thin to judge, recommendation is need more info.
reason is one or two sentences, drawn from the text, saying why.
Do not invent revenue, headcount, or a valuation.
""".strip()


class TargetEvaluation(BaseModel):
    """The five fields the targets table stores, besides the filename and the time."""

    company_name: str
    industry: str
    summary: str
    recommendation: Literal["look further", "pass", "need more info"]
    reason: str


def evaluate(text: str) -> dict:
    """Return company_name, industry, summary, recommendation, and reason."""
    excerpt = text[:MAX_CHARS]
    result = structured(
        f"Company document:\n\n{excerpt}",
        TargetEvaluation,
        instructions=INSTRUCTIONS,
    )
    return result.model_dump()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: STEP3_evaluate_target.py path/to/company.pdf")
    try:
        note = evaluate(read_pdf(sys.argv[1]))
    except PdfReadError as exc:
        raise SystemExit(str(exc)) from exc
    for key, value in note.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
