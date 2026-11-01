"""Owner contract: missing inputs taint their dependents and leave independent metrics exact."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CALC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALC))
from hybridcalc.engine import load, run
from hybridcalc.inputs import ROOT, InputError
from hybridcalc.paper import calculate
from hybridcalc.formatters import render


def tables(result):
    return {table['name']: table for table in result['tables']}


def is_alarm(value):
    return isinstance(value, dict) and 'alarm' in value


class GapTests(unittest.TestCase):
    def setUp(self):
        self.scenario, self.inputs = load('paper-base', ['workload.sample_calls=232'])

    # A single missing rental price produces exactly one root alarm and changes only cells declaring that dependency.
    def test_planted_gap_preserves_independent_tables(self):
        baseline = calculate(self.scenario, self.inputs)
        del self.inputs.data['prices']['rental_gpu_hour']
        changed = calculate(self.scenario, self.inputs)
        expected = {'input': 'prices.rental_gpu_hour', 'reason': 'missing input'}
        self.assertEqual(changed['alarms'], [expected])
        affected = 0
        for before, after in zip(baseline['tables'], changed['tables']):
            for row_index, (a, b) in enumerate(zip(before['rows'], after['rows'])):
                for column in before['columns']:
                    dependencies = after['dependencies']['{}.{}'.format(row_index, column)]['inputs']
                    if 'prices.rental_gpu_hour' in dependencies:
                        self.assertEqual(b[column], {'alarm': [expected]})
                        affected += 1
                    else:
                        self.assertEqual(a[column], b[column])
            if not after['alarms']:
                self.assertEqual(before, after)
        self.assertGreater(affected, 0)

    # Every canonical output cell has a declaration, including transitive paths; none is inferred from numeric coincidence.
    def test_every_cell_declares_dependencies(self):
        result = calculate(self.scenario, self.inputs)
        self.assertFalse(result['alarms'])
        for table in result['tables']:
            for index,row in enumerate(table['rows']):
                for column in table['columns']:
                    self.assertIn(column,row)
                    declaration=table['dependencies']['{}.{}'.format(index,column)]
                    self.assertIn('inputs',declaration)
                    self.assertIn('requires',declaration)

    # Null, bad units/provenance, NaN and infinity raise input-specific alarms; unrelated calibration is unchanged.
    def test_invalid_values_are_alarms(self):
        base=calculate(self.scenario,self.inputs)
        name=next(t['name'] for t in base['tables'] if t['name'].startswith('M3 Max'))
        for field,value,reason in [('value',None,'finite'),('value',float('nan'),'finite'),('value',float('inf'),'finite'),
                                   ('unit','USD/month','wrong unit'),('provenance',None,'provenance')]:
            with self.subTest(field=field,value=value):
                _,data=load('paper-base',['workload.sample_calls=232'])
                data.data['prices']['rental_gpu_hour'][field]=value
                result=calculate(self.scenario,data)
                self.assertEqual(len(result['alarms']),1)
                self.assertEqual(result['alarms'][0]['input'],'prices.rental_gpu_hour')
                self.assertIn(reason,result['alarms'][0]['reason'])
                self.assertEqual(tables(result)[name],tables(base)[name])
                json.dumps(result,allow_nan=False)

    # Empty samples have a known zero count, but no price/mean is invented; one call is a valid denominator.
    def test_empty_and_single_call(self):
        for count in (0,1):
            result=run('paper-base',['workload.sample_calls='+str(count)])
            mix=result['tables'][0]['rows'][0]
            self.assertEqual(mix['calls'],count)
            if count:
                self.assertFalse(result['alarms'])
                self.assertGreater(mix['mean_depth'],0)
            else:
                self.assertTrue(is_alarm(mix['mean_depth']))
                self.assertTrue(any('empty call mix' in a['reason'] for a in result['alarms']))

    # A zero or absent link prevents hybrid metrics and explicitly says offload is impossible; local edge/API values survive.
    def test_zero_and_missing_link(self):
        baseline=calculate(self.scenario,self.inputs)
        for missing in (False,True):
            _,data=load('paper-base',['workload.sample_calls=232'])
            if missing: del data.data['hardware']['links']['wan']['bandwidth']
            else: data.data['hardware']['links']['wan']['bandwidth']['value']=0
            result=calculate(self.scenario,data)
            self.assertTrue(any(a['input']=='hardware.links.wan.bandwidth' and 'offload impossible' in a['reason'] for a in result['alarms']))
            api=next(t['name'] for t in baseline['tables'] if t['name'].startswith('API and'))
            self.assertEqual(tables(result)[api],tables(baseline)[api])
            edge=next(t for t in result['tables'] if t['name'].startswith('Edge'))
            self.assertGreater(edge['rows'][0]['local_prefill'],0)
            self.assertTrue(is_alarm(edge['rows'][0]['hybrid_ttft']))

    # Zero rental utilization alarms instead of division-by-zero; full utilization and a free price compute exactly zero rent.
    def test_utilization_and_zero_price(self):
        invalid=run('paper-base',['workload.sample_calls=232','economics.rental_utilization=0'])
        self.assertTrue(any(a['input']=='economics.rental_utilization' for a in invalid['alarms']))
        valid=run('paper-base',['workload.sample_calls=232','economics.rental_utilization=1','prices.rental_gpu_hour=0'])
        self.assertFalse(valid['alarms'])
        ops=next(t for t in valid['tables'] if t['name'].startswith('Prefill and'))
        for row in ops['rows']:
            if row['variant'].startswith('Rented'):
                self.assertEqual(row['per_1000_calls'],0)

    # Missing and corrupt packages alarm at the measured-file input; a missing dates package cannot change workload/API cells.
    def test_measurement_missing_or_corrupt(self):
        baseline=calculate(self.scenario,self.inputs)
        for corrupt in (False,True):
            _,data=load('paper-base',['workload.sample_calls=232'])
            if corrupt: data.data['measurements']['dates']['sha256']='0'*64
            else: data.data['measurements']['dates']['path']='.temp/hybrid-calc-r2-261030/absent-package.json'
            changed=calculate(self.scenario,data)
            self.assertEqual(len(changed['alarms']),1)
            self.assertEqual(changed['alarms'][0]['input'],'measurements.dates')
            self.assertIn('sha256 mismatch' if corrupt else 'unavailable',changed['alarms'][0]['reason'])
            self.assertEqual(changed['tables'][0],baseline['tables'][0])
            api=next(t['name'] for t in baseline['tables'] if t['name'].startswith('API and'))
            self.assertEqual(tables(changed)[api],tables(baseline)[api])

    # Markdown/CSV/JSON/TeX carry cell alarms and table-level alarm lists; renderers never turn them into blank numeric cells.
    def test_alarm_formatters(self):
        del self.inputs.data['prices']['rental_gpu_hour']
        result=calculate(self.scenario,self.inputs)
        for fmt in ('md','csv','json','tex'):
            output=render(result,fmt)
            self.assertIn('rental',output)
            self.assertIn('missing input',output)
            if fmt!='json': self.assertIn('ALARM',output)

    # Strict mode gates alarms after printing partial results; normal mode exits 0, and unknown overrides remain hard errors.
    def test_cli_exit_contract(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            target=Path(directory)/'gap.json'
            target.write_text(json.dumps({'name':'gap','kind':'paper','inputs':['bundle:hardware.json','bundle:models.json','bundle:workload.json','bundle:economics.json','bundle:sampler.json',str(Path(directory)/'prices.json')],
                                         **{k:v for k,v in self.scenario.items() if k not in ('name','kind','inputs')}}))
            data=copy.deepcopy(self.inputs.data['prices']);del data['rental_gpu_hour']
            (Path(directory)/'prices.json').write_text(json.dumps({'prices':data}))
            for strict in (False,True):
                args=[sys.executable,'-m','hybridcalc','run',str(target),'--set','workload.sample_calls=232','--format','json']
                result=subprocess.run(args+(['--strict'] if strict else []),cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(result.returncode,1 if strict else 0,result.stderr)
                self.assertIn('rental_gpu_hour',result.stdout)
                self.assertNotIn('Traceback',result.stderr)
                json.loads(result.stdout)
        with self.assertRaises(InputError):
            run('paper-base',['unknown.path=1'])


class BoundaryTests(unittest.TestCase):
    # Depth zero and the declared context boundary use exact FLOP arithmetic; one token beyond the envelope alarms.
    def test_depth_zero_and_context_limit(self):
        from hybridcalc.performance import flop, transfer
        from hybridcalc.inputs import InputGap
        _,inputs=load('paper-base')
        model=inputs.section('models.qwen27')
        self.assertEqual(flop(model,0),54e9)
        limit=model['context_limit']
        self.assertEqual(flop(model,limit),54e9+393216*limit)
        with self.assertRaisesRegex(InputGap,'exceeds declared context limit'):
            flop(model,limit+1)
        for link in ({'bandwidth':0,'goodput':.9,'latency':.4},{'goodput':.9,'latency':.4}):
            with self.assertRaisesRegex(InputGap,'offload impossible'):
                transfer(1000,32768,1,link)

    # A deterministic one-call fixture validates API billing at depth 0 and the envelope; unsupported client memory gives an alarm, not zero cost.
    def test_one_call_at_both_depth_boundaries(self):
        from unittest.mock import patch
        for depth in (0,1000000):
            with patch('hybridcalc.analysis_graph.sampled_calls',return_value=[(depth,0,100,2)]):
                result=run('paper-base',['workload.sample_calls=1'])
            mix=result['tables'][0]['rows'][0]
            self.assertEqual(mix['mean_depth'],depth)
            api=next(t for t in result['tables'] if t['name'].startswith('API and'))['rows'][0]
            self.assertAlmostEqual(api['per_1000_calls'],(depth*.05+100*2.30)/1e6*1000)
            clients=next(t for t in result['tables'] if t['name'].startswith('Decode'))['rows']
            self.assertFalse(is_alarm(clients[0]['per_session']))
            if depth:
                self.assertEqual(clients[1]['fit_share'],0)
                self.assertTrue(is_alarm(clients[1]['per_session']))

    # Missing stats stops every call-derived price while leaving independent prefill calibration and call-date tables exact.
    def test_corrupted_workload_preserves_measurement_tables(self):
        scenario,inputs=load('paper-base',['workload.sample_calls=232'])
        baseline=calculate(scenario,inputs)
        inputs.data['measurements']['stats']['sha256']='0'*64
        changed=calculate(scenario,inputs)
        self.assertEqual(changed['alarms'],[{'input':'measurements.stats','reason':'measurement sha256 mismatch'}])
        for prefix in ('M3 Max','Separate call-date'):
            name=next(t['name'] for t in baseline['tables'] if t['name'].startswith(prefix))
            self.assertEqual(tables(changed)[name],tables(baseline)[name])
        for row in next(t for t in changed['tables'] if t['name'].startswith('API and'))['rows']:
            self.assertTrue(is_alarm(row['per_1000_calls']))

    # A nonfinite measured field is rejected even if its file hash was deliberately repinned; caps cannot convert NaN into a valid sampled token count.
    def test_nonfinite_measured_field_is_not_capped_to_a_number(self):
        import hashlib
        scenario,inputs=load('paper-base',['workload.sample_calls=1'])
        document=inputs.measured_json('stats')
        document['agents']['all']['output_per_call']['mean']=float('nan')
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            path=Path(directory)/'bad-stats.json';content=json.dumps(document).encode();path.write_bytes(content)
            inputs.data['measurements']['stats']['path']=str(path)
            inputs.data['measurements']['stats']['sha256']=hashlib.sha256(content).hexdigest()
            result=calculate(scenario,inputs)
        self.assertEqual(len(result['alarms']),1)
        self.assertEqual(result['alarms'][0]['input'],'measurements.stats')
        self.assertIn('finite',result['alarms'][0]['reason'])
        self.assertTrue(is_alarm(result['tables'][0]['rows'][0]['mean_output']))
        json.dumps(result,allow_nan=False)

    # Missing laptop baseline affects laptop premiums only; the owned M3 and full-price Ultras keep their exact amortization.
    def test_missing_baseline_has_only_laptop_dependents(self):
        scenario,inputs=load('paper-base',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['economics']['baseline_laptop']
        after=calculate(scenario,inputs)
        a=next(t for t in before['tables'] if t['name'].startswith('Decode'))['rows']
        b=next(t for t in after['tables'] if t['name'].startswith('Decode'))['rows']
        for index in (0,4,5):
            self.assertEqual(a[index],b[index])
        for index in (1,2,3):
            self.assertTrue(is_alarm(b[index]['device_session']))
            self.assertEqual(a[index]['tok_s_stream'],b[index]['tok_s_stream'])

    # With no computable numeric metrics, normal CLI mode still exits nonzero after rendering its alarms, with no traceback.
    def test_nothing_computable_exits_one(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            path=Path(directory)/'empty.json'
            path.write_text(json.dumps({'name':'empty','kind':'service','inputs':[],'model':'qwen27','api_keys':['qwen_median'],'option_keys':['h100_sxm']}))
            result=subprocess.run([sys.executable,'-m','hybridcalc','run',str(path),'--format','json'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stderr)
        document=json.loads(result.stdout)
        self.assertEqual(document['computed_metrics'],0)
        self.assertTrue(document['alarms'])
        self.assertNotIn('Traceback',result.stderr)


class SourceFileTests(unittest.TestCase):
    # A failed local prices layer removes earlier prices; calibration survives and no bundled/prior price leaks into results.
    def test_failed_scoped_layer_has_no_earlier_fallback(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            root=Path(directory)
            original,_=load('paper-base')
            scenario={**original,'name':'broken-file','inputs':['bundle:hardware.json','bundle:models.json','bundle:workload.json','bundle:economics.json','bundle:sampler.json','bundle:prices.json',{'file':'absent.json','provides':['prices']}]}
            path=root/'scenario.json';path.write_text(json.dumps(scenario))
            result=run(str(path),['workload.sample_calls=1'])
        self.assertTrue(result['alarms'])
        self.assertTrue(any(a['input']=='prices.rental_gpu_hour' and 'source file unavailable' in a['reason'] for a in result['alarms']))
        calibration=next(t for t in result['tables'] if t['name'].startswith('M3 Max'))
        self.assertFalse(calibration['alarms'])
        for row in next(t for t in result['tables'] if t['name'].startswith('API and'))['rows']:
            self.assertTrue(is_alarm(row['per_1000_calls']))

    # A same-named missing local file is not replaced by bundled data; malformed scoped JSON has the same fail-closed semantics.
    def test_missing_or_malformed_local_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            root=Path(directory)
            scenario,_=load('paper-base')
            scenario['inputs']=['bundle:hardware.json','bundle:models.json','bundle:workload.json','bundle:economics.json','bundle:sampler.json','prices.json']
            path=root/'scenario.json';path.write_text(json.dumps(scenario))
            for malformed in (False,True):
                if malformed:(root/'prices.json').write_text('{broken')
                result=run(str(path),['workload.sample_calls=1'])
                self.assertTrue(any(a['input']=='prices.rental_gpu_hour' for a in result['alarms']))
                self.assertEqual(result['tables'][0]['rows'][0]['calls'],1)

    # One invalid cohort value cannot erase independent cohort rows from the table shape.
    def test_invalid_user_entry_preserves_other_cohorts(self):
        baseline=run('service-fp8',['workload.sample_calls=1'])
        changed=run('service-fp8',['workload.sample_calls=1','service.users.1=NaN'])
        before=next(t for t in baseline['tables'] if t['name'].startswith('Service GPU'))['rows']
        after=next(t for t in changed['tables'] if t['name'].startswith('Service GPU'))['rows']
        self.assertEqual(len(before),len(after))
        for a,b in zip(before,after):
            if a['users']==100:self.assertTrue(is_alarm(b['gpus']))
            else:self.assertEqual(a,b)


class CatalogueTests(unittest.TestCase):
    # A null catalogue is a scoped input alarm, never an attribute/iteration crash that suppresses independent tables.
    def test_null_catalogues_preserve_unrelated_results(self):
        scenario,inputs=load('paper-base',['workload.sample_calls=1'])
        baseline=calculate(scenario,inputs)
        inputs.data['edge']=None
        result=calculate(scenario,inputs)
        self.assertEqual(result['tables'][0],baseline['tables'][0])
        name=next(t['name'] for t in baseline['tables'] if t['name'].startswith('API and'))
        self.assertEqual(tables(result)[name],tables(baseline)[name])
        self.assertTrue(any(a['input']=='edge' for a in result['alarms']))
        from hybridcalc.service import calculate as service
        scenario,inputs=load('service-fp8',['workload.sample_calls=1'])
        before=service(scenario,inputs)
        inputs.data['service']['profiles']=None
        after=service(scenario,inputs)
        self.assertEqual(after['tables'][0],before['tables'][0])
        self.assertTrue(any(a['input']=='service.profiles' for a in after['alarms']))


class PrecisionControlTests(unittest.TestCase):
    # Full utilization has the independently calculated nonzero GPU price; a missing benchmark only alarms benchmark-dependent cells.
    def test_full_utilization_and_missing_depth_package(self):
        from unittest.mock import patch
        with patch('hybridcalc.analysis_graph.sampled_calls',return_value=[(0,1000,100,2)]):
            result=run('paper-base',['workload.sample_calls=1','economics.rental_utilization=1'])
        row=next(row for t in result['tables'] if t['name'].startswith('Prefill and') for row in t['rows'] if row['variant']=='Rented shadow prefill')
        self.assertAlmostEqual(row['per_1000_calls'],1100*54e9/(4.5e15*.3)*9.5/3600*1000)
        scenario,inputs=load('paper-base',['workload.sample_calls=1'])
        baseline=calculate(scenario,inputs)
        inputs.data['measurements']['depth']['path']='.temp/hybrid-calc-r2-261030/missing-depth.jsonl'
        changed=calculate(scenario,inputs)
        curve=next(t for t in changed['tables'] if t['name'].startswith('M3 Max'))
        self.assertTrue(curve['alarms'])
        self.assertTrue(all(is_alarm(row['rate']) for row in curve['rows']))
        before=next(t for t in baseline['tables'] if t['name'].startswith('API and'))['rows'][0]
        after=next(t for t in changed['tables'] if t['name'].startswith('API and'))['rows'][0]
        self.assertEqual(before,after)


class TopologyTests(unittest.TestCase):
    # A missing inter-node message width cannot change single-machine GLM metrics or full-mix API prices.
    def test_pair_only_input_does_not_taint_single_machine(self):
        scenario,inputs=load('glm-tier2',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['models']['glm']['hidden_width']
        after=calculate(scenario,inputs)
        self.assertEqual(after['alarms'],[{'input':'models.glm.hidden_width','reason':'missing input'}])
        a=next(t for t in before['tables'] if t['name'].startswith('Decode'))['rows']
        b=next(t for t in after['tables'] if t['name'].startswith('Decode'))['rows']
        self.assertEqual(a[:2],b[:2])
        for row in b[2:]:self.assertTrue(is_alarm(row['tok_s_stream']))
        name=next(t['name'] for t in before['tables'] if t['name'].startswith('API and'))
        self.assertEqual(tables(before)[name],tables(after)[name])


class SnapshotContractTests(unittest.TestCase):
    # Invalid full05 counts alarm their own cell, leave valid date metadata intact, and cannot affect full04 API denominators.
    def test_invalid_date_count_is_scoped_to_its_metric(self):
        import hashlib
        scenario,inputs=load('paper-base',['workload.sample_calls=1'])
        before=calculate(scenario,inputs)
        document=inputs.measured_json('dates');document['agents']['all']['calls']=True
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            path=Path(directory)/'dates.json';content=json.dumps(document).encode();path.write_bytes(content)
            inputs.data['measurements']['dates']['path']=str(path)
            inputs.data['measurements']['dates']['sha256']=hashlib.sha256(content).hexdigest()
            after=calculate(scenario,inputs)
        dates=next(t for t in after['tables'] if t['name'].startswith('Separate call-date'))['rows'][0]
        self.assertTrue(is_alarm(dates['calls']))
        self.assertEqual(dates['contexts'],13175)
        self.assertEqual(dates['first'],document['agents']['all']['call_time']['first_utc'])
        name=next(t['name'] for t in before['tables'] if t['name'].startswith('API and'))
        self.assertEqual(tables(before)[name],tables(after)[name])


class ScenarioErrorTests(unittest.TestCase):
    # Invalid scenario shapes are command errors with no numeric output and no raw traceback.
    def test_malformed_scenario_shape_has_no_traceback(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.temp') as directory:
            path=Path(directory)/'bad.json'
            for document in ([], {'name':'bad','kind':'service','inputs':[None]}):
                path.write_text(json.dumps(document))
                result=subprocess.run([sys.executable,'-m','hybridcalc','run',str(path)],cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertEqual(result.stdout,'')
                self.assertIn('hybridcalc:',result.stderr)
                self.assertNotIn('Traceback',result.stderr)


if __name__=='__main__':
    unittest.main()
