# STEP1_build_frontend

Files: `app/frontend/STEP1_build_frontend.html` and `app/frontend/app.js`

This one is the page, not a Python script. Build it as a single HTML file. The backend will serve it later. For this task, opening the file in a browser is enough to check the layout. The buttons get wired to the real server in [STEP5_run_backend](STEP5_run_backend.md).

## How the page should look

One column, centered, comfortable to read on a laptop. White background, dark text, one dark button. Plenty of space. It should look like a quiet internal tool.

```text
Acquisition targets
Upload a company PDF. We save it and write a short first look.

Company PDF
[ Choose file ]                    [ Evaluate ]

Saved targets

┌─────────────────────────────────────────────┐
│ Northwind Analytics                         │
│ Software  ·  22 Oct 2026          Look further
│                                             │
│ Sells workflow software to mid-market       │
│ manufacturers. Recurring revenue, about     │
│ 40 people, founder still runs it.           │
│                                             │
│ Why   Recurring revenue and a narrow        │
│       customer base are enough to look.     │
│ northwind-teaser.pdf                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Harbor Freight Logistics                    │
│ Transportation  ·  21 Oct 2026        Pass  │
│ ...                                         │
└─────────────────────────────────────────────┘
```

**Top.** Title: `Acquisition targets`. Under it, one line: `Upload a company PDF. We save it and write a short first look.`

**Upload.** A file field labeled `Company PDF` that accepts `.pdf` only. Next to it, one button labeled `Evaluate`. Nothing else in this block. No second button, no text box for notes.

**List.** A heading, `Saved targets`. Then one card per company, newest first. On a card:

- Company name, the largest text on the card
- Industry and the date, smaller, on one line
- The recommendation, on the right of that line, as a small label
- The summary, two or three sentences
- The reason, with the word `Why` in front of it
- The PDF filename, smallest text, at the bottom

The three labels should be easy to tell apart at a glance:

| Recommendation | Label color |
| --- | --- |
| Look further | green |
| Pass | muted red |
| Need more info | amber |

**Empty list.** Before any upload, the list area says: `No targets yet. Upload a PDF to add the first one.`

**While a PDF is being read.** The button label changes to `Reading the PDF…` and the form cannot be clicked again until the answer comes back.

**When something is wrong.** One line of red text under the button. Two cases we already know:

- The file is not a PDF: `Upload a PDF.`
- The server or the model failed: show the short message the server sends back.

Done when: the page matches this layout with sample cards filled in by hand, including the empty state, and the three recommendation labels are visually distinct.
