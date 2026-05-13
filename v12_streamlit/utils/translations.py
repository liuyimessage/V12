"""EN / JP translation dictionary for V9 Streamlit dashboard."""

T = {
    "en": {
        # App-level
        "app_title": "UDX Spend Analytics",
        "app_subtitle": "800,158 POs · $1,164.7M spend · Jan 2024 – Apr 2026 · Internal review only",
        "draft_badge": "Draft for Review",
        "lang_toggle": "日本語",
        # Sidebar tabs
        "tab_pulse": "Spend Pulse",
        "tab_cat": "Category Intelligence",
        "tab_supplier": "Supplier Intelligence",
        "tab_behavior": "Procurement Behavior",
        "tab_savings": "Savings Opportunity Map",
        "tab_idea": "Idea Generation",
        "tab_bc": "Business Case Builder",
        "tab_datareq": "Data Requirements",
        "tab_assumptions": "Assumptions & README",
        # KPIs
        "kpi_total": "Total Spend",
        "kpi_po": "Total POs",
        "kpi_avg": "Avg PO Value",
        "kpi_yoy": "YoY Change (Q1 2026 vs 2025)",
        "kpi_peak": "Peak Month — Apr 2026",
        # Spend Pulse
        "trend_hdr": "Monthly Spend Trend ($M)",
        "trend_sub": "All categories · Jan 2024 – Apr 2026",
        "stack_hdr": "Spend by Top Categories Over Time ($M)",
        "yoy_hdr": "Q1 Year-over-Year Comparison",
        "col_month": "Month", "col_2025": "2025 ($M)", "col_2026": "2026 ($M)",
        "col_chg": "Change", "col_note": "Note",
        "yoy_footnote": "The Apr 2026 WF lease batch ($46.3M) concentrated 2025 spend artificially. Underlying operational spend is broadly stable.",
        # Category Intel
        "cat_pareto_hdr": "Spend by Category — Pareto View",
        "hm_hdr": "Category × Month Heatmap ($M)",
        "hm_sub": "Color intensity = spend magnitude",
        "cat_gap_hdr": "Category Coverage Gap (WAVE vs Spend)",
        # Supplier Intel
        "pareto_hdr": "Vendor Pareto — Top 30 by Spend ($M)",
        "pareto_sub": "Bars = spend · Line = cumulative %",
        "catrisk_hdr": "Category Supplier Concentration Risk",
        "vtbl_hdr": "Top 30 Vendor Detail",
        "col_vendor": "Vendor", "col_spend": "Spend ($M)", "col_pct": "% Total",
        "col_cum": "Cumul. %", "col_pos": "POs", "col_cats": "Categories", "col_flag": "Risk Flag",
        # Procurement Behavior
        "mav_hdr": "Spend w/o Justification by Category ($M)",
        "mav_sub": "'#' justification share",
        "bundle_hdr": "Demand Consolidation Opportunities",
        "dq_hdr": "Data Quality Signals",
        "col_action": "Recommended Action",
        "col_total_k": "Total ($K)",
        # Savings Map
        "sav_mx_hdr": "Savings Opportunity Matrix — Categories × Levers",
        "wave_hdr": "WAVE Initiatives — Ranked by BP Benefit",
        "col_name": "Initiative", "col_ws": "Workstream", "col_stage": "Stage",
        "col_bp": "BP ($M)", "col_lat": "Latest ($M)", "col_owner": "Owner",
        "lever_comp": "Competitive Sourcing",
        "lever_demand": "Demand Consolidation",
        "lever_spec": "Spec Standardization",
        "lever_contract": "Contract Compliance",
        "lever_process": "Process Reform",
        # Idea Generation
        "idea_title": "AI Procurement Idea Generator",
        "idea_sub": "Ask anything about the UDX procurement landscape — WAVE pipeline, spend gaps, sourcing opportunities, and savings strategies.",
        "idea_ph": "e.g. What categories have no WAVE initiative? Suggest new sourcing ideas for Construction spend.",
        "idea_clear": "Clear Chat",
        # Business Case Builder
        "bc_title": "Business Case Builder",
        "bc_sub": "Describe your initiative; the AI advisor populates an L2-ready Business Case.",
        "bc_demo": "Load Dry RFP Demo",
        "bc_new": "+ New Business Case",
        # Data Requirements
        "dr_title": "Data Requirements",
        "dr_sub": "Track outstanding data requests and blockers.",
        # Assumptions
        "assump_title": "Assumptions & README",
        "assump_sub": "Read before sharing externally.",
        # Status labels
        "status_on_track": "On Track",
        "status_cancelled": "Cancelled",
        "status_on_hold": "On Hold",
        # Generic
        "gap": "Gap",
        "partial": "Partial",
        "covered": "Covered",
        "filter_ws": "Filter by Workstream",
        "filter_stage": "Filter by Stage",
        "all": "All",
        "download_excel": "Download Excel",
        "search": "Search initiatives...",
        "total": "Total",
        "l4_executed": "L4 Executed",
        "l3_planned": "L3 Planned",
    },
    "jp": {
        # App-level
        "app_title": "UDX 購買分析",
        "app_subtitle": "800,158件の発注 · $1,164.7M · 2024年1月〜2026年4月 · 社内レビュー用",
        "draft_badge": "レビュー用草稿",
        "lang_toggle": "English",
        # Sidebar tabs
        "tab_pulse": "支出パルス",
        "tab_cat": "カテゴリ分析",
        "tab_supplier": "サプライヤー分析",
        "tab_behavior": "調達行動",
        "tab_savings": "節約機会マップ",
        "tab_idea": "アイデア創出",
        "tab_bc": "ビジネスケース",
        "tab_datareq": "データ要件",
        "tab_assumptions": "前提条件 & README",
        # KPIs
        "kpi_total": "総支出",
        "kpi_po": "発注総件数",
        "kpi_avg": "平均発注額",
        "kpi_yoy": "前年比（2026年Q1 vs 2025年）",
        "kpi_peak": "ピーク月 — 2026年4月",
        # Spend Pulse
        "trend_hdr": "月次支出トレンド（百万ドル）",
        "trend_sub": "全カテゴリ · 2024年1月 〜 2026年4月",
        "stack_hdr": "上位カテゴリ別支出推移（百万ドル）",
        "yoy_hdr": "Q1 前年比較",
        "col_month": "月", "col_2025": "2025年（百万ドル）", "col_2026": "2026年（百万ドル）",
        "col_chg": "変化", "col_note": "備考",
        "yoy_footnote": "2025年4月のウェルズ・ファーゴ一括リース（$46.3M）が人為的に支出を集中させました。実質的な業務支出は概ね安定しています。",
        # Category Intel
        "cat_pareto_hdr": "カテゴリ別支出 — パレート図",
        "hm_hdr": "カテゴリ×月 ヒートマップ（百万ドル）",
        "hm_sub": "色の濃さ = 支出の大きさ",
        "cat_gap_hdr": "カテゴリカバレッジギャップ（WAVE vs 支出）",
        # Supplier Intel
        "pareto_hdr": "ベンダーパレート — 上位30社（百万ドル）",
        "pareto_sub": "棒グラフ = 支出 · 折れ線 = 累積 %",
        "catrisk_hdr": "カテゴリ別サプライヤー集中リスク",
        "vtbl_hdr": "上位30ベンダー詳細",
        "col_vendor": "ベンダー名", "col_spend": "支出（百万ドル）", "col_pct": "総計比",
        "col_cum": "累積 %", "col_pos": "発注件数", "col_cats": "カテゴリ", "col_flag": "リスクフラグ",
        # Procurement Behavior
        "mav_hdr": "正当理由なし支出（カテゴリ別・百万ドル）",
        "mav_sub": "「#」理由の割合",
        "bundle_hdr": "需要統合の機会",
        "dq_hdr": "データ品質シグナル",
        "col_action": "推奨アクション",
        "col_total_k": "合計（千ドル）",
        # Savings Map
        "sav_mx_hdr": "節約機会マトリクス — カテゴリ × 施策",
        "wave_hdr": "WAVEイニシアティブ — BP順",
        "col_name": "イニシアティブ", "col_ws": "ワークストリーム", "col_stage": "ステージ",
        "col_bp": "BP（百万ドル）", "col_lat": "最新値（百万ドル）", "col_owner": "担当者",
        "lever_comp": "競争調達",
        "lever_demand": "需要統合",
        "lever_spec": "仕様標準化",
        "lever_contract": "契約コンプライアンス",
        "lever_process": "プロセス改革",
        # Idea Generation
        "idea_title": "AI 調達アイデア生成",
        "idea_sub": "UDXの調達状況について何でも聞いてください — WAVEパイプライン、支出ギャップ、調達機会、節約戦略など。",
        "idea_ph": "例：WAVEイニシアティブがないカテゴリは？建設支出の新しい調達アイデアを提案してください。",
        "idea_clear": "チャットをクリア",
        # Business Case Builder
        "bc_title": "ビジネスケース作成",
        "bc_sub": "イニシアティブを説明すると、AIアドバイザーがL2レベルのビジネスケースを作成します。",
        "bc_demo": "Dry RFPデモを読み込む",
        "bc_new": "+ 新規ビジネスケース",
        # Data Requirements
        "dr_title": "データ要件",
        "dr_sub": "未解決のデータリクエストとブロッカーを追跡します。",
        # Assumptions
        "assump_title": "前提条件 & README",
        "assump_sub": "外部共有前に必ずお読みください。",
        # Status labels
        "status_on_track": "進行中",
        "status_cancelled": "キャンセル済",
        "status_on_hold": "保留中",
        # Generic
        "gap": "ギャップ",
        "partial": "部分対応",
        "covered": "対応済",
        "filter_ws": "ワークストリームで絞り込み",
        "filter_stage": "ステージで絞り込み",
        "all": "全て",
        "download_excel": "Excelダウンロード",
        "search": "イニシアティブを検索...",
        "total": "合計",
        "l4_executed": "L4 実行済",
        "l3_planned": "L3 計画済",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Get translated string. Falls back to English if JP key missing."""
    return T.get(lang, T["en"]).get(key, T["en"].get(key, key))
