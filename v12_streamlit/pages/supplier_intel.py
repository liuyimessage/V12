"""Tab 3 — Supplier Intelligence."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.vendor_data import PARETO


def render(lang: str = "en"):
    st.title(f"🏭 {t('tab_supplier', lang)}")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("28" if lang == "en" else "28社", "50% of Spend" if lang == "en" else "支出の50%")
    k2.metric("Captive Lease Vendors" if lang == "en" else "キャプティブリース", "4 vendors — $91M")
    k3.metric("Single-Cat in Top 30" if lang == "en" else "単一カテゴリ上位30社", "30 / 30")
    k4.metric("Top Vendor Share" if lang == "en" else "最大ベンダーシェア", "5.5%")
    st.divider()

    # ── Vendor Pareto ─────────────────────────────────────────────────────────
    st.subheader(t("pareto_hdr", lang))
    st.caption(t("pareto_sub", lang))

    vendors = [p["vendor"][:30] for p in PARETO]
    spends  = [p["spend"] for p in PARETO]
    cums    = [p["cum_pct"] for p in PARETO]
    colors  = ["#e74c3c" if p["single_cat"] else "#4f8ef7" for p in PARETO]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vendors, y=spends, name="Spend ($M)",
        marker_color=colors, yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=vendors, y=cums, name="Cumul. %",
        mode="lines+markers", yaxis="y2",
        line=dict(color="#ffcc00", width=2),
    ))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
        yaxis=dict(title="Spend ($M)", gridcolor="#2a2f40"),
        yaxis2=dict(title="Cumul. %", overlaying="y", side="right",
                    range=[0, 50], showgrid=False),
        xaxis=dict(tickangle=-60, tickfont=dict(size=9)),
        legend=dict(orientation="h", y=1.05),
        margin=dict(l=10, r=10, t=30, b=120),
        hovermode="x unified",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔴 Red = single-category vendors (highest dependency risk)" if lang == "en"
               else "🔴 赤 = 単一カテゴリベンダー（依存リスク最高）")

    # ── Vendor detail table ───────────────────────────────────────────────────
    st.subheader(t("vtbl_hdr", lang))
    df = pd.DataFrame([
        {
            t("col_vendor", lang): p["vendor"],
            t("col_spend", lang): p["spend"],
            t("col_pct", lang): f"{p['pct']}%",
            t("col_cum", lang): f"{p['cum_pct']}%",
            t("col_pos", lang): f"{p['po_count']:,}",
            t("col_cats", lang): ", ".join(p["cats"]),
            t("col_flag", lang): ("⚠️ Single-cat" if lang == "en" else "⚠️ 単一カテゴリ") if p["single_cat"] else "✅",
        }
        for p in PARETO
    ])
    st.dataframe(
        df.style.background_gradient(
            subset=[t("col_spend", lang)], cmap="Blues"
        ),
        use_container_width=True,
        hide_index=True,
    )
