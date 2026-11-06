"""Run22 acceptance contracts: paired negatives and evidence-grounded controls."""
import copy
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.inputs import InputGap,ROOT
from hybridcalc import deep_r21 as deep, measurements_r16 as r16
from run22 import measurements as m, interfaces as i, api, economics as e, engine, sentences


def fixture():
    return dict(profile='existing_combined',scope_tier='measured_ladder',server='pro6000_fp8',billing='bought',client='m5max64',basis='owned',share=.2,
        cache_basis='98.1% aggregate allowance with1.9% billed misses, provider cache unverified',load='medium',full_calls_day=800,
        intensity_basis='typical medium load',transport='bf16',rate_basis='measured envelope interpolation; tails estimated',
        workload_scope='combined: share of calls whose shapes lie inside the common measured ladder 10885/39904 (27.28%); selected measured envelope10885/39904 (27.28%); normalized to 3360 calls/person-month; full unconditioned mix unsupported')


class Run22Policy(unittest.TestCase):
    # Default transport halves only the recurrent wire tensor, never resident
    # KV/state memory. Unknown formats are refused rather than made a new default.
    def test_bf16_default_refuses_unknown_and_preserves_f32_residency(self):
        self.assertEqual(m.wire(690),102469632)
        self.assertEqual(m.wire(690,'f32'),180916224)
        self.assertEqual(m.wire(2343,'f32')-m.wire(2343),78446592)
        self.assertEqual(e.Server('b300_fp8_kv').state,156893184)
        with self.assertRaisesRegex(InputGap,'explicit f32'):m.wire(690,'fp16')
        with self.assertRaises(InputGap):m.wire(-1)

    # Accepted paired scores do not establish answer identity:28/33 answers
    # differ from local. A substituted analysis is rejected by its source digest.
    def test_quality_refuses_answer_identity_and_substituted_analysis(self):
        rows=m.quality_rows();ruler=[r for r in rows if r['evidence'].startswith('bf16 RULER')]
        self.assertEqual([r['value']for r in ruler],[390,390])
        self.assertEqual({r['evidence']:r['answer_changes']for r in ruler},{'bf16 RULER8192':28,'bf16 RULER32768':33})
        original=Path.read_bytes
        def corrupt(path):
            return b'[]' if path.name=='bf16-8192-analysis.json' else original(path)
        with patch.object(Path,'read_bytes',corrupt),self.assertRaisesRegex(InputGap,'SHA256'):
            m.quality_rows()

    # Actual manifest/readiness samples admit this rerun. A fabricated priority
    # flag cannot mask a throttled server or override.
    def test_recorded_priority_refuses_throttled_sample_with_real_control(self):
        manifest,readiness,_=m.evidence('qwen')
        self.assertEqual(m.priority(manifest,readiness),35)
        bad=copy.deepcopy(readiness)
        next(row['servers'][0] for row in bad['samples'] if row.get('servers'))['pri']=4
        with self.assertRaisesRegex(InputGap,'PRI31'):m.priority(manifest,bad)
        bad=copy.deepcopy(manifest);bad['priority_override_used']=True
        with self.assertRaisesRegex(InputGap,'without overrides'):m.priority(bad,readiness)

    # The new curve reproduces raw elapsed time at the real start depth, and
    # refuses an impossible Glimmer context; nominal-depth labels aren't aliases.
    def test_new_ladder_refuses_native_overflow_with_raw_timing_control(self):
        _,_,files=m.evidence('qwen')
        turn=next(r for name,rows in files.items() if 'hybrid-bench' in name for r in rows if r.get('kind')=='turn' and r['level']==100000 and r['delta']==2000)
        mac=m.Mac()
        self.assertAlmostEqual(mac.prefill(turn['depth'],2000),turn['prompt_ms']/1000)
        self.assertEqual(turn['depth'],100640)
        self.assertNotEqual(mac.prefill(100000,2000),mac.prefill(turn['depth'],2000))
        glimmer=m.Mac('glimmer');self.assertGreater(glimmer.prefill(118000,2000),0)
        with self.assertRaisesRegex(InputGap,'context envelope'):glimmer.prefill(131000,512)
        m3=m.Mac('glimmer','m3max')
        self.assertAlmostEqual(m3.prefill(118000,512),512/66.9)
        measured=next(r for r in m.measurement_rows() if r['client']=='m3max' and r['depth']==118000 and r['delta']==512)
        self.assertEqual(measured['single_decode_tok_s'],9.01)
        self.assertIn('archive unavailable',measured['basis'])

    # Client depth batching is measured, server depth batching remains modelled
    # absent CSV. Unmeasured client stream counts cannot be invented.
    def test_client_batching_refuses_unmeasured_streams_with_depth_controls(self):
        q=m.Mac();g=m.Mac('glimmer')
        self.assertAlmostEqual(q.decode(16,32768)*16/q.decode(1,32768),62.727/23.108)
        self.assertAlmostEqual(q.decode(4,131072)*4/q.decode(1,131072),20.778/16.186)
        self.assertAlmostEqual(g.decode(8,129024)*8/g.decode(1,129024),46.938/19.863)
        self.assertIn('modelled',e.Server('b300_fp8_kv').decode(1000000,32)['basis'])
        with self.assertRaisesRegex(InputGap,'unmeasured'):q.decode(3,64000)

    # Server batching reads one weights copy and each session's complete KV;
    # a depth-flat gain or a capacity-exceeding PRO1M batch is forbidden.
    def test_server_decode_refuses_flat_gain_with_capacity_control(self):
        server=e.Server('b300_fp8_kv')
        shallow=server.decode(16000,32);deep_row=server.decode(1000000,32)
        self.assertLess(deep_row['gain'],shallow['gain'])
        self.assertLess(deep_row['gain'],2)
        self.assertEqual(deep_row['batch'],7)
        expected=7*8e12*.7/(27e9+7*(32768*1000000+156893184))
        self.assertAlmostEqual(deep_row['aggregate_tok_s'],expected)
        with self.assertRaisesRegex(InputGap,'complete session'):e.Server('pro6000_fp8').decode(1000000,1)

    # Low/zero measured hits increase price; they do not fail admission. A
    # three-call exploratory series cannot populate the production cache interface.
    def test_low_cache_is_priced_not_excluded_and_three_call_probe_refused(self):
        p=next(r for r in api.providers() if r['tag']=='chutes/fp8')
        self.assertEqual(api.admission(p,262144,99),[])
        row=dict(model=api.MODEL,tag=p['tag'],profile='existing_combined',input_tokens='1000',cached_tokens='0',
            series_calls='10',warm_calls='9',observed_at='2026-11-03T20:00:00Z',source='test repeated series')
        known={(api.MODEL,p['tag'])}
        measured=i.cache_rows([row],known)
        rows,selected=api.baseline((100000,2343,512),'existing_combined',262144,'same shapes',measured,scenarios=('snapshot_1d',))
        real=[x for x in rows if x['provider']==p['tag']]
        self.assertTrue(all(r['admitted'] for r in real))
        self.assertNotIn(('snapshot_1d','measured'),selected,'partial cache observations do not establish cohort cheapest/median')
        self.assertEqual(next(x['effective_usd_per_1000_calls']for x in real if x['cache_point']=='measured'),next(x['effective_usd_per_1000_calls']for x in real if x['cache_point']=='no_cache'))
        row['series_calls']='3';row['warm_calls']='2'
        with self.assertRaisesRegex(InputGap,'three-call probe'):i.cache_rows([row],known)

    # A common-window comparison never combines5m/30m/1d minima. Missing
    # provider observations stay disclosed, without snapshot backfill.
    def test_availability_refuses_mixed_windows_with_same_window_control(self):
        row=dict(model=api.MODEL,tag='phala',window_start='2026-10-31T00:00:00Z',window_end='2026-11-03T00:00:00Z',availability_percent='86',source='fixture')
        other=dict(row,tag='alibaba',availability_percent='96')
        known={(api.MODEL,x)for x in ('phala','alibaba')}
        values,window=i.availability_rows([row,other],known)
        self.assertEqual(values[api.MODEL,'alibaba'],96)
        self.assertEqual((window[1]-window[0]).days,3)
        other['window_start']='2026-11-02T00:00:00Z'
        with self.assertRaisesRegex(InputGap,'same stated window'):i.availability_rows([row,other],known)

    # A provider excluded by a snapshot1d window can pass a different, explicitly
    # named72h scenario. The without-Alibaba bound remains a separate cohort.
    def test_million_window_flip_and_without_alibaba_control(self):
        with self.assertRaisesRegex(InputGap,'generated answer'):
            api.baseline((1000000,690,762),'million',1000000,'invalid unreserved shape')
        rows,selected=api.baseline((1000000-690-762,690,762),'million',1000000,'fixed1M shape')
        choose=lambda scenario,tag:next(r for r in rows if r['availability_scenario']==scenario and r['provider']==tag and r['cache_point']=='owner_981')
        self.assertFalse(choose('snapshot_1d','alibaba')['admitted'])
        self.assertTrue(choose('analyst_72h_with_alibaba','alibaba')['admitted'])
        self.assertFalse(choose('analyst_72h_with_alibaba','phala')['admitted'])
        self.assertFalse(choose('analyst_72h_without_alibaba','alibaba')['admitted'])
        self.assertEqual(choose('analyst_72h_with_alibaba','novita')['availability_percent'],'')

    # The fixed task reserves the generated answer inside the advertised total
    # API window, reproducing R21's valid shape rather than a >1M request.
    def test_api_context_refuses_unreserved_answer_with_r21_shape_control(self):
        with self.assertRaisesRegex(InputGap,'generated answer'):
            api.baseline((1000000,690,762),'million',1000000,'unreserved')
        rows,selected=api.baseline((998548,690,762),'million',1000000,'R21 fixed task')
        self.assertTrue(all(r['mean_input_tokens']+r['mean_output_tokens']==1000000 for r in rows))
        self.assertAlmostEqual(selected['snapshot_1d','owner_981']['cheapest']*1000,54.715,places=3)

    # The anchored million-token threshold keeps identical import/rate budgets
    # in both transport arms; the120s estimate is a different sensitivity.
    def test_million_anchor_refuses_analyst_substitution_with_bf16_control(self):
        c=engine.context();server=e.Server('b300_fp8_kv')
        rows=engine.threshold_rows(c,{server.key:server},{})
        choose=lambda fmt,variant:next(r for r in rows if r['model']=='qwen' and r['client']=='m3max' and r['depth']==1000000 and r['transport']==fmt and r['link']=='historic_home_wifi_5_19' and r['rate_basis'].startswith(variant))
        # Link keys are source-defined; use the measured rate rather than a label alias.
        values=[r for r in rows if r['model']=='qwen' and r['client']=='m3max' and r['depth']==1000000 and r['bytes_s']==5190000]
        f=next(r for r in values if r['transport']=='f32' and r['rate_basis'].startswith('measured_anchor'))
        b=next(r for r in values if r['transport']=='bf16' and r['rate_basis'].startswith('measured_anchor'))
        a=next(r for r in values if r['transport']=='bf16' and r['rate_basis'].startswith('analyst'))
        self.assertAlmostEqual(f['threshold_MB_s'],5.283,places=3)
        self.assertAlmostEqual(b['threshold_MB_s']/f['threshold_MB_s'],102469632/180916224)
        self.assertNotEqual(b['local_prefill_s'],120)
        self.assertEqual(a['local_prefill_s'],120)
        self.assertEqual(b['import_s'],f['import_s'])

    # Service occupancy is divided by installed GPU time and is not advertised
    # as SM utilization. An impossible capacity result has no finite utilization.
    def test_utilization_refuses_finite_value_on_capacity_alarm(self):
        econ=object.__new__(e.Economics);econ.units={('pro6000_fp8','bought'):(1000,1)};econ.days=21;econ.hours=8
        row=dict(boxes=2,prefill_gpu_s_day=100,decode_overflow_gpu_s_day=0)
        v=econ.utilization('pro6000_fp8',5,100,row,'hybrid')
        self.assertAlmostEqual(v['service_utilization'],500/(2*8*3600))
        self.assertIn('not nvidia-smi',v['utilization_basis'])
        row['boxes']={'alarm':[]}
        self.assertEqual(econ.utilization('pro6000_fp8',5,100,row,'hybrid')['service_utilization'],'')

    # The existing tariff is USD per decimal TB, not per GB. Exercise both new
    # billing paths: one monthly TB costs$5; office transfer remains zero.
    def test_egress_refuses_gigabyte_tariff_with_dedicated_and_shared_controls(self):
        econ=object.__new__(e.Economics)
        econ.days=21;econ.hours=8;econ.load=1;econ.sessions=1
        econ.inputs=SimpleNamespace(get=lambda key:5 if key=='prices.egress' else 0)
        stat=dict(wire_bytes_call=1e12/21,client_capacity_day=1,gpu_s_call=0,offload_share=1)
        prepared=SimpleNamespace(stats=lambda *args:stat,profiles={name:dict(bytes_s=1e9)for name in ('engine_wan','office_gigabit')})
        econ.prepared={('pro6000_fp8','m5max64','measured_envelope'):prepared}
        base=dict(person_month=100,served_day=1,spill_share=0)
        with patch.object(e.old.Economics,'hybrid',return_value=base):
            rented=econ.hybrid('pro6000_fp8',1,1,'m5max64','owned','rented','measured_envelope')
            office=econ.hybrid('pro6000_fp8',1,1,'m5max64','owned','bought','measured_envelope')
        self.assertAlmostEqual(rented['egress_person_month'],5)
        self.assertAlmostEqual(rented['person_month'],105)
        self.assertEqual(office['egress_person_month'],0)
        econ.servers={'pro6000_fp8':SimpleNamespace(session_bytes=lambda depth:0)}
        econ.own_stats=lambda *args:dict(seconds=0)
        econ.units={('pro6000_fp8','rented'):(0,1)};econ.cfg=dict(reservation_depth=0)
        shared=econ.shared('pro6000_fp8',1,'m5max64','owned')
        self.assertAlmostEqual(shared['egress_person_month'],5)
        self.assertAlmostEqual(shared['person_month'],5)

    # Both sentence surfaces require their own link and every changing condition;
    # valid canonical and prose controls bind to the same source row.
    def test_words_ready_refuses_missing_link_with_long_and_short_controls(self):
        row=fixture()
        full=sentences.sentence(row,'hybrid costs $100')
        short=sentences.short_sentence(row,'hybrid costs $100')
        sentences.validate(full,row);sentences.validate_short(short,row)
        with self.assertRaisesRegex(AssertionError,'link'):
            sentences.validate(full.replace('link='+sentences.LINKS['bought']+'; ',''),row)
        with self.assertRaises(AssertionError):
            sentences.validate_short(short.replace(' (125 MB/s, RTT 1 ms)',''),row)
        for field in sentences.FIELDS:
            bad=re.sub(r'(?:^|; )'+re.escape(field)+r'=[^;]+;?','',full,count=1)
            with self.subTest(field=field),self.assertRaises(AssertionError):sentences.validate(bad,row)

    # Coverage names measured CALL SHAPES, not a fraction of work. Physical
    # extrapolation cannot be substituted for measured-ladder coverage.
    def test_coverage_refuses_workload_fraction_wording(self):
        row=fixture();text=sentences.sentence(row,'claim')
        sentences.validate(text,row)
        bad=text.replace('share of calls whose shapes lie inside the common measured ladder','quarter of the workload')
        with self.assertRaisesRegex(AssertionError,'coverage meaning'):sentences.validate(bad,row)

    # Both quote forms bind printed cost and utilization to their row, rather
    # than checking only the surrounding condition keywords.
    def test_sentence_refuses_changed_cost_with_numeric_positive_control(self):
        row=dict(fixture(),person_month=100,service_utilization=.125,calendar_utilization=.03)
        claim='team50 hybrid $100.00/person-month, service utilization12.50%'
        claim=claim.replace('utilization12','utilization 12')
        text=sentences.sentence(row,claim)
        sentences.validate(text,row)
        with self.assertRaisesRegex(AssertionError,'price'):
            sentences.validate(text.replace('$100.00','$101.00'),row)
        short=sentences.short_sentence(row,claim)
        sentences.validate_short(short,row)
        with self.assertRaisesRegex(AssertionError,'utilization'):
            sentences.validate_short(short.replace('12.50%','13.50%'),row)

    # Export projection refuses a forbidden server before writing paper files;
    # the same dedicated PRO row is a valid projection control.
    def test_paper_projection_refuses_5090_server_with_pro_control(self):
        from run22.export import paper_tables
        names=('small_team_cost','team_break_even','dedicated_multiples','shared_multiples','main_economics')
        tables={name:[fixture()] for name in names}
        self.assertEqual(paper_tables(tables)['small_team_cost'][0]['server'],'pro6000_fp8')
        tables['small_team_cost']=[dict(fixture(),server='rtx5090')]
        with self.assertRaisesRegex(AssertionError,'forbidden server'):paper_tables(tables)

    # A restored1.04M normal-priority observation can arrive without code edits;
    # a background-priority or un-restored sample cannot replace it.
    def test_mac_csv_refuses_unrestored_background_with_positive_control(self):
        row=dict(client='m3max',depth='1040000',delta='690',prefill_s='65',import_s='',decode_tok_s='',logits_kl='',
            priority='normal_priority',slot_restored='true',extension='yarn_factor4',observed_at='2026-11-03T23:00:00Z',source='fixture')
        self.assertEqual(i.mac_rows([row])['m3max',1040000,690]['prefill_s'],65)
        row['priority']='background_priority_interim'
        with self.assertRaisesRegex(InputGap,'normal priority'):i.mac_rows([row])
        row['priority']='normal_priority';row['slot_restored']='false'
        with self.assertRaisesRegex(InputGap,'restored'):i.mac_rows([row])

    # Accepted16k means16384, including the measured39-stream endpoint. The
    # sparse point cannot be copied to64k or used to invent40 resident sessions.
    def test_pro16k_measurement_refuses_deep_reuse_and_capacity_overrun(self):
        servers={k:e.Server(k)for k in deep.SERVERS}
        receipt=json.loads((m.DATA/'pro6000-decode-16384.json').read_text())
        fixed=[dict(server='pro6000_fp8',depth=receipt['depth'],streams=s['streams'],aggregate_tok_s=s['median']['aggregate_tok_s'],
            resident_limit=receipt['resident_limit'],engine='vllm',extension='native',source='accepted16k receipt fixture',observed_at='2026-11-03T19:35:00Z')for s in receipt['shapes']]
        parsed=i.server_rows(fixed,servers,'decode')
        pro=e.Server('pro6000_fp8',decode_observations=parsed)
        result=pro.decode(16384,39,parsed)
        self.assertAlmostEqual(result['aggregate_tok_s'],738.10,places=2)
        self.assertAlmostEqual(result['gain'],15.15,places=2)
        self.assertEqual(pro.slots(16384),39)
        self.assertIn('measured',result['basis'])
        self.assertIn('modelled',pro.decode(64000,32)['basis'])
        with self.assertRaisesRegex(InputGap,'cannot extrapolate'):
            pro.decode(64000,8,parsed)
        bad=copy.deepcopy(parsed);bad[-1]['streams']=40
        with self.assertRaisesRegex(InputGap,'resident capacity'):
            i.server_rows(bad,servers,'decode')
        # A resident cap belongs to the host/depth, even if another row omits it.
        bad[-1]['resident_limit']=''
        with self.assertRaisesRegex(InputGap,'resident capacity'):
            i.server_rows(bad,servers,'decode')
        self.assertEqual({r['depth'] for r in parsed},{16384})

    # Factor4 extends Qwen to1,048,576, not indefinitely. A physically resident
    # one-stream B300 observation at the exact boundary is the positive control.
    def test_decode_csv_refuses_beyond_yarn_window_with_boundary_control(self):
        servers={k:e.Server(k)for k in deep.SERVERS}
        row=dict(server='b300_fp8_kv',depth='1048576',streams='1',aggregate_tok_s='10',engine='vllm',
            extension='yarn_factor4',source='boundary fixture',observed_at='2026-11-03T22:00:00Z')
        self.assertEqual(i.server_rows([row],servers,'decode')[0]['depth'],1048576)
        row['depth']='1048577'
        with self.assertRaisesRegex(InputGap,'YaRN analysis envelope'):
            i.server_rows([row],servers,'decode')

    # Sparse deep server prefill feeds exact observed shapes without fabricating
    # other shapes; invalid engine/provenance or over-capacity measurements refuse.
    def test_server_csv_refuses_wrong_engine_with_measured_prefill_control(self):
        servers={k:e.Server(k)for k in deep.SERVERS}
        row=dict(server='b300_fp8_kv',depth='1000000',delta='2000',prefill_s='3',engine='vllm',extension='yarn_factor4',observed_at='2026-11-03T22:00:00Z',source='fixture')
        parsed=i.server_rows([row],servers,'prefill')
        measured=e.Server('b300_fp8_kv',observations=parsed)
        self.assertEqual(measured.cached(1000000,2000),3)
        second=dict(row,delta='10000',prefill_s='10')
        surface=e.Server('b300_fp8_kv',observations=i.server_rows([row,second],servers,'prefill'))
        self.assertAlmostEqual(surface.cached(1000000,690),3+(690-2000)*7/8000)
        row['engine']='llama_cpp'
        with self.assertRaisesRegex(InputGap,'vLLM'):i.server_rows([row],servers,'prefill')

    # Deep decode observations require their own single-stream reference and
    # physical resident capacity; an impossible32-stream1M result cannot enter.
    def test_decode_csv_refuses_impossible_batch_and_missing_yarn(self):
        servers={k:e.Server(k)for k in deep.SERVERS}
        row=dict(server='b300_fp8_kv',depth='1000000',streams='1',aggregate_tok_s='100',engine='vllm',extension='yarn_factor4',observed_at='2026-11-03T22:00:00Z',source='fixture')
        parsed=i.server_rows([row],servers,'decode')
        self.assertEqual(servers[row['server']].decode(1000000,1,parsed)['aggregate_tok_s'],100)
        row['streams']='32'
        with self.assertRaisesRegex(InputGap,'capacity'):i.server_rows([row],servers,'decode')
        row['streams']='1';row['extension']=''
        with self.assertRaisesRegex(InputGap,'YaRN'):i.server_rows([row],servers,'decode')

    # Actual GPU fill timings replace the old extrapolated resync, while the
    # smaller bf16 serialized payload remains explicitly an encoding estimate.
    def test_full_resync_refuses_measured_bf16_claim_with_f32_control(self):
        rows=engine.full_resync(None)
        f=next(r for r in rows if r['depth']==1040000 and r['transport']=='f32')
        b=next(r for r in rows if r['depth']==1040000 and r['transport']=='bf16')
        self.assertEqual(f['rebuild_s'],1813.77);self.assertEqual(f['wire_bytes'],36394654776)
        self.assertEqual(f['wire_bytes']-b['wire_bytes'],78446592)
        self.assertIn('encoding unmeasured',b['basis'])
        self.assertNotIn('measured bf16',b['basis'])

    # Only dedicated PRO6000/B300 server classes are offered; the historical
    # measured5090 client implementation remains outside this server exclusion.
    def test_server_refuses_5090_with_pro_b300_controls(self):
        self.assertEqual(e.Server('pro6000_fp8').engine,'vllm')
        self.assertEqual(e.Server('b300_fp8').engine,'vllm')
        with self.assertRaisesRegex(InputGap,'excludes5090'):e.Server('rtx5090')


