"""Tab 8 — Data Requirements."""
import streamlit as st
from utils.translations import t

_DATA_REQS = [
    {
        "area_en": "FA Equipment Rental ($87.4M)",
        "area_jp": "FA機器リース（$87.4M）",
        "request_en": "Full lease schedule with term dates, monthly payment breakdown, and CapEx vs OpEx classification per asset",
        "request_jp": "各資産のリーススケジュール（契約期間、月次支払い内訳、CapEx/OpEx分類）",
        "source_en": "Finance / Treasury",
        "source_jp": "財務・トレジャリー部門",
        "status": "gap",
        "priority": "High",
    },
    {
        "area_en": "Construction ($42.0M)",
        "area_jp": "建設（$42.0M）",
        "request_en": "Project-level spend breakdown by park, contractor, scope; retro PO rate by project code",
        "request_jp": "パーク別・請負業者別・スコープ別プロジェクト支出; プロジェクトコード別遡及PO率",
        "source_en": "Capital Projects / Engineering",
        "source_jp": "資本プロジェクト・エンジニアリング部門",
        "status": "gap",
        "priority": "High",
    },
    {
        "area_en": "Clothing/Uniforms ($22.8M)",
        "area_jp": "ユニフォーム/衣類（$22.8M）",
        "request_en": "SKU-level uniform spend by department, current vendor contract terms, CINTAS SLA details",
        "request_jp": "部門別SKUユニフォーム支出、現行ベンダー契約条件、CINTAS SLA詳細",
        "source_en": "HR / Operations",
        "source_jp": "人事・オペレーション部門",
        "status": "partial",
        "priority": "High",
    },
    {
        "area_en": "Ride Repair ($11.2M)",
        "area_jp": "ライド修繕（$11.2M）",
        "request_en": "Ride-by-ride maintenance spend; OEM vs aftermarket split; warranty recovery data",
        "request_jp": "ライド別メンテナンス支出; OEM vs アフターマーケット比率; 保証回収データ",
        "source_en": "Tech Services / Maintenance",
        "source_jp": "テクサービス・メンテナンス部門",
        "status": "gap",
        "priority": "Medium",
    },
    {
        "area_en": "PO Justification / Spend w/o Justification",
        "area_jp": "発注理由 / 正当理由なし支出",
        "request_en": "Root cause analysis on '#' justification codes — which cost centers, approvers, and categories have highest incidence",
        "request_jp": "「#」理由コードの根本原因分析 — 最も高い発生率のコストセンター・承認者・カテゴリ",
        "source_en": "Procurement Operations / P2P Team",
        "source_jp": "調達オペレーション・P2Pチーム",
        "status": "partial",
        "priority": "High",
    },
    {
        "area_en": "F&B Cost-per-Unit Pricing",
        "area_jp": "F&B 単価データ",
        "request_en": "Historical unit pricing by SKU per distributor (US Foods, Cheney, Peninsula) to enable cleansheet analysis",
        "request_jp": "ディストリビューター別SKU単価履歴（US Foods、Cheney、Peninsula）によるクリーンシート分析",
        "source_en": "F&B Sourcing / Avendra",
        "source_jp": "F&B調達・Avendra",
        "status": "partial",
        "priority": "High",
    },
    {
        "area_en": "Merchandise COGS Detail",
        "area_jp": "Merch COGS詳細",
        "request_en": "Product-level COGS by country of origin, duty/tariff rates; First Sale vs Landed Cost comparison",
        "request_jp": "原産国別製品レベルCOGS、関税率; First Sale対Landed Costの比較",
        "source_en": "Merchandise Finance",
        "source_jp": "Merch財務部門",
        "status": "ok",
        "priority": "Medium",
    },
    {
        "area_en": "Vendor Master Data Quality",
        "area_jp": "ベンダーマスターデータ品質",
        "request_en": "Deduplicated vendor master with D&B DUNS, NAICS codes, and geographic classification",
        "request_jp": "重複排除されたベンダーマスター（D&B DUNS、NAICSコード、地理的分類付き）",
        "source_en": "ERP / Master Data Management",
        "source_jp": "ERP / マスターデータ管理",
        "status": "gap",
        "priority": "Medium",
    },
]

STATUS_COLOR = {"gap": "🔴", "partial": "🟡", "ok": "🟢"}
PRIORITY_COLOR = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#27ae60"}


def render(lang: str = "en"):
    st.title(f"📂 {t('tab_datareq', lang)}")
    st.caption(t("dr_sub", lang))

    # Summary KPIs
    gaps = sum(1 for d in _DATA_REQS if d["status"] == "gap")
    partials = sum(1 for d in _DATA_REQS if d["status"] == "partial")
    ok = sum(1 for d in _DATA_REQS if d["status"] == "ok")
    high = sum(1 for d in _DATA_REQS if d["priority"] == "High")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🔴 Gaps" if lang == "en" else "🔴 ギャップ", gaps)
    k2.metric("🟡 Partial" if lang == "en" else "🟡 部分対応", partials)
    k3.metric("🟢 Available" if lang == "en" else "🟢 取得済", ok)
    k4.metric("High Priority" if lang == "en" else "高優先度", high)
    st.divider()

    area_key    = "area_en"    if lang == "en" else "area_jp"
    request_key = "request_en" if lang == "en" else "request_jp"
    source_key  = "source_en"  if lang == "en" else "source_jp"

    for req in _DATA_REQS:
        icon = STATUS_COLOR[req["status"]]
        p_color = PRIORITY_COLOR[req["priority"]]
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"#### {icon} {req[area_key]}")
            c2.markdown(
                f"<span style='color:{p_color};font-weight:bold'>{req['priority']} Priority</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{'Request' if lang == 'en' else '依頼内容'}:** {req[request_key]}")
            st.caption(f"{'Source' if lang == 'en' else '情報源'}: {req[source_key]}")
        st.divider()
