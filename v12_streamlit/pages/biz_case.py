"""
Tab 7 — Business Case Builder
V12: matches HTML layout — Initiative Log table + Generated Cases table + form panel.
"""
from __future__ import annotations
from datetime import date
import streamlit as st
from utils.translations import t
from utils.excel_export import export_business_case
from data.wave_data import WAVE_DATA


# ── Demo data ─────────────────────────────────────────────────────────────────
_DEMO_FIELDS = {
    "initiative_name": "[SPRINT] - Dry Foods RFP (#63296)",
    "category": "Dry Foods",
    "department": "F&B",
    "wave_id": "63296",
    "ws": "F&B",
    "stage": "Su",
    "status": "On track",
    "baseline_value": 8728182,
    "saving_rate": 10.0,
    "recurring_benefit": 870000,
    "one_time_benefit": 0,
    "implementation_cost": 50000,
    "execution_steps": (
        "1. Issue RFP to 8 qualified dry goods distributors\n"
        "2. Evaluate bids and conduct negotiations (target -10% off baseline)\n"
        "3. Implement preferred supplier contract (Avendra leverage)\n"
        "4. Monitor compliance via Vroozi catalog"
    ),
    "assumptions": (
        "Baseline: $8.73M annualized spend per Dry_input.xlsx upload.\n"
        "Saving rate: 10% — consistent with comparable F&B RFP events (Proteins Phase I: 10.1%).\n"
        "Implementation cost: $50K — legal, project management, and system setup.\n"
        "Source: WAVE ID #63296, owner Annmarie Venne; latest $0.87M realized."
    ),
}


def _find_wave(search: str) -> list[dict]:
    s = search.lower()
    return [w for w in WAVE_DATA
            if s in w["name"].lower() or s in str(w["id"]) or s in w["ws"].lower()]


def _auto_fill_from_wave(wave: dict) -> dict:
    return {
        "initiative_name": wave["name"],
        "category": wave["ws"],
        "department": wave["ws"],
        "wave_id": str(wave["id"]),
        "ws": wave["ws"],
        "stage": wave["stage"],
        "status": wave["status"],
        "baseline_value": "",
        "saving_rate": 10.0,
        "recurring_benefit": wave["latest"] * 1_000_000 if wave["latest"] else 0,
        "one_time_benefit": 0,
        "implementation_cost": 50000,
        "execution_steps": "",
        "assumptions": f"Recurring benefit sourced from WAVE latest value: ${wave['latest']:.2f}M.",
    }


def _ai_populate(lang: str):
    import os; from dotenv import load_dotenv; load_dotenv()
    key = ""
    try: key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception: pass
    if not key: key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_JWT_TOKEN_HERE":
        st.warning("AI not available — add API key to Streamlit Secrets" if lang == "en"
                   else "APIキーが必要です。")
        return
    fields = st.session_state.bc_fields
    prompt = (
        f"I'm building an L2 Business Case for the following initiative:\n"
        f"  Name: {fields.get('initiative_name')}\n"
        f"  Category: {fields.get('category')}\n"
        f"  Department: {fields.get('department')}\n"
        f"  Stage: {fields.get('stage')}\n\n"
        "Please populate Sections B, C, D of the L2 Business Case. "
        "Section B: financial inputs (baseline value, savings rate %, recurring benefit). "
        "Section C: implementation steps (numbered list). "
        "Section D: key assumptions and risks. "
        "Ground all figures in actual UDX spend data. Use WAVE data where available."
    )
    from utils.ai_client import build_system_prompt, chat_completion
    messages = [{"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": prompt}]
    with st.spinner("AI is generating Sections B–D…" if lang == "en" else "AIがB〜Dセクションを生成中…"):
        try:
            resp = chat_completion(messages, stream=False)
            st.session_state.bc_ai_messages.append({"role": "assistant", "content": resp})
            st.success("AI populated Sections B–D. Review and adjust below." if lang == "en"
                       else "AIがB〜Dセクションを生成しました。以下を確認・調整してください。")
            st.markdown(resp)
        except Exception as exc:
            st.error(f"AI error: {exc}")


