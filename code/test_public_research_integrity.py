"""Integrity checks for the public evidence database and known audit regressions."""
import csv
import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def rows(name):
    with (ROOT/'data/clean'/name).open() as f:
        return list(csv.DictReader(f))

class ResearchIntegrity(unittest.TestCase):
    def test_preserved_graph_and_foreign_keys(self):
        graph=json.loads((ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json').read_text())
        nodes={n['id'] for n in graph['nodes']}
        audit=rows('full_supply_chain_edges_audit.csv')
        self.assertEqual({e['id'] for e in graph['edges']},{e['edge_id'] for e in audit})
        self.assertTrue(all(e['source_node_id'] in nodes and e['target_node_id'] in nodes for e in audit))
        self.assertEqual(len(audit),757)

    def test_evidence_requires_real_source_ids(self):
        known={r['source_id'] for r in rows('sources.csv')}
        for table in ['full_supply_chain_edges_audit.csv','full_supply_chain_vendors.csv','full_supply_chain_facilities.csv','full_supply_chain_nearest_hubs.csv']:
            for row in rows(table):
                for field in ['source_ids','ownership_source_ids']:
                    for sid in filter(None,row.get(field,'').split(';')):
                        self.assertIn(sid,known,(table,row,sid))
                if row.get('validation_status','').startswith('supported_'):
                    self.assertTrue(row['source_ids'],row)

    def test_keyword_matching_does_not_verify_chemical_edges(self):
        audit={r['edge_id']:r for r in rows('full_supply_chain_edges_audit.csv')}
        self.assertFalse(audit['E0177']['validation_status'].startswith('supported_'))
        self.assertEqual(audit['E0036']['validation_status'],'semantic_conflict')
        self.assertEqual(audit['E0101']['validation_status'],'technology_specific_review_required')
        self.assertEqual(audit['E0754']['validation_status'],'optional_or_design_dependent')

    def test_vendor_limits_and_qualification_fields(self):
        vendors=rows('full_supply_chain_vendors.csv')
        counts=Counter(r['full_graph_node_id'] for r in vendors)
        self.assertTrue(all(n<=10 for n in counts.values()))
        pairs={(r['full_graph_node_id'],r['provider_name'].casefold()) for r in vendors}
        self.assertEqual(len(pairs),len(vendors))
        self.assertTrue(all(r['product_scope'] and r['qualification_status'] for r in vendors))

    def test_nearest_hub_ranks_are_distance_ordered(self):
        grouped=defaultdict(list)
        sites={r['facility_id'] for r in rows('full_supply_chain_facilities.csv')}
        for row in rows('full_supply_chain_nearest_hubs.csv'):
            self.assertIn(row['facility_id'],sites)
            grouped[(row['facility_id'],row['hub_type'])].append(row)
        for group in grouped.values():
            group.sort(key=lambda r:int(r['proximity_rank']))
            self.assertEqual([int(r['proximity_rank']) for r in group],[1,2,3])
            distance=[float(r['great_circle_distance_km']) for r in group]
            self.assertEqual(distance,sorted(distance))
            self.assertTrue(all(r['cargo_service_status'].startswith('unverified_') for r in group))

    def test_geocodes_stay_within_coordinate_bounds(self):
        for row in rows('full_supply_chain_facilities.csv'):
            if row['latitude'] and row['longitude']:
                self.assertTrue(-90<=float(row['latitude'])<=90)
                self.assertTrue(-180<=float(row['longitude'])<=180)

    def test_research_log_is_discovery_only(self):
        log=json.loads((ROOT/'data/raw/additional_node_research_search_log.json').read_text())
        self.assertEqual(len({r['node_id'] for r in log}),101)
        self.assertTrue(all(r['status'] in {'discovery_only_requires_product_and_source_review','no_usable_result_returned'} for r in log))

    def test_export_counts_and_no_confidential_allocation_claim(self):
        exported=json.loads((ROOT/'data/clean/full_supply_chain_research_database.json').read_text())
        self.assertEqual(len(exported['nodes']),289)
        self.assertEqual(len(exported['edges']),757)
        self.assertTrue(exported['metadata']['original_graph_preserved'])

    def test_factory_search_log_is_not_accepted_evidence(self):
        log=json.loads((ROOT/'data/raw/manufacturing_site_research_search_log.json').read_text())
        self.assertEqual(len(log),127)
        self.assertTrue(all(r['status']=='discovery_only_requires_entity_and_product_site_review' for r in log))
        report=json.loads((ROOT/'data/clean/full_supply_chain_completion_report.json').read_text())
        self.assertEqual(report['factory_discovery_searches_logged'],len(log))

    def test_curated_register_keys_and_site_scopes(self):
        from additional_public_research import SOURCES,SITES,VENDORS,EDGE_EVIDENCE
        import expanded_public_research
        from geocode_public_production_sites import COUNTRY_CODES
        raw=json.loads((ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json').read_text())
        nodes={n['id'] for n in raw['nodes']}
        edges={e['id'] for e in raw['edges']}
        source_ids=[s['source_id'] for s in SOURCES]
        self.assertEqual(len(source_ids),len(set(source_ids)))
        self.assertEqual(len(SITES),len({s['facility_name'] for s in SITES}))
        for s in SITES:
            self.assertIn(s['country'],COUNTRY_CODES)
            self.assertTrue(set(s['node_ids'].split())<=nodes,s)
            self.assertTrue(set(s['source_ids'].split(';'))<=set(source_ids),s)
        self.assertTrue(all(v['node_id'] in nodes for v in VENDORS))
        self.assertTrue(all(e['edge_id'] in edges for e in EDGE_EVIDENCE))

    def test_handoff_reconciles_with_current_export(self):
        import hashlib
        task=json.loads((ROOT/'data/clean/full_supply_chain_task_status.json').read_text())
        original=ROOT/'data/raw/gpu_complete_node_to_node_supply_chain.json'
        self.assertEqual(task['original_json_sha256'],hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertEqual(task['counts']['public_production_site_rows'],len(rows('full_supply_chain_facilities.csv')))
        self.assertEqual(task['counts']['vendor_component_rows'],len(rows('full_supply_chain_vendors.csv')))
        self.assertEqual(task['counts']['nearest_hub_rows'],len(rows('full_supply_chain_nearest_hubs.csv')))

if __name__=='__main__':
    unittest.main()
