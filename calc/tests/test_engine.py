"""Physical invariants, input rejection and bounded end-to-end controls."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

CALC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALC))
from hybridcalc.engine import load, run
from hybridcalc.inputs import DATA, ROOT, InputError, Inputs
from hybridcalc.performance import (Calibration, dense_decode, flop, payload,
                                    roofline_prefill, transfer)
from hybridcalc import economics as ec
from hybridcalc import glm
from hybridcalc.formatters import render
from hybridcalc.workload import sampled_calls


class PhysicsTests(unittest.TestCase):
    def setUp(self):
        _, self.inputs = load('paper-base')
        self.model = self.inputs.section('models.qwen27')
        self.model['state'] = 156894784
        self.link = self.inputs.section('hardware.links.wan')

    # Increasing link bandwidth never increases transfer time; payload has the correct affine state intercept.
    def test_transfer_monotonicity_and_payload(self):
        self.assertEqual(payload(10, 100, 500), 1500)
        for delta in (0, 1, 512, 2000, 10000, 1000000):
            times = [transfer(delta, self.model['kv'], self.model['state'], dict(self.link, bandwidth=b))
                     for b in (1e6, 1e8, 1e9, 200e9)]
            self.assertEqual(times, sorted(times, reverse=True))
            self.assertGreaterEqual(times[-1], self.link['latency'])

    # Compute upgrades cannot increase prefill time, and infinite compute cannot remove a memory bottleneck.
    def test_roofline_monotonicity(self):
        for depth in (0, 32000, 200000, 1000000):
            times = [roofline_prefill(self.model, depth, c, 400e9, 1e9) for c in (1e12, 1e13, 1e15)]
            self.assertEqual(times, sorted(times, reverse=True))
            self.assertAlmostEqual(times[-1], 1e9 / 400e9)

    # Billing is homogeneous in ALL token prices; valid free prices produce zero, not rejection.
    def test_price_linearity(self):
        calls = [(10000, 1000, 100, 2), (200000, 2000, 200, 1)]
        prices = {'input': .2, 'output': 2, 'cache_read': .05, 'cache_write': .2}
        self.assertAlmostEqual(ec.api_cost(calls, {k: 3*v for k,v in prices.items()}), 3*ec.api_cost(calls, prices))
        self.assertEqual(ec.api_cost(calls, {k: 0 for k in prices}), 0)
        # Prefix+delta+output is independently priced once; no assumed cache write of prior outputs.
        self.assertAlmostEqual(ec.api_cost(calls, prices), (210000*.05 + 3000*.2 + 300*2)/2/1e6)

    # Calibration reproduces the raw segment anchors, exact slot affine fit, and normalized 32k single/four-stream data.
    def test_measurement_calibration(self):
        calibration = Calibration(self.inputs, self.model)
        for depth, rate in calibration.curve:
            self.assertEqual(calibration.rate(depth), rate)
        self.assertEqual(calibration.slot_per_token, 34844)
        self.assertEqual(calibration.slot_fixed, 156894784)
        x, y = calibration.curve[-1]
        self.assertAlmostEqual(calibration.rate(1e6)*flop(self.model,1e6), y*flop(self.model,x))
        dev = self.inputs.section('hardware.clients.m3max')
        eff, penalty = calibration.decode_parameters(self.model['weights'], self.model['kv'], dev['bandwidth'], 2)
        self.model['state'] = calibration.slot_fixed
        one = dense_decode(self.model, dev, 1, 32000, eff, penalty, 2)
        four = dense_decode(self.model, dev, 4, 32000, eff, penalty, 2)
        self.assertAlmostEqual(one, 8.440946539830035)
        self.assertAlmostEqual(4*four/one, 1.665015442445748)

    # Sequential pipeline memory bandwidth does not double with node count; increasing inter-node bandwidth cannot slow decode.
    def test_glm_pair_communication(self):
        _, data = load('glm-tier2')
        model = data.section('models.glm')
        pair = data.section('hardware.glm_family.spark2')
        link = data.section('hardware.links.spark')
        expected = 2*(50e-6 + 4*6144*2*8/(200e9*.8))
        self.assertAlmostEqual(glm.communication(model,pair,4,link), expected)
        rates = [glm.decode_rate(model,pair,4,110000,2,dict(link,bandwidth=b))[0] for b in (1e9,10e9,200e9)]
        self.assertEqual(rates, sorted(rates))
        single = dict(pair,nodes=1)
        single_rate = glm.decode_rate(model,single,4,110000,2)[0]
        self.assertGreater(single_rate, rates[-1])
        self.assertEqual(glm.communication(model,single,4,None), 0)

    # Integer fleets cover computed peak demand; a doubled capex cannot lower fleet cash cost.
    def test_integer_fleet(self):
        server = self.inputs.section('hardware.servers.b300')
        prices = self.inputs.section('prices')
        econ = self.inputs.section('economics')
        for people in (5,100,1000,5000):
            result = ec.fleet(people,2,server,prices,econ)
            self.assertGreaterEqual(result['units']*server['gpus'], result['peak_gpus'])
            expensive = ec.fleet(people,2,dict(server,capex=2*server['capex']),prices,econ)
            self.assertGreater(expensive['monthly'],result['monthly'])

    # Crossing is on the finite grid and must survive every later point, including a reversal.
    def test_equilibrium_requires_staying_below(self):
        rows = [{'people':n,'a':a,'b':2} for n,a in [(5,1),(10,3),(20,1),(50,2)]]
        self.assertEqual(ec.first_stays(rows,'a','b'),20)
        self.assertIsNone(ec.first_stays(rows+[{'people':100,'a':3,'b':2}],'a','b'))


class InputTests(unittest.TestCase):
    def setUp(self):
        _, self.inputs = load('paper-base')

    # Each invalid quantity is rejected with its exact path and intended reason; the valid control still loads.
    def test_rejections(self):
        self.inputs.validate()
        path = 'hardware.links.wan.bandwidth'
        for field,value,message in [('provenance',None,'provenance'),('unit','GB','wrong unit'),('value',0,'greater than'),('value',-1,'greater than'),('value',float('nan'),'finite'),('value',True,'finite')]:
            data = copy.deepcopy(self.inputs.data)
            data['hardware']['links']['wan']['bandwidth'][field] = value
            with self.subTest(field=field,value=value), self.assertRaisesRegex(InputError, path+'.*'+message):
                Inputs(data)

    # The strict Inputs API (used by legacy execution) rejects invalid overrides atomically; canonical CLI invalids become alarms.
    def test_overrides_are_strict_and_atomic(self):
        self.inputs = Inputs(self.inputs.data)
        original = copy.deepcopy(self.inputs.data)
        for expression in ('hardware.links.wan.typo=1','hardware.links.wan=10','workload.sample_calls=2.5','hardware.links.wan.bandwidth=-1','economics.regions=4','prices.egress=true'):
            with self.subTest(expression=expression), self.assertRaises(InputError):
                self.inputs.override(expression)
            self.assertEqual(self.inputs.data, original)
        self.inputs.override('hardware.links.wan.bandwidth=2000000000')
        self.assertEqual(self.inputs.get('hardware.links.wan.bandwidth'), 2000000000)
        self.assertIn('CLI override', self.inputs.locate('hardware.links.wan.bandwidth')['provenance']['reason'])

    # Fact/measured provenance has independently validated shape; valid controls precede each bad case.
    def test_provenance_shapes(self):
        from hybridcalc.inputs import provenance
        provenance('x',{'kind':'fact','url':'https://example.org','access_date':'2026-10-30'})
        provenance('x',{'kind':'measured','package':'p','sha256':'a'*64})
        for source in ({'kind':'fact','url':'file:///tmp/x','access_date':'2026-10-30'},
                       {'kind':'fact','url':'https://example.org','access_date':'bad'},
                       {'kind':'measured','package':'p','sha256':'broken'},
                       {'kind':'estimate','reason':''}):
            with self.subTest(source=source), self.assertRaises(InputError):
                provenance('x',source)

    # A hash mutation rejects a real measured file, while unchanged files pass their pinned hash.
    def test_checksum_rejection(self):
        self.inputs.measured('stats')
        self.inputs.data['measurements']['stats']['sha256'] = '0'*64
        with self.assertRaisesRegex(InputError,'sha256 mismatch'):
            self.inputs.measured('stats')

    # Both copied packages preserve every file digest and the supplied archive identity.
    def test_package_integrity(self):
        base = ROOT/'data/measurements/ivmbp-2026-10-30'
        packages = json.loads((base/'ENGINE-PACKAGES.json').read_text())
        self.assertEqual(packages['qwen27b-bench']['archive_sha256'],'5c393bdf40052eb582b5c17aac6176a9273a866c4fadde999ee19afa30924439')
        self.assertEqual(packages['session-call-dates']['archive_sha256'],'164be0dbe0a294ef12bd209207582421164e049a7b8bec9d8d4d2a1e85c1d190')
        for directory,info in packages.items():
            self.assertEqual({str(p.relative_to(base/directory)) for p in (base/directory).rglob('*') if p.is_file()},set(info['files']))
            for file,expected in info['files'].items():
                self.assertEqual(hashlib.sha256((base/directory/file).read_bytes()).hexdigest(),expected)

    # Sampler output is seeded and keeps partial groups, including a single call; session normalization cannot discard valid calls.
    def test_sampler_reproducibility_and_limits(self):
        cfg = self.inputs.section('workload')
        cfg['sample_calls'] = 117
        a = sampled_calls(self.inputs,cfg)
        self.assertEqual(len(a),117)
        self.assertEqual(a,sampled_calls(self.inputs,cfg))
        cfg['sample_calls'] = 115
        self.assertEqual(len(sampled_calls(self.inputs,cfg)),115)
        cfg['sample_calls'] = 1
        self.assertEqual(len(sampled_calls(self.inputs,cfg)),1)


class EndToEndTests(unittest.TestCase):
    # All structured renderers consume the same table cells; CSV is rectangular and TeX escapes booktabs cells.
    def test_formatters(self):
        result={'tables':[{'name':'example','columns':{'device':'text','cost':'USD'},'rows':[{'device':'A&B_1','cost':1.25}]}]}
        self.assertEqual(json.loads(render(result,'json')),result)
        self.assertIn('1.25',render(result,'md'))
        row=list(csv.DictReader(io.StringIO(render(result,'csv'))))[0]
        self.assertEqual(row,{'table':'example','device':'A&B_1','cost':'1.25'})
        self.assertIn(r'\toprule',render(result,'tex'))
        self.assertIn(r'A\&B\_1',render(result,'tex'))
        with self.assertRaisesRegex(InputError,'historical'):
            render(result,'legacy')

    # A data-only hardware entry participates in the paper model, and an API-price override changes only its billing row.
    def test_data_only_hardware_and_pricing(self):
        result=run('paper-base',['workload.sample_calls=232'])
        changed=run('paper-base',['workload.sample_calls=232','prices.apis.qwen_median.input=0.36'])
        def api_row(result):return next(t for t in result['tables'] if t['name'].startswith('API and'))['rows'][0]
        mix=result['tables'][0]['rows'][0]
        difference=api_row(changed)['per_1000_calls']-api_row(result)['per_1000_calls']
        self.assertAlmostEqual(difference,mix['mean_new']*.18/1e6*1000)
        scenario,inputs=load('paper-base',['workload.sample_calls=232'])
        inputs.data['hardware']['clients']['newbox']=copy.deepcopy(inputs.data['hardware']['clients']['m5max'])
        inputs.data['hardware']['clients']['newbox']['label']='New hardware, data only'
        inputs.validate()
        scenario['client_keys']=['newbox'];scenario['fleet_client']='newbox'
        from hybridcalc.paper import calculate
        tables=calculate(scenario,inputs)['tables']
        newrow=next(t for t in tables if t['name'].startswith('Decode'))['rows'][0]
        self.assertEqual(newrow['device'],'New hardware, data only')
        original=next(row for t in result['tables'] if t['name'].startswith('Decode') for row in t['rows'] if row['device']=='M5 Max 128 GB')
        self.assertEqual(newrow['per_session'],original['per_session'])

    # The GLM hardware family includes both pair links and full cost components, with same-mix API/own references.
    def test_glm_family(self):
        result=run('glm-tier2',['workload.sample_calls=232'])
        rows=next(t for t in result['tables'] if t['name'].startswith('Decode'))['rows']
        self.assertEqual(len(rows),4)
        self.assertIn('200.0 Gbit/s',rows[2]['link'])
        self.assertIn('10.0 Gbit/s',rows[3]['link'])
        for row in rows:
            self.assertGreater(row['tok_s_stream'],0)
            self.assertAlmostEqual(row['per_session'],sum(row[k] for k in ('server_session','egress_session','device_session','energy_session','storage_session')))
            self.assertGreater(row['api_session'],0)
            self.assertGreater(row['own_session'],0)
        rental=run('glm-tier2',['workload.sample_calls=232','prices.rental_gpu_hour=19'])
        altered=next(t for t in rental['tables'] if t['name'].startswith('Decode'))['rows']
        for before,after in zip(rows,altered):
            self.assertAlmostEqual(after['rental_session']-before['rental_session'], before['rental_session']-before['per_session']+before['server_session'])

    # The public module entry point works from the repo root; invalid overrides exit 2 with a clear error, no traceback.
    def test_cli_and_wrapper(self):
        def command(*args):return subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True)
        valid=command('-m','hybridcalc','list')
        self.assertEqual(valid.returncode,0,valid.stderr)
        self.assertIn(b'paper-base',valid.stdout)
        invalid=command('-m','hybridcalc','run','paper-base','--set','bad.path=1')
        self.assertEqual(invalid.returncode,2)
        self.assertIn(b'unknown override/input path',invalid.stderr)
        self.assertNotIn(b'Traceback',invalid.stderr)
        wrapper=command('calc/hybrid_calc9_m3max_measured.py')
        self.assertEqual(wrapper.returncode,0,wrapper.stderr)
        self.assertEqual(wrapper.stdout,(CALC/'hybrid_calc9_m3max_measured.out').read_bytes())

    # Sources retain measurement archive identities and override provenance; no full05 counts feed the full04 workload.
    def test_sources_and_snapshot_separation(self):
        result=run('paper-base',['workload.sample_calls=232','prices.egress=0'])
        source=next(s for s in result['sources'] if s['path']=='prices.egress')
        self.assertEqual(source['value'],0)
        self.assertIn('CLI override',source['provenance']['reason'])
        paths={row['path'] for row in result['files']}
        self.assertTrue(any(p.endswith('session-call-dates/call-dates.json') for p in paths))
        self.assertTrue(any(p.endswith('/qwen27b-bench/depth.jsonl') for p in paths))
        self.assertFalse(any(p.endswith('session-call-dates/stats.json') for p in paths))
        self.assertEqual(result['tables'][0]['rows'][0]['calls'],232)


if __name__ == '__main__':
    unittest.main()
