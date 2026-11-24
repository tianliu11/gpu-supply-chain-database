#!/usr/bin/env python3
"""Conservative, reversible semantic review; not a qualified procurement graph."""
import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from component_definition_research import DEFINITIONS

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT/'data/clean'

def save_table(name, records):
    with (CLEAN/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def main():
    db = json.loads((CLEAN/'full_supply_chain_research_database.json').read_text())
    definitions = list(DEFINITIONS.values())
    source_ids = {s['source_id'] for s in db['sources']}
    for d in definitions:
        assert set(filter(None, d['source_ids'].split(';'))) <= source_ids, d
    save_table('component_definitions.csv', definitions)
    (CLEAN/'component_definitions.json').write_text(json.dumps(definitions, indent=2)+'\n')
    # Canonical IDs remove the original packaged-output -> bare-die reversal.
    aliases = {'LD:finished_logic_die':'1.2', '1.2.1':'LD:logic_die_fabricated'}
    nodes = {}
    for n in db['nodes']:
        nid = aliases.get(n['id'], n['id'])
        if nid not in nodes:
            nodes[nid] = dict(n, id=nid, original_node_ids=[], vendor_candidates=[])
        nodes[nid]['original_node_ids'].append(n['id'])
        nodes[nid]['vendor_candidates'].extend(n['vendor_candidates'])
        if nid in DEFINITIONS:
            nodes[nid]['name'] = DEFINITIONS[nid]['preferred_name']
            nodes[nid]['component_definition'] = DEFINITIONS[nid]
    exclusions = {
        'E0036': 'Removed reversed packaged-output to bare-die dependency; aliases preserve both original node IDs.',
        'E0101': 'Soda-lime mask substrate is not established for the selected advanced-logic case.',
        'E0486': 'Generic coating resin does not establish a photoresist binder recipe.',
        'E0527': 'Generic coating resin does not establish a pressure-sensitive adhesive recipe.',
        'E0541': 'Generic coating resin does not establish an electrical-steel interlaminar varnish recipe.',
        'E0754': 'YAG phosphor is not a mandatory input for a direct-emitting RGB LED option.'}
    reviews, edges = [], []
    for original in db['edges']:
        e = dict(original)
        eid = e['edge_id']
        e['source_node_id'] = aliases.get(e['source_node_id'], e['source_node_id'])
        e['target_node_id'] = aliases.get(e['target_node_id'], e['target_node_id'])
        kind = DEFINITIONS.get(e['target_node_id'], {}).get('semantic_kind', '')
        relation = 'dependency_or_ancestry_requires_process_review'
        note = 'Retained as submitted dependency; not a verified direct shipment or universal AND requirement.'
        if kind in ('material_family','component_group','process_consumable_family','category'):
            relation = 'category_or_family_membership'
            note = 'Group membership is not a shipment; select applicable species/device families before analysis.'
        if eid in ('E0037','E0041'):
            relation = 'process_output'
        elif eid == 'E0038':
            relation = 'bare_die_input_to_packaging'
        elif eid in ('E0004','E0005'):
            relation = 'physical_constituent_not_additional_process'
            note = 'Descriptive package constituent; do not add another manufacture or packaging duration.'
        elif e['source_node_id'] == 'SC-SMD-TERM':
            relation = 'device_specific_internal_structure'
            note = 'R/C/L termination recipes differ; not an independently qualified merchant input.'
        enabled = eid not in exclusions
        if not enabled:
            note = exclusions[eid]
        e.update(reviewed_relation=relation, enabled_in_reviewed_view=enabled,
                 review_note=note, observed_shipping_edge=False)
        reviews.append(dict(edge_id=eid, original_source=original['source_node_id'],
            original_target=original['target_node_id'], reviewed_source=e['source_node_id'],
            reviewed_target=e['target_node_id'], enabled=enabled, relation=relation,
            decision=note, source_ids=original.get('source_ids','')))
        if enabled:
            e['audit_note'] = note+' Original evidence: '+e.get('audit_note','')
            edges.append(e)
    # Every original edge has a decision; retained edges remain explicitly unqualified.
    assert len(reviews) == len(db['edges'])
    indegree = Counter(e['target_node_id'] for e in edges)
    outgoing = defaultdict(list)
    for e in edges:
        assert e['source_node_id'] in nodes and e['target_node_id'] in nodes
        outgoing[e['source_node_id']].append(e['target_node_id'])
    queue = deque(n for n in nodes if not indegree[n])
    visited = 0
    while queue:
        node = queue.popleft(); visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if not indegree[target]: queue.append(target)
    assert visited == len(nodes), 'Reviewed dependency graph contains a cycle'
    save_table('structure_review_decisions.csv', reviews)
    meta = dict(original_nodes=len(db['nodes']), original_edges=len(db['edges']),
        reviewed_nodes=len(nodes), reviewed_edges=len(edges), aliases=aliases,
        excluded_edges=exclusions, definitions_added=len(definitions), acyclic=True,
        original_sha256=hashlib.sha256((ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json').read_bytes()).hexdigest(),
        readiness='Semantic review draft, NOT a verified full process or transport network',
        open_issues=[
          'Polysilicon deposition/crystal growth/wafer preparation still need separate process nodes; starter rods and TCS are upstream of wafer production, not direct fab inputs.',
          'R/C/L passive groups must select distinct device recipes; current shared inputs are not one universal bill of materials.',
          'Leadframe/bond-wire and flip-chip package options must be selected rather than all imposed simultaneously.',
          'Memory generation, connector generation, quantities and mechanical dimensions require a chosen reference design.',
          'Raw-ore ancestry is not a direct factory shipment. Refining and recovery pathways need process-specific review.',
          'Definitions do not verify every existing edge, exact grade, supplier qualification, site allocation or logistics route.'])
    result = dict(metadata=meta, nodes=list(nodes.values()), edges=edges, sources=db['sources'],
        vendor_site_coverage=[dict(r, node_id=aliases.get(r.get('node_id'),r.get('node_id'))) for r in db['vendor_site_coverage']])
    (CLEAN/'reviewed_supply_chain_structure.json').write_text(json.dumps(result,indent=2)+'\n')
    (CLEAN/'structure_review_summary.json').write_text(json.dumps(meta,indent=2)+'\n')
    lines = ['COMPONENT DEFINITIONS AND STRUCTURE REVIEW', '',
        f"{len(definitions)} scoped definitions; {len(nodes)} canonical nodes; {len(edges)} retained dependencies.",
        'Original 289-node / 757-edge JSON is unchanged. This is a reversible review layer, not a claim that all relationships are correct.',
        '', 'CORRECTED: packaged chip -> bare die reversal and duplicate packaged/bare identities.',
        'EXCLUDED FROM REVIEWED DEFAULT: '+', '.join(exclusions), '', 'IMPORTANT REMAINING STRUCTURAL WORK'] + meta['open_issues']
    for d in definitions:
        lines += ['', d['node_id']+' | '+d['preferred_name'], d['formal_definition'],
                  'Scope: '+d['project_interpretation'], 'Sources: '+(d['source_ids'] or 'Source review open')]
    (ROOT/'STRUCTURE_REVIEW.txt').write_text('\n'.join(lines)+'\n')
    print(f'Reviewed structure: {len(nodes)} nodes, {len(edges)} edges; {len(definitions)} definitions.')
    return result

if __name__ == '__main__': main()
