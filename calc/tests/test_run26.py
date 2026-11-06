"""Named controls for the closed-contour calculation, not runtime certification."""
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run26 import model as m
from run23 import engine as r23
from hybridcalc.inputs import InputGap


class Run26Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=r23.context()

    # The cloud FP8 example is rejected; a fitting middle model is still admitted.
    def test_cloud_class_hybrid_refuses_not_fitting_client_positive_middle(self):
        with self.assertRaisesRegex(InputGap,'model does not fit client'):
            m.hybrid_admission('cloud',2.4e12,512e9)
        self.assertTrue(m.hybrid_admission('middle',18.97e9,64e9,8e9))
        with self.assertRaisesRegex(InputGap,'model does not fit client'):
            m.hybrid_admission('middle',181.4e9,128e9)

    # Finite paid costs cannot conceal generation on a prefill-only server.
    def test_prefill_only_refuses_decode_overflow_positive_zero_overflow(self):
        r=m.prefill_only(dict(person_month=20,server_decode_overflow_day=1))
        self.assertFalse(r['feasible']);self.assertIsNone(r['person_month'])
        self.assertEqual(r['status'],'client_decode_capacity_shortfall')
        self.assertTrue(m.prefill_only(dict(person_month=20,server_decode_overflow_day=0))['feasible'])

    # Refusals retain their specific storage cause rather than becoming a free row.
    def test_storage_refusal_not_erased_positive_feasible(self):
        self.assertEqual(m.prefill_only(dict(person_month='',status='storage_shortfall'))['status'],'storage_shortfall')
        self.assertEqual(m.prefill_only(dict(person_month=20))['person_month'],20)

    # Equal-sized uniform experts solve both source parameter constraints; invalid ones refuse.
    def test_expert_partition_refuses_impossible_active_positive_reconstruction(self):
        a,r=m.expert_partition(320e9,18e9,288,8)
        self.assertAlmostEqual(a+r,320e9,delta=1e-3)
        self.assertAlmostEqual(a+r*8/288,18e9,delta=1e-3)
        with self.assertRaisesRegex(InputGap,'inconsistent'):
            m.expert_partition(320e9,1e9,288,8)

    # Per-session KV is never shared; weight reads can be amortized only through union.
    def test_expert_batch_cannot_share_kv_positive_weight_amortization(self):
        args=(328e9,320e9,18e9,288,8)
        low=m.expert_traffic(32,16000,*args,11264,152633344)
        high=m.expert_traffic(32,64000,*args,11264,152633344)
        self.assertAlmostEqual(high-low,32*11264*48000,delta=.01)
        one=m.expert_traffic(1,16000,*args,11264,152633344)
        self.assertLess(low,one*32)

    # Official config supplies experts and layer counts; KV is explicitly a derived layout.
    def test_architecture_derived_layout_positive_source_counts(self):
        a=m.architecture()
        self.assertEqual((a['experts'],a['topk'],a['layers'],a['full_layers'],a['linear_layers']),(288,8,45,11,34))
        self.assertEqual(a['client_kv'],5984);self.assertEqual(a['server_kv'],11264)
        self.assertEqual(a['state'],152633344);self.assertEqual(a['wire_state'],76316672)

    # The sourced configuration is not evidence of GLM timing; captured files remain hash-bound.
    def test_captured_source_hashes_positive_real_files(self):
        rows=json.loads((m.DATA/'data/source-index.json').read_text())
        self.assertGreaterEqual(len(rows),5)
        for r in rows:
            self.assertEqual(hashlib.sha256((m.DATA/'data'/r['path']).read_bytes()).hexdigest(),r['sha256'])
        prices=json.loads((m.DATA/'data/studio-price-provenance.json').read_text())
        self.assertTrue(any(r.get('reported_list_512_usd')==22299 and r.get('sha256_fetched_page') for r in prices))

    # Two-die compute extrapolation is exactly stated, not an inherited Studio57min guess.
    def test_ultra_extrapolation_positive_max_anchor_and_memory_negative(self):
        u=m.Ultra();d,n=64000,2000
        expected=u.mac.prefill(d,n)*m.glm_flops(d+n/2)/m.qwen_flops(d+n/2)/2
        self.assertAlmostEqual(u.prefill(d,n),expected)
        self.assertGreater(u.decode(d,1),0)
        with self.assertRaisesRegex(InputGap,'does not fit client'):
            m.Ultra(128e9).slots(d)
        self.assertGreaterEqual(m.Ultra(512e9).slots(d),u.slots(d))

    # Unknown GLM prefill is varied on both alternatives; no measured point is invented.
    def test_glm_prefill_unmeasured_sensitivity_positive_factor_two(self):
        from run23.economics import Server
        a=m.GlmServer(Server('b300_fp8'),1);b=m.GlmServer(Server('b300_fp8'),2)
        self.assertAlmostEqual(b.cached(64000,2000),2*a.cached(64000,2000))
        with self.assertRaisesRegex(InputGap,'declared unmeasured'):
            m.GlmServer(Server('b300_fp8'),0)
        dec=a.decode(164000,10**6)
        self.assertEqual(dec['batch'],a.slots(164000))
        self.assertIn('UNMEASURED',dec['basis'])

    # Owned/new differ only in client capital; a bad ownership basis is rejected.
    def test_purchase_capital_positive_owned_zero_negative_bad_basis(self):
        self.assertEqual(m.capital(22299,self.c.inputs,'owned'),0)
        self.assertGreater(m.capital(22299,self.c.inputs,'new'),0)
        with self.assertRaisesRegex(InputGap,'owned or new'):
            m.capital(22299,self.c.inputs,'shared')

    # The common large model is paid identically, so no outside80% or free common service appears.
    def test_mixed_common_cost_cancels_positive_equal_common_negative_invalid(self):
        r=m.mixed(20,50,674)
        self.assertEqual(r['hybrid_common_large_person_month'],r['own_common_large_person_month'])
        self.assertEqual(r['difference_person_month'],-30)
        self.assertEqual(r['total_hybrid_floor_person_month'],694)
        with self.assertRaisesRegex(InputGap,'invalid common'):
            m.mixed(20,50,-1)

    # Weight-capacity floor needs more than one8-GPU node; it is not a throughput result.
    def test_cloud_capacity_not_one_node_positive_pending_service(self):
        r=m.cloud_capacity(50,self.c.inputs,'bought')
        self.assertEqual(r['nodes'],2);self.assertTrue(r['service_cost_pending'])
        self.assertTrue(r['storage_cost_pending'])
        self.assertEqual(r['hbm_node_bytes'],2.304e12)
        crowded=m.cloud_capacity(500,self.c.inputs,'bought',retention='all_resident_sessions')
        self.assertGreater(crowded['nodes'],2)
        with self.assertRaisesRegex(InputGap,'unknown retention'):
            m.cloud_capacity(50,self.c.inputs,'bought',retention='free_infinite_hbm')

    # A point win must not be reported as a sustained crossing through500.
    def test_crossing_refuses_point_win_positive_sustained_suffix(self):
        from run25.engine import compare
        self.assertEqual(compare([1,3],[2,2])['sustained_from'],'')
        self.assertEqual(compare([3,1],[2,2])['sustained_from'],2)

    # Four two-GPU replicas still pay for the full8-GPU chassis; overload cannot be free.
    def test_glm_full_node_price_four_replicas_positive_negative_client_overload(self):
        from run23.economics import Server
        from hybridcalc import server_economics_r20 as se
        cfg=se.config();cfg['reservation_depth']=249000
        q=Server('b300_fp8');g=m.GlmEconomics(self.c,[(64000,2000,500,8)],m.GlmServer(q),cfg)
        unit,count=g.units['glm_two_b300','bought']
        self.assertEqual(count,4);self.assertEqual(unit,se.unit_month(q,self.c.inputs,'bought')[0])
        self.assertTrue(g.hybrid(50,200,'ultra256','owned','bought')['feasible'])
        r=g.hybrid(50,1e9,'ultra256','owned','bought')
        self.assertFalse(r['feasible']);self.assertIsNone(r['person_month'])
        self.assertEqual(r['status'],'client_decode_capacity_shortfall')

if __name__=='__main__':unittest.main()
