#!/usr/bin/env python3
"""Build a source-aware GPU supply-chain database and review figures.

The model joins two different structures:

* BOMWiki's product hierarchy for a representative PCIe graphics card.
* Georgetown CSET ETO's logical semiconductor input/process network.

ETO's "Finished logic chip" is a packaged and tested output, while BOMWiki's
"GPU Die" is bare fabricated silicon.  The join therefore inserts the GPU die
between ETO fabrication and ETO assembly/packaging, then maps ETO's tested
output to BOMWiki's GPU package.  This avoids equating a die with a package.

The script preserves raw inputs, exports normalized CSV/JSON tables, and makes
separate logical-dependency and physical-transport figures.  Facility and
route rows are analytical candidates unless their evidence field says that a
specific relationship is confirmed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import textwrap
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
PACKAGED_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_BOM = Path("/Users/lt/Downloads/gpu_bom_609_parts.json")
if not DEFAULT_BOM.exists() and (PACKAGED_RAW_DIR / "gpu_bom_609_parts.json").exists():
    DEFAULT_BOM = PACKAGED_RAW_DIR / "gpu_bom_609_parts.json"
DEFAULT_STRUCTURE_WORKBOOK = Path("/Users/lt/Downloads/gpu.xlsx")
if not DEFAULT_STRUCTURE_WORKBOOK.exists() and (PACKAGED_RAW_DIR / "gpu.xlsx").exists():
    DEFAULT_STRUCTURE_WORKBOOK = PACKAGED_RAW_DIR / "gpu.xlsx"
ETO_DIR = ROOT / "output" / "data" if (ROOT / "output" / "data").exists() else PACKAGED_RAW_DIR
UPSTREAM_MODULE = ROOT / "src" / "upstream_research_data.mjs"
if not UPSTREAM_MODULE.exists() and (PACKAGED_RAW_DIR / "upstream_research_data.mjs").exists():
    UPSTREAM_MODULE = PACKAGED_RAW_DIR / "upstream_research_data.mjs"
BASE_FACILITIES = ETO_DIR / "facility_locations.csv"
BASE_ROUTES = ETO_DIR / "transport_routes.csv"

ETO_FILES = ["inputs", "providers", "provision", "sequence", "stages"]
ETO_BASE = "https://raw.githubusercontent.com/georgetown-cset/eto-chip-explorer/main/data"

SOURCES = [
    {
        "source_id": "SRC_BOMWIKI_GPU",
        "organization": "BOMWiki",
        "title": "Graphics Card (GPU) bill of materials",
        "url": "https://bomwiki.com/item/graphics-card/",
        "use": "Product hierarchy and approximate repeated-part quantities",
        "reliability": "Secondary structural reference; vendor suggestions are not procurement evidence",
    },
    {
        "source_id": "SRC_GPU_WORKBOOK_ATP",
        "organization": "Project team",
        "title": "GPU construction hierarchy, ATP sheet columns R:AM",
        "url": "local project workbook",
        "use": "Canonical project hierarchy for finished logic die, ATP inputs, fabrication inputs and listed subcategories",
        "reliability": "Team-defined model structure; component contents should be validated against technical sources",
    },
    {
        "source_id": "SRC_ETO_2026",
        "organization": "Georgetown CSET Emerging Technology Observatory",
        "title": "Semiconductor Supply Chain Dataset, September 2026 release",
        "url": "https://www.eto.tech/dataset-docs/chipexplorer/",
        "use": "Semiconductor inputs, process relationships, providers and market shares",
        "reliability": "Curated research dataset; high-level and not a factory-location database",
    },
    {
        "source_id": "SRC_NVIDIA_5080",
        "organization": "NVIDIA",
        "title": "GeForce RTX 5080 specifications",
        "url": "https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/",
        "use": "Reference-card configuration used to interpret the representative BOM",
        "reliability": "Official product specification",
    },
    {
        "source_id": "SRC_NVIDIA_SUPPLY",
        "organization": "NVIDIA",
        "title": "FY2025 Sustainability Report",
        "url": "https://images.nvidia.com/aem-dam/Solutions/documents/NVIDIA-Sustainability-Report-Fiscal-Year-2025.pdf",
        "use": "Named foundry, memory, packaging and manufacturing partner categories",
        "reliability": "Official company disclosure; does not disclose every product-to-factory allocation",
    },
    {
        "source_id": "SRC_TSMC_FABS",
        "organization": "TSMC",
        "title": "TSMC fabs and advanced backend fabs",
        "url": "https://www.tsmc.com/english/aboutTSMC/TSMC_Fabs",
        "use": "Official facility names and addresses",
        "reliability": "Official company facility directory",
    },
    {
        "source_id": "SRC_SK_GDDR7",
        "organization": "SK hynix",
        "title": "GDDR7 product page",
        "url": "https://product.skhynix.com/products/dram/gddr/gddr7.go",
        "use": "GDDR7 vendor capability",
        "reliability": "Official product page",
    },
    {
        "source_id": "SRC_SAMSUNG_GDDR7",
        "organization": "Samsung Electronics",
        "title": "24 Gb GDDR7 announcement",
        "url": "https://semiconductor.samsung.com/news-events/news/samsung-develops-industrys-first-24gb-gddr7-dram-for-next-generation-ai-computing/",
        "use": "GDDR7 vendor capability",
        "reliability": "Official company release",
    },
    {
        "source_id": "SRC_MICRON_GDDR7",
        "organization": "Micron",
        "title": "GDDR7 graphics memory",
        "url": "https://www.micron.com/products/memory/graphics-memory/gddr7",
        "use": "GDDR7 vendor capability and x32 device organization",
        "reliability": "Official product page",
    },
    {
        "source_id": "SRC_COMPEQ_PLANTS",
        "organization": "Compeq Manufacturing",
        "title": "Manufacturing bases",
        "url": "https://www.compeq.com.tw/base01.php?language=en",
        "use": "PCB manufacturing locations",
        "reliability": "Official company location page",
    },
    {
        "source_id": "SRC_GBM_SITES",
        "organization": "Global Brands Manufacture",
        "title": "Operation sites",
        "url": "https://www.gbm.com.tw/en.war/about/operation_sites.html",
        "use": "PCB manufacturing locations",
        "reliability": "Official company location page",
    },
    {
        "source_id": "SRC_INFINEON_POWER",
        "organization": "Infineon",
        "title": "Integrated power stages",
        "url": "https://www.infineon.com/products/power/dc-dc-converters/integrated-power-stages",
        "use": "VRM power-stage vendor capability",
        "reliability": "Official product page; product-to-factory allocation is not disclosed",
    },
    {
        "source_id": "SRC_MPS_GPU",
        "organization": "Monolithic Power Systems",
        "title": "Accelerator-card power solutions",
        "url": "https://www.monolithicpower.com/en/applications/accelerator-cards.html",
        "use": "VRM vendor capability",
        "reliability": "Official application page; MPS is fabless and exact production sites are not public",
    },
    {
        "source_id": "SRC_TDK_PLANTS",
        "organization": "TDK Electronics",
        "title": "Sales offices and plants",
        "url": "https://www.tdk-electronics.tdk.com/en/517992/contact/sales-offices-and-plants",
        "use": "Passive-component manufacturing locations",
        "reliability": "Official company location page",
    },
    {
        "source_id": "SRC_MURATA_WUXI",
        "organization": "Murata",
        "title": "Wuxi Murata Electronics",
        "url": "https://corporate.murata.com/en-eu/company/muratalocations/affiliated_eastasia/wuxi-murataelectronics",
        "use": "Passive-component facility capability",
        "reliability": "Official company location page",
    },
    {
        "source_id": "SRC_AURAS",
        "organization": "Auras Technology",
        "title": "Corporate profile and manufacturing sites",
        "url": "https://www.auras.com.tw/CMSFS/InformationCenters/English/ecfc7b18-d55e-4ca3-a673-b449f83d051c.pdf",
        "use": "Graphics-card heat-pipe and vapor-chamber supplier/site candidates",
        "reliability": "Official company document; exact card allocation is not disclosed",
    },
    {
        "source_id": "SRC_SUNON",
        "organization": "SUNON",
        "title": "Company profile and production bases",
        "url": "https://www.sunon.com/en/about.aspx",
        "use": "Fan and motor supplier/site candidates",
        "reliability": "Official company page; exact card allocation is not disclosed",
    },
    {
        "source_id": "SRC_AMPHENOL_PCIE",
        "organization": "Amphenol Communications Solutions",
        "title": "Minitek Pwr CEM-5 PCIe connector",
        "url": "https://www.amphenol-cs.com/product-series/minitek-pwr-cem-5-pcie.html",
        "use": "Auxiliary-power connector capability",
        "reliability": "Official product page; exact factory is not disclosed",
    },
    {
        "source_id": "SRC_NEXPERIA_ESD",
        "organization": "Nexperia",
        "title": "PHDMI2FR4 HDMI ESD protection",
        "url": "https://www.nexperia.com/product/PHDMI2FR4",
        "use": "Display-output ESD component capability",
        "reliability": "Official product page; exact card and factory allocation is not disclosed",
    },
    {
        "source_id": "SRC_NUVOTON_MCU",
        "organization": "Nuvoton",
        "title": "Microcontroller products",
        "url": "https://www.nuvoton.com/products/microcontrollers/",
        "use": "RGB-controller MCU capability",
        "reliability": "Official product page; exact card allocation is not disclosed",
    },
    {
        "source_id": "SRC_OSM",
        "organization": "OpenStreetMap contributors",
        "title": "OpenStreetMap geodata",
        "url": "https://www.openstreetmap.org/copyright",
        "use": "Coordinates and road-geography basis",
        "reliability": "Open geodata; facility addresses should be verified against official company pages",
    },
    {
        "source_id": "SRC_OSRM",
        "organization": "Project OSRM",
        "title": "OSRM routing API",
        "url": "https://project-osrm.org/docs/v5.24.0/api/",
        "use": "Road-route distance and uncongested driving-time method",
        "reliability": "Routing engine; not live traffic or a freight-carrier schedule",
    },
]


# Candidate vendors are mapped to grouped BOM nodes, not to every repeated
# resistor/capacitor instance.  "Capability" does not claim that the vendor is
# used by NVIDIA or by a specific graphics-card brand.
BOM_VENDOR_LINKS = [
    ("BOM:1.2.1", "NVIDIA", "designer", "confirmed_company_role", "SRC_NVIDIA_5080"),
    ("BOM:1.2.1", "TSMC", "foundry", "confirmed_company_role_candidate_facility", "SRC_NVIDIA_SUPPLY;SRC_TSMC_FABS"),
    ("BOM:1.2.2", "Kinsus", "package substrate", "confirmed_partner_candidate_product", "SRC_NVIDIA_SUPPLY"),
    ("BOM:1.2.2", "IBIDEN", "package substrate", "confirmed_capability_candidate_product", "SRC_NVIDIA_SUPPLY"),
    ("BOM:1.3", "Samsung Electronics", "GDDR7", "confirmed_capability", "SRC_SAMSUNG_GDDR7"),
    ("BOM:1.3", "SK hynix", "GDDR7", "confirmed_capability", "SRC_SK_GDDR7"),
    ("BOM:1.3", "Micron", "GDDR7", "confirmed_capability", "SRC_MICRON_GDDR7"),
    ("BOM:1.1", "Compeq", "multilayer PCB", "confirmed_capability_candidate_product", "SRC_COMPEQ_PLANTS"),
    ("BOM:8.2.1", "Compeq", "multilayer PCB", "confirmed_capability_candidate_product", "SRC_COMPEQ_PLANTS"),
    ("BOM:1.1", "Global Brands Manufacture", "multilayer PCB", "confirmed_capability_candidate_product", "SRC_GBM_SITES"),
    ("BOM:8.2.1", "Global Brands Manufacture", "multilayer PCB", "confirmed_capability_candidate_product", "SRC_GBM_SITES"),
    ("BOM:1.4.1", "Infineon", "integrated power stage", "confirmed_capability", "SRC_INFINEON_POWER"),
    ("BOM:1.4.1", "Monolithic Power Systems", "accelerator-card power", "confirmed_capability", "SRC_MPS_GPU"),
    ("BOM:1.4.2", "TDK", "power inductor", "confirmed_category_capability", "SRC_TDK_PLANTS"),
    ("BOM:1.4.3", "Murata", "passive components", "confirmed_category_capability", "SRC_MURATA_WUXI"),
    ("BOM:1.6", "Murata", "passive components", "confirmed_category_capability", "SRC_MURATA_WUXI"),
    ("BOM:8.2.3", "Murata", "passive components", "confirmed_category_capability", "SRC_MURATA_WUXI"),
    ("BOM:1.4.3", "TDK", "passive components", "confirmed_category_capability", "SRC_TDK_PLANTS"),
    ("BOM:1.6", "TDK", "passive components", "confirmed_category_capability", "SRC_TDK_PLANTS"),
    ("BOM:2.1", "Auras Technology", "vapor chamber", "confirmed_capability_candidate_product", "SRC_AURAS"),
    ("BOM:2.2", "Auras Technology", "heat pipe", "confirmed_capability_candidate_product", "SRC_AURAS"),
    ("BOM:2.3", "Auras Technology", "thermal module/fin stack", "confirmed_capability_candidate_product", "SRC_AURAS"),
    ("BOM:2.4", "SUNON", "fan and motor", "confirmed_capability_candidate_product", "SRC_SUNON"),
    ("BOM:5.1", "Amphenol", "PCIe auxiliary power connector", "confirmed_capability", "SRC_AMPHENOL_PCIE"),
    ("BOM:5.2", "Amphenol", "PCIe power-connector sense contacts", "confirmed_capability", "SRC_AMPHENOL_PCIE"),
    ("BOM:6.3", "Nexperia", "HDMI/DisplayPort ESD protection", "confirmed_capability", "SRC_NEXPERIA_ESD"),
    ("BOM:8.2.2", "Nuvoton", "microcontroller", "confirmed_capability", "SRC_NUVOTON_MCU"),
]


# Three-point manufacturing durations are transparent scenario inputs, not
# confidential factory cycle-time measurements.  They deliberately remain
# separate from sourced vendor/facility facts.
MANUFACTURING_TIMES = [
    ("ETO:N0", "Semiconductor design program", 30, 90, 180, "days", "assumption", "Program duration varies radically; exclude it for steady-state replenishment analysis."),
    ("MODEL:FABRICATION", "Advanced logic wafer fabrication", 60, 90, 120, "days", "assumption_calibrated_to_existing_model", "Cycle time covers a representative leading-edge wafer-fab flow, not queue time or design."),
    ("MODEL:ATP", "Logic-device assembly, packaging and test", 7, 14, 28, "days", "assumption_calibrated_to_existing_model", "Includes packaging and final test after the bare die and packaging materials are available."),
    ("BOM:1.3", "GDDR fabrication and package", 45, 70, 100, "days", "assumption_calibrated_to_existing_model", "Representative memory production cycle; not a supplier quote."),
    ("BOM:1.2.2", "Package substrate", 20, 35, 60, "days", "assumption_calibrated_to_existing_model", "Representative production cycle; qualification and backlog are separate."),
    ("BOM:1.1", "Bare multilayer PCB", 5, 10, 20, "days", "assumption", "Fabrication only; excludes component procurement and final board assembly."),
    ("BOM:1", "Graphics-card PCB assembly and test", 1, 3, 7, "days", "assumption", "SMT, inspection and board test after all components arrive."),
    ("BOM:1.4", "VRM components", 10, 21, 45, "days", "assumption", "Production/availability proxy; actual lead time is order- and inventory-dependent."),
    ("BOM:2", "Cooling module", 7, 14, 30, "days", "assumption", "Fabrication and assembly of vapor chamber, pipes, fins and fans."),
    ("BOM:3", "Backplate and bracket metalwork", 3, 7, 14, "days", "assumption", "Forming, finishing and inspection."),
    ("BOM:5", "Power connector assembly", 5, 14, 30, "days", "assumption", "Production/availability proxy, not a quoted lead time."),
    ("BOM:6", "Display connector cluster", 5, 14, 30, "days", "assumption", "Production/availability proxy, not a quoted lead time."),
    ("BOM:7", "Injection-molded shroud", 3, 7, 14, "days", "assumption", "Assumes tooling already exists."),
    ("BOM:8", "RGB lighting assembly", 3, 7, 14, "days", "assumption", "Small PCB assembly after parts are available."),
]


LOGISTICS_HUBS = [
    ("HUB:TPE", "Taiwan Taoyuan International Airport", "airport", "Taiwan", 25.0797, 121.2342),
    ("HUB:KHH", "Kaohsiung International Airport", "airport", "Taiwan", 22.5771, 120.3500),
    ("HUB:KEL", "Port of Keelung", "port", "Taiwan", 25.1322, 121.7460),
    ("HUB:KHG", "Port of Kaohsiung", "port", "Taiwan", 22.6133, 120.2881),
    ("HUB:ICN", "Incheon International Airport", "airport", "South Korea", 37.4602, 126.4407),
    ("HUB:PUS", "Port of Busan", "port", "South Korea", 35.1028, 129.0403),
    ("HUB:NRT", "Narita International Airport", "airport", "Japan", 35.7720, 140.3929),
    ("HUB:NGO", "Chubu Centrair International Airport", "airport", "Japan", 34.8584, 136.8054),
    ("HUB:NGO_PORT", "Port of Nagoya", "port", "Japan", 35.0350, 136.8400),
    ("HUB:FRA", "Frankfurt Airport", "airport", "Germany", 50.0379, 8.5622),
    ("HUB:HAM_PORT", "Port of Hamburg", "port", "Germany", 53.5461, 9.9661),
    ("HUB:DTW", "Detroit Metropolitan Airport", "airport", "United States", 42.2162, -83.3554),
    ("HUB:LAX", "Los Angeles International Airport", "airport", "United States", 33.9416, -118.4085),
    ("HUB:SFO", "San Francisco International Airport", "airport", "United States", 37.6213, -122.3790),
    ("HUB:KUL", "Kuala Lumpur International Airport", "airport", "Malaysia", 2.7456, 101.7072),
    ("HUB:PKG", "Port Klang", "port", "Malaysia", 3.0000, 101.4000),
    ("HUB:PVG", "Shanghai Pudong International Airport", "airport", "China", 31.1443, 121.8083),
    ("HUB:SHA_PORT", "Port of Shanghai", "port", "China", 31.3500, 121.7000),
    ("HUB:SZX", "Shenzhen Bao'an International Airport", "airport", "China", 22.6393, 113.8107),
    ("HUB:YTN", "Yantian Port", "port", "China", 22.5780, 114.2720),
]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not columns:
        raise ValueError(f"Cannot infer columns for empty output: {path}")
    fieldnames = columns or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_eto_files(refresh: bool) -> None:
    ETO_DIR.mkdir(parents=True, exist_ok=True)
    for stem in ETO_FILES:
        path = ETO_DIR / f"eto_{stem}.csv"
        if path.exists() and not refresh:
            continue
        url = f"{ETO_BASE}/{stem}.csv"
        req = urllib.request.Request(url, headers={"User-Agent": "gpu-supply-chain-student-project/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            path.write_bytes(response.read())


def load_upstream_module() -> dict:
    if not UPSTREAM_MODULE.exists():
        return {"materials": [], "facilities": [], "edges": [], "sources": []}
    script = textwrap.dedent(
        f"""
        import {{upstreamMaterials, upstreamFacilities, upstreamSources}}
          from {json.dumps(UPSTREAM_MODULE.as_uri())};
        process.stdout.write(JSON.stringify({{
          materials: upstreamMaterials,
          facilities: upstreamFacilities,
          edges: [],
          sources: upstreamSources
        }}));
        """
    )
    node_executable = shutil.which("node") or "/Users/lt/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    if not Path(node_executable).exists():
        return {"materials": [], "facilities": [], "edges": [], "sources": []}
    result = subprocess.run(
        [node_executable, "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def normalize_bom(bom: dict) -> tuple[list[dict], list[dict]]:
    nodes = []
    for row in bom["grouped_graph"]["nodes"]:
        nodes.append(
            {
                "node_id": f"BOM:{row['id']}",
                "namespace": "BOMWiki",
                "source_record_id": row["id"],
                "name": row["name"],
                "node_type": row["type"],
                "stage": "graphics_card_bom",
                "bom_level": row.get("layer", ""),
                "quantity_per_parent": row.get("qty_per_assy", ""),
                "extended_quantity": row.get("ext_qty", ""),
                "description": "",
                "scope_status": "included",
                "source_ids": "SRC_BOMWIKI_GPU",
            }
        )
    edges = []
    for index, row in enumerate(bom["grouped_graph"]["edges"], 1):
        # Reverse the page's parent->child orientation for supply flow:
        # component -> assembly.  The relationship remains structural, not a
        # manufacturing-time edge.
        edges.append(
            {
                "edge_id": f"BOM_E{index:03d}",
                "from_node": f"BOM:{row['target']}",
                "to_node": f"BOM:{row['source']}",
                "relationship": "component_of",
                "edge_class": "bom_structure",
                "requirement_status": "required_quantity_in_reference_bom",
                "quantity": row.get("qty_per_assy", ""),
                "evidence_level": "secondary_structure",
                "source_ids": "SRC_BOMWIKI_GPU",
                "note": "Repeated quantity is stored on one grouped component node; it is not expanded into separate supplier nodes.",
            }
        )
    return nodes, edges


def normalize_eto() -> tuple[list[dict], list[dict], list[dict], list[dict], set[str]]:
    inputs = read_csv(ETO_DIR / "eto_inputs.csv")
    sequence = read_csv(ETO_DIR / "eto_sequence.csv")
    provision = read_csv(ETO_DIR / "eto_provision.csv")
    providers = read_csv(ETO_DIR / "eto_providers.csv")

    graph = nx.DiGraph()
    for row in sequence:
        if row.get("goes_into_id"):
            graph.add_edge(row["input_id"], row["goes_into_id"])
        elif row.get("is_type_of_id"):
            graph.add_edge(row["input_id"], row["is_type_of_id"])

    # Preserve the complete ETO dataset in the clean database.  The separate
    # project-focus tables below select only the hierarchy specified in
    # gpu.xlsx ATP!R:AM, so the research data remain intact without cluttering
    # the construction view.
    relevant = {row["input_id"] for row in inputs}

    nodes = []
    for row in inputs:
        if row["input_id"] not in relevant:
            continue
        nodes.append(
            {
                "node_id": f"ETO:{row['input_id']}",
                "namespace": "ETO",
                "source_record_id": row["input_id"],
                "name": row["input_name"],
                "node_type": row["type"],
                "stage": row.get("stage_name", ""),
                "bom_level": "",
                "quantity_per_parent": "",
                "extended_quantity": "",
                "description": row.get("description", ""),
                "scope_status": "eto_full_dataset",
                "source_ids": "SRC_ETO_2026",
            }
        )

    edges = []
    for index, row in enumerate(sequence, 1):
        if row["input_id"] not in relevant:
            continue
        target = row.get("goes_into_id") or row.get("is_type_of_id")
        if not target or target not in relevant:
            continue
        relation = "goes_into" if row.get("goes_into_id") else "is_type_of"
        edges.append(
            {
                "edge_id": f"ETO_E{index:03d}",
                "from_node": f"ETO:{row['input_id']}",
                "to_node": f"ETO:{target}",
                "relationship": relation,
                "edge_class": "process_flow" if relation == "goes_into" else "taxonomy",
                "requirement_status": "logical_input_or_predecessor" if relation == "goes_into" else "alternative_or_subtype_not_all_required",
                "quantity": "",
                "evidence_level": "curated_research_dataset",
                "source_ids": "SRC_ETO_2026",
                "note": "ETO relationship; taxonomy members must not be interpreted as all simultaneously required.",
            }
        )
    provider_by_id = {row["provider_id"]: row for row in providers}
    provider_rows = []
    provider_links = []
    retained_provider_ids = set()
    for index, row in enumerate(provision, 1):
        if row["provided_id"] not in relevant:
            continue
        retained_provider_ids.add(row["provider_id"])
        provider_links.append(
            {
                "link_id": f"ETO_P{index:04d}",
                "provider_id": f"ETO_PROVIDER:{row['provider_id']}",
                "component_node_id": f"ETO:{row['provided_id']}",
                "role": "provider",
                "market_share_percent": row.get("share_provided", ""),
                "market_share_year": row.get("year", ""),
                "evidence_level": "curated_research_dataset",
                "source_ids": "SRC_ETO_2026",
                "source_detail": row.get("source", ""),
            }
        )
    for provider_id in sorted(retained_provider_ids):
        row = provider_by_id.get(provider_id, {})
        provider_rows.append(
            {
                "provider_id": f"ETO_PROVIDER:{provider_id}",
                "provider_name": row.get("provider_name", ""),
                "provider_type": row.get("provider_type", ""),
                "headquarters_country": row.get("country", ""),
                "facility_status": "headquarters_only_not_factory_location",
                "source_ids": "SRC_ETO_2026",
            }
        )
    return nodes, edges, provider_rows, provider_links, relevant


def build_project_focus_hierarchy(eto_nodes: list[dict], bom_nodes: list[dict]) -> tuple[list[dict], list[dict]]:
    """Build the exact hierarchy specified in gpu.xlsx ATP!R:AM.

    The workbook calls the ATP output a "finished logic die."  We preserve
    that project label while documenting that industry usage would normally
    call the post-packaging/test output a packaged and tested logic device.
    """
    eto_by_id = {row["source_record_id"]: row for row in eto_nodes}
    bom_by_id = {row["source_record_id"]: row for row in bom_nodes}

    model_nodes = [
        {
            "node_id": "MODEL:FINISHED_LOGIC_DIE",
            "namespace": "Project model",
            "source_record_id": "ATP!X4 / gpu supply chain!E5",
            "name": "Finished logic die",
            "node_type": "intermediate_output",
            "stage": "ATP",
            "bom_level": "logic-die detail",
            "quantity_per_parent": 1,
            "extended_quantity": 1,
            "description": "Project-team label for the output after assembly, packaging and testing; technically this is a packaged and tested logic device.",
            "scope_status": "canonical_project_focus",
            "source_ids": "SRC_GPU_WORKBOOK_ATP",
        },
        {
            "node_id": "MODEL:ATP",
            "namespace": "Project model",
            "source_record_id": "ATP!S4:X5",
            "name": "Assembly, packaging, and testing",
            "node_type": "process",
            "stage": "ATP",
            "bom_level": "logic-die detail",
            "quantity_per_parent": "",
            "extended_quantity": "",
            "description": "Consumes electronic gases, packaging materials and the bare logic die to produce the finished logic-die output in the project hierarchy.",
            "scope_status": "canonical_project_focus",
            "source_ids": "SRC_GPU_WORKBOOK_ATP;SRC_ETO_2026",
        },
        {
            "node_id": "MODEL:BARE_LOGIC_DIE",
            "namespace": "Project model",
            "source_record_id": "ATP!X4 logic die input",
            "name": "Logic die (fabricated, before ATP)",
            "node_type": "intermediate_input",
            "stage": "Fabrication output",
            "bom_level": "logic-die detail",
            "quantity_per_parent": 1,
            "extended_quantity": 1,
            "description": "Bare fabricated logic die used as an input to ATP.",
            "scope_status": "canonical_project_focus",
            "source_ids": "SRC_GPU_WORKBOOK_ATP;SRC_ETO_2026",
        },
        {
            "node_id": "MODEL:FABRICATION",
            "namespace": "Project model",
            "source_record_id": "ATP!S22:AM23",
            "name": "Fabrication",
            "node_type": "process",
            "stage": "Fabrication",
            "bom_level": "logic-die detail",
            "quantity_per_parent": "",
            "extended_quantity": "",
            "description": "Project-level fabrication process fed by the eight material categories listed in the ATP sheet.",
            "scope_status": "canonical_project_focus",
            "source_ids": "SRC_GPU_WORKBOOK_ATP;SRC_ETO_2026",
        },
    ]

    custom_children = {
        "ETO:N91": [
            "Nitrogen", "Hydrogen", "Helium", "Argon", "Carbon dioxide", "Nitrogen trifluoride",
            "Tungsten hexafluoride", "Hydrogen chloride", "Ammonia", "Disilane", "Germane",
            "Nitrous oxide", "Neon", "Krypton",
        ],
        "ETO:N100": ["Interconnect materials", "Solder balls", "Plastic substrate"],
        "ETO:N90": ["Chemical slurries", "Rare-earth mineral inputs", "Polishing pads"],
        "ETO:N26": [
            "Quartzite / silica sand", "Carbon source (coal, coke, or wood chips)", "Graphite electrodes",
            "Metallurgical-grade silicon", "High-purity polysilicon slim starter rods", "Anhydrous HCl",
            "Trichlorosilane", "Ultra-pure hydrogen", "P-type or n-type dopants", "Ultra-pure argon",
            "High-purity synthetic fused-quartz crucible", "Deionized-water coolant",
            "Diamond/SiC abrasive slurry and glycol carrier", "Alumina", "SiC lapping slurry", "Colloidal silica",
        ],
        "ETO:N92": [
            "Sulfuric acid", "Isopropyl alcohol", "Ammonium hydroxide", "Phosphoric acid",
            "Nitric acid", "Hydrochloric acid", "Acetic acid",
        ],
        "ETO:N88": ["Sputtering targets", "Aluminum", "Copper", "Tantalum", "Titanium"],
    }
    for parent, names in custom_children.items():
        prefix = parent.split(":", 1)[1]
        for index, name in enumerate(names, 1):
            model_nodes.append(
                {
                    "node_id": f"DETAIL:{prefix}:{index:02d}",
                    "namespace": "Project workbook detail",
                    "source_record_id": f"ATP detail under {prefix}",
                    "name": name,
                    "node_type": "listed_subcategory_or_input",
                    "stage": "ATP" if parent in {"ETO:N91", "ETO:N100"} else "Fabrication",
                    "bom_level": "material detail",
                    "quantity_per_parent": "",
                    "extended_quantity": "",
                    "description": "Listed under the parent category in gpu.xlsx ATP sheet columns R:AM.",
                    "scope_status": "canonical_project_focus",
                    "source_ids": "SRC_GPU_WORKBOOK_ATP",
                }
            )

    def edge(edge_id: str, source: str, target: str, relationship: str, note: str = "") -> dict:
        return {
            "edge_id": edge_id,
            "from_node": source,
            "to_node": target,
            "relationship": relationship,
            "edge_class": "project_focus_hierarchy",
            "requirement_status": "listed_as_necessary_input" if relationship != "listed_under" else "listed_detail_not_separately_quantified",
            "quantity": "",
            "evidence_level": "team_defined_structure",
            "source_ids": "SRC_GPU_WORKBOOK_ATP",
            "note": note,
        }

    focus_edges = [
        edge("FOCUS_001", "MODEL:ATP", "MODEL:FINISHED_LOGIC_DIE", "process_produces"),
        edge("FOCUS_002", "ETO:N91", "MODEL:ATP", "necessary_input"),
        edge("FOCUS_003", "ETO:N100", "MODEL:ATP", "necessary_input"),
        edge("FOCUS_004", "MODEL:BARE_LOGIC_DIE", "MODEL:ATP", "necessary_input"),
        edge("FOCUS_005", "MODEL:FABRICATION", "MODEL:BARE_LOGIC_DIE", "process_produces"),
        edge("FOCUS_006", "ETO:N90", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_007", "ETO:N91", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_008", "ETO:N126", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_009", "ETO:N26", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_010", "ETO:N92", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_011", "ETO:N31", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_012", "ETO:N33", "MODEL:FABRICATION", "necessary_input"),
        edge("FOCUS_013", "ETO:N88", "MODEL:FABRICATION", "necessary_input"),
        edge(
            "FOCUS_014", "MODEL:FINISHED_LOGIC_DIE", "BOM:1.2.1", "details_bom_node",
            "This follows the team's requested mapping to the JSON GPU Die node. The terminology note on MODEL:FINISHED_LOGIC_DIE records the package/die distinction.",
        ),
        # ETO-defined packaging material subtypes, matching the workbook text.
        edge("FOCUS_015", "ETO:N93", "ETO:N100", "listed_under"),
        edge("FOCUS_016", "ETO:N94", "ETO:N100", "listed_under"),
        edge("FOCUS_017", "ETO:N96", "ETO:N100", "listed_under"),
        edge("FOCUS_018", "ETO:N97", "ETO:N100", "listed_under"),
        edge("FOCUS_019", "ETO:N98", "ETO:N100", "listed_under"),
        # ETO-defined process-specific fabrication material variants.
        edge("FOCUS_020", "ETO:N90", "ETO:N126", "listed_under"),
        edge("FOCUS_021", "ETO:N88", "ETO:N126", "listed_under"),
        edge("FOCUS_022", "ETO:N33", "ETO:N126", "listed_under"),
        edge("FOCUS_023", "ETO:N31", "ETO:N126", "listed_under"),
    ]
    counter = 24
    for parent, names in custom_children.items():
        prefix = parent.split(":", 1)[1]
        for index, _ in enumerate(names, 1):
            focus_edges.append(edge(f"FOCUS_{counter:03d}", f"DETAIL:{prefix}:{index:02d}", parent, "listed_under"))
            counter += 1

    selected_ids = {x["node_id"] for x in model_nodes}
    selected_ids |= {e["from_node"] for e in focus_edges} | {e["to_node"] for e in focus_edges}
    source_nodes = {n["node_id"]: n for n in eto_nodes + bom_nodes}
    focus_nodes = [source_nodes[node_id] for node_id in sorted(selected_ids) if node_id in source_nodes] + model_nodes
    return focus_nodes, focus_edges


def add_bom_vendors(provider_rows: list[dict], provider_links: list[dict]) -> None:
    names = sorted({row[1] for row in BOM_VENDOR_LINKS})
    id_by_name = {name: f"BOM_PROVIDER:{index:03d}" for index, name in enumerate(names, 1)}
    for name in names:
        provider_rows.append(
            {
                "provider_id": id_by_name[name],
                "provider_name": name,
                "provider_type": "organization",
                "headquarters_country": "",
                "facility_status": "see_facility_table_or_unresolved",
                "source_ids": ";".join(sorted({x[4] for x in BOM_VENDOR_LINKS if x[1] == name})),
            }
        )
    for index, (node_id, name, role, evidence, source_ids) in enumerate(BOM_VENDOR_LINKS, 1):
        provider_links.append(
            {
                "link_id": f"BOM_P{index:03d}",
                "provider_id": id_by_name[name],
                "component_node_id": node_id,
                "role": role,
                "market_share_percent": "",
                "market_share_year": "",
                "evidence_level": evidence,
                "source_ids": source_ids,
                "source_detail": "Candidate supplier mapping based on official capability/partner evidence; not a purchase-order claim.",
            }
        )


def normalize_base_facilities() -> list[dict]:
    if not BASE_FACILITIES.exists():
        return []
    rows = []
    for row in read_csv(BASE_FACILITIES):
        rows.append(
            {
                "facility_id": f"BASE:{row['node_id']}",
                "facility_name": row["name"],
                "company": row.get("company", ""),
                "country": row.get("country", ""),
                "city": row.get("city", ""),
                "address": row.get("address", ""),
                "latitude": row.get("latitude", ""),
                "longitude": row.get("longitude", ""),
                "facility_type": row.get("node_type", ""),
                "coordinate_precision": row.get("coordinate_precision", ""),
                "component_categories": row.get("role", ""),
                "capability_evidence": row.get("role", ""),
                "product_assignment": row.get("product_assignment", ""),
                "evidence_level": row.get("evidence_level", ""),
                "source_ids": row.get("source_ids", ""),
                "confidence": row.get("coordinate_precision", ""),
            }
        )
    return rows


def normalize_upstream(upstream: dict) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    material_columns = [
        "material_id", "material_name", "tier", "feeds_process", "function", "eto_mapping",
        "prior_status", "current_status", "facility_count", "company_count", "gap", "confidence",
    ]
    facility_columns = [
        "facility_id", "facility_name", "company", "country", "city", "address", "latitude",
        "longitude", "coordinate_precision", "component_categories", "capability_evidence",
        "product_assignment", "evidence_level", "source_ids", "confidence",
    ]
    edge_columns = [
        "edge_id", "from_node", "to_node", "relationship", "edge_class", "requirement_status",
        "quantity", "evidence_level", "source_ids", "note",
    ]
    source_columns = [
        "source_id", "organization", "title", "url", "use", "reliability", "note", "accessed_date",
    ]
    materials = [dict(zip(material_columns, row)) for row in upstream.get("materials", [])]
    facilities = [dict(zip(facility_columns, row)) for row in upstream.get("facilities", [])]
    edges = [dict(zip(edge_columns, row)) for row in upstream.get("edges", [])]
    sources = [dict(zip(source_columns, row)) for row in upstream.get("sources", [])]
    return materials, facilities, edges, sources


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def build_transport_edges(facilities: list[dict]) -> tuple[list[dict], list[dict]]:
    hubs = [
        {
            "hub_id": hub_id,
            "hub_name": name,
            "hub_type": hub_type,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "source_ids": "SRC_OSM",
        }
        for hub_id, name, hub_type, country, lat, lon in LOGISTICS_HUBS
    ]
    by_type = {
        kind: [x for x in hubs if x["hub_type"] == kind]
        for kind in ("airport", "port")
    }
    edges: list[dict] = []

    # Every geocoded physical factory gets candidate first/last-mile links to
    # its nearest airport and port.  These are geography-based options, not
    # evidence of a real carrier contract.
    for facility in facilities:
        if facility.get("facility_type") in {"airport", "port", "testing"}:
            continue
        try:
            lat = float(facility["latitude"])
            lon = float(facility["longitude"])
        except (TypeError, ValueError, KeyError):
            continue
        for kind in ("airport", "port"):
            nearest = min(
                by_type[kind],
                key=lambda hub: haversine_km(lat, lon, float(hub["latitude"]), float(hub["longitude"])),
            )
            distance = haversine_km(lat, lon, float(nearest["latitude"]), float(nearest["longitude"])) * 1.25
            travel_days = distance / 60.0 / 24.0
            edges.append(
                {
                    "route_id": f"ROUTE:{facility['facility_id']}->{nearest['hub_id']}",
                    "from_node": facility["facility_id"],
                    "to_node": nearest["hub_id"],
                    "mode": "road",
                    "distance_km": round(distance, 1),
                    "travel_days": round(travel_days, 3),
                    "handling_days": 0.25,
                    "baseline_lead_days": round(travel_days + 0.25, 3),
                    "method": "nearest hub; great-circle x1.25 / 60 km/h",
                    "evidence_level": "modeled_geographic_option",
                    "source_ids": "SRC_OSM;SRC_OSRM",
                    "note": "Candidate first/last-mile route. Replace with OSRM road route and a carrier schedule for operational use.",
                }
            )

    # Candidate international connections into Taiwan and a final example
    # outbound connection to SFO.  Air/sea speeds are transparent assumptions.
    taiwan_air = next(x for x in hubs if x["hub_id"] == "HUB:TPE")
    taiwan_port = next(x for x in hubs if x["hub_id"] == "HUB:KHG")
    for hub in hubs:
        if hub["hub_type"] == "airport" and hub["hub_id"] not in {"HUB:TPE", "HUB:KHH"}:
            distance = haversine_km(float(hub["latitude"]), float(hub["longitude"]), float(taiwan_air["latitude"]), float(taiwan_air["longitude"])) * 1.05
            travel = distance / 750.0 / 24.0
            edges.append(
                {
                    "route_id": f"ROUTE:{hub['hub_id']}->HUB:TPE",
                    "from_node": hub["hub_id"],
                    "to_node": "HUB:TPE",
                    "mode": "air",
                    "distance_km": round(distance, 1),
                    "travel_days": round(travel, 3),
                    "handling_days": 1.0,
                    "baseline_lead_days": round(travel + 1.0, 3),
                    "method": "great-circle x1.05 / 750 km/h",
                    "evidence_level": "modeled_geographic_option",
                    "source_ids": "SRC_OSM",
                    "note": "No live flight, capacity, customs or weather schedule is used.",
                }
            )
        if hub["hub_type"] == "port" and hub["hub_id"] not in {"HUB:KEL", "HUB:KHG"}:
            distance = haversine_km(float(hub["latitude"]), float(hub["longitude"]), float(taiwan_port["latitude"]), float(taiwan_port["longitude"])) * 1.10
            travel = distance / 30.0 / 24.0
            edges.append(
                {
                    "route_id": f"ROUTE:{hub['hub_id']}->HUB:KHG",
                    "from_node": hub["hub_id"],
                    "to_node": "HUB:KHG",
                    "mode": "sea",
                    "distance_km": round(distance, 1),
                    "travel_days": round(travel, 3),
                    "handling_days": 1.5,
                    "baseline_lead_days": round(travel + 1.5, 3),
                    "method": "great-circle x1.10 / 30 km/h",
                    "evidence_level": "modeled_geographic_option",
                    "source_ids": "SRC_OSM",
                    "note": "No liner schedule, transshipment, capacity, customs or weather delay is used.",
                }
            )
    return hubs, edges


def build_focus_input_coverage(
    nodes: list[dict],
    providers: list[dict],
    provider_links: list[dict],
    upstream_materials: list[dict],
    facilities: list[dict],
) -> list[dict]:
    focus_input_ids = ["ETO:N90", "ETO:N91", "ETO:N126", "ETO:N26", "ETO:N92", "ETO:N31", "ETO:N33", "ETO:N88", "ETO:N100"]
    node_by_id = {row["node_id"]: row for row in nodes}
    provider_by_id = {row["provider_id"]: row for row in providers}
    links_by_node: dict[str, list[dict]] = defaultdict(list)
    for row in provider_links:
        links_by_node[row["component_node_id"]].append(row)

    material_map = {
        "ETO:N26": ["MAT_WAFER", "MAT_POLYSILICON"],
        "ETO:N31": ["MAT_PHOTORESIST"],
        "ETO:N33": ["MAT_PHOTOMASK"],
        "ETO:N90": ["MAT_WET_CHEM_CMP"],
        "ETO:N91": ["MAT_E_GASES"],
        "ETO:N92": ["MAT_WET_CHEM_CMP"],
        "ETO:N88": ["MAT_PRECURSORS"],
        "ETO:N100": ["MAT_UNDERFILL", "MAT_ABF", "MAT_GLASS_CLOTH", "MAT_COPPER_FOIL"],
        "ETO:N126": ["MAT_WET_CHEM_CMP", "MAT_PRECURSORS", "MAT_PHOTOMASK", "MAT_PHOTORESIST"],
    }
    provider_expansion = {
        "ETO:N126": ["ETO:N90", "ETO:N88", "ETO:N33", "ETO:N31"],
        "ETO:N100": ["ETO:N93", "ETO:N94", "ETO:N95", "ETO:N96", "ETO:N97", "ETO:N98"],
    }
    material_by_id = {row["material_id"]: row for row in upstream_materials}
    rows = []
    for node_id in focus_input_ids:
        direct_links = links_by_node.get(node_id, [])
        links = direct_links[:]
        for child_id in provider_expansion.get(node_id, []):
            links.extend(links_by_node.get(child_id, []))
        organization_links = [
            row for row in links
            if provider_by_id.get(row["provider_id"], {}).get("provider_type") == "organization"
        ]
        ranked = sorted(
            organization_links,
            key=lambda row: float(row["market_share_percent"]) if str(row.get("market_share_percent", "")).strip() not in {"", "None"} else -1,
            reverse=True,
        )
        provider_labels = []
        for link in ranked[:8]:
            name = provider_by_id.get(link["provider_id"], {}).get("provider_name", link["provider_id"])
            share = str(link.get("market_share_percent", "")).strip()
            provider_labels.append(f"{name} ({share}%)" if share else name)
        material_ids = material_map.get(node_id, [])
        facility_count = 0
        for facility in facilities:
            cats = str(facility.get("component_categories", ""))
            if any(material_id in cats for material_id in material_ids):
                facility_count += 1
        rows.append(
            {
                "component_node_id": node_id,
                "component_name": node_by_id[node_id]["name"],
                "direct_eto_provider_rows": len(direct_links),
                "expanded_provider_rows": len(links),
                "organization_provider_rows": len(organization_links),
                "top_organization_candidates": "; ".join(provider_labels),
                "curated_material_extensions": ";".join(material_ids),
                "curated_facility_candidates": facility_count,
                "provider_source_ids": "SRC_ETO_2026",
                "facility_evidence_note": "Facility candidates confirm site capability; exact product/customer allocation is usually not public.",
            }
        )
    return rows


def make_dependency_figure(nodes: list[dict], edges: list[dict], output: Path) -> None:
    """Draw the exact team hierarchy from the ATP sheet."""
    output.parent.mkdir(parents=True, exist_ok=True)
    by_id = {node["node_id"]: node for node in nodes}
    fig, ax = plt.subplots(figsize=(22, 14))
    ax.axis("off")
    process_ids = ["MODEL:FABRICATION", "MODEL:BARE_LOGIC_DIE", "MODEL:ATP", "MODEL:FINISHED_LOGIC_DIE", "BOM:1.2.1"]
    positions: dict[str, tuple[float, float]] = {
        "MODEL:FABRICATION": (0.50, 0.52),
        "MODEL:BARE_LOGIC_DIE": (0.50, 0.66),
        "MODEL:ATP": (0.50, 0.78),
        "MODEL:FINISHED_LOGIC_DIE": (0.50, 0.88),
        "BOM:1.2.1": (0.50, 0.97),
    }
    fabrication_inputs = ["ETO:N90", "ETO:N91", "ETO:N126", "ETO:N26", "ETO:N92", "ETO:N31", "ETO:N33", "ETO:N88"]
    for idx, node_id in enumerate(fabrication_inputs):
        positions[node_id] = (0.08 + idx * 0.12, 0.36)
    positions["ETO:N100"] = (0.78, 0.68)
    # Detail nodes are placed in compact columns below their parent categories.
    detail_by_parent: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge["relationship"] == "listed_under" and edge["from_node"].startswith("DETAIL:"):
            detail_by_parent[edge["to_node"]].append(edge["from_node"])
    for parent, child_ids in detail_by_parent.items():
        px, _ = positions.get(parent, (0.5, 0.35))
        for idx, child_id in enumerate(child_ids):
            col_shift = (idx % 2) * 0.045 - 0.0225
            row = idx // 2
            positions[child_id] = (px + col_shift, 0.28 - row * 0.033)

    # ETO packaging subtypes and process-specific variants get a small second row.
    packaging_subtypes = ["ETO:N93", "ETO:N94", "ETO:N96", "ETO:N97", "ETO:N98"]
    for idx, node_id in enumerate(packaging_subtypes):
        positions[node_id] = (0.60 + idx * 0.095, 0.59)

    # Draw only edges whose endpoints have positions to keep the diagram readable.
    for edge in edges:
        if edge["from_node"] not in positions or edge["to_node"] not in positions:
            continue
        x1, y1 = positions[edge["from_node"]]
        x2, y2 = positions[edge["to_node"]]
        color = "#999999" if edge["relationship"] == "listed_under" else "#555555"
        width = 0.7 if edge["relationship"] == "listed_under" else 1.7
        ax.annotate("", xy=(x2, y2 - 0.016), xytext=(x1, y1 + 0.016), arrowprops=dict(arrowstyle="-|>", lw=width, color=color, alpha=0.7), zorder=1)

    def node_style(node_id: str) -> tuple[str, int]:
        if node_id == "BOM:1.2.1":
            return "#E15759", 10
        if node_id.startswith("MODEL:"):
            return "#4C78A8", 9
        if node_id.startswith("DETAIL:"):
            return "#DCEBD8", 6
        return "#59A14F", 8

    for node_id, (x, y) in positions.items():
        if node_id not in by_id:
            continue
        color, fontsize = node_style(node_id)
        label = by_id[node_id]["name"]
        wrap_width = 19 if node_id.startswith("DETAIL:") else 22
        if len(label) > wrap_width:
            label = "\n".join(textwrap.wrap(label, wrap_width))
        text_color = "#222222" if node_id.startswith("DETAIL:") else "white"
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            color=text_color,
            fontsize=fontsize,
            fontweight="bold" if not node_id.startswith("DETAIL:") else "normal",
            bbox=dict(boxstyle="round,pad=0.38", facecolor=color, edgecolor="white", linewidth=1.0),
            zorder=4,
        )

    ax.text(0.02, 0.02, "Hierarchy follows gpu.xlsx ATP!R:AM. The workbook's ‘finished logic die’ label is preserved; the database records the industry terminology caveat.\nRepeated gases can feed both fabrication and ATP. Process-specific fabrication materials are a grouping of CMP, deposition, photomask and photoresist categories.", fontsize=10, color="#555555", va="bottom")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    fig.suptitle("Project GPU logic-die construction hierarchy", fontsize=20, fontweight="bold", y=0.995)
    fig.tight_layout()
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_world_geojson(cache_path: Path) -> dict | None:
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    try:
        if not cache_path.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "gpu-supply-chain-student-project/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_bytes(response.read())
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def make_transport_figure(facilities: list[dict], hubs: list[dict], routes: list[dict], output: Path, cache_dir: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(20, 11))
    world = load_world_geojson(cache_dir / "natural_earth_countries.geojson")
    if world:
        for feature in world.get("features", []):
            geom = feature.get("geometry") or {}
            coords = geom.get("coordinates", [])
            polygons = [coords] if geom.get("type") == "Polygon" else coords if geom.get("type") == "MultiPolygon" else []
            for polygon in polygons:
                if not polygon:
                    continue
                ring = polygon[0]
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                ax.fill(xs, ys, color="#F1F1F1", edgecolor="#CCCCCC", linewidth=0.35, zorder=0)

    coords: dict[str, tuple[float, float]] = {}
    for row in facilities:
        try:
            coords[row["facility_id"]] = (float(row["longitude"]), float(row["latitude"]))
        except (ValueError, TypeError, KeyError):
            pass
    for row in hubs:
        coords[row["hub_id"]] = (float(row["longitude"]), float(row["latitude"]))

    route_colors = {"road": "#777777", "air": "#4C78A8", "sea": "#59A14F"}
    shown = set()
    for row in routes:
        if row["from_node"] not in coords or row["to_node"] not in coords:
            continue
        x1, y1 = coords[row["from_node"]]
        x2, y2 = coords[row["to_node"]]
        mode = row["mode"]
        label = mode.title() if mode not in shown else None
        shown.add(mode)
        ax.plot([x1, x2], [y1, y2], color=route_colors.get(mode, "#999999"), linewidth=0.65 if mode == "road" else 1.0, alpha=0.22 if mode == "road" else 0.32, label=label, zorder=1)

    facility_x = [xy[0] for key, xy in coords.items() if key.startswith(("BASE:", "UP_"))]
    facility_y = [xy[1] for key, xy in coords.items() if key.startswith(("BASE:", "UP_"))]
    hub_x = [xy[0] for key, xy in coords.items() if key.startswith("HUB:")]
    hub_y = [xy[1] for key, xy in coords.items() if key.startswith("HUB:")]
    ax.scatter(facility_x, facility_y, s=28, color="#E15759", marker="o", edgecolor="white", linewidth=0.5, label="Factory / process site", zorder=3)
    ax.scatter(hub_x, hub_y, s=42, color="#F28E2B", marker="s", edgecolor="white", linewidth=0.5, label="Airport / port", zorder=3)

    for hub in hubs:
        x, y = coords[hub["hub_id"]]
        ax.text(x + 1.2, y + 0.5, hub["hub_id"].split(":", 1)[1], fontsize=7, color="#333333", zorder=4)

    ax.set_xlim(-135, 150)
    ax.set_ylim(-5, 65)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, color="#DDDDDD", linewidth=0.35, alpha=0.6)
    ax.legend(loc="upper left", ncol=3, frameon=False)
    ax.set_title("Candidate physical facilities and modeled multimodal connections", fontsize=18, fontweight="bold")
    ax.text(-133, -2.5, "Routes show geographic options, not confirmed carriers or commercial schedules. Air/sea times use transparent speed and handling assumptions.", fontsize=9, color="#555555")
    fig.tight_layout()
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def build_readme(path: Path, summary: dict) -> None:
    text = f"""# GPU supply-chain database package

