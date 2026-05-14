"""Tab 5 — Savings Opportunity Map."""
import pandas as pd
import streamlit as st
from utils.translations import t
from data.cat_data import SAV_MATRIX
from data.wave_data import WAVE_DATA


def render(lang: str = "en"):
    st.title(f"💰 {t('tab_savings', lang)}")

    # Compute aggregate KPIs from WAVE data
    l4 = [w for w in WAVE_DATA if w["stage"] == "L4" and w["status"] == "On track"]
    l3 = [w for w in WAVE_DATA if w["stage"] == "L3" and w["status"] == "On track"]
    l4_latest = sum(w["latest"] for w in l4)
    l3_bp     = sum(w["bp"] for w in l3)
    total_bp  = l4_latest + l3_bp

    # KPI order matches HTML: Total WAVE BP | L3 Planned | No Coverage | Below 50% of BP
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Total WAVE BP (Annualized)" if lang == "en" else "WAVE BP 合計（年換算）",
        f"${total_bp:.1f}M",
        help=f"L4 ${l4_latest:.1f}M executed ({len(l4)}) · L3 ${l3_bp:.1f}M planned ({len(l3)})"
    )
    k2.metric(
        t("l3_planned", lang),
        f"${l3_bp:.1f}M",
        help=f"{len(l3)} initiatives in pipeline"
    )
    k3.metric(
        "Spend — No WAVE Coverage" if lang == "en" else "WAVEカバレッジなし支出",
        "$107.3M",
        help="Construction + MRO + Ride Repair" if lang == "en" else "建設＋MRO＋ライド修繕"
    )
    k4.metric(
        "Initiatives Below 50% of BP" if lang == "en" else "BP50%未満のイニシアティブ",
        "12",
    )
    st.divider()

    # ── Savings Matrix ────────────────────────────────────────────────────────
    st.subheader(t("sav_mx_hdr", lang))

    lever_keys = ["lever_comp", "lever_demand", "lever_spec", "lever_contract", "lever_process"]
    levers = [t(k, lang) for k in lever_keys]

    COLOR = {"wave": "#1e7e34", "partial": "#7d4700", "gap": "#7b1f1f"}
    LABEL = {
        "wave":    {"en": "✅ Covered", "jp": "✅ 対応済"},
        "partial": {"en": "🟡 Partial",  "jp": "🟡 部分対応"},
        "gap":     {"en": "🔴 Gap",      "jp": "🔴 ギャップ"},
    }
    label_key = "en" if lang == "en" else "jp"
    note_key  = "en" if lang == "en" else "jp"

    for row in SAV_MATRIX["rows"]:
        st.markdown(f"**{row['cat']}**")
        cols = st.columns(len(levers))
        for ci, (lever, cell) in enumerate(zip(levers, row["cells"])):
            lbl = LABEL[cell["t"]][label_key]
            note = cell[f"en"] if lang == "en" else cell.get("jp", cell["en"])
            with cols[ci]:
                cell_color = COLOR[cell["t"]]
                st.markdown(
                    f"<div style='background:{cell_color};padding:8px;border-radius:6px;"
                    f"font-size:11px;min-height:64px'>"
                    f"<b>{lever}</b><br>{lbl}<br><span style='opacity:.8'>{note}</span></div>",
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()

    # ── WAVE Initiatives table ────────────────────────────────────────────────
    st.subheader(t("wave_hdr", lang))

    # Filters
    all_ws     = sorted({w["ws"] for w in WAVE_DATA})
    all_stages = sorted({w["stage"] for w in WAVE_DATA})

    col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
    search     = col_f1.text_input(t("search", lang), "")
    sel_ws     = col_f2.selectbox(t("filter_ws", lang), [t("all", lang)] + all_ws)
    sel_stage  = col_f3.selectbox(t("filter_stage", lang), [t("all", lang)] + all_stages)

    filtered = WAVE_DATA
    if search:
        search_low = search.lower()
        filtered = [w for w in filtered
                    if search_low in w["name"].lower() or search_low in str(w["id"])]
    if sel_ws != t("all", lang):
        filtered = [w for w in filtered if w["ws"] == sel_ws]
    if sel_stage != t("all", lang):
        filtered = [w for w in filtered if w["stage"] == sel_stage]

    # Sort by latest desc then bp desc
    filtered = sorted(filtered, key=lambda w: (-w["latest"], -w["bp"]))

    df = pd.DataFrame([
        {
            "ID": w["id"],
            t("col_name", lang): w["name"],
            t("col_ws", lang): w["ws"],
            t("col_stage", lang): w["stage"],
            t("col_bp", lang): w["bp"],
            t("col_lat", lang): w["latest"],
            "Status": (
                t("status_on_track", lang) if w["status"] == "On track" else
                t("status_cancelled", lang) if w["status"] == "Cancelled" else
                t("status_on_hold", lang)
            ),
            t("col_owner", lang): w["owner"],
        }
        for w in filtered
    ])

    if not df.empty:
        st.dataframe(
            df.style.background_gradient(
                subset=[t("col_bp", lang), t("col_lat", lang)],
                cmap="Greens",
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"{len(filtered)} initiative(s) shown")
    else:
        st.info("No initiatives match the current filter.")
