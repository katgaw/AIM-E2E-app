// Draws the target list and sends one PDF to the backend.
// Opened from the server, it loads real rows from GET /targets.
// Opened as a file, it shows two sample cards so the layout can be checked.

const form = document.querySelector("#upload");
const fileInput = document.querySelector("#pdf");
const button = document.querySelector("#evaluate");
const error = document.querySelector("#error");
const list = document.querySelector("#targets");
const filename = document.querySelector("#filename");
const count = document.querySelector("#count");

const LABELS = {
  "look further": ["Look further", "look"],
  pass: ["Pass", "pass"],
  "need more info": ["Need more info", "more"],
};

const SAMPLES = [
  {
    company_name: "Northwind Analytics",
    industry: "Software",
    created_at: "2026-10-22T12:00:00",
    recommendation: "look further",
    summary:
      "Sells workflow software to mid-market manufacturers. Recurring revenue, about 40 people, founder still runs it.",
    reason: "Recurring revenue and a narrow customer base are enough to look.",
    source_file: "northwind-teaser.pdf",
  },
  {
    company_name: "Harbor Freight Logistics",
    industry: "Transportation",
    created_at: "2026-10-21T12:00:00",
    recommendation: "pass",
    summary: "Regional trucking firm. A few large customers, and the fleet is aging.",
    reason: "Customer concentration and an aging fleet are enough to pass on this PDF.",
    source_file: "harbor-one-pager.pdf",
  },
  {
    company_name: "Lumen Glass",
    industry: "Industrials",
    created_at: "2026-10-20T12:00:00",
    recommendation: "need more info",
    summary: "A two-page note. It names the company and says it makes specialty glass. Little else.",
    reason: "The PDF does not say enough about customers or how the business makes money.",
    source_file: "lumen-note.pdf",
  },
];

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function card(row) {
  const known = LABELS[row.recommendation] || LABELS["need more info"];
  const article = document.createElement("article");
  article.className = "card " + known[1];

  const top = document.createElement("div");
  top.className = "card-top";

  const heading = document.createElement("div");
  const name = document.createElement("h3");
  name.className = "name";
  name.textContent = row.company_name || "Unknown";
  const meta = document.createElement("p");
  meta.className = "meta";
  meta.textContent = [row.industry, formatDate(row.created_at)].filter(Boolean).join("  ·  ");
  heading.append(name, meta);

  const tag = document.createElement("span");
  tag.className = "tag " + known[1];
  tag.textContent = known[0];
  top.append(heading, tag);

  const summary = document.createElement("p");
  summary.className = "summary";
  summary.textContent = row.summary || "";

  const why = document.createElement("p");
  why.className = "why";
  const whyLabel = document.createElement("strong");
  whyLabel.textContent = "Why";
  why.append(whyLabel, document.createTextNode(row.reason || ""));

  const foot = document.createElement("div");
  foot.className = "card-foot";
  const file = document.createElement("span");
  file.className = "file";
  file.textContent = row.source_file || "";
  foot.append(file);

  article.append(top, summary, why, foot);
  return article;
}

function render(rows) {
  list.replaceChildren();
  count.textContent = rows.length ? rows.length + (rows.length === 1 ? " company" : " companies") : "";
  if (!rows.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    const title = document.createElement("p");
    title.className = "empty-title";
    title.textContent = "No targets yet";
    const copy = document.createElement("p");
    copy.textContent = "Upload a PDF to add the first one.";
    empty.append(title, copy);
    list.append(empty);
    return;
  }
  for (const row of rows) list.append(card(row));
}

function showChosenFile() {
  const file = fileInput.files[0];
  filename.textContent = file ? file.name : "Choose a company PDF";
  form.classList.toggle("has-file", Boolean(file));
}

function messageFrom(body) {
  if (body && typeof body.detail === "string") return body.detail;
  return "The evaluation failed. Check the model and the database, then try again.";
}

async function load() {
  if (location.protocol === "file:") {
    render(SAMPLES);
    return;
  }
  try {
    const response = await fetch("/targets");
    const body = await response.json();
    if (!response.ok) {
      error.textContent = messageFrom(body);
      render([]);
      return;
    }
    render(body);
  } catch {
    error.textContent = "Could not reach the database. Start STEP0 and the server, then refresh.";
    render([]);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";

  const file = fileInput.files[0];
  if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
    error.textContent = "Upload a PDF.";
    return;
  }
  if (location.protocol === "file:") {
    error.textContent = "Open this page from the server at http://localhost:8000.";
    return;
  }

  button.disabled = true;
  fileInput.disabled = true;
  form.classList.add("busy");
  button.textContent = "Reading the PDF…";

  const payload = new FormData();
  payload.append("file", file);

  try {
    const response = await fetch("/targets", { method: "POST", body: payload });
    const body = await response.json();
    if (!response.ok) {
      error.textContent = messageFrom(body);
      return;
    }
    const previous = [...list.querySelectorAll(".card")];
    render([body]);
    for (const node of previous) list.append(node);
    fileInput.value = "";
    showChosenFile();
  } catch {
    error.textContent = "The evaluation failed. Check the model and the database, then try again.";
  } finally {
    button.disabled = false;
    fileInput.disabled = false;
    form.classList.remove("busy");
    button.textContent = "Evaluate";
  }
});

fileInput.addEventListener("change", () => {
  error.textContent = "";
  showChosenFile();
});

load();