This package joins the BOMWiki graphics-card hierarchy to Georgetown CSET ETO's semiconductor supply-chain data. It is a representative RTX 5080-class graphics-card model, not an exact reconstruction of one brand's confidential bill of materials or purchase orders.

## Project hierarchy from gpu.xlsx

The project-focus graph follows `gpu.xlsx` sheet `ATP`, columns R through AM:

1. `Finished logic die` is produced by assembly, packaging and testing (ATP).
2. ATP requires electronic gases, packaging materials and the fabricated logic die.
3. Fabrication produces the bare logic die.
4. Fabrication requires CMP materials, electronic gases, process-specific fabrication materials, silicon wafer, wet chemicals, photoresists, photomasks and deposition materials.
5. Each category is expanded using the items listed beneath it in the ATP sheet and matching ETO subtype records.

The workbook's phrase `finished logic die` is preserved as the project label. A terminology note records that the output after packaging and testing would normally be called a packaged and tested logic device, while a bare die is the fabrication output.

## Delivered tables

- `nodes.csv`: normalized ETO and grouped-BOM nodes.
- `edges.csv`: ETO process/taxonomy edges, BOM component edges and the project-focus hierarchy edges.
- `project_focus_nodes.csv` and `project_focus_edges.csv`: the exact construction hierarchy selected from `ATP!R:AM`.
- `providers.csv`: ETO providers plus independently researched BOM candidate vendors.
- `provider_component_links.csv`: provider-to-input/component relationships with market-share fields where ETO supplies them.
- `focus_input_coverage.csv`: review table for the nine selected fabrication/ATP material categories, including provider and physical-facility coverage.
- `facilities.csv`: source-backed physical facility candidates; exact product allocation is often undisclosed.
- `upstream_materials.csv`: curated commodity/material extensions beneath ETO categories.
- `logistics_hubs.csv`: airports and ports used as candidate transfer nodes.
- `transport_edges.csv`: modeled road/air/sea routes with method and caveat fields.
- `transport_graph_statistics.csv` and `.json`: reproducible connectivity and topology summary for the physical facility/hub network.
- `manufacturing_time_assumptions.csv`: min / most-likely / max scenario inputs, clearly separated from sourced facts.
- `sources.csv`: URLs, intended use and reliability notes.
- `unified_graph.json`: machine-readable graph for algorithms and visualization.
- `status_summary.json`: completeness counts and known gaps.

