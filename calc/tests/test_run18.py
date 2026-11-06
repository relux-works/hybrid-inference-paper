"""Run18 capacity, rate, transport and ephemeral-rental contract witnesses."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc import measurements_r18 as r18,measurements_r17 as r17,measurements_r16 as r16
from hybridcalc.inputs import InputGap,ROOT


class Run18Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=r18.Client('rtx3090_qwen27')
        cls.g=r18.Client('rtx3090_glimmer30')
        cls.fast=r18.Client('rtx5090_glimmer30')
        cls.qfast=r18.Client('rtx5090_qwen27')

    # The5090 Qwen source is admitted only after the canonical digest fix.
    # Physical262144 and measured249k bounds remain separate on this card too.
    def test_5090_qwen_rejects_context_overflow_and_rate_extrapolation(self):
        p=self.qfast;self.assertEqual(p.cap,262144)
        p.admit(262144)
        self.assertGreater(p.for_delta(249000,10000),0)
        self.assertAlmostEqual(p.parallel_at(2,131088,2)['aggregate_tok_s'],57.77,delta=.00051)
        with self.assertRaisesRegex(InputGap,'hard context'):p.admit(262145)
        with self.assertRaisesRegex(InputGap,'measured rate coverage'):p.for_delta(250000,512)

    # Capacity counts prefix, newly-prefilled tokens and generated output.
    # A rate endpoint hold cannot make a99,329-token session fit the3090.
    def test_3090_capacity_rejects_prefix_delta_and_output_overflow(self):
        self.q.admit(99328);self.q.admit(98000,1000,328)
        for d,n,o in ((99329,0,0),(99000,329,0),(98000,1000,329)):
            with self.subTest(d=d,n=n,o=o),self.assertRaisesRegex(InputGap,'hard context capacity 99328'):
                self.q.admit(d,n,o)
        with self.assertRaisesRegex(InputGap,'hard context'):self.q.for_delta(100000,512)
        self.assertGreater(self.q.for_delta(64000,2343),0)

    # Unmeasured rates between86k and the99,328 capacity cap stay unavailable;
    # rejecting every physically-fitting session would fail the86k control.
    def test_rate_coverage_rejects_extrapolation_inside_capacity(self):
        self.q.admit(90000,512)
        with self.assertRaisesRegex(InputGap,'measured rate coverage'):self.q.for_delta(90000,512)
        with self.assertRaisesRegex(InputGap,'measured rate coverage'):self.q.decode(90000)
        self.assertGreater(self.q.for_delta(86000,512),0)
        self.assertGreater(self.q.decode(86000),0)
        self.assertEqual(self.q.for_delta(0,1),self.q.for_delta(16000,512))
        with self.assertRaises(InputGap):self.q.for_delta(-1,512)
        with self.assertRaises(InputGap):self.q.decode(float('nan'))

    # A data-file edit cannot inflate the measured one-slot memory limit.
    def test_capacity_config_rejects_inflated_3090_limit(self):
        cfg=r18.config();cfg['clients']['rtx3090_qwen27']['context_limit']=262144
        with self.assertRaisesRegex(InputGap,'cannot be enlarged'):r18.Client('rtx3090_qwen27',cfg)
        self.assertEqual(self.q.cap,99328);self.assertEqual(self.g.cap,131072)

    def altered(self,key,change):
        manifest,p=r18.package(key);p=dict(p)
        model='q27b' if key.endswith('qwen27') else 'glimmer30'
        name=next(n for n in p if '-'+model+'-q4km-' in n and n.endswith('.jsonl'))
        records=[json.loads(l) for l in p[name].splitlines()];change(records)
        p[name]='\n'.join(map(json.dumps,records)).encode()
        return r18.Client(key,evidence=(manifest,p))

    # Real reused grids pass; missing/duplicated rows, rereads, wrong framing,
    # altered weights and wrong device are refused before any rate is used.
    def test_rates_reject_partial_reread_wrong_device_and_weights(self):
        self.altered('rtx3090_qwen27',lambda rs:None)
        for key,v in (('reread',True),('prompt_n',9999),('predicted_n',127),('prompt_ms',0),('depth',123)):
            def change(rs):next(r for r in rs if r['kind']=='turn')[key]=v
            with self.subTest(key=key),self.assertRaises(InputGap):self.altered('rtx3090_qwen27',change)
        with self.assertRaisesRegex(InputGap,'complete distinct'):
            self.altered('rtx3090_qwen27',lambda rs:rs.pop(next(i for i,r in enumerate(rs) if r['kind']=='turn')))
        with self.assertRaisesRegex(InputGap,'device/model/context'):
            self.altered('rtx3090_qwen27',lambda rs:rs[0].update(label='rtx-5090-q27b'))
        m,p=r18.package('rtx3090_qwen27');m=dict(m,model_sha256='0'*64)
        with self.assertRaisesRegex(InputGap,'same measured model'):r18.Client('rtx3090_qwen27',evidence=(m,p))

    # Linux GPU normal priority is TS/nice0, independently of macOS PRI31.
    # Manifest-only relabelling cannot overrule a background server sample.
    def test_priority_rejects_override_and_background_server(self):
        m,p=r18.package('rtx3090_qwen27');r18.normal_priority(m,p)
        with self.assertRaisesRegex(InputGap,'without override'):r18.normal_priority(dict(m,priority_override_used=True),p)
        n=next(n for n in p if 'OPERATOR-READINESS' in n and n.endswith('.json'))
        for field,value in (('nice',10),('scheduling_class','IDLE')):
            bad=dict(p);d=json.loads(p[n]);next(s for r in d['samples'] for s in r['servers'])[field]=value
            bad[n]=json.dumps(d).encode()
            with self.subTest(field=field),self.assertRaisesRegex(InputGap,'Linux TS nice0'):r18.normal_priority(m,bad)

    # A custody discrepancy refuses. A corrected expected digest must match
    # literally; the archive's actual bytes are still independently checked.
    def test_custody_rejects_FACTS_discrepancy_and_bad_archive_hash(self):
        cfg=r18.config();key='rtx3090_qwen27';self.assertTrue(r18.package(key,cfg)[1])
        cfg['sources'][key].update(facts_suffix='abcd')
        with self.assertRaisesRegex(InputGap,'FACTS checksum discrepancy'):r18.package(key,cfg)
        cfg['sources'][key]['facts_suffix']=cfg['sources'][key]['sha256'][-4:]
        self.assertTrue(r18.package(key,cfg)[1]) # synthetic correction control only
        cfg['sources'][key]['sha256']='0'*64
        cfg['sources'][key].update(facts_prefix='00000000',facts_suffix='0000')
        with self.assertRaisesRegex(InputGap,'archive sha256 mismatch'):r18.package(key,cfg)

    # Raw round intervals reproduce all admitted parallel aggregates. Counts,
    # depths and server np are exact lookup coordinates, not interpolation axes.
    def test_parallel_rejects_unmeasured_count_depth_and_server_shape(self):
        p=self.q.parallel_at(1,65552,1);self.assertAlmostEqual(p['aggregate_tok_s'],22.421,delta=.00051)
        self.assertAlmostEqual(self.g.parallel_at(8,65552,8)['aggregate_tok_s'],56.98,delta=.00051)
        for args in ((2,65552,1),(1,65536,1),(1,65552,2),(0,65552,1)):
            with self.subTest(args=args),self.assertRaises(InputGap):self.q.parallel_at(*args)
        self.assertEqual(self.q.parallel_at(2,32000,2)['aggregate_tok_s'],42.66)

    # A valid summary cannot hide an invalid/unrestored/incomplete raw round.
    def test_parallel_rejects_damaged_rounds_and_missing_counts(self):
        m,p=r18.package('rtx3090_glimmer30')
        n=next(n for n in p if n.startswith('results/parallel-depth-'))
        for field,value in (('valid',False),('restore_reused',False),('n_ctx_slot',1),('aggregate_tok_s',99)):
            bad=dict(p);rs=[json.loads(l) for l in p[n].splitlines()];next(r for r in rs if r['kind']=='round')[field]=value
            bad[n]='\n'.join(map(json.dumps,rs)).encode()
            with self.subTest(field=field),self.assertRaises(InputGap):r18.Client('rtx3090_glimmer30',evidence=(m,bad))
        bad={name:b for name,b in p.items() if name!=n}
        with self.assertRaisesRegex(InputGap,'complete distinct parallel shape'):r18.Client('rtx3090_glimmer30',evidence=(m,bad))
        self.assertTrue(self.g.parallel)

    # Rate interpolation uses both measured axes and raw timings; rounded
    # display fields and a flat2k rate cannot silently replace a delta surface.
    def test_prefill_rejects_flat_delta_and_display_rounding(self):
        p=self.q;a=p.for_delta(50000,2000);b=p.for_delta(50000,10000)
        self.assertAlmostEqual(p.for_delta(50000,2343),a+(b-a)*343/8000)
        r=next(r for r in p.turns if r['level']==16000 and r['delta']==512)
        self.assertEqual(p.for_delta(16000,512),r['prompt_n']*1000/r['prompt_ms'])
        self.assertNotEqual(p.for_delta(16000,512),r['prefill_tok_s'])

    # Nonpositive serial budget means no finite rate, never0MB/s. Physical
    # capacity rejection has a separate status from an unprofitable valid call.
    def test_threshold_rejects_zero_finite_rate_and_capacity_laundering(self):
        rs=r18.threshold_rows([self.q,self.g,self.fast]);self.assertEqual(len(rs),36)
        blocked=[r for r in rs if r['client']==self.q.key and r['depth']==100000]
        self.assertEqual(len(blocked),6)
        self.assertTrue(all(r['threshold_status']=='capacity_refused' for r in blocked))
        never=[r for r in rs if r['threshold_status']=='never_pays_nonpositive_budget'];self.assertTrue(never)
        for r in never:
            self.assertLessEqual(r['budget_s'],0)
            self.assertIn('alarm',r['break_even_downstream_mb_s'])
        # The optimistic importer is a bounded control, not an admitted rate.
        with patch.object(r18,'cuda_import',return_value=0):control=r18.threshold_rows([self.q])
        finite=[r for r in control if r['threshold_status']=='finite_threshold'];self.assertTrue(finite)
        for r in finite:
            speed=r['break_even_downstream_mb_s']*1e6
            self.assertAlmostEqual(r['wire_bytes']/speed+r['server_prefill_s']+r['import_s']+r['rtt_s'],r['local_prefill_s'])
            self.assertEqual(r['break_even_downstream_mbit_s'],8*r['break_even_downstream_mb_s'])

    # CUDA depth is jointly fitted, including its intercept. The old Mac slope
    # is never read, and negative delta is still refused; bf16 has no speedup.
    def test_cuda_import_rejects_apple_fit_and_omitted_depth(self):
        a,b,c=r18.cuda_depth_fit()
        with patch.object(r16,'depth_fit',side_effect=AssertionError('Mac fit read by CUDA')):
            self.assertAlmostEqual(r18.cuda_import(2343,64000,'qwen27'),a+b*2343+c*64000)
        self.assertNotAlmostEqual(r18.cuda_import(2343,64000,'qwen27'),r16.ClientImport().at_depth(2343,64000))
        with self.assertRaises(InputGap):r18.cuda_import(-1,64000,'qwen27')
        with self.assertRaises(TypeError):r18.cuda_import(2343,model='qwen27')

    # Explicit Apple slope provenance cannot be admitted on a CUDA host;
    # the adjacent CUDA control produces a positive, finite prediction.
    def test_cuda_import_refuses_mac_slope_on_cuda_host(self):
        self.assertGreater(r18.cuda_import(512,100000,'qwen27',depth_basis='cuda_pr9'),0)
        with self.assertRaisesRegex(InputGap,'Mac slope forbidden'):
            r18.cuda_import(512,100000,'qwen27',depth_basis='mac_r16')
        with self.assertRaisesRegex(InputGap,'unqualified model'):
            r18.cuda_import(512,100000,'unknown')

    # A known two-axis synthetic law is independently recoverable; correlated
    # predictors or negative fitted import costs cannot define the fallback.
    def test_cuda_joint_fit_refuses_rank_deficiency_and_negative_costs(self):
        def records(a=1,b=.001,c=.000002):
            return [dict(remote_applied=n,depth_before=d,import_ms=1000*(a+b*n+c*d))
                    for n,d in ((10,1000),(20,1000),(10,2000),(20,2000))]
        with patch('hybridcalc.run14_r5.cuda_import_rows',return_value=records()):
            for got,want in zip(r18.cuda_depth_fit(),(1,.001,.000002)):self.assertAlmostEqual(got,want)
        bad=[dict(remote_applied=n,depth_before=n*100,import_ms=1000+n) for n in (10,20,30)]
        with patch('hybridcalc.run14_r5.cuda_import_rows',return_value=bad),self.assertRaisesRegex(InputGap,'independent delta and depth'):
            r18.cuda_depth_fit()
        for a,b,c in ((-0.001,.001,.000002),(1,-.001,.000002),(1,.001,-.000002)):
            with self.subTest(a=a,b=b,c=c),patch('hybridcalc.run14_r5.cuda_import_rows',return_value=records(a,b,c)),self.assertRaisesRegex(InputGap,'nonnegative CUDA depth'):
                r18.cuda_depth_fit()

    # Each partial rental repeats fetch+cold state. No persistence/free fetch
    # is inferred from an earlier rental or from fewer than116 remaining calls.
    def test_rental_rejects_free_fetch_persistent_state_and_dropped_tail(self):
        f=r18.rental_bill
        self.assertEqual(f(0,10,20,185,.55,116,'ceil_hour_assumption'),0)
        self.assertEqual(f(117,10,20,185,.55,116,'ceil_hour_assumption'),1.10)
        self.assertAlmostEqual(f(117,10,20,185,.55,116,'prorated_hourly_quote'),(2*(185+20)+117*10)/3600*.55)
        self.assertGreater(f(117,10,20,185,.55,116,'prorated_hourly_quote'),(185+20+117*10)/3600*.55)
        for values in ((1,10,20,0,.55,116,'ceil_hour_assumption'),(1,10,20,185,.55,0,'ceil_hour_assumption'),(1,10,20,185,.55,116,'market_bill'),(1.5,10,20,185,.55,116,'ceil_hour_assumption')):
            with self.subTest(values=values),self.assertRaises(InputGap):f(*values)

    # Hourly rounding is explicitly optional; just beyond an hour cannot cost
    # one hour. The hourly quote itself does not assert Vast's billing quantum.
    def test_rental_rejects_floor_hours_and_quote_billing_conflation(self):
        f=r18.rental_bill
        self.assertEqual(f(1,3415,0,185,.55,116,'ceil_hour_assumption'),.55)
        self.assertEqual(f(1,3416,0,185,.55,116,'ceil_hour_assumption'),1.10)
        self.assertLess(f(1,3416,0,185,.55,116,'prorated_hourly_quote'),1.10)
        cfg=r18.config()['rental'];self.assertIn('observed',cfg['price_basis']);self.assertIn('not market',cfg['price_basis'])
        self.assertEqual(cfg['prices']['rtx3090']['download_s'],1029);self.assertEqual(cfg['prices']['rtx5090']['download_s'],185)
        self.assertGreater(cfg['prices']['rtx5090']['rented'],cfg['prices']['rtx5090']['search_high'])

    # Cold state is integrated anew; no snapshot or zero-time prefix appears.
    # An isolated constant-rate control has an independently known integral.
    def test_cold_prefill_rejects_free_prefix_and_out_of_coverage(self):
        p=copy.copy(self.q);p.cold_points=[(8000,100),(40000,100)]
        self.assertEqual(p.cold_seconds(0),0)
        self.assertAlmostEqual(p.cold_seconds(16000),160)
        self.assertGreater(self.q.cold_seconds(50000),0)
        with self.assertRaisesRegex(InputGap,'cold depth beyond'):self.q.cold_seconds(90000)
        with self.assertRaisesRegex(InputGap,'hard context'):self.q.cold_seconds(100000)


class Run18Economics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from hybridcalc.engine import load
        cls.s,cls.i=load('discrete-clients-r18');cls.client=r18.Client('rtx3090_qwen27')
        cls.rs,cls.coverage=r18.economics(cls.i,cls.s,[cls.client])

    # A full-distribution quote cannot silently drop the71% of calls that do
    # not fit this device. Conditional costs disclose the still-smaller rate set.
    def test_comparator_rejects_silent_full_workload_or_context_truncation(self):
        c=self.coverage[0]
        self.assertFalse(c['full_workload_supported'])
        self.assertIn('alarm',c['full_workload_rental_cost'])
        self.assertEqual(c['total_calls'],39904)
        self.assertEqual(c['capacity_fit_calls'],11551)
        self.assertEqual(c['rate_covered_calls'],9324)
        for r in self.rs:
            self.assertEqual(r['workload'],'common_measured_capacity_subset')
            self.assertAlmostEqual(r['coverage_call_share'],9324/39904)
            self.assertEqual(r['context_limit'],99328)
            self.assertAlmostEqual(r['device_capacity_share'],11551/39904)
            self.assertAlmostEqual(r['device_measured_coverage_share'],9324/39904)
        from hybridcalc.engine import load
        s,i=load('discrete-clients-r18',['workload.sample_calls=0'])
        with self.assertRaisesRegex(InputGap,'run18.workload'):r18.economics(i,s,[self.client])

    # APIs, hybrid+overflow and the owned-server allocation share the same
    # conditional calls and demand denominator; price cases change only rental.
    def test_comparator_rejects_unmatched_price_and_demand_denominators(self):
        self.assertEqual(len(self.rs),6)
        for prefix in ('api_cheapest','api_median','hybrid','own_server'):
            self.assertEqual(len({r[prefix+'_usd_person_month'] for r in self.rs}),1)
            for r in self.rs:
                self.assertAlmostEqual(r[prefix+'_usd_per_1000_calls'],r[prefix+'_usd_person_month']/r['calls_person_month']*1000)
        for r in self.rs:
            self.assertEqual(r['calls_person_month'],52500)
            self.assertGreater(r['fetch_s_per_rental'],0)
            self.assertGreater(r['cold_prefill_s_per_rental'],0)
            self.assertIn('none across rentals',r['persistence'])
            self.assertAlmostEqual(r['rented_usd_person_month'],r['rented_billed_hours_person_month']*r['observed_hourly_usd'])
        # Aggregate GPU hours can exceed one8h/day machine; cost is a sum of
        # independent rentals, not a claim that one card serves that calendar.
        self.assertGreater(self.rs[0]['rented_wall_hours_person_month'],21*8)


class Run18CustodyAndHistory(unittest.TestCase):
    # The new history perimeter includes accepted Run17, not only runs13–16.
    # A bounded read plant verifies rejection without altering real files.
    def test_history_rejects_mutated_run17_bytes(self):
        import r18_audit as audit
        self.assertEqual(audit.frozen(),907)
        real=Path.read_bytes;target=ROOT/'calc/out/run17/f32/client_sessions_day.csv'
        def damaged(p):return b'bounded historical corruption' if p==target else real(p)
        with patch.object(Path,'read_bytes',damaged),self.assertRaisesRegex(AssertionError,'changed historical bytes'):
            audit.frozen()

    # An authoritative digest disagreement stops the complete exporter before
    # atomic writing begins; valid admitted evidence remains a positive control.
    def test_export_rejects_digest_disagreement_before_any_write(self):
        import r18_audit as audit
        self.assertTrue(r18.package('rtx3090_qwen27')[1])
        cfg=r18.config();cfg['sources']['rtx3090_qwen27']['facts_suffix']='ffff'
        with patch.object(r18,'config',return_value=cfg),patch.object(audit,'frozen',return_value=907),patch.object(audit,'write_tables') as writer,patch.object(sys,'argv',['r18_audit.py']):
            with self.assertRaisesRegex(InputGap,'source correction: rtx3090_qwen27'):audit.main()
            writer.assert_not_called()


class Run18Exports(unittest.TestCase):
    # Changed CUDA cells retain exact prior values; a removed rework record
    # or a forged old value cannot satisfy complete quote coverage. Input
    # changes through R16b/PRI31 may legitimately alter future comparator rows.
    def test_cuda_rework_refuses_missing_old_quotes_and_forged_previous_values(self):
        import r18_audit as audit
        records=audit.read(audit.LEDGER)
        changes=[r for r in records if r['comparison'].startswith('r18_cuda_import_rework')]
        self.assertTrue(changes)
        without=[r for r in records if r is not changes[0]]
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(without)
        bad=copy.deepcopy(records)
        next(r for r in bad if r['comparison'].startswith('r18_cuda_import_rework'))['old']='forged prior value'
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(bad)

    # Current manifests bind the complete four-client export; an in-memory
    # byte plant must be detected without changing any real output.
    def test_complete_exports_reject_changed_bytes_and_stale_generator(self):
        import r18_audit as audit
        self.assertEqual(audit.verify_tables(),9)
        rs=audit.read(audit.OUT/'gpu_client_rates.csv')
        self.assertEqual({r['client'] for r in rs},set(r18.config()['clients']))
        self.assertEqual(len(rs),51)
        real=Path.read_bytes;target=audit.OUT/'gpu_link_threshold.csv'
        def damaged(p):return b'bounded export corruption' if p==target else real(p)
        with patch.object(Path,'read_bytes',damaged),self.assertRaisesRegex(AssertionError,'changed export bytes'):audit.verify_tables()
        with patch.object(audit,'generator_identity',return_value={}),self.assertRaisesRegex(AssertionError,'stale generator'):audit.verify_tables()

    # Full coordinate coverage cannot be satisfied by equal numeric values at
    # another client/depth/billing case, or by omitting the custody correction.
    def test_quote_ledger_rejects_missing_and_forged_coordinates(self):
        import r18_audit as audit
        records=audit.read(audit.LEDGER);self.assertGreater(audit.verify_quotes(records),2000)
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(records[1:])
        bad=copy.deepcopy(records);bad[0]['engine_key']+='; forged=true'
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(bad)
        corrections=[r for r in records if r['comparison']=='recorded_FACTS_checksum_correction']
        self.assertEqual(len(corrections),1)
        self.assertEqual(corrections[0]['old'],'b10541aa...16b')


if __name__=='__main__':unittest.main()
