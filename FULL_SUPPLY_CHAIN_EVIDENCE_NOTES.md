# Full supply-chain evidence audit

## What was checked

The submitted full graph contains 289 nodes and 757 directed edges from raw
materials toward a single graphics-card root. The rebuild script independently
confirmed that it is a directed acyclic graph, contains no missing-node edges or
self-loops, and that every node has a path to the root and a raw-material
ancestor.

Structural correctness is different from factual verification. Each edge is
therefore assigned one of five evidence statuses in
`data/clean/full_supply_chain_edges_audit.csv`:

1. `supported_structural_reference`: the relationship follows the generic
   BOMWiki hierarchy.
2. `supported_category_level`: authoritative semiconductor sources support the
   broad process or material category, but not an exact chemical recipe.
3. `supported_product_or_industry_level`: an official product document or
   industry standard supports the material relationship for that product class.
4. `partially_supported_requires_specific_confirmation`: a source supports the
   commodity or process class but not the exact conversion edge.
5. `unverified_specific_relation`: the submitted graph is currently the only
   evidence for that exact relationship.

These statuses must not be collapsed into a single “verified” flag.

## Vendor interpretation

The vendor table uses ETO's curated provider relationships for directly aligned
semiconductor categories and official company evidence for researched graphics-
card components. It contains no more than ten providers per mapped node.

Where ETO publishes no comparable market-share number, the suppliers are marked
`unranked`. Their presence in ETO supports that they are relevant suppliers; it
does not prove they are the ten largest firms by revenue or volume. The vendor
coverage table lists every unsupported node so that later research does not
silently inherit a parent-category supplier as a supplier of every chemical
precursor.

## Facility interpretation

The facility table contains factories, fabs, assembly sites and material plants
identified in official company sources. Corporate offices, sales locations and
R&D-only sites are excluded. A public facility confirms that a company operates
that type of production at that location; it usually does not prove that the
site supplies NVIDIA or a particular GPU model.

Some official company sources publish a complete global manufacturing footprint;
others publish only a regional or business-unit list. The
`public_site_list_completeness` field records that distinction.

## Nearby hubs

For each geocoded production site, the pipeline calculates:

- the three nearest medium or large airports with scheduled service in
  OurAirports; and
- the three nearest ports in the NGA World Port Index.

Distance is great-circle distance. These rows are screening candidates only.
Before using them as graph transportation edges, confirm cargo handling,
customs, carrier schedules, mode suitability, road/rail access and actual
supplier practice.

## Remaining work before claiming a complete real supply chain

- Obtain node-specific suppliers for the unsupported nodes in
  `full_supply_chain_vendor_coverage.csv`.
- Replace unranked provider sets with comparable market-share evidence when a
  reputable source publishes it.
- Verify the 203 exact relations currently marked
  `unverified_specific_relation`.
- Obtain confidential or primary customer-to-factory allocations if the project
  needs actual rather than candidate routes.
- Validate nearby hubs operationally before converting proximity candidates to
  transportation edges.
- Add manufacturing lead-time distributions from defensible sources or label
  them explicitly as scenario assumptions.

## Rebuild

```bash
python3 code/build_full_supply_chain_evidence.py
```

The script is deterministic given the checked-in raw datasets.