def _respond_advisor(lang: str, user_prompt: str):
    import os; from dotenv import load_dotenv; load_dotenv()
    key = ""
    try: key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception: pass
    if not key: key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_JWT_TOKEN_HERE":
        st.session_state.bc_ai_messages.append({
            "role": "assistant",
            "content": "API key not set." if lang == "en" else "APIキーが設定されていません。"
        })
        return
    from utils.ai_client import build_system_prompt, chat_completion
    fields = st.session_state.bc_fields
    context = (
        f"Current initiative: {fields.get('initiative_name','?')} | "
        f"Category: {fields.get('category','?')} | "
        f"Baseline: ${fields.get('baseline_value',0):,} | "
        f"Saving rate: {fields.get('saving_rate',0)}%"
    )
    messages = [{"role": "system", "content": build_system_prompt() + f"\n\nCurrent BC context: {context}"}]
    messages += st.session_state.bc_ai_messages
    messages.append({"role": "user", "content": user_prompt})
    st.session_state.bc_ai_messages.append({"role": "user", "content": user_prompt})
    try:
        resp = chat_completion(messages, stream=False)
        st.session_state.bc_ai_messages.append({"role": "assistant", "content": resp})
    except Exception as exc:
        st.session_state.bc_ai_messages.append({"role": "assistant", "content": f"Error: {exc}"})


