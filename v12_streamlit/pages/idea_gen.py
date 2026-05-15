"""
Tab 6 — Idea Generation (AI Chatbot)

V12 fixes vs V9:
  B1 — Removed crossing col_input/col_clear layout; Clear button above chips
  B3 — Fixed message duplication bug; better token expiry banner
  B4 — Added grounded-in badge, session status line, turn counter

V12.1 upgrades:
  U1 — Grouped chips (4 categories, 2-col grid, coloured header labels)
  U2 — pending_prompt flag so chip clicks fire the full AI pipeline
  U3 — Contextual follow-up chips below the last AI reply (keyword-matched)
  U4 — "Save to Business Case" button on every AI reply
"""
import re
import os
import streamlit as st
from dotenv import load_dotenv
from utils.translations import t
from utils.ai_client import build_system_prompt, chat_completion

load_dotenv()

# ── U1: Grouped starter chips ─────────────────────────────────────────────────
_CHIP_GROUPS_EN = [
    {
        "label": "Spend Analysis",
        "accent": "#1565C0",
        "chips": [
            "Explain the spend pulse trend and the November 2025 spike",
            "Where is maverick or uncontrolled spend most concentrated? What should we do?",
            "What is the FA Equipment Rental spend and what should we do about it?",
        ],
    },
    {
        "label": "New Ideas",
        "accent": "#2E7D32",
        "chips": [
            "What are the top F&B savings opportunities not yet in WAVE?",
            "What new WAVE initiatives should we add that are not in the current pipeline?",
            "What quick-win initiatives could we execute in the next 90 days?",
        ],
    },
    {
        "label": "Vendor Strategy",
        "accent": "#E65100",
        "chips": [
            "Which vendors have the most consolidation potential based on the spend data?",
            "How can we improve payment terms to boost working capital?",
        ],
    },
    {
        "label": "Build a Case",
        "accent": "#6A1B9A",
        "chips": [
            "Which categories have the highest savings rates in the current WAVE pipeline?",
            "How do I build an L2 business case for a new initiative?",
        ],
    },
]

_CHIP_GROUPS_JP = [
    {
        "label": "支出分析",
        "accent": "#1565C0",
        "chips": [
            "支出トレンドと2025年11月のスパイクを説明して",
            "正当理由なし支出が最も集中しているのはどこか？何をすべきか？",
            "FA設備レンタル支出（$87M）について何をすべきか？",
        ],
    },
    {
        "label": "新しいアイデア",
        "accent": "#2E7D32",
        "chips": [
            "WAVEにまだ含まれていないF&B節約機会は？",
            "現在のパイプラインにない新しいWAVEイニシアティブは？",
            "今後90日以内に実行できるクイックウィンは？",
        ],
    },
    {
        "label": "ベンダー戦略",
        "accent": "#E65100",
        "chips": [
            "支出データから最も統合可能性が高いベンダーは？",
            "支払条件を改善して運転資本を改善するには？",
        ],
    },
    {
        "label": "ケース構築",
        "accent": "#6A1B9A",
        "chips": [
            "現在のWAVEパイプラインで最も節約率が高いカテゴリは？",
            "新しいイニシアティブのL2ビジネスケースをどう構築するか？",
        ],
    },
]

# ── U3: Follow-up keyword rules ───────────────────────────────────────────────
_FOLLOWUP_RULES = [
    (
        r"F&B|food|beverage|dry food|non.alcohol|avendra",
        [
            "Which F&B vendors can we consolidate?",
            "What is the Dry Foods RFP status?",
            "How much can Avendra leverage save?",
        ],
    ),
    (
        r"construction|M\.E\.|retro.PO|mechanical|HVAC",
        [
            "Who are the top Construction vendors?",
            "What is the retro-PO rate for Construction?",
            "Suggest an RFP approach for ME Construction",
        ],
    ),
    (
        r"vendor|supplier|consolidat|single.sourc",
        [
            "Which vendors have dual-source risk?",
            "What is the spend concentration for the top 5 vendors?",
            "Which categories are single-sourced?",
        ],
    ),
    (
        r"WAVE|initiative|pipeline|business plan|BP",
        [
            "Which WAVE initiatives are below 50% of BP?",
            "What categories have no WAVE coverage?",
            "Which Sprint-stage initiatives close fastest?",
        ],
    ),
    (
        r"payment|DPO|working capital|term",
        [
            "Which vendors offer the best DPO extension potential?",
            "What is our current average DPO?",
            "How does improving DPO affect cash flow?",
        ],
    ),
    (
        r"equipment|rental|FA |facility",
        [
            "What vendors cover FA Equipment Rental?",
            "Is FA Equipment Rental in the WAVE pipeline?",
            "What are the top spend months for equipment rental?",
        ],
    ),
    (
        r"business case|L2|L3|BCG model",
        [
            "What inputs does an L2 business case need?",
            "Show me a worked example for a beverage initiative",
            "What is the approval process for a new WAVE initiative?",
        ],
    ),
    (
        r"maverick|uncontrolled|rogue|off.contract",
        [
            "Which categories have the highest maverick spend?",
            "How can we redirect maverick spend to contract?",
            "What PO discipline metrics should we track?",
        ],
    ),
    (
        r"november|spike|anomaly|peak spend",
        [
            "What drove the November 2025 spend spike?",
            "Are there other seasonal anomalies to watch?",
            "How does November compare to prior year?",
        ],
    ),
]
_FOLLOWUP_DEFAULT = [
    "What category should we prioritize next?",
    "Which initiative has the best ROI in the pipeline?",
    "What data gaps are blocking progress?",
]


