"""Tab 1 — Spend Pulse."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.spend_data import MONTHS, MONTHLY_TOTAL, MONTHLY_BY_CAT, YOY

# ── Shared chart constants — both charts must be identical ────────────────────
_H        = 400                               # fixed height for both charts
_BG       = "#1a1f2e"
_GRID     = "#2a2f40"
_MARGIN   = dict(l=55, r=15, t=50, b=90)     # t=50 reserves room for in-chart title
_XAXIS    = dict(tickangle=-45, gridcolor=_GRID, tickfont=dict(size=9))
_YAXIS    = dict(gridcolor=_GRID, tickfont=dict(size=10))
_TITLE_FONT = dict(size=13, color="#e0e6ff", family="sans-serif")


def render(lang: str = "en"):
    st.title(f"📈 {t('tab_pulse', lang)}")
    st.caption(t("app_subtitle", lang))

    # KPI row — 5 tiles matching HTML
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(t("kpi_total", lang), "$1,164.7M")
    k2.metric(t("kpi_po", lang), "800,158")
    k3.metric(t("kpi_avg", lang), "$1,456")
    k4.metric(t("kpi_yoy", lang), "-16.1%", delta_color="off")
    k5.metric(t("kpi_peak", lang), "$96.9M")
    st.divider()

    # ── Two-column chart row ───────────────────────────────────────────────────
    # Titles are embedded INSIDE the Plotly figure so the only element in each
    # column is the chart itself — guaranteeing pixel-perfect alignment.
    col_left, col_right = st.columns(2)

    # LEFT — Monthly Spend Trend
    with col_left:
        trend_title = (
            "Monthly Spend Trend ($M)"
            if lang == "en" else "月次支出トレンド（百万ドル）"
        )
        trend_sub = (
            "All categories · Jan 2024 – Apr 2026"
            if lang == "en" else "全カテゴリ · 2024年1月〜2026年4月"
        )

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
            annotation_position="right",
        )
        fig_trend.update_layout(
            height=_H,
            plot_bgcolor=_BG, paper_bgcolor=_BG,
            margin=_MARGIN,
            xaxis={**_XAXIS, "title": ""},
            yaxis={**_YAXIS, "title": "Spend ($M)"},
            hovermode="x unified",
            showlegend=False,
            title=dict(
                text=f"<b>{trend_title}</b><br><span style='font-size:10px;color:#8090b0'>{trend_sub}</span>",
                x=0, xanchor="left",
                font=_TITLE_FONT,
                pad=dict(l=0, t=0),
            ),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # RIGHT — Stacked Area by Category
    with col_right:
        stack_title = (
            "Spend by Top Categories Over Time ($M)"
            if lang == "en" else "カテゴリ別支出推移（百万ドル）"
        )
        stack_sub = "Stacked area" if lang == "en" else "積み上げエリア"

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
            height=_H,
            plot_bgcolor=_BG, paper_bgcolor=_BG,
            margin=_MARGIN,
            xaxis={**_XAXIS, "title": ""},
            yaxis={**_YAXIS, "title": "Spend ($M)"},
            title=dict(
                text=f"<b>{stack_title}</b><br><span style='font-size:10px;color:#8090b0'>{stack_sub}</span>",
                x=0, xanchor="left",
                font=_TITLE_FONT,
                pad=dict(l=0, t=0),
            ),
            legend=dict(
                orientation="v",
                x=1.01, xanchor="left", y=1, yanchor="top",
                font=dict(size=9, color="#c0c8e0"),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    # ── YoY table (full-width) ────────────────────────────────────────────────
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
