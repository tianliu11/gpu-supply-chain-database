"""Render the repository's shareable PNGs from the full-chain research exports."""
import json
from collections import defaultdict, deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data/clean"
FIGURES = ROOT / "figures"


def load(name):
    return json.loads((CLEAN / name).read_text())


def dependency(graph):
    incoming = defaultdict(list)
    for edge in graph["edges"]:
        incoming[edge["target_node_id"]].append(edge["source_node_id"])
    depth = {"0": 0}
    queue = deque(depth)
    while queue:
        target = queue.popleft()
        for source in incoming[target]:
            if source not in depth:
                depth[source] = depth[target] + 1
                queue.append(source)
    groups = defaultdict(list)
    for node in graph["nodes"]:
        groups[depth.get(node["id"], -1)].append(node)
    positions = {}
    for distance, nodes in groups.items():
        for index, node in enumerate(nodes):
            positions[node["id"]] = (-distance, (index + 0.5) / len(nodes))
    fig, ax = plt.subplots(figsize=(12, 7))
    for context, color, label in [
        (True, "#a1a9b4", "Context or relationship requiring review"),
        (False, "#397e86", "Scoped technical dependency"),
    ]:
        links = [[positions[e["source_node_id"]], positions[e["target_node_id"]]]
                 for e in graph["edges"] if (e.get("analysis_use") != "technical_dependency_not_observed_shipment") == context]
        ax.add_collection(LineCollection(links, colors=color, linewidths=0.55, alpha=0.28, label=label))
    for distance, nodes in sorted(groups.items()):
        points = [positions[n["id"]] for n in nodes]
        ax.scatter(*zip(*points), s=12, color="#21566d", zorder=3)
        ax.text(-distance, 1.02, str(len(nodes)), ha="center", fontsize=9)
    ax.set_xlim(min(-d for d in groups)-0.45, max(-d for d in groups)+0.55)
    ax.set_ylim(-0.06, 1.11)
    ax.set_yticks([])
    ax.set_xticks([-d for d in sorted(groups)], [str(d) if d >= 0 else "No path" for d in sorted(groups)])
    ax.set_xlabel("Fewest dependency links to the graphics card  |  upstream → finished card")
    ax.set_title(f"GPU component dependency graph  |  {len(graph['nodes']):,} nodes · {len(graph['edges']):,} links", loc="left", pad=18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncols=2, frameon=False)
    fig.text(0.08, 0.025, "Numbers above columns count components and process nodes. Individual names and citations are available in the reviewed graph explorer.", fontsize=9)
    fig.subplots_adjust(bottom=0.21, top=0.88)
    fig.savefig(FIGURES / "dependency_graph_overview.png", dpi=170)
    plt.close(fig)


def transport(database):
    sites = {s["facility_id"]: (float(s["longitude"]), float(s["latitude"]))
             for s in database["facilities"] if s["longitude"] not in ("", None) and s["latitude"] not in ("", None)}
    candidates = database["nearby_hub_candidates"]
    world = json.loads((ROOT / "data/raw/natural_earth_countries.geojson").read_text())
    land = []
    for feature in world["features"]:
        geometry = feature["geometry"]
        if geometry and geometry["type"] in {"Polygon", "MultiPolygon"}:
            polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
            land.extend(polygon[0] for polygon in polygons if polygon)
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.add_collection(PolyCollection(land, facecolors="#edf0eb", edgecolors="#b9c5c4", linewidths=0.28))
    for kind, label, color in [
        ("port", "Port proximity", "#187b9c"),
        ("commercial_airport", "Airport proximity", "#b5601c"),
    ]:
        lines = []
        for row in candidates:
            if row["hub_type"] == kind and row["proximity_rank"] in (1, "1"):
                start = sites[row["facility_id"]]
                end = (float(row["hub_longitude"]), float(row["hub_latitude"]))
                if abs(start[0] - end[0]) <= 180:
                    lines.append([start, end])
        ax.add_collection(LineCollection(lines, colors=color, linewidths=0.85, alpha=0.63, label=label))
    ax.scatter(*zip(*sites.values()), s=9, c="#202d48", zorder=4, label="Production location")
    ax.set(xlim=(-180, 180), ylim=(-60, 84), xlabel="Longitude", ylabel="Latitude")
    ax.set_title(f"Production sites and nearby logistics hubs  |  {len(sites):,} mapped sites", loc="left", pad=15)
    ax.legend(loc="lower left", frameon=False)
    fig.text(0.10, 0.025, "One nearest port and airport shown per site. Lines indicate straight-line proximity. The data table includes up to three candidates per mode.", fontsize=9)
    fig.subplots_adjust(bottom=0.14, top=0.88)
    fig.savefig(FIGURES / "transport_network.png", dpi=170)
    plt.close(fig)


def transport_statistics(database):
    candidates = database["nearby_hub_candidates"]
    facilities = {("site", row["facility_id"]) for row in database["facilities"]}
    hubs = {(row["hub_type"], row["hub_id"]) for row in candidates}
    links = {(("site", row["facility_id"]), (row["hub_type"], row["hub_id"])) for row in candidates}
    adjacency = {node: set() for node in facilities | hubs}
    for site, hub in links:
        adjacency[site].add(hub)
        adjacency[hub].add(site)
    remaining = set(adjacency)
    sizes = []
    while remaining:
        stack = [remaining.pop()]
        size = 0
        while stack:
            size += 1
            new_nodes = adjacency[stack.pop()] & remaining
            remaining.difference_update(new_nodes)
            stack.extend(new_nodes)
        sizes.append(size)
    rows = [
        ("Production-site records", f"{len(facilities):,}"),
        ("Sites with nearby-hub candidates", f"{sum(bool(adjacency[n]) for n in facilities):,}"),
        ("Unique airports", f"{sum(k == 'commercial_airport' for k, _ in hubs):,}"),
        ("Unique ports", f"{sum(k == 'port' for k, _ in hubs):,}"),
        ("Site + hub nodes", f"{len(adjacency):,}"),
        ("Site-to-hub proximity links", f"{len(links):,}"),
        ("Weakly connected components", f"{len(sizes):,}"),
        ("Largest weakly connected component", f"{max(sizes):,}  ({max(sizes)/len(adjacency):.1%})"),
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_axis_off()
    ax.set_title("Site-to-hub proximity graph statistics", loc="left", fontsize=17, pad=15)
    table = ax.table(cellText=rows, colLabels=["Metric", "Value"], colWidths=[0.74, 0.26],
                     cellLoc="left", colLoc="left", bbox=(0, 0.12, 1, 0.84))
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_facecolor("#21566d" if row == 0 else ("#edf2f4" if row % 2 else "#f7f9fa"))
        cell.get_text().set_color("white" if row == 0 else "#192b38")
        if col == 1:
            cell.get_text().set_ha("right")
    ax.text(0, 0.025, "Connectivity uses geographic candidate links. Route and cargo-service verification remains open.",
            transform=ax.transAxes, fontsize=9)
    fig.savefig(FIGURES / "transport_graph_statistics.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    database = load("full_supply_chain_research_database.json")
    dependency(load("reviewed_supply_chain_structure.json"))
    transport(database)
    transport_statistics(database)
