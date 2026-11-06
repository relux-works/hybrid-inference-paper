"""Run20 forbidden outcomes paired with valid measured or analytic controls."""
import copy
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc import server_economics_r20 as s,measurements_r20 as r
from hybridcalc.inputs import InputGap,ROOT


class AdmissionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=json.loads(s.SNAPSHOT.read_text())['data']['endpoints'];cls.chutes=next(x for x in cls.rows if x['tag']=='chutes/fp8')

    # Chutes is admitted at262144, but its declared cap excludes the1M section.
    def test_context_admission_refuses_short_providers_with_boundary_control(self):
        self.assertEqual(s.admission(self.chutes,262144),[])
        self.assertIn('context_below_1000000',s.admission(self.chutes,1000000))
        row=copy.deepcopy(self.chutes);row['context_length']=262143
        self.assertIn('context_below_262144',s.admission(row,262144))

    # Declared caching plus a cache-read price are required; explicit writes
    # can declare caching even when implicit caching is false (Alibaba case).
    def test_cache_admission_refuses_undeclared_and_unpriced_cache(self):
        row=copy.deepcopy(self.chutes);row['supports_implicit_caching']=False
        self.assertIn('caching_not_declared',s.admission(row,262144))
        row['pricing']['input_cache_write']='0.00000005';self.assertEqual(s.admission(row,262144),[])
        del row['pricing']['input_cache_read'];self.assertIn('cache_read_price_missing',s.admission(row,262144))

    # Every recorded availability window binds; missing data is disclosed,
    # not fabricated as a100% observation.95% is an inclusive boundary.
    def test_availability_refuses_one_bad_window_and_accepts_95(self):
        row=copy.deepcopy(self.chutes);row['uptime_last_1d']=95;self.assertEqual(s.admission(row,262144),[])
        row['uptime_last_5m']=94.999;self.assertIn('recorded_availability_below_95_or_invalid',s.admission(row,262144))
        for k in ('uptime_last_5m','uptime_last_30m','uptime_last_1d'):row[k]=None
        self.assertEqual(s.admission(row,262144),[])

    # A zero-hit provider uses billed misses; default98.1% is not confused
    # with a100% hit promise.Explicit cache-write prices bind on misses.
    def test_effective_price_rejects_free_cache_misses_and_bad_fraction(self):
        row=copy.deepcopy(self.chutes);row['pricing']['input_cache_write']='0.000000078'
        means=(980,20,30);p=s.api_cost(row,means,.981)
        self.assertAlmostEqual(p,1000*(.981*3.9e-9+.019*78e-9)+30*1.25e-6)
        self.assertGreater(p,s.api_cost(row,means,1))
        self.assertAlmostEqual(s.api_cost(row,means,0),1000*78e-9+30*1.25e-6)
        for h in (-.01,1.01,float('nan')):
            with self.subTest(h=h),self.assertRaises(InputGap):s.api_cost(row,means,h)

    # Provider tests can update data alone; wrong model, duplicate coordinates,
    # missing provenance or cached>input refuses rather than silently defaulting.
    def test_cache_data_interface_refuses_wrong_model_duplicate_and_invalid_tokens(self):
        row=dict(tag='chutes/fp8',profile='main',model='qwen/qwen3.8-27b',observed_at='2026-11-03',source='planned-test-fixture',input_tokens=100,cached_tokens=90)
        known={'chutes/fp8'}
        self.assertEqual(s.cache_measurements({'measurements':[row]},known),{('chutes/fp8','main'):.9})
        for k,v in (('cached_tokens',101),('input_tokens',0),('model','wrong'),('source',''),('profile','wrong'),('tag','unknown')):
            bad=dict(row,**{k:v})
            with self.subTest(k=k),self.assertRaises(InputGap):s.cache_measurements({'measurements':[bad]},known)
        with self.assertRaisesRegex(InputGap,'duplicate'):s.cache_measurements({'measurements':[row,row]},known)

    # Provider observations change the public effective-price output through
    # data alone; the default remains explicitly unverified for other providers.
    def test_provider_cache_data_updates_effective_price_without_code_change(self):
        cfg=s.config();calls=[(100000,2343,512,0)]
        before,_=s.api_baselines(calls,cfg)
        cfg['provider_cache_hits']['measurements']=[dict(tag='chutes/fp8',profile='main',model='qwen/qwen3.8-27b',observed_at='2026-11-03',source='fixture-token-counts',input_tokens=100,cached_tokens=0)]
        after,_=s.api_baselines(calls,cfg)
        a=next(x for x in before if x['profile']=='main'and x['tag']=='chutes/fp8');b=next(x for x in after if x['profile']=='main'and x['tag']=='chutes/fp8')
        self.assertGreater(b['effective_usd_per_1000_calls'],a['effective_usd_per_1000_calls'])
        self.assertEqual(b['cache_basis'],'measured provider token fraction')

    # A source-labelled default cannot drift away from the archived owner log.
    def test_owner_cache_default_refuses_unproven_fraction(self):
        cfg=s.config();self.assertEqual(cfg['owner_cache_fraction'],.981)
        s.api_baselines([(100000,2343,512,0)],cfg)
        cfg['owner_cache_fraction']=.99
        with self.assertRaisesRegex(InputGap,'NOTES evidence'):s.api_baselines([(100000,2343,512,0)],cfg)

    # Ranking uses effective same-mix cost, never minimum input-token tariff.
    def test_provider_ranking_excludes_alibaba_and_keeps_chutes(self):
        rows,chosen=s.api_baselines([(100000,2343,512,0)],s.config())
        self.assertEqual(chosen['main']['cheapest_tag'],'chutes/fp8')
        self.assertEqual(chosen['million']['cheapest_tag'],'phala')
        self.assertFalse(next(x for x in rows if x['profile']=='million'and x['tag']=='alibaba')['admitted'])
        self.assertIn(chosen['main']['median_tag'],{x['tag']for x in rows if x['profile']=='main'and x['admitted']})
        self.assertEqual(chosen['main']['count'],17)


class ServerContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cfg=s.config();cls.b=s.Server('b300_fp8');cls.fp8=s.Server('b300_fp8_kv');cls.pro=s.Server('pro6000_fp8')

    # Cached useful-delta TTFT matches raw rows; processed-token counts cannot
    # turn a2k request into a cheaper2704-token useful-throughput charge.
    def test_vllm_cached_times_reject_processed_token_overcredit_and_depth_extension(self):
        self.assertAlmostEqual(self.b.cached(16384,2000),.17185799597064033)
        self.assertAlmostEqual(self.b.cached(16384,10000),.49651675298810005,places=5)
        self.assertGreater(self.b.cached(249000,2000),self.b.cached(16384,2000))
        with self.assertRaisesRegex(InputGap,'outside measured'):self.b.cached(249001,2343)
        with self.assertRaisesRegex(InputGap,'outside measured'):self.b.cached(16000,10001)
        with self.assertRaisesRegex(InputGap,'outside measured'):self.b.cold(249001)
        self.assertGreater(self.b.cold(249000),0)

    # PRO6000 FP8 KV never started; successful B300 FP8 KV is a nearby control.
    def test_pro6000_failed_fp8_kv_cannot_be_promoted_to_measured(self):
        self.assertGreater(self.fp8.cached(16384,2000),0)
        bad=copy.deepcopy(self.cfg);bad['servers']['pro6000_fp8']['variant']='fp8-kv'
        with self.assertRaisesRegex(InputGap,'did not start'):s.Server('pro6000_fp8',bad)

    # Weight traffic is shared once; KV/state traffic remains per stream.
    # Expected gain is independently computed from the byte equation.
    def test_decode_refuses_depth_independent_gain_and_shared_kv(self):
        p=self.b;d=164000;probe=p.decode(d,32);k=probe['batch'];traffic=d*65536+156893184
        expected=k*(27e9+traffic)/(27e9+k*traffic)
        self.assertAlmostEqual(probe['gain'],expected)
        self.assertGreater(p.decode(16000,32)['gain'],probe['gain'])
        self.assertGreater(probe['gain'],p.decode(1000000,32)['gain'])
        self.assertEqual(p.decode(64000,1)['gain'],1)
        self.assertLess(probe['gain'],k)

    # A session consumes its own KV/state before a batch is admitted; capacity
    # clamps batch32 and rejects a single1M BF16-KV session on PRO6000.
    def test_decode_memory_refuses_pooled_capacity_and_impossible_single_session(self):
        p=self.b;dec=p.decode(1000000,32)
        self.assertEqual(dec['batch'],3)
        self.assertLessEqual(p.weights+p.info['workspace_bytes']+dec['batch']*p.session_bytes(1000000),p.info['memory_bytes'])
        with self.assertRaisesRegex(InputGap,'one complete session'):self.pro.decode(1000000,1)
        self.assertGreater(self.pro.decode(164000,8)['batch'],0)
        for k in (0,1.5):
            with self.assertRaises(InputGap):p.decode(16000,k)

    # Main bridge costs retain measured gather/conversion work once, separate
    # from Mac import.Opting out is explicitly a lower-bound sensitivity.
    def test_bridge_refuses_free_cost_unknown_assumption_and_corrupt_evidence(self):
        p=self.pro;measured=s.bridge_evidence()['pro6000']
        self.assertGreater(measured['seconds_token'],.0005)
        self.assertEqual(p.cached(32000,2343,'measured_envelope'),max(p.cached(32000,2343),2343*measured['seconds_token']))
        self.assertGreater(p.cached(32000,2343,'measured_envelope'),p.cached(32000,2343))
        with self.assertRaisesRegex(InputGap,'unknown bridge'):p.cached(32000,2343,'magic')
        with patch.object(s.hashlib,'sha256')as h:
            h.return_value.hexdigest.return_value='0'*64
            with self.assertRaisesRegex(InputGap,'SHA256'):s.bridge_evidence()

    # Planned measurements update exact capacity-admitted curves without code;
    # wrong engine, unreferenced curve or impossible32-stream deep PRO rows refuse.
    def test_decode_data_interface_refuses_unreferenced_wrong_engine_and_capacity(self):
        servers={'b300_fp8':self.b,'pro6000_fp8':self.pro}
        def rows(key,streams):return [dict(server=key,streams=streams,depth=d,aggregate_tok_s=100/streams+d/10000,engine='vllm',observed_at='2026-11-03',source='fixture')for d in (16000,64000,164000)]
        good=rows('b300_fp8',1)+rows('b300_fp8',8)
        self.assertEqual(len(s.decode_measurements({'measurements':good},servers)),6)
        self.assertEqual(len(s.decode_measurements({'measurements':[good[0],good[3]]},servers)),2)
        self.assertIn('measured aggregate',self.b.decode(64000,8,good)['basis'])
        with self.assertRaisesRegex(InputGap,'cannot extrapolate'):self.b.decode(164001,8,good)
        for bad in (good[3:],[dict(x,engine='llama_cpp')for x in good],rows('pro6000_fp8',1)+rows('pro6000_fp8',32)):
            with self.assertRaises(InputGap):s.decode_measurements({'measurements':bad},servers)


