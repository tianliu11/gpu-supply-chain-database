#!/usr/bin/env python3
"""Build an evidence-audited extension of the submitted full GPU supply-chain graph.

The script deliberately separates four different claims:

1. a relationship appears in the submitted graph;
2. a reputable source supports the relationship at an exact or category level;
3. a company is publicly documented as capable of supplying a category; and
4. a public production site exists for that company.

It never converts a category-level source into a claim that a named factory supplies a
particular NVIDIA product.  Those allocations are normally confidential.
"""

from __future__ import annotations

import csv
import json
import math
import re
import hashlib
from collections import Counter, defaultdict, deque
from pathlib import Path

from additional_public_research import SOURCES as RESEARCH_SOURCES, VENDORS as RESEARCH_VENDORS
from additional_public_research import SITES as RESEARCH_SITES, EDGE_EVIDENCE, REVIEW_DATE
from additional_public_research import CORPORATE_GROUPS
import expanded_public_research  # registers explicitly reviewed second-pass evidence
import component_definition_research  # scoped definitions and fourth-pass evidence
import process_validation_research
import remaining_public_research


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
INPUT_JSON = RAW / "gpu_complete_node_to_node_supply_chain.json"


SOURCE_ADDITIONS = [
    {
        "source_id": "SRC_SIA_PROCESS",
        "organization": "Semiconductor Industry Association",
        "title": "How Are Semiconductors Made?",
        "url": "https://www.semiconductors.org/semiconductors-101/how-are-semiconductors-made/",
        "use": "Authoritative high-level sequence from wafer fabrication through packaging and circuit-board installation",
        "reliability": "Industry association; category-level process evidence, not a product recipe",
    },
    {
        "source_id": "SRC_SIA_FRONTEND",
        "organization": "Semiconductor Industry Association",
        "title": "Stage 3: Front-end Manufacturing",
        "url": "https://www.semiconductors.org/semiconductors-101/how-are-semiconductors-made/stage-3-front-end-manufacturing/",
        "use": "Photolithography, deposition, doping, etch and CMP process/material roles",
        "reliability": "Industry association; category-level process evidence",
    },
    {
        "source_id": "SRC_EPA_SEMI",
        "organization": "U.S. Environmental Protection Agency",
        "title": "Semiconductor Industry",
        "url": "https://www.epa.gov/eps-partnership/semiconductor-industry",
        "use": "Use of fluorinated gases, NF3 and nitrous oxide in semiconductor etch, deposition-chamber cleaning and CVD",
        "reliability": "U.S. government source; supports process use, not supplier allocation",
    },
    {
        "source_id": "SRC_USGS_MCS2026",
        "organization": "U.S. Geological Survey",
        "title": "Mineral Commodity Summaries 2026",
        "url": "https://doi.org/10.3133/mcs2026",
        "use": "Raw-mineral definitions, production, reserves, trade and industry structure",
        "reliability": "U.S. government commodity reference; does not by itself prove every chemical conversion edge",
    },
    {
        "source_id": "SRC_IPC_PCB",
        "organization": "IPC",
        "title": "Controlling Moisture in Printed Circuit Boards",
        "url": "https://www.ipc.org/system/files/technical_resource/E6%26S01_01.pdf",
        "use": "FR-4 PCB construction using laminate, prepreg, copper foil, copper plating and solder mask",
        "reliability": "Electronics manufacturing standards association technical resource",
    },
    {
        "source_id": "SRC_TE_PCIE_MATERIALS",
        "organization": "TE Connectivity",
        "title": "PCIe Gen 4 Connector Product Flyer",
        "url": "https://www.te.com/content/dam/te-com/documents/consumer-devices/global/pcie-gen-4-connector-ecard.pdf",
        "use": "PCIe connector housing and contact material composition",
        "reliability": "Official manufacturer product document; exact connector family, not every GPU card",
    },
    {
        "source_id": "SRC_MURATA_MLCC_MATERIALS",
        "organization": "Murata Manufacturing",
        "title": "Heat Treatment Technology",
        "url": "https://corporate.murata.com/en-sg/technology/technology-platform/production-technology/heat-treatment",
        "use": "BaTiO3/ferrite ceramic powders and Ni/Ag/Cu metal powders used in electronic components including MLCCs",
        "reliability": "Official component-manufacturer technical page",
    },
    {
        "source_id": "SRC_TDK_INDUCTOR_MATERIALS",
        "organization": "TDK",
        "title": "Power Inductors VLS Series",
        "url": "https://product.tdk.com/en/techlibrary/productoverview/inductors_vls.html",
        "use": "Ferrite or metallic magnetic core materials used in wire-wound power inductors",
        "reliability": "Official component-manufacturer technical page",
    },
    {
        "source_id": "SRC_INFINEON_FOOTPRINT_2026",
        "organization": "Infineon Technologies",
        "title": "FY2026 Q4 company presentation—global manufacturing locations",
        "url": "https://www.infineon.com/assets/row/public/documents/corporate/company/fy2026-q4-web-en.pdf",
        "use": "Public list of frontend and backend manufacturing cities",
        "reliability": "Official company publication; does not allocate a specific GPU power-stage order to a site",
    },
    {
        "source_id": "SRC_NEXPERIA_LOCATIONS",
        "organization": "Nexperia",
        "title": "Worldwide locations",
        "url": "https://www.nexperia.com/about/worldwide-locations/",
        "use": "Public list of wafer fabs and assembly centers",
        "reliability": "Official company page; product-to-site allocation is not stated",
    },
    {
        "source_id": "SRC_OURAIRPORTS",
        "organization": "OurAirports",
        "title": "Open airport data",
        "url": "https://ourairports.com/data/",
        "use": "Coordinates and scheduled-service flag for nearest-commercial-airport calculations",
        "reliability": "Public-domain community dataset; proximity is not proof of cargo service",
    },
    {
        "source_id": "SRC_NGA_WPI",
        "organization": "U.S. National Geospatial-Intelligence Agency",
        "title": "World Port Index",
        "url": "https://msi.nga.mil/Publications/WPI",
        "use": "Port names and coordinates for nearest-port calculations",
        "reliability": "Government port index; proximity is not proof of a booked route or suitable service",
    },
]


# Direct alignment between the submitted node IDs and ETO categories.  These are
# category equivalences, not claims that every sub-ingredient has the same vendors.
ETO_NODE_MAP = {
    "LD:packaging_materials": "N100",
    "LD:substrates": "N96",
    "LD:cmp_materials": "N90",
    "LD:electronic_gases": "N91",
    "LD:wafer": "N26",
    "LD:wet_chemicals": "N92",
    "LD:photoresists": "N31",
    "LD:photomasks": "N33",
    "LD:deposition_materials": "N88",
    "LD:lead_frames": "N93",
    "LD:bond_wires": "N94",
    "LD:encapsulation_resins": "N97",
    "LD:die_attach_materials": "N98",
    "PM-SI-WAFER": "N26",
}


