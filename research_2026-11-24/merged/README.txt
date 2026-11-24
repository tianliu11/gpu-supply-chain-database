RECONCILED RESEARCH HANDOFF

vendor_candidates.csv preserves every batch row plus older scoped suppliers omitted from the batches.
A citation-present status is not independent verification. Original numeric ranks remain claims, not accepted market rankings.
prior_source_ids and prior_product_scope carry only the earlier evidence, not the new rank.
production_sites.csv and nearest_hubs.csv reuse the existing sourced site/hub database.
vendor_site_links.csv uses exact normalized company names only. Missing matches may be aliases, not missing factories.
No site is inherited from headquarters country. No nearby hub is a confirmed freight lane.
node_coverage.csv includes all 289 nodes, including those missing from Claude batches.
citation_repair_queue.csv, vendor_research_queue.csv and edge_review_queue.csv expose remaining research.
Batch files and main reviewed database are unchanged. Rerun: python3 research_2026-11-24/code/reconcile.py
