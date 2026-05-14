"""Tab 4 — Procurement Behavior."""
import pandas as pd
import plotly.express as px
import streamlit as st
from utils.translations import t
from data.vendor_data import MAVERICK, BUNDLING, DQ


def render(lang: str = "en"):
    st.title(f"⚙️ {t('tab_behavior', lang)}")

    # KPIs — matches HTML exactly
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        "Spend w/o Justification — 16.3%" if lang == "en" else "正当理由なし支出 — 16.3%",
        f"${DQ['hash_spend']:.0f}M",
        help="'#' or blank justification" if lang == "en" else "「#」または空白の理由",
    )
    k2.metric(
        "POs with No Justification" if lang == "en" else "理由なし発注件数",
        "N/A",
        help="16.3% of all POs" if lang == "en" else "全発注件数の16.3%",
    )
    k3.metric(
        "Bundling Opportunity" if lang == "en" else "統合機会",
        "$14.7M",
        help="Top 5 consolidation candidates" if lang == "en" else "上位5統合候補",
    )
    k4.metric(
        "Distinct Units of Measure" if lang == "en" else "数量単位バリエーション",
        str(DQ["uom_distinct"]),
        help="UOM fragmentation risk" if lang == "en" else "UOM断片化リスク",
    )
    st.divider()

    # ── Two-column row: Maverick chart (left) | Data Quality (right) ──────────
    # Matches HTML grid-2 layout
    col_mav, col_dq = st.columns(2)

    with col_mav:
        st.subheader(t("mav_hdr", lang))
        st.caption(t("mav_sub", lang))

        df_mav = pd.DataFrame(MAVERICK).sort_values("hash_spend", ascending=True)
        label = (
            "Spend w/o Justification ($M)" if lang == "en"
            else "正当理由なし支出（百万ドル）"
        )
        fig = px.bar(
            df_mav, x="hash_spend", y="cat",
            orientation="h",
            color="hash_pct",
            color_continuous_scale="Reds",
            template="plotly_dark",
            labels={"hash_spend": label, "cat": "", "hash_pct": "% w/o justification"},
            custom_data=["total_spend", "hash_pct"],
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>w/o justification: $%{x:.2f}M<br>"
                "Total: $%{customdata[0]:.2f}M<br>Rate: %{customdata[1]:.1f}%<extra></extra>"
            )
        )
        fig.update_layout(
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_colorbar=dict(title="%"),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dq:
        st.subheader(t("dq_hdr", lang))
        st.markdown(f"**Total PO rows:** {DQ['total_rows']:,}")
        st.markdown(f"**Rows w/o justification:** {DQ['hash_rows']:,} ({DQ['hash_pct']}%)")
        st.markdown(f"**Spend w/o justification:** ${DQ['hash_spend']:.0f}M")
        st.markdown(f"**Distinct UOMs:** {DQ['uom_distinct']}")
        st.markdown("**Top 5 UOMs:**")
        for u in DQ["uom_top"]:
            st.markdown(f"- **{u['uom']}**: {u['count']:,} POs")

    # ── Bundling table (full-width, below the two columns) ────────────────────
    # Matches HTML layout: bundling table is the bottom card
    st.subheader(t("bundle_hdr", lang))
    action_map = {
        "Tech Services":          ("Consolidate to catalog / blanket PO" if lang == "en" else "カタログ/包括PO統合"),
        "Building Maint.":        ("RFP + preferred supplier program" if lang == "en" else "RFP＋優先サプライヤー"),
        "Merch Imports":          ("Vendor consolidation to 3–5 global suppliers" if lang == "en" else "グローバル3〜5社に集約"),
        "Construction":           ("Competitive RFP across parks" if lang == "en" else "パーク横断競争RFP"),
        "ADULT APPAREL":          ("SKU rationalization + volume bundling" if lang == "en" else "SKU整理＋数量バンドル"),
        "Maintenance/Repair":     ("Blanket orders + storeroom consolidation" if lang == "en" else "包括注文＋倉庫統合"),
        "TOYS/PLUSH":             ("SKU reduction + preferred vendor RFP" if lang == "en" else "SKU削減＋優先ベンダーRFP"),
        "Non-Alcoholic Beverage": ("Avendra leverage + Cheney Brothers expansion" if lang == "en" else "Avendra活用＋拡大"),
        "Clothing/Uniforms":      ("Wardrobe RFP + CINTAS expansion" if lang == "en" else "ユニフォームRFP＋CINTAS拡大"),
        "HOME":                   ("SKU rationalization" if lang == "en" else "SKU整理"),
        "ACCESSORIES":            ("SKU consolidation" if lang == "en" else "SKU統合"),
        "Prof. Services":         ("Preferred vendor list" if lang == "en" else "優先ベンダーリスト"),
        "SOUVENIRS":              ("Volume bundling + RFM brands" if lang == "en" else "数量バンドル"),
        "Beef":                   ("Multi-park volume leverage" if lang == "en" else "パーク横断数量交渉"),
        "Ride Repair":            ("Blanket PO + catalog consolidation" if lang == "en" else "包括PO＋カタログ統合"),
    }
    df_bundle = pd.DataFrame([
        {
            ("Category" if lang == "en" else "カテゴリ"): b["cat"],
            t("col_total_k", lang): f"${b['total']/1000:,.0f}K",
            ("Detail" if lang == "en" else "詳細"): b["detail"],
            t("col_action", lang): action_map.get(b["cat"], "Review"),
        }
        for b in BUNDLING
    ])
    st.dataframe(df_bundle, use_container_width=True, hide_index=True)
