"""Page 1 — Spend Pulse: custom chart functions + Vizro page config."""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import vizro.models as vm
from vizro.models.types import capture

from data.spend_data import MONTHS, MONTHLY_TOTAL, MONTHLY_BY_CAT, HEATMAP, YOY


# ── Custom chart functions ────────────────────────────────────────────────────

@capture("graph")
def monthly_trend(data_frame: pd.DataFrame) -> go.Figure:
    df = pd.DataFrame({"Month": MONTHS, "Spend ($M)": MONTHLY_TOTAL})
    avg = sum(MONTHLY_TOTAL) / len(MONTHLY_TOTAL)
    fig = px.line(
        df, x="Month", y="Spend ($M)",
        markers=True, template="vizro_dark",
        color_discrete_sequence=["#4f8ef7"],
        title="",
    )
    fig.add_hline(y=avg, line_dash="dash", line_color="#888",
                  annotation_text=f"Avg ${avg:.1f}M", annotation_position="top right")
    # Highlight Nov-25 peak
    peak_idx = MONTHLY_TOTAL.index(max(MONTHLY_TOTAL))
    fig.add_scatter(
        x=[MONTHS[peak_idx]], y=[MONTHLY_TOTAL[peak_idx]],
        mode="markers", marker=dict(color="#ff6b35", size=14, symbol="star"),
        name="Peak: Nov-25",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(tickangle=-45, gridcolor="#2a2f40"),
        yaxis=dict(gridcolor="#2a2f40"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.05),
    )
    return fig


@capture("graph")
def stacked_area(data_frame: pd.DataFrame) -> go.Figure:
    rows = []
    for cat, vals in MONTHLY_BY_CAT.items():
        for m, v in zip(MONTHS, vals):
            rows.append({"Month": m, "Category": cat, "Spend ($M)": v})
    df = pd.DataFrame(rows)
    fig = px.area(
        df, x="Month", y="Spend ($M)", color="Category",
        template="vizro_dark",
        title="",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(tickangle=-45, gridcolor="#2a2f40"),
        yaxis=dict(gridcolor="#2a2f40"),
        legend=dict(orientation="h", y=1.05, font=dict(size=10)),
    )
    return fig


@capture("graph")
def spend_heatmap(data_frame: pd.DataFrame) -> go.Figure:
    cats = list(HEATMAP.keys())
    vals = [HEATMAP[c] for c in cats]
    fig = px.imshow(
        vals, x=MONTHS, y=cats,
        color_continuous_scale="Blues",
        template="vizro_dark", aspect="auto",
        labels={"color": "$M"},
        title="",
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(tickangle=-45),
        coloraxis_colorbar=dict(title="$M"),
    )
    return fig


@capture("graph")
def yoy_bar(data_frame: pd.DataFrame) -> go.Figure:
    months_label = [r["month"] for r in YOY]
    y2025 = [r["y2025"] for r in YOY]
    y2026 = [r["y2026"] for r in YOY]
    fig = go.Figure()
    fig.add_bar(x=months_label, y=y2025, name="2025", marker_color="#4f8ef7")
    fig.add_bar(x=months_label, y=y2026, name="2026", marker_color="#ff9800")
    fig.update_layout(
        barmode="group",
        template="vizro_dark",
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Spend ($M)",
        xaxis_title="",
        legend=dict(orientation="h", y=1.05),
    )
    return fig


# ── Vizro Page ────────────────────────────────────────────────────────────────

spend_pulse_page = vm.Page(
    id="spend-pulse",
    title="📈 Spend Pulse",
    layout=vm.Grid(grid=[
        [0, 0, 1, 1, 2, 2, 3, 3],
        [4, 4, 4, 4, 4, 4, 4, 4],
        [5, 5, 5, 5, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7, 7, 7],
    ]),
    components=[
        vm.Card(id="kpi-total-spend",   text="### $1,164.7M\n**Total Spend** · Jan 2024–Apr 2026"),
        vm.Card(id="kpi-total-pos",     text="### 800,158\n**Total Purchase Orders**"),
        vm.Card(id="kpi-peak-month",    text="### $96.9M\n**Peak Month** · Nov 2025"),
        vm.Card(id="kpi-yoy",           text="### −16.1%\n**Q1 YoY** · 2026 vs 2025"),
        vm.Graph(
            id="chart-monthly-trend",
            title="Monthly Total Spend Trend",
            figure=monthly_trend(data_frame=pd.DataFrame()),
        ),
        vm.Graph(
            id="chart-stacked-area",
            title="Monthly Spend by Top Category",
            figure=stacked_area(data_frame=pd.DataFrame()),
        ),
        vm.Graph(
            id="chart-heatmap",
            title="Category × Month Heatmap ($M)",
            figure=spend_heatmap(data_frame=pd.DataFrame()),
        ),
        vm.Graph(
            id="chart-yoy-bar",
            title="Q1 Year-over-Year Comparison",
            figure=yoy_bar(data_frame=pd.DataFrame()),
        ),
    ],
)
