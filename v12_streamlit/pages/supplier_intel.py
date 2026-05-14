"""Tab 3 — Supplier Intelligence."""
from collections import defaultdict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.translations import t
from data.vendor_data import PARETO

# ── Risk flag data (matches HTML catRiskPanel) ────────────────────────────────
_RISK_FLAGS = [
    {
        "vendor": "WELLS FARGO EQUIPMENT FINANCE INC + WELLS FARGO EQUIPMEN",
        "spend": 71.08,
        "note_en": "Single-source captive lease — structurally non-RFP-able without CapEx reclassification.",
        "note_jp": "単一調達のキャプティブリース — CapEx再分類なしでは競争調達不可。",
        "risk": "high",
    },
    {
        "vendor": "CARTER LEASING SOLUTIONS LLC",
        "spend": 13.89,
        "note_en": "Captive lease vendor — full dependency. No alternative pricing available.",
        "note_jp": "キャプティブリース — 完全依存。代替価格なし。",
        "risk": "high",
    },
    {
        "vendor": "THE HUNTINGTON NATIONAL BANK",
        "spend": 6.96,
        "note_en": "Captive lease — single-source FA Equipment. Part of $91M non-competitive block.",
        "note_jp": "キャプティブリース — 単一調達FA機器。$91Mの非競争ブロックの一部。",
        "risk": "high",
    },
    {
        "vendor": "US FOODS INC (Interface) + US FOODS INC",
        "spend": 45.71,
        "note_en": "Two US Foods entities: possible duplicate vendor master. Combined spend creates leverage for consolidated RFP.",
        "note_jp": "US Foods 2社：ベンダーマスター重複の可能性。統合RFPによるレバレッジ機会。",
        "risk": "medium",
    },
    {
        "vendor": "INTAMIN LTD",
        "spend": 23.04,
        "note_en": "Single-cat (Tech Services). 957 POs — high fragmentation. OEM dependency for ride systems.",
        "note_jp": "単一カテゴリ（テクサービス）。957件発注 — 高度に分散。ライドシステムのOEM依存。",
        "risk": "medium",
    },
    {
        "vendor": "MOTION INDUSTRIES INC",
        "spend": 18.84,
        "note_en": "7,353 POs — highest PO count in top 30. Catalog migration opportunity to reduce transaction cost.",
        "note_jp": "7,353件発注 — 上位30社中最多。カタログ移行でトランザクションコスト削減機会。",
        "risk": "medium",
    },
    {
        "vendor": "TRI-CAN INC",
        "spend": 20.24,
        "note_en": "Poultry single-source. 3 POs for $20.2M — extreme concentration. Competitive RFP recommended.",
        "note_jp": "家禽の単一調達。3件で$20.2M — 極度の集中。競争RFP推奨。",
        "risk": "high",
    },
]


def render(lang: str = "en"):
    st.title(f"🏭 {t('tab_supplier', lang)}")

    # KPIs — matches HTML exactly
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Vendors Cover 50% of Spend" if lang == "en" else "支出の50%をカバーするベンダー数",
        "28",
        help="Out of 1,800+ total vendors" if lang == "en" else "1,800社以上のうち",
    )
    k2.metric(
        "Captive Lease Vendors" if lang == "en" else "キャプティブリースベンダー",
        "$91.0M",
        help="WF + Carter + Huntington + Trilogy" if lang == "en" else "WF＋Carter＋Huntington＋Trilogy",
    )
    k3.metric(
        "Single-Category Vendors in Top 30" if lang == "en" else "単一カテゴリ上位30社",
        "7",
    )
    k4.metric(
        "Top Vendor Share" if lang == "en" else "最大ベンダーシェア",
        "15.6%",
        help="Wells Fargo Equipment Finance" if lang == "en" else "ウェルズ・ファーゴ機器ファイナンス",
    )
    st.divider()

    # ── Vendor Pareto (full-width) ─────────────────────────────────────────────
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
    st.caption(
        "🔴 Red = single-category vendors (highest dependency risk)" if lang == "en"
        else "🔴 赤 = 単一カテゴリベンダー（依存リスク最高）"
    )

    # ── Two-column row: Cat Risk chart (left) | Risk Flags (right) ───────────
    # Matches HTML grid-2 below the pareto
    col_risk, col_flags = st.columns(2)

    with col_risk:
        st.subheader(
            "Category Supplier Concentration Risk" if lang == "en"
            else "カテゴリ別サプライヤー集中リスク"
        )
        st.caption(
            "Spend ($M) per category · top vendors in dataset" if lang == "en"
            else "カテゴリ別支出（$M）· 上位ベンダー"
        )
        # Compute spend by category from PARETO
        cat_spend: dict[str, float] = defaultdict(float)
        cat_vendor_count: dict[str, int] = defaultdict(int)
        for p in PARETO:
            for cat in p["cats"]:
                cat_spend[cat] += p["spend"]
                cat_vendor_count[cat] += 1

        cats_sorted = sorted(cat_spend.keys(), key=lambda c: -cat_spend[c])
        fig_cat = go.Figure(go.Bar(
            x=[cat_spend[c] for c in cats_sorted],
            y=cats_sorted,
            orientation="h",
            marker=dict(
                color=[cat_vendor_count[c] for c in cats_sorted],
                colorscale="RdYlGn_r",
                showscale=True,
                colorbar=dict(title="# vendors"),
            ),
            hovertemplate="<b>%{y}</b><br>Spend: $%{x:.1f}M<extra></extra>",
        ))
        fig_cat.update_layout(
            template="plotly_dark",
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title="Spend ($M)", gridcolor="#2a2f40"),
            yaxis=dict(gridcolor="#2a2f40"),
            height=420,
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_flags:
        st.subheader(
            "Single-Source & Dependency Risk Flags" if lang == "en"
            else "シングルソース・依存リスクフラグ"
        )
        note_key = "note_en" if lang == "en" else "note_jp"
        risk_color = {"high": "#c0392b", "medium": "#e67e22"}
        risk_label = {
            "high": {"en": "🔴 High Risk", "jp": "🔴 高リスク"},
            "medium": {"en": "🟡 Medium", "jp": "🟡 中リスク"},
        }
        lk = "en" if lang == "en" else "jp"
        for flag in _RISK_FLAGS:
            col = risk_color[flag["risk"]]
            lbl = risk_label[flag["risk"]][lk]
            st.markdown(
                f"<div style='border-left:3px solid {col};padding:8px 12px;margin-bottom:8px;"
                f"background:#13182a;border-radius:0 6px 6px 0'>"
                f"<div style='font-size:12px;font-weight:600;color:#e0e6ff'>{flag['vendor']}</div>"
                f"<div style='font-size:11px;color:#8090b0;margin:2px 0'>{flag[note_key]}</div>"
                f"<div style='font-size:11px;color:{col};font-weight:600'>{lbl} · ${flag['spend']:.1f}M</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── Vendor detail table (full-width) ──────────────────────────────────────
    st.subheader(t("vtbl_hdr", lang))
    df = pd.DataFrame([
        {
            t("col_vendor", lang): p["vendor"],
            t("col_spend", lang): p["spend"],
            t("col_pct", lang): f"{p['pct']}%",
            t("col_cum", lang): f"{p['cum_pct']}%",
            t("col_pos", lang): f"{p['po_count']:,}",
            t("col_cats", lang): ", ".join(p["cats"]),
            t("col_flag", lang): (
                ("⚠️ Single-cat" if lang == "en" else "⚠️ 単一カテゴリ")
                if p["single_cat"] else "✅"
            ),
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
