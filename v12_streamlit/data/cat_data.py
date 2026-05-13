"""Category Pareto and coverage gap data."""

CAT_LABELS = ["Tech Services","FA Equip. Rental","Building Maint.","Merch Imports",
               "Construction","ADULT APPAREL","Maintenance/Repair","TOYS/PLUSH",
               "Non-Alcoholic Beverage","Clothing/Uniforms"]
CAT_SPEND   = [249.3, 87.4, 68.9, 62.6, 42.0, 35.8, 35.2, 30.1, 23.8, 22.8]

TOTAL_SPEND = 1164.7
TOTAL_POS   = 800158
AVG_PO      = 1456

CAT_GAP = [
    {"cat":"FA Equip. Rental ($87.4M)","wave":None,"status":"gap",
     "note_en":"Lease payment streams — no WAVE initiative. CapEx reclassification is the priority action.",
     "note_jp":"リース契約 — WAVEなし。CapEx再分類が優先アクション。"},
    {"cat":"Building Maint. ($68.9M)","wave":"Preferred Supplier Program (Facilities) $5.36M","status":"ok",
     "note_en":"Facilities WAVE exists. Construction and MRO subcategory coverage still needed.",
     "note_jp":"Facilities WAVEあり。建設・MROカテゴリのカバレッジが依然として必要。"},
    {"cat":"Construction ($42.0M)","wave":None,"status":"gap",
     "note_en":"No WAVE initiative — $42M, largest uncovered spend category.",
     "note_jp":"WAVEなし — $42M、最大の未カバーカテゴリ"},
    {"cat":"Maintenance/Repair ($35.2M)","wave":None,"status":"gap",
     "note_en":"No WAVE coverage — demand consolidation and competitive sourcing opportunity.",
     "note_jp":"WAVEカバレッジなし — 需要統合と競争調達の機会"},
    {"cat":"Clothing/Uniforms ($22.8M)","wave":None,"status":"gap",
     "note_en":"No WAVE coverage — Clothing/Uniforms (wardrobe) is distinct from Merch Apparel.",
     "note_jp":"WAVEカバレッジなし — ユニフォームはMerch Apparelとは別カテゴリ"},
    {"cat":"Prof. Services ($18.8M)","wave":"D&T Consulting only — $3.60M","status":"partial",
     "note_en":"D&T consulting covered — general professional services uncovered.",
     "note_jp":"D&TコンサルのみD&T($3.60M) — 一般プロフサービスは未対応"},
    {"cat":"Ride Repair ($11.2M)","wave":None,"status":"gap",
     "note_en":"No WAVE coverage — competitive RFP opportunity.",
     "note_jp":"WAVEカバレッジなし — 競争RFP機会"},
    {"cat":"Merchandise (COGS)","wave":"14 active WAVE initiatives — $24.5M L3 BP · $15.9M L4 executed","status":"ok",
     "note_en":"Strong WAVE coverage across all sub-categories: Apparel, Plush, Accessories, Home, Souvenirs, Toys, Candy.",
     "note_jp":"Merch Apparel・Plush・Accessories・Home・Souvenirs・Toys・Candy全カテゴリにWAVEあり。"},
]

SAV_MATRIX = {
    "levers_en": ["Competitive Sourcing","Demand Consolidation","Spec Standardization","Contract Compliance","Process Reform"],
    "levers_jp": ["競争調達","需要統合","仕様標準化","契約コンプライアンス","プロセス改革"],
    "rows": [
        {"cat":"FA Equip. Rental ($87.4M)","cells":[
            {"t":"gap","en":"Gap — Lease captive, RFP not possible","jp":"ギャップ — リース拘束"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},{"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — No contract register","jp":"ギャップ — 契約なし"},
            {"t":"wave","en":"CapEx reclassification (Priority #1)","jp":"CapEx再分類（優先#1）"},
        ]},
        {"cat":"Building Maint. ($68.9M)","cells":[
            {"t":"wave","en":"Preferred Supplier Program $5.36M","jp":"優先サプライヤー $5.36M"},
            {"t":"wave","en":"Consolidation: JK2/Slalom/Flow $22M+","jp":"統合機会: JK2/Slalom $22M+"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — Retro PO rate 34.2%","jp":"ギャップ — 遡及PO率34.2%"},
            {"t":"wave","en":"PO reform — Vroozi configuration","jp":"PO改革 — Vroozi設定変更"},
        ]},
        {"cat":"Construction ($42.0M)","cells":[
            {"t":"partial","en":"Partial — USJ construction RFP only","jp":"部分 — USJ建設RFPのみ"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},{"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — Retro PO is primary issue","jp":"ギャップ — 遡及POが主要問題"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
        ]},
        {"cat":"Maintenance/Repair ($35.2M)","cells":[
            {"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"wave","en":"VERITIV 3,590 small POs — bundle opp.","jp":"VERITIV 小口PO統合"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — 44.4% # justification","jp":"ギャップ — 44.4%が「#」"},
            {"t":"partial","en":"Partial — catalog consolidation","jp":"部分 — カタログ統合"},
        ]},
        {"cat":"Clothing/Uniforms ($22.8M)","cells":[
            {"t":"gap","en":"Gap — no Wardrobe WAVE initiative","jp":"ギャップ — Wardrobe WAVEなし"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — distinct from Merch Apparel","jp":"ギャップ — Merch Apparelとは別"},
            {"t":"gap","en":"Gap — 48.7% # justification","jp":"ギャップ — 48.7%が「#」"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
        ]},
        {"cat":"Prof. Services ($18.8M)","cells":[
            {"t":"wave","en":"D&T Strategic Consulting $3.60M","jp":"D&T戦略コンサル $3.60M"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},{"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap — 66.4% # justification","jp":"ギャップ — 66.4%が「#」"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},
        ]},
        {"cat":"Ride Repair ($11.2M)","cells":[
            {"t":"gap","en":"Gap — No competitive sourcing","jp":"ギャップ"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},{"t":"gap","en":"Gap","jp":"ギャップ"},
            {"t":"gap","en":"Gap","jp":"ギャップ"},{"t":"gap","en":"Gap","jp":"ギャップ"},
        ]},
        {"cat":"Merchandise (COGS)","cells":[
            {"t":"wave","en":"Global Vendor Diversif. $6.65M + First Sale $7.92M","jp":"Global Vendor多様化 $6.65M + First Sale $7.92M"},
            {"t":"wave","en":"Plush / Accessories / Home SKU consolidation","jp":"Plush・Accessories SKU統合"},
            {"t":"wave","en":"Merch Apparel Enhanced Sourcing $5.17M","jp":"Merch Apparel強化調達 $5.17M"},
            {"t":"partial","en":"Partial — cost compliance tracking needed","jp":"部分 — コスト遵守追跡が必要"},
            {"t":"wave","en":"Tariff mitigation — Apparel/Toys/Plush/Souvenirs","jp":"関税緩和交渉"},
        ]},
    ],
}