class Run22Exports(unittest.TestCase):
    # Both costs in an idleness comparison name their own billing basis. A
    # shared-work label cannot silently stand for its dedicated bought column.
    def test_idleness_refuses_shared_label_on_dedicated_cost_with_control(self):
        from run22 import export
        self.assertGreater(export.verify()['historical_files'],900)
        original=export.read
        def wrong(path):
            values=original(path)
            return [dict(r,billing='shared_work')for r in values] if path==export.OUT/'idleness.csv' else values
        with patch.object(export,'read',side_effect=wrong),self.assertRaisesRegex(AssertionError,'billing mismatch'):
            export.verify()

    # Production verification checks recursive frozen bytes, quoted cells, both
    # sentence surfaces, utilization fields, and every paper server coordinate.
    def test_export_contracts_and_missing_quote_negative(self):
        from run22 import export
        self.assertGreater(export.verify()['historical_files'],900)
        original=export.read
        # Plant a missing entry in the real ledger read path, not a disconnected
        # fixture that would leave the production quote gate unexercised.
        def missing(path):
            values=original(path)
            return values[:-1] if path==export.LEDGER else values
        with patch.object(export,'read',side_effect=missing),self.assertRaisesRegex(AssertionError,'quote'):
            export.verify()


if __name__=='__main__':unittest.main()
