#!/usr/bin/env python3
"""Conservative, reversible semantic review; not a qualified procurement graph."""
import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from component_definition_research import DEFINITIONS
from process_validation_research import expand_structure, CLAIMS as PROCESS_CLAIMS
from remaining_public_research import CLAIMS as ADDITIONAL_CLAIMS
from claude_followup_research import CLAIMS as FOLLOWUP_CLAIMS

# Latest explicit claim wins for a repeated original relation. Never count
# duplicated citations as independently validated graph edges.
CLAIMS = list({c['edge_id']: c for c in PROCESS_CLAIMS + ADDITIONAL_CLAIMS + FOLLOWUP_CLAIMS}.values())

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT/'data/clean'

def save_table(name, records):
    with (CLEAN/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
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
        'E0042': 'Leadframe is not a mandatory input for the selected substrate-based flip-chip logic package; retained in the original technology catalogue.',
        'E0043': 'Bond wire is not a mandatory die interconnect for the selected flip-chip logic package; other package branches may still use it.',
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
    added_edges=expand_structure(nodes,edges,reviews)
    indegrees=Counter(e['target_node_id'] for e in edges)
    outdegrees=Counter(e['source_node_id'] for e in edges)
    for nid,n in nodes.items():
        n.update(in_degree=indegrees[nid],out_degree=outdegrees[nid])
    for e in edges:
        e['source_node_name']=nodes[e['source_node_id']]['name']
        e['target_node_name']=nodes[e['target_node_id']]['name']
    save_table('process_validation_claims.csv',CLAIMS)
    save_table('reviewed_structure_added_edges.csv',added_edges)
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
        added_process_and_component_nodes=18, added_edges=len(added_edges),
        original_edge_claims_researched_this_pass=len(CLAIMS),
        selected_scope='Representative CZ silicon-wafer route and substrate-based flip-chip logic packaging; not an exact branded GPU BOM',
        original_sha256=hashlib.sha256((ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json').read_bytes()).hexdigest(),
        readiness='Semantic review draft, NOT a verified full process or transport network',
        open_issues=[
          'Wafer process backbone is expanded and sourced; ancillary chemistry, selected dopant species and optional epitaxy still need process-specific specifications.',
          'R/C/L finished-device branches are now separated; exact internal recipes and board quantities remain part-specific.',
          'The reviewed logic package selects flip-chip; package details for memory and power devices still need individual part choices.',
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
    audit_counts=Counter(e['validation_status'] for e in db['edges'])
    summary=dict(original_claims_researched=len(CLAIMS),claim_outcomes=dict(Counter(c['validation_status'] for c in CLAIMS)),
        additional_process_component_nodes=18,additional_links=len(added_edges),
        original_links_excluded=len(exclusions),original_audit_status_counts=dict(audit_counts),
        important_scope='Source-backed process/material classes are not proof of exact GPU recipes, qualified supplier interchangeability, or observed shipments.',
        research_still_open='Unverified relations and upstream lineage entries remain unfinished research. They are not declared impossible to validate.',
        external_information_needed='Actual customer contracts, qualified part numbers, production queues, route bookings and capacity are not established by the sources inspected.')
    (CLEAN/'process_validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    text=['VALIDATION RESULTS — 2026-11-24','',
      f"Individually researched {len(CLAIMS)} original relationship claims; outcomes and sources are in data/clean/process_validation_claims.csv.",
      'Implemented corrections, not just warnings:',
      '- Polysilicon deposition -> polysilicon -> CZ growth -> ingot -> wafer forming -> wafer.',
      '- Distinct resistor, capacitor and inductor/filter finished-device branches.',
      '- Substrate-based flip-chip logic-package scenario; no mandatory leadframe/bond-wire inputs.',
      '- Polyol/isocyanate inputs for polyurethane; intermediate PO and PGME stages for PGMEA.',
      '- Separate transmissive and EUV mask branches; pellicles remain exposure-specific accessories.',
      '- Anthraquinone carrier and process stage for peroxide; no direct gas-mixing shortcut.',
      '- Rechecked Wacker Burghausen and SUMCO Imari records; added six Murata capacitor production locations.',
      '- Merged Shinko/Shinko Electric Industries supplier identity to prevent false redundancy.',
      '', 'Limits of the result:',summary['important_scope'],summary['research_still_open'],summary['external_information_needed'],
      '', 'Original-edge evidence totals (not a completion percentage):']
    text += [f'{k}: {v}' for k,v in sorted(audit_counts.items())]
    (ROOT/'VALIDATION_RESULTS.txt').write_text('\n'.join(text)+'\n')
    print(f'Reviewed structure: {len(nodes)} nodes, {len(edges)} edges; {len(definitions)} definitions.')
    return result

if __name__ == '__main__': main()
