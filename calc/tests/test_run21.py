"""Run21 independent boundaries and paired negative/positive controls."""
import copy
import csv
import hashlib
import json
import io
import itertools
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.inputs import InputGap, ROOT
from hybridcalc import deep_r21 as d, measurements_r21 as r
from hybridcalc import measurements_r19 as r19, server_economics_r20 as s
from hybridcalc.engine import load
from hybridcalc.paper_tables import Context


class ProfileContracts(unittest.TestCase):
    # Source digest refuses substituted statistics; the original aggregate
    # and exact Claude quantiles are independent positive controls.
    def test_profile_source_refuses_corruption_and_combined_pause_substitution(self):
        cfg=d.config();stats=d.checked_stats(cfg)
        self.assertEqual(stats['agents']['claude']['depth_per_call']['p50'],212311)
        self.assertEqual(stats['agents']['claude']['gap_seconds']['p90'],60.6)
        rows=d.profile_rows(stats)
        val=lambda p:next(x['value']for x in rows if x['profile']==p and x['metric']=='gap_seconds'and x['statistic']=='p90')
        self.assertEqual(val('claude_deep'),60.6);self.assertEqual(val('existing_combined'),34.8)
        cfg['stats_sha256']='0'*64
        with self.assertRaisesRegex(InputGap,'SHA256'):d.checked_stats(cfg)

    # Reconstruction is deterministic and deep, not a second combined draw;
    # an under-resolved quadrature is refused rather than called raw replay.
    def test_deep_reconstruction_refuses_tiny_grid_with_deep_positive_control(self):
        a=d.checked_stats()['agents']['claude'];calls=d.reconstruct(a)
        self.assertEqual(calls,d.reconstruct(a));self.assertEqual(len(calls),1000)
        self.assertGreater(sum(x[0]>=200000 for x in calls)/len(calls),.5)
        self.assertEqual(next(x[1]for x in calls if x[0]>900000),689.7)
        self.assertGreater(sum(x[0]for x in calls)/len(calls),250000)
        self.assertAlmostEqual(sum(x[0]for x in calls)/len(calls),a['depth_per_call']['mean'],places=3)
        self.assertAlmostEqual(sum(x[2]for x in calls)/len(calls),a['output_per_call']['mean'],places=3)
        self.assertLessEqual(max(x[3]for x in calls),300)
        with self.assertRaisesRegex(InputGap,'at least100'):d.reconstruct(a,10)
        with self.assertRaises(InputGap):d.reconstruct(a,pause_cap=0)
        bad=copy.deepcopy(a);bad['depth_per_call']['mean']=2000000
        with self.assertRaisesRegex(InputGap,'incompatible'):d.reconstruct(bad)

    # API extension is explicitly unknown, even with local YaRN factor4.
    def test_yarn_refuses_identical_api_extension_claim_with_hybrid_control(self):
        self.assertIn('factor4',d.extension_basis('qwen','client'))
        self.assertEqual(d.extension_basis('qwen','client'),d.extension_basis('qwen','server'))
        self.assertIn('unknown',d.extension_basis('qwen','api'))
        self.assertNotIn('factor4',d.extension_basis('qwen','api'))
        with self.assertRaisesRegex(InputGap,'unknown model'):d.extension_basis('wrong','server')


class ServerContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers={k:d.Server(k)for k in d.SERVERS}
        spec,inp=load('deep-economics-r21');oldspec,_=load('paper-tables-r17');cls.c=Context(oldspec,inp)

    # Owner exclusion applies only to new server classes; measured B300 and
    # PRO variants remain admissible, historical5090 client code is untouched.
    def test_server_refuses_5090_with_pro_and_b300_controls(self):
        self.assertEqual(set(self.servers),{'pro6000_fp8','b300_fp8','b300_fp8_kv'})
        with self.assertRaisesRegex(InputGap,'owner excludes5090'):d.Server('rtx5090')

    # R20 still refuses deep input, while the explicitly named R21 extension
    # is continuous at249k, nonnegative, and bounded by the analysis envelope.
    def test_deep_prefill_refuses_unbounded_extension_and_preserves_measured_anchor(self):
        server=self.servers['b300_fp8'];old=s.Server('b300_fp8')
        self.assertEqual(server.cached(249000,2000),old.cached(249000,2000))
        self.assertGreater(server.cached(1000000,690),server.cached(249000,690))
        self.assertGreater(server.cold(1000000),server.cold(249000))
        with self.assertRaisesRegex(InputGap,'outside measured'):old.cached(1000000,690)
        with self.assertRaisesRegex(InputGap,'envelope exceeded'):server.cached(1048576,1)
        with self.assertRaisesRegex(InputGap,'cold rebuild exceeds'):server.cold(1048577)
        self.assertEqual(server.cached(1000000,0),0)

    # Complete default-KV1M sessions refuse on PRO6000; B300 FP8-KV fits,
    # and gain must fall with depth rather than share per-session KV.
    def test_million_capacity_refuses_pro_and_depth_independent_batch_gain(self):
        pro=self.servers['pro6000_fp8'];b=self.servers['b300_fp8_kv']
        with self.assertRaisesRegex(InputGap,'complete session'):pro.decode(1000000,1)
        self.assertEqual(b.decode(1000000,32)['batch'],7)
        self.assertLess(b.decode(1000000,32)['gain'],b.decode(16000,32)['gain'])
        self.assertLess(b.decode(1000000,32)['gain'],2)

    # Deep decode can arrive through data only; missing extension evidence,
    # duplicates, unrecorded engine or impossible streams cannot be admitted.
    def test_decode_data_interface_refuses_missing_yarn_and_impossible_streams(self):
        row=dict(server='b300_fp8_kv',streams=1,depth=1000000,aggregate_tok_s=100,
            source='fixture',observed_at='2026-11-03',engine='vllm',extension='yarn_factor4')
        valid={'measurements':[row]};parsed=d.decode_measurements(valid,self.servers)
        self.assertEqual(self.servers[row['server']].decode(1000000,1,parsed)['aggregate_tok_s'],100)
        for key,value,reason in (('extension','unknown','YaRN'),('streams',8,'resident capacity'),('engine','llama_cpp','dated vLLM'),('source','','dated vLLM')):
            with self.subTest(key=key),self.assertRaisesRegex(InputGap,reason):
                d.decode_measurements({'measurements':[dict(row,**{key:value})]},self.servers)
        with self.assertRaisesRegex(InputGap,'finite nonnegative'):
            d.decode_measurements({'measurements':[dict(row,streams=True)]},self.servers)
        with self.assertRaisesRegex(InputGap,'duplicate'):d.decode_measurements({'measurements':[row,row]},self.servers)
        controls=[dict(row,depth=512000,streams=1),dict(row,depth=512000,streams=8)]
        self.assertEqual(len(d.decode_measurements({'measurements':controls},self.servers)),2)

    # A zero-new-token call may create output catch-up, but never divide by
    # zero or offload a free local prefill. Nearby real deltas stay positive.
    def test_zero_delta_refuses_spurious_offload_with_output_catchup_control(self):
        p=r.Prepared([(100000,0,512,8)],self.servers['b300_fp8'],'m5max64',self.c,'measured_envelope',[])
        self.assertEqual(p.own,[0]);self.assertGreater(p.shadow[0],0)
        self.assertEqual(p.stats(0,'office_gigabit')['offload_share'],0)
        self.assertGreater(self.servers['b300_fp8'].cached(100000,512),0)

    # Payload includes fixed state and the analyst sensitivity pays transfer,
    # import and RTT. The slow0.8MB/s link cannot inherit5.19MB/s's decision.
    def test_million_links_refuse_missing_state_and_unlabelled_local_estimate(self):
        rows=r.million_links(self.c,{'b300_fp8_kv':self.servers['b300_fp8_kv']},d.config())
        sel=lambda k:next(x for x in rows if x['client']=='m3max'and x['link']==k and x['rate_basis'].startswith('analyst'))
        wifi=sel('historical_home_wifi');slow=sel('today_wifi')
        self.assertEqual(wifi['wire_bytes'],180916224)
        self.assertAlmostEqual(wifi['transfer_s'],180916224/5190000)
        self.assertTrue(wifi['offload']);self.assertFalse(slow['offload'])
        self.assertGreater(wifi['import_s'],30)
        with self.assertRaisesRegex(InputGap,'unlabelled'):d.mac_prefill(self.c,'m3max',1000000,690,'measured')

    # Raw bandwidth is a ceiling, not calibrated achieved throughput; the
    # actual1.67 observation retains its distinct depth and priority label.
    def test_decode_ceiling_refuses_invalid_bandwidth_and_efficiency_claim(self):
        ceiling=d.mac_ceiling(1000000)
        self.assertAlmostEqual(ceiling,400e9/(18.97e9+34816e6+156893184))
        self.assertGreater(ceiling,7);self.assertLess(ceiling,8)
        self.assertGreater(ceiling/1.67,4)
        self.assertEqual(d.config()['mac_1M_decode_priority'],'background_priority_interim')
        with self.assertRaises(InputGap):d.mac_ceiling(1000000,0)

    # GLM FP8's328GB weights require two GPUs. MoE union grows with batch;
    # full KV/state are per session, so gain cannot equal the batch count.
    def test_glm_batch_refuses_dense_weight_sharing_and_single_gpu_fit(self):
        one=r.glm_batch(1000000,1,self.c.inputs);many=r.glm_batch(1000000,32,self.c.inputs)
        self.assertEqual(one['replica_gpus'],2);self.assertGreater(one['weights_bytes'],288e9)
        self.assertEqual(one['session_bytes'],5984e6+152600000)
        self.assertLess(many['gain'],many['batch']/2)
        self.assertGreater(many['aggregate_tok_s'],one['aggregate_tok_s'])
        with self.assertRaises(InputGap):r.glm_batch(1000000,0,self.c.inputs)

    # Million fleets use whole boxes and total team streams; doubling boxes
    # does not mint more than4T sessions. Small-team capacity stays explicit.
    def test_million_fleet_refuses_duplicate_concurrency_and_invalid_team(self):
        b=self.servers['b300_fp8_kv'];own=r.million_own(self.c,b,'qwen',200,1,b.cold(1000000),team=5)
        self.assertIsInstance(own['boxes'],int)
        self.assertLessEqual(own['total_streams'],20)
        self.assertGreater(own['person_month'],0)
        with self.assertRaises(InputGap):r.million_own(self.c,b,'qwen',200,1,1,team=0)

    # Retained-slot pricing reserves the deepest complete admitted call;
    # a shallower configured minimum cannot underprice its host storage.
    def test_profile_retention_refuses_shallower_than_end_depth_reservation(self):
        calls=[(920000,690,762,8)]
        self.assertEqual(r.profile_reservation(calls,900000,self.servers),921452)
        self.assertEqual(r.profile_reservation([(16000,512,128,8)],249000,self.servers),249000)
        with self.assertRaisesRegex(InputGap,'complete session'):r.profile_reservation(calls,1000000,self.servers)


