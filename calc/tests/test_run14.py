"""Measured run14 consumers, refusal witnesses and nearby accepted controls."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap, DATA, ROOT
from hybridcalc.measurements_r13 import verified_archive
from hybridcalc.measurements_r14 import ParallelAnchors, B300Measurements, b300_vllm_rates, package, one_file, aggregate_round, day_bounds
import hybridcalc.measurements_r14 as measured
from hybridcalc.server_prefill import compute_at,fit
from hybridcalc.paper_tables import Context, end_memory
from hybridcalc.paper import throughput


class Run14ParallelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scenario, inputs = load('paper-tables-r14')
        cls.anchors = Context(scenario,inputs).parallel

    # Independent raw interval counts reproduce the sweep and the selected
    # control; stale hot-prefill 1/2/4/8 anchors cannot replace the control.
    def test_raw_anchor_recomputation_and_control_selection(self):
        for key, fragment, depth in (('mac','-depth64k-',65552),('control','-maxctx131k-',131088),('mac','-maxctx260k-',260016)):
            name, content = one_file(package(key)[1], fragment)
            for row in map(json.loads, content.splitlines()):
                if row['kind'] != 'round': continue
                expected = sum(r['predicted_n']-1 for r in row['requests'])/max(r['predicted_ms']/1000 for r in row['requests'])
                actual = self.anchors.lookup(row['streams'], depth)
                self.assertAlmostEqual(actual['aggregate_tok_s'],expected)
                self.assertEqual(actual['sources'], name)
                self.assertEqual(round(expected,3),row['aggregate_tok_s'])
        lower = self.anchors.lookup(12,131088)
        self.assertIn('after a long prefill, lower bound',lower['condition'])
        self.assertTrue(lower['conservative'])

    # A supported interval interpolates only its own count and can fall at
    # greater depth. Below the first anchor the unchanged rate is flagged.
    def test_depth_interpolation_and_conservative_shallow_control(self):
        a=self.anchors.lookup(4,131088)['aggregate_tok_s']
        b=self.anchors.lookup(4,260016)['aggregate_tok_s']
        self.assertAlmostEqual(self.anchors.decode(4,(131088+260016)/2)*4,(a+b)/2)
        self.assertLess(b,a)
        self.assertEqual(self.anchors.decode(6,0),self.anchors.decode(6,131088))
        self.assertTrue(self.anchors.lookup(6,0)['conservative'])
        self.assertFalse(self.anchors.lookup(6,131088)['conservative'])

    # Measured-only lookup retains the r4 boundary. The full-mix r5 model
    # slows beyond it and explicitly marks its estimated depth law.
    def test_refuses_optimistic_depth_extrapolation(self):
        self.assertGreater(self.anchors.decode(16,65552),0)
        with self.assertRaisesRegex(InputGap,'depth exceeds deepest measured anchor'):
            self.anchors.measured_lookup(16,65553)
        self.assertLess(self.anchors.decode(16,65553),self.anchors.decode(16,65552))
        self.assertTrue(self.anchors.lookup(16,65553)['zones']['depth_modelled'])
        self.assertGreater(self.anchors.decode(4,260016),0)
        with self.assertRaisesRegex(InputGap,'depth exceeds deepest measured anchor'):
            self.anchors.measured_lookup(4,260017)

    # Count25 is never extrapolated. Holes conservatively reuse the lower
    # measured aggregate rather than interpolating a larger rate.
    def test_refuses_stream_count_above_anchor_and_unmeasured_holes(self):
        self.assertGreater(self.anchors.decode(24,65552),0)
        with self.assertRaisesRegex(InputGap,'above largest measured count'):
            self.anchors.decode(25,32000)
        for count,lower in ((3,2),(5,4),(7,6)):
            self.assertEqual(self.anchors.decode(count,32000)*count,self.anchors.decode(lower,32000)*lower)
            self.assertTrue(self.anchors.lookup(count,32000)['zones']['count_conservative'])

    # A mismatched outer checksum rejects before any payload is admitted;
    # the same pinned archive is the adjacent positive control.
    def test_refuses_archive_checksum_mismatch(self):
        config=json.loads((DATA/'run14-measurements.json').read_text())
        for key,info in config.items():
            path=ROOT/info['directory']/info['archive']
            self.assertTrue(verified_archive(path,info['sha256'])[1])
            with self.subTest(key=key),self.assertRaisesRegex(InputGap,'archive sha256 mismatch'):
                verified_archive(path,'0'*64)

    # Exposed components reproduce the existing device/cycle calculation.
    # Admission is per call, after output growth; a count hole retains all
    # admitted streams, with the lower measured aggregate and coverage flag.
    def test_day_bounds_match_throughput_and_per_call_memory(self):
        calls=[(32000,1000,500,10),(128000,2000,400,20)]
        steps=[(10,10,0,False),(5,0,100,True)]
        mem=end_memory(calls,lambda d:2 if d>100000 else 4)
        result=day_bounds(calls,steps,4,mem,self.anchors,8)
        self.assertAlmostEqual(result['calls_day'],throughput(calls,steps,4,mem,self.anchors.decode,8))
        self.assertEqual((result['min_streams'],result['max_streams']),(2,4))
        lower=day_bounds(calls,steps,4,lambda d:3,self.anchors,8)
        self.assertEqual(lower['min_streams'],3)
        self.assertEqual(lower['zones']['count_conservative']['calls'],1)


class Run14HardwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scenario, inputs=load('paper-tables-r14')
        cls.context=Context(scenario,inputs)
        cls.b300=cls.context.b300

    # The same SoC has identical curves at all probed depths and counts;
    # memory alone permits more resident streams on the128 GB machine.
    def test_m5_same_soc_curves_and_memory_only_difference(self):
        c=self.context;m=c.model('qwen27')
        a=c.client('m5max64','hardware.links.wan.bandwidth','test')
        b=c.client('m5max','hardware.links.wan.bandwidth','test')
        for depth in (16000,32000,65536,131072,249000,1000000):
            self.assertEqual(c.g.resolve(a['local']).value(depth),c.g.resolve(b['local']).value(depth))
            for streams in (1,2,3,4):
                self.assertEqual(c.g.resolve(a['decoder']).value(streams,depth),c.g.resolve(b['decoder']).value(streams,depth))
        self.assertLess(c.g.resolve(a['memory']).value(500000),c.g.resolve(b['memory']).value(500000))
        decode=c.g.resolve(b['decoder']).value
        self.assertAlmostEqual(4*decode(4,32000)/decode(1,32000),33.37/18.29)

    # Ultra compute/bandwidth factors use measured M5 Max as denominator;
    # the M3-derived sensitivity remains a distinct selectable calculation.
    def test_ultra_scales_from_measured_m5_and_old_sensitivity_is_distinct(self):
        c=self.context;base=c.client('m5max','hardware.links.wan.bandwidth','test')
        for key in ('ultra96','ultra256'):
            cl=c.client(key,'hardware.links.wan.bandwidth','test')
            for depth in (32000,131072):
                ratio=c.inputs.get('hardware.clients.'+key+'.compute')/c.inputs.get('hardware.clients.m5max.compute')
                self.assertAlmostEqual(c.g.resolve(cl['local']).value(depth)/c.g.resolve(base['local']).value(depth),ratio)
                self.assertAlmostEqual(c.g.resolve(cl['decoder']).value(4,depth)/c.g.resolve(base['decoder']).value(4,depth),2)
        scenario,inputs=load('paper-tables-r14');scenario['m5_m3_sensitivity']=True
        old=Context(scenario,inputs);rate=old.g.resolve(old.local_rate('m5max',old.model('qwen27'))).value
        self.assertNotAlmostEqual(rate(32000),c.g.resolve(base['local']).value(32000))

    # The real Context consumes the B300 bulk fit with unit peak factor;
    # measured decode and step70's explicit skip are retained separately.
    def test_b300_measured_curve_decode_and_tuning_skip(self):
        b=self.b300;c=self.context
        self.assertAlmostEqual(b.a,.0005673505018699517,places=16)
        self.assertAlmostEqual(b.b,2.1666191870109614e-9,places=18)
        compute=c.g.resolve(c.server('b300',c.model('qwen27'))['compute']).value
        for depth in (16000,100000,249000):
            self.assertAlmostEqual(compute_at(compute,depth)/(54e9+393216*depth),1/(b.a+b.b*depth))
        turns=[r for r in b.rows if r.get('kind')=='turn' and r['delta']==2000]
        for raw,(d,r) in zip(turns,b.decode_curve):
            self.assertAlmostEqual(r,raw['predicted_n']/(raw['predicted_ms']/1000))
            self.assertEqual(b.decode(d),r)
        self.assertEqual(b.tuning['status'],'skipped')
        self.assertEqual(b.tuning['pinned_commit'],b.tuning['new_commit'])
        self.assertEqual(b.tuning['pinned_commit'],'dde879bc4f954b809892fd0d660515f42536394a')

    # A real measured archive is accepted. Removing it in an isolated root
    # makes the B300 option refuse, rather than using the former peak ratio.
    def test_refuses_b300_option_without_measured_inputs(self):
        self.assertGreater(self.b300.compute(self.context.g.resolve(self.context.fm).value,'Q4')(100000),0)
        with tempfile.TemporaryDirectory() as tmp,patch.object(measured,'ROOT',Path(tmp)):
            with self.assertRaisesRegex(InputGap,'measurements.b300: missing measured inputs'):
                B300Measurements()

    # Both KV formats use their own observed cache-block lengths; cached
    # useful rates are independently derived from delta/TTFT, not labels.
    def test_b300_vllm_both_kv_settings_recomputed(self):
        blocks={}
        for doc in self.b300.vllm:
            rates=b300_vllm_rates(doc);blocks[doc['name']]={r['cache_block_tokens'] for r in rates}
            for raw,out in zip(doc['B'],rates):
                self.assertAlmostEqual(out['delta_tok_s'],raw['delta']/raw['measurement']['ttft_s'])
                self.assertAlmostEqual(out['processed_tok_s'],(raw['depth']+raw['delta']-raw['measurement']['cached_tokens'])/raw['measurement']['ttft_s'])
                self.assertLessEqual(out['delta_tok_s'],out['processed_tok_s'])
        self.assertEqual(blocks['fp8-default'],{784})
        self.assertEqual(blocks['fp8-kv'],{1568})

    # Wrong cache geometry and zero TTFT reject beside valid FP8 KV probes.
    def test_b300_vllm_refuses_wrong_cache_block_or_ttft(self):
        doc=next(d for d in self.b300.vllm if d['name']=='fp8-kv')
        self.assertGreater(b300_vllm_rates(doc)[0]['delta_tok_s'],0)
        for field,value in (('cache_block_tokens',1024),('ttft_s',0)):
            bad=copy.deepcopy(doc)
            if field=='ttft_s':bad['B'][0]['measurement'][field]=value
            else:bad['B'][0][field]=value
            with self.assertRaisesRegex(InputGap,'invalid measured cached-delta inputs'):
                b300_vllm_rates(bad)

    # Cold fits reproduce the raw TTFT normal equations for both KV formats;
    # these are server-only prefills, with no inferred hybrid transfer rate.
    def test_b300_vllm_cold_fit_goldens(self):
        expected={'fp8-default':(3.655281885151814e-5,3.162585040047219e-10),
                  'fp8-kv':(3.765754048715862e-5,1.6236251049617047e-10)}
        for doc in self.b300.vllm:
            if doc['name'] not in expected:continue
            a,b=measured.cold_fit(doc);aa,bb=expected[doc['name']]
            self.assertAlmostEqual(a,aa,places=16);self.assertAlmostEqual(b,bb,places=18)
            for r in doc['A']:
                self.assertEqual(r['cached_tokens'],0)
                self.assertLess(abs((a*r['length']+b*r['length']**2/2)/r['ttft_s']-1),.04)

    # The owned B300 fleet consumes measured decode, independently of the
    # older analytical bandwidth-efficiency setting; no batching gain is claimed.
    def test_owned_b300_consumes_measured_decode(self):
        values=[]
        for efficiency in (.1,.9):
            scenario,inputs=load('paper-tables-r14',['owners.server_bw_efficiency='+str(efficiency)])
            c=Context(scenario,inputs);m=c.model('qwen27');server=c.server('b300',m)
            calls=c.label('test.calls',[(100000,2000,500,10),(200000,2000,500,10)])
            values.append(c.g.resolve(c.own_seconds('test.owned',calls,m,server)).value)
        self.assertIsInstance(values[0],float)
        self.assertEqual(values[0],values[1])


class Run14ExportTests(unittest.TestCase):
    # All14 full-mix rows are modelled without dropping calls. Measured-only
    # bounded tables retain the independent r4 lookup limits.
    def test_agent_day_gaps_and_supported_rows(self):
        import csv,io
        rows=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run14/base/client_agents_day.csv').read_text())))
        self.assertEqual(len(rows),14)
        for row in rows:
            self.assertEqual(int(row['calls']),39904)
            self.assertEqual(row['depth_ceiling'],'full mix')
            self.assertEqual(row['status'],'ok')
            self.assertGreater(float(row['hybrid_sessions_day']),float(row['local_sessions_day']))
            self.assertIn(row['local_bound'],('device','agent cycle'))
            if int(row['agents'])>=4:self.assertGreater(float(row['depth_modelled_call_share']),0)
        bounded=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run14/base/client_agents_day_bounded.csv').read_text())))
        row=next(r for r in bounded if r['agents']=='16' and r['depth_ceiling']=='65552' and r['link_mbit']=='1000')
        self.assertEqual(row['status'],'ok');self.assertLess(int(row['calls']),39904)

    # New sidecars bind the current source and real payload bytes; both old
    # export trees bind immutable history and are compared byte for byte.
    def test_run14_manifest_hashes_and_all402_frozen_files(self):
        from hybridcalc.export import generator_identity
        from r14_audit import frozen
        self.assertEqual(frozen(),{'calc/out/paper':150,'calc/out/run13':252})
        paths=list((ROOT/'calc/out/run14').rglob('*manifest.json'));self.assertEqual(len(paths),9)
        for p in paths:
            manifest=json.loads(p.read_text());self.assertEqual(manifest['generator'],generator_identity())
            for name,digest in manifest['files'].items():
                self.assertEqual(hashlib.sha256((p.parent/name).read_bytes()).hexdigest(),digest)
        index=json.loads((ROOT/'calc/out/run14/INDEX.json').read_text())
        for name,digest in index['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'calc/out/run14'/name).read_bytes()).hexdigest(),digest)

    # Every new B300 option row is explicitly server-only, including both KV
    # formats; the skipped tuning result survives CSV's reserved status field.
    def test_server_options_are_server_only_and_tuning_is_skipped(self):
        import csv,io
        directory=ROOT/'calc/out/run14/measurements'
        for name in ('b300_vllm_cold','b300_vllm_cached'):
            rows=list(csv.DictReader(io.StringIO((directory/(name+'.csv')).read_text())))
            self.assertEqual(len(rows),24)
            self.assertEqual({r['kv'] for r in rows},{'auto','fp8'})
            self.assertTrue(all(r['server_only']=='1' and r['client_bridge']=='0' and 'in qualification' in r['qualification'] for r in rows))
        tuning=list(csv.DictReader(io.StringIO((directory/'b300_tuning.csv').read_text())))[0]
        self.assertEqual(tuning['tuning_status'],'skipped')


if __name__ == '__main__':
    unittest.main()
