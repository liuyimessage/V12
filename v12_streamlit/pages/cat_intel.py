"""Tab 2 — Category Intelligence."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.cat_data import CAT_LABELS, CAT_SPEND, CAT_GAP
from data.spend_data import MONTHS, HEATMAP


def render(lang: str = "en"):
    st.title(f"🗂️ {t('tab_cat', lang)}")

    # KPIs — matches HTML exactly (10 / $87.4M / Nov 2025 / 3)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Categories Cover 85%+ of Spend" if lang == "en" else "カテゴリが支出の85%以上をカバー",
        "10"
    )
    k2.metric(
        "FA Equip. Rental — #1 Category" if lang == "en" else "FA機器リース — 第1カテゴリ",
        "$87.4M",
        help="21.1% of total spend" if lang == "en" else "総支出の21.1%"
    )
    k3.metric(
        "Anomaly Spike Month" if lang == "en" else "異常スパイク月",
        "Nov 2025",
        help="$96.9M — FA Equip. lease spike" if lang == "en" else "$96.9M — FA機器リーススパイク"
    )
    k4.metric(
        "Top Categories with No WAVE Coverage" if lang == "en" else "WAVEカバレッジなし上位カテゴリ",
        "3"
    )
    st.divider()

    # ── Two-column layout: Pareto (left) | Coverage Gap (right) ─────────────
    # Matches HTML grid-2
    col_pareto, col_gap = st.columns(2)

    with col_pareto:
        st.subheader(t("cat_pareto_hdr", lang))
        cum = 0.0
        cum_pcts = []
        total = sum(CAT_SPEND)
        for s in CAT_SPEND:
            cum += s / total * 100
            cum_pcts.append(round(cum, 1))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=CAT_LABELS, y=CAT_SPEND, name="Spend ($M)",
            marker_color="#4f8ef7", yaxis="y",
        ))
        fig.add_trace(go.Scatter(
            x=CAT_LABELS, y=cum_pcts, name="Cumul. %",
            mode="lines+markers", yaxis="y2",
            line=dict(color="#ffcc00", width=2),
        ))
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
            yaxis=dict(title="Spend ($M)", gridcolor="#2a2f40"),
            yaxis2=dict(title="Cumul. %", overlaying="y", side="right",
                        range=[0, 110], showgrid=False),
            xaxis=dict(tickangle=-30),
            legend=dict(orientation="h", y=1.05),
            margin=dict(l=10, r=10, t=30, b=10),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_gap:
        st.subheader(t("cat_gap_hdr", lang))
        note_key = "note_en" if lang == "en" else "note_jp"
        for gap in CAT_GAP:
            color = {"gap": "#c0392b", "partial": "#e67e22", "ok": "#27ae60"}[gap["status"]]
            label = {
                "gap": t("gap", lang),
                "partial": t("partial", lang),
                "ok": t("covered", lang),
            }[gap["status"]]
            with st.container():
                c1, c2, c3 = st.columns([2, 4, 1])
                c1.markdown(f"**{gap['cat']}**")
                c2.caption(gap[note_key])
                c3.markdown(
                    f"<span style='color:{color};font-weight:bold'>{label}</span>",
                    unsafe_allow_html=True,
                )
            st.divider()

    # ── Heatmap (full-width, below the two columns) ───────────────────────────
    # Matches HTML: heatmap is the bottom card in cat_intel
    st.subheader(t("hm_hdr", lang))
    st.caption(t("hm_sub", lang))

    heat_cats = list(HEATMAP.keys())
    heat_vals = [HEATMAP[c] for c in heat_cats]
    fig_hm = px.imshow(
        heat_vals,
        x=MONTHS,
        y=heat_cats,
        color_continuous_scale="Blues",
        template="plotly_dark",
        aspect="auto",
        labels={"color": "$M"},
    )
    fig_hm.update_layout(
        plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickangle=-45),
        coloraxis_colorbar=dict(title="$M"),
    )
    st.plotly_chart(fig_hm, use_container_width=True)
