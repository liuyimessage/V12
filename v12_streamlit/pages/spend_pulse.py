"""Tab 1 — Spend Pulse."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.spend_data import MONTHS, MONTHLY_TOTAL, MONTHLY_BY_CAT, YOY


def render(lang: str = "en"):
    st.title(f"📈 {t('tab_pulse', lang)}")
    st.caption(t("app_subtitle", lang))

    # KPI row — matches HTML: 5 tiles
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(t("kpi_total", lang), "$1,164.7M")
    k2.metric(t("kpi_po", lang), "800,158")
    k3.metric(t("kpi_avg", lang), "$1,456")
    k4.metric(t("kpi_yoy", lang), "-16.1%", delta_color="off")
    k5.metric(t("kpi_peak", lang), "$96.9M")
    st.divider()

    # ── Two-column charts (matches HTML grid-2) ───────────────────────────────
    col_left, col_right = st.columns(2)

    # Monthly trend line (left column)
    with col_left:
        st.subheader(t("trend_hdr", lang))
        st.caption(t("trend_sub", lang))
        df_trend = pd.DataFrame({"Month": MONTHS, "Spend ($M)": MONTHLY_TOTAL})
        fig_trend = px.line(
            df_trend, x="Month", y="Spend ($M)",
            markers=True, template="plotly_dark",
            color_discrete_sequence=["#4f8ef7"],
        )
        fig_trend.add_hline(
            y=sum(MONTHLY_TOTAL) / len(MONTHLY_TOTAL),
            line_dash="dash", line_color="#aaa",
            annotation_text="Avg",
        )
        fig_trend.update_layout(
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-45, gridcolor="#2a2f40"),
            yaxis=dict(gridcolor="#2a2f40"),
            hovermode="x unified",
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Stacked area (right column)
    with col_right:
        st.subheader(t("stack_hdr", lang))
        cat_frames = []
        for cat, vals in MONTHLY_BY_CAT.items():
            for m, v in zip(MONTHS, vals):
                cat_frames.append({"Month": m, "Category": cat, "Spend ($M)": v})
        df_stack = pd.DataFrame(cat_frames)
        fig_area = px.area(
            df_stack, x="Month", y="Spend ($M)", color="Category",
            template="plotly_dark",
        )
        fig_area.update_layout(
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-45, gridcolor="#2a2f40"),
            yaxis=dict(gridcolor="#2a2f40"),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    # ── YoY table (full-width, matches HTML) ─────────────────────────────────
    st.subheader(t("yoy_hdr", lang))
    note_key = "note_en" if lang == "en" else "note_jp"
    df_yoy = pd.DataFrame([
        {
            t("col_month", lang): row["month"],
            t("col_2025", lang): row["y2025"],
            t("col_2026", lang): row["y2026"],
            t("col_chg", lang): f"{((row['y2026'] - row['y2025']) / row['y2025'] * 100):.1f}%",
            t("col_note", lang): row[note_key],
        }
        for row in YOY
    ])
    st.dataframe(df_yoy, use_container_width=True, hide_index=True)
    st.caption(t("yoy_footnote", lang))
