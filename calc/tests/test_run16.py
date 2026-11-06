"""Run16 contract witnesses: positive controls paired with forbidden outcomes."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap, ROOT
from hybridcalc.paper_tables import Context
from hybridcalc.measurements_r13 import rows
from hybridcalc.measurements_r14 import one_file
from hybridcalc.measurements_r15 import package as old_package
from hybridcalc import measurements_r16 as r16
from hybridcalc.performance import import_at, local_rate_at


class Run16Anchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,i=load('paper-tables-r16');cls.c=Context(s,i);cls.single=cls.c.r16_single
        cls.manifest,cls.payload=r16.package('m3')

    # Raw rates round to all18 PRI31 cells and six decode means in FACTS;
    # the historical100k37.8/5.52 values cannot serve the canonical path.
    def test_pri31_grid_rejects_background_single_rates(self):
        expected=((174.2,176.9,156.3),(121.7,116.1,106.7),(65.3,66.2,63.5),
                  (46.2,47.1,44.4),(36.5,36.8,34.5),(28.7,29.7,27.8))
        for d,values in zip(r16.DEPTHS,expected):
            for n,v in zip(r16.DELTAS,values):self.assertAlmostEqual(self.single.for_delta(d,n),v,delta=.05)
        for (d,rate),expected in zip(self.single.decode_points,(14.99,13.52,10.36,8.99,7.82,6.93)):
            self.assertAlmostEqual(rate,expected,delta=.005)
            self.assertEqual(self.c.parallel.decode(1,d),rate)
        self.assertGreater(self.single.for_delta(100000,512),65)
        self.assertNotAlmostEqual(self.c.parallel.decode(1,100000),5.52,places=1)
        self.assertEqual(local_rate_at(self.single,100000,512),self.single.for_delta(100000,512))
        self.assertNotEqual(local_rate_at(self.single,100000,512),local_rate_at(self.single,100000,10000))

    # The real PRI31 server samples pass despite background ancestors. False
    # manifest flags, overrides and a PRI4 server fail admission distinctly.
    def test_priority_gate_rejects_background_override_and_unrecorded(self):
        r16.normal_priority(self.manifest,self.payload)
        for key,value in (('normal_priority',False),('priority_override_used',True),('normal_priority',None)):
            manifest=dict(self.manifest);manifest[key]=value
            with self.subTest(key=key,value=value),self.assertRaisesRegex(InputGap,'recorded normal priority'):
                r16.SingleStream(manifest,self.payload)
        payload=dict(self.payload);name,content=one_file(payload,'OPERATOR-READINESS','.json');d=json.loads(content)
        next(s for sample in d['samples'] for s in sample.get('servers',[]))['pri']=4
        payload[name]=json.dumps(d).encode()
        with self.assertRaisesRegex(InputGap,'PRI31 server'):r16.SingleStream(self.manifest,payload)

    def altered_single(self,mutate):
        payload=dict(self.payload);name,content=one_file(payload,'-q27b-q4km-');rs=rows(content);mutate(rs)
        payload[name]='\n'.join(map(json.dumps,rs)).encode()
        return r16.SingleStream(self.manifest,payload)

    # Nearby valid framed2001/10001 prompts are accepted. Missing, duplicated,
    # reread, inexact and wrong-coordinate probes do not reduce to partial data.
    def test_single_grid_rejects_partial_reread_and_wrong_actual_depth(self):
        self.altered_single(lambda rs:None)
        for key,value in (('reread',True),('gen_tokens_exact',False),('prompt_n',99999),('depth',1000),('prompt_ms',float('nan'))):
            def mutate(rs):next(r for r in rs if r['kind']=='turn')[key]=value
            with self.subTest(key=key),self.assertRaises(InputGap):self.altered_single(mutate)
        with self.assertRaisesRegex(InputGap,'complete six-depth'):
            self.altered_single(lambda rs:rs.pop(next(i for i,r in enumerate(rs) if r['kind']=='turn')))

    # Interpolation is bounded by the adjacent measured deltas. Outside that
    # finite grid is an explicit endpoint hold, not a faster fabricated rate.
    def test_delta_surface_rejects_flat_bulk_rate_and_invalid_arguments(self):
        a=self.single.for_delta(140000,2000);b=self.single.for_delta(140000,10000)
        self.assertAlmostEqual(self.single.for_delta(140000,2343),a+(b-a)*343/8000)
        self.assertEqual(self.single.for_delta(140000,20000),b)
        self.assertEqual(self.single.for_delta(140000,1),self.single.for_delta(140000,512))
        for d,n in ((-1,512),(100000,-1),(float('nan'),512),(100000,float('inf'))):
            with self.subTest(d=d,n=n),self.assertRaises(InputGap):self.single.for_delta(d,n)

    # All old singleton anchors remain discoverable only as throttled history;
    # every multi-stream lookup keeps the interim flag, including extrapolation.
    def test_parallel_interim_cannot_become_a_final_anchor(self):
        cfg=r16.config()
        cfg['m3_parallel']=dict(mode='r15_interim',priority_basis='historical_background_priority_throttled',background_priority_interim=True)
        anchors=r16.M3Anchors(self.c.inputs.measured_json('normalized'),self.c.m3_depth_law,self.single,cfg)
        self.assertTrue(anchors.historical)
        for p in anchors.historical:self.assertIn('background priority and throttled',p['sensitivity'])
        for k,d in ((4,32784),(3,140000),(16,500000)):
            p=anchors.lookup(k,d);self.assertTrue(p['background_priority_interim'])
        self.assertFalse(anchors.lookup(1,100000)['background_priority_interim'])
        cfg['m3_parallel']['background_priority_interim']=False
        with self.assertRaisesRegex(InputGap,'cannot claim final'):r16.M3Anchors(self.c.inputs.measured_json('normalized'),self.c.m3_depth_law,self.single,cfg)

    # A synthetic fixture adds recorded-priority evidence to the old M3 sweep
    # solely to exercise the data-only replacement interface. Real R16b still
    # requires a hash-verified new archive. Unrecorded replacement is refused.
    def test_data_only_replacement_rejects_unrecorded_sweep(self):
        cfg=r16.config()
        # The synthetic source is always the frozen R15 grid, independently
        # of any real R16b archive subsequently selected by runtime data.
        grids=[dict(fragment='-scale'+str(depth)+'-largest-np'+str(np)+'-',depth=depth+16,server_np=np,counts=list(counts))
               for depth,np,counts in ((32768,32,(1,2,4,8,12,16,24,32)),(65536,32,(1,2,4,8,12,16,24,32)),(131072,16,(1,2,4,8,12,16)))]
        cfg['m3_parallel']=dict(mode='verified_sweep',priority_basis='recorded_normal_priority_PRI31',background_priority_interim=False,expected_device='Apple M3 Max',grids=grids)
        manifest,payload=old_package();manifest=dict(manifest);payload=dict(payload)
        with patch.object(r16,'package',return_value=(manifest,payload)):
            with self.assertRaisesRegex(InputGap,'recorded normal priority'):r16.M3Anchors(self.c.inputs.measured_json('normalized'),self.c.m3_depth_law,self.single,cfg)
        manifest.update(normal_priority=True,priority_override_used=False)
        payload['results/OPERATOR-READINESS.json']=self.payload['results/OPERATOR-READINESS.json']
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'calc/hybridcalc').glob('*.py')}
        real_package=r16.package
        def fixture(key,cfg=None):return (manifest,payload) if key=='m3_parallel' else real_package(key,cfg)
        with patch.object(r16,'package',side_effect=fixture):
            a=r16.M3Anchors(self.c.inputs.measured_json('normalized'),self.c.m3_depth_law,self.single,cfg)
        self.assertFalse(a.lookup(4,32784)['background_priority_interim'])
        expected=next(p['aggregate_tok_s'] for p in r16.cooled_points(payload,grids[0]['fragment'],32784,32,tuple(grids[0]['counts'])) if p['streams']==4)
        self.assertEqual(a.lookup(4,32784)['aggregate_tok_s'],expected)
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
        # A future archive can retire a background-only shape control. Every
        # removed quote keeps its original row and physical coordinates.
        import r16_audit
        old=ROOT/'calc/out/run15/base/parallel_server_shape_sensitivity.csv'
        with tempfile.TemporaryDirectory(prefix='future-shape-') as tmp:
            dest=Path(tmp)
            for variant in ('base','bounded_undo'):
                (dest/variant).mkdir();(dest/variant/old.name).write_text(old.read_text().splitlines()[0]+'\n')
            with patch.object(r16_audit,'OUT',dest):cells=r16_audit.changed_cells()
        records=list(csv.DictReader(io.StringIO(old.read_text())))
        self.assertEqual(len(cells),2*sum(len(r) for r in records))
        self.assertTrue(all(c['row']=='r15:0' and 'depth=131088' in c['coordinates'] for c in cells))

    # Actual interval arithmetic reproduces the13 three-round M5 medians and
    # largest fitting np16/8/4. The second np4 run cannot replace the base.
    def test_m5_cooled_sweep_rejects_wrong_np_mean_and_control_substitution(self):
        a=self.c.r16_m5;payload=r16.package('m5')[1]
        self.assertEqual(len(a.points),13)
        for p in a.points:
            rs=[r for r in rows(payload[p['source']]) if r['kind']=='round' and r['streams']==p['streams']]
            samples=[sum(q['predicted_n']-1 for q in r['requests'])/max(q['predicted_ms']/1000 for q in r['requests']) for r in rs]
            self.assertEqual(p['aggregate_tok_s'],sorted(samples)[1])
            self.assertEqual(p['server_np'],{32784:16,65552:8,131088:4}[p['depth']])
            self.assertEqual(p['priority_basis'],'owner_reported_normal_priority_not_recorded')
        self.assertAlmostEqual(a.decode(4,131088)*4,20.69,delta=.005)
        self.assertAlmostEqual(a.control['aggregate_tok_s'],23.76,delta=.01)
        self.assertNotEqual(a.control['aggregate_tok_s'],a.decode(4,131088)*4)
        cfg=r16.config()['m5'];bad=copy.deepcopy(cfg);bad['grids'][0]['server_np']=8
        with self.assertRaisesRegex(InputGap,'required largest-np'):r16.sweep(bad,*r16.package('m5'))

    # Missing rounds and uncooled/wrong-device sweeps are invalid even if a
    # summary row looks plausible. The real owner-reported sweep is accepted.
    def test_m5_sweep_rejects_partial_uncooled_and_wrong_device(self):
        cfg=r16.config()['m5'];manifest,payload=r16.package('m5')
        for mode in ('missing','uncooled','wrong_device'):
            bad=dict(payload);name,content=one_file(bad,cfg['grids'][0]['fragment']);rs=rows(content)
            if mode=='missing':rs.pop(next(i for i,r in enumerate(rs) if r['kind']=='round'))
            elif mode=='uncooled':next(r for r in rs if r['kind']=='meta')['cooldown_s']=0
            else:next(r for r in rs if r['kind']=='meta')['system']['machdep.cpu.brand_string']='Apple M3 Max'
            bad[name]='\n'.join(map(json.dumps,rs)).encode()
            with self.subTest(mode=mode),self.assertRaises(InputGap):r16.sweep(cfg,manifest,bad)

    # Raw archive/config identities are checked before reduction, including
    # gzip evidence; an unknown or wrong digest cannot bless supplied bytes.
    def test_source_hash_mismatch_refuses_admission(self):
        info=r16.config()['m3'];self.assertTrue(r16.checked(info))
        info['sha256']='0'*64
        with self.assertRaisesRegex(InputGap,'sha256 mismatch'):r16.checked(info)

    # The architecture comparison consumes the PRI31 delta surface, rather
    # than quietly retaining the attached script's old41.2tok/s scalar.
    def test_architecture_reference_rejects_old_background_scalar(self):
        from hybridcalc.paper_tables_r7 import R7,architecture_table
        s,i=load('paper-tables-r7-r16');r=R7(s,i);architecture_table(r)
        table=r.g.result('test')['tables'][0]
        expected=self.single.for_delta(i.get('r7.arch.reference_depth'),i.get('r7.arch.portion'))
        for row in table['rows']:
            self.assertEqual(row['reference_rate_tok_s'],expected)
            self.assertNotAlmostEqual(row['reference_rate_tok_s'],41.2,places=1)
        qwen=[row for row in table['rows'] if row['model']==r.g.resolve('r7.arch.models.qwen27.label').value]
        self.assertEqual({r['state_format']:r['fixed_mb'] for r in qwen},{'f32':157.0,'bf16':78.5})


class Run16ImportAndLink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,i=load('paper-tables-r16');cls.c=Context(s,i)

    # Conditional OLS matches all four fixed-delta probes, retaining the weak
    # marginal token coefficient. The old1.498s intercept cannot be doubled.
    def test_import_depth_rule_rejects_omitted_or_double_counted_term(self):
        intercept,slope,r2=r16.depth_fit()
        self.assertAlmostEqual(slope,0.00003464415395787945,places=16)
        self.assertAlmostEqual(intercept,.28530137981118364)
        self.assertGreater(r2,.9999)
        proto=r16.ClientImport();undo=r16.ClientImport('bounded_undo')
        for d in (2000,20000,50000,100000,200000):
            self.assertAlmostEqual(proto.at_depth(539,d),intercept+slope*d)
            self.assertAlmostEqual(undo.at_depth(539,d),intercept)
            self.assertAlmostEqual(proto.at_depth(539,d)-undo.at_depth(539,d),slope*d)
        self.assertEqual(r16.config()['import']['fit_r2'],.12)
        self.assertAlmostEqual(proto.fixed_s,.25905207981118364)
        for d,measured in r16.config()['import']['depth_points']:
            self.assertAlmostEqual(proto.at_depth(539,d),measured,delta=.01)
        self.assertGreater(1.498+.0000487*539+slope*2000-proto.at_depth(539,2000),1.2)

    # Missing depth and invalid inputs refuse explicitly rather than silently
    # using depth0. The real0-depth cold-import control remains valid.
    def test_import_rejects_missing_depth_negative_and_nonfinite_inputs(self):
        imp=r16.ClientImport();self.assertAlmostEqual(imp.at_depth(0,0),.25905207981118364)
        with self.assertRaisesRegex(InputGap,'conditioning depth required'):imp(539)
        for n,d in ((-1,0),(1,-1),(float('inf'),100),(539,float('nan'))):
            with self.subTest(n=n,d=d),self.assertRaises(InputGap):import_at(imp,n,d)
        with self.assertRaisesRegex(InputGap,'unknown import variant'):r16.ClientImport('fake')
        with self.assertRaisesRegex(InputGap,'positive measured depth slope'):r16.depth_fit([[0,1],[1,1],[2,1]])

    # The production route receives prefix depth and the delta-specific rate;
    # a depth0 callback or a fixed2000-token rate changes this observable wait.
    def test_route_rejects_depth_loss_and_flat_delta_rate(self):
        from hybridcalc.session_hosting import Migration,policy_with_reload
        from hybridcalc.performance import payload
        calls=[(100000,512,0,0),(140000,2343,0,0)];v=Migration([(0,0)]*2);v.catch_up='per_call'
        model=dict(r16.MODEL,kv=34816,wire_state=157000000)
        link=dict(bandwidth=100e9,goodput=1,latency=0)
        steps=policy_with_reload(calls,model,1e18,link,self.c.r16_single,v,self.c.client_import())
        for (d,n,_,_),step in zip(calls,steps):
            expected=n*(54e9+393216*d)/1e18+payload(n,34816,157000000)*8/100e9+.25905207981118364+n*.0000487+r16.depth_fit()[1]*d
            self.assertTrue(step[3]);self.assertAlmostEqual(step[0],expected)
            self.assertAlmostEqual(step[1],self.c.client_import().at_depth(n,d))

    # Each of36 threshold rows includes exactly one state plus delta KV. An
    # arbitrary link below/equal/above the threshold has the required verdict.
    def test_threshold_rejects_state_omission_bits_and_import_omission(self):
        records=r16.threshold_rows(self.c.r16_single,self.c.b300);self.assertEqual(len(records),36)
        for r in records:
            state=157000000 if r['state_format']=='f32' else 78500000
            self.assertEqual(r['wire_bytes'],state+34816*r['delta'])
            budget=r['local_prefill_s']-r['server_prefill_s']-r['import_s']-r['rtt_s']
            rate=r['break_even_downstream_mb_s']*1e6
            self.assertAlmostEqual(r['wire_bytes']/rate,budget)
            self.assertGreater(r['wire_bytes']/(rate*.99),budget)
            self.assertLess(r['wire_bytes']/(rate*1.01),budget)
        row=next(r for r in records if r['depth']==100000 and r['delta']==2343 and r['state_format']=='f32' and r['import_variant']=='prototype_depth')
        self.assertGreater(row['break_even_downstream_mb_s'],8.0)
        self.assertLess(row['break_even_downstream_mb_s'],8.1)
        self.assertFalse(row['offload_at_wifi_5_19_mb_s'])
        self.assertTrue(row['offload_at_5g_9_75_mb_s'])

    # A nonpositive compute/import budget has no finite link solution. Valid
    # adjacent budget1s still returns bytes/s; missing state is not accepted.
    def test_threshold_rejects_nonpositive_budget_and_zero_wire(self):
        self.assertEqual(r16.link_threshold(4,1,1,157000000,1),157000000)
        for args in ((3,1,1,157000000,1),(2,1,1,157000000,1),(4,1,1,0,1),(4,1,float('nan'),157000000,1)):
            with self.subTest(args=args),self.assertRaises(InputGap):r16.link_threshold(*args)

    # The preserved plans reproduce8.45 only with the source-backed15% entry
    # saving. Economic equality must not be confused with that routing gate.
    def test_preflight_check_rejects_confusing_entry_and_break_even(self):
        records=r16.preflight_rows(self.c.r16_single,self.c.b300)
        wifi=records[0];self.assertEqual(wifi['recorded_connected_offloads'],0)
        self.assertEqual(wifi['pri31_prototype_connected_offloads'],0)
        self.assertEqual(records[1]['recorded_connected_offloads'],2)
        self.assertEqual(wifi['facts_reported_entry_threshold_mb_s'],8.45)
        self.assertTrue(wifi['reported_threshold_reproduced'])
        self.assertAlmostEqual(wifi['policy_entry_threshold_mb_s'],8.45,delta=.005)
        self.assertAlmostEqual(wifi['policy_entry_local_fraction'],.85)
        self.assertNotAlmostEqual(wifi['policy_break_even_mb_s'],8.45,places=1)

    # Independently summing the enclosing snapshot events yields43.1/35.3/
    #483.3s. The original TTFT cannot masquerade as a production prediction.
    def test_growing_validation_rejects_instrumented_ttft_as_residual(self):
        records=r16.validation_rows(self.c.r16_single,self.c.b300)
        expected={0:(483.3,884.0),7:(43.1,33.7),31:(35.3,38.9)}
        for r in records:
            hybrid,local=expected[r['turn']]
            self.assertAlmostEqual(r['measured_residual_s'],hybrid,delta=.05)
            self.assertAlmostEqual(r['measured_local_ttft_s'],local,delta=.05)
            self.assertAlmostEqual(r['measured_ttft_s']-r['instrumentation_capture_s'],r['measured_residual_s'])
            self.assertIn('not production TTFT',r['basis']);self.assertIn('fidelity/checkpoint unmeasured',r['basis'])
            if r['turn']==0:self.assertGreater(r['measured_wire_bytes'],r['ideal_wire_bytes'])
            else:self.assertLess(abs(r['measured_wire_bytes']-r['ideal_wire_bytes']),100000)

    # A broken trace identity, duplicate/missing enclosing capture or negative
    # residual refuses before a comparison row can be published.
    def test_instrumentation_rejects_wrong_trace_or_capture_accounting(self):
        timing=r16.source_json('TIMING-EXTRACT.json.gz');instrument=r16.source_json('INSTRUMENTATION-TIMING-EXTRACT.json.gz')
        hybrid=next(r for r in timing['calls'] if r['arm']=='hybrid' and r['turn']==7)
        component=next(r for r in instrument['base_and_offload_call_components'] if r['turn']==7)
        self.assertAlmostEqual(r16.instrumentation_residual(timing,instrument,hybrid,component),43.07490087603219)
        for kind in ('trace','missing','outside','duration'):
            bad=copy.deepcopy(instrument)
            if kind=='trace':bad['trace_sha256']='0'*64
            else:
                index=next(i for i,r in enumerate(bad['node_snapshot_capture_events']) if r['turn']==7)
                if kind=='missing':bad['node_snapshot_capture_events'].pop(index)
                elif kind=='outside':bad['node_snapshot_capture_events'][index]['inside_call_ttft']=False
                else:bad['node_snapshot_capture_events'][index]['duration_seconds']=10000
            with self.subTest(kind=kind),self.assertRaises(InputGap):r16.instrumentation_residual(timing,bad,hybrid,component)


class Run16Exports(unittest.TestCase):
    # The prior608 files are compared to accepted Git objects, including file
    # sets and sidecars. New manifests must bind every file to current sources.
    def test_frozen_exports_reject_changed_bytes_or_stale_generator(self):
        from r16_audit import frozen,verify_tables
        self.assertEqual(sum(frozen().values()),608)
        self.assertGreater(verify_tables(),190)
        index=json.loads((ROOT/'calc/out/run16/INDEX.json').read_text())
        for name,digest in index['files'].items():self.assertEqual(hashlib.sha256((ROOT/'calc/out/run16'/name).read_bytes()).hexdigest(),digest)
        real=Path.read_bytes
        target=ROOT/'calc/out/paper/manifest.json'
        def damaged(p):return b'planted changed bytes' if p==target else real(p)
        with patch.object(Path,'read_bytes',damaged):
            with self.assertRaisesRegex(AssertionError,'changed historical bytes'):frozen()
        import r16_audit
        with patch.object(r16_audit,'accepted_generator_identity',return_value={}):
            with self.assertRaisesRegex(AssertionError,'stale generator'):verify_tables()

    # Deleting one coordinate-qualified changed cell cannot be covered by a
    # duplicate value at another row, table or sensitivity variant.
    def test_quote_ledger_rejects_deleted_cell_or_forged_coordinates(self):
        from r16_audit import read,verify_quote_coverage,changed_cells,cell_key
        ledger=read(ROOT/'calc/ENGINE-QUOTES-R16-261103.csv');count=verify_quote_coverage(ledger)
        self.assertGreater(count,1000)
        cell=next(c for c in changed_cells() if c['column']=='background_priority_interim');key=cell_key(cell)
        bad=[r for r in ledger if not (r['source']==cell['source'] and r['engine_key']==key)]
        with self.assertRaisesRegex(AssertionError,'unreported changed cells'):verify_quote_coverage(bad)
        for r in ledger:
            if r['source']==cell['source'] and r['engine_key']==key:r['engine_key']=key+'; forged=true'
        with self.assertRaisesRegex(AssertionError,'unreported changed cells'):verify_quote_coverage(ledger)

    # Every inherited table carries the conservative interim qualifier, and
    # both import variants are exported. No interim capacity is called final.
    def test_dependent_exports_reject_unqualified_agents_per_day(self):
        import r16_audit
        interim=r16_audit.accepted_config()['m3_parallel']['background_priority_interim']
        self.assertGreater(r16_audit.verify_qualification(),1000)
        for variant in ('base','bounded_undo'):
            for p in (ROOT/'calc/out/run16'/variant).glob('*.csv'):
                for r in csv.DictReader(io.StringIO(p.read_text())):
                    self.assertIn('background_priority_interim',r,p.name)
                    self.assertIn('capacity_status',r,p.name)
                    if p.name in ('client_agents_day.csv','client_sessions_day.csv'):
                        self.assertEqual(r['background_priority_interim'],str(interim))
                        if interim:self.assertIn('interim;',r['capacity_status'])
                        else:self.assertNotIn('interim;',r['capacity_status'])
            self.assertTrue((ROOT/'calc/out/run16'/variant/'state_link_threshold.csv').exists())
        real=r16_audit.read
        def missing(p):
            records=real(p)
            if p.name=='client_agents_day.csv':records[0].pop('background_priority_interim')
            return records
        with patch.object(r16_audit,'read',side_effect=missing):
            with self.assertRaisesRegex(AssertionError,'missing priority qualifier'):r16_audit.verify_qualification()


if __name__=='__main__':unittest.main()
