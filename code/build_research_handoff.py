#!/usr/bin/env python3
"""Build offline evidence explorers and a candid handoff from the latest tables.

Standard library only. No inferred shipments, manufacturing-time estimates,
market shares or new BOM edges are introduced by this presentation script.
"""
import csv
import hashlib
import html
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLEAN=ROOT/'data/clean'
FIG=ROOT/'figures'

def rows(name):
    with (CLEAN/name).open() as f:
        return list(csv.DictReader(f))

def save_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')

def page(title,intro,controls,body,script,data):
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+html.escape(title)+'''</title><style>
:root{color-scheme:light dark;--bg:#fafbfc;--fg:#172436;--panel:#fff;--line:#aab5c2;--faint:#e9edf2;--yes:#287453;--no:#a55324;--conflict:#b52735}
@media(prefers-color-scheme:dark){:root{--bg:#151c25;--fg:#e4eaf2;--panel:#202b38;--line:#8495a9;--faint:#354352;--yes:#77cda6;--no:#e6ae79;--conflict:#ff8d9c}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:24px}
h1{font-size:27px;margin:0 0 10px}h2{font-size:20px}p{max-width:100ch}.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:end;margin:20px 0}
label{display:flex;flex-direction:column;gap:4px}select,button{font:inherit;max-width:100%;padding:8px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:4px}
select{max-width:min(720px,90vw)}svg{width:100%;height:auto;color:var(--fg)}.plot{overflow:auto;border:1px solid var(--line)}
table{width:100%;border-collapse:collapse;margin:12px 0}th,td{text-align:left;padding:10px 8px;vertical-align:top;border-bottom:1px solid var(--line);overflow-wrap:anywhere}#graph{min-width:1300px}
.table-wrap{overflow:auto}a{color:inherit;text-decoration:underline}code{overflow-wrap:anywhere}.muted{opacity:.8}.legend{display:flex;gap:20px;flex-wrap:wrap}.swatch{width:13px;height:13px;display:inline-block;margin-right:6px}.card{padding:14px;background:var(--panel)}
button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid var(--yes);outline-offset:3px}footer{margin-top:28px}.node{cursor:pointer}
</style></head><body><main><h1>'''+html.escape(title)+'''</h1><p>'''+html.escape(intro)+'''</p>'''+controls+body+'''
<footer class="muted">Source register and evidence fields are embedded. Public evidence review: 2026-11-24. Download this HTML and open it locally; no network connection or Python is needed to explore it.</footer>
<script id="data" type="application/json">'''+payload+'''</script><script>
const D=JSON.parse(document.getElementById('data').textContent);
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs={},text=null){const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==null)e.textContent=text;return e}
function refs(cell,ids){for(const id of (ids||'').split(';').filter(Boolean)){const s=D.sources.find(x=>x.source_id===id);if(!s)continue;const a=document.createElement('a');a.href=s.url;a.target='_blank';a.rel='noopener';a.textContent=id;a.title=s.title;cell.append(a,document.createTextNode(' '))}}
function table(headers,records,container){const t=document.createElement('table'),thead=t.createTHead(),hr=thead.insertRow();for(const h of headers){const th=document.createElement('th');th.scope='col';th.textContent=h;hr.append(th)}const b=t.createTBody();for(const row of records){const tr=b.insertRow();for(const value of row){const td=tr.insertCell();if(value&&typeof value==='object'&&value.sources!==undefined)refs(td,value.sources);else td.textContent=value??''}}container.replaceChildren(t)}
'''+script+'''</script></main></body></html>'''

