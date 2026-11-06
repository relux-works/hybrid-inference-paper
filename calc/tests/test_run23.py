"""Run23 measurements, forbidden substitutions and unchanged policy controls."""
import copy
import csv
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.inputs import InputGap
from hybridcalc import server_economics_r20 as s
from run22 import economics as previous, export as old_export
from run23 import economics as e, inputs, engine, routing, sentences, changes


def fixture():
    return dict(profile='claude_deep',scope_tier='measured_ladder',server='pro6000_fp8',billing='bought',client='m5max64',basis='owned',share=.2,
        cache_basis='98.1% aggregate allowance with1.9% billed misses, provider cache unverified',load='medium',full_calls_day=800,
        intensity_basis='typical medium load',transport='bf16',offload_share_max=0,
        workload_scope='Claude: share of calls whose shapes lie inside the common measured ladder 554/1000 (55.40%); selected measured envelope554/1000 (55.40%); normalized to 3360 calls/person-month; full unconditioned mix unsupported')


class Run23Policy(unittest.TestCase):
    # Accepted raw medians must bypass the model, even when callers pass no
    # sparse measurement list. All11 coordinates are grounded in the receipt.
    def test_measured_pro_point_never_replaced_by_model(self):
        server=e.Server('pro6000_fp8')
        receipt=json.loads((inputs.DATA/'pro-decode-receipt.json').read_text())
        with patch.object(previous.Server,'decode',side_effect=AssertionError('model used at measured point')):
            for depth in receipt['rows']:
                for shape in depth['shapes']:
                    result=server.decode(depth['depth'],shape['streams'])
                    self.assertEqual(result['aggregate_tok_s'],shape['median']['aggregate_tok_s'])
                    self.assertIn('measured PRO',result['basis'])
        self.assertIn('modelled',server.decode(512000,1)['basis'])

    # At an unmeasured batch the service-time interpolation stays inside measured
    # N endpoints; it cannot silently substitute a bandwidth curve.
    def test_pro_interpolation_refuses_model_fallback_with_service_time_control(self):
        server=e.Server('pro6000_fp8')
        one=server.decode(164000,1);maximum=server.decode(164000,5)
        expected=3/(1/one['aggregate_tok_s']+.5*(5/maximum['aggregate_tok_s']-1/one['aggregate_tok_s']))
        with patch.object(previous.Server,'decode',side_effect=AssertionError('unmeasured batch fell back to model')):
            middle=server.decode(164000,3)
            self.assertAlmostEqual(middle['aggregate_tok_s'],expected)
            self.assertIn('interpolated',middle['basis'])
            self.assertGreater(server.decode(100000,8)['aggregate_tok_s'],0)
        self.assertLess(middle['gain'],maximum['gain'])
        self.assertGreater(middle['gain'],1)

    # PRO measurements cannot leak into another GPU's service curve. The failed
    # B300 rental leaves precisely the prior model, while the PRO differs.
    def test_b300_refuses_pro_curve_reuse_with_model_control(self):
        for key in ('b300_fp8','b300_fp8_kv'):
            self.assertEqual(e.Server(key).decode(164000,8)['aggregate_tok_s'],previous.Server(key).decode(164000,8)['aggregate_tok_s'])
            self.assertIn('pending',e.Server(key).decode(164000,8)['basis'])
        self.assertNotEqual(e.Server('pro6000_fp8').decode(164000,5)['aggregate_tok_s'],previous.Server('pro6000_fp8').decode(164000,5)['aggregate_tok_s'])

    # Reciprocal residency interpolation follows space/session, not arithmetic
    # interpolation of session counts (which would incorrectly admit9 at100k).
    def test_residency_refuses_linear_count_overadmission_with_anchor_controls(self):
        server=e.Server('pro6000_fp8')
        self.assertEqual([server.slots(d)for d in (16384,65536,164000,256000)],[39,12,5,3])
        self.assertEqual(server.slots(100000),8)
        self.assertEqual(server.decode(100000,32)['batch'],8)
        self.assertNotEqual(server.slots(100000),9)

    # The actual fleet accounting must consume the measured8-stream64k rate;
    # publishing a new table while retaining the old model is not sufficient.
    def test_own_fleet_refuses_inert_measurement_with_accounting_control(self):
        context=engine.context();server=e.Server('pro6000_fp8');cfg=s.config()
        cfg['servers']={'pro6000_fp8':cfg['servers']['pro6000_fp8']};cfg['reservation_depth']=65536
        econ=e.Economics(context,[(63536,2000,512,8.1)],{'pro6000_fp8':server},cfg)
        with patch.object(previous.Server,'decode',side_effect=AssertionError('fleet used old decode model')):
            result=econ.fleet_stats(server,2,1,1)
        rate=190.28855418503053;pre=server.cached(63536,2000)
        expected=max(pre+512/rate,(pre+512/(rate/8)+8.1)/8)
        self.assertAlmostEqual(result['fleet_s_call'],expected)
        old_server=previous.Server('pro6000_fp8')
        self.assertNotAlmostEqual(rate,old_server.decode(65536,8)['aggregate_tok_s'])

    # Default-KV1M did not start, and an unavailable FP8-KV variant cannot make
    # it feasible. The B300 control still admits its modelled1M session.
    def test_pro_million_server_cannot_be_feasible(self):
        pro=e.Server('pro6000_fp8')
        for call in (lambda:pro.slots(1000000),lambda:pro.decode(1000000,1),lambda:pro.cached(1000000,690),lambda:pro.cold(1000000)):
            with self.assertRaisesRegex(InputGap,'61.97GiB.*56.62GiB'):call()
        self.assertGreater(e.Server('b300_fp8_kv').decode(1000000,1)['aggregate_tok_s'],0)
        cfg=s.config();cfg['servers']['pro6000_fp8']['variant']='fp8-kv'
        with self.assertRaisesRegex(InputGap,'FP8 KV did not start'):
            e.Server('pro6000_fp8',cfg,decode_observations=[])

    # Routing refuses the impossible server before assigning any remote time or
    # finite threshold, even though a local timing observation exists.
    def test_pro_million_routing_refuses_finite_remote_time_with_control(self):
        rows=routing.threshold_rows(engine.context(),{'pro6000_fp8':e.Server('pro6000_fp8')},{})
        impossible=[r for r in rows if r['server']=='pro6000_fp8'and r['depth']>=1000000]
        self.assertTrue(impossible)
        self.assertTrue(all(not r['feasible']and not r['offload']and r['threshold_MB_s']==''and r['remote_s']==''for r in impossible))
        self.assertTrue(any(r['feasible']for r in rows if r['server']=='pro6000_fp8'and r['depth']==100000))

    # Native prefill excludes the per-round restore. Both measured times enter
    # once, and the1.04M observation is not called a direct1M measurement.
    def test_mac_prefill_refuses_double_restore_with_measured_threshold_control(self):
        server=e.Server('b300_fp8_kv')
        rows=routing.threshold_rows(engine.context(),{server.key:server},{})
        choose=lambda fmt,depth:next(r for r in rows if r['server']==server.key and r['client']=='m3max'and r['depth']==depth and r['delta']==690 and r['transport']==fmt and float(r['bytes_s'])==5190000 and r['primary'])
        b=choose('bf16',1040000);f=choose('f32',1040000);proxy=choose('bf16',1000000)
        self.assertEqual(b['local_prefill_s'],72.408)
        self.assertEqual(b['recovery_s'],40.479)
        self.assertEqual(b['recovery_kind'],'full_slot_restore_proxy')
        self.assertEqual(proxy['measurement_depth'],1040000)
        self.assertIn('proxy at1M',proxy['rate_basis'])
        expected=72.408-server.cached(1040000,690,'measured_envelope')-40.479-.126
        self.assertAlmostEqual(b['threshold_MB_s'],102469632/expected/1e6)
        self.assertAlmostEqual(f['threshold_MB_s']/b['threshold_MB_s'],180916224/102469632)
        analyst=next(r for r in rows if r['server']==server.key and r['client']=='m3max'and r['depth']==1000000 and r['rate_basis'].startswith('analyst'))
        self.assertEqual(analyst['local_prefill_s'],120);self.assertFalse(analyst['primary'])

    # The shape that overflows the native window must stay refused; a new CSV
    # must not turn its absent timing into a fabricated measured number.
    def test_mac_context_refusal_cannot_become_a_prefill_with_valid_control(self):
        self.assertEqual(inputs.mac_rows()[524288,10000]['prefill_s'],843.260)
        records=inputs.rows('mac_direct');bad=copy.deepcopy(records)
        row=next(r for r in bad if r['depth']=='1040000'and r['delta']=='10000')
        row['prefill_s']='1000';row['status']='measured'
        with self.assertRaisesRegex(InputGap,'context refusal'):
            inputs.mac_rows(bad)

    # Warm storage and the raised, uncalibrated gate are material conditions;
    # stripping either the earlier refusal or cache state must refuse ingestion.
    def test_mac_provenance_refuses_hidden_gate_and_cache_with_control(self):
        good=inputs.rows('mac_direct');self.assertEqual(len(inputs.mac_rows(good)),6)
        for field,value,reason in [('earlier_refusal','','both the earlier'),('cache_state','cold','warm/no-purge'),('recovery_kind','delta_import','full-slot restore')]:
            bad=copy.deepcopy(good);bad[0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(InputGap,reason):inputs.mac_rows(bad)

    # At512k first and warm restores are distinct observations, not a generic
    # cold/warm benchmark; the first-restore sensitivity has a higher threshold.
    def test_first_restore_is_not_warm_median_or_purged_cold(self):
        server=e.Server('b300_fp8_kv');rows=routing.threshold_rows(engine.context(),{server.key:server},{})
        selected=[r for r in rows if r['client']=='m3max'and r['depth']==524288 and r['delta']==690 and r['transport']=='bf16'and float(r['bytes_s'])==5190000]
        warm=next(r for r in selected if r['primary']);first=next(r for r in selected if not r['primary'])
        self.assertEqual(warm['recovery_s'],2.965);self.assertEqual(first['recovery_s'],20.523)
        self.assertGreater(first['threshold_MB_s'],warm['threshold_MB_s'])
        self.assertIn('not a purged cold',first['rate_basis'])

    # A loopback CUDA import cannot replace a Metal recovery; component medians
    # are context alongside the unchanged aggregate bridge envelope.
    def test_cuda_bridge_cannot_replace_mac_restore_with_context_control(self):
        rows=inputs.bridge_rows();row=next(r for r in rows if r['depth']==16384 and r['delta']==2343)
        self.assertAlmostEqual(row['import_ms'],349.02931191027164)
        self.assertEqual(row['client'],'cuda');self.assertIn('context only',row['use'])
        mac=inputs.mac_rows()[1040000,690]
        self.assertNotAlmostEqual(mac['restore_warm_s'],row['import_ms']/1000)

    # Accepted reviewer note: zero-offload crossings are local work plus the
    # residency/overflow costs, and cannot be quoted as an offload benefit.
    def test_zero_offload_sentence_refuses_missing_disclosure_with_control(self):
        row=fixture();text=sentences.sentence(row,'no crossing');short=sentences.short_sentence(row,'no crossing')
        sentences.validate(text,row);sentences.validate_short(short,row)
        for value,validator in ((text,sentences.validate),(short,sentences.validate_short)):
            with self.assertRaisesRegex(AssertionError,'zero-offload'):
                validator(value.replace(sentences.zero_offload(row),''),row)
        row['offload_share_max']=.5
        sentences.validate(sentences.sentence(row,'crossing'),row)

    # A capacity alarm has no finite offload fraction and cannot masquerade as
    # a zero-offload local-only observation. The genuine zero remains labelled.
    def test_capacity_alarm_refuses_zero_offload_classification_with_control(self):
        row=fixture();self.assertTrue(sentences.zero_offload(row))
        row['offload_share_max']=dict(alarm=[dict(input='fixture',reason='no finite fleet')])
        text=sentences.sentence(row,'capacity alarm: no finite cost')
        self.assertNotIn('Zero prefill offload',text)
        self.assertIn('capacity alarm',text);sentences.validate(text,row)

    # Like-for-like comparison matches coordinates, not row order. A duplicate
    # coordinate is rejected instead of quietly overwriting a changed price.
    def test_comparison_refuses_duplicate_coordinate_with_cell_delta_control(self):
        row=fixture();row['reference']='own_cluster'
        keyed=changes.index('team_break_even',[row])
        self.assertEqual(len(keyed),1)
        with self.assertRaisesRegex(AssertionError,'duplicate comparison'):
            changes.index('team_break_even',[row,row])
        record=changes.cell('main_economics',('fixture',),'person_month','10','12',0,1)
        self.assertEqual(record['absolute_delta'],2);self.assertAlmostEqual(record['percent_delta'],20)


class Run23Exports(unittest.TestCase):
    # A successful export-health status must not hide a native context refusal.
    # Raw inputs are the independent control; the published read-path plant must
    # reject a fabricated measured disposition without changing numerical cells.
    def test_native_context_refusal_status_cannot_be_overwritten_by_export_health(self):
        from run23 import export
        self.assertEqual(export.verify()['historical_files'],1014)
        original=export.read
        def overwritten(path):
            rows=original(path)
            if path==export.OUT/'mac_direct_measurements.csv':
                next(r for r in rows if r['depth']=='1040000'and r['delta']=='10000')['measurement_status']='measured'
            return rows
        with patch.object(export,'read',overwritten),self.assertRaisesRegex(AssertionError,'native Mac context refusal'):
            export.verify()


    # Audits exercise published read paths: historical bytes, semantic changes,
    # measured protocol labels and no feasible1M PRO server.
    def test_published_audit_and_missing_abstract_quote_negative(self):
        from run23 import export
        self.assertEqual(export.verify()['historical_files'],1014)
        original=export.read
        def missing(path):
            values=original(path)
            if path==export.LEDGER:
                selected=next(i for i,r in enumerate(values)if r['source'].endswith('/abstract_bound_changes.csv'))
                return values[:selected]+values[selected+1:]
            return values
        with patch.object(export,'read',missing),self.assertRaisesRegex(AssertionError,'quote'):
            export.verify()

    # A planted feasible1M PRO row in the production read path is rejected;
    # the untouched committed export is the positive control.
    def test_export_refuses_feasible_pro_million_row_with_published_control(self):
        from run23 import export
        self.assertEqual(export.verify()['historical_files'],1014)
        original=export.read
        def feasible(path):
            rows=original(path)
            if path==export.OUT/'link_thresholds.csv':
                for row in rows:
                    if row['server']=='pro6000_fp8'and row['depth']=='1000000':row['feasible']='True'
            return rows
        with patch.object(export,'read',feasible),self.assertRaisesRegex(AssertionError,'impossible PRO1M'):
            export.verify()


if __name__=='__main__':unittest.main()
