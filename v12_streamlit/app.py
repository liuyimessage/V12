"""
UDX Spend Analytics — V12 Streamlit Dashboard
Entry point: run with `streamlit run app.py`

V12 fixes vs V9:
  B1 — idea_gen layout: removed crossing col_input/col_clear pattern
  B2 — CSS: stripped fragile data-testid color overrides; theme from config.toml
  B3 — AI: fixed message duplication bug + better token expiry UX
  B4 — Logs: added grounded-in badge + session status line
"""
import streamlit as st

st.set_page_config(
    page_title="UDX Spend Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal CSS — layout only; all colors come from .streamlit/config.toml ───
# Using only stable selectors that don't depend on Streamlit internals.
st.markdown("""
<style>
/* Hide Streamlit chrome — stable selectors */
#MainMenu, footer { visibility: hidden; }

/* Hide auto-generated multi-page sidebar nav */
[data-testid="stSidebarNav"] { display: none !important; }

/* Main content padding */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 1400px;
}

/* Chat message cards — layout only, color from theme */
[data-testid="stChatMessage"] {
    border-radius: 10px !important;
    margin: 4px 0 !important;
}

/* Grounded badge — custom HTML element */
.v12-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(79,142,247,.08);
    border: 1px solid rgba(79,142,247,.25);
    border-radius: 8px;
    margin-bottom: 12px;
    font-size: 12px;
    color: #4f8ef7;
}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bc_cases" not in st.session_state:
    st.session_state.bc_cases = []

from utils.translations import t

lang = st.session_state.lang

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<h2 style='color:#4f8ef7;margin-bottom:0'>📊 UDX</h2>"
        f"<p style='color:#888;font-size:12px;margin-top:2px'>{t('app_subtitle', lang)}</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col_en, col_jp = st.columns(2)
    with col_en:
        if st.button("EN", use_container_width=True,
                     type="primary" if lang == "en" else "secondary"):
            st.session_state.lang = "en"
            st.rerun()
    with col_jp:
        if st.button("日本語", use_container_width=True,
                     type="primary" if lang == "jp" else "secondary"):
            st.session_state.lang = "jp"
            st.rerun()

    st.divider()

    page = st.radio(
        "Navigation",
        options=[
            "spend_pulse", "cat_intel", "supplier_intel", "proc_behavior",
            "savings_map", "idea_gen", "biz_case", "data_req", "assumptions",
        ],
        format_func=lambda x: {
            "spend_pulse":    f"📈 {t('tab_pulse', lang)}",
            "cat_intel":      f"🗂️ {t('tab_cat', lang)}",
            "supplier_intel": f"🏭 {t('tab_supplier', lang)}",
            "proc_behavior":  f"⚙️ {t('tab_behavior', lang)}",
            "savings_map":    f"💰 {t('tab_savings', lang)}",
            "idea_gen":       f"💡 {t('tab_idea', lang)}",
            "biz_case":       f"📋 {t('tab_bc', lang)}",
            "data_req":       f"📂 {t('tab_datareq', lang)}",
            "assumptions":    f"📝 {t('tab_assumptions', lang)}",
        }[x],
        label_visibility="collapsed",
        key="nav_page",
    )

    st.divider()
    st.caption("🔒 Draft for Review · Internal only")

# ── Page routing ──────────────────────────────────────────────────────────────
# nav_page is the keyed radio value; other pages can set it to navigate
page = st.session_state.get("nav_page", "spend_pulse")

if page == "spend_pulse":
    import pages.spend_pulse as pg
elif page == "cat_intel":
    import pages.cat_intel as pg
elif page == "supplier_intel":
    import pages.supplier_intel as pg
elif page == "proc_behavior":
    import pages.proc_behavior as pg
elif page == "savings_map":
    import pages.savings_map as pg
elif page == "idea_gen":
    import pages.idea_gen as pg
elif page == "biz_case":
    import pages.biz_case as pg
elif page == "data_req":
    import pages.data_req as pg
else:
    import pages.assumptions as pg

pg.render(lang)
