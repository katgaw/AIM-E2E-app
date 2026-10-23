"""Ask the model for a short first look at one company PDF.

Run from the repo root:

    uv run python 17_E2E_Application/app/backend/STEP3_evaluate_target.py path/to/company.pdf

The model and the key come from the repo-root .env, through helpers.llm_call.
This file does not name a provider.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

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


def _load_local_env() -> None:
    """Read a .env above this file when the laptop has one. Render has none."""
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        env_file = candidate / ".env"
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            return


def _course_structured(prompt: str, instructions: str):
    """Use helpers.llm_call when this file is running inside the course repo."""
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "helpers").is_dir():
            root = str(candidate)
            if root not in sys.path:
                sys.path.insert(0, root)
            break
    else:
        return None
    from helpers.llm_call import structured

    return structured(prompt, TargetEvaluation, instructions=instructions)


def _litellm_structured(prompt: str, instructions: str):
    """Call the model from LLM_MODEL when helpers/ is not in this deploy."""
    import litellm

    model = os.environ.get("LLM_MODEL", "").strip()
    if not model:
        raise RuntimeError(
            "LLM_MODEL is missing. On Render, set it as an environment variable."
        )
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ],
        response_format=TargetEvaluation,
    )
    content = response.choices[0].message.content or ""
    return TargetEvaluation.model_validate_json(content)


def evaluate(text: str) -> dict:
    """Return company_name, industry, summary, recommendation, and reason."""
    _load_local_env()
    excerpt = text[:MAX_CHARS]
    prompt = f"Company document:\n\n{excerpt}"
    result = _course_structured(prompt, INSTRUCTIONS)
    if result is None:
        result = _litellm_structured(prompt, INSTRUCTIONS)
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
