import csv
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
OUT=BASE/'merged'

def rows(name):
    with (OUT/name).open(newline='') as f: return list(csv.DictReader(f))

class ReconciliationTests(unittest.TestCase):
    def test_input_manifest(self):
        s=json.loads((OUT/'reconciliation_summary.json').read_text())
        self.assertEqual(s['original_batch_vendor_rows'],1793)
        self.assertEqual(s['batch_node_ids'],278)
        for r in s['original_manifest']:
            self.assertEqual(hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest(),r['sha256'])

    def test_all_original_rows_preserved(self):
        candidates=rows('vendor_candidates.csv')
        self.assertEqual(len({r['record_id'] for r in candidates}),len(candidates))
        self.assertEqual(sum(r['input_file'].startswith('V') for r in candidates),1793)
        self.assertEqual(len(rows('node_coverage.csv')),289)

    def test_claims_are_not_auto_approved(self):
        candidates=rows('vendor_candidates.csv')
        for r in candidates:
            self.assertEqual(r['observed_procurement'],'False')
            if r['review_status']=='prior_scoped_capability_evidence':
                self.assertTrue(r['prior_source_ids'])
                self.assertTrue(r['prior_product_scope'])
            if r['review_status']=='citation_present_content_review_pending':
                self.assertTrue(r['source_ids'])
            self.assertNotIn('verified_market_rank',r['ranking_review_status'])

    def test_source_foreign_keys(self):
        sources={r['source_id'] for r in rows('sources.csv')}
        for r in rows('vendor_candidates.csv'):
            for field in ('source_ids','prior_source_ids','alias_source_ids'):
                self.assertTrue(set(filter(None,r.get(field,'').split(';')))<=sources)

    def test_screen_and_market_review_preserve_claim_boundaries(self):
        candidates = {r['record_id']: r for r in rows('vendor_candidates.csv')}
        for screen in rows('vendor_citation_screen.csv'):
            record = candidates[screen['record_id']]
            self.assertIn(screen['source_id'], record['source_ids'].split(';'))
            self.assertEqual(screen['node_id'], record['node_id'])
        for review in rows('manual_market_claim_reviews.csv'):
            record = candidates[review['record_id']]
            self.assertEqual(review['result'], record['ranking_review_status'])
            self.assertEqual(review['exact_gpu_product_or_factory_qualification'], 'False')

    def test_site_joins_do_not_imply_backups(self):
        sites={r['facility_id'] for r in rows('production_sites.csv')}
        candidates={r['record_id'] for r in rows('vendor_candidates.csv')}
        for r in rows('vendor_site_links.csv'):
            self.assertIn(r['facility_id'],sites)
            self.assertIn(r['record_id'],candidates)
            self.assertEqual(r['qualified_backup'],'False')

    def test_portable_hub_script(self):
        spec=importlib.util.spec_from_file_location('portable_hubs',BASE/'code/hubs.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        hubs=[dict(id=str(i),lat=0,lon=i/100) for i in range(4)]
        self.assertEqual([h['id'] for _,h in module.nearest(0,0,hubs)],['0','1','2'])
        self.assertTrue(module.load_airports())
        self.assertTrue(module.load_ports())

if __name__=='__main__': unittest.main()
