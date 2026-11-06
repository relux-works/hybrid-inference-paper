"""Published labels and finite-capacity invariants; no empirical GLM validation."""
import csv
import gzip
import math
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run26 import export, model as m


def rows(name):
    with (export.OUT/name).open()as f:return list(csv.DictReader(f))


def conditions(sentence):
    needed=('dedicated calendar billing','MB/s','RTT','client','s=','cache allowance','load',
            'call shapes inside the measured ladder','normalized per person-month','full log mix unsupported','calls/person-day','calls/person-month','GB')
    return all(x in sentence for x in needed) and any(x in sentence for x in ('bought','rented'))


class Run26Published(unittest.TestCase):
    # Parent files and both source/output hashes are checked, including the new report.
    def test_all_accepted_parent_bytes_positive_manifest(self):
        a=export.audit()
        self.assertTrue(a['all_parent_bytes_identical']);self.assertLess(a['csv_bytes'],50_000_000)
        self.assertGreater(a['parent_files'],1900)

    # A partial shape cohort must not become the full workload in a published comparison.
    def test_coverage_not_full_log_positive_both_profiles(self):
        rr=rows('middle_cost.csv');self.assertEqual({x['profile']for x in rr},{'existing_combined','claude_deep'})
        for r in rr:
            self.assertIn('full log mix unsupported',r['coverage']);self.assertIn('CALL SHAPES',r['coverage'])
            self.assertEqual(int(r['selected_shapes']),10885 if r['profile']=='existing_combined' else 554)

    # Purchased capital is present; the cloud class and excluded5090 never enter hybrid cost rows.
    def test_class_map_cloud_negative_positive_middle_and_new_clients(self):
        classes=rows('class_map.csv')
        self.assertEqual(next(r['hybrid_applies']for r in classes if r['model_class']=='cloud'),'False')
        self.assertEqual(next(r['hybrid_applies']for r in classes if r['model_class']=='middle dense'),'True')
        costs=rows('middle_cost.csv')
        self.assertEqual({r['client']for r in costs},{'m5max64','m5max','ultra256','ultra512'})
        for r in costs:
            self.assertNotIn('rtx5090',r['server']);self.assertIn(r['model'],('qwen','glm'))
            if r['hybrid_person_month'] and r['client_basis']=='new':self.assertGreater(float(r['client_capital_month']),0)
            if r['client_basis']=='owned':self.assertEqual(float(r['client_capital_month']),0)

    # Primary feasible hybrids contain no server generation; real refused and valid rows both exist.
    def test_prefill_only_published_negative_overflow_positive_feasible(self):
        rr=rows('middle_cost.csv')+rows('fleet_variants.csv')
        valid=[r for r in rr if r['hybrid_status']=='feasible_prefill_only']
        refused=[r for r in rr if r['hybrid_status']=='client_decode_capacity_shortfall']
        self.assertTrue(valid);self.assertTrue(refused)
        for r in valid:self.assertEqual(float(r['server_decode_overflow_day']or 0),0)
        for r in refused:self.assertFalse(r['hybrid_person_month'])

    # The common large-model component is identical and explicitly a floor, not free80% or a cloud API.
    def test_mixed_common_identical_positive_delta_cancellation_negative_free_cloud(self):
        rr=rows('mixed_scheme.csv');self.assertEqual({r['share']for r in rr},{'0.2','0.5'})
        for r in rr:
            self.assertIn('internal large model',r['contour']);self.assertIn('FLOOR',r['large_cost_basis'])
            self.assertEqual(r['hybrid_common_large_person_month'],r['own_common_large_person_month'])
            self.assertGreater(float(r['common_large_person_month']),0)
            if r['hybrid_person_month'] and r['own_person_month']:
                self.assertAlmostEqual(float(r['difference_person_month']),float(r['hybrid_person_month'])-float(r['own_person_month']),places=8)

    # Every GLM timing/crossing remains conditional and x2 prefilling is not hidden.
    def test_glm_never_promoted_to_measurement_positive_two_sensitivities(self):
        rr=[r for r in rows('crossings.csv')if r['model']=='glm']
        self.assertTrue(rr);self.assertEqual({r['glm_prefill_slowdown']for r in rr},{'1','2'})
        for r in rr:self.assertIn('UNMEASURED',r['rate_basis']);self.assertIn('extrapolated',r['rate_basis'])
        pending=rows('pending_inputs.csv')
        self.assertGreaterEqual(len(pending),7)
        for r in pending:self.assertIn('pending',r['status'])

    # A words-ready sentence missing its link fails the same parser used on every exported sentence.
    def test_words_ready_refuses_missing_link_positive_all_conditions(self):
        rr=rows('paper/words_ready.csv');self.assertTrue(rr)
        for r in rr:
            self.assertTrue(conditions(r['sentence']),r['sentence'])
            self.assertIn({'m5max64':'64GB','m5max':'128GB','ultra256':'256GB','ultra512':'512GB'}[r['client']],r['sentence'])
        sample=rr[0]['sentence'];self.assertFalse(conditions(sample.replace(rr[0]['link'],'link omitted')))

    # Fixed-fleet storage/latency shortfalls are explicit; a proxy-admitted case is also priced.
    def test_small_fleet_shortfall_positive_qualified_proxy(self):
        rr=rows('fleet_variants.csv')
        self.assertTrue(any(r['hybrid_status']=='storage_shortfall' and not r['hybrid_person_month']for r in rr))
        valid=[r for r in rr if r['hybrid_person_month']]
        self.assertTrue(valid)
        for r in valid:
            self.assertIn('UNMEASURED',r['proxy_basis'])
            if r['actual_mean_queue_s']:self.assertLessEqual(float(r['actual_mean_queue_s']),float(r['charged_mean_queue_s'])+1e-10)
            self.assertLessEqual(float(r['hybrid_service_utilization']),.7+1e-10)

    # A reported affordability threshold is for hardware capacity only, never qualified service.
    def test_cloud_affordability_pending_positive_weight_floor(self):
        rr=rows('cloud_reference.csv')
        for r in rr:
            self.assertTrue(r['service_cost_pending']=='True');self.assertIn('CAPACITY COST ONLY',r['basis'])
            if r['retention_basis']=='weights_only_floor':self.assertEqual(int(r['nodes']),2)
        self.assertEqual({r['billing']for r in rows('cloud_affordability.csv')},{'bought','rented'})

    # A wrong quoted cell fails the same audit that accepts all real quote coordinates.
    def test_quotes_refuse_changed_cell_positive_coordinate_audit(self):
        from run26 import finish
        from unittest.mock import patch
        self.assertGreater(finish.verify_quotes(),100)
        read=finish.read
        def wrong(name):
            rr=read(name)
            if name=='quotes.csv':rr=[dict(r) for r in rr];rr[0]['value']='invented'
            return rr
        with patch.object(finish,'read',side_effect=wrong),self.assertRaisesRegex(AssertionError,'quote coordinate mismatch'):
            finish.verify_quotes()
        for r in rows('crossings.csv'):self.assertEqual(r['scan_max'],'500')

    # Finite owned-Qwen prices reproduce independent accepted run24 cached curves;
    # this does not qualify GLM or new off-GPU queue proxies.
    def test_qwen_cost_refuses_changed_numeric_positive_accepted_cache(self):
        doc=json.loads(gzip.decompress((export.ROOT/'calc/run24/data/cost-curves.json.gz').read_bytes()))
        keys=('profile','scope_tier','transport','load','share','client','server','billing')
        index={tuple(str(r[k]) for k in keys):r for r in doc['curves']}
        def accepted(r):
            enriched=dict(r,scope_tier='measured_ladder',transport='bf16')
            expected=index[tuple(enriched[k] for k in keys)]['prices'][int(r['team'])-1]
            return math.isclose(float(r['hybrid_person_month']),expected,rel_tol=1e-13,abs_tol=1e-10)
        valid=[r for r in rows('middle_cost.csv')if r['model']=='qwen'and r['client_basis']=='owned'and r['hybrid_person_month']]
        self.assertGreater(len(valid),800);self.assertTrue(all(accepted(r) for r in valid))
        changed=dict(valid[0],hybrid_person_month=str(float(valid[0]['hybrid_person_month'])+1))
        self.assertFalse(accepted(changed))

    # Ratios in mixed rows must name the middle segment; the common total is a floor.
    def test_mixed_ratio_refuses_total_scope_positive_middle_scope(self):
        from run26 import finish
        from unittest.mock import patch
        self.assertGreater(finish.verify_mixed(),1000)
        original=finish.read
        def wrong(name):
            rr=original(name)
            return [dict(r,middle_ratio_basis='total internal cost') for r in rr] if name=='mixed_scheme.csv'else rr
        with patch.object(finish,'read',side_effect=wrong),self.assertRaisesRegex(AssertionError,'mixed ratio scope'):
            finish.verify_mixed()

if __name__=='__main__':unittest.main()