## Current coverage

- Grouped BOM nodes: {summary['bom_nodes']} of {summary['bom_nodes']} included.
- Rolled-up physical part count preserved from the JSON: {summary['rolled_up_parts']}.
- Full ETO nodes preserved: {summary['eto_nodes']}.
- Logical edges: {summary['logical_edges']}.
- Provider-component rows: {summary['provider_links']}.
- Physical facility candidates: {summary['facilities']}.
- Modeled transport edges: {summary['transport_edges']}.

## Physical transport graph statistics

Run `python3 code/compute_transport_graph_statistics.py` to rebuild the statistics table and graphic. For this graph, nodes are manufacturing/design/process facilities and logistics hubs; directed edges are modeled road, air and sea movements. WCC and SCC retain the standard directed-network definitions, while clustering, triangles and path-length measures use the undirected projection so that they remain defined for a mostly acyclic supply-flow graph.

The 609 figure is the extended quantity of repeated parts, not 609 different supplier categories. For example, hundreds of passive placements are modeled as grouped passive-component nodes with quantities.

## Evidence levels

- `confirmed_*`: the source confirms the company role, product capability, facility or relationship stated.
- `candidate_*`: the source confirms capability or a facility, but not the exact product/customer allocation.
- `modeled_geographic_option`: a route is computed from geodata and assumptions; it is not a booked carrier route.
- `assumption`: a transparent analytical input that must not be presented as an observed industry value.

