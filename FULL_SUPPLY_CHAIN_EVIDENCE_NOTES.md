# Full supply-chain evidence audit

## What was checked

The submitted full graph contains 289 nodes and 757 directed edges from raw
materials toward a single graphics-card root. The rebuild script independently
confirmed that it is a directed acyclic graph, contains no missing-node edges or
self-loops, and that every node has a path to the root and a raw-material
ancestor.

Structural correctness is different from factual verification. The current
edge audit uses explicitly scoped source records for particular edge IDs.
Supported category membership, manufacturing use, composition and process-stage
sequence have separate statuses. Proposed ore-conversion links, optional process
choices, consumables and unresolved relationships are labeled separately.

The earlier statement that 400 edges were supported is withdrawn. That count
came from a first-pass keyword/category matching rule: for example, a broad
semiconductor document could be attached to an exact precursor recipe. The
current pipeline no longer treats those matches as verification. Consult the
live counts in `data/clean/full_supply_chain_completion_report.json`.

`source_ids` identifies evidence scoped to the claim in `audit_note`. A blank
source field means exact evidence remains absent. An upstream-lineage label is
not an assertion that the chemical conversion is impossible; it means the
route and skipped intermediates still need evidence. None of these statuses
establishes an observed transaction or mandatory input for every GPU.

## Vendor interpretation

The vendor table uses ETO's curated provider relationships for directly aligned
semiconductor categories and official company evidence for researched graphics-
card components. It contains no more than ten providers per mapped node.

Where ETO publishes no comparable market-share number, the suppliers are marked
`unranked`. Their presence in ETO supports that they are relevant suppliers; it
does not prove they are the ten largest firms by revenue or volume. The vendor
coverage table lists every unsupported node so that later research does not
silently inherit a parent-category supplier as a supplier of every chemical
precursor. `product_scope` identifies the supported branch of combined nodes,
and `qualification_status` identifies missing grade/eligibility information.
Candidate finished-device manufacturers are explicitly distinguished from
confirmed sellers of separate bare die or unfinished component bodies.

The supplementary research register is in `code/additional_public_research.py`.
It contains scoped observations from official product, operations and corporate
documents reviewed on 2026-11-24. The follow-up search log records searches for
all 101 nodes that lacked candidates when that search pass began. Search-result
links are discovery leads; they are not automatically added as verified vendors.
Current coverage is a candidate-presence measure, not a market-share percentage.

## Facility interpretation

The facility table contains factories, fabs, assembly sites and material plants
identified in official company sources. Corporate offices, sales locations and
R&D-only sites are excluded. A public facility confirms that a company operates
that type of production at that location; it usually does not prove that the
site supplies NVIDIA or a particular GPU model.

Some official company sources publish a complete global manufacturing footprint;
others publish only a regional or business-unit list. The
`public_site_list_completeness` field records that distinction. The follow-up
`full_supply_chain_vendor_site_coverage.csv` distinguishes a documented product-
class site from an otherwise known company site. Most corporate footprints are
still partial; none is described as exhaustive without a complete source audit.

New coordinates are cached OSM city/district proxies with country checks,
retrieval queries and feature IDs in `data/raw/public_site_geocodes.json`.
Older approximate coordinates are labeled as inherited approximations. These
coordinates should be replaced with factory-gate locations for operational
routing. Idle assets, planned expansions and commercial interruptions must be
checked before treating a site as an available source.

## Nearby hubs

For each geocoded production site, the pipeline calculates:

- the three nearest medium or large airports with scheduled service in
  OurAirports; and
- the three nearest ports in the NGA World Port Index.

The cached port records were downloaded from an ArcGIS-hosted World Port Index
mirror, not directly from NGA. `R_WPI_MIRROR` records the actual endpoint; its
revision and completeness have not been reconciled with the current NGA release.

Distance is great-circle distance. These rows are screening candidates only.
Before using them as graph transportation edges, confirm cargo handling,
customs, carrier schedules, mode suitability, road/rail access and actual
supplier practice.

## Problems found in the submitted structure

The modeling-issues table documents specific problems, including a post-packaging
output feeding the bare GPU die, a GDDR6/GDDR6X node in an RTX 5080-class GDDR7
reference, combined alternative materials treated as simultaneously necessary,
generic mask substrate assumptions, and a mandatory YAG phosphor assumption for
RGB LEDs. The raw-material set also omits gallium and indium despite naming
compound-semiconductor products containing them. Reachability to the existing
36 raw nodes therefore does not establish chemical completeness.

The original JSON is preserved. The audit recommends changes for team review;
it does not silently turn those proposals into an exact product BOM.

## Current research pass

