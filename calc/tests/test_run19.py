"""Run19 node admission, routing, priced fleets and export refusal witnesses."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc import measurements_r19 as r19,measurements_r18 as r18,measurements_r16 as r16
from hybridcalc.inputs import InputGap,ROOT


class NodeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.node=r19.Node('rtx5090');cls.pro=r19.Node('pro6000')

    # Each resident has its own recurrent state; the fourth100k session cannot
    # be made resident by pooling tokens while dropping the per-session state.
    def test_resident_overflow_must_swap_or_refuse(self):
        p=self.node
        self.assertEqual(p.session_bytes(100000),3638493184)
        self.assertEqual(p.resident_slots(100000),3)
        self.assertEqual(p.placement(3,100000,'resident'),dict(resident=3,swapped=0))
        for tier in ('RAM','NVMe'):self.assertEqual(p.placement(4,100000,tier),dict(resident=3,swapped=1))
        with self.assertRaisesRegex(InputGap,'must swap or refuse'):p.placement(4,100000,'resident')
        with self.assertRaisesRegex(InputGap,'unknown residency'):p.placement(1,100000,'disk_magic')
        with self.assertRaisesRegex(InputGap,'integer'):p.placement(1.5,100000,'RAM')

    # The physical estimate does not authorize a configured262145 session or
    # rate extrapolation beyond249k; prefix+delta+output all consume capacity.
    def test_capacity_estimate_cannot_extend_configured_or_measured_limits(self):
        p=self.node;self.assertGreater(p.physical_token_limit,368000)
        p.admit(262144);p.admit(260000,2000,144)
        for d,n,o in ((262145,0,0),(260000,2000,145)):
            with self.assertRaisesRegex(InputGap,'one session exceeds'):p.admit(d,n,o)
        self.assertGreater(p.rate(249000,512),0)
        with self.assertRaisesRegex(InputGap,'unmeasured node depth'):p.rate(250000,512)
        with self.assertRaisesRegex(InputGap,'unmeasured node delta'):p.rate(100000,10001)
        cfg=r19.config();cfg['nodes']['rtx5090']['session_budget_bytes']=20e9
        with self.assertRaisesRegex(InputGap,'cannot be enlarged'):r19.Node('rtx5090',cfg)

    # The raw client-kit path is reused explicitly, never promoted to a fresh
    # hybrid-node benchmark or a flat depth-independent server rate.
    def test_node_rates_require_hybrid_binary_assumption_and_raw_delta_surface(self):
        p=self.node
        row=next(r for r in p.records if r['kind']=='turn' and r['level']==100000 and r['delta']==2000)
        self.assertEqual(p.rate(100000,2000),row['prompt_n']*1000/row['prompt_ms'])
        self.assertNotEqual(p.rate(100000,2000),p.rate(100000,10000))
        cfg=r19.config();cfg['nodes']['rtx5090']['rate_basis']='fresh measured hybrid node'
        with self.assertRaisesRegex(InputGap,'portability assumption'):r19.Node('rtx5090',cfg)

    # Complete measured save/restore pairs are admitted; missing, failed or
    # mismatched pairs refuse before a swap cost can become a zero default.
    def test_swap_evidence_rejects_missing_failed_and_mismatched_pairs(self):
        records=self.node.records
        for mode in ('missing','failed','mismatch'):
            rows=copy.deepcopy(records);row=next(r for r in rows if r['kind']=='slot_restore')
            if mode=='missing':rows.remove(row)
            elif mode=='failed':row['n_restored']=0
            else:row['bytes']+=1
            with self.subTest(mode=mode),patch.object(r18,'Client',return_value=SimpleNamespace(records=rows)),self.assertRaises(InputGap):r19.Node('rtx5090')
        self.assertEqual(len(self.node.slot_points['slot_restore']),6)

    # Measured round-trip costs are charged once, with a max bandwidth floor
    # rather than adding file IO twice. Unmeasured restoration cannot be free.
    def test_swap_rejects_free_reload_double_count_and_depth_extrapolation(self):
        p=self.node
        self.assertAlmostEqual(p.swap_seconds(100000,'NVMe'),(.801337+.593491))
        self.assertAlmostEqual(p.swap_seconds(100000,'RAM'),(.801337+.593491))
        self.assertEqual(p.swap_seconds(100000,'resident'),0)
        self.assertGreater(p.swap_seconds(200000,'NVMe'),p.swap_seconds(100000,'NVMe'))
        with self.assertRaisesRegex(InputGap,'beyond measured'):p.swap_seconds(250000,'RAM')
        slow=copy.copy(p);slow.cfg=copy.deepcopy(p.cfg);slow.cfg['tiers']['NVMe']['bandwidth_bytes_s']=1e9
        self.assertAlmostEqual(slow.swap_seconds(100000,'NVMe'),2*p.session_bytes(100000)/1e9)

    # A positive host allowance is distinct from a sold-out card listing;
    # the observed rental label and evidence bytes cannot be fabricated.
    def test_prices_reject_card_only_box_market_relabelling_and_bad_digest(self):
        cfg=r19.config();self.assertEqual(r19.checked_price(cfg)['sources'][0]['price_usd'],1999.99)
        for key,value in (('host_usd',0),('card_usd',999),('price_basis','available box quote')):
            bad=copy.deepcopy(cfg);bad['office'][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(InputGap,'separate host allowance'):r19.checked_price(bad)
        bad=copy.deepcopy(cfg);bad['rental']['price_basis']='current market rates'
        with self.assertRaisesRegex(InputGap,'cannot be relabelled'):r19.checked_price(bad)
        bad=copy.deepcopy(cfg);bad['price_evidence']['sha256']='0'*64
        with self.assertRaisesRegex(InputGap,'byte identity mismatch'):r19.checked_price(bad)

    def fake(self,gpu=.0001):
        def routed(link,tier,p):
            return dict(offload_share=1,offload_calls=1,calls=1,gpu_s_call=gpu,migration_s_call=0,wire_bytes_call=1,pending_s_offload=0,prefill_wait_s_call=1,local_prefill_s_call=2)
        return SimpleNamespace(node=self.node,routed=routed)

    # Fragmented spare VRAM cannot be pooled across boxes. With no host
    # capacity every retained249k session needs its own physical5090 replica.
    def test_fleet_rejects_pooled_vram_fragmentation_and_free_retention(self):
        cfg=r19.config();p=self.fake();link={}
        resident=r19.fleet(p,link,'resident',5,2500,8,.7,4,cfg)
        self.assertEqual(resident['boxes'],20)
        cfg['tiers']['RAM']['capacity_bytes']=1
        self.assertEqual(r19.fleet(p,link,'RAM',5,2500,8,.7,4,cfg)['boxes'],20)
        cfg=r19.config();shared=r19.fleet(p,link,'RAM',5,2500,8,.7,4,cfg)
        self.assertLess(shared['boxes'],20)
        self.assertLessEqual(shared['host_bytes'],shared['boxes']*cfg['tiers']['RAM']['capacity_bytes'])

    # A residency change may change routing. The chosen integer fleet must
    # still satisfy its recomputed GPU demand; invalid load is not spare room.
    def test_fleet_rechecks_routed_demand_and_refuses_impossible_load(self):
        f=r19.fleet(self.fake(100),{},'NVMe',50,2500,8,.7,4,r19.config())
        self.assertGreater(f['boxes'],1)
        self.assertGreaterEqual(f['boxes']*8*3600*.7,50*2500*f['gpu_s_call'])
        for load in (0,1.1):
            with self.subTest(load=load),self.assertRaises(InputGap):r19.fleet(self.fake(),{},'RAM',5,2500,8,load,4,r19.config())

    # Expected pending local work can veto an initially faster remote call;
    # rejected calls leave no transfer or billed server work behind.
    def test_routing_rejects_ignored_catchup_and_bills_only_selected_work(self):
        p=object.__new__(r19.Prepared)
        p.own=[1,100];p.prefill=[.1,200];p.shadow=[1,200];p.output=[.1,.1]
        p.wire=[1,1];p.imports=[0,0];p.swap={'resident':[0,0],'RAM':[10,10]}
        link=dict(bytes_s=1e9,rtt_s=0)
        dead=p.routed(link,'resident',0);self.assertEqual(dead['offload_calls'],0)
        self.assertEqual(dead['gpu_s_call'],0);self.assertEqual(dead['wire_bytes_call'],0)
        p.shadow=[.1,.1];alive=p.routed(link,'resident',0);self.assertGreater(alive['offload_calls'],0)
        with self.assertRaisesRegex(InputGap,'invalid spill'):p.routed(link,'resident',.1)
        with self.assertRaisesRegex(InputGap,'invalid spill'):p.routed(link,'RAM',1.1)


class Run19Outputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from hybridcalc.engine import run
        cls.result=run('prefill-nodes-r19')
        cls.tables={t['id']:t['rows'] for t in cls.result['tables']}

    # Bandwidth must retain byte/bit units despite its _s suffix. Actual time
    # and call-cost columns are positive controls against a blanket relabel.
    def test_export_units_reject_bandwidth_labelled_as_time(self):
        columns={t['id']:t['columns'] for t in self.result['tables']}
        self.assertEqual(columns['node_link_profiles']['bytes_s'],'B/s')
        self.assertEqual(columns['node_link_threshold']['break_even_downstream_mb_s'],'MB/s (decimal)')
        self.assertEqual(columns['node_link_threshold']['break_even_downstream_mbit_s'],'Mbit/s')
        self.assertEqual(columns['node_link_threshold']['node_prefill_s'],'s')
        self.assertEqual(columns['rented_prefill_node']['usd_per_1000_calls'],'USD/1000 conditional calls')

    # A fully covered small workload can use the cost table as its complete
    # mix. Adding one excluded session must revoke that full-workload claim.
    def test_full_mix_claim_refuses_filtered_calls_with_complete_positive_control(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables import Context
        s,i=load('paper-tables-r17')
        for excluded in (False,True):
            def context(spec,inputs):
                c=Context(spec,inputs)
                calls=[(32000,2343,128,0)]+([(260000,2343,128,0)] if excluded else [])
                c.valid=c.label('test.r19.fixed_mix',calls)
                return c
            with patch('hybridcalc.paper_tables.Context',side_effect=context):
                result=r19.calculate(s,i)
            row=next(t for t in result['tables'] if t['id']=='workload_coverage')['rows'][0]
            self.assertEqual(row['full_workload_supported'],not excluded)
            if excluded:self.assertIn('alarm',row['full_workload_office_cost'])
            else:self.assertEqual(row['full_workload_office_cost'],'see office_node_economics; complete fitted mix')

    # Conditional quotes name the whole unsupported remainder. All economics
    # alternatives share10885 original indices and the same52500-call month.
    def test_same_mix_rejects_silent_full_workload_and_api_cache_restarts(self):
        r=self.tables['workload_coverage'][0]
        self.assertEqual((r['original_calls'],r['common_calls']),(39904,10885))
        self.assertFalse(r['full_workload_supported']);self.assertIn('alarm',r['full_workload_office_cost'])
        self.assertEqual(r['normalized_calls_person_month'],52500)
        from hybridcalc.engine import load
        from hybridcalc.paper_tables import Context,api_vector
        s,i=load('paper-tables-r17');c=Context(s,i);calls=c.g.resolve(c.valid).value
        vector=api_vector(calls,{k:i.get('prices.apis.qwen_cheap.'+k) for k in ('cache_read','cache_write','output')},116)
        indices=[j for j,(d,n,o,t) in enumerate(calls) if d+n+o<=249000 and 512<=n<=10000]
        want=sum(vector[j] for j in indices)/len(indices)*52500
        values={r['api_cheapest_usd_person_month'] for r in self.tables['office_node_economics']}
        self.assertEqual(values,{want})
        from hybridcalc.engine import run
        with self.assertRaisesRegex(InputGap,'run19.workload'):run('prefill-nodes-r19',['workload.sample_calls=0'])

    # Mac import stays on the Mac law, independently of a CUDA client's fit.
    # Nonpositive budgets remain named alarms rather than finite zero rates.
    def test_thresholds_reject_cuda_import_laundering_and_zero_never_rates(self):
        rows=self.tables['node_link_threshold'];self.assertEqual(len(rows),540)
        finite=[r for r in rows if r['threshold_status']=='finite'];never=[r for r in rows if r['threshold_status']!='finite']
        self.assertTrue(finite);self.assertTrue(never)
        for r in rows:
            self.assertAlmostEqual(r['client_import_s'],r16.ClientImport().at_depth(r['delta'],r['depth']))
            if r['threshold_status']=='finite':
                self.assertGreater(r['budget_s'],0)
                self.assertAlmostEqual(r['wire_bytes']/r['budget_s']/1e6,r['break_even_downstream_mb_s'])
                self.assertEqual(8*r['break_even_downstream_mb_s'],r['break_even_downstream_mbit_s'])
            else:self.assertIn('alarm',r['break_even_downstream_mb_s'])
        with patch.object(r18,'cuda_import',side_effect=AssertionError('CUDA law on Mac')):
            from hybridcalc.engine import load
            from hybridcalc.paper_tables import Context
            s,i=load('paper-tables-r17')
            self.assertTrue(r19.thresholds(Context(s,i),[r19.Node('rtx5090')],[dict(key='control',bytes_s=125e6,rtt_s=.001)]))

    # Office rows reserve four sessions per person, include a host allowance,
    # and count whole boxes; per-call work cannot waive retained-session limits.
    def test_office_rejects_fractional_boxes_and_card_only_prices(self):
        rows=self.tables['office_node_economics'];self.assertEqual({r['team'] for r in rows},{5,50,500})
        for r in rows:
            self.assertEqual(r['boxes'],int(r['boxes']))
            self.assertEqual(r['retained_sessions'],r['team']*4)
            if r['node']=='rtx5090':
                self.assertEqual(r['box_capex_usd'],3499.99)
                self.assertAlmostEqual(r['box_month_usd'],3499.99*.8/48+.75*1.3*730*.5*.15+3499.99*.02/12)
            self.assertEqual(r['host_storage_month_usd'],0) # No second rental charge for already-owned cache.
            if r['boxes']:
                if r['tier']=='resident':self.assertGreaterEqual(r['boxes']*r['resident_slots_box'],r['retained_sessions'])
                self.assertGreaterEqual(r['boxes']*8*3600*.7,r['team']*2500*r['gpu_s_call'])
            self.assertAlmostEqual(r['usd_person_month']/52500*1000,r['usd_per_1000_calls'])

    # Observed offer endpoints and complete calendar rental costs stay distinct
    # from utilization-priced work; every selected byte receives egress cost.
    def test_rental_rejects_market_rates_free_egress_and_idle_cost_erasure(self):
        rows=self.tables['rented_prefill_node'];self.assertEqual(len(rows),48)
        self.assertEqual({r['hourly_usd'] for r in rows},{.448,.522})
        self.assertEqual({r['link'] for r in rows},{'measured_wifi_wan','measured_5g_wan','engine_wan'})
        for r in rows:
            self.assertIn('not market rates',r['basis'])
            self.assertAlmostEqual(r['egress_usd_month'],r['wire_bytes_call']*52500/1e12*5)
            self.assertAlmostEqual(r['usd_person_month'],r['billed_hours_month']*r['hourly_usd']+r['storage_usd_month']+r['egress_usd_month'])
            if r['billing']=='warm_calendar_node':self.assertEqual(r['billed_hours_month'],r['boxes']*730)


class Run19Custody(unittest.TestCase):
    # Frozen R18 remains bound to its producer head when R19 grows the engine.
    # A changed old byte and a missing/forged quote must be detected in memory.
    def test_exports_reject_historical_corruption_and_quote_omission(self):
        import r19_audit as audit
        import r18_audit as previous
        self.assertEqual(audit.frozen(),917);self.assertEqual(previous.verify_tables(),9)
        self.assertEqual(audit.verify_tables(),13)
        records=audit.read(audit.LEDGER);self.assertGreater(audit.verify_quotes(records),10000)
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(records[1:])
        bad=copy.deepcopy(records);bad[0]['engine_key']+=' forged'
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(bad)
        real=Path.read_bytes;target=ROOT/'calc/out/run18/gpu_link_threshold.csv'
        def damaged(p):return b'bounded old-file corruption' if p==target else real(p)
        with patch.object(Path,'read_bytes',damaged),self.assertRaisesRegex(AssertionError,'changed historical bytes'):audit.frozen()
        with patch.object(audit,'generator_identity',return_value={}),self.assertRaisesRegex(AssertionError,'stale generator'):audit.verify_tables()


if __name__=='__main__':unittest.main()
