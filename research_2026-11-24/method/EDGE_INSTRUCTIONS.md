# Edge validation instructions (GPU supply-chain project, MATH 168)

Context: a student team models the supply chain of a discrete graphics card from the
finished card down to raw materials as a directed graph. Each edge says
SOURCE node is an input to (feeds_into / necessary_input_for / constituent_of) TARGET node.
An earlier automated audit could not confirm the edges in your batch file. Your job:
decide for EACH edge whether it is a real, defensible manufacturing relationship, and
back it with a reputable source.

## Verdicts (column `verdict`)
- valid_direct: source material/part is a direct input or constituent of the target (e.g., copper foil -> copper-clad laminate).
- valid_upstream: the source is a genuine upstream ancestor but via intermediate steps not shown (e.g., bauxite -> aluminum fin stock via alumina & smelting). Say what intermediates are missing in `explanation`.
- valid_consumable: process consumable/tooling genuinely used in making the target (e.g., dicing blades in die singulation) but not incorporated.
- valid_optional: used only in some designs/process variants (state which).
- invalid: not a real relationship, or wrong direction, or chemically/technically implausible. Explain why and propose `suggested_fix` (e.g. "replace with X -> Y", "remove").
- uncertain: could not find evidence either way after reasonable search.

Many edges are of the form "raw material X -> processed material Y" (lineage). Raw ores
are often linked to distant products; judge whether the chain is chemically real
(e.g., coking coal -> carbon steel via BOF: valid_upstream; coking coal -> "Wafer":
plausible only as carbon reductant for metallurgical silicon -> valid_upstream with note;
coking coal -> PC/ABS plastic: likely invalid unless a defensible route exists).

## Sources
Each non-invalid verdict needs at least one source that explicitly supports the relationship
(that Y is made from / uses X). Preferred: government (USGS Mineral Commodity Summaries,
EPA AP-42 / emission docs, DOE), academic papers & textbooks, industry associations
(SEMI, IPC, The Aluminum Association, Copper Development Association, International
Tin Association...), company technical/product pages, Wikipedia, reputable encyclopedias
(Britannica). Invalid verdicts may cite a source if it helps. One source can support
many edges — reuse its ID. Never invent URLs; only use URLs you actually saw.
Be efficient: group similar edges (e.g., all "Disposable X plating bath -> part" edges)
and research the underlying fact once. Budget ~1-3 tool calls per distinct fact.

## Output (Write tool, CSV with header, properly quoted)
1) `/home/claude/work/edges/<BATCH>_edges.csv` columns:
edge_id,source_node_name,target_node_name,verdict,explanation,suggested_fix,source_ids
(explanation <= 40 words; source_ids semicolon-separated)
2) `/home/claude/work/sources/<BATCH>_sources.csv` columns:
source_id,organization,title,url,source_type,accessed_on,supports
- source_id prefix = your batch code, e.g. E03_S001.
- source_type one of: government, company_website, public_filing, annual_report, wikipedia, think_tank, consultancy_market_report, industry_association, trade_press, academic, encyclopedia, other
- accessed_on: 2026-11-24

Every edge in the batch must get exactly one row. When finished reply with a SHORT
summary (<=120 words): counts per verdict and the most important invalid edges.
Do not paste the CSV.