class ApiContracts(unittest.TestCase):
    # Filtering cannot restart a group or drop the preceding call's output.
    # A genuine original group boundary resets billing as a nearby control.
    def test_profile_api_refuses_cache_group_restart_after_filtering(self):
        calls=[(100000,100,500,8),(100000,100,700,8),(100000,100,900,8)]
        rows,_=r.profile_api(calls,[0,2],'existing_combined',d.config(),116)
        chutes=next(x for x in rows if x['model']=='qwen'and x['tag']=='chutes/fp8')
        self.assertEqual(chutes['mean_input_tokens'],100450)
        self.assertEqual(chutes['mean_output_tokens'],700)
        reset,_=r.profile_api(calls,[0,2],'existing_combined',d.config(),2)
        control=next(x for x in reset if x['model']=='qwen'and x['tag']=='chutes/fp8')
        self.assertEqual(control['mean_input_tokens'],100100)
        self.assertLess(control['usd_per_1000_calls'],chutes['usd_per_1000_calls'])

    # Cache data is keyed by model AND profile; over-counts and wrong-model
    # observations cannot silently alter an unrelated provider's price.
    def test_cache_interface_refuses_model_leakage_and_invalid_counts(self):
        row=dict(model='qwen/qwen3.8-27b',tag='phala',profile='million',source='fixture',observed_at='2026-11-03',input_tokens=100,cached_tokens=90)
        known={(row['model'],row['tag'])}
        self.assertEqual(d.provider_measurements({'measurements':[row]},known),{(row['model'],'phala','million'):.9})
        for key,value in (('model','wrong'),('cached_tokens',101),('source',''),('profile','wrong')):
            with self.subTest(key=key),self.assertRaises(InputGap):d.provider_measurements({'measurements':[dict(row,**{key:value})]},known)

    # At1M Alibaba's bad uptime excludes it, Phala/Novita pass. GLM price
    # alone cannot prove cache declaration; a declared fixture is a control.
    def test_million_admission_refuses_alibaba_and_unverified_glm_cache(self):
        cfg=d.config();rows,chosen=d.api_baselines([(998548,690,762,8)],'million',cfg,1000000)
        q=[x for x in rows if x['model']=='qwen'];g=[x for x in rows if x['model']=='glm']
        self.assertFalse(next(x for x in q if x['tag']=='alibaba')['admitted'])
        self.assertEqual({x['tag']for x in q if x['admitted']},{'phala','novita'})
        self.assertEqual(chosen['qwen']['count'],2);self.assertEqual(chosen['glm']['count'],0)
        self.assertTrue(all(not x['admitted']for x in g))
        candidate=copy.deepcopy(cfg['glm_endpoints']['endpoints'][0]);candidate['supports_implicit_caching']=True
        self.assertEqual(s.admission(candidate,1000000),[])
        cfg['owner_cache_fraction']=1
        with self.assertRaisesRegex(InputGap,'NOTES evidence'):d.api_baselines([(998548,690,762,8)],'million',cfg,1000000)

    # Measured provider hits change effective prices via data alone; no-hit
    # misses remain billed rather than becoming an optimistic free cache.
    def test_provider_cache_data_changes_effective_price_with_positive_control(self):
        cfg=d.config();calls=[(998548,690,762,8)]
        before,_=d.api_baselines(calls,'million',cfg,1000000)
        cfg['provider_cache_hits']['measurements']=[dict(model='qwen/qwen3.8-27b',tag='phala',profile='million',source='fixture',observed_at='2026-11-03',input_tokens=100,cached_tokens=0)]
        after,_=d.api_baselines(calls,'million',cfg,1000000)
        get=lambda rows:next(x for x in rows if x['model']=='qwen'and x['tag']=='phala')
        self.assertGreater(get(after)['usd_per_1000_calls'],get(before)['usd_per_1000_calls'])
        self.assertEqual(get(after)['cache_basis'],'measured provider token fraction')



