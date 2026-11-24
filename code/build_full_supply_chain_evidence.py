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
from collections import Counter, defaultdict, deque
from pathlib import Path


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
    for row in SOURCE_ADDITIONS:
        by_id[row["source_id"]] = row
    merged = list(by_id.values())
    write_csv(path, merged, ["source_id", "organization", "title", "url", "use", "reliability"])
    write_csv(CLEAN / "full_supply_chain_sources.csv", merged, ["source_id", "organization", "title", "url", "use", "reliability"])
    return merged


def evidence_for_edge(edge: dict, nodes: dict[str, dict]) -> tuple[str, str, str, str]:
    s = nodes[edge["source"]]
    t = nodes[edge["target"]]
    text = f"{s['name']} {t['name']}".lower()
    dataset = edge.get("source_dataset", "")
    ids: list[str] = []
    note = ""

    if dataset == "gpu_bom_609_parts":
        return (
            "supported_structural_reference",
            "secondary_BOM_structure",
            "SRC_BOMWIKI_GPU",
            "BOMWiki supports the generic graphics-card hierarchy; it is not an exact confidential NVIDIA BOM.",
        )

    if "pcie" in text or "card edge" in text or "connector" in text and ("lcp" in text or "copper" in text):
        ids.append("SRC_TE_PCIE_MATERIALS")
    if any(k in text for k in ["mlcc", "barium titanate", "batio3"]):
        ids.append("SRC_MURATA_MLCC_MATERIALS")
    if any(k in text for k in ["inductor", "ferrite", "magnetic powder core"]):
        ids.append("SRC_TDK_INDUCTOR_MATERIALS")
    if any(k in text for k in ["pcb", "fr-4", "prepreg", "soldermask", "copper-clad", "copper foil"]):
        ids.append("SRC_IPC_PCB")
    if any(k in text for k in ["wafer", "photoresist", "photomask", "deposition", "cmp", "etch", "logic die", "semiconductor"]):
        ids.extend(["SRC_ETO_2026", "SRC_SIA_FRONTEND"])
    if any(k in text for k in ["nitrogen trifluoride", "nitrous oxide", "fluorinated", "electronic gases"]):
        ids.append("SRC_EPA_SEMI")
    if s.get("is_raw_material") or t.get("is_raw_material"):
        ids.append("SRC_USGS_MCS2026")
    if dataset in {"gpu_logic_die_supply_chain", "package_substrate_bridge"}:
        ids.extend(["SRC_ETO_2026", "SRC_SIA_PROCESS"])

    ids = list(dict.fromkeys(ids))
    exact_product_sources = {
        "SRC_TE_PCIE_MATERIALS",
        "SRC_MURATA_MLCC_MATERIALS",
        "SRC_TDK_INDUCTOR_MATERIALS",
        "SRC_IPC_PCB",
    }
    if any(i in exact_product_sources for i in ids):
        status = "supported_product_or_industry_level"
        scope = "official technical or standards evidence"
        note = "The cited source supports the material relationship for the product class; exact GPU model allocation remains unverified."
    elif dataset == "package_substrate_bridge":
        status = "supported_category_level"
        scope = "industry category evidence"
        ids.append("SRC_AJINOMOTO_ABF")
        note = "The relationship is supported at package-substrate category level, not as a complete recipe."
    elif dataset == "gpu_logic_die_supply_chain" and ids:
        status = "supported_category_level"
        scope = "semiconductor process/material category evidence"
        note = "The broad manufacturing relationship is supported; the exact precursor recipe and quantities are not public."
    elif ids:
        status = "partially_supported_requires_specific_confirmation"
        scope = "general commodity or process evidence"
        note = "The source supports the commodity or process class but does not independently verify this exact source-to-target conversion."
    else:
        status = "unverified_specific_relation"
        scope = "submitted_graph_only"
        note = "No independent reputable source in the current evidence package verifies this exact relationship."

    return status, scope, ";".join(dict.fromkeys(ids)), note


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
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["full_graph_node_id"]].append(row)
    for group in grouped.values():
        with_share = all(r["market_share_percent"] not in ("", None) for r in group)
        if with_share:
            group.sort(key=lambda r: float(r["market_share_percent"]), reverse=True)
        else:
            group.sort(key=lambda r: r["provider_name"])
        for i, row in enumerate(group, 1):
            row["provider_rank_within_node"] = i if with_share else "unranked"

    rows.sort(key=lambda r: (r["full_graph_node_id"], str(r["provider_rank_within_node"]), r["provider_name"]))
    write_csv(CLEAN / "full_supply_chain_vendors.csv", rows)

    covered = set(grouped)
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
            "next_action": "" if count else "Research official product pages or authoritative market source; do not inherit parent vendors automatically.",
        })
    write_csv(CLEAN / "full_supply_chain_vendor_coverage.csv", coverage)
    return rows, coverage


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
            "coordinate_precision": "address_or_city_centroid",
            "public_site_list_completeness": "all manufacturing sites visible in the cited source scope; may not be a complete global corporate footprint",
        })
    by_id = {r["facility_id"]: r for r in rows}
    rows = sorted(by_id.values(), key=lambda r: (r["company"], r["country"], r["facility_name"]))
    write_csv(CLEAN / "full_supply_chain_facilities.csv", rows)
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
        for hub_type, hubs, source_id in [("commercial_airport", airports, "SRC_OURAIRPORTS"), ("port", ports, "SRC_NGA_WPI")]:
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
                    "caveat": "Nearest by straight-line distance only; does not prove cargo service, customs suitability, road access, capacity or an actual route.",
                })
    write_csv(CLEAN / "full_supply_chain_nearest_hubs.csv", rows)
    return rows


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
        "public_production_site_rows": len(facilities),
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
    write_completion_report(graph, edge_rows, vendor_rows, coverage, facilities, hubs)
    print(f"Audited {len(edge_rows)} edges")
    print(f"Built {len(vendor_rows)} vendor-component rows")
    print(f"Built {len(facilities)} production-site rows")
    print(f"Built {len(hubs)} nearest-hub rows")


if __name__ == "__main__":
    main()