GRAPH_JS=r'''
const select=document.getElementById('component'),mode=document.getElementById('mode'),svg=document.getElementById('graph');
const N=new Map(D.nodes.map(n=>[n.id,n]));
for(const n of D.nodes){const o=document.createElement('option');o.value=n.id;o.textContent=n.id+' — '+n.name;select.append(o)}select.value='0';
function choose(id){select.value=id;mode.value='focus';draw()}
function mark(n,x,y,overview=false){const g=el('g',{class:'node'}),color=n.vendor_candidates.length?'var(--yes)':'var(--no)';
g.append(el('title',{},n.id+' '+n.name+'; supplier candidates: '+n.vendor_candidates.length));
if(overview){g.append(el('circle',{cx:x,cy:y,r:5,fill:color}));g.append(el('text',{x:x+8,y:y+4,fill:'currentColor','font-size':11},n.id))}
else{g.append(el('rect',{x:x-155,y:y-24,width:310,height:48,rx:5,fill:'var(--panel)',stroke:color}));
g.append(el('text',{x:x-145,y:y-3,fill:'currentColor','font-size':12},n.id));g.append(el('text',{x:x-145,y:y+14,fill:'currentColor','font-size':12},n.name.length>42?n.name.slice(0,39)+'…':n.name))}
g.addEventListener('click',()=>choose(n.id));svg.append(g)}
function line(x1,y1,x2,y2,e,overview=false){const supported=e.validation_status.startsWith('supported_'),bad=e.validation_status==='semantic_conflict';
const l=el('path',{d:`M${x1},${y1} L${x2},${y2}`,stroke:bad?'var(--conflict)':supported?'var(--yes)':'var(--line)',fill:'none','stroke-width':overview ? 0.6 : 1.5,'marker-end':'url(#arrow)'});
if(!supported)l.setAttribute('stroke-dasharray','4 3');l.append(el('title',{},e.edge_id+': '+e.validation_status));svg.append(l)}
function draw(){svg.replaceChildren();const defs=el('defs'),m=el('marker',{id:'arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});m.append(el('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'var(--line)'}));defs.append(m);svg.append(defs);
const id=select.value,n=N.get(id),inc=D.edges.filter(e=>e.target_node_id===id),out=D.edges.filter(e=>e.source_node_id===id);
if(mode.value==='overview'){const h=D.overview_height;svg.setAttribute('viewBox',`0 0 1350 ${h}`);for(const e of D.edges){const a=D.positions[e.source_node_id],b=D.positions[e.target_node_id];line(a[0],a[1],b[0],b[1],e,true)}for(const v of D.nodes){const p=D.positions[v.id];mark(v,p[0],p[1],true)}}
else{const inputIds=[...new Set(inc.map(e=>e.source_node_id))],outputIds=[...new Set(out.map(e=>e.target_node_id))],h=Math.max(300,80+Math.max(inputIds.length,outputIds.length)*65),cy=h/2;svg.setAttribute('viewBox',`0 0 1300 ${h}`);
for(const [i,k]of inputIds.entries()){const y=60+i*65;for(const e of inc.filter(e=>e.source_node_id===k))line(340,y,495,cy,e)}
for(const [i,k]of outputIds.entries()){const y=60+i*65;for(const e of out.filter(e=>e.target_node_id===k))line(805,cy,960,y,e)}
inputIds.forEach((k,i)=>mark(N.get(k),185,60+i*65));outputIds.forEach((k,i)=>mark(N.get(k),1115,60+i*65));mark(n,650,cy)}
document.getElementById('selected').textContent=n.id+' — '+n.name+' | '+inc.length+' proposed inputs | '+out.length+' proposed downstream links';
const d=n.component_definition;table(['Definition','Project scope / limitations','Sources'],d?[[d.formal_definition,d.project_interpretation,{sources:d.source_ids}]]:[['No separate formal definition reviewed in this pass.','Original label retained; not certification of the recipe.',{sources:''}]],document.getElementById('definition'));
table(['Supplier candidate','Product scope','Qualification status','Sources'],n.vendor_candidates.map(v=>[v.provider_name,v.product_scope,v.qualification_status,{sources:v.source_ids}]),document.getElementById('vendors'));
table(['Connection','Input → output','Evidence status','Review note','Sources'],[...inc,...out].map(e=>[e.edge_id,N.get(e.source_node_id).name+' → '+N.get(e.target_node_id).name,e.validation_status,e.audit_note,{sources:e.source_ids}]),document.getElementById('edges'));
const links=D.site_coverage.filter(v=>v.node_id===id);table(['Supplier','Site evidence status','Product-class sites','Other company sites'],links.map(v=>[v.provider_name,v.site_status,v.product_class_site_ids,v.other_company_site_ids]),document.getElementById('sites'))}
select.addEventListener('change',draw);mode.addEventListener('change',draw);draw();
'''

