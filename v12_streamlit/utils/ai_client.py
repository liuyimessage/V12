"""OpenAI client wrapper for McKinsey AI Gateway."""
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # no-op on Streamlit Cloud (no .env file), works locally

OPENAI_BASE_URL = "https://openai.prod.ai-gateway.quantumblack.com/15656447-a087-481e-8c68-3563149046cd/v1"
MODEL = "gpt-5-nano-2025-08-07"


def _get_client() -> OpenAI | None:
    """Return an OpenAI client.

    Priority:
    1. st.secrets["OPENAI_API_KEY"]  — Streamlit Community Cloud
    2. OPENAI_API_KEY env var         — local .env file via load_dotenv()
    """
    api_key = ""

    # 1. Try Streamlit secrets (populated on Streamlit Cloud)
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception:
        pass  # st.secrets not available outside Streamlit runtime

    # 2. Fall back to environment variable / .env
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key or api_key == "PASTE_YOUR_JWT_TOKEN_HERE":
        return None
    return OpenAI(api_key=api_key, base_url=OPENAI_BASE_URL)


def build_system_prompt() -> str:
    """Construct a rich system prompt embedding all key dashboard data."""
    from data.wave_data import WAVE_DATA
    from data.cat_data import CAT_LABELS, CAT_SPEND, TOTAL_SPEND, TOTAL_POS
    from data.vendor_data import MAVERICK, BUNDLING

    l3 = [w for w in WAVE_DATA if w["stage"] == "L3" and w["status"] == "On track"]
    l4 = [w for w in WAVE_DATA if w["stage"] == "L4" and w["status"] == "On track"]
    l3_bp = sum(w["bp"] for w in l3)
    l4_latest = sum(w["latest"] for w in l4)

    wave_summary = "\n".join(
        f"  #{w['id']} [{w['stage']}] {w['name']} | WS: {w['ws']} | BP: ${w['bp']}M | Latest: ${w['latest']}M | Owner: {w['owner']}"
        for w in WAVE_DATA
        if w["stage"] in ("L3", "L4", "Su") and w["status"] != "Cancelled"
    )

    cat_summary = "\n".join(
        f"  {CAT_LABELS[i]}: ${CAT_SPEND[i]}M"
        for i in range(len(CAT_LABELS))
    )

    mav_summary = "\n".join(
        f"  {m['cat']}: ${m['hash_spend']}M of ${m['total_spend']}M ({m['hash_pct']}% w/o justification)"
        for m in MAVERICK
    )

    return f"""You are an expert procurement analytics AI assistant embedded in the UDX Spend Analytics dashboard.

== PORTFOLIO OVERVIEW ==
- Total spend analysed: ${TOTAL_SPEND}M across {TOTAL_POS:,} purchase orders (Jan 2024 – Apr 2026)
- L4 executed savings: ${l4_latest:.1f}M across {len(l4)} initiatives
- L3 planned savings (2026 pipeline): ${l3_bp:.1f}M across {len(l3)} initiatives
- Total WAVE initiatives in scope: {len(WAVE_DATA)}

== TOP SPEND CATEGORIES ==
{cat_summary}

== ACTIVE WAVE INITIATIVES (L3/L4/Sprint) ==
{wave_summary}

== SPEND WITHOUT JUSTIFICATION (MAVERICK) ==
{mav_summary}

== KEY UNCOVERED SPEND AREAS (NO WAVE INITIATIVE) ==
- FA Equipment Rental: $87.4M — captive lease, CapEx reclassification is the priority
- Construction: $42.0M — no WAVE coverage, competitive RFP opportunity
- Maintenance/Repair: $35.2M — 44.4% spend without justification
- Clothing/Uniforms: $22.8M — distinct from Merch Apparel, no WAVE initiative
- Ride Repair: $11.2M — no competitive sourcing event

== IMPORTANT DISTINCTIONS ==
- "Clothing/Uniforms" = wardrobe/employee uniforms — completely separate from "Merch Apparel" (COGS merchandise)
- "Spend w/o justification" = POs with '#' justification code, not necessarily fraudulent
- Merch Apparel is its own COGS category under Merchandise workstream

Your role: Answer questions about the UDX procurement landscape, suggest new savings initiatives, identify white spaces, and help users build business cases. Always ground your answers in the data above. Be specific with dollar amounts and initiative IDs. When data is unavailable, say so clearly and suggest how to obtain it."""


def chat_completion(messages: list[dict], stream: bool = False):
    """
    Call the McKinsey OpenAI Gateway.
    messages: list of {"role": "user"|"assistant"|"system", "content": str}
    Returns: generator (stream=True) or full response string (stream=False)
    """
    client = _get_client()
    if client is None:
        raise ValueError(
            "No API key found. "
            "On Streamlit Cloud: go to Settings → Secrets and add OPENAI_API_KEY = \"your-token\". "
            "Locally: add OPENAI_API_KEY=your-token to the .env file."
        )

    try:
        if stream:
            return client.chat.completions.create(
                model=MODEL,
                messages=messages,
                stream=True,
                timeout=60,
            )
        else:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                timeout=60,
            )
            return resp.choices[0].message.content
    except Exception as exc:
        err = str(exc)
        if "401" in err or "unauthorized" in err.lower():
            raise ValueError(
                "JWT token expired or invalid. "
                "On Streamlit Cloud: go to Settings → Secrets, update OPENAI_API_KEY, and Save. "
                "Locally: replace the token in .env and save the file."
            ) from exc
        raise
