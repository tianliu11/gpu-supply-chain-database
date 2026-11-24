# Manufacturing-site research instructions (GPU supply-chain project, MATH 168)

Context: a student team models the GPU (graphics card) supply chain from finished card down
to raw materials. Earlier research picked the industry-leading vendors for each component or
material. Your batch file (JSON) lists vendors. For each one you get the products/nodes it
was selected for, plus any production sites already in the repo (`known_sites`, which may be
incomplete, imprecise or wrong).

## Goal
For EACH vendor, find its physical PRODUCTION sites: mines, refineries, smelters, wafer fabs,
semiconductor assembly/test plants, chemical plants, gas plants (air-separation or specialty-gas
fill plants), and factories.
EXCLUDE: headquarters, corporate/sales offices, R&D/research/innovation/technical centers,
design centers, laboratories, and pure warehouses/distribution centers. Include a site only if
a source says it manufactures, refines, mines or processes. A "Head Office & Plant" counts only
if the source says production happens there.

## Scope rule
- Focused companies (most of their business is the selected product, e.g., SUMCO, Ibiden, Ajinomoto
  Fine-Techno, a mining company for its commodity): list ALL production sites.
- Diversified conglomerates (e.g., BASF, Samsung, Linde, ExxonMobil, Mitsubishi Chemical, Glencore):
  list only the sites that make the selected product(s) or belong to that business segment. Put
  the reasoning in `notes`.
- If a company has more than 40 qualifying sites (e.g., industrial gas majors with hundreds of
  air-separation units), list up to 40 of the most relevant: the largest, those serving
  semiconductor clusters, and electronics/specialty-gas plants. Set site_list_complete=no.
- Mining companies: list each operating mine (and smelter/refinery if relevant) producing the
  selected commodity. Include the joint-venture share in notes when the source gives it.
- Sites that are closed, sold, or still under construction: include them only with
  operating_status set accordingly (operating / under_construction / closed / divested / unknown).

## Allowed sources ONLY
company websites (global network / plant / "our locations" pages, product pages naming the plant),
public filings (SEC 10-K "Item 2. Properties", 20-F, annual/integrated reports, Japanese
securities reports, TWSE/KRX/HKEX filings, NI 43-101 / JORC technical reports), Wikipedia,
government organizations (USGS, DOE, EPA, national ministries, EU), think tanks (CSET/ETO, CSIS,
etc.), consulting firms, and industry primers/associations (SEMI, IPC...). Do NOT use news blogs,
forums, LinkedIn, job boards, directories (Zoominfo, Dun & Bradstreet), or SEO sites. Never
invent URLs; only cite URLs you actually saw.

## Coordinates
Fill latitude/longitude ONLY if a source you saw gives them (e.g., Wikipedia infobox for a mine
or fab) and set coordinate_precision=source_exact. Otherwise leave them blank and give an
accurate city + state/province + country. The coordininator geocodes those blanks to city level.
For remote mines, try to get coordinates from Wikipedia or a technical report, since city-level
geocoding is poor there.

## Efficiency
Usually one or two fetches of the company's "locations"/"global network" page or annual-report
properties section are enough per vendor. Budget about 2-5 tool calls per vendor and do not
stall on one company. If nothing is found under the allowed sources, write one row with
site_name "NOT FOUND" and explain in notes.

## Output (Write tool, CSV with header, properly quoted, UTF-8)
1) `/home/claude/work/sites/<BATCH>_sites.csv` columns:
vendor_name,site_name,site_type,products_at_site,node_ids,street_address_or_area,city,state_province,country,latitude,longitude,coordinate_precision,operating_status,site_list_complete,source_ids,notes
- site_type: mine | refinery | smelter | wafer_fab | semiconductor_assembly_test | substrate_or_pcb_factory | chemical_plant | gas_plant | materials_plant | component_factory | assembly_factory | steel_or_metal_mill | other_factory
- node_ids: semicolon-separated node_ids from the batch that this site plausibly serves (by product line).
- site_list_complete: yes or no (applies to the vendor, repeat on every row).
2) `/home/claude/work/sources/<BATCH>_sources.csv` columns:
source_id,organization,title,url,source_type,accessed_on,supports
- source_id prefix = your batch code (e.g., S05_S001). source_type one of: company_website, public_filing,
  annual_report, wikipedia, government, think_tank, consultancy_market_report, industry_association, other
- accessed_on: 2026-11-24

When done, reply with a SHORT summary (<=120 words): vendors covered, total sites, and vendors
NOT FOUND. Do not paste the CSV.
