# UDX Spend Analytics — V9 Streamlit Dashboard

A multi-tab, bilingual (EN/JP) procurement analytics dashboard built with Streamlit.
Grounded in $1,164.7M of UDX spend data and 107 WAVE initiatives.

---

## Option A — Deploy to Streamlit Community Cloud (shared URL for your team)

This gives your team a permanent URL like `https://yi-liu.streamlit.app` that anyone
can open in a browser — no Python or installation required on their end.

### Step 1 — Push code to GitHub (one-time, ~5 min)

1. Go to [github.com](https://github.com) and create a **new private repository**
   (e.g. `udx-spend-analytics`)
2. Upload the contents of this `v9_streamlit/` folder as the **root** of the repo
   — so `app.py` is at the top level, not inside a subfolder
3. Make sure `.env` is **not** uploaded (it is listed in `.gitignore`)

> **Tip:** Use GitHub Desktop or drag-and-drop upload on github.com to avoid CLI.

### Step 2 — Deploy on Streamlit Cloud (one-time, ~2 min)

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account
2. Click **New app**
3. Select your repository and set:
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Advanced settings → Secrets** and paste:
   ```toml
   OPENAI_API_KEY = "eyJhbGci..."
   ```
   *(replace with your current McKinsey JWT token — see `.streamlit/secrets.toml.example`)*
5. Click **Deploy** — the app goes live in about 2 minutes
6. Copy the URL and share it with your team

### Step 3 — Refresh the token when it expires (~daily)

The McKinsey JWT token expires every ~24 hours. To refresh:

1. Get a new token (log in to the McKinsey AI Gateway portal)
2. Go to your Streamlit Cloud app → **⋮ menu → Settings → Secrets**
3. Replace the `OPENAI_API_KEY` value with the new token
4. Click **Save** — the app reloads in seconds, no redeployment needed

> All 9 analytics tabs (charts, tables, WAVE data) work without a token.
> Only the AI chatbot (Idea Generation + Business Case Builder) needs the token.

---

## Option B — Run locally

### 1. Install Python dependencies

```bash
cd v9_streamlit
pip install -r requirements.txt
```

### 2. Set your API key

Copy `.env.example` to `.env` and paste your McKinsey JWT token:

```
OPENAI_API_KEY=eyJhbGci...
```

### 3. Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### 4. Share over your local network (optional)

```bash
streamlit run app.py --server.address 0.0.0.0
```

Team members on the same Wi-Fi can access it at `http://<your-IP>:8501`.

---

## Tab Overview

| Tab | Description |
|-----|-------------|
| Spend Pulse | Monthly trend, category stacked area, heatmap, YoY table |
| Category Intelligence | Category Pareto, heatmap, WAVE coverage gap analysis |
| Supplier Intelligence | Vendor Pareto (top 30), dependency risk flags, detail table |
| Procurement Behavior | Spend w/o Justification bars, demand consolidation, data quality |
| Savings Opportunity Map | Category × lever matrix, filterable WAVE initiative table |
| Idea Generation | AI chatbot grounded in all embedded spend and WAVE data |
| Business Case Builder | Section A–D form, AI auto-populate, Excel export |
| Data Requirements | Outstanding data requests by category and priority |
| Assumptions & README | Methodology, limitations, data scope notes |

---

## File Structure

```
v9_streamlit/
├── app.py                   # Entry point — sidebar, language toggle, routing
├── requirements.txt         # Python dependencies
├── .env                     # Your JWT token (gitignored — never commit)
├── .env.example             # Template for local use
├── .gitignore               # Excludes .env and secrets from git
├── .streamlit/
│   ├── config.toml          # Dark theme, port settings
│   └── secrets.toml.example # Template for Streamlit Cloud secrets
├── data/
│   ├── spend_data.py        # MONTHS, MONTHLY_TOTAL, HEATMAP, YOY
│   ├── vendor_data.py       # PARETO, MAVERICK, BUNDLING, DQ
│   ├── cat_data.py          # Category Pareto, gap analysis, savings matrix
│   └── wave_data.py         # All WAVE initiatives (107 records)
├── pages/
│   ├── spend_pulse.py
│   ├── cat_intel.py
│   ├── supplier_intel.py
│   ├── proc_behavior.py
│   ├── savings_map.py
│   ├── idea_gen.py
│   ├── biz_case.py
│   ├── data_req.py
│   └── assumptions.py
└── utils/
    ├── translations.py      # EN/JP string dictionary
    ├── ai_client.py         # OpenAI wrapper — reads st.secrets or .env
    └── excel_export.py      # openpyxl L2 Business Case export
```

---

## Confidentiality

**DRAFT — Internal use only.**
Do not share the GitHub repo URL or Streamlit app URL externally without
Procurement leadership approval. The repo should remain **private**.
