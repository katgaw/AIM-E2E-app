# STEP2_read_pdf

File: `app/backend/STEP2_read_pdf.py`

Turn an uploaded PDF into plain text. Use `pypdf`, which is already in this repo.

The script should:

1. Take a path to a PDF as its argument.
2. Read every page and join the text into one string.
3. Print that text.
4. If the file is missing, is not a PDF, or has no text, stop with a clear message and do not print an empty success.

Expose the reading as a function the later scripts can call, something like `read_pdf(path) -> str`. [STEP3_evaluate_target](STEP3_evaluate_target.md) and [STEP5_run_backend](STEP5_run_backend.md) will call it.

Running the file directly is the check:

```bash
uv run python 17_E2E_Application/app/backend/STEP2_read_pdf.py path/to/company.pdf
```

Done when: a real PDF prints its text, and a bad file prints an error instead of blank output.