class ExportLabelContracts(unittest.TestCase):
    # R20 F1 repeats the R19 rental omission: a price needs original/common
    # counts and explicit1000-call normalization, not just a mean token count.
    def test_r20_api_coverage_regression_refuses_missing_population_provenance(self):
        import r21_export_labels as labels
        text=labels.scope('fixture',10885,39904)
        for expected in ('10885/39904','27.28%','1000','full observed workload unsupported'):
            self.assertIn(expected,text)
        self.assertIn('100.00%',labels.scope('control',1,1))
        with self.assertRaisesRegex(AssertionError,'positive original/common'):labels.scope('bad',0,1)

    # R20 F2's actual Novita witness has a missing5m window. A full recorded
    # Phala fixture cannot be mislabeled as missing all availability data.
    def test_r20_missing_availability_regression_names_partial_windows(self):
        import r21_export_labels as labels
        rows=json.loads(s.SNAPSHOT.read_text())['data']['endpoints']
        novita=next(x for x in rows if x['tag']=='novita')
        self.assertIn('missing windows: 5m',labels.availability(novita))
        self.assertNotIn('missing windows: none',labels.availability(novita))
        complete=dict(novita,uptime_last_5m=100,uptime_last_30m=100,uptime_last_1d=100)
        self.assertIn('missing windows: none',labels.availability(complete))
        self.assertIn('5m=100%',labels.availability(complete))

    # Real API publications must carry labels on every row and bind their
    # publisher source hash; an omitted label is a known checker violation.
    def test_api_publication_refuses_removed_scope_with_price_preservation_control(self):
        import r21_export_labels as labels
        import r21_audit as a
        self.assertTrue(labels.verify(a.OUT,'r21','api_admission'))
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)
            for name in ('r21_manifest.json','api_admission.csv','workload_coverage.csv'):
                (root/name).write_bytes((a.OUT/name).read_bytes())
            rows=labels.read(root/'api_admission.csv');fields=list(rows[0]);rows[0]['workload_scope']=''
            with (root/'api_admission.csv').open('w',newline='')as f:
                writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
            with self.assertRaisesRegex(AssertionError,'label omitted'):labels.verify(root,'r21','api_admission')


