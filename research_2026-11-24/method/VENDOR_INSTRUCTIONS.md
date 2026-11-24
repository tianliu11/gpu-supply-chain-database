# Vendor research instructions (GPU supply-chain project, MATH 168)

Context: a student team models the supply chain of a discrete graphics card (RTX 5080-class)
from finished card down to raw materials as a directed graph. Each node is a
component, material, consumable, process stage or raw material. Your batch file
(JSON) lists nodes with: node_id, node_name, node_type, inputs (what feeds it),
used_in (what it feeds), and existing_vendors_in_repo (an earlier, weak pass —
mostly 1-2 unranked names; some are wrong or are small/hobby suppliers).

## Goal
For EACH node in your batch, find the industry-leading suppliers of that exact
component/material: **at most 10**, ideally the top ~5-10 by market share,
production volume or capacity. Fewer than 10 is fine when the market is
concentrated or evidence is thin. Never pad with obscure firms to reach 10.

Interpretation rules:
- Component nodes (e.g., "GPU Die", "Package Substrate", "VRM Power Stage"): the companies that make that
  part class at scale (e.g., substrate: Ibiden, Unimicron, Shinko, AT&S, Nan Ya PCB, Kinsus, Samsung Electro-Mechanics...).
- Assemblies/finished card: the companies that assemble/sell them (e.g., graphics card AIB partners: ASUS, MSI, Gigabyte, Zotac/PC Partner, Palit, etc.; PCB assembly: EMS firms). Say which role.
- Process-stage nodes: "Fabrication" / "Logic die fabricated" -> leading foundries; "Assembly, packaging, and testing" -> leading OSATs (+TSMC advanced packaging); "Finished logic die" -> GPU designers (NVIDIA, AMD, Intel) — mark role.
- Material-category nodes (e.g., "CMP materials", "Electronic gases", "Wet chemicals"): leaders of that category overall.
- Raw materials/ores: the leading MINING companies by production of that commodity (e.g., copper: Freeport-McMoRan, BHP, Codelco, Zijin, Glencore, Southern Copper, Anglo American...). For crude oil/natural gas: leading producers (Saudi Aramco, etc.). For utilities like atmospheric air or freshwater: write a single row with vendor_name "N/A – utility/ambient resource" and explain (air: captured on-site by air-separation-unit operators; list the leading ASU/industrial gas operators only if natural).
- Very generic nodes (e.g., "Fastener Set", "I/O Bracket", "Backplate", "Cooler Shroud"): list the large, documented suppliers of that part class to the electronics/PC industry if you can find sources; else give the few you can source and flag `evidence_strength=weak`.
- Use the parent company name as vendor_name when the subsidiary is just a brand (e.g., Merck KGaA's EMD Electronics -> "Merck KGaA (EMD Electronics)"). Do not list the same corporate group twice for one node.

## Ranking & sourcing (most important)
For each node, try to find ONE OR TWO sources that rank or name the market leaders
(market share table, production ranking, "key players" list). Acceptable source
types, best first: government (USGS, DOE, EU CRM reports), company annual reports /
SEC or other public filings, think tanks (CSET/ETO, CSIS, SIA/BCG), consultancies &
market-research firms (Yole, TechInsights, TrendForce, Omdia, Gartner, IDC, Prismark,
Wood Mackenzie, S&P Global, Roskill/Project Blue; reputable press releases summarising
them are OK), industry associations/primers (SEMI, IPC, Cobalt Institute...), Wikipedia,
reputable trade/business press (Nikkei Asia, DigiTimes, Reuters, Bloomberg, Mining.com,
Mining Technology, C&EN, ICIS). Avoid content farms, forums, AI-written SEO listicles.
If the ranking source does not cover a vendor, back that vendor with its own product page.
Record market share/volume figures only when the source states them.

Work efficiently: WebSearch first, WebFetch only where needed. Budget roughly 4-8
tool calls per node; aim to finish the batch, don't get stuck on one node.

## Output (write with the Write tool, CSV with header, UTF-8, properly quoted)
1) `/home/claude/work/vendors/<BATCH>_vendors.csv` with columns:
node_id,node_name,vendor_rank,vendor_name,vendor_parent_group,hq_country,vendor_role,ranking_basis,metric_value,metric_year,evidence_strength,source_ids,notes
- vendor_rank: 1..10 in order of the ranking source; if the source names leaders without order, rank by your best evidence and set ranking_basis accordingly ("named leading supplier, unordered").
- ranking_basis: e.g. "market share (revenue)", "mine production volume", "capacity", "named key player".
- metric_value: e.g. "31% share", "1.1 Mt Cu", blank if none.
- evidence_strength: strong (ranked market data), medium (named leader in reputable source), weak (product capability only).
- source_ids: semicolon-separated IDs from your sources file.
2) `/home/claude/work/sources/<BATCH>_sources.csv` with columns:
source_id,organization,title,url,source_type,accessed_on,supports
- source_id prefix = your batch code, e.g. V07_S001, V07_S002...
- source_type one of: government, company_website, public_filing, annual_report, wikipedia, think_tank, consultancy_market_report, industry_association, trade_press, academic, other
- accessed_on: 2026-11-24
- url must be the real URL you actually saw in search results/fetches. Never invent URLs.

When finished, reply with a SHORT summary (<=150 words): rows written, nodes with <3 vendors, any node you could not resolve, and notable corrections to existing_vendors_in_repo (wrong or minor firms). Do not paste the CSV in your reply.
