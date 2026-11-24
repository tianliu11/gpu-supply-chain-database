# GPU supply-chain database package

This package joins the BOMWiki graphics-card hierarchy to Georgetown CSET ETO's semiconductor supply-chain data. It is a representative RTX 5080-class graphics-card model, not an exact reconstruction of one brand's confidential bill of materials or purchase orders.

## Latest handoff: supplied full node-to-node JSON

Start with [RESEARCH_HANDOFF.txt](RESEARCH_HANDOFF.txt) for what is done and what
is still missing. The latest extension preserves the supplied JSON and has 247
nodes with supplier-candidate evidence, 393 supplier-node records, 231 public
production-asset records and 1,386 nearby-hub records. These are research-coverage
counts, not percentages of a fully verified or market-representative chain.

- `figures/full_supply_chain_structure.html`: offline component graph and
  node-by-node supplier, site-coverage and edge-source explorer.
- `figures/full_supply_chain_reviewed_structure.html`: separate semantic-review
  graph, with 287 canonical nodes and 751 retained links. Not a fully validated BOM.
- `STRUCTURE_REVIEW.txt`: corrections, 54 scoped definitions and remaining issues.
- `data/clean/component_definitions.json` and `.csv`: definitions, references and
  project-specific interpretations; exact grades are not implied by class evidence.
- `data/clean/structure_review_decisions.csv`: reversible decisions for all 757
  original edges. The original input JSON is unchanged.
- `figures/full_supply_chain_transport_map.html`: offline geographic factory/hub
  screening map. Dashed lines are proximity candidates, not verified shipments.
- `data/clean/full_supply_chain_research_database.json`: consolidated handoff.
- `data/clean/full_supply_chain_task_status.json`: checklist and current counts.
- `data/clean/full_supply_chain_remaining_work.json`: explicit unresolved queue.
- `GAP_DIAGNOSIS.txt` and `data/clean/full_supply_chain_gap_diagnosis.json`:
  reasons and next actions for all 42 nodes without supplier mappings, including
  official-source access failures and product-definition issues. Missing does
  not mean impossible to find.
- `data/clean/full_supply_chain_data_dictionary.json`: fields, joins, units and
  interpretation of missing values.

Download the repository ZIP and open the HTML files locally; GitHub's source
viewer does not execute HTML. They embed their data and need no network access.
All three pass JavaScript/DOM interaction smoke tests. Browser layout review was
unavailable in this session, as recorded in the handoff. The older PNG figures
and the smaller legacy graph statistics below have **not** been regenerated as
the full-node research graph and must not be cited as its current outputs.

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

### Evidence-audited full node-to-node extension

The submitted `gpu_complete_node_to_node_supply_chain.json` is preserved in
`data/raw/`. Run `python3 code/build_full_supply_chain_evidence.py` to rebuild
the following review files:

- `full_supply_chain_nodes.csv`: all 289 submitted nodes in a flat table.
- `full_supply_chain_edges_audit.csv`: all 757 submitted edges with structural
  checks, evidence status, source IDs and an audit note.
- `full_supply_chain_audit_summary.json`: independent DAG, root-path and
  raw-material-ancestry checks plus evidence-status counts.
- `full_supply_chain_vendors.csv`: up to ten source-backed providers for mapped
  ETO categories and researched BOM components. Unranked provider sets are not
  presented as market-share rankings.
- `full_supply_chain_vendor_coverage.csv`: node-by-node vendor coverage and a
  research queue for unsupported nodes.
- `full_supply_chain_facilities.csv`: public production sites only; corporate
  offices and R&D-only locations are excluded.
- `full_supply_chain_nearest_hubs.csv`: three nearest scheduled medium/large
  airports and three nearest World Port Index ports per geocoded production
  site, using straight-line distance.
- `full_supply_chain_completion_report.json`: concise completion counts and the
  claims the package intentionally does not make.
- `full_supply_chain_sources.csv`: combined source register.
- `data/raw/additional_node_research_search_log.json` and
  `data/raw/manufacturing_site_research_search_log.json`: discovery-only query
  logs, not verified supplier or site evidence.
- `full_supply_chain_vendor_site_coverage.csv`: distinguishes a product-class
  manufacturing site from a company site with unverified product allocation.
- `full_supply_chain_modeling_issues.csv`: specific structural and interpretation
  problems found in the submitted proposal.
- `full_supply_chain_research_database.json`: consolidated JSON handoff containing
  all the above evidence layers. Edge endpoints are `source_node_id` and
  `target_node_id`.

The follow-up research adds explicit `product_scope`, qualification and corporate-
group fields. All counts are rebuilt in `full_supply_chain_completion_report.json`.
The earlier count of 400 supported edges was based on overly broad category
matching and has been withdrawn; the current audit requires explicitly scoped
evidence. Read `FULL_SUPPLY_CHAIN_EVIDENCE_NOTES.md` before using the database for
redundancy or lead-time results.

The airport and port results are proximity screening. They do not demonstrate
cargo schedules, customs capability, road accessibility, carrier capacity or an
actual supplier route.

## Legacy smaller-model coverage (not the latest full-node extension)

- Grouped BOM nodes: 36 of 36 included.
- Rolled-up physical part count preserved from the JSON: 609.
- Full ETO nodes preserved: 126.
- Logical edges: 245.
- Provider-component rows: 1306.
- Physical facility candidates: 35.
- Modeled transport edges: 72.

## Legacy physical transport graph statistics

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
python3 code/build_unified_gpu_database.py   --bom data/raw/gpu_bom_609_parts.json   --structure-workbook data/raw/gpu.xlsx   --output rebuilt-package
```

Use `--refresh-eto` to download the current ETO CSV files from the official GitHub repository.

Rebuild the evidence-audited full graph after updating the raw JSON or source
tables:

```bash
python3 code/build_full_supply_chain_evidence.py
python3 code/build_research_handoff.py
python3 code/test_public_research_integrity.py
```

Optional explorer smoke tests: `node code/test_research_explorers.mjs`.
The evidence and presentation rebuilds use only Python's standard library and
the checked-in data. No live scraping is required for reproduction.
