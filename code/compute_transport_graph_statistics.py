#!/usr/bin/env python3
"""Compute reproducible summary statistics for the physical transport graph.

Nodes are manufacturing/design/processing facilities plus logistics hubs.
Edges are the modeled road, air, and sea movements in transport_edges.csv.
Connectivity follows edge direction for SCCs and ignores direction for WCCs,
clustering, triangles, diameter, and effective diameter.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
FIGURES = ROOT / "figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def connected_components(nodes: set[str], adjacency: dict[str, set[str]]) -> list[set[str]]:
    unseen = set(nodes)
    components: list[set[str]] = []
    while unseen:
        start = next(iter(unseen))
        component = {start}
        queue = deque([start])
        unseen.remove(start)
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        components.append(component)
    return sorted(components, key=lambda component: (-len(component), sorted(component)[0]))


def strongly_connected_components(nodes: set[str], outgoing: dict[str, set[str]]) -> list[set[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[set[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in outgoing[node]:
            if neighbor not in indices:
                visit(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])

        if lowlinks[node] == indices[node]:
            component: set[str] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda component: (-len(component), sorted(component)[0]))


def shortest_path_lengths(start: str, allowed: set[str], adjacency: dict[str, set[str]]) -> dict[str, int]:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor in allowed and neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances


def percentile(values: list[int], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def undirected_metrics(nodes: set[str], adjacency: dict[str, set[str]], largest_wcc: set[str]) -> dict[str, float | int]:
    local_coefficients = []
    triangle_sum = 0
    connected_triples = 0
    for node in nodes:
        neighbors = adjacency[node]
        degree = len(neighbors)
        possible_pairs = degree * (degree - 1) // 2
        connected_triples += possible_pairs
        linked_pairs = 0
        neighbor_list = sorted(neighbors)
        for index, left in enumerate(neighbor_list):
            for right in neighbor_list[index + 1 :]:
                if right in adjacency[left]:
                    linked_pairs += 1
        triangle_sum += linked_pairs
        local_coefficients.append(linked_pairs / possible_pairs if possible_pairs else 0.0)

    all_pair_distances: list[int] = []
    diameter = 0
    ordered_nodes = sorted(largest_wcc)
    for index, node in enumerate(ordered_nodes):
        distances = shortest_path_lengths(node, largest_wcc, adjacency)
        for other in ordered_nodes[index + 1 :]:
            distance = distances[other]
            all_pair_distances.append(distance)
            diameter = max(diameter, distance)

    triangles = triangle_sum // 3
    return {
        "average_clustering_coefficient": sum(local_coefficients) / len(nodes) if nodes else 0.0,
        "number_of_triangles": triangles,
        "fraction_of_closed_triangles": (3 * triangles / connected_triples) if connected_triples else 0.0,
        "diameter_largest_wcc_undirected": diameter,
        "effective_diameter_90_percentile": percentile(all_pair_distances, 0.90),
    }


def edges_inside(edge_pairs: set[tuple[str, str]], component: set[str]) -> int:
    return sum(1 for source, target in edge_pairs if source in component and target in component)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size, index=1 if bold and candidate.suffix == ".ttc" else 0)
            except OSError:
                continue
    return ImageFont.load_default()


def render_table(metrics: list[tuple[str, str]], output: Path) -> None:
    width = 1500
    margin = 72
    header_height = 110
    row_height = 68
    footer_height = 126
    height = margin * 2 + header_height + row_height * len(metrics) + footer_height
    image = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(image)
    title_font = load_font(40, bold=True)
    header_font = load_font(28, bold=True)
    body_font = load_font(27)
    value_font = load_font(27, bold=True)
    note_font = load_font(22)

    left = margin
    right = width - margin
    top = margin
    draw.rounded_rectangle((left, top, right, height - margin), radius=28, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.rounded_rectangle((left, top, right, top + header_height), radius=28, fill="#315d75")
    draw.rectangle((left, top + header_height - 28, right, top + header_height), fill="#315d75")
    draw.text((left + 36, top + 28), "Physical transport graph statistics", fill="#ffffff", font=title_font)

    y = top + header_height
    for index, (label, value) in enumerate(metrics):
        if index % 2:
            draw.rectangle((left + 2, y, right - 2, y + row_height), fill="#f1f5f9")
        draw.line((left + 28, y + row_height, right - 28, y + row_height), fill="#dbe3ea", width=2)
        draw.text((left + 36, y + 18), label, fill="#1f2937", font=body_font)
        value_box = draw.textbbox((0, 0), value, font=value_font)
        value_width = value_box[2] - value_box[0]
        draw.text((right - 36 - value_width, y + 18), value, fill="#0f172a", font=value_font)
        y += row_height

    footer_y = y + 25
    draw.text((left + 36, footer_y), "Definition", fill="#315d75", font=header_font)
    draw.text(
        (left + 210, footer_y + 2),
        "Facilities + logistics hubs are nodes; modeled road, air, and sea movements are directed edges.",
        fill="#475569",
        font=note_font,
    )
    draw.text(
        (left + 36, footer_y + 48),
        "WCC/SCC use direction-aware connectivity; clustering and path-length measures use the undirected projection.",
        fill="#64748b",
        font=note_font,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)


def main() -> None:
    facilities = read_csv(CLEAN / "facilities.csv")
    # The legacy facilities table also contains six airport/port reference
    # rows.  Exclude them here because the normalized HUB:* records represent
    # logistics nodes and otherwise the same places would be counted twice.
    physical_facilities = [
        row for row in facilities if row.get("facility_type", "").strip().lower() not in {"airport", "port"}
    ]
    hubs = read_csv(CLEAN / "logistics_hubs.csv")
    routes = read_csv(CLEAN / "transport_edges.csv")

    node_ids = {row["facility_id"] for row in physical_facilities} | {row["hub_id"] for row in hubs}
    outgoing = {node: set() for node in node_ids}
    undirected = {node: set() for node in node_ids}
    edge_pairs: set[tuple[str, str]] = set()
    unknown_endpoints: set[str] = set()
    for route in routes:
        source, target = route["from_node"], route["to_node"]
        if source not in node_ids or target not in node_ids:
            unknown_endpoints.update({node for node in (source, target) if node not in node_ids})
            continue
        outgoing[source].add(target)
        undirected[source].add(target)
        undirected[target].add(source)
        edge_pairs.add((source, target))

    wccs = connected_components(node_ids, undirected)
    sccs = strongly_connected_components(node_ids, outgoing)
    largest_wcc = wccs[0] if wccs else set()
    largest_scc = sccs[0] if sccs else set()
    extra = undirected_metrics(node_ids, undirected, largest_wcc)
    modes = Counter(route["mode"] for route in routes)

    result = {
        "graph_definition": "Facilities and logistics hubs are nodes; modeled road, air, and sea route rows are directed edges.",
        "nodes": len(node_ids),
        "manufacturing_or_process_facility_nodes": len(physical_facilities),
        "logistics_hub_nodes": len(hubs),
        "directed_edges": len(edge_pairs),
        "road_edges": modes.get("road", 0),
        "air_edges": modes.get("air", 0),
        "sea_edges": modes.get("sea", 0),
        "rail_edges": modes.get("rail", 0),
        "weakly_connected_components": len(wccs),
        "nodes_in_largest_wcc": len(largest_wcc),
        "fraction_nodes_in_largest_wcc": len(largest_wcc) / len(node_ids) if node_ids else 0.0,
        "edges_in_largest_wcc": edges_inside(edge_pairs, largest_wcc),
        "fraction_edges_in_largest_wcc": edges_inside(edge_pairs, largest_wcc) / len(edge_pairs) if edge_pairs else 0.0,
        "strongly_connected_components": len(sccs),
        "nodes_in_largest_scc": len(largest_scc),
        "fraction_nodes_in_largest_scc": len(largest_scc) / len(node_ids) if node_ids else 0.0,
        "edges_in_largest_scc": edges_inside(edge_pairs, largest_scc),
        "fraction_edges_in_largest_scc": edges_inside(edge_pairs, largest_scc) / len(edge_pairs) if edge_pairs else 0.0,
        "isolated_nodes": sum(1 for node in node_ids if not undirected[node]),
        "directed_density": len(edge_pairs) / (len(node_ids) * (len(node_ids) - 1)) if len(node_ids) > 1 else 0.0,
        "average_total_degree": 2 * len(edge_pairs) / len(node_ids) if node_ids else 0.0,
        **extra,
        "unknown_route_endpoints_excluded": sorted(unknown_endpoints),
        "interpretation_note": "A small SCC is expected because the dataset stores supply-flow direction rather than guaranteed return routes.",
    }

    json_path = CLEAN / "transport_graph_statistics.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    csv_path = CLEAN / "transport_graph_statistics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value", "definition"])
        writer.writeheader()
        definitions = {
            "nodes": "All registered manufacturing/design/process facilities and logistics hubs.",
            "directed_edges": "Unique modeled transport movements between registered nodes.",
            "nodes_in_largest_wcc": "Nodes connected when transport direction is ignored.",
            "edges_in_largest_wcc": "Directed transport edges whose endpoints are both in the largest WCC.",
            "nodes_in_largest_scc": "Nodes mutually reachable while respecting transport direction.",
            "edges_in_largest_scc": "Directed transport edges whose endpoints are both in the largest SCC.",
            "average_clustering_coefficient": "Mean local clustering in the undirected projection.",
            "number_of_triangles": "Three-node closed groups in the undirected projection.",
            "fraction_of_closed_triangles": "Global transitivity: closed triples divided by all connected triples.",
            "diameter_largest_wcc_undirected": "Longest shortest path in the largest WCC, measured in edges.",
            "effective_diameter_90_percentile": "90th percentile of pairwise shortest paths in the largest WCC.",
        }
        for metric, definition in definitions.items():
            writer.writerow({"metric": metric, "value": result[metric], "definition": definition})

    table_rows = [
        ("Nodes", f"{result['nodes']}"),
        ("Manufacturing/process facilities", f"{result['manufacturing_or_process_facility_nodes']}"),
        ("Logistics hubs", f"{result['logistics_hub_nodes']}"),
        ("Directed transport edges", f"{result['directed_edges']}"),
        ("Road / air / sea edges", f"{result['road_edges']} / {result['air_edges']} / {result['sea_edges']}"),
        ("Nodes in largest WCC", f"{result['nodes_in_largest_wcc']} ({result['fraction_nodes_in_largest_wcc']:.3f})"),
        ("Edges in largest WCC", f"{result['edges_in_largest_wcc']} ({result['fraction_edges_in_largest_wcc']:.3f})"),
        ("Nodes in largest SCC", f"{result['nodes_in_largest_scc']} ({result['fraction_nodes_in_largest_scc']:.3f})"),
        ("Edges in largest SCC", f"{result['edges_in_largest_scc']} ({result['fraction_edges_in_largest_scc']:.3f})"),
        ("Average clustering coefficient", f"{result['average_clustering_coefficient']:.4f}"),
        ("Number of triangles", f"{result['number_of_triangles']}"),
        ("Fraction of closed triangles", f"{result['fraction_of_closed_triangles']:.6f}"),
        ("Diameter (largest WCC)", f"{result['diameter_largest_wcc_undirected']} edges"),
        ("90-percentile effective diameter", f"{result['effective_diameter_90_percentile']:.1f} edges"),
    ]
    render_table(table_rows, FIGURES / "transport_graph_statistics.png")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