def _pick_followups(text: str) -> list:
    """Return 3 follow-up chip texts based on keyword matching in the AI reply."""
    for pattern, suggestions in _FOLLOWUP_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return suggestions[:3]
    return _FOLLOWUP_DEFAULT


def _extract_bc_prefill(text: str) -> dict:
    """Extract initiative name and a dollar figure from an AI reply for BC pre-fill.

    Keys match what _bc_modal() in biz_case.py reads via prefill.get(…):
      initiative_name → PROPOSED NAME field
      baseline_value  → BASELINE VALUE ($) field (numeric, stripped of $ and M/K suffixes)
    """
    prefill = {}
    name_match = re.search(r"\*\*([^*]{5,70})\*\*", text)
    if name_match:
        prefill["initiative_name"] = name_match.group(1).strip()
    dollar_match = re.search(r"\$([\d,]+(?:\.\d+)?)([MK]?)", text)
    if dollar_match:
        raw = dollar_match.group(1).replace(",", "")
        suffix = dollar_match.group(2)
        try:
            value = float(raw)
            if suffix == "M":
                value *= 1_000_000
            elif suffix == "K":
                value *= 1_000
            prefill["baseline_value"] = value
        except ValueError:
            pass
    return prefill


def _get_api_key() -> str:
    """Read API key from st.secrets (Cloud) then env var (.env locally)."""
    key = ""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception:
        pass
    if not key:
        key = os.getenv("OPENAI_API_KEY", "").strip()
    return key


def _token_is_expired(api_key: str) -> bool:
    """Decode JWT exp claim and check if the token is already expired."""
    try:
        import base64, json, time
        parts = api_key.split(".")
        if len(parts) < 2:
            return False
        padding = 4 - len(parts[1]) % 4
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * padding))
        exp = payload.get("exp", 0)
        return exp < time.time()
    except Exception:
        return False


