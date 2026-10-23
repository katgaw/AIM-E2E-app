# STEP3_evaluate_target

File: `app/backend/STEP3_evaluate_target.py`

One model call. Send it the PDF text from [STEP2_read_pdf](STEP2_read_pdf.md). Get back the fields we store.

The model comes from the repo-root `.env`, through `helpers.llm_call`. Do not hardcode a provider or an API key.

Ask for exactly this:

| Field | What we want |
| --- | --- |
| `company_name` | The company the PDF is about. `Unknown` if it is not named. |
| `industry` | A short industry label. Empty if the PDF does not say. |
| `summary` | Two or three sentences on what the business is. Use only what the PDF says. |
| `recommendation` | `look further`, `pass`, or `need more info` |
| `reason` | One or two sentences. Why that recommendation, from the PDF. |

Rules for the prompt, kept short:

- Use only the PDF. Do not fill gaps with outside knowledge.
- If the text is too thin to judge, recommendation is `need more info`.
- Do not invent revenue, headcount, or a valuation.

Call the model with `helpers.llm_call.structured` and a small Pydantic model, so we get those fields back as data rather than a paragraph we have to parse. Load the repo the same way the notebooks do, so `.env` is picked up.

Running it:

```bash
uv run python 17_E2E_Application/app/backend/STEP3_evaluate_target.py path/to/company.pdf
```

It should use STEP2 to read the file, then print the five fields.

Done when: a real teaser PDF prints a company name, a summary that matches the PDF, and one of the three recommendations.