The extension contains 252 nodes with supplier-candidate evidence out of the 289
submitted nodes, 403 supplier-to-node records, and 315 production-asset records.
These are not completion percentages: category nodes, process stages, internal
subcomponents and purchased materials have different evidence requirements.
Supplier capability does not establish market coverage or a qualified substitute.

The second pass added 70 public production-asset records and 47 supplier-node
records. A further gap pass added three previously unmapped material nodes
(WC-Co hardmetal, silicone-coated PET liners and matte-tin bath chemistry),
12 production-asset records, and one scoped PET-carrier relationship. Among
the current 403 supplier-node records, 99 have an explicitly documented
product-class site match, 134 have company sites but unconfirmed product
allocation, 169 lack a matched site in this package, and one is a fabless
designer. Product-class matches still do not prove exact grades, customer
qualification or independent operational backups. Some records describe units
within a common complex. The facility table flags company/city record counts;
do not count every row as an independent backup factory.

`GAP_DIAGNOSIS.txt` and its machine-readable JSON distinguish unfinished research
from ambiguous definitions, integrated/internal parts, categories and utilities.

The definition pass adds five supplier-node mappings and six production-site
records, plus 54 scoped definitions. `STRUCTURE_REVIEW.txt` explains the separate
reviewed graph: duplicate die identities merged, reversed packaging dependency
removed, and seven other unsuitable default relationships excluded. Every
original edge has a reversible decision record. Remaining links are not all
verified: process expansion, design alternatives and material recipes still
require validation before redundancy or lead-time analysis.

The cumulative process register researches 108 original relationship claims and adds 18
process/component nodes and 23 links, and separates wafer production, passive
device families, mask technologies and several chemical intermediates. Six
Murata capacitor production locations are added. Shinko aliases are merged to
avoid counting one supplier twice. The reviewed graph is 305 nodes / 772 links;
the source JSON remains 289 / 757. See `VALIDATION_RESULTS.txt` and the scoped
claim register: source support for a chemical route is not evidence of exact
semiconductor purity, customer procurement, production duration or shipments.
No remaining item is declared publicly unavailable merely because a search did
not resolve it. Covestro resin and Umicore gold-salt pages were promising indexed
leads, but full-source access returned HTTP 403 and 402 respectively; they were
not admitted as verified supplier mappings. A slurry for polishing SiC was not
automatically accepted as a slurry containing SiC abrasive. CERATIZIT sites
announced for closure in 2026 were not added as operating plants. Newly listed
company plants remain unallocated where individual product grades were not
established by the inspected source.

The discovery logs record follow-up queries for 101 then-uncovered nodes and 127
then-uncovered vendor names. Search hits are leads, not automatically accepted
evidence. Ambiguous entities (for example CMC, Merck and ASM-related names) require
company-identity checks before accepting a factory. Only reviewed observations
are added to the curated research module.

The site-coverage table is the most useful readiness check: many supplier-node
pairs still have no documented production site, or only company-level sites
without product allocation. A fabless designer such as NVIDIA is distinguished
from a manufacturer that needs a production-site match. Public sources rarely
establish every supplier's complete global footprint, qualified grade, current
capacity and actual customer shipping lane.

## Remaining work before claiming a complete real supply chain

- Obtain node-specific suppliers for the unsupported nodes in
  `full_supply_chain_vendor_coverage.csv`.
- Replace unranked provider sets with comparable market-share evidence when a
  reputable source publishes it.
- Check the current unresolved edge groups in the completion report. These
  counts increased after correcting the overly broad first-pass validation.
- Obtain confidential or primary customer-to-factory allocations if the project
  needs actual rather than candidate routes.
- Validate nearby hubs operationally before converting proximity candidates to
  transportation edges.
- Add manufacturing lead-time distributions from defensible sources or label
  them explicitly as scenario assumptions.

## Rebuild

```bash
python3 code/build_full_supply_chain_evidence.py
python3 code/build_research_handoff.py
python3 code/test_public_research_integrity.py
```

`node code/test_research_explorers.mjs` checks JavaScript syntax and data-driven
interactions in the two standalone explorers with a DOM test double. This is not
a rendered browser-layout test. Browser layout review could not be completed
because in-app localhost access timed out and local Chrome attachment required
an app network-policy update. The browser problem does not prevent database
rebuilding or the automated data checks.

The builder is deterministic given the checked-in raw datasets. To refresh new
site proxies through public Nominatim, run
`python3 code/geocode_public_production_sites.py --retry-missing`, then rebuild.
This performs sequential, rate-limited network requests and retains the cache.

The consolidated machine-readable handoff is
`data/clean/full_supply_chain_research_database.json`. It includes the original
nodes, evidence-audited edges, vendor candidates, public production sites, nearby
hubs, site-coverage records, modeling issues and the source register. Its edges
use `source_node_id` and `target_node_id`; the untouched original JSON uses
`source` and `target`.