MAP_JS=r'''
const select=document.getElementById('factory'),svg=document.getElementById('map');
const project=(lon,lat)=>[(Number(lon)+180)*4,(90-Number(lat))*4];
const world=el('g',{fill:'var(--faint)',stroke:'var(--line)','stroke-width':.4});
for(const f of D.world.features){const g=f.geometry;if(!g)continue;const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];for(const p of polys){let d='';for(const ring of p){if(!ring.length)continue;d+='M'+ring.map(c=>project(c[0],c[1]).join(',')).join('L')+'Z'}world.append(el('path',{d,'fill-rule':'evenodd'}))}}svg.append(world);
const routes=el('g'),points=el('g');svg.append(routes,points);
const all=document.createElement('option');all.value='';all.textContent='All documented production assets';select.append(all);
for(const f of D.facilities){const o=document.createElement('option');o.value=f.facility_id;o.textContent=f.company+' — '+f.facility_name;select.append(o);const p=project(f.longitude,f.latitude),c=el('circle',{cx:p[0],cy:p[1],r:3.3,fill:'var(--yes)',class:'node'});c.append(el('title',{},f.company+' — '+f.facility_name+'; '+f.coordinate_precision));c.addEventListener('click',()=>{select.value=f.facility_id;draw()});points.append(c)}
function draw(){routes.replaceChildren();const f=D.facilities.find(x=>x.facility_id===select.value),hubs=D.hubs.filter(h=>h.facility_id===select.value);
if(!f){document.getElementById('selected').textContent=D.facilities.length+' production-asset records; some share a city-level coordinate. Select an asset to inspect up to three airports and three ports.';document.getElementById('facility').replaceChildren();document.getElementById('hubtable').replaceChildren();return}
const a=project(f.longitude,f.latitude);for(const h of hubs){const b=project(h.hub_longitude,h.hub_latitude),air=h.hub_type==='commercial_airport',c=air?'var(--no)':'var(--fg)';routes.append(el('path',{d:`M${a[0]},${a[1]}L${b[0]},${b[1]}`,fill:'none',stroke:c,'stroke-width':1.4,'stroke-dasharray':'4 3'}));const point=air?el('path',{d:`M${b[0]},${b[1]-5}L${b[0]-5},${b[1]+4}L${b[0]+5},${b[1]+4}Z`,fill:c}):el('rect',{x:b[0]-4,y:b[1]-4,width:8,height:8,fill:c});point.append(el('title',{},h.hub_name+' '+h.great_circle_distance_km+' km; '+h.cargo_service_status));routes.append(point)}
document.getElementById('selected').textContent=f.company+' — '+f.facility_name+' | '+f.country+' | '+f.coordinate_precision;
table(['Address or location','Component scope','Site status','Sources'],[[f.address,f.component_categories||'Company production site only; product allocation unconfirmed',f.operating_status,{sources:f.source_ids}]],document.getElementById('facility'));
table(['Hub type','Rank','Name','Straight-line distance (km)','Cargo verification','Sources'],hubs.map(h=>[h.hub_type,h.proximity_rank,h.hub_name,h.great_circle_distance_km,h.cargo_service_status,{sources:h.source_ids}]),document.getElementById('hubtable'))}
select.addEventListener('change',draw);draw();
'''

def overview(nodes,edges):
    ids={n['id'] for n in nodes}
    incoming=Counter(e['target_node_id'] for e in edges)
    out=defaultdict(list)
    for e in edges:out[e['source_node_id']].append(e['target_node_id'])
    q=deque(sorted(ids-set(incoming)))
    level=defaultdict(int)
    while q:
        v=q.popleft()
        for w in out[v]:
            level[w]=max(level[w],level[v]+1);incoming[w]-=1
            if incoming[w]==0:q.append(w)
    groups=defaultdict(list)
    for n in nodes:groups[level[n['id']]].append(n['id'])
    height=max(600,max(map(len,groups.values()))*24+60)
    maxlevel=max(groups) or 1
    positions={}
    for lev,members in groups.items():
        for i,nid in enumerate(sorted(members)):
            positions[nid]=[20+lev/maxlevel*1170,35+(i+.5)*(height-70)/len(members)]
    return positions,height