def render(lang: str = "en"):
    # ── Session state ─────────────────────────────────────────────────────────
    for key, default in [
        ("bc_fields", {}),
        ("bc_ai_messages", []),
        ("bc_wave_results", []),
        ("bc_ideas", []),       # Initiative Log entries
        ("bc_cases", []),       # Generated Business Cases archive
        ("bc_show_form", False),
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
            unsafe_allow_html=True
        )
    with hdr2:
        if st.button("▶ Load Demo" if lang == "en" else "▶ デモ読込", use_container_width=True):
            # Add demo to log if not already there
            demo_id = "63296"
            existing_ids = [i.get("wave_id") for i in st.session_state.bc_ideas]
            if demo_id not in existing_ids:
                st.session_state.bc_ideas.append({
                    "initiative_name": "[SPRINT] - Dry Foods RFP (#63296)",
                    "category": "Dry Foods",
                    "stage": "Su",
                    "wave_id": "63296",
                    "department": "F&B",
                    "added": date.today().strftime("%b %d"),
                })
            st.session_state.bc_fields = _DEMO_FIELDS.copy()
            st.session_state.bc_ai_messages = []
            st.session_state.bc_show_form = True
            st.rerun()
    with hdr3:
        if st.button("+ New Business Case" if lang == "en" else "+ 新規ケース",
                     use_container_width=True, type="primary"):
            st.session_state.bc_fields = {}
            st.session_state.bc_ai_messages = []
            st.session_state.bc_show_form = True
            st.rerun()

    # Initiative log table
    if st.session_state.bc_ideas:
        for i, idea in enumerate(st.session_state.bc_ideas):
            row = st.columns([3, 1.5, 1, 1, 1, 1])
            row[0].markdown(f"**{idea['initiative_name']}**")
            row[1].caption(idea.get("category", "—"))
            row[2].caption(idea.get("stage", "—"))
            row[3].caption(f"#{idea.get('wave_id', '—')}")
            row[4].caption(idea.get("added", "—"))
            if row[5].button("Open", key=f"open_idea_{i}"):
                # Find matching wave and pre-fill
                wid = idea.get("wave_id", "")
                matches = [w for w in WAVE_DATA if str(w["id"]) == wid]
                if matches:
                    st.session_state.bc_fields = _auto_fill_from_wave(matches[0])
                else:
                    st.session_state.bc_fields = idea.copy()
                st.session_state.bc_show_form = True
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
        unsafe_allow_html=True
    )
    if st.session_state.bc_cases:
        for i, case in enumerate(st.session_state.bc_cases):
            row = st.columns([3, 1, 1.5, 1.5, 1])
            row[0].markdown(f"**{case['initiative_name']}**")
            row[1].caption(f"#{case.get('wave_id', '—')}")
            row[2].caption(case.get("category", "—"))
            row[3].caption(case.get("generated", "—"))
            if row[4].button("Re-download", key=f"redl_{i}"):
                xlsx = export_business_case(case)
                st.download_button(
                    "📥 Download Excel",
                    data=xlsx,
                    file_name=f"L2_BC_{case.get('wave_id','')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"redl_btn_{i}",
                )
    else:
        st.caption(
            "Every time you click Generate & download Excel, the inputs are archived here. "
            "Click Re-download on a row to regenerate the exact same workbook without retyping anything."
            if lang == "en" else
            "Excel生成ボタンを押すたびにここに記録されます。再ダウンロードボタンで同じワークブックを再生成できます。"
        )

    st.divider()

    # ════════════════════════════════════════════════════════════════════════
    # BUSINESS CASE FORM (shown when bc_show_form = True)
    # ════════════════════════════════════════════════════════════════════════
    if not st.session_state.bc_show_form:
        return

    st.markdown(
        "---\n### 📝 " + ("Build Business Case" if lang == "en" else "ビジネスケース作成"),
        unsafe_allow_html=False,
    )

    # ── Section A ─────────────────────────────────────────────────────────────
    st.subheader("Section A — Initiative Identity" if lang == "en" else "セクションA — イニシアティブ情報")

    col_search, col_close = st.columns([5, 1])
    search_query = col_search.text_input(
        "Search WAVE by name, ID, or workstream" if lang == "en"
        else "WAVE名・ID・ワークストリームで検索", ""
    )
    if col_close.button("✕ Close" if lang == "en" else "✕ 閉じる", use_container_width=True):
        st.session_state.bc_show_form = False
        st.rerun()

    if search_query:
        results = _find_wave(search_query)
        if results:
            st.session_state.bc_wave_results = results
        else:
            st.info("No WAVE initiatives found." if lang == "en" else "WAVEイニシアティブが見つかりません。")

    if st.session_state.bc_wave_results:
        options = {f"#{w['id']} — {w['name']} [{w['stage']}]": w
                   for w in st.session_state.bc_wave_results}
        selected_label = st.selectbox(
            "Select initiative" if lang == "en" else "イニシアティブを選択", list(options.keys())
        )
        if st.button("Load selected" if lang == "en" else "選択を読み込む"):
            sel = options[selected_label]
            st.session_state.bc_fields = _auto_fill_from_wave(sel)
            # Add to initiative log
            existing_ids = [i.get("wave_id") for i in st.session_state.bc_ideas]
            if str(sel["id"]) not in existing_ids:
                st.session_state.bc_ideas.append({
                    "initiative_name": sel["name"],
                    "category": sel["ws"],
                    "stage": sel["stage"],
                    "wave_id": str(sel["id"]),
                    "department": sel["ws"],
                    "added": date.today().strftime("%b %d"),
                })
            st.session_state.bc_wave_results = []
            st.session_state.bc_ai_messages = []
            st.rerun()

    fields = st.session_state.bc_fields

    with st.form("section_a_form"):
        c1, c2 = st.columns(2)
        initiative_name = c1.text_input(
            "Initiative Name *" if lang == "en" else "イニシアティブ名 *",
            value=fields.get("initiative_name", ""))
        wave_id = c2.text_input("WAVE ID", value=fields.get("wave_id", ""))
        c3, c4 = st.columns(2)
        category = c3.text_input(
            "Category" if lang == "en" else "カテゴリ", value=fields.get("category", ""))
        department = c4.text_input(
            "Department / Owner" if lang == "en" else "部門 / 担当者",
            value=fields.get("department", ""))
        c5, c6 = st.columns(2)
        ws = c5.text_input(
            "Workstream" if lang == "en" else "ワークストリーム", value=fields.get("ws", ""))
        stage_opts = ["L0","L1","L2","L3","L4","Su"]
        stage = c6.selectbox(
            "Stage" if lang == "en" else "ステージ", stage_opts,
            index=stage_opts.index(fields.get("stage","L1"))
            if fields.get("stage") in stage_opts else 1)
        submit_a = st.form_submit_button(
            "Save & Populate with AI" if lang == "en" else "保存してAI入力",
            type="primary")

    if submit_a:
        st.session_state.bc_fields.update({
            "initiative_name": initiative_name,
            "wave_id": wave_id,
            "category": category,
            "department": department,
            "ws": ws,
            "stage": stage,
        })
        # Add to initiative log if new
        existing_ids = [i.get("wave_id") for i in st.session_state.bc_ideas]
        if wave_id and wave_id not in existing_ids:
            st.session_state.bc_ideas.append({
                "initiative_name": initiative_name,
                "category": category,
                "stage": stage,
                "wave_id": wave_id,
                "department": department,
                "added": date.today().strftime("%b %d"),
            })
        _ai_populate(lang)

    # ── Sections B–D (only if Section A filled) ───────────────────────────────
    if not fields.get("initiative_name"):
        return

    st.divider()

    # Section B
    st.subheader("Section B — Financial Inputs" if lang == "en" else "セクションB — 財務インプット")
    with st.form("section_b_form"):
        c1, c2, c3 = st.columns(3)
        baseline_value = c1.number_input(
            "Baseline Value ($)" if lang == "en" else "ベースライン値（$）",
            min_value=0.0, value=float(fields.get("baseline_value") or 0),
            step=1000.0, format="%.0f")
        saving_rate = c2.number_input(
            "Savings Rate (%)" if lang == "en" else "節約率（%）",
            min_value=0.0, max_value=100.0,
            value=float(fields.get("saving_rate") or 10.0), step=0.5)
        recurring_benefit = c3.number_input(
            "Recurring Benefit ($/yr)" if lang == "en" else "毎年の便益（$/年）",
            min_value=0.0, value=float(fields.get("recurring_benefit") or 0),
            step=1000.0, format="%.0f")
        c4, c5 = st.columns(2)
        one_time = c4.number_input(
            "One-time Benefit ($)" if lang == "en" else "一時的便益（$）",
            min_value=0.0, value=float(fields.get("one_time_benefit") or 0),
            step=1000.0, format="%.0f")
        impl_cost = c5.number_input(
            "Implementation Cost ($)" if lang == "en" else "実装コスト（$）",
            min_value=0.0, value=float(fields.get("implementation_cost") or 50000),
            step=1000.0, format="%.0f")
        submit_b = st.form_submit_button("Save Section B" if lang == "en" else "セクションBを保存")
    if submit_b:
        st.session_state.bc_fields.update({
            "baseline_value": baseline_value,
            "saving_rate": saving_rate,
            "recurring_benefit": recurring_benefit,
            "one_time_benefit": one_time,
            "implementation_cost": impl_cost,
        })
        st.success("Section B saved." if lang == "en" else "セクションBを保存しました。")

    st.divider()

    # Section C
    st.subheader("Section C — Implementation Steps" if lang == "en" else "セクションC — 実施ステップ")
    with st.form("section_c_form"):
        exec_steps = st.text_area(
            "Steps" if lang == "en" else "ステップ",
            value=fields.get("execution_steps", ""), height=140)
        submit_c = st.form_submit_button("Save Section C" if lang == "en" else "セクションCを保存")
    if submit_c:
        st.session_state.bc_fields["execution_steps"] = exec_steps
        st.success("Section C saved." if lang == "en" else "セクションCを保存しました。")

    st.divider()

    # Section D
    st.subheader("Section D — Assumptions & Risks" if lang == "en" else "セクションD — 前提条件・リスク")
    with st.form("section_d_form"):
        assumptions = st.text_area(
            "Assumptions" if lang == "en" else "前提条件",
            value=fields.get("assumptions", ""), height=120)
        submit_d = st.form_submit_button("Save Section D" if lang == "en" else "セクションDを保存")
    if submit_d:
        st.session_state.bc_fields["assumptions"] = assumptions
        st.success("Section D saved." if lang == "en" else "セクションDを保存しました。")

    st.divider()

    # ── AI Advisor chat ───────────────────────────────────────────────────────
    st.subheader("🤖 AI Case Advisor" if lang == "en" else "🤖 AIケースアドバイザー")
    for msg in st.session_state.bc_ai_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    advisor_prompt = st.chat_input(
        "Ask the AI to improve or explain any section…" if lang == "en"
        else "AIにセクションの改善・説明を依頼…")
    if advisor_prompt:
        _respond_advisor(lang, advisor_prompt)
        st.rerun()

    st.divider()

    # ── Generate & Download Excel ─────────────────────────────────────────────
    st.subheader("📥 Generate & Download Excel" if lang == "en" else "📥 Excel生成・ダウンロード")
    col_gen, col_info = st.columns([2, 3])
    with col_gen:
        if st.button("Generate & Download Excel" if lang == "en" else "Excel生成・ダウンロード",
                     type="primary", use_container_width=True):
            all_fields = {**fields,
                          "execution_steps": fields.get("execution_steps",""),
                          "assumptions": fields.get("assumptions","")}
            xlsx = export_business_case(all_fields)
            fn = f"L2_BC_{fields.get('wave_id','')}.xlsx"
            st.download_button(
                "📥 Click to Download" if lang == "en" else "📥 クリックしてダウンロード",
                data=xlsx,
                file_name=fn,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            # Archive to Generated Cases
            archive_entry = {**all_fields, "generated": date.today().strftime("%b %d, %Y")}
            # Replace if same wave_id exists
            st.session_state.bc_cases = [
                c for c in st.session_state.bc_cases
                if c.get("wave_id") != fields.get("wave_id")
            ]
            st.session_state.bc_cases.append(archive_entry)
    with col_info:
        if fields.get("baseline_value") and fields.get("saving_rate"):
            bv = float(fields.get("baseline_value") or 0)
            sr = float(fields.get("saving_rate") or 0)
            est = bv * sr / 100
            st.info(
                f"Estimated savings: **${est:,.0f}** ({sr:.1f}% of ${bv:,.0f} baseline)"
                if lang == "en" else
                f"推定節約額: **${est:,.0f}** (ベースライン ${bv:,.0f} の {sr:.1f}%)"
            )
