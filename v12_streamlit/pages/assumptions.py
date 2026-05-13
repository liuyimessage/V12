"""Tab 9 — Assumptions & README."""
import streamlit as st
from utils.translations import t

_ASSUMPTIONS_EN = [
    {
        "section": "Data Scope",
        "items": [
            "Source: UDX enterprise ERP export — 800,158 PO line items, Jan 2024 – Apr 2026.",
            "Total addressable spend: $1,164.7M (all PO categories, all parks including USH, USJ, UOPB).",
            "Data extracted by the UDX Procurement Analytics team; last refresh: May 2026.",
            "Apr 2026 data is partial (cut-off date mid-month); the $160M spike reflects a multi-park FA Equipment lease batch.",
        ],
    },
    {
        "section": "Spend Classification",
        "items": [
            "'Clothing/Uniforms' ($22.8M) = operational wardrobe / employee uniforms. "
            "Completely separate from 'Merch Apparel' which is COGS merchandise sold to guests.",
            "'FA Equipment Rental' = Fixed Asset lease payments (Wells Fargo, Carter Leasing, Huntington, Trilogy). "
            "These are structurally non-RFP-able without CapEx reclassification.",
            "'Spend w/o Justification' = POs where the justification field contains '#' (system placeholder). "
            "Not necessarily fraudulent — often a Vroozi system configuration issue.",
            "Merch categories (ADULT APPAREL, TOYS/PLUSH, HOME, ACCESSORIES, SOUVENIRS) are distinct merchandise COGS lines, "
            "not operational procurement categories.",
        ],
    },
    {
        "section": "WAVE Data",
        "items": [
            "WAVE data sourced from the WAVE_List_May-8-2026.xlsx as provided by the Procurement team.",
            "Total WAVE initiatives in scope: 107 active (L0–L4 + Sprint), 3 cancelled.",
            "L4 'executed' savings: sum of 'latest' column for all L4 On-Track initiatives = $28.1M.",
            "L3 'planned' savings: sum of 'bp' column for all L3 On-Track initiatives = $59.6M.",
            "Recurring Benefit for Dry Foods RFP (#63296): $870K per WAVE data; baseline $8.73M from Dry_input.xlsx.",
        ],
    },
    {
        "section": "Analytical Methodology",
        "items": [
            "Vendor Pareto: top 30 vendors ranked by total spend, cumulative % calculated on $1,164.7M base.",
            "Category Pareto: spend aggregated by ERP category code, top 10 shown.",
            "Savings Opportunity Matrix: manual cross-reference of WAVE initiatives vs spend categories and strategic levers.",
            "Category Gap analysis: categories with >$10M spend and no direct WAVE initiative flagged as 'Gap'.",
            "YoY comparison: Q1 2025 vs Q1 2026 using Jan–Mar months only to avoid Apr 2026 batch distortion.",
        ],
    },
    {
        "section": "Key Limitations",
        "items": [
            "This dashboard uses embedded data snapshots — it is not connected to a live ERP system.",
            "Vendor name deduplication is partial; some vendors appear under multiple names (e.g. 'Wells Fargo Equipment Finance' vs 'Wells Fargo Equipmen').",
            "F&B cost-per-unit pricing is not available in this dataset; cleansheet analysis requires additional data pull.",
            "Construction and Ride Repair spend cannot be fully attributed to WAVE initiatives without project-code-level data.",
            "Japanese translations were generated with AI assistance — verify accuracy before presenting to Japanese stakeholders.",
        ],
    },
    {
        "section": "Distribution",
        "items": [
            "DRAFT — for internal review only. Do not distribute externally without Procurement leadership approval.",
            "Confidential — contains vendor pricing and spend data subject to NDA.",
        ],
    },
]

_ASSUMPTIONS_JP = [
    {
        "section": "データスコープ",
        "items": [
            "データソース: UDX企業ERPエクスポート — 800,158件の発注明細、2024年1月〜2026年4月。",
            "総対象支出: $1,164.7M（全カテゴリ、USH・USJ・UOPBを含む全パーク）。",
            "UDX調達分析チームがデータを抽出; 最終更新: 2026年5月。",
            "2026年4月データは月中カットオフのため部分的; $160MのスパイクはマルチパークのFA機器リース一括支払いを反映。",
        ],
    },
    {
        "section": "支出分類",
        "items": [
            "「Clothing/Uniforms」（$22.8M）= 業務用ユニフォーム/衣類。ゲスト向けCOGSのMerch Apparelとは完全に別カテゴリ。",
            "「FA Equipment Rental」= 固定資産リース支払い（Wells Fargo、Carter Leasing等）。CapEx再分類なしでは競争調達不可。",
            "「正当理由なし支出」= 理由欄が「#」の発注（システムプレースホルダー）。不正とは限らず、Vroozi設定の問題が多い。",
            "MerchカテゴリはCOGSとして別管理; 業務調達カテゴリではない。",
        ],
    },
    {
        "section": "WAVEデータ",
        "items": [
            "WAVEデータ: 調達チーム提供のWAVE_List_May-8-2026.xlsx。",
            "対象イニシアティブ数: アクティブ107件（L0〜L4＋Sprint）、キャンセル3件。",
            "L4実行済節約: L4 On-Trackイニシアティブの最新値合計 = $28.1M。",
            "L3計画済節約: L3 On-TrackイニシアティブのBP合計 = $59.6M。",
            "Dry Foods RFP（#63296）の継続的便益: WAVEデータより$870K; ベースライン$8.73M (Dry_input.xlsx)。",
        ],
    },
    {
        "section": "分析手法",
        "items": [
            "ベンダーパレート: 上位30社を総支出順にランク付け、累積%は$1,164.7Mベースで計算。",
            "カテゴリパレート: ERPカテゴリコード別に集計、上位10カテゴリを表示。",
            "節約機会マトリクス: WAVEイニシアティブと支出カテゴリ・戦略施策の手動クロスリファレンス。",
            "カテゴリギャップ分析: $10M超の支出でWAVEイニシアティブのないカテゴリを「ギャップ」としてフラグ。",
            "前年比較: 4月スパイクの歪みを避けるため1〜3月のみで比較。",
        ],
    },
    {
        "section": "主な制限事項",
        "items": [
            "このダッシュボードは組み込みデータスナップショットを使用; ライブERPシステムには接続されていません。",
            "ベンダー名の重複排除は部分的。",
            "F&B単価データは非公開; クリーンシート分析には追加データが必要。",
            "建設・ライド修繕は追加データなしでWAVEイニシアティブへの完全な帰属不可。",
            "日本語翻訳はAI支援; 日本語話者への提示前に正確性を確認してください。",
        ],
    },
    {
        "section": "配布",
        "items": [
            "草稿 — 社内レビューのみ。調達リーダーシップの承認なしに外部配布禁止。",
            "機密情報 — NDの対象となるベンダー価格・支出データを含む。",
        ],
    },
]


def render(lang: str = "en"):
    st.title(f"📝 {t('tab_assumptions', lang)}")
    st.caption(t("assump_sub", lang))

    sections = _ASSUMPTIONS_JP if lang == "jp" else _ASSUMPTIONS_EN

    for sec in sections:
        st.subheader(sec["section"])
        for item in sec["items"]:
            st.markdown(f"- {item}")
        st.divider()