## Important remaining gaps

1. Most firms do not publish product-to-factory or customer-to-factory allocations.
2. ETO identifies corporate providers and headquarters countries, not physical manufacturing sites.
3. Public manufacturing cycle times are sparse. The time table is therefore a reviewable three-point assumption set.
4. Air and sea rows do not yet use live schedules, customs queues, weather or carrier capacity.
5. Several generic mechanical BOM items, including the shroud, fasteners, bracket and backplate, do not have verified independent tier-two factories.
6. A potential vendor is not necessarily a qualified interchangeable replacement. Redundancy analysis should apply an eligibility/qualification field.

## Rebuild

```bash
python3 code/build_unified_gpu_database.py \
  --bom data/raw/gpu_bom_609_parts.json \
  --structure-workbook data/raw/gpu.xlsx \
  --output rebuilt-package
```

Use `--refresh-eto` to download the current ETO CSV files from the official GitHub repository.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bom", type=Path, default=DEFAULT_BOM)
    parser.add_argument("--structure-workbook", type=Path, default=DEFAULT_STRUCTURE_WORKBOOK)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "gpu-supply-chain-database")
    parser.add_argument("--refresh-eto", action="store_true")
    args = parser.parse_args()

    if not args.bom.exists():
        raise FileNotFoundError(args.bom)
    ensure_eto_files(args.refresh_eto)

    output = args.output.resolve()
    raw_dir = output / "data" / "raw"
    clean_dir = output / "data" / "clean"
    figure_dir = output / "figures"
    code_dir = output / "code"
    for directory in (raw_dir, clean_dir, figure_dir, code_dir):
        directory.mkdir(parents=True, exist_ok=True)

    bom = json.loads(args.bom.read_text(encoding="utf-8"))
    bom_nodes, bom_edges = normalize_bom(bom)
    eto_nodes, eto_edges, providers, provider_links, relevant_eto = normalize_eto()
    add_bom_vendors(providers, provider_links)
    focus_nodes, focus_edges = build_project_focus_hierarchy(eto_nodes, bom_nodes)
    custom_focus_nodes = [row for row in focus_nodes if row["node_id"].startswith(("MODEL:", "DETAIL:"))]
    nodes = eto_nodes + bom_nodes + custom_focus_nodes
    edges = eto_edges + bom_edges + focus_edges
    upstream = load_upstream_module()
    upstream_materials, upstream_facilities, upstream_edges, upstream_sources = normalize_upstream(upstream)
    facilities = normalize_base_facilities() + upstream_facilities
    hubs, transport_edges = build_transport_edges(facilities)

    source_rows = SOURCES[:]
    known_source_ids = {row["source_id"] for row in source_rows}
    base_source_manifest = ETO_DIR / "source_manifest.csv"
    if base_source_manifest.exists():
        for row in read_csv(base_source_manifest):
            if row["source_id"] in known_source_ids:
                continue
            source_rows.append(
                {
                    "source_id": row["source_id"],
                    "organization": row.get("organization", ""),
                    "title": row.get("title", ""),
                    "url": row.get("url", ""),
                    "use": row.get("use", ""),
                    "reliability": "Source retained from the existing physical-location model; review the row-level evidence label before use.",
                }
            )
            known_source_ids.add(row["source_id"])
    for row in upstream_sources:
        if row["source_id"] not in known_source_ids:
            source_rows.append(
                {
                    "source_id": row["source_id"],
                    "organization": row.get("organization", ""),
                    "title": row.get("title", ""),
                    "url": row.get("url", ""),
                    "use": row.get("use", ""),
                    "reliability": row.get("reliability", ""),
                }
            )
            known_source_ids.add(row["source_id"])

    time_rows = [
        {
            "node_id": node_id,
            "activity": activity,
            "minimum_days": low,
            "most_likely_days": mode,
            "maximum_days": high,
            "unit": unit,
            "evidence_level": evidence,
            "source_ids": "",
            "note": note,
        }
        for node_id, activity, low, mode, high, unit, evidence, note in MANUFACTURING_TIMES
    ]
    focus_coverage_rows = build_focus_input_coverage(nodes, providers, provider_links, upstream_materials, facilities)

    # Preserve raw, auditable inputs.
    shutil.copy2(args.bom, raw_dir / "gpu_bom_609_parts.json")
    if args.structure_workbook.exists():
        shutil.copy2(args.structure_workbook, raw_dir / "gpu.xlsx")
    for stem in ETO_FILES:
        shutil.copy2(ETO_DIR / f"eto_{stem}.csv", raw_dir / f"eto_{stem}.csv")
    for supporting_name in ("facility_locations.csv", "source_manifest.csv"):
        supporting_path = ETO_DIR / supporting_name
        if supporting_path.exists() and supporting_path.resolve() != (raw_dir / supporting_name).resolve():
            shutil.copy2(supporting_path, raw_dir / supporting_name)
    if UPSTREAM_MODULE.exists():
        shutil.copy2(UPSTREAM_MODULE, raw_dir / "upstream_research_data.mjs")

    write_csv(clean_dir / "nodes.csv", nodes)
    write_csv(clean_dir / "edges.csv", edges)
    write_csv(clean_dir / "project_focus_nodes.csv", focus_nodes)
    write_csv(clean_dir / "project_focus_edges.csv", focus_edges)
    write_csv(clean_dir / "providers.csv", providers)
    write_csv(clean_dir / "provider_component_links.csv", provider_links)
    write_csv(clean_dir / "facilities.csv", facilities)
    write_csv(clean_dir / "upstream_materials.csv", upstream_materials)
    write_csv(
        clean_dir / "upstream_edges.csv",
        upstream_edges,
        ["edge_id", "from_node", "to_node", "relationship", "edge_class", "requirement_status", "quantity", "evidence_level", "source_ids", "note"],
    )
    write_csv(clean_dir / "logistics_hubs.csv", hubs)
    write_csv(clean_dir / "transport_edges.csv", transport_edges)
    write_csv(clean_dir / "manufacturing_time_assumptions.csv", time_rows)
    write_csv(clean_dir / "focus_input_coverage.csv", focus_coverage_rows)
    write_csv(clean_dir / "sources.csv", source_rows)

    graph_json = {
        "metadata": {
            "model": "Representative RTX 5080-class PCIe graphics card",
            "bom_source": "BOMWiki structure with official specifications used to resolve conflicts",
            "eto_source": "Georgetown CSET ETO Semiconductor Supply Chain Dataset",
            "raw_bom_sha256": sha256(raw_dir / "gpu_bom_609_parts.json"),
            "structure_workbook_sha256": sha256(raw_dir / "gpu.xlsx") if (raw_dir / "gpu.xlsx").exists() else "",
            "structure_workbook_range": "ATP!R:AM",
            "edge_direction": "input_or_component_to_process_or_assembly",
            "important_semantics": "taxonomy edges are alternatives/subtypes; BOM structure edges are not timed process edges",
        },
        "nodes": nodes,
        "edges": edges,
        "project_focus": {
            "source_range": "gpu.xlsx ATP!R:AM",
            "nodes": focus_nodes,
            "edges": focus_edges,
        },
        "providers": providers,
        "provider_component_links": provider_links,
        "facilities": facilities,
        "logistics_hubs": hubs,
        "transport_edges": transport_edges,
    }
    (clean_dir / "unified_graph.json").write_text(json.dumps(graph_json, indent=2, ensure_ascii=False), encoding="utf-8")

    atomic_bom_nodes = [n for n in bom_nodes if n["node_type"] == "part"]
    covered_atomic = {row[0] for row in BOM_VENDOR_LINKS}
    summary = {
        "model_scope": "representative RTX 5080-class graphics card; grouped component categories",
        "rolled_up_parts": bom["summary"]["total_rolled_up_parts"],
        "bom_nodes": len(bom_nodes),
        "bom_edges": len(bom_edges),
        "atomic_bom_nodes": len(atomic_bom_nodes),
        "atomic_bom_nodes_with_candidate_vendor": sum(1 for n in atomic_bom_nodes if n["node_id"] in covered_atomic),
        "eto_nodes": len(eto_nodes),
        "eto_edges": len(eto_edges),
        "logical_edges": len(edges),
        "project_focus_nodes": len(focus_nodes),
        "project_focus_edges": len(focus_edges),
        "provider_links": len(provider_links),
        "providers": len(providers),
        "facilities": len(facilities),
        "logistics_hubs": len(hubs),
        "transport_edges": len(transport_edges),
        "manufacturing_time_rows": len(time_rows),
        "known_gaps": [
            "Exact product-to-factory and customer-to-factory allocations are usually confidential.",
            "BOM vendor coverage remains incomplete for generic mechanical and connector items.",
            "Manufacturing times are scenario assumptions, not supplier quotes or measured cycle times.",
            "Transport rows are geographic options, not live carrier schedules.",
            "ETO providers use headquarters nationality and should not be treated as factory locations.",
        ],
    }
    (clean_dir / "status_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    make_dependency_figure(focus_nodes, focus_edges, figure_dir / "dependency_graph_overview.png")
    make_transport_figure(facilities, hubs, transport_edges, figure_dir / "transport_network.png", raw_dir)
    shutil.copy2(Path(__file__), code_dir / Path(__file__).name)
    stats_source = Path(__file__).with_name("compute_transport_graph_statistics.py")
    if stats_source.exists():
        stats_target = code_dir / stats_source.name
        if stats_source.resolve() != stats_target.resolve():
            shutil.copy2(stats_source, stats_target)
        subprocess.run([sys.executable, str(stats_target)], check=True)
    (code_dir / "requirements.txt").write_text("matplotlib>=3.8\nnetworkx>=3.2\nPillow>=10\n", encoding="utf-8")
    build_readme(output / "README.md", summary)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