# Publicly listed production sites added beyond the repository's existing facility
# table. Coordinates are city-level centroids unless a full address is available.
# A city coordinate supports hub screening, not operational route selection.
EXTRA_FACILITIES = [
    # Compeq factories from the official plant page.
    ("COMPEQ_LUZHU", "Compeq Luzhu Plant", "Compeq", "Taiwan", "Luzhu, Taoyuan", "No. 91, Ln. 814, Daxin Rd., Luzhu Dist., Taoyuan", 25.095, 121.262, "PCB factory", "HDI, multilayer and rigid PCB", "SRC_COMPEQ_PLANTS"),
    ("COMPEQ_HUIZHOU", "Compeq Huizhou Plant", "Compeq", "China", "Huizhou, Guangdong", "168 Huguang Rd., Huzhen, Boluo County, Huizhou", 23.174, 114.284, "PCB factory", "HDI and multilayer PCB", "SRC_COMPEQ_PLANTS"),
    ("COMPEQ_DAYUAN", "Compeq Dayuan Plant", "Compeq", "Taiwan", "Dayuan, Taoyuan", "275 Zhongshan N. Rd., Dayuan Dist., Taoyuan", 25.064, 121.200, "PCB factory", "High-end HDI PCB", "SRC_COMPEQ_PLANTS"),
    ("COMPEQ_SUZHOU", "Compeq Suzhou Plant", "Compeq", "China", "Suzhou, Jiangsu", "428 Xinglong St., Suzhou Industrial Park", 31.318, 120.686, "electronics assembly factory", "Surface-mount and module assembly", "SRC_COMPEQ_PLANTS"),
    ("COMPEQ_CHONGQING", "Compeq Chongqing Plant", "Compeq", "China", "Fuling, Chongqing", "21 Panlong Rd., Lidu, Fuling District, Chongqing", 29.704, 107.395, "PCB factory", "High-end HDI and multilayer PCB", "SRC_COMPEQ_PLANTS"),
    ("COMPEQ_THAILAND", "Compeq Thailand Plant", "Compeq", "Thailand", "Bang Bo, Samut Prakan", "999 Moo 9, Ban Rakat, Bang Bo, Samut Prakan", 13.574, 100.835, "PCB factory", "HDI and multilayer PCB", "SRC_COMPEQ_PLANTS"),
    # GBM/Lincstech production sites; offices and warehouse excluded.
    ("GBM_SHENZHEN", "GBM Shenzhen PCB Site", "Global Brands Manufacture", "China", "Shenzhen, Guangdong", "Yinhai Industrial Area, Yuanshan St., Shenzhen", 22.555, 114.104, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_HUANGJIANG", "GBM Huangjiang Plant", "Global Brands Manufacture", "China", "Dongguan, Guangdong", "YueYuen Industrial Estate, Huangjiang, Dongguan", 22.915, 114.009, "PCB/EMS factory", "PCB and electronics manufacturing services", "SRC_GBM_SITES"),
    ("GBM_CHONGQING", "GBM Chongqing PCB Site", "Global Brands Manufacture", "China", "Yongchuan, Chongqing", "Building 15, No. 6 Tanguan Rd., Yongchuan", 29.357, 105.927, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_ELNA_NAGAHAMA", "ELNA Printed Circuits Nagahama", "Global Brands Manufacture", "Japan", "Nagahama, Shiga", "30 Tamachi, Nagahama, Shiga 529-0142", 35.381, 136.268, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_ELNA_PENANG", "ELNA PCB Malaysia", "Global Brands Manufacture", "Malaysia", "Prai, Penang", "Plot 558, Lorong Perusahaan 4, Prai Industrial Estate", 5.389, 100.403, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_LINCSTECH_SHIMODATE", "Lincstech Shimodate Plant", "Global Brands Manufacture", "Japan", "Chikusai, Ibaraki", "1500 Ogawa, Chikusai, Ibaraki", 36.307, 139.983, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_LINCSTECH_ISHIOKA", "Lincstech Ishioka Plant", "Global Brands Manufacture", "Japan", "Ishioka, Ibaraki", "4-5 Kashiwabara, Ishioka, Ibaraki", 36.190, 140.278, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_LINCSTECH_IIDA", "Lincstech Iida Plant", "Global Brands Manufacture", "Japan", "Shimojo, Nagano", "1608 Hisawa, Shimojo, Nagano", 35.397, 137.786, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_LINCSTECH_SG", "Lincstech Circuit Singapore", "Global Brands Manufacture", "Singapore", "Singapore", "32 Loyang Way, Singapore", 1.370, 103.969, "PCB factory", "Printed circuit boards", "SRC_GBM_SITES"),
    ("GBM_KUNSHAN", "GBM Kunshan EMS Plant", "Global Brands Manufacture", "China", "Kunshan, Jiangsu", "888 Jinshajiang Rd., Kunshan", 31.386, 120.981, "electronics assembly factory", "Electronics manufacturing services", "SRC_GBM_SITES"),
    ("GBM_MALAYSIA", "GBM Malaysia EMS Plant", "Global Brands Manufacture", "Malaysia", "Chemor, Perak", "No. 5 Jalan Klebang 1/5, Chemor, Perak", 4.721, 101.119, "electronics assembly factory", "Electronics manufacturing services", "SRC_GBM_SITES"),
    ("GBM_HUKOU", "GBM Hukou EMS Plant", "Global Brands Manufacture", "Taiwan", "Hukou, Hsinchu", "12 Shijian Rd., Hukou Township, Hsinchu", 24.902, 121.044, "electronics assembly factory", "Electronics manufacturing services", "SRC_GBM_SITES"),
    ("GBM_SUZHOU", "GBM Suzhou EMS Plant", "Global Brands Manufacture", "China", "Suzhou, Jiangsu", "183 Jinfeng Rd., Suzhou New District", 31.300, 120.578, "electronics assembly factory", "Electronics manufacturing services", "SRC_GBM_SITES"),
    ("GBM_WUHU", "GBM Wuhu EMS Plant", "Global Brands Manufacture", "China", "Wuhu, Anhui", "108 Huajin South Rd., Yijiang District, Wuhu", 31.327, 118.376, "electronics assembly factory", "Electronics manufacturing services", "SRC_GBM_SITES"),
    # SUNON production bases.
    ("SUNON_KAOHSIUNG", "SUNON Kaohsiung Factory", "SUNON", "Taiwan", "Kaohsiung", "Kaohsiung, Taiwan", 22.627, 120.301, "fan/motor factory", "Fans, motors and thermal modules", "SRC_SUNON"),
    ("SUNON_KUNSHAN", "SUNON Kunshan Factory", "SUNON", "China", "Kunshan, Jiangsu", "Kunshan, Jiangsu, China", 31.385, 120.981, "fan/motor factory", "Fans, motors and thermal modules", "SRC_SUNON"),
    ("SUNON_BEIHAI", "SUNON Beihai Factory", "SUNON", "China", "Beihai, Guangxi", "Beihai, Guangxi, China", 21.481, 109.120, "fan/motor factory", "Fans, motors and thermal modules", "SRC_SUNON"),
    ("SUNON_BATAAN", "SUNON Bataan Factory", "SUNON", "Philippines", "Bataan", "Bataan, Philippines", 14.641, 120.481, "fan/motor factory", "Fans, motors and thermal modules", "SRC_SUNON"),
    # TDK Electronics plants listed on the cited official Greater China page.
    ("TDK_XIAMEN", "TDK Xiamen Plant", "TDK", "China", "Xiamen, Fujian", "413-419 Tong Ji Nan Rd., Jimei, Xiamen", 24.575, 118.095, "electronic components factory", "Aluminum electrolytic capacitors", "SRC_TDK_PLANTS"),
    ("TDK_XIAOGAN", "TDK Xiaogan Plant", "TDK", "China", "Xiaogan, Hubei", "257-1 Changzheng Rd., Xiaogan", 30.925, 113.916, "electronic components factory", "Piezo and protection devices", "SRC_TDK_PLANTS"),
    ("TDK_ZHUHAI", "TDK Zhuhai Plant", "TDK", "China", "Zhuhai, Guangdong", "9 Shuanglin East Rd., Jinwan District, Zhuhai", 22.079, 113.363, "magnetics factory", "Power inductors, transformers and EMC filters", "SRC_TDK_PLANTS"),
    ("TDK_ZHUHAI_FTZ", "TDK Zhuhai FTZ Plant", "TDK", "China", "Zhuhai, Guangdong", "Lianfeng Rd., Zhuhai Free Trade Zone", 22.181, 113.517, "electronic components factory", "Protection devices and film capacitors", "SRC_TDK_PLANTS"),
    # Auras public production-base list.
    ("AURAS_GUANGZHOU", "Auras Guangzhou Factory", "Auras Technology", "China", "Guangzhou, Guangdong", "Guangzhou, Guangdong, China", 23.129, 113.264, "thermal module factory", "Graphics-card cooling, heat pipes and vapor chambers", "SRC_AURAS"),
    ("AURAS_KUNSHAN", "Auras Kunshan Factory", "Auras Technology", "China", "Kunshan, Jiangsu", "Kunshan, Jiangsu, China", 31.385, 120.981, "thermal module factory", "Cooling modules, heat pipes and vapor chambers", "SRC_AURAS"),
    ("AURAS_CHONGQING", "Auras Chongqing Factory", "Auras Technology", "China", "Chongqing", "Chongqing, China", 29.563, 106.551, "thermal module factory", "Cooling modules, heat pipes and vapor chambers", "SRC_AURAS"),
    ("AURAS_HEFEI", "Auras Anhui/Hefei Factory", "Auras Technology", "China", "Hefei, Anhui", "Hefei, Anhui, China", 31.820, 117.227, "thermal module factory", "Cooling modules, heat pipes and vapor chambers", "SRC_AURAS"),
    # Infineon official global manufacturing footprint (city-level).
    ("INF_TIJUANA", "Infineon Tijuana", "Infineon", "Mexico", "Tijuana", "Tijuana, Mexico", 32.514, -117.038, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_MESA", "Infineon Mesa", "Infineon", "United States", "Mesa, Arizona", "Mesa, Arizona, USA", 33.415, -111.831, "semiconductor frontend factory", "Frontend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_LEOMINSTER", "Infineon Leominster", "Infineon", "United States", "Leominster, Massachusetts", "Leominster, MA, USA", 42.525, -71.760, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_WARSTEIN", "Infineon Warstein", "Infineon", "Germany", "Warstein", "Warstein, Germany", 51.445, 8.355, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_VILLACH", "Infineon Villach", "Infineon", "Austria", "Villach", "Villach, Austria", 46.611, 13.855, "semiconductor frontend factory", "Frontend power-semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_REGENSBURG", "Infineon Regensburg", "Infineon", "Germany", "Regensburg", "Regensburg, Germany", 49.014, 12.101, "semiconductor frontend/backend factory", "Frontend and backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_DRESDEN", "Infineon Dresden", "Infineon", "Germany", "Dresden", "Dresden, Germany", 51.050, 13.738, "semiconductor frontend factory", "Frontend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_CEGLED", "Infineon Cegled", "Infineon", "Hungary", "Cegled", "Cegled, Hungary", 47.173, 19.799, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_WUXI", "Infineon Wuxi", "Infineon", "China", "Wuxi, Jiangsu", "Wuxi, Jiangsu, China", 31.491, 120.312, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_SINGAPORE", "Infineon Singapore", "Infineon", "Singapore", "Singapore", "Singapore", 1.352, 103.820, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_BATAM", "Infineon Batam", "Infineon", "Indonesia", "Batam", "Batam, Indonesia", 1.045, 104.030, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_MELAKA", "Infineon Melaka", "Infineon", "Malaysia", "Melaka", "Melaka, Malaysia", 2.189, 102.250, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_KULIM", "Infineon Kulim", "Infineon", "Malaysia", "Kulim, Kedah", "Kulim, Kedah, Malaysia", 5.365, 100.561, "semiconductor frontend factory", "Frontend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    ("INF_BANGKOK", "Infineon Bangkok", "Infineon", "Thailand", "Bangkok/Samut Prakan", "Samut Prakan, Thailand", 13.600, 100.600, "semiconductor backend factory", "Backend semiconductor manufacturing", "SRC_INFINEON_FOOTPRINT_2026"),
    # Nexperia official manufacturing footprint.
    ("NXP_HAMBURG", "Nexperia Hamburg Wafer Fab", "Nexperia", "Germany", "Hamburg", "Hamburg, Germany", 53.551, 9.994, "semiconductor wafer fab", "Discrete semiconductor wafer fabrication", "SRC_NEXPERIA_LOCATIONS"),
    ("NXP_MANCHESTER", "Nexperia Manchester Wafer Fab", "Nexperia", "United Kingdom", "Manchester", "Manchester, UK", 53.481, -2.242, "semiconductor wafer fab", "Discrete semiconductor wafer fabrication", "SRC_NEXPERIA_LOCATIONS"),
    ("NXP_GUANGDONG", "Nexperia Guangdong Assembly Center", "Nexperia", "China", "Guangdong", "Guangdong, China", 23.129, 113.264, "semiconductor assembly factory", "Semiconductor assembly and packaging", "SRC_NEXPERIA_LOCATIONS"),
    ("NXP_SEREMBAN", "Nexperia Seremban Assembly Center", "Nexperia", "Malaysia", "Seremban", "Seremban, Malaysia", 2.729, 101.938, "semiconductor assembly factory", "Semiconductor assembly and packaging", "SRC_NEXPERIA_LOCATIONS"),
    ("NXP_CABUYAO", "Nexperia Cabuyao Assembly Center", "Nexperia", "Philippines", "Cabuyao", "Cabuyao, Philippines", 14.278, 121.125, "semiconductor assembly factory", "Semiconductor assembly and packaging", "SRC_NEXPERIA_LOCATIONS"),
]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fields:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def merge_sources() -> list[dict]:
    path = CLEAN / "sources.csv"
    rows = read_csv(path)
    by_id = {r["source_id"]: r for r in rows}
    for row in SOURCE_ADDITIONS + RESEARCH_SOURCES:
        by_id[row["source_id"]] = row
    merged = list(by_id.values())
    fields = ["source_id", "organization", "title", "url", "use", "reliability", "reviewed_on"]
    write_csv(path, merged, fields)
    write_csv(CLEAN / "full_supply_chain_sources.csv", merged, fields)
    return merged


def evidence_for_edge(edge: dict, nodes: dict[str, dict]) -> tuple[str, str, str, str]:
    # Source assignment must be scoped to a reviewed edge.  The previous version
    # assigned broad documents from keywords; that is insufficient verification.
    manual = {r['edge_id']: r for r in EDGE_EVIDENCE}.get(edge.get('id'))
    if manual:
        return manual['validation_status'], manual['evidence_scope'], manual['source_ids'], manual['audit_note']
    eid = edge.get('id', '')
    if eid == 'E0036':
        return ('semantic_conflict', 'stage_output_definition', 'SRC_SIA_PROCESS',
                'ATP produces a packaged/tested device, whereas GPU Die is a bare-die constituent of GPU Package. Connecting ATP output back into the die double-counts packaging; split bare die and package output.')
    if edge.get('source_dataset') == 'gpu_bom_609_parts':
        return ('secondary_structure_reference', 'generic_BOM_structure', 'SRC_BOMWIKI_GPU',
                'Preserved submitted generic BOM hierarchy; presence, quantities and supplier allocation require a specific card reference.')
    if eid in {'E0037','E0038','E0039','E0041'}:
        return ('supported_process_stage', 'semiconductor_stage_sequence', 'SRC_SIA_PROCESS',
                'Industry source supports fabrication followed by assembly, packaging and testing; rename the post-ATP output as a packaged device.')
    if eid in {f'E{i:04d}' for i in range(49,57)}:
        return ('supported_category_use', 'industry_process_input', 'SRC_ETO_2026;SRC_SIA_FRONTEND',
                'Supports broad fabrication input category. Specific materials and recipes depend on process technology.')
    if eid in {'E0594','E0595'}:
        return ('supported_product_class','MLCC_materials','SRC_MURATA_MLCC_MATERIALS',
                'Supports barium titanate and nickel in ceramic component manufacture; exact MLCC grade remains unspecified.')
    if eid in {'E0683','E0685','E0729','E0604'}:
        return ('supported_product_class','PCB_laminate_construction','SRC_IPC_PCB',
                'FR-4 multilayer boards use laminate and prepreg with resin and reinforcement; exact board stack-up is unspecified.')
    if str(edge['source']).startswith('RAW-'):
        return ('upstream_lineage_requires_process_evidence','unverified_conversion','',
                'A raw-material ancestry link may skip refining or chemical intermediates. Verify the actual route before treating it as direct factory-to-factory supply.')
    if str(edge['source']).startswith('DC-'):
        return ('consumable_use_requires_confirmation','unverified_consumable_choice','',
                'Tooling or consumable use is design/process dependent and does not imply that it remains in the product.')
    return ('unverified_specific_relation','submitted_graph_only','',
            'Exact relationship has not been independently verified. Retain as a proposal pending a specific technical source.')


def audit_graph(graph: dict) -> tuple[list[dict], dict]:
    nodes = {str(n["id"]): n for n in graph["nodes"]}
    node_rows = []
    for n in graph["nodes"]:
        node_rows.append({
            "node_id": n["id"],
            "node_name": n["name"],
            "node_type": n.get("node_type", ""),
            "is_raw_material": n.get("is_raw_material", False),
            "source_dataset": n.get("source_dataset", ""),
            "bom_layer": n.get("bom_layer", ""),
            "in_degree_submitted": n.get("in_degree", ""),
            "out_degree_submitted": n.get("out_degree", ""),
        })
    write_csv(CLEAN / "full_supply_chain_nodes.csv", node_rows)

    edge_rows = []
    seen_pairs = Counter((str(e["source"]), str(e["target"]), e.get("relationship", "")) for e in graph["edges"])
    for e in graph["edges"]:
        source_exists = str(e["source"]) in nodes
        target_exists = str(e["target"]) in nodes
        if source_exists and target_exists:
            status, scope, source_ids, note = evidence_for_edge(e, nodes)
        else:
            status, scope, source_ids, note = "invalid_missing_node", "structural_error", "", "Source or target node is absent."
        edge_rows.append({
            "edge_id": e.get("id", ""),
            "source_node_id": e["source"],
            "source_node_name": e.get("source_name", nodes.get(str(e["source"]), {}).get("name", "")),
            "target_node_id": e["target"],
            "target_node_name": e.get("target_name", nodes.get(str(e["target"]), {}).get("name", "")),
            "relationship": e.get("relationship", ""),
            "edge_type": e.get("edge_type", ""),
            "submitted_source_dataset": e.get("source_dataset", ""),
            "source_node_exists": source_exists,
            "target_node_exists": target_exists,
            "self_loop": str(e["source"]) == str(e["target"]),
            "duplicate_pair_count": seen_pairs[(str(e["source"]), str(e["target"]), e.get("relationship", ""))],
            "validation_status": status,
            "evidence_scope": scope,
            "source_ids": source_ids,
            "audit_note": note,
            "recommended_relationship": ('upstream_feedstock_lineage' if str(e['source']).startswith('RAW-') else
                'consumed_in_process' if str(e['source']).startswith('DC-') else
                'member_of_category' if status == 'supported_category_membership' else e.get('relationship','')),
            "mandatory_input_status": 'not_established_for_specific_GPU',
        })
    write_csv(CLEAN / "full_supply_chain_edges_audit.csv", edge_rows)

    # Independently validate the graph structure instead of trusting metadata in the
    # submitted file.
    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, list[str]] = defaultdict(list)
    indegree = {nid: 0 for nid in nodes}
    for e in graph["edges"]:
        s, t = str(e["source"]), str(e["target"])
        if s not in nodes or t not in nodes:
            continue
        outgoing[s].append(t)
        incoming[t].append(s)
        indegree[t] += 1
    queue = deque(nid for nid, degree in indegree.items() if degree == 0)
    visited = 0
    work_indegree = dict(indegree)
    while queue:
        nid = queue.popleft()
        visited += 1
        for nxt in outgoing[nid]:
            work_indegree[nxt] -= 1
            if work_indegree[nxt] == 0:
                queue.append(nxt)
    dag_valid = visited == len(nodes)
    roots = sorted(nid for nid in nodes if not outgoing[nid])
    raw_ids = {nid for nid, n in nodes.items() if n.get("is_raw_material")}

    def can_reach_any(start: str, adjacency: dict[str, list[str]], targets: set[str]) -> bool:
        todo = [start]
        seen = set()
        while todo:
            current = todo.pop()
            if current in targets:
                return True
            if current in seen:
                continue
            seen.add(current)
            todo.extend(adjacency[current])
        return False

    nodes_without_root_path = sorted(nid for nid in nodes if not can_reach_any(nid, outgoing, set(roots)))
    nodes_without_raw_ancestor = sorted(nid for nid in nodes if not can_reach_any(nid, incoming, raw_ids))
    raw_nodes_not_reaching_root = sorted(nid for nid in raw_ids if not can_reach_any(nid, outgoing, set(roots)))

    summary = {
        "submitted_nodes": len(graph["nodes"]),
        "submitted_edges": len(graph["edges"]),
        "missing_node_edges": sum(r["validation_status"] == "invalid_missing_node" for r in edge_rows),
        "self_loops": sum(bool(r["self_loop"]) for r in edge_rows),
        "duplicate_relationship_rows": sum(int(r["duplicate_pair_count"]) > 1 for r in edge_rows),
        "independently_validated_dag": dag_valid,
        "root_node_ids_out_degree_zero": roots,
        "nodes_without_path_to_a_root": nodes_without_root_path,
        "nodes_without_raw_material_ancestor": nodes_without_raw_ancestor,
        "raw_material_nodes_without_path_to_root": raw_nodes_not_reaching_root,
        "validation_status_counts": dict(Counter(r["validation_status"] for r in edge_rows)),
        "important_interpretation": "Category-level support is not exact recipe, quantity, transaction, or factory-allocation evidence.",
    }
    (CLEAN / "full_supply_chain_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return edge_rows, summary


def build_vendor_table(graph: dict) -> tuple[list[dict], list[dict]]:
    providers = {r["provider_id"]: r for r in read_csv(CLEAN / "providers.csv")}
    links = read_csv(CLEAN / "provider_component_links.csv")
    nodes = {str(n["id"]): n for n in graph["nodes"]}
    rows: list[dict] = []

    def append_row(node_id: str, link: dict, basis: str, exactness: str) -> None:
        p = providers[link["provider_id"]]
        rows.append({
            "full_graph_node_id": node_id,
            "full_graph_node_name": nodes[node_id]["name"],
            "provider_id": link["provider_id"],
            "provider_name": p["provider_name"],
            "provider_role": link.get("role", "provider"),
            "provider_rank_within_node": "",
            "market_share_percent": link.get("market_share_percent", ""),
            "market_share_year": link.get("market_share_year", ""),
            "selection_basis": basis,
            "mapping_exactness": exactness,
            "evidence_level": link.get("evidence_level", ""),
            "source_ids": link.get("source_ids", ""),
            "caveat": "Capability/provider evidence does not prove a purchase order or a particular manufacturing site supplies this GPU.",
        })

    # ETO categories: take organization providers only, up to ten.  Market share is
    # used when present; otherwise the set is explicitly unranked.
    for full_id, eto_id in ETO_NODE_MAP.items():
        candidates = [
            r for r in links
            if r["component_node_id"] == f"ETO:{eto_id}"
            and providers.get(r["provider_id"], {}).get("provider_type") == "organization"
        ]
        candidates.sort(key=lambda r: (-(float(r["market_share_percent"]) if r.get("market_share_percent") else -1), providers[r["provider_id"]]["provider_name"]))
        for link in candidates[:10]:
            basis = "ETO market-share field" if link.get("market_share_percent") else "ETO curated provider set; unranked because no share field is published"
            append_row(full_id, link, basis, "direct category alignment")

    # Existing hand-researched BOM providers, mapped from BOM:x to submitted x.
    for link in links:
        cid = link.get("component_node_id", "")
        if not cid.startswith("BOM:"):
            continue
        full_id = cid.split(":", 1)[1]
        if full_id in nodes and link["provider_id"] in providers:
            append_row(full_id, link, "official company capability or disclosed partner evidence", "direct BOM component alignment")

    # Rank only when comparable market shares exist. Otherwise retain a stable row
    # number while calling it an evidence order, not a market rank.
    for record in RESEARCH_VENDORS:
        nid = record['node_id']
        if nid not in nodes:
            raise ValueError(f'Unknown research node: {nid}')
        pid = 'PUBLIC:' + hashlib.sha256(record['provider_name'].casefold().encode()).hexdigest()[:12]
        rows.append({
            'full_graph_node_id': nid, 'full_graph_node_name': nodes[nid]['name'],
            'provider_id': pid, 'provider_name': record['provider_name'],
            'provider_role': 'documented_product_supplier', 'provider_rank_within_node': 'unranked',
            'market_share_percent': '', 'market_share_year': '',
            'selection_basis': 'official product or production evidence; market rank not independently established',
            'mapping_exactness': 'explicit scoped research mapping',
            'evidence_level': 'official_product_capability', 'source_ids': record['source_ids'],
            'caveat': 'See product_scope: a combined node may only have one supported branch.',
            'product_scope': record['product_scope'], 'qualification_status': record['qualification'],
            'reviewed_on': REVIEW_DATE,
        })
    # Consolidate the same named supplier within a node; keep all cited sources.
    merged = {}
    for row in rows:
        # The short and full SHINKO name denote the same company, not two
        # independent backups. Corporate name supported by R2_SHINKO_PLANTS.
        if row['provider_name'].casefold() in {'shinko','shinko electric industries'}:
            row['provider_name']='Shinko Electric Industries'
            row['provider_id']='PUBLIC:'+hashlib.sha256(row['provider_name'].casefold().encode()).hexdigest()[:12]
            row['source_ids']=';'.join(sorted(set(filter(None,(row['source_ids']+';R2_SHINKO_PLANTS').split(';')))))
        key = (row['full_graph_node_id'], row['provider_name'].casefold())
        if key in merged:
            old = merged[key]
            row['source_ids'] = ';'.join(sorted(set((old['source_ids']+';'+row['source_ids']).split(';'))))
        merged[key] = row
    rows = list(merged.values())
    for row in rows:
        row.setdefault('product_scope', 'Published category capability; product grade and recipe are unspecified')
        row.setdefault('qualification_status', 'grade_and_customer_qualification_unverified')
        row.setdefault('reviewed_on', '')
        ownership = CORPORATE_GROUPS.get(row['provider_name'].casefold())
        row['corporate_group'] = ownership[0] if ownership else row['provider_name']
        row['corporate_group_status'] = ownership[2] if ownership else 'not_independently_reviewed'
        row['ownership_source_ids'] = ownership[1] if ownership else ''
        row['independent_leadership_rank_status'] = 'not_established'
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["full_graph_node_id"]].append(row)
    for group in grouped.values():
        # Favor explicitly checked product records over an alphabetical selection
        # from an unranked ETO list. This order is not a market-share ranking.
        group.sort(key=lambda r: (r['mapping_exactness'] != 'explicit scoped research mapping', r['provider_name']))
        del group[10:]
        with_share = (all(r["market_share_percent"] not in ("", None) for r in group)
                      and len({str(r['market_share_year']) for r in group}) == 1
                      and all(r['mapping_exactness']=='direct category alignment' for r in group))
        if with_share:
            group.sort(key=lambda r: float(r["market_share_percent"]), reverse=True)
        else:
            group.sort(key=lambda r: r["provider_name"])
        for i, row in enumerate(group, 1):
            row["provider_rank_within_node"] = i if with_share else "unranked"

    rows = [r for group in grouped.values() for r in group]
    rows.sort(key=lambda r: (r["full_graph_node_id"], str(r["provider_rank_within_node"]), r["provider_name"]))
    write_csv(CLEAN / "full_supply_chain_vendors.csv", rows)

    search_log_path=RAW/'additional_node_research_search_log.json'
    search_log=json.loads(search_log_path.read_text()) if search_log_path.exists() else []
    attempts=Counter(r['node_id'] for r in search_log)
    coverage = []
    for n in graph["nodes"]:
        nid = str(n["id"])
        count = len(grouped.get(nid, []))
        coverage.append({
            "node_id": nid,
            "node_name": n["name"],
            "node_type": n.get("node_type", ""),
            "vendor_count": count,
            "vendor_status": "documented_provider_set" if count else "not_yet_supported_by_node_specific_vendor_evidence",
            "procurement_treatment": ('process_stage_no_material_vendor' if n.get('node_type') == 'process_stage' else
                'category_expand_children' if n.get('node_type') == 'material_category' else
                'local_resource_or_utility' if nid in {'RAW-AIR','RAW-WATER'} else 'supplier_research_required'),
            "coverage_means": "At least one product/category capability record; does not establish qualified alternatives or market coverage.",
            "recorded_followup_searches": attempts[nid],
            "distinct_corporate_groups": len({r['corporate_group'] for r in grouped.get(nid,[])}),
            "next_action": "" if count else "Research official product pages or authoritative market source; do not inherit parent vendors automatically.",
        })
    write_csv(CLEAN / "full_supply_chain_vendor_coverage.csv", coverage)
    return rows, coverage


def research_site_id(record: dict) -> str:
    return 'PUBLIC_SITE:' + hashlib.sha256(record['facility_name'].encode()).hexdigest()[:12]


def build_facility_table() -> list[dict]:
    existing = read_csv(CLEAN / "facilities.csv")
    rows = []
    excluded_types = {"airport", "port", "design", "test"}
    for r in existing:
        if r.get("facility_type", "").lower() in excluded_types or r.get("company") in {"Transport node", "Scenario stage"}:
            continue
        rows.append({
            "facility_id": r["facility_id"],
            "facility_name": r["facility_name"],
            "company": r["company"],
            "country": r["country"],
            "city": r["city"],
            "address": r["address"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "facility_type": r["facility_type"],
            "component_categories": r["component_categories"],
            "site_evidence_level": r["evidence_level"],
            "product_assignment": r["product_assignment"],
            "source_ids": r["source_ids"],
            "coordinate_precision": r["coordinate_precision"],
            "public_site_list_completeness": "existing curated record; company-wide completeness varies by source",
        })
    for fid, name, company, country, city, address, lat, lon, ftype, components, source_id in EXTRA_FACILITIES:
        rows.append({
            "facility_id": f"EXT:{fid}",
            "facility_name": name,
            "company": company,
            "country": country,
            "city": city,
            "address": address,
            "latitude": lat,
            "longitude": lon,
            "facility_type": ftype,
            "component_categories": components,
            "site_evidence_level": "official company production-site evidence",
            "product_assignment": "capability/site confirmed; exact GPU customer allocation not public",
            "source_ids": source_id,
            "coordinate_precision": "legacy_approximation_not_independently_geocoded",
            "public_site_list_completeness": "partial public list; exhaustive global footprint not established",
        })
    cache_path = RAW / 'public_site_geocodes.json'
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for record in RESEARCH_SITES:
        fid = research_site_id(record)
        geo = cache.get(fid, {})
        rows.append({
            'facility_id': fid, 'facility_name': record['facility_name'],
            'company': record['company'], 'country': record['country'],
            'city': record['city'], 'address': record['address'],
            'latitude': geo.get('latitude',''), 'longitude': geo.get('longitude',''),
            'facility_type': 'production_asset', 'component_categories': record['node_ids'],
            'site_evidence_level': 'official named production-site evidence',
            'product_assignment': 'Only the product scope listed in component_categories is evidenced; no GPU customer allocation established.',
            'source_ids': record['source_ids'] + (';R_OSM_GEOCODE' if geo.get('latitude') is not None and geo.get('latitude') != '' else ''),
            'coordinate_precision': geo.get('precision','not_geocoded'),
            'public_site_list_completeness': 'partial public list; exhaustive global footprint not established',
            'operating_status': record['operating_status'],
            'geocode_display_name': geo.get('display_name',''),
        })
    for row in rows:
        row.setdefault('operating_status', 'legacy_public_site_status_not_rechecked')
        row.setdefault('geocode_display_name','')
    by_id = {r["facility_id"]: r for r in rows}
    rows = sorted(by_id.values(), key=lambda r: (r["company"], r["country"], r["facility_name"]))
    city_groups=Counter((r['company'].casefold(),r['city'].casefold()) for r in rows)
    for row in rows:
        group=(row['company'].casefold(),row['city'].casefold())
        row['same_company_city_asset_count']=city_groups[group]
        row['site_independence_caveat']='Records in the same company/city may be units of one complex, duplicate disclosures or distinct plants; do not automatically count them as independent backup locations.'
    for row in rows:
        row.update(process_validation_research.SITE_UPDATES.get(row['facility_id'], {}))
    fields = list(rows[0]) + [x for x in ['operating_status','geocode_display_name'] if x not in rows[0]]
    write_csv(CLEAN / "full_supply_chain_facilities.csv", rows, fields)
    return rows


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_airports() -> list[dict]:
    rows = read_csv(RAW / "ourairports_airports.csv")
    airports = []
    for r in rows:
        if r.get("scheduled_service") != "yes" or r.get("type") not in {"large_airport", "medium_airport"} or not r.get("iata_code"):
            continue
        try:
            lat, lon = float(r["latitude_deg"]), float(r["longitude_deg"])
        except (ValueError, TypeError):
            continue
        airports.append({"hub_id": r["ident"], "hub_name": r["name"], "country": r["iso_country"], "latitude": lat, "longitude": lon})
    return airports


def load_ports() -> list[dict]:
    ports = []
    for path in sorted(RAW.glob("world_port_index_*.geojson")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        for feature in obj.get("features", []):
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])
            if len(coords) < 2:
                continue
            ports.append({
                "hub_id": str(props.get("INDEX_NO", "")),
                "hub_name": props.get("PORT_NAME", ""),
                "country": props.get("COUNTRY", ""),
                "latitude": float(coords[1]),
                "longitude": float(coords[0]),
            })
    return ports


def build_nearest_hubs(facilities: list[dict]) -> list[dict]:
    airports = load_airports()
    ports = load_ports()
    rows = []
    for f in facilities:
        try:
            lat, lon = float(f["latitude"]), float(f["longitude"])
        except (ValueError, TypeError):
            continue
        for hub_type, hubs, source_id in [("commercial_airport", airports, "SRC_OURAIRPORTS"), ("port", ports, "SRC_NGA_WPI;R_WPI_MIRROR")]:
            nearest = sorted(hubs, key=lambda h: haversine_km(lat, lon, h["latitude"], h["longitude"]))[:3]
            for rank, h in enumerate(nearest, 1):
                rows.append({
                    "facility_id": f["facility_id"],
                    "facility_name": f["facility_name"],
                    "company": f["company"],
                    "hub_type": hub_type,
                    "proximity_rank": rank,
                    "hub_id": h["hub_id"],
                    "hub_name": h["hub_name"],
                    "hub_country_code_or_name": h["country"],
                    "hub_latitude": h["latitude"],
                    "hub_longitude": h["longitude"],
                    "great_circle_distance_km": round(haversine_km(lat, lon, h["latitude"], h["longitude"]), 1),
                    "source_ids": source_id,
                    "facility_coordinate_precision": f['coordinate_precision'],
                    "cargo_service_status": 'unverified_air_cargo_capability' if hub_type == 'commercial_airport' else 'unverified_commercial_cargo_capability',
                    "caveat": "Nearest by straight-line distance only; does not prove cargo service, customs suitability, road access, capacity, hazardous/bulk-material handling suitability or an actual route.",
                })
    write_csv(CLEAN / "full_supply_chain_nearest_hubs.csv", rows)
    return rows


def build_site_coverage(vendors: list[dict], facilities: list[dict]) -> list[dict]:
    """Only explicit researched product/site associations are product-scope links.

    Company name matching can identify a publicly known factory, but cannot assign
    all of that vendor's products to that factory.
    """
    rows=[]
    aliases={
             'jsr':'jsr', 'shinko':'shinko electric industries',
             'nitto boseki':'nitto boseki', 'ibiden':'ibiden'}
    def key(name):
        name=name.casefold().strip()
        return aliases.get(name,name)
    for vendor in vendors:
        sites=[s for s in facilities if key(s['company'])==key(vendor['provider_name'])]
        scoped=[s for s in sites if vendor['full_graph_node_id'] in s['component_categories'].split()]
        rows.append({
            'node_id':vendor['full_graph_node_id'], 'node_name':vendor['full_graph_node_name'],
            'provider_name':vendor['provider_name'], 'public_site_count':len(sites),
            'explicit_product_class_site_count':len(scoped),
            'product_class_site_ids':';'.join(s['facility_id'] for s in scoped),
            'other_company_site_ids':';'.join(s['facility_id'] for s in sites if s not in scoped),
            'site_status':'fabless_designer_no_owned_fab_required' if vendor['provider_name'].casefold()=='nvidia' else 'product_class_site_documented' if scoped else
                          'company_sites_only_product_allocation_unverified' if sites else 'no_site_evidence_in_current_package',
            'next_action':'Check every facility for grade, available capacity, operating status and customer qualification.',
            'source_ids':';'.join(sorted({v for s in scoped for v in s['source_ids'].split(';')})),
        })
    write_csv(CLEAN/'full_supply_chain_vendor_site_coverage.csv',rows)
    return rows


def build_modeling_issues(graph: dict) -> list[dict]:
    issues=[
        ('PACKAGING_DOUBLE_COUNT','high','E0036','LD:finished_logic_die;1.2.1',
         'Post-ATP packaged output feeds the bare GPU die, which then feeds GPU Package.',
         'Use fabricated bare die as GPU Package input; connect ATP output to the packaged-device node.',
         'SRC_SIA_PROCESS'),
        ('MEMORY_GENERATION','high','E0688','SC-DRAM-DIE;1.3',
         'Submitted die names GDDR6/GDDR6X while the repository reference is RTX 5080-class with GDDR7.',
         'Choose generic GDDR family or use GDDR7 throughout and source a matching package structure.',
         'SRC_NVIDIA_5080;SRC_MICRON_GDDR7'),
        ('OPTIONAL_VS_REQUIRED','high','','',
         'Alternative materials and process options are all labeled necessary_input_for.',
         'Represent alternatives with OR/eligibility groups and mandatory simultaneous inputs with AND groups before min-cut or lead-time analysis.',
         ''),
        ('MASK_TECHNOLOGY','high','E0101','LD:soda_lime_glass;LD:photomasks',
         'Generic soda-lime glass has been assigned to all semiconductor photomasks.',
         'Use a technology-specific DUV/EUV mask-blank reference and actual required substrate/coating.',
         'R_HOYA_BLANKS'),
        ('RGB_PHOSPHOR','medium','E0754','SC-PHOSPHOR;8.1',
         'YAG phosphor is treated as necessary for RGB LED.',
         'Make phosphor dependent on white/phosphor-converted LED design; source the selected LED package.',
         'R_CREE_RGB'),
        ('MISSING_ELEMENT_FEEDSTOCKS','high','','SC-LED-DIE;PM-SAPPHIRE-WAFER',
         'InGaN/AlInGaP and GaAs are named, but no raw gallium/indium nodes exist in the submitted raw-material set.',
         'Review elemental inputs and compound-semiconductor chain; graph reachability alone does not establish chemical completeness.',
         'R_IQE_GAAS'),
        ('RAW_ORE_SHORTCUTS','medium','','',
         'Many edges jump from ore directly to a high-purity chemical, wire or plated product.',
         'Keep as ancestry links or insert refining/synthesis/purification steps. Do not use them as observed direct shipments.',
         ''),
        ('COMBINED_PRODUCT_NODES','high','','',
         'Several nodes combine different saleable products, grades or materials with slash/and labels.',
         'Split procurement alternatives or specify which branch each supplier and factory supports.',
         ''),
        ('INTERNAL_SUBCOMPONENTS','medium','','SC-MLCC-BODY;SC-POWER-DIE;SC-MCU-DIE;SC-TVS-DIE',
         'Finished-device capability does not establish separately sold bare die or unfinished component bodies.',
         'Model in-house production at the parent manufacturer where relevant; independently qualify bare-part suppliers if needed.',
         ''),
        ('SITE_PRODUCT_GRADE','high','','',
         'Publicly listed company sites may not manufacture the required grade/product. Legacy HBM sites do not establish GDDR production.',
         'Require product-class site evidence and qualification; use vendor_site_coverage to distinguish company-level site matches.',
         ''),
        ('GEOGRAPHIC_HUBS','medium','','',
         'Nearby airports may have passenger service only; WPI ports can include unsuitable terminals.',
         'Confirm cargo acceptance, customs, operating status and feasible land access before routing.',
         'SRC_OURAIRPORTS;SRC_NGA_WPI'),
        ('LOCATION_PRECISION','medium','','',
         'Many coordinates are city/district proxies or inherited approximations.',
         'Retain coordinate_precision and obtain factory-gate coordinates before operational routing.',
         'R_OSM_GEOCODE'),
        ('MARKET_REPRESENTATIVENESS','high','','',
         'Provider presence and up-to-ten supplier count do not measure market coverage or qualified redundancy.',
         'Add independent market-share evidence with product definition/year, or report a sample of documented providers.',
         'SRC_ETO_2026'),
    ]
    rows=[dict(issue_id=i,severity=s,edge_ids=e,node_ids=n,problem=p,recommended_action=a,source_ids=src)
          for i,s,e,n,p,a,src in issues]
    write_csv(CLEAN/'full_supply_chain_modeling_issues.csv',rows)
    return rows


def export_enriched_data(graph, edges, vendors, facilities, hubs, site_coverage, issues):
    vendor_by_node=defaultdict(list)
    for v in vendors:
        vendor_by_node[v['full_graph_node_id']].append(v)
    enriched={
        'metadata':{'reviewed_on':REVIEW_DATE,'original_graph_preserved':True,
                    'scope':'Public evidence extension; no confidential procurement or qualified-alternative claim',
                    'edge_audit_method':'Explicitly scoped evidence; broad keyword matches do not verify edges'},
        'nodes':[dict(n,vendor_candidates=vendor_by_node[str(n['id'])], component_definition=component_definition_research.DEFINITIONS.get(str(n['id']))) for n in graph['nodes']],
        'edges':edges,'facilities':facilities,'nearby_hub_candidates':hubs,
        'vendor_site_coverage':site_coverage,'modeling_issues':issues,
        'sources':read_csv(CLEAN/'sources.csv'),
    }
    (CLEAN/'full_supply_chain_research_database.json').write_text(json.dumps(enriched,indent=2,ensure_ascii=False)+'\n')


def write_completion_report(graph: dict, edge_rows: list[dict], vendor_rows: list[dict], coverage: list[dict], facilities: list[dict], hubs: list[dict]) -> None:
    status_counts = Counter(r["validation_status"] for r in edge_rows)
    vendor_covered = sum(int(r["vendor_count"]) > 0 for r in coverage)
    report = {
        "generated_from": INPUT_JSON.name,
        "graph_nodes": len(graph["nodes"]),
        "graph_edges": len(graph["edges"]),
        "edge_evidence_status": dict(status_counts),
        "nodes_with_node_specific_vendor_evidence": vendor_covered,
        "nodes_without_node_specific_vendor_evidence": len(coverage) - vendor_covered,
        "vendor_component_rows": len(vendor_rows),
        "distinct_named_vendors": len({r['provider_name'].casefold() for r in vendor_rows}),
        "procurement_node_treatments": dict(Counter(r['procurement_treatment'] for r in coverage)),
        "physical_nodes_with_supplier_evidence": sum(int(r['vendor_count'])>0 and r['procurement_treatment']=='supplier_research_required' for r in coverage),
        "physical_nodes_requiring_supplier_research": sum(r['procurement_treatment']=='supplier_research_required' for r in coverage),
        "coverage_warning": "A supplier listing is capability evidence, not proof of qualification, complete material branches, market representativeness or actual procurement.",
        "public_production_site_rows": len(facilities),
        "vendor_site_coverage_status": dict(Counter(r['site_status'] for r in read_csv(CLEAN/'full_supply_chain_vendor_site_coverage.csv'))),
        "factory_discovery_searches_logged": len(json.loads((RAW/'manufacturing_site_research_search_log.json').read_text())),
        "sites_without_geocodes": sum(r['latitude'] in ('',None) or r['longitude'] in ('',None) for r in facilities),
        "readiness": "research_extension_incomplete_for_validated_redundancy_or_end_to_end_transport_analysis",
        "legacy_audit_correction": "The earlier 400-supported-edge total relied on broad keyword/category matching and is withdrawn. Current edge support uses explicit scoped records only.",
        "nearest_hub_rows": len(hubs),
        "nearest_hub_definition": "Up to three scheduled medium/large airports and three WPI ports per geocoded production site",
        "not_claimed": [
            "The submitted 757-edge graph is fully verified.",
            "Unranked ETO providers are the market-share top ten.",
            "A listed factory supplies NVIDIA or a specific GPU model.",
            "The geographically nearest hub is actually used or operationally suitable.",
            "Public facility lists are complete when a company does not publish a global manufacturing register.",
        ],
    }
    (CLEAN / "full_supply_chain_completion_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    if not INPUT_JSON.exists():
        raise SystemExit(f"Missing {INPUT_JSON}. Copy the submitted JSON into data/raw first.")
    merge_sources()
    graph = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    edge_rows, _ = audit_graph(graph)
    vendor_rows, coverage = build_vendor_table(graph)
    facilities = build_facility_table()
    hubs = build_nearest_hubs(facilities)
    site_coverage=build_site_coverage(vendor_rows,facilities)
    issues=build_modeling_issues(graph)
    export_enriched_data(graph,edge_rows,vendor_rows,facilities,hubs,site_coverage,issues)
    write_completion_report(graph, edge_rows, vendor_rows, coverage, facilities, hubs)
    print(f"Audited {len(edge_rows)} edges")
    print(f"Built {len(vendor_rows)} vendor-component rows")
    print(f"Built {len(facilities)} production-site rows")
    print(f"Built {len(hubs)} nearest-hub rows")


if __name__ == "__main__":
    main()
