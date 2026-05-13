"""Tab 1 — Spend Pulse."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.spend_data import MONTHS, MONTHLY_TOTAL, MONTHLY_BY_CAT, HEATMAP, YOY


def render(lang: str = "en"):
    st.title(f"📈 {t('tab_pulse', lang)}")
    st.caption(t("app_subtitle", lang))

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(t("kpi_total", lang), "$1,164.7M")
    k2.metric(t("kpi_po", lang), "800,158")
    k3.metric(t("kpi_avg", lang), "$1,456")
    k4.metric(t("kpi_yoy", lang), "-35.7%", delta_color="off")
    k5.metric(t("kpi_peak", lang), "$160.0M")
    st.divider()

    # ── Monthly trend line ────────────────────────────────────────────────────
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

    # ── Stacked area by top category ─────────────────────────────────────────
    st.subheader(t("stack_hdr", lang))
    months_list = MONTHS
    cat_frames = []
    for cat, vals in MONTHLY_BY_CAT.items():
        for m, v in zip(months_list, vals):
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

    # ── Heatmap ───────────────────────────────────────────────────────────────
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

    # ── YoY table ─────────────────────────────────────────────────────────────
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
