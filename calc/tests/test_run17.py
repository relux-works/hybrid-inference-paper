"""Run17 named contract witnesses with valid controls beside forbidden outcomes."""
import copy
import csv
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc import measurements_r17 as r17
from hybridcalc import measurements_r16 as r16
from hybridcalc.inputs import InputGap, ROOT
from hybridcalc.engine import load, run
from hybridcalc.paper_tables import Context


class Run17Contracts(unittest.TestCase):
    # Tensor geometry rejects stale half-sized Gemma KV and allocated slot
    # storage as the live window. All three measured geometries are controls.
    def test_geometry_rejects_half_gemma_kv_and_wrong_window(self):
        for m in r17.MODELS:self.assertEqual(r17.geometry(m)['model'],m)
        _,p=r17.package('gemma31_server')
        for key,value in (('kv_bytes_per_token',21760),('sliding_window_bytes',668467200)):
            bad=dict(p);g=json.loads(p['results/model-geometry.json']);g[key]=value
            bad['results/model-geometry.json']=json.dumps(g).encode()
            with self.subTest(key=key),self.assertRaisesRegex(InputGap,'geometry disagrees|window byte product'):
                r17.geometry('gemma31',bad)

    # Reconcile every measured full-save row including16B/position metadata;
    # neither these observations nor the fitted intercept are delta transport.
    def test_sequence_save_rejects_missing_metadata_and_damaged_rows(self):
        for m,fixed in (('glimmer30',25900),('gemma31',13804)):
            records=r17.geometry_rows(m);self.assertEqual(len(records),3)
            for r in records:
                self.assertEqual(r['residual_bytes'],0)
                self.assertEqual(r['sequence_metadata_bytes'],16*r['depth']+fixed)
                self.assertNotEqual(r['estimated_tensor_bytes'],r['measured_sequence_bytes'])
            _,p=r17.package(m+'_server');bad=dict(p)
            name=next(n for n in p if 'delta-geometry-' in n and n.endswith('.json'))
            d=json.loads(p[name]);d['samples'][1]['bytes']+=1;bad[name]=json.dumps(d).encode()
            with self.assertRaisesRegex(InputGap,'reconciliation failed'):r17.geometry_rows(m,bad)

    # A small delta still exports the whole live window. Short cold prefixes
    # saturate atW; no full historical attention prefix is retransferred.
    def test_offload_rejects_delta_only_window_and_full_prefix_charge(self):
        for m,k,w,W in (('glimmer30',7072,21216,2048),('gemma31',43520,435200,1024)):
            g=r17.geometry(m)
            for delta in r17.DELTAS:
                self.assertEqual(r17.offload_bytes(g,delta,100000),k*delta+w*W)
                self.assertEqual(r17.offload_bytes(g,delta,32000),k*delta+w*W)
            self.assertEqual(r17.offload_bytes(g,5,0),5*(k+w))
            self.assertEqual(r17.offload_bytes(g,5,W-5),5*k+W*w)
            self.assertNotEqual(r17.offload_bytes(g,512,100000),512*(k+w))

    # Native admission is prefix+delta; negative/fractional/nonfinite tokens,
    # unsupported state formats and cross-model bf16 cannot become payloads.
    def test_offload_rejects_context_overflow_and_invalid_coordinates(self):
        g=r17.geometry('glimmer30');self.assertGreater(r17.offload_bytes(g,512,131072-512),0)
        for n,d in ((512,131072),(-1,0),(0,-1),(.5,1),(float('nan'),0),(1,float('inf'))):
            with self.subTest(n=n,d=d),self.assertRaises(InputGap):r17.offload_bytes(g,n,d)
        for fmt in ('bf16','f16'):
            with self.assertRaisesRegex(InputGap,'unsupported state format'):r17.offload_bytes(g,512,100000,fmt)

    # Only Qwen recurrent tensors halve; KV and full f32 import time do not.
    def test_bf16_rejects_halving_whole_wire_and_rounded_state(self):
        g=r17.geometry('qwen27')
        for delta in r17.DELTAS:
            a=r17.offload_bytes(g,delta,100000);b=r17.offload_bytes(g,delta,100000,'bf16')
            self.assertEqual(a-b,78446592)
            self.assertEqual(b,34816*delta+78446592)
            self.assertNotEqual(b,a/2)
            self.assertNotEqual(a,34816*delta+157000000)

    def altered_surface(self,model,change):
        manifest,p=r17.package(model+'_mac');p=dict(p)
        n=next(n for n in p if '-'+model+'-' in n and n.endswith('.jsonl'))
        rs=[json.loads(line) for line in p[n].splitlines()];change(rs)
        p[n]='\n'.join(map(json.dumps,rs)).encode()
        return r17.Surface(model,'mac',evidence=(manifest,p))

    # The full real grids pass. Rereads, short generation, wrong actual depth,
    # invalid timing, wrong device and incomplete grids fail before reduction.
    def test_rates_reject_reread_partial_wrong_depth_and_device(self):
        self.altered_surface('gemma31',lambda rs:None)
        for key,value in (('reread',True),('predicted_n',127),('depth',16001),('prompt_ms',0),('prompt_ms',float('nan'))):
            def change(rs):next(r for r in rs if r['kind']=='turn')[key]=value
            with self.subTest(key=key),self.assertRaises(InputGap):self.altered_surface('gemma31',change)
        with self.assertRaisesRegex(InputGap,'complete depth/delta'):
            self.altered_surface('glimmer30',lambda rs:rs.pop(next(i for i,r in enumerate(rs) if r['kind']=='turn')))
        with self.assertRaisesRegex(InputGap,'model identity'):
            self.altered_surface('glimmer30',lambda rs:rs[0].update({'machdep.cpu.brand_string':'Apple M5 Max'}))

    # Linear interpolation uses both delta and depth axes; rates outside the
    # finite measured envelope refuse instead of inventing a native-depth rate.
    def test_surface_rejects_flat_delta_and_unmeasured_grid(self):
        s=r17.Surface('glimmer30','mac')
        expected=(s.rates[50000,2000]+(s.rates[50000,10000]-s.rates[50000,2000])*343/8000)
        expected2=(s.rates[100000,2000]+(s.rates[100000,10000]-s.rates[100000,2000])*343/8000)
        self.assertAlmostEqual(s.for_delta(64000,2343),expected+(expected2-expected)*14000/50000)
        self.assertNotEqual(s.for_delta(64000,2343),s.for_delta(64000,512))
        for d,n in ((120000,512),(15000,512),(32000,511),(32000,10001)):
            with self.assertRaisesRegex(InputGap,'outside measured'):s.for_delta(d,n)

    # A data-only Mac source/mode swap admits a recorded PRI31 fixture.
    # Labelling background evidence as PRI31 fails; real future data is needed.
    def test_mac_data_only_interface_rejects_unrecorded_priority(self):
        for model in ('glimmer30','gemma31'):
            cfg=r17.config();manifest,p=r17.package(model+'_mac');p=dict(p)
            self.assertTrue(r17.Surface(model,'mac').interim)
            cfg['mac'][model].update(mode='verified_pri31',background_priority_interim=False,priority_basis='recorded_normal_priority_PRI31')
            with self.assertRaisesRegex(InputGap,'recorded normal priority'):
                r17.Surface(model,'mac',cfg,(manifest,p))
            # Synthetic evidence only: no assertion of an actual PRI31 run.
            manifest=dict(manifest,normal_priority=True,priority_override_used=False)
            p={n:b for n,b in p.items() if 'OPERATOR-READINESS' not in n}
            p['results/OPERATOR-READINESS.json']=r16.package('m3')[1][next(n for n in r16.package('m3')[1] if 'OPERATOR-READINESS' in n and n.endswith('.json'))]
            accepted=r17.Surface(model,'mac',cfg,(manifest,p));self.assertFalse(accepted.interim)
            self.assertEqual(accepted.for_delta(100000,2343),r17.Surface(model,'mac').for_delta(100000,2343))
            cfg['mac'][model].update(mode='background_interim')
            with self.assertRaisesRegex(InputGap,'cannot claim final'):r17.Surface(model,'mac',cfg,(manifest,p))

    # The unchanged R16b config selects parallel rates in a Run17 Context;
    # a recorded synthetic fixture passes, the same unrecorded sweep refuses.
    def test_r16b_parallel_interface_rejects_unrecorded_run17_replacement(self):
        from hybridcalc.measurements_r15 import package as old_package
        cfg=r16.config();info=cfg['m3_parallel']
        info.update(mode='verified_sweep',priority_basis='recorded_normal_priority_PRI31',background_priority_interim=False)
        manifest,p=old_package();p=dict(p)
        original=r16.package
        def fixture(key,cfg=None):return (manifest,p) if key=='m3_parallel' else original(key,cfg)
        with patch.object(r16,'config',return_value=cfg),patch.object(r16,'package',side_effect=fixture):
            with self.assertRaisesRegex(InputGap,'recorded normal priority'):Context(*load('paper-tables-r17'))
            manifest=dict(manifest,normal_priority=True,priority_override_used=False)
            p={n:b for n,b in p.items() if 'OPERATOR-READINESS' not in n}
            p['results/OPERATOR-READINESS.json']=original('m3')[1][next(n for n in original('m3')[1] if 'OPERATOR-READINESS' in n and n.endswith('.json'))]
            c=Context(*load('paper-tables-r17'))
            self.assertFalse(c.parallel.lookup(4,32784)['background_priority_interim'])
            self.assertEqual(c.g.resolve(c.wire_state).value,156893184)

    # Archive digests are checked before rates/geometry are trusted.
    def test_source_admission_rejects_wrong_hash(self):
        cfg=r17.config();self.assertTrue(r17.package('glimmer30_server',cfg)[1])
        cfg['sources']['glimmer30_server']['sha256']='0'*64
        with self.assertRaisesRegex(InputGap,'archive sha256 mismatch'):r17.package('glimmer30_server',cfg)

    # Raw server reductions reproduce every rounded FACTS1a delta/decode cell;
    # the old c21284cd Qwen rate must not substitute for the new build.
    def test_server_facts_rejects_previous_build_rates(self):
        expected={
            'qwen27':((3876,3909,3778,63.8),(2653,2716,2657,57.3),(1807,1767,1888,49.6),
                      (1382,1345,1477,43.5),(1111,1097,1214,38.4),(950,925,1035,34.5)),
            'gemma31':((3025,2977,2684,56.0),(1614,1633,1560,44.1),(1019,1039,1018,33.5),
                       (746,767,761,27.0),(593,613,610,22.6),(492,511,511,19.5)),
            'glimmer30':((4042,4171,4221,73.4),(3378,3616,3712,68.1),(2725,3015,3126,61.6),(2531,2823,2936,59.4))}
        for model,grid in expected.items():
            s=r17.Surface(model,'server')
            for d,values in zip(s.depths,grid):
                for n,value in zip(r16.DELTAS,values):
                    self.assertAlmostEqual(s.for_delta(d,n),value,delta=.6)
                decode=sum(r['predicted_n']*1000/r['predicted_ms'] for r in s.turns if r['level']==d)/3
                self.assertAlmostEqual(decode,values[-1],delta=.06)
        self.assertNotAlmostEqual(r17.Surface('qwen27','server').for_delta(16000,2000),3547,delta=100)

    # All36 thresholds use correct bytes and all serial latency components.
    # Below/equal/above thresholds produce lose/tie/win, with bits conversion.
    def test_threshold_rejects_omitted_window_import_rtt_and_bits(self):
        rs=r17.threshold_rows();self.assertEqual(len(rs),36)
        for r in rs:
            speed=r['break_even_downstream_mb_s']*1e6
            base=r['server_prefill_s']+r['import_s']+r['rtt_s']
            self.assertAlmostEqual(base+r['wire_bytes']/speed,r['local_prefill_s'])
            self.assertGreater(base+r['wire_bytes']/(speed*.99),r['local_prefill_s'])
            self.assertLess(base+r['wire_bytes']/(speed*1.01),r['local_prefill_s'])
            self.assertEqual(r['break_even_downstream_mbit_s'],8*r['break_even_downstream_mb_s'])
            self.assertEqual(r['background_priority_interim'],r['model']!='qwen27')
            self.assertEqual(r['import_s'],r16.ClientImport().at_depth(r['delta'],r['depth']))
        self.assertGreater(r16.link_threshold(10,1,1,100,1),0)
        with self.assertRaisesRegex(InputGap,'no finite downstream'):r16.link_threshold(3,1,1,100,1)

    # S=0 retains K*delta, MB is decimal and KiB is binary; every row states
    # the extrapolation and holds Qwen rates/import fixed, not model speedups.
    def test_extrapolation_rejects_unit_mix_and_model_claim(self):
        rs=r17.extrapolation_rows();self.assertEqual(len(rs),15)
        for r in rs:
            self.assertEqual(r['wire_bytes'],r['fixed_mb']*1000000+r['kv_kib_token']*1024*2343)
            self.assertIn('not a model claim',r['basis'])
        self.assertGreater(rs[0]['wire_bytes'],0)
        self.assertEqual(len({r['import_s'] for r in rs}),1)
        self.assertLess(rs[0]['break_even_downstream_mb_s'],rs[-1]['break_even_downstream_mb_s'])

    # Wire-only bf16 does not double client residency or decode capacity.
    # Both paired scenarios feed the actual policy wire node, not just labels.
    def test_economics_rejects_resident_halving_and_wire_label_only(self):
        cs=[]
        for name in ('paper-tables-r17','paper-tables-r17-bf16'):
            s,i=load(name);cs.append(Context(s,i))
        states=[c.g.resolve(c.state).value for c in cs]
        self.assertEqual(states[0],states[1]);self.assertEqual(states[0],157000000)
        for c,expected in zip(cs,(156893184,78446592)):
            self.assertEqual(c.g.resolve(c.wire_state).value,expected)
            c.client('m3max',c.positions('paper_tables.links')[0],'test')
            # Locate the actual dependency instead of duplicating the policy.
            matches=[k for k in c.g.nodes if k.endswith('.wire') and '.client.' in k]
            self.assertTrue(matches)
            self.assertEqual(c.g.resolve(matches[0]).value['wire_state'],expected)
        cfg=r17.config();cfg['qwen_state_bytes']=0
        with patch.object(r17,'config',return_value=cfg):
            # A missing state must be rejected by the configure contract.
            with self.assertRaises(InputGap):Context(*load('paper-tables-r17'))

    # Per-offload savings apply to transfer/egress only; import has no measured
    # bf16 speedup. Re-routing may increase total monthly egress, so not pinned.
    def test_sensitivity_rejects_total_wire_half_and_missing_pending_label(self):
        rs=r17.sensitivity_rows();self.assertEqual(len(rs),54)
        for a in [r for r in rs if r['state_format']=='f32']:
            b=next(r for r in rs if all(r[k]==a[k] for k in ('depth','delta','downstream_mb_s')) and r['state_format']=='bf16')
            self.assertAlmostEqual(a['transfer_s']-b['transfer_s'],78446592/a['downstream_mb_s']/1e6)
            self.assertAlmostEqual(a['egress_usd']-b['egress_usd'],78446592/1e9*.02)
            self.assertIn('pending measured quality of dev-a r38',b['state_quality'])
            self.assertNotEqual(b['wire_bytes'],a['wire_bytes']/2)


