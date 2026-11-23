# GPU supply-chain database package

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
- `manufacturing_time_assumptions.csv`: min / most-likely / max scenario inputs, clearly separated from sourced facts.
- `sources.csv`: URLs, intended use and reliability notes.
- `unified_graph.json`: machine-readable graph for algorithms and visualization.
- `status_summary.json`: completeness counts and known gaps.

## Current coverage

- Grouped BOM nodes: 36 of 36 included.
- Rolled-up physical part count preserved from the JSON: 609.
- Full ETO nodes preserved: 126.
- Logical edges: 245.
- Provider-component rows: 1306.
- Physical facility candidates: 35.
- Modeled transport edges: 72.

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
python3 src/build_unified_gpu_database.py   --bom /Users/lt/Downloads/gpu_bom_609_parts.json   --structure-workbook /Users/lt/Downloads/gpu.xlsx   --output outputs/gpu-supply-chain-database
```

Use `--refresh-eto` to download the current ETO CSV files from the official GitHub repository.
