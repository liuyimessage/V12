"""
Tab 7 — Business Case Builder
V12: modal pop-up (st.dialog) matches HTML layout exactly.
  - Initiative Log table (top card)
  - Generated Business Cases archive (bottom card)
  - Pop-up form with 5 sections: Identity / Baseline / Forecast / Value Tracking / Dependencies
"""
from __future__ import annotations
from datetime import date
import streamlit as st
from utils.translations import t
from utils.excel_export import export_business_case
from data.wave_data import WAVE_DATA


# ── Demo pre-fill ──────────────────────────────────────────────────────────────
_DEMO_FIELDS = {
    "initiative_name":  "[SPRINT] - Dry Foods RFP (#63296)",
    "wave_id":          "63296",
    "owner":            "Annmarie Venne",
    "workstream":       "F&B",
    "sub_workstream":   "Food & Beverage",
    "baseline_value":   8728182,
    "cat_l3":           "Dry Foods",
    "vendor_contains":  "",
    "item_contains":    "",
    "saving_rate":      10.0,
    "recurring_benefit": 870000,
    "one_time_benefit": 0,
    "one_time_cost":    50000,
    "neg_impact":       0,
    "unit":             "$ / year, USD",
    "assumptions": (
        "Baseline: $8.73M annualized spend per Dry_input.xlsx upload.\n"
        "Saving rate: 10% — consistent with comparable F&B RFP events (Proteins Phase I: 10.1%).\n"
        "Implementation cost: $50K — legal, project management, and system setup.\n"
        "Source: WAVE ID #63296, owner Annmarie Venne; latest $0.87M realized."
    ),
    "execution_step": (
        "1. Issue RFP to 8 qualified dry goods distributors\n"
        "2. Evaluate bids and conduct negotiations (target -10% off baseline)\n"
        "3. Implement preferred supplier contract (Avendra leverage)\n"
        "4. Monitor compliance via Vroozi catalog"
    ),
    "pnl_allocation":   "UOR-Wide",
    "inc_avoidance":    "Cost reduction",
    "dep_it":           "Unknown",
    "dep_hr":           "No",
    "dep_cross":        "Unknown",
    "dep_capex":        "No",
    "category":         "Dry Foods",
    "stage":            "Su",
}

_SUB_WS_OPTIONS = [
    "— Select —",
    "Food & Beverage",
    "Merchandise (COGS)",
    "Facilities & MRO",
    "Technology",
    "Logistics & Distribution",
    "Marketing",
    "Professional Services",
    "Other",
]
_UNIT_OPTIONS = [
    "$ / year, USD",
    "$ / month, USD",
    "$ / unit, USD",
    "% of spend",
    "Other",
]
_INC_AVOIDANCE_OPTIONS = ["Cost avoidance", "Incremental", "Cost reduction"]
_DEP_OPTIONS = ["Yes", "No", "Unknown"]


def _find_wave(search: str) -> list[dict]:
    s = search.lower()
    return [w for w in WAVE_DATA
            if s in w["name"].lower() or s in str(w["id"]) or s in w["ws"].lower()]


def _auto_fill_from_wave(wave: dict) -> dict:
    return {
        "initiative_name":   wave["name"],
        "wave_id":           str(wave["id"]),
        "owner":             wave.get("owner", ""),
        "workstream":        wave["ws"],
        "sub_workstream":    "— Select —",
        "baseline_value":    0,
        "cat_l3":            "",
        "vendor_contains":   "",
        "item_contains":     "",
        "saving_rate":       10.0,
        "recurring_benefit": int(wave["latest"] * 1_000_000) if wave["latest"] else 0,
        "one_time_benefit":  0,
        "one_time_cost":     50000,
        "neg_impact":        0,
        "unit":              "$ / year, USD",
        "assumptions":       f"Recurring benefit sourced from WAVE latest value: ${wave['latest']:.2f}M.",
        "execution_step":    "",
        "pnl_allocation":    "",
        "inc_avoidance":     "Cost reduction",
        "dep_it":            "Unknown",
        "dep_hr":            "Unknown",
        "dep_cross":         "Unknown",
        "dep_capex":         "Unknown",
        "category":          wave["ws"],
        "stage":             wave["stage"],
    }