class Run17Artifacts(unittest.TestCase):
    # Audit hashes against accepted R16 and current generators; a bounded byte
    # plant must fail without editing any real historical or generated file.
    def test_exports_reject_mutated_frozen_or_current_bytes(self):
        import r17_audit as audit
        self.assertGreater(audit.frozen(),800)
        self.assertGreater(audit.verify_tables(),80)
        real=Path.read_bytes
        for target,claim in ((ROOT/'calc/out/run16/base/client_sessions_day.csv','changed historical bytes'),
                             (audit.OUT/'architectures/architecture_link_threshold.csv','changed export bytes')):
            def damaged(p):return b'bounded planted corruption' if p==target else real(p)
            with patch.object(Path,'read_bytes',damaged),self.assertRaisesRegex(AssertionError,claim):
                (audit.frozen if 'run16' in str(target) else audit.verify_tables)()

    # A deleted or forged coordinate cannot be covered by an equal number
    # elsewhere in the complete changed-cell ledger.
    def test_quotes_reject_deleted_and_forged_cells(self):
        import r17_audit as audit
        records=audit.read(audit.LEDGER);self.assertGreater(audit.verify_quotes(records),1000)
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(records[1:])
        bad=copy.deepcopy(records);bad[0]['engine_key']+='; forged=true'
        with self.assertRaisesRegex(AssertionError,'unreported or forged'):audit.verify_quotes(bad)

    # Both client and economics exports are actual recomputations. Local
    # capacity/decode stay fixed; every bf16 row keeps the pending-quality gate.
    def test_exported_bf16_rejects_label_only_sensitivity(self):
        import r17_audit as audit
        for table in ('client_sessions_day.csv','person_cost_s20.csv','traffic_user_month.csv'):
            a=audit.read(audit.OUT/'f32'/table);b=audit.read(audit.OUT/'bf16'/table)
            self.assertEqual(len(a),len(b))
            self.assertTrue(any(x!=y for r,s in zip(a,b) for k,x in r.items() for y in [s.get(k)]
                                if k not in ('wire_state_format','state_quality')))
            for r,s in zip(a,b):
                self.assertEqual(s['wire_state_format'],'bf16')
                self.assertIn('pending measured quality of dev-a r38',s['state_quality'])
                if 'local' in r:self.assertEqual(r['local'],s['local'])


if __name__=='__main__':unittest.main()
