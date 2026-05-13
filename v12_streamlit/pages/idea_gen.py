"""
Tab 6 — Idea Generation (AI Chatbot)

V12 fixes vs V9:
  B1 — Removed crossing col_input/col_clear layout; Clear button above chips
  B3 — Fixed message duplication bug; better token expiry banner
  B4 — Added grounded-in badge, session status line, turn counter
"""
import os
import streamlit as st
from dotenv import load_dotenv
from utils.translations import t
from utils.ai_client import build_system_prompt, chat_completion

load_dotenv()

_STARTER_CHIPS_EN = [
    "What categories have no WAVE initiative?",
    "Suggest 3 new savings ideas for Construction spend ($42M)",
    "Which initiatives are below 50% of their business case?",
    "What is the highest-risk supplier concentration?",
    "Compare F&B WAVE initiatives vs Merchandise WAVE initiatives",
    "How can we reduce Spend w/o Justification in Clothing/Uniforms?",
    "What is the FA Equipment Rental spend and what should we do?",
    "How can we improve payment terms to boost working capital?",
]
_STARTER_CHIPS_JP = [
    "WAVEイニシアティブのないカテゴリは？",
    "建設支出（$42M）の新しい節約アイデアを3つ提案して",
    "ビジネスケースの50%未満のイニシアティブは？",
    "最も高リスクのサプライヤー集中度は？",
    "F&B vs Merchandiseのイニシアティブを比較して",
    "Clothing/Uniformsの正当理由なし支出を減らすには？",
    "FA設備レンタル支出（$87M）について何をすべきか？",
    "支払条件を改善して運転資本を改善するには？",
]


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

    # ── B4: Grounded-in badge ─────────────────────────────────────────────────
    st.markdown(
        '<div class="v12-badge">'
        '🔗 Grounded in 107 WAVE initiatives &nbsp;·&nbsp; $1,164.7M spend &nbsp;·&nbsp; Top 30 vendors'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── B3: API key check with expiry detection ───────────────────────────────
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
            if lang == "en" else
            "**APIキーが見つかりません。** McKinsey JWTトークンが必要です。\n\n"
            "Streamlit Cloud → 設定 → シークレット で `OPENAI_API_KEY` を追加してください。"
        )
    elif key_expired:
        st.warning(
            "**JWT token has expired.** The AI chatbot will not respond until you refresh the token.\n\n"
            "**To fix:**\n"
            "1. Get a new McKinsey JWT token\n"
            "2. Go to Streamlit Cloud → **⋮ → Settings → Secrets**\n"
            "3. Replace `OPENAI_API_KEY` value → **Save**"
            if lang == "en" else
            "**JWTトークンが期限切れです。** 新しいトークンを取得し、Streamlit CloudのSecretsを更新してください。"
        )

    # ── B1: Clear button ABOVE chips — no column layout competing with chat_input
    if st.session_state.chat_history:
        if st.button(
            t("idea_clear", lang),
            key="v12_clear_btn",
            help="Start a new conversation",
        ):
            st.session_state.chat_history = []
            st.rerun()

    # ── Starter chips ─────────────────────────────────────────────────────────
    chips = _STARTER_CHIPS_EN if lang == "en" else _STARTER_CHIPS_JP
    if not st.session_state.chat_history:
        st.markdown("**" + ("Starter questions:" if lang == "en" else "よくある質問:") + "**")
        chip_cols = st.columns(4)
        for i, chip in enumerate(chips):
            if chip_cols[i % 4].button(chip, key=f"v12_chip_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": chip})
                st.rerun()

    # ── Chat history display ──────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── B4: Session status line ───────────────────────────────────────────────
    turn_count = len([m for m in st.session_state.chat_history if m["role"] == "user"])
    if turn_count > 0:
        status_label = (
            f"gpt-5-nano-2025-08-07 · Turn {turn_count} · Demo grounded in 107 WAVE initiatives"
            if key_valid and not key_expired
            else f"Turn {turn_count} · AI offline — refresh token to enable"
        )
        st.caption(status_label)

    # ── B1: chat_input is the only input element — no competing column layout ─
    prompt = st.chat_input(t("idea_ph", lang))
    if prompt:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        if not key_valid or key_expired:
            error_msg = (
                "Cannot reach AI — token missing or expired. See banner above for fix instructions."
                if lang == "en" else
                "AI接続不可 — トークンがないか期限切れです。上のバナーをご確認ください。"
            )
            with st.chat_message("assistant"):
                st.error(error_msg)
            # B3: Append user then error — no duplication
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        else:
            # B3: Build messages from existing history BEFORE appending new user msg
            # This fixes the V9 duplication bug where user msg appeared twice
            messages = [{"role": "system", "content": build_system_prompt()}]
            messages += st.session_state.chat_history
            messages.append({"role": "user", "content": prompt})

            # Now append to history (after building messages)
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