def main():
    from build_reviewed_structure import main as build_reviewed_structure
    reviewed=build_reviewed_structure()
    from build_gap_diagnosis import main as build_gap_diagnosis
    build_gap_diagnosis()
    FIG.mkdir(exist_ok=True)
    db=json.loads((CLEAN/'full_supply_chain_research_database.json').read_text())
    report=json.loads((CLEAN/'full_supply_chain_completion_report.json').read_text())
    pos,height=overview(db['nodes'],db['edges'])
    controls='<div class="controls"><label>Component<select id="component"></select></label><label>View<select id="mode"><option value="focus">Selected node and immediate neighbors</option><option value="overview">All submitted nodes and connections</option></select></label></div>'
    body='''<div class="legend"><span><i class="swatch" style="background:var(--yes)"></i>Supplier candidate present</span><span><i class="swatch" style="background:var(--no)"></i>No supplier candidate</span><span>Solid link: scoped supporting evidence; dashed: other audit status</span></div><p id="selected" aria-live="polite"></p><div class="plot"><svg id="graph" role="img" aria-label="Submitted component dependency graph with evidence states"></svg></div><h2>Supplier candidates</h2><div id="vendors" class="table-wrap"></div><h2>Connections and evidence</h2><div id="edges" class="table-wrap"></div><h2>Manufacturing-site coverage</h2><div id="sites" class="table-wrap"></div>'''
    data=dict(nodes=db['nodes'],edges=db['edges'],sources=db['sources'],site_coverage=db['vendor_site_coverage'],positions=pos,overview_height=height)
    body += '<h2>Definition and interpretation</h2><div id="definition" class="table-wrap"></div>'
    (FIG/'full_supply_chain_structure.html').write_text(page('GPU component structure and evidence',
        'The submitted JSON is preserved: arrows point from an input to the item or stage it feeds. Connections include categories, consumables and proposed material relationships—not observed shipments. Click a node to inspect its sources. Supplier presence does not prove interchangeability.',controls,body,GRAPH_JS,data))
    review_pos,review_height=overview(reviewed['nodes'],reviewed['edges'])
    review_data=dict(nodes=reviewed['nodes'],edges=reviewed['edges'],sources=reviewed['sources'],site_coverage=reviewed['vendor_site_coverage'],positions=review_pos,overview_height=review_height)
    (FIG/'full_supply_chain_reviewed_structure.html').write_text(page('Reviewed GPU dependency structure — provisional',
        'Review layer: duplicate bare/packaged die identities merged and six unsuitable default links excluded. Definitions and decision notes are available below. Retained links are NOT all verified recipes or shipments; missing process stages and conditional alternatives still prevent validated redundancy analysis. Original JSON is preserved separately.',controls,body,GRAPH_JS,review_data))
    world=json.loads((ROOT/'data/raw/natural_earth_countries.geojson').read_text())
    data=dict(world=world,facilities=[f for f in db['facilities'] if f['latitude'] not in ('',None) and f['longitude'] not in ('',None)],hubs=db['nearby_hub_candidates'],sources=db['sources'])
    controls='<div class="controls"><label>Production asset<select id="factory"></select></label></div>'
    body='''<div class="legend"><span>● Production asset</span><span>▲ Airport candidate</span><span>■ Port candidate</span><span>Dashed lines: proximity only, not verified freight routes</span></div><p id="selected" aria-live="polite"></p><div class="plot"><svg id="map" viewBox="0 0 1440 720" role="img" aria-label="World production locations and nearby airport and port candidates"></svg></div><div id="facility" class="table-wrap"></div><h2>Nearby hubs</h2><div id="hubtable" class="table-wrap"></div><p class="muted">Equirectangular world basemap: Natural Earth, 1:110m. Coordinates may be city proxies. Points and city labels do not establish borders, land access, cargo acceptance or actual supplier relationships.</p>'''
    (FIG/'full_supply_chain_transport_map.html').write_text(page('Production locations and nearby transport hubs',
        'This map screens geography. It does not reconstruct factory-to-factory shipments or calculate travel time. Airports have scheduled passenger/commercial service in OurAirports; air-cargo capability is unverified. Ports are World Port Index mirror candidates, not a fully vetted commercial-cargo set.',controls,body,MAP_JS,data))
    tasks=[
      dict(task='Preserve supplied JSON and audit graph integrity',status='done',detail='All 289 nodes and 757 edges retained; structural checks and evidence labels exported.'),
      dict(task='Verify every material/input relationship',status='partial',detail='Specific supporting sources and conflicts documented; unresolved edge statuses remain in the audit CSV.'),
      dict(task='Find suppliers for every component/material',status='partial',detail=f"{report['nodes_with_node_specific_vendor_evidence']} of 289 nodes have candidate evidence; categories/process stages do not all need independent vendors."),
      dict(task='Identify up to ten industry-leading suppliers per input',status='partial',detail='At most ten suppliers retained per node. Product capability is cited; comparable top-ten market rankings are generally not established.'),
      dict(task='Find all manufacturing sites for selected vendors',status='partial',detail=f"{report['public_production_site_rows']} public production-asset records; office/R&D-only sites excluded. Global footprint completeness and exact product-grade allocation remain partial."),
      dict(task='Nearest one to three commercial airports and ports',status='geographic_screening_done_cargo_validation_pending',detail=f"{report['nearest_hub_rows']} nearest-hub records; up to three of each type per geocoded asset. Cargo suitability and operational access are not verified."),
      dict(task='Clean database, sources and reproducible code',status='done',detail='CSV tables, consolidated JSON, raw inputs, source register, geocode cache, research logs and integrity tests included.'),
      dict(task='Two visualizations matching the updated data',status='done',detail='Offline original component explorer and production-location/hub map, plus a separate reviewed-structure explorer with scoped definitions.'),
      dict(task='Observed manufacturing times and multimodal delivery times',status='not_completed',detail='Earlier scenario assumptions are not observed node-specific lead times; this extension adds no fabricated times or booked routes.'),
      dict(task='Validated real-world redundancy analysis',status='not_completed',detail='Requires reviewed AND/OR dependencies, qualified supplier alternatives, site allocations, capacity and validated logistics. No finished analysis is claimed.'),
    ]
    raw=ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json'
    payload=dict(reviewed_on='2026-11-24',original_json_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),tasks=tasks,counts=report,
      visualization_qa=dict(javascript_dom_smoke_tests='Run node code/test_research_explorers.mjs',browser_layout_review='not_completed_browser_attachment_policy_and_localhost_access_unavailable'),
      important_warning='A completed research pass is not a complete real industry supply chain. Empty data are not approximated into facts.')
    save_json(CLEAN/'full_supply_chain_task_status.json',payload)
    coverage=rows('full_supply_chain_vendor_coverage.csv')
    save_json(CLEAN/'full_supply_chain_remaining_work.json',dict(
      nodes_without_supplier_candidates=[r for r in coverage if r['vendor_count']=='0'],
      supplier_site_followups=[r for r in db['vendor_site_coverage'] if r['site_status'] not in {'product_class_site_documented','fabless_designer_no_owned_fab_required'}],
      graph_review_issues=db['modeling_issues'],
      edge_review_file='full_supply_chain_edges_audit.csv',
      note='Even product_class_site_documented still requires grade/customer qualification; listed candidate branches may cover only part of a combined node.'))
    save_json(CLEAN/'full_supply_chain_data_dictionary.json',dict(
      node_identifier='Original submitted node id is preserved. Nodes include saleable materials, internal parts, categories and stages; not all represent independent procurement markets.',
      edge_direction='source_node_id is an input/category member/process predecessor; target_node_id is its proposed dependent node. Check recommended_relationship and audit_note before applying AND/OR or transport semantics.',
      vendor_join='nodes.id = vendors.full_graph_node_id = vendor_site_coverage.node_id; provider_id is an identifier, not a market rank.',
      site_join='vendor_site_coverage.product_class_site_ids and other_company_site_ids reference facilities.facility_id. Semicolon-delimited IDs are lists; empty product scope is unallocated, not every vendor product.',
      hub_join='nearby_hub_candidates.facility_id references facilities.facility_id; (facility_id,hub_type,proximity_rank) identifies a row. The same hub may appear for many factories.',
      source_join='Every source_ids/ownership_source_ids value references sources.source_id. The source use/reliability and claim-specific note limit what the citation establishes.',
      coordinates='Decimal degrees (WGS84-style latitude/longitude). coordinate_precision distinguishes inherited approximations and city/district proxies; no factory-gate precision is implied.',
      distance='great_circle_distance_km is spherical great-circle distance in kilometres, Earth radius 6371.0088 km. It is not road/rail/seaway distance or duration.',
      manufacturing_times='The full-node extension contains no observed manufacturing-time series. Older manufacturing_time_assumptions.csv describes a separate scenario, not newly verified durations.',
      missing_values='Empty fields mean missing, not applicable or unestablished as explained by the status/note. Never convert missing duration, share or capacity into zero.',
      counts='Nodes with vendor candidates measures presence of some capability evidence. Partial branches, internal-part capability and unqualified grades do not establish complete node coverage or independent redundancy.',
      views='New HTML views use the full-node extension; older PNGs/unified_graph.json/transport statistics describe the legacy smaller model.',
    ))
    lines=['GPU SUPPLY-CHAIN RESEARCH HANDOFF','Review date: 2026-11-24','',
      'Scope: best-effort public evidence extension of the supplied JSON, not a confidential NVIDIA procurement reconstruction.','',
      f"Nodes: 289; proposed connections: 757; nodes with supplier candidates: {report['nodes_with_node_specific_vendor_evidence']}; supplier-node records: {report['vendor_component_rows']}; public production-asset records: {report['public_production_site_rows']}; nearest-hub records: {report['nearest_hub_rows']}.",'',
      'TASK STATUS','']
    for t in tasks:lines.extend([t['status'].upper()+': '+t['task'],t['detail'],''])
    lines.extend(['HOW TO OPEN THE PACKAGE',
      '1. Open figures/full_supply_chain_structure.html to browse components, suppliers and edge citations.',
      '2. Open figures/full_supply_chain_transport_map.html to inspect factories and geographic hub candidates.',
      '3. Import data/clean/full_supply_chain_research_database.json for the consolidated machine-readable dataset.',
      '4. Use data/clean/full_supply_chain_remaining_work.json for the unresolved research queue; GAP_DIAGNOSIS.txt explains each remaining supplier-node gap.',
      '5. Read FULL_SUPPLY_CHAIN_EVIDENCE_NOTES.md for caveats and the correction to the earlier overly broad edge audit.','',
      'REBUILD (from repository root)',
      'python3 code/build_full_supply_chain_evidence.py',
      'python3 code/build_research_handoff.py',
      'python3 code/test_public_research_integrity.py','',
      'The rebuild uses checked-in inputs and no external Python packages. Refreshing geocodes is optional and uses a rate-limited network service.',
      'The older PNGs and legacy transport/time tables describe the earlier smaller model, not this complete-node research extension.',
      'Definition and semantic review: see STRUCTURE_REVIEW.txt, component_definitions.json and structure_review_decisions.csv. Original input preserved; revised graph is provisional.',
      'Visualization QA: JavaScript/DOM smoke tests exercise all three files. Actual browser layout review was unavailable: in-app localhost timed out and local Chrome attachment required an app network-policy update.'])
    (ROOT/'RESEARCH_HANDOFF.txt').write_text('\n'.join(lines)+'\n')
    print('Built three offline visualizations, task status, unresolved queue and RESEARCH_HANDOFF.txt')

if __name__=='__main__':main()
