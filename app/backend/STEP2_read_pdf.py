"""Turn a company PDF into plain text.

Run from the repo root:

    uv run python 17_E2E_Application/app/backend/STEP2_read_pdf.py path/to/company.pdf

Later scripts call read_pdf() instead of running this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader


class PdfReadError(Exception):
    """The file cannot be used as a company PDF. The message is safe to show on the page."""


def read_pdf(path: Path | str) -> str:
    """Read every page and return one string. Raise PdfReadError when there is nothing to judge."""
    pdf = Path(path)
    if not pdf.is_file():
        raise PdfReadError(f"File not found: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise PdfReadError("Upload a PDF.")

    reader = PdfReader(str(pdf))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n\n".join(pages).strip()
    if not text:
        raise PdfReadError("This PDF had no readable text.")
    return text


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: STEP2_read_pdf.py path/to/company.pdf")
    try:
        print(read_pdf(sys.argv[1]))
    except PdfReadError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