# ── Modal dialog (matches HTML bcg-modal exactly) ─────────────────────────────
@st.dialog("Build business case", width="large")
def _bc_modal(lang: str, prefill: dict):
    """5-section modal that matches the HTML overlay exactly."""

    subtitle = (
        "Building a new business case from scratch."
        if not prefill.get("wave_id")
        else f"Editing from WAVE initiative #{prefill.get('wave_id')}."
    )
    st.caption(subtitle)

    # ── Section 1: Initiative Identity ────────────────────────────────────────
    st.markdown("##### INITIATIVE IDENTITY")
    name = st.text_input(
        "PROPOSED NAME *" if lang == "en" else "提案名 *",
        value=prefill.get("initiative_name", ""),
        placeholder="e.g. Wheat flour supplier consolidation",
    )

    c_id, c_owner = st.columns(2)
    wave_id = c_id.text_input(
        "INITIATIVE #*" if lang == "en" else "イニシアティブ番号 *",
        value=prefill.get("wave_id", ""),
        placeholder="e.g. 63296",
    )
    owner = c_owner.text_input(
        "INITIATIVE OWNER" if lang == "en" else "担当者",
        value=prefill.get("owner", ""),
        placeholder="e.g. Smith, Jane",
    )

    # WAVE auto-lookup hint
    if wave_id:
        hits = [w for w in WAVE_DATA if str(w["id"]) == wave_id.strip()]
        if hits:
            st.success(
                f"✨ WAVE match: **{hits[0]['name']}** [{hits[0]['stage']}] — owner: {hits[0]['owner']}",
                icon=None,
            )

    c_ws, c_subws = st.columns(2)
    workstream = c_ws.text_input(
        "WORKSTREAM" if lang == "en" else "ワークストリーム",
        value=prefill.get("workstream", ""),
        placeholder="e.g. F&B",
    )
    sub_ws_default = prefill.get("sub_workstream", "— Select —")
    sub_ws_idx = _SUB_WS_OPTIONS.index(sub_ws_default) if sub_ws_default in _SUB_WS_OPTIONS else 0
    sub_workstream = c_subws.selectbox(
        "SUB-WORKSTREAM *" if lang == "en" else "サブワークストリーム *",
        _SUB_WS_OPTIONS,
        index=sub_ws_idx,
    )

    st.divider()

    # ── Section 2: Baseline Spend Pull ───────────────────────────────────────
    st.markdown("##### BASELINE SPEND PULL")
    st.caption(
        "Upload a spend file to derive the Baseline Value. "
        "Filters are case-insensitive substring matches."
        if lang == "en" else
        "ベースライン値を取得するための支出ファイルをアップロードしてください。"
    )

    uploaded = st.file_uploader(
        "📂 Drop spend file here or click to upload (.xlsx / .csv)"
        if lang == "en" else
        "📂 支出ファイルをドロップまたはクリックしてアップロード",
        type=["xlsx", "xls", "csv"],
        label_visibility="visible",
    )
    if uploaded:
        st.success(f"📄 {uploaded.name} uploaded — baseline extraction requires backend processing.")

    c_baseline, c_catl3 = st.columns(2)
    baseline_value = c_baseline.number_input(
        "BASELINE VALUE ($)" if lang == "en" else "ベースライン値（$）",
        min_value=0.0,
        value=float(prefill.get("baseline_value") or 0),
        step=1000.0, format="%.0f",
    )
    cat_l3 = c_catl3.text_input(
        "CATEGORY L3 CONTAINS" if lang == "en" else "カテゴリL3（含む）",
        value=prefill.get("cat_l3", ""),
        placeholder="e.g. Dry Foods",
    )

    c_vendor, c_item = st.columns(2)
    vendor_contains = c_vendor.text_input(
        "SUPPLIER / VENDOR CONTAINS" if lang == "en" else "サプライヤー（含む）",
        value=prefill.get("vendor_contains", ""),
        placeholder="e.g. US Foods",
    )
    item_contains = c_item.text_input(
        "ITEM CONTAINS" if lang == "en" else "品目（含む）",
        value=prefill.get("item_contains", ""),
        placeholder="e.g. Flour, Rice",
    )

    st.divider()

    # ── Section 3: Forecast Assumptions ──────────────────────────────────────
    st.markdown("##### FORECAST ASSUMPTIONS")
    st.caption(
        "Savings are calculated from the baseline value. "
        "Recurring benefit is auto-derived from WAVE where available."
        if lang == "en" else
        "節約額はベースライン値から計算されます。継続便益はWAVEから自動導出されます。"
    )

    c_rate, c_rec = st.columns(2)
    saving_rate = c_rate.number_input(
        "SAVINGS ESTIMATION (%) *" if lang == "en" else "節約率（%）*",
        min_value=0.0, max_value=100.0,
        value=float(prefill.get("saving_rate") or 10.0),
        step=0.5,
    )
    # Auto-calculate recurring benefit when baseline + rate are set
    auto_rec = int(baseline_value * saving_rate / 100) if baseline_value else 0
    rec_default = prefill.get("recurring_benefit") or auto_rec
    recurring_benefit = c_rec.number_input(
        "RECURRING BENEFIT ($)" if lang == "en" else "継続便益（$）",
        min_value=0.0,
        value=float(rec_default),
        step=1000.0, format="%.0f",
        help="Auto-calculated from baseline × savings rate" if lang == "en" else "ベースライン×節約率から自動計算",
    )

    c_ot_ben, c_ot_cost = st.columns(2)
    one_time_benefit = c_ot_ben.number_input(
        "ONE-TIME BENEFIT ($)" if lang == "en" else "一時的便益（$）",
        min_value=0.0, value=float(prefill.get("one_time_benefit") or 0),
        step=1000.0, format="%.0f",
    )
    one_time_cost = c_ot_cost.number_input(
        "ONE-TIME IMPL. COST ($)" if lang == "en" else "実装コスト（$）",
        min_value=0.0, value=float(prefill.get("one_time_cost") or 50000),
        step=1000.0, format="%.0f",
    )

    c_neg, c_unit = st.columns(2)
    neg_impact = c_neg.number_input(
        "RECURRING NEG. IMPACT ($)" if lang == "en" else "継続的マイナス影響（$）",
        min_value=0.0, value=float(prefill.get("neg_impact") or 0),
        step=1000.0, format="%.0f",
    )
    unit_default = prefill.get("unit", "$ / year, USD")
    unit_idx = _UNIT_OPTIONS.index(unit_default) if unit_default in _UNIT_OPTIONS else 0
    unit = c_unit.selectbox(
        "BASELINE MEASURE UNIT" if lang == "en" else "ベースライン単位",
        _UNIT_OPTIONS, index=unit_idx,
    )

    st.divider()

    # ── Section 4: Value Tracking ─────────────────────────────────────────────
    st.markdown("##### VALUE TRACKING")
    st.caption(
        "These narrative fields populate the L2 Business Case template."
        if lang == "en" else
        "これらの記述フィールドはL2ビジネスケーステンプレートに反映されます。"
    )

    assumptions = st.text_area(
        "ASSUMPTIONS" if lang == "en" else "前提条件",
        value=prefill.get("assumptions", ""),
        height=100,
        placeholder="e.g. 2025 Rate ($10/unit) - 2026 Rate ($9/unit) = Rate Savings ($1/unit)",
    )
    execution_step = st.text_area(
        "EXECUTION STEP" if lang == "en" else "実施ステップ",
        value=prefill.get("execution_step", ""),
        height=100,
        placeholder="e.g. Master supply agreement signed at new negotiated unit prices",
    )

    c_pnl, c_inc = st.columns(2)
    pnl_allocation = c_pnl.text_input(
        "P&L ALLOCATION" if lang == "en" else "P&L配賦",
        value=prefill.get("pnl_allocation", ""),
        placeholder="e.g. UOR-Wide",
    )
    inc_default = prefill.get("inc_avoidance", "Cost avoidance")
    inc_idx = _INC_AVOIDANCE_OPTIONS.index(inc_default) if inc_default in _INC_AVOIDANCE_OPTIONS else 0
    inc_avoidance = c_inc.selectbox(
        "INC / AVOIDANCE" if lang == "en" else "増分 / 回避",
        _INC_AVOIDANCE_OPTIONS, index=inc_idx,
    )

    st.divider()

    # ── Section 5: Dependencies ───────────────────────────────────────────────
    st.markdown("##### DEPENDENCIES")

    c_it, c_hr = st.columns(2)
    dep_it = c_it.radio(
        "IT DEPENDENCY" if lang == "en" else "IT依存",
        _DEP_OPTIONS,
        index=_DEP_OPTIONS.index(prefill.get("dep_it", "Unknown")),
        horizontal=True,
    )
    dep_hr = c_hr.radio(
        "HR DEPENDENCY" if lang == "en" else "HR依存",
        _DEP_OPTIONS,
        index=_DEP_OPTIONS.index(prefill.get("dep_hr", "Unknown")),
        horizontal=True,
    )
    c_cross, c_capex = st.columns(2)
    dep_cross = c_cross.radio(
        "CROSS-FUNCTIONAL SUPPORT" if lang == "en" else "部門横断サポート",
        _DEP_OPTIONS,
        index=_DEP_OPTIONS.index(prefill.get("dep_cross", "Unknown")),
        horizontal=True,
    )
    dep_capex = c_capex.radio(
        "CAPEX INVESTMENT" if lang == "en" else "CapEx投資",
        _DEP_OPTIONS,
        index=_DEP_OPTIONS.index(prefill.get("dep_capex", "Unknown")),
        horizontal=True,
    )

    st.divider()

    # ── Footer: Cancel | Generate & Download ─────────────────────────────────
    col_cancel, col_gen = st.columns([1, 2])

    with col_cancel:
        if st.button(
            "Cancel" if lang == "en" else "キャンセル",
            use_container_width=True,
        ):
            # Close the dialog by clearing the open flag and rerunning
            st.session_state.bc_open_modal = False
            st.rerun()

    with col_gen:
        if st.button(
            "⬇ Generate & download" if lang == "en" else "⬇ 生成・ダウンロード",
            type="primary",
            use_container_width=True,
            disabled=not name.strip(),
        ):
            all_fields = {
                "initiative_name":   name,
                "wave_id":           wave_id,
                "owner":             owner,
                "workstream":        workstream,
                "sub_workstream":    sub_workstream,
                "category":          workstream,
                "department":        owner,
                "stage":             prefill.get("stage", "L1"),
                "ws":                workstream,
                "baseline_value":    baseline_value,
                "saving_rate":       saving_rate,
                "recurring_benefit": recurring_benefit,
                "one_time_benefit":  one_time_benefit,
                "implementation_cost": one_time_cost,
                "neg_impact":        neg_impact,
                "unit":              unit,
                "assumptions":       assumptions,
                "execution_steps":   execution_step,
                "pnl_allocation":    pnl_allocation,
                "inc_avoidance":     inc_avoidance,
                "dep_it":            dep_it,
                "dep_hr":            dep_hr,
                "dep_cross":         dep_cross,
                "dep_capex":         dep_capex,
                "cat_l3":            cat_l3,
                "vendor_contains":   vendor_contains,
                "item_contains":     item_contains,
            }
            xlsx = export_business_case(all_fields)
            fn = f"L2_BC_{wave_id or name[:20]}.xlsx"

            # Archive to Generated Cases
            archive = {**all_fields, "generated": date.today().strftime("%b %d, %Y")}
            st.session_state.bc_cases = [
                c for c in st.session_state.bc_cases
                if c.get("wave_id") != wave_id
            ]
            st.session_state.bc_cases.append(archive)

            # Add to initiative log if new
            existing_ids = [i.get("wave_id") for i in st.session_state.bc_ideas]
            if wave_id not in existing_ids:
                st.session_state.bc_ideas.append({
                    "initiative_name": name,
                    "category":        workstream,
                    "stage":           prefill.get("stage", "L1"),
                    "wave_id":         wave_id,
                    "owner":           owner,
                    "added":           date.today().strftime("%b %d"),
                })

            st.download_button(
                "📥 Click to Download Excel" if lang == "en" else "📥 クリックしてダウンロード",
                data=xlsx,
                file_name=fn,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            # Close the dialog after the download button appears
            st.session_state.bc_open_modal = False


# ── Main render ────────────────────────────────────────────────────────────────
def render(lang: str = "en"):
    # Session state init
    for key, default in [
        ("bc_ideas", []),
        ("bc_cases", []),
        ("bc_prefill", {}),
        ("bc_open_modal", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Header ────────────────────────────────────────────────────────────────
    st.title(f"📋 {t('tab_bc', lang)}")
    st.caption(
        "Capture initiative ideas from WAVE and turn them into a populated L2 Business Case. "
        "Grounded in 107 active pipeline initiatives (L0–L3) across all spend categories."
        if lang == "en" else
        "WAVEのイニシアティブアイデアを収集し、L2ビジネスケースに変換します。"
        "107のアクティブパイプライン（L0–L3）に基づいています。"
    )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # CARD 1 — Initiative Log
    # ════════════════════════════════════════════════════════════════════════
    idea_count = len(st.session_state.bc_ideas)
    hdr1, hdr2, hdr3 = st.columns([4, 1, 1])
    with hdr1:
        st.markdown(
            f"### {'Initiative log' if lang == 'en' else 'イニシアティブログ'} "
            f"&nbsp;<span style='background:#1e2642;color:#4f8ef7;font-size:11px;"
            f"padding:2px 10px;border-radius:12px;font-weight:600'>"
            f"{idea_count} {'IDEAS' if lang == 'en' else 'アイデア'}</span>",
            unsafe_allow_html=True,
        )
    with hdr2:
        if st.button(
            "▶ Load Demo" if lang == "en" else "▶ デモ読込",
            use_container_width=True,
        ):
            demo_id = "63296"
            if demo_id not in [i.get("wave_id") for i in st.session_state.bc_ideas]:
                st.session_state.bc_ideas.append({
                    "initiative_name": _DEMO_FIELDS["initiative_name"],
                    "category":        _DEMO_FIELDS["workstream"],
                    "stage":           _DEMO_FIELDS["stage"],
                    "wave_id":         demo_id,
                    "owner":           _DEMO_FIELDS["owner"],
                    "added":           date.today().strftime("%b %d"),
                })
            st.session_state.bc_prefill = _DEMO_FIELDS.copy()
            st.session_state.bc_open_modal = True
            st.rerun()
    with hdr3:
        if st.button(
            "+ New Business Case" if lang == "en" else "+ 新規ケース",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.bc_prefill = {}
            st.session_state.bc_open_modal = True
            st.rerun()

    # Initiative log table rows
    if st.session_state.bc_ideas:
        for i, idea in enumerate(st.session_state.bc_ideas):
            row = st.columns([3, 1.5, 1, 1, 1.2, 1])
            row[0].markdown(f"**{idea['initiative_name']}**")
            row[1].caption(idea.get("category", "—"))
            row[2].caption(idea.get("stage", "—"))
            row[3].caption(f"#{idea.get('wave_id', '—')}")
            row[4].caption(idea.get("added", "—"))
            if row[5].button(
                "Build" if lang == "en" else "作成",
                key=f"open_idea_{i}",
            ):
                wid = idea.get("wave_id", "")
                matches = [w for w in WAVE_DATA if str(w["id"]) == wid]
                st.session_state.bc_prefill = (
                    _auto_fill_from_wave(matches[0]) if matches else idea.copy()
                )
                st.session_state.bc_open_modal = True
                st.rerun()
    else:
        st.info(
            "No proposed ideas added yet — click **+ New Business Case** or **Load Demo** to get started."
            if lang == "en" else
            "まだアイデアがありません — **+ 新規ケース**または**デモ読込**をクリックしてください。"
        )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # CARD 2 — Generated Business Cases archive
    # ════════════════════════════════════════════════════════════════════════
    case_count = len(st.session_state.bc_cases)
    st.markdown(
        f"### {'Generated business cases' if lang == 'en' else '生成済みビジネスケース'} "
        f"&nbsp;<span style='background:#1e2642;color:#4ade80;font-size:11px;"
        f"padding:2px 10px;border-radius:12px;font-weight:600'>"
        f"{case_count} {'CASES' if lang == 'en' else 'ケース'}</span>",
        unsafe_allow_html=True,
    )

    if st.session_state.bc_cases:
        for i, case in enumerate(st.session_state.bc_cases):
            row = st.columns([3, 1, 1.5, 1.5, 1])
            row[0].markdown(f"**{case['initiative_name']}**")
            row[1].caption(f"#{case.get('wave_id', '—')}")
            row[2].caption(case.get("category", case.get("workstream", "—")))
            row[3].caption(case.get("generated", "—"))
            if row[4].button(
                "Re-download" if lang == "en" else "再DL",
                key=f"redl_{i}",
            ):
                xlsx = export_business_case(case)
                st.download_button(
                    "📥 Download Excel",
                    data=xlsx,
                    file_name=f"L2_BC_{case.get('wave_id', '')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"redl_btn_{i}",
                )
    else:
        st.caption(
            "Every time you click Generate & download, the inputs are archived here. "
            "Click Re-download on a row to regenerate the exact same workbook without retyping anything."
            if lang == "en" else
            "Excel生成ボタンを押すたびにここに記録されます。再ダウンロードで同じワークブックを再生成できます。"
        )

    # ── Open modal if triggered ───────────────────────────────────────────────
    # Keep bc_open_modal = True while dialog is alive so widget reruns inside
    # the dialog don't accidentally close it. The dialog itself clears this flag
    # via Cancel or Generate buttons.
    if st.session_state.get("bc_open_modal"):
        _bc_modal(lang=lang, prefill=st.session_state.bc_prefill)