def render(lang: str = "en"):
    st.title(f"💡 {t('tab_idea', lang)}")
    st.caption(t("idea_sub", lang))

    # ── Grounded-in badge ─────────────────────────────────────────────────────
    st.markdown(
        '<div class="v12-badge">'
        "🔗 Grounded in 107 WAVE initiatives &nbsp;·&nbsp; $1,164.7M spend &nbsp;·&nbsp; Top 30 vendors"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── API key check with expiry detection ───────────────────────────────────
    api_key = _get_api_key()
    key_valid = bool(api_key) and api_key != "PASTE_YOUR_JWT_TOKEN_HERE"
    key_expired = key_valid and _token_is_expired(api_key)

    if not key_valid:
        st.error(
            "**No API key found.** The AI chatbot requires a McKinsey JWT token.\n\n"
            "**To fix:**\n"
            "1. Go to your Streamlit Cloud app → **⋮ → Settings → Secrets**\n"
            "2. Add: `OPENAI_API_KEY = \"eyJhbGci...\"`\n"
            "3. Click **Save** — app reloads automatically"
            if lang == "en"
            else "**APIキーが見つかりません。** McKinsey JWTトークンが必要です。\n\n"
            "Streamlit Cloud → 設定 → シークレット で `OPENAI_API_KEY` を追加してください。"
        )
    elif key_expired:
        st.warning(
            "**JWT token has expired.** The AI chatbot will not respond until you refresh the token.\n\n"
            "**To fix:**\n"
            "1. Get a new McKinsey JWT token\n"
            "2. Go to Streamlit Cloud → **⋮ → Settings → Secrets**\n"
            "3. Replace `OPENAI_API_KEY` value → **Save**"
            if lang == "en"
            else "**JWTトークンが期限切れです。** 新しいトークンを取得し、Streamlit CloudのSecretsを更新してください。"
        )

    # ── Clear button (only when history exists) ───────────────────────────────
    if st.session_state.chat_history:
        if st.button(
            t("idea_clear", lang),
            key="v12_clear_btn",
            help="Start a new conversation",
        ):
            st.session_state.chat_history = []
            st.session_state.pop("followup_chips", None)
            st.rerun()

    # ── U2: Consume pending_prompt BEFORE chat_input so chip clicks fire AI ───
    prompt = st.session_state.pop("pending_prompt", None)

    # ── U1: Grouped starter chips (hidden once conversation starts) ───────────
    chip_groups = _CHIP_GROUPS_EN if lang == "en" else _CHIP_GROUPS_JP
    if not st.session_state.chat_history and not prompt:
        label = "Starter questions:" if lang == "en" else "よくある質問:"
        st.markdown(f"**{label}**")
        col_left, col_right = st.columns(2)
        halves = [chip_groups[:2], chip_groups[2:]]
        for col, half in zip([col_left, col_right], halves):
            with col:
                for gi, group in enumerate(half):
                    st.markdown(
                        f'<p style="font-size:11px;font-weight:600;'
                        f'color:{group["accent"]};letter-spacing:0.06em;'
                        f'margin-bottom:2px;margin-top:12px;">'
                        f'{group["label"].upper()}</p>',
                        unsafe_allow_html=True,
                    )
                    for ci, chip in enumerate(group["chips"]):
                        chip_key = f"v12_chip_{'L' if col is col_left else 'R'}_{gi}_{ci}"
                        if st.button(chip, key=chip_key, use_container_width=True):
                            # U2: Set pending_prompt so AI pipeline fires on next rerun
                            st.session_state.pending_prompt = chip
                            st.rerun()

    # ── Chat history display ──────────────────────────────────────────────────
    last_ai_idx = max(
        (i for i, m in enumerate(st.session_state.chat_history) if m["role"] == "assistant"),
        default=None,
    )
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                # U4: "Save to Business Case" button on every AI reply
                bc_label = "📋 Save to Business Case" if lang == "en" else "📋 ビジネスケースに保存"
                if st.button(bc_label, key=f"v12_save_bc_{i}"):
                    st.session_state.bc_prefill = _extract_bc_prefill(msg["content"])
                    st.session_state.bc_open_modal = True
                    st.switch_page("pages/biz_case.py")

                # U3: Follow-up chips only beneath the LAST AI message
                if i == last_ai_idx:
                    followups = st.session_state.get("followup_chips", [])
                    if followups:
                        fu_label = "💬 Follow-up:" if lang == "en" else "💬 次の質問:"
                        st.caption(fu_label)
                        fu_cols = st.columns(len(followups))
                        for j, fu in enumerate(followups):
                            if fu_cols[j].button(fu, key=f"v12_fu_{j}", use_container_width=True):
                                st.session_state.pending_prompt = fu
                                st.session_state.pop("followup_chips", None)
                                st.rerun()

    # ── Session status line ───────────────────────────────────────────────────
    turn_count = len([m for m in st.session_state.chat_history if m["role"] == "user"])
    if turn_count > 0:
        status_label = (
            f"gpt-5-nano-2025-08-07 · Turn {turn_count} · Demo grounded in 107 WAVE initiatives"
            if key_valid and not key_expired
            else f"Turn {turn_count} · AI offline — refresh token to enable"
        )
        st.caption(status_label)

    # ── chat_input always rendered at the bottom ──────────────────────────────
    typed_prompt = st.chat_input(t("idea_ph", lang))
    if typed_prompt:
        prompt = typed_prompt

    # ── AI pipeline (fires for both chip clicks and typed messages) ───────────
    if prompt:
        # Clear stale follow-ups when a new prompt fires
        st.session_state.pop("followup_chips", None)

        with st.chat_message("user"):
            st.markdown(prompt)

        if not key_valid or key_expired:
            error_msg = (
                "Cannot reach AI — token missing or expired. See banner above for fix instructions."
                if lang == "en"
                else "AI接続不可 — トークンがないか期限切れです。上のバナーをご確認ください。"
            )
            with st.chat_message("assistant"):
                st.error(error_msg)
            # Append both so history stays in sync (B3 pattern)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        else:
            # B3: Build messages from existing history BEFORE appending new user msg
            messages = [{"role": "system", "content": build_system_prompt()}]
            messages += st.session_state.chat_history
            messages.append({"role": "user", "content": prompt})

            # Append user message to history after building messages list
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                try:
                    stream = chat_completion(messages, stream=True)
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                except ValueError as ve:
                    err = str(ve)
                    placeholder.error(err)
                    full_response = f"Error: {err}"
                except Exception as exc:
                    err = f"Unexpected error: {exc}"
                    placeholder.error(err)
                    full_response = err

            st.session_state.chat_history.append(
                {"role": "assistant", "content": full_response}
            )
            # U3: Generate follow-up chips from the fresh AI response
            st.session_state.followup_chips = _pick_followups(full_response)
            st.rerun()
