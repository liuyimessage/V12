"""Tab 7 — Business Case Builder."""
from __future__ import annotations
import json
from datetime import date
import streamlit as st
from utils.translations import t
from utils.excel_export import export_business_case
from data.wave_data import WAVE_DATA
from utils.ai_client import build_system_prompt, chat_completion

_DEMO_FIELDS = {
    "initiative_name": "[SPRINT] - Dry Foods RFP (#63296)",
    "category": "Dry Foods",
    "department": "F&B",
    "wave_id": "63296",
    "ws": "F&B",
    "stage": "L1",
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
    search_low = search.lower()
    return [
        w for w in WAVE_DATA
        if search_low in w["name"].lower()
        or search_low in str(w["id"])
        or search_low in w["ws"].lower()
    ]


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


def render(lang: str = "en"):
    st.title(f"📋 {t('tab_bc', lang)}")
    st.caption(t("bc_sub", lang))

    # Session state for this page
    if "bc_fields" not in st.session_state:
        st.session_state.bc_fields = {}
    if "bc_ai_messages" not in st.session_state:
        st.session_state.bc_ai_messages = []
    if "bc_wave_results" not in st.session_state:
        st.session_state.bc_wave_results = []

    # ── "What am I?" card ─────────────────────────────────────────────────────
    with st.expander("ℹ️ What is the Business Case Builder?" if lang == "en"
                     else "ℹ️ ビジネスケースビルダーとは？", expanded=False):
        if lang == "en":
            st.markdown(
                "The **Business Case Builder** turns your procurement initiative into a structured "
                "L2 Business Case in **1–2 hours** instead of 2–3 days.\n\n"
                "- Grounded in $59.6M active L3 pipeline WAVE data across 107 initiatives\n"
                "- AI advisor auto-populates Sections B, C, D from WAVE data\n"
                "- One-click export to colour-coded Excel matching the L2 template"
            )
        else:
            st.markdown(
                "**ビジネスケースビルダー**は、調達イニシアティブを構造化されたL2ビジネスケースに"
                "**1〜2時間**で変換します（従来は2〜3日）。\n\n"
                "- 107のイニシアティブにわたる$59.6M L3パイプラインWAVEデータに基づく\n"
                "- AIアドバイザーがWAVEデータからセクションB、C、Dを自動入力\n"
                "- L2テンプレートに一致するカラーコードExcelへのワンクリックエクスポート"
            )

    st.divider()

    # ── Section A — Initiative Identity ──────────────────────────────────────
    st.subheader("Section A — Initiative Identity" if lang == "en"
                 else "セクションA — イニシアティブ情報")

    col_search, col_demo = st.columns([4, 1])
    search_query = col_search.text_input(
        "Search WAVE by name, ID, or workstream" if lang == "en"
        else "WAVE名・ID・ワークストリームで検索", ""
    )
    with col_demo:
        st.write("")
        if st.button(t("bc_demo", lang), use_container_width=True):
            st.session_state.bc_fields = _DEMO_FIELDS.copy()
            st.session_state.bc_ai_messages = []
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
            st.session_state.bc_fields = _auto_fill_from_wave(options[selected_label])
            st.session_state.bc_wave_results = []
            st.session_state.bc_ai_messages = []
            st.rerun()

    fields = st.session_state.bc_fields

    with st.form("section_a_form"):
        col1, col2 = st.columns(2)
        initiative_name = col1.text_input(
            "Initiative Name *" if lang == "en" else "イニシアティブ名 *",
            value=fields.get("initiative_name", "")
        )
        wave_id = col2.text_input(
            "WAVE ID" if lang == "en" else "WAVE ID",
            value=fields.get("wave_id", "")
        )
        col3, col4 = st.columns(2)
        category = col3.text_input(
            "Category" if lang == "en" else "カテゴリ",
            value=fields.get("category", "")
        )
        department = col4.text_input(
            "Department / Owner" if lang == "en" else "部門 / 担当者",
            value=fields.get("department", "")
        )
        col5, col6 = st.columns(2)
        ws = col5.text_input(
            "Workstream" if lang == "en" else "ワークストリーム",
            value=fields.get("ws", "")
        )
        stage = col6.selectbox(
            "Stage" if lang == "en" else "ステージ",
            ["L0","L1","L2","L3","L4","Su"],
            index=["L0","L1","L2","L3","L4","Su"].index(fields.get("stage","L1"))
            if fields.get("stage") in ["L0","L1","L2","L3","L4","Su"] else 1
        )
        submit_a = st.form_submit_button(
            "Save & Populate with AI" if lang == "en" else "保存してAI入力"
        )

    if submit_a:
        st.session_state.bc_fields.update({
            "initiative_name": initiative_name,
            "wave_id": wave_id,
            "category": category,
            "department": department,
            "ws": ws,
            "stage": stage,
        })
        # Trigger AI to fill sections B-D
        _ai_populate(lang)

    # ── Sections B-D (shown if fields populated) ──────────────────────────────
    if fields.get("initiative_name"):
        st.divider()
        st.subheader("Section B — Financial Inputs" if lang == "en"
                     else "セクションB — 財務インプット")

        with st.form("section_b_form"):
            col1, col2, col3 = st.columns(3)
            baseline_value = col1.number_input(
                "Baseline Value ($)" if lang == "en" else "ベースライン値（ドル）",
                min_value=0.0,
                value=float(fields.get("baseline_value", 0) or 0),
                step=1000.0,
                format="%.0f",
            )
            saving_rate = col2.number_input(
                "Saving Rate (%)" if lang == "en" else "節約率（%）",
                min_value=0.0, max_value=100.0,
                value=float(fields.get("saving_rate", 10.0) or 10.0),
                step=0.5,
            )
            rec_benefit = col3.number_input(
                "Recurring Benefit ($)" if lang == "en" else "継続的便益（ドル）",
                min_value=0.0,
                value=float(fields.get("recurring_benefit", 0) or 0),
                step=1000.0, format="%.0f",
            )
            col4, col5 = st.columns(2)
            one_time = col4.number_input(
                "One-Time Benefit ($)" if lang == "en" else "一時便益（ドル）",
                min_value=0.0,
                value=float(fields.get("one_time_benefit", 0) or 0),
                step=1000.0, format="%.0f",
            )
            impl_cost = col5.number_input(
                "Implementation Cost ($)" if lang == "en" else "実装コスト（ドル）",
                min_value=0.0,
                value=float(fields.get("implementation_cost", 50000) or 50000),
                step=1000.0, format="%.0f",
            )
            net = rec_benefit + one_time - impl_cost
            st.metric(
                "Net Benefit ($)" if lang == "en" else "純便益（ドル）",
                f"${net:,.0f}"
            )
            submit_b = st.form_submit_button("Save" if lang == "en" else "保存")

        if submit_b:
            st.session_state.bc_fields.update({
                "baseline_value": baseline_value,
                "saving_rate": saving_rate,
                "recurring_benefit": rec_benefit,
                "one_time_benefit": one_time,
                "implementation_cost": impl_cost,
            })
            st.success("Section B saved." if lang == "en" else "セクションBを保存しました。")

        st.divider()
        st.subheader("Section C — Execution Plan" if lang == "en"
                     else "セクションC — 実行計画")
        exec_steps = st.text_area(
            "Execution steps (one per line)" if lang == "en" else "実行ステップ（1行に1ステップ）",
            value=fields.get("execution_steps", ""),
            height=120,
            key="exec_steps_area",
        )
        if st.button("Save execution plan" if lang == "en" else "実行計画を保存"):
            st.session_state.bc_fields["execution_steps"] = exec_steps
            st.success("Saved." if lang == "en" else "保存しました。")

        st.divider()
        st.subheader("Section D — Assumptions & Risks" if lang == "en"
                     else "セクションD — 前提条件とリスク")
        assumptions = st.text_area(
            "Assumptions" if lang == "en" else "前提条件",
            value=fields.get("assumptions", ""),
            height=100,
            key="assumptions_area",
        )
        if st.button("Save assumptions" if lang == "en" else "前提条件を保存"):
            st.session_state.bc_fields["assumptions"] = assumptions
            st.success("Saved." if lang == "en" else "保存しました。")

        # ── AI Advisor ────────────────────────────────────────────────────────
        st.divider()
        st.subheader("🤖 AI Case Advisor" if lang == "en" else "🤖 AIケースアドバイザー")
        for msg in st.session_state.bc_ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        advisor_prompt = st.chat_input(
            "Ask the AI to improve or explain any section..." if lang == "en"
            else "AIにセクションの改善や説明を依頼してください..."
        )
        if advisor_prompt:
            st.session_state.bc_ai_messages.append({"role": "user", "content": advisor_prompt})
            with st.chat_message("user"):
                st.markdown(advisor_prompt)
            _respond_advisor(lang, advisor_prompt)

        # ── Excel Export ──────────────────────────────────────────────────────
        st.divider()
        current_fields = st.session_state.bc_fields
        if current_fields.get("initiative_name"):
            xls_bytes = export_business_case(current_fields)
            fname = f"UDX_L2_BusinessCase_{date.today().strftime('%Y-%m-%d')}.xlsx"
            st.download_button(
                label=t("download_excel", lang),
                data=xls_bytes,
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )


def _ai_populate(lang: str):
    """Use AI to auto-suggest Sections B-D based on Section A."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    key = ""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception:
        pass
    if not key:
        key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_JWT_TOKEN_HERE":
        st.warning("AI not available — add API key to .env or Streamlit Secrets" if lang == "en"
                   else "APIキーが必要です。")
        return

    fields = st.session_state.bc_fields
    prompt = (
        f"I'm building an L2 Business Case for the following initiative:\n"
        f"  Name: {fields.get('initiative_name')}\n"
        f"  Category: {fields.get('category')}\n"
        f"  Workstream: {fields.get('ws')}\n"
        f"  WAVE ID: {fields.get('wave_id')}\n"
        f"  Stage: {fields.get('stage')}\n\n"
        "Based on the embedded WAVE data and spend analytics:\n"
        "1. Suggest a realistic Baseline Value (annualized spend in this category).\n"
        "2. Recommend a saving rate (%) with justification.\n"
        "3. Estimate Recurring Benefit and Implementation Cost.\n"
        "4. Draft 3-5 Execution Steps.\n"
        "5. Draft key Assumptions.\n"
        "Return JSON with keys: baseline_value, saving_rate, recurring_benefit, "
        "implementation_cost, execution_steps (multiline string), assumptions (string)."
    )

    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": prompt},
    ]

    with st.spinner("AI is populating Sections B–D..." if lang == "en"
                    else "AIがセクションB〜Dを入力中..."):
        try:
            raw = chat_completion(messages, stream=False)
            # Try to extract JSON from markdown fences
            raw_clean = raw
            if "```json" in raw:
                raw_clean = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw_clean = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw_clean)
            st.session_state.bc_fields.update(data)
            st.session_state.bc_ai_messages.append({
                "role": "assistant",
                "content": (
                    f"✅ Sections B–D auto-populated from WAVE data.\n\n"
                    f"**Baseline:** ${float(data.get('baseline_value',0)):,.0f} · "
                    f"**Rate:** {data.get('saving_rate',0):.1f}% · "
                    f"**Recurring Benefit:** ${float(data.get('recurring_benefit',0)):,.0f}"
                ),
            })
            st.rerun()
        except Exception as exc:
            st.warning(f"AI population failed: {exc}. Please fill Sections B–D manually.")


def _respond_advisor(lang: str, user_prompt: str):
    """Stream a response from the AI Advisor."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    key = ""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "").strip()
    except Exception:
        pass
    if not key:
        key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "PASTE_YOUR_JWT_TOKEN_HERE":
        msg = "API key not set." if lang == "en" else "APIキーが設定されていません。"
        st.session_state.bc_ai_messages.append({"role": "assistant", "content": msg})
        return

    fields = st.session_state.bc_fields
    context = (
        f"Current Business Case context:\n"
        f"  Initiative: {fields.get('initiative_name')}\n"
        f"  Baseline: ${fields.get('baseline_value', 'N/A')}\n"
        f"  Saving Rate: {fields.get('saving_rate', 'N/A')}%\n"
        f"  Recurring Benefit: ${fields.get('recurring_benefit', 'N/A')}\n"
    )
    messages = [
        {"role": "system", "content": build_system_prompt() + "\n\n" + context},
    ] + st.session_state.bc_ai_messages

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
        except Exception as exc:
            full_response = f"Error: {exc}"
            placeholder.error(full_response)

    st.session_state.bc_ai_messages.append(
        {"role": "assistant", "content": full_response}
    )