class EconomicsContracts(unittest.TestCase):
    # Filtering must not reset the original116-call cache boundary or omit
    # the preceding generated output from the API input-token budget.
    def test_same_mix_api_refuses_cache_boundary_reset_after_filter(self):
        calls=[(1000,100,10,0),(2000,100,20,0),(3000,100,30,0)]
        self.assertEqual(r.billing_calls(calls,[1,2],2),[(2000,110,20,0),(3000,100,30,0)])
        self.assertEqual(r.billing_calls(calls,[0],2),[(1000,100,10,0)])

    # A team supplies4T simultaneous sessions to the whole fleet, not4T
    # to every GPU. Balanced batches conserve this count on an8-GPU node.
    def test_fleet_batching_refuses_duplicated_team_concurrency(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables import Context
        spec,inputs=load('paper-tables-r17');c=Context(spec,inputs);calls=[(16000,2343,512,1)]
        c.valid=c.label('test.r20.fleet',calls);server=s.Server('b300_fp8')
        econ=r.Economics(c,calls,{'b300_fp8':server},s.config(),{})
        one=econ.fleet_stats(server,3,1,8);two=econ.fleet_stats(server,3,2,8)
        self.assertEqual(one['total_streams'],12);self.assertEqual(two['total_streams'],12)
        self.assertEqual(one['active_gpus'],8);self.assertEqual(two['active_gpus'],12)
        self.assertEqual(one['batch_min'],1)
        self.assertLessEqual(two['fleet_s_call'],one['fleet_s_call'])
        econ.sessions=100
        self.assertEqual(econ.fleet_stats(server,3,2,8)['total_streams'],12)

    # R19 review F1 (rental-basis-missing-coverage): every standalone
    # R20 cost row must carry coverage, normalization and unsupported-full-mix.
    def test_rental_basis_missing_coverage_regression_with_positive_control(self):
        good=r.conditional_scope(10885,39904,10500)
        for expected in ('10885/39904','27.28%','normalized to 10500 calls/person-month','full workload unsupported'):
            self.assertIn(expected,good)
        other=r.conditional_scope(10,20,1000)
        self.assertIn('10/20 (50.00%)',other)
        self.assertIn('full workload covered',r.conditional_scope(20,20,1000))
        for args in ((21,20,1000),(10,20,0),(0,20,1000)):
            with self.assertRaises(InputGap):r.conditional_scope(*args)

    # Integer-box discontinuities invalidate a first-crossing claim.A sustained
    # crossing on a bounded scan and strict equality are exercised separately.
    def test_break_even_refuses_first_lucky_crossing_and_unbounded_prose(self):
        result=r.break_even([9,11,8,7],[10]*4)
        self.assertEqual(result['from_people'],3)
        self.assertEqual(result['scan_max'],4)
        self.assertEqual(r.break_even([9]*4,[10]*4)['from_people'],1)
        self.assertIn('alarm',r.break_even([9,9,10],[10]*3)['from_people'])

    # Storage capacity is per node; a fourth retained session cannot use
    # fragmented free memory pooled across replicas without an actual slot.
    def test_retention_refuses_host_overflow_and_charges_residency_misses(self):
        server=s.Server('pro6000_fp8')
        econ=object.__new__(r.Economics);econ.cfg=s.config();econ.sessions=4
        miss,host=econ.retention(server,1,1,1)
        self.assertGreater(miss,0);self.assertGreater(host,0)
        self.assertEqual(econ.retention(server,1,2,1),(0,0))
        with self.assertRaisesRegex(InputGap,'NVMe capacity'):econ.retention(server,500,1,1)
        boxes=econ.storage_boxes(server,500,1)
        self.assertGreater(boxes,1);econ.retention(server,500,boxes,1)

    # Full new-client amortization, calendar rental billing and all-server
    # overflow are exercised with real engine inputs on one bounded call.
    def test_economics_refuses_free_new_client_calendar_rental_and_overflow(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables import Context
        spec,inputs=load('paper-tables-r17');c=Context(spec,inputs);calls=[(100000,2343,512,5)]
        c.valid=c.label('test.r20.common',calls)
        servers={'pro6000_fp8':s.Server('pro6000_fp8')};econ=r.Economics(c,calls,servers,s.config(),{})
        owned=econ.hybrid('pro6000_fp8',5,100,'m5max64','owned','bought','measured_envelope')
        new=econ.hybrid('pro6000_fp8',5,100,'m5max64','new','bought','measured_envelope')
        self.assertAlmostEqual(new['person_month']-owned['person_month'],5099*.65/48)
        self.assertEqual(owned['device_month'],0)
        self.assertAlmostEqual(s.unit_month(servers['pro6000_fp8'],inputs,'rented')[0],2.2*730)
        large=econ.hybrid('pro6000_fp8',5,2500,'m5max64','owned','bought','measured_envelope')
        self.assertGreater(large['server_decode_overflow_day'],0)
        self.assertGreater(large['decode_overflow_gpu_s_day'],0)
        self.assertGreater(large['boxes'],owned['boxes'])
        refused=econ.hybrid('pro6000_fp8',5,1e6,'m5max64','owned','bought','measured_envelope')
        self.assertIn('alarm',refused['person_month']);self.assertIn('finite team concurrency',str(refused))
        # At a full-prefix rebuild, pending local history is already inside d.
        # Only resident opportunities need the deferred journal catch-up.
        prepared=econ.prepared[('pro6000_fp8','m5max64','measured_envelope')]
        original=r.route;observed=[]
        def capture(own,remote,shadow,output,wire,imports,mode):
            observed.append((shadow,output));return original(own,remote,shadow,output,wire,imports,mode)
        with patch.object(r,'route',side_effect=capture):
            prepared.stats(.25,'office_gigabit');prepared.stats(.75,'office_gigabit')
        self.assertAlmostEqual(observed[0][0][0],prepared.shadow[0]*.75)
        self.assertAlmostEqual(observed[1][0][0],prepared.shadow[0]*.25)
        # Minimal all-server sizing is independently enumerated on this fixture.
        own=econ.own('pro6000_fp8',5,100)
        feasible=[];server=servers['pro6000_fp8'];stat=econ.own_stats(server,20)
        for boxes in range(econ.storage_boxes(server,5,1),own['boxes']+1):
            spill,_=econ.retention(server,5,boxes,1)
            stat=econ.fleet_stats(server,5,boxes,1)
            if 5*100*(stat['fleet_s_call']+spill*econ.cold[server.key]/stat['active_gpus'])<=econ.hours*3600*econ.load:feasible.append(boxes)
        self.assertEqual(own['boxes'],min(feasible))

        for demand,team in ((0,5),(100,0)):
            with self.assertRaises(InputGap):econ.own('pro6000_fp8',team,demand)
        with self.assertRaisesRegex(InputGap,'full new purchase'):econ.hybrid('pro6000_fp8',5,100,'m5max64','free new','bought','measured_envelope')
        with self.assertRaisesRegex(InputGap,'calendar'):s.unit_month(servers['pro6000_fp8'],inputs,'free')

    # Schema labels separate aggregate token rate, bytes and time.
    def test_output_units_refuse_rates_labelled_as_time(self):
        self.assertEqual(r.unit('aggregate_tok_s',1),'token/s')
        self.assertEqual(r.unit('prefill_s',1),'s')
        self.assertEqual(r.unit('kv_bytes_token',1),'B/token')
        self.assertEqual(r.unit('person_month',1),'USD/person-month (open-model component)')
        self.assertEqual(r.unit('unit_month',1),'USD/node-month')


class Run20Outputs(unittest.TestCase):
    # Historical paths and bytes stay exact; no regenerated R13-R19 files.
    def test_historical_exports_reject_changed_bytes_with_positive_control(self):
        import r20_audit as audit
        self.assertEqual(audit.frozen(),931)
        original=audit.history.snapshot_hash
        def corrupt(revision,name):
            return '0'*64
        with patch.object(audit.history,'snapshot_hash',side_effect=corrupt),self.assertRaisesRegex(AssertionError,'changed historical bytes'):audit.frozen()

    # Every grid cell has a coordinate-qualified quote; dropping one fails.
    def test_quote_ledger_refuses_missing_cell_and_stale_generator(self):
        import r20_audit as audit
        rows=audit.read(audit.LEDGER);self.assertEqual(audit.verify_quotes(rows),len(rows))
        with self.assertRaisesRegex(AssertionError,'quote coordinates'):audit.verify_quotes(rows[:-1])
        self.assertEqual(audit.verify_tables(),14)
        with patch.object(audit,'generator_identity',return_value={}),self.assertRaisesRegex(AssertionError,'stale generator'):audit.verify_tables()

    # Grid completeness and explicit capacity alarms prevent silently dropped
    # load/classes or a plotted1M PRO session that cannot fit.
    def test_small_team_grid_and_capacity_alarms_refuse_silent_omission(self):
        import r20_audit as audit
        rows=audit.read(audit.OUT/'small_team_cost.csv')
        coordinates={(x['profile'],x['share'],x['client'],x['basis'],x['server'],x['billing'],x['team']) for x in rows}
        self.assertEqual(len(coordinates),576);self.assertEqual(len(rows),576)
        dec=audit.read(audit.OUT/'decode_scaling.csv')
        invalid=[x for x in dec if x['server']=='pro6000_fp8' and x['depth']=='1000000']
        self.assertEqual(len(invalid),3);self.assertTrue(all(x['status']=='alarm' and x['gain']=='nan' for x in invalid))
        valid=next(x for x in dec if x['server']=='b300_fp8' and x['depth']=='1000000' and x['requested_streams']=='32')
        self.assertEqual(valid['status'],'ok');self.assertEqual(valid['batch'],'3')
        for table in ('small_team_cost','team_break_even','engine_sensitivity','rented_vllm_prefill'):
            for row in audit.read(audit.OUT/(table+'.csv')):
                scope=row['workload_scope']
                for expected in ('10885/39904','27.28%','normalized to ','calls/person-month','full workload unsupported'):self.assertIn(expected,scope)
        coverage=audit.read(audit.OUT/'workload_coverage.csv')[0]
        self.assertEqual(coverage['full_workload_cost'],'nan');self.assertEqual(coverage['common_calls'],'10885')

    # A valid standalone scientific SVG is tied to the exact CSV; stale source
    # metadata is rejected in a scratch fixture without changing real exports.
    def test_figure_refuses_stale_csv_binding_with_positive_control(self):
        import tempfile
        import r20_audit as audit
        self.assertTrue(audit.verify_figure())
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            for name in ('batching_figure.json','batching_gain.svg','decode_scaling.csv'):(out/name).write_bytes((audit.OUT/name).read_bytes())
            meta=json.loads((out/'batching_figure.json').read_text());meta['source_sha256']='0'*64
            (out/'batching_figure.json').write_text(json.dumps(meta))
            with patch.object(audit,'OUT',out),self.assertRaisesRegex(AssertionError,'figure source mismatch'):audit.verify_figure()


if __name__=='__main__':unittest.main()