class CustodyContracts(unittest.TestCase):
    # Standalone-I commands can import their publisher; bad arguments fail
    # before writes, rather than succeeding only under unittest's sys.path.
    def test_standalone_auditors_refuse_unknown_arguments_and_import_in_isolation(self):
        paths=list((ROOT/'calc/out/run21').rglob('*'))
        before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths if p.is_file()}
        for name in ('r21_audit.py','r21_growth_audit.py'):
            script=Path(__file__).with_name(name)
            valid=subprocess.run([sys.executable,'-B','-I',str(script),'--audit-only'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(valid.returncode,0,valid.stderr)
            invalid=subprocess.run([sys.executable,'-B','-I',str(script),'--unsupported-flag'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(invalid.returncode,1)
            self.assertIn('assert sys.argv[1:]',invalid.stderr);self.assertIn('AssertionError',invalid.stderr)
        self.assertEqual(before,{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths if p.is_file()})

    # The original profile inputs and scenario accounting stay byte-identical;
    # a substituted sampler blob is a known checker violation in a fixture.
    def test_existing_profile_refuses_changed_sampler_with_historical_control(self):
        import r21_audit as a
        self.assertEqual(a.frozen(),931)
        oldspec,_=load('server-economics-r20');newspec,_=load('deep-economics-r21')
        self.assertEqual(newspec['overrides'],oldspec['overrides'])
        original=a.history.snapshot_hash
        def corrupt(revision,name):
            return '0'*64 if name.endswith('/sampler.json')else original(revision,name)
        with patch.object(a.history,'snapshot_hash',side_effect=corrupt),self.assertRaisesRegex(AssertionError,'changed existing profile bytes'):a.frozen()

    # Bandwidth and a whole-node calendar price cannot inherit seconds or
    # per-person labels from suffix matching. Actual seconds are a control.
    def test_units_refuse_bandwidth_as_time_and_node_price_as_person_price(self):
        self.assertEqual(r.unit('bytes_s',5190000),'B/s')
        self.assertEqual(r.unit('threshold_MB_s',2),'MB/s (decimal)')
        self.assertEqual(r.unit('warm_rental_floor_node_month',55480),'USD/node-month')
        self.assertEqual(r.unit('reservation_depth',1000000),'token')
        self.assertEqual(r.unit('target_depth',1000000),'token')
        self.assertEqual(r.unit('tasks_day',2),'task/person/day')
        self.assertEqual(r.unit('calls_per_task',700),'call/task')
        self.assertEqual(r.unit('import_s',3),'s')
        self.assertEqual(r.unit('hybrid_work_person_month',3),'USD/person-month (open-model component)')

    # F1 regression retains exact numeric/display cells in the corrected view;
    # a bare historical rental basis is the known negative witness.
    def test_r19_rental_basis_missing_coverage_regression_and_numeric_control(self):
        original=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run19/rented_prefill_node.csv').read_text())))
        corrected=d.corrected_r19();self.assertEqual(len(corrected),48)
        for old,new in zip(original,corrected):
            self.assertNotIn('10885/39904',old['basis'])
            for expected in ('10885/39904','27.28%','52500','full workload unsupported'):self.assertIn(expected,new['basis'])
            for key,value in old.items():
                if key not in ('basis','status','alarm_inputs'):self.assertEqual(value,new[key])

    # The PRO6000 guard now refuses the exact reviewer relabelling witness;
    # the published source basis is still accepted without new rate claims.
    def test_pro6000_refuses_fresh_hybrid_measurement_relabelling(self):
        self.assertEqual(r19.Node('pro6000').key,'pro6000')
        cfg=r19.config();cfg['nodes']['pro6000']['rate_basis']='fresh measured hybrid node'
        with self.assertRaisesRegex(InputGap,'portability'):r19.Node('pro6000',cfg)

    # Dropping a historical file or one quote is detectable. New server rows
    # must exclude5090 for both workloads, while old exports remain exact.
    def test_exports_refuse_missing_history_quotes_and_5090_server_rows(self):
        import r21_audit as a
        self.assertEqual(a.frozen(),931)
        with patch.object(a.history,'snapshot_hash',return_value='0'*64),self.assertRaisesRegex(AssertionError,'changed historical bytes'):a.frozen()
        rows=a.read(a.LEDGER);self.assertEqual(a.verify_quotes(rows),len(rows))
        with self.assertRaisesRegex(AssertionError,'quote coordinates'):a.verify_quotes(rows[:-1])
        self.assertEqual(a.verify_tables(),17)
        with patch.object(a,'generator_identity',return_value={}),self.assertRaisesRegex(AssertionError,'stale generator'):a.verify_tables()
        for table in ('small_team_cost','main_economics','team_break_even'):
            rows=a.read(a.OUT/(table+'.csv'))
            self.assertEqual({x['profile']for x in rows},{'existing_combined','claude_deep'})
            self.assertEqual({x['server']for x in rows},set(d.SERVERS))
            self.assertTrue(all('full original workload unsupported'in x['workload_scope']for x in rows))
            fields=('profile','load','share','client','basis','server','billing')
            axes=(('existing_combined','claude_deep'),('light','medium','heavy'),('0.2','0.5','1.0'),('m5max64','m5max'),('owned','new'),d.SERVERS,('bought','rented'))
            last='reference'if table=='team_break_even'else'team'
            values=('api_cheapest','api_median','own_cluster')if last=='reference'else('3','5','10','20')if table=='small_team_cost'else('50','500')
            coordinates=[tuple(row[k]for k in fields+(last,))for row in rows]
            self.assertEqual(set(coordinates),set(itertools.product(*axes,values)))
            self.assertEqual(len(coordinates),len(set(coordinates)))


if __name__=='__main__':unittest.main()
