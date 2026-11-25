"""Reconcile supplied batches without promoting an unchecked claim to fact.

The original batches and existing reviewed database are read-only inputs.
Run from any directory. Only merged/ outputs are replaced on rerun.
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from review_market_claims import review_claim

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
OUT=BASE/'merged'
REVIEWED_NAMES={
    'Sumitomo Chemical (Sumikasuper)': ('Sumitomo Chemical','R7_SUMITOMO_LCP'),
    'Toray (Siveras)': ('Toray Industries','R7_TORAY_LCP'),
    'PC Partner (Zotac)': ('PC Partner','R12_PCP_PRODUCTS'),
    'Henkel (Loctite Ablestik)': ('Henkel','R12_HENKEL_DA'),
    'Celanese (Vectra/Zenite)': ('Celanese','R12_CELANESE_LCP'),
    'Cargill (Cargill Salt)': ('Cargill','R12_CARGILL_SALT'),
    'Kazphosphate (Novo-Dzhambul Phosphorus Plant)': ('Kazphosphate','R12_KAZ_PHOSPHORUS'),
    'Mitsubishi Chemical (jER)': ('Mitsubishi Chemical','R12_MCC_EPOXY'),
}

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def write(name, rows):
    if not rows:
        return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        w.writeheader();w.writerows(rows)

def key(name):
    # Punctuation/case normalization only. No fuzzy company or parent matches.
    return re.sub(r'[^a-z0-9]','',name.casefold())

def placeholder(name):
    return name.upper().startswith(('UNRESOLVED','N/A','NOT FOUND'))

def main():
    OUT.mkdir(exist_ok=True)
    graph=json.loads((ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json').read_text())
    nodes={n['id']:n['name'] for n in graph['nodes']}
    old=read(ROOT/'data/clean/full_supply_chain_vendors.csv')
    known={(r['full_graph_node_id'],key(r['provider_name'])):r for r in old}
    sources=read(ROOT/'data/clean/sources.csv')
    source_map={r['source_id']:r for r in sources}
    batch_sources=[]
    review_path=BASE/'method/SOURCE_RECHECKS.json'
    rechecks={r['source_id']:r for r in json.loads(review_path.read_text())} if review_path.exists() else {}
    manifest=[]
    vendors=[]
    for path in sorted((BASE/'batches').glob('*.csv')):
        rows=read(path)
        manifest.append(dict(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=len(rows)))
        if path.name.endswith('_sources.csv'):
            for r in rows:
                assert r['source_id'] not in source_map, r['source_id']
                source_map[r['source_id']]=r
                review=rechecks.get(r['source_id'],{})
                batch_sources.append(dict(r,source_batch=path.stem.split('_')[0],
                    content_review=review.get('review_status','not_independently_rechecked'),
                    reviewed_scope=review.get('scope',''),reviewed_restriction=review.get('restriction','')))
        else:
            vendors.extend(dict(r,input_file=path.name,input_row=i+2) for i,r in enumerate(rows))
    reconciled=[]
    represented=set()
    for r in vendors:
        nid=r['node_id']; name=r['vendor_name']
        assert nid in nodes,(nid,name)
        cited=[s.strip() for s in r['source_ids'].split(';') if s.strip()]
        assert all(s in source_map for s in cited),(nid,cited)
        canonical,alias_source=REVIEWED_NAMES.get(name,(name,''))
        pair=(nid,key(canonical)); previous=known.get(pair)
        represented.add(pair)
        status=('not_a_vendor_record' if placeholder(name) else
                'prior_scoped_capability_evidence' if previous else
                'citation_present_content_review_pending' if cited else 'missing_citation')
        # No inherited ranking: old evidence supports capability only.
        rank_basis=r['ranking_basis'].casefold()
        rank_status=('unordered_listing_not_market_rank' if any(t in rank_basis for t in ('unordered','key player','named','capability')) else 'ranking_claim_requires_source_review')
        row=dict(r,record_id=f"{r['input_file']}:{r['input_row']}",
                 canonical_vendor_name=canonical,alias_source_ids=alias_source,
                 review_status=status,ranking_review_status=rank_status,
                 prior_source_ids=previous['source_ids'] if previous else '',
                 prior_product_scope=previous['product_scope'] if previous else '',
                 prior_qualification_status=previous['qualification_status'] if previous else '',
                 observed_procurement=False)
        reconciled.append(row)
    # Preserve older scoped suppliers even if Claude omitted them; do not replace
    # an evidence-backed record with a placeholder or speculative rank.
    for r in old:
        pair=(r['full_graph_node_id'],key(r['provider_name']))
        if pair in represented: continue
        reconciled.append(dict(node_id=r['full_graph_node_id'],node_name=r['full_graph_node_name'],
            vendor_name=r['provider_name'],vendor_parent_group=r['corporate_group'],
            vendor_role=r['provider_role'],vendor_rank='',ranking_basis='',metric_value='',metric_year='',
            source_ids=r['source_ids'],record_id='prior:'+r['full_graph_node_id']+':'+r['provider_id'],
            input_file='data/clean/full_supply_chain_vendors.csv',input_row='',
            review_status='prior_scoped_capability_evidence',ranking_review_status='no_new_rank_claim',
            prior_source_ids=r['source_ids'],prior_product_scope=r['product_scope'],
            prior_qualification_status=r['qualification_status'],observed_procurement=False))
    facilities=read(ROOT/'data/clean/full_supply_chain_facilities.csv')
    by_company=defaultdict(list)
    for f in facilities: by_company[key(f['company'])].append(f)
    joins=[]; queue=defaultdict(lambda:dict(nodes=set(),names=set()))
    for r in reconciled:
        if r['review_status']=='not_a_vendor_record': continue
        matches=by_company[key(r.get('canonical_vendor_name',r['vendor_name']))]
        if not matches:
            q=queue[key(r['vendor_name'])];q['nodes'].add(r['node_id']);q['names'].add(r['vendor_name'])
        for f in matches:
            scoped=r['node_id'] in re.split(r'[;\s]+',f['component_categories'])
            joins.append(dict(record_id=r['record_id'],node_id=r['node_id'],vendor_name=r['vendor_name'],
                facility_id=f['facility_id'],company_name_match='exact_after_punctuation_normalization',
                product_allocation='documented_class_only' if scoped else 'company_site_only_not_product_allocation',
                site_source_ids=f['source_ids'],qualified_backup=False))
    screen_path = OUT/'vendor_citation_screen.csv'
    screening = defaultdict(Counter)
    if screen_path.exists():
        for row in read(screen_path):
            screening[row['record_id']][row['screen_result']] += 1
    market_reviews = []
    for row in reconciled:
        if row['input_file'].startswith('V'):
            result = review_claim(row)
            if result:
                market_reviews.append(result)
                row['ranking_review_status'] = result['result']
        counts = screening[row['record_id']]
        row['citation_screen_count'] = sum(counts.values())
        row['citation_screen_results'] = ';'.join(f'{k}={v}' for k,v in sorted(counts.items()))
    write('manual_market_claim_reviews.csv', market_reviews)
    coverage=[]
    raw_nodes={r['node_id'] for r in vendors}
    for nid,name in nodes.items():
        rr=[r for r in reconciled if r['node_id']==nid]
        counts=Counter(r['review_status'] for r in rr)
        coverage.append(dict(node_id=nid,node_name=name,claude_batch_present=nid in raw_nodes,
            prior_capability_rows=counts['prior_scoped_capability_evidence'],
            cited_rows_pending_review=counts['citation_present_content_review_pending'],
            uncited_rows=counts['missing_citation'],placeholder_rows=counts['not_a_vendor_record'],
            company_site_links=sum(j['node_id']==nid for j in joins)))
    write('vendor_candidates.csv',reconciled)
    write('sources.csv',[dict(r,record_origin='prior_database') for r in sources]+batch_sources)
    write('vendor_site_links.csv',joins)
    write('production_sites.csv',facilities)
    write('nearest_hubs.csv',read(ROOT/'data/clean/full_supply_chain_nearest_hubs.csv'))
    write('node_coverage.csv',coverage)
    write('vendor_research_queue.csv',[dict(vendor_name=';'.join(sorted(q['names'])),node_ids=';'.join(sorted(q['nodes'])),status='no_exact_name_site_match_alias_or_site_research_needed') for q in queue.values()])
    write('citation_repair_queue.csv',[r for r in reconciled if r['review_status']=='missing_citation'])
    edges=read(ROOT/'data/clean/full_supply_chain_edges_audit.csv')
    write('edge_evidence.csv',edges)
    write('edge_review_queue.csv',[r for r in edges if not r['validation_status'].startswith('supported_')])
    summary=dict(batch_files=len(manifest),original_batch_vendor_rows=len(vendors),original_batch_source_rows=len(batch_sources),
        batch_node_ids=len(raw_nodes),missing_from_batches=[dict(node_id=nid,node_name=nodes[nid]) for nid in nodes.keys()-raw_nodes],
        merged_candidate_rows=len(reconciled),statuses=dict(Counter(r['review_status'] for r in reconciled)),
        previously_uncited_batch_rows_recovered=sum(r['input_file'].startswith('V') and not r['source_ids'] and r['review_status']=='prior_scoped_capability_evidence' for r in reconciled),
        uncited_placeholder_rows=sum(r['input_file'].startswith('V') and not r['source_ids'] and r['review_status']=='not_a_vendor_record' for r in reconciled),
        node_coverage_rows=len(coverage),public_production_site_rows=len(facilities),
        claim_citation_links_screened=sum(sum(c.values()) for c in screening.values()),
        pending_vendor_rows_screened=sum(bool(screening[r['record_id']]) for r in reconciled
                                       if r['review_status']=='citation_present_content_review_pending'),
        independently_reviewed_market_claim_rows=len(market_reviews),
        nearest_hub_rows=len(read(ROOT/'data/clean/full_supply_chain_nearest_hubs.csv')),
        vendors_without_exact_name_site_match=len(queue),site_link_rows=len(joins),
        claim='Reconciliation and scoped prior evidence; not all batch citations, ranks, factories or relationships have been independently validated.',
        original_manifest=manifest)
    (OUT/'reconciliation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (OUT/'README.txt').write_text(
        'RECONCILED RESEARCH HANDOFF\n\n'
        'vendor_candidates.csv preserves every batch row plus older scoped suppliers omitted from the batches.\n'
        'A citation-present status is not independent verification. Original numeric ranks remain claims, not accepted market rankings.\n'
        'prior_source_ids and prior_product_scope carry only the earlier evidence, not the new rank.\n'
        'production_sites.csv and nearest_hubs.csv reuse the existing sourced site/hub database.\n'
        'vendor_site_links.csv uses exact normalized company names only. Missing matches may be aliases, not missing factories.\n'
        'No site is inherited from headquarters country. No nearby hub is a confirmed freight lane.\n'
        'node_coverage.csv includes all 289 nodes, including those missing from Claude batches.\n'
        'citation_repair_queue.csv, vendor_research_queue.csv and edge_review_queue.csv expose remaining research.\n'
        'Batch files and main reviewed database are unchanged. Rerun: python3 research_2026-11-24/code/reconcile.py\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('original_manifest','missing_from_batches')},indent=2))

if __name__=='__main__': main()
