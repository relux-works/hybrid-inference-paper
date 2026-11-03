"""R7 timings, sensitivity and architecture reproduction have explicit numerical claims."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run


def table(result,key):return next(t for t in result['tables'] if t['id']==key)


class R7TablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=run('paper-tables-r7',['workload.sample_calls=232'])

    # Exactly four charts cover both state representations, with the requested turn/one-shot/sensitivity grids and architecture rows.
    def test_named_tables(self):
        self.assertEqual({t['id'] for t in self.result['tables']},{'turn_speedup','oneshot_ingest','decode_sensitivity','arch_compare'})
        for key,count in [('turn_speedup',48),('oneshot_ingest',36),('decode_sensitivity',32),('arch_compare',8)]:
            self.assertEqual(len(table(self.result,key)['rows']),count)
        for t in self.result['tables']:self.assertEqual({r['state_format'] for r in t['rows']},{'f32','bf16'})

    # A hybrid turn pays each declared component, uses measured KV/fixed state, and exposes losing links as speedup below one.
    def test_turn_components(self):
        rows=table(self.result,'turn_speedup')['rows']
        self.assertTrue(any(x['speedup']>1 for x in rows))
        for x in rows:
            self.assertEqual(x['kv_bytes_token'],34844)
            self.assertEqual(x['state_bytes'],156894784*(.5 if x['state_format']=='bf16' else 1))
            self.assertEqual(x['payload_bytes'],x['portion']*34844+x['state_bytes'])
            self.assertAlmostEqual(x['hybrid_s'],x['server_reload_s']+x['server_prefill_s']+x['transfer_s']+x['import_s']+x['last_token_s'])
            self.assertAlmostEqual(x['speedup'],x['local_prefill_s']/x['hybrid_s'])
            self.assertGreater(x['import_s'],0);self.assertGreater(x['last_token_s'],0)

    # One-shot load starts at depth zero, transfers the full context and charges import/evaluation in TTFT, with identical local time at every link.
    def test_oneshot_components(self):
        for x in table(self.result,'oneshot_ingest')['rows']:
            self.assertEqual(x['start_depth'],0)
            self.assertEqual(x['payload_bytes'],x['context']*34844+x['state_bytes'])
            self.assertAlmostEqual(x['hybrid_ttft_s'],x['server_reload_s']+x['server_prefill_s']+x['transfer_s']+x['import_s']+x['last_token_s'])
            self.assertAlmostEqual(x['speedup'],x['local_s']/x['hybrid_ttft_s'])
        for context in (100000,200000,262000):
            values={x['local_s'] for x in table(self.result,'oneshot_ingest')['rows'] if x['context']==context}
            self.assertEqual(len(values),1)

    # Decode factors scale single-stream rates without changing the measured four-stream anchor gain; physically impossible rates alarm capacity cells.
    def test_decode_sensitivity(self):
        rows=table(self.result,'decode_sensitivity')['rows']
        for x in rows:
            self.assertAlmostEqual(x['anchor_gain'],1.665015442445748)
            self.assertIn('hypothetical' if x['decode_scale']>1 else 'anchor',x['decode_basis'])
            if x['decode_scale']==3:
                for key in ('local_sessions_day','hybrid_sessions_day','gain'):self.assertIn('alarm',x[key])
            else:
                self.assertGreaterEqual(x['hybrid_sessions_day'],x['local_sessions_day'])
                self.assertAlmostEqual(x['gain'],x['hybrid_sessions_day']/x['local_sessions_day'])
        for client in {x['client'] for x in rows}:
            for state in ('f32','bf16'):
                for link in (300,1000):
                    group=sorted((x for x in rows if x['client']==client and x['state_format']==state and x['link_mbit']==link and x['decode_scale']<=2),key=lambda x:x['decode_scale'])
                    self.assertEqual([x['local_sessions_day'] for x in group],sorted(x['local_sessions_day'] for x in group))


class R7ArchitectureTests(unittest.TestCase):
    # All original numeric f32 fields match execution of the attached script; its unsupported None values become explicit context alarms.
    def test_attached_script_numbers(self):
        import csv,shutil,subprocess,tempfile
        fixture=Path(__file__).parent/'fixtures/arch_compare_r7.py'
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'arch_compare.py';shutil.copyfile(fixture,path)
            result=subprocess.run([sys.executable,str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            expected=list(csv.DictReader((Path(tmp)/'arch-compare.csv').read_text().splitlines()))
        actual=[r for r in table(run('paper-tables-r7',['workload.sample_calls=1']),'arch_compare')['rows'] if r['state_format']=='f32']
        self.assertEqual([x['model'] for x in actual],[x['model'] for x in expected])
        for x,y in zip(actual,expected):
            for k,v in y.items():
                if k in ('model','kind'):continue
                if v=='':self.assertIn('alarm',x[k])
                else:self.assertEqual(float(x[k]),float(v),(x['model'],k))

    # Window KV saturates at W and Gemma shared K=V stores one global array; bf16 changes only recurrent Qwen state, not sliding-window cache.
    def test_architecture_state_geometry(self):
        rows=table(run('paper-tables-r7',['workload.sample_calls=1']),'arch_compare')['rows']
        by={(x['model'],x['state_format']):x for x in rows}
        q=by[('Qwen3.8-27B','f32')];self.assertEqual(q['kv_full_bytes_token'],34816)
        self.assertEqual(q['fixed_mb'],156.9)
        for x in rows:
            y=by[(x['model'],'bf16' if x['state_format']=='f32' else 'f32')]
            if x['model']!='Qwen3.8-27B':
                for k in ('kv_full_bytes_token','fixed_mb','delta_1k_mb','delta_10k_mb'):self.assertEqual(x[k],y[k])
        gem=by[('Gemma 4 31B','f32')];self.assertEqual(gem['kv_full_bytes_token'],21760);self.assertEqual(gem['swa_bytes_token'],435200)
        old=by[('Qwen3-32B','f32')];self.assertEqual(old['within_context_131k'],0);self.assertIsInstance(old['client_prefill_1k_131k_s'],float)


class R7CornerTests(unittest.TestCase):
    @staticmethod
    def changed(mutate,overrides=('workload.sample_calls=1',)):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables_r7 import calculate
        s,i=load('paper-tables-r7',overrides);mutate(i.data)
        return calculate(s,i)

    # Removing import efficiency creates one precise new alarm and preserves local/server/transfer components and the architecture table.
    def test_import_gap_control(self):
        a=run('paper-tables-r7',['workload.sample_calls=1']);b=self.changed(lambda d:d['r7'].pop('import_efficiency'))
        self.assertEqual([x for x in b['alarms'] if x not in a['alarms']],[{'input':'r7.import_efficiency','reason':'missing input'}])
        self.assertEqual(table(a,'arch_compare'),table(b,'arch_compare'))
        for x,y in zip(table(a,'turn_speedup')['rows'],table(b,'turn_speedup')['rows']):
            for k in ('local_prefill_s','server_prefill_s','transfer_s','last_token_s'):self.assertEqual(x[k],y[k])
            self.assertIn('alarm',y['hybrid_s'])

    # Zero/absent bandwidth forbids offload while local/server timings stay numeric; a slow valid link yields speedup below one without a gap.
    def test_link_corner(self):
        for value in (0,None):
            r=run('paper-tables-r7',['workload.sample_calls=1','r7.links.0='+('null' if value is None else str(value))])
            x=table(r,'turn_speedup')['rows'][0]
            self.assertIn('alarm',x['hybrid_s']);self.assertIsInstance(x['local_prefill_s'],float);self.assertIsInstance(x['server_prefill_s'],float)
        r=self.changed(lambda d:d['r7']['links'].__setitem__(0,None));self.assertIn('alarm',table(r,'oneshot_ingest')['rows'][0]['transfer_s'])
        slow=run('paper-tables-r7',['workload.sample_calls=1','r7.links.0=1000000'])
        self.assertLess(table(slow,'turn_speedup')['rows'][0]['speedup'],1)

    # Spans at depth zero and the actual context limit are valid; overflowing the limit or memory alarms capacity instead of calculating impossible timings.
    def test_context_and_memory(self):
        a=run('paper-tables-r7',['workload.sample_calls=1','r7.turn.depths.0=0','r7.oneshot.contexts.2=262144'])
        self.assertIsInstance(table(a,'turn_speedup')['rows'][0]['local_prefill_s'],float)
        self.assertIsInstance(table(a,'oneshot_ingest')['rows'][12]['local_s'],float)
        bad=run('paper-tables-r7',['workload.sample_calls=1','r7.oneshot.contexts.2=262145'])
        self.assertTrue(any(x['input']=='r7.context_limit' for x in bad['alarms']))
        nofit=run('paper-tables-r7',['workload.sample_calls=1','hardware.clients.m3max.memory=16000000000'])
        x=table(nofit,'turn_speedup')['rows'][0];self.assertIn('alarm',x['local_prefill_s']);self.assertIn('alarm',x['hybrid_s']);self.assertIsInstance(x['server_prefill_s'],float)

    # Empty real mix alarms only sensitivity; single call is valid, and missing/hash-corrupt measurements alarm their actual consumers.
    def test_mix_and_measurements(self):
        a=run('paper-tables-r7',['workload.sample_calls=0']);b=run('paper-tables-r7',['workload.sample_calls=1'])
        for key in ('turn_speedup','oneshot_ingest','arch_compare'):self.assertEqual(table(a,key),table(b,key))
        self.assertIn('alarm',table(a,'decode_sensitivity')['rows'][0]['local_sessions_day'])
        self.assertIsInstance(table(b,'decode_sensitivity')['rows'][0]['local_sessions_day'],float)
        for key in ('depth','normalized'):
            for field,value in [('path','.temp/hybrid-calc-r7-261030/absent.json'),('sha256','0'*64)]:
                r=self.changed(lambda d:d['measurements'][key].__setitem__(field,value))
                self.assertTrue(any(x['input']=='measurements.'+key for x in r['alarms']))
                self.assertGreater(r['computed_metrics'],0)

    # More bandwidth cannot increase transfer, bf16 reduces transferred state, and integration refinement stays stable for the requested spans.
    def test_invariants_and_integration(self):
        from hybridcalc.paper_tables_r7 import integrate_span,import_time,hybrid_time
        from hybridcalc.inputs import InputGap
        self.assertAlmostEqual(integrate_span(lambda x:2*x+3,5,100,7),11300)
        self.assertEqual(integrate_span(lambda x:1,0,0,1),0)
        with self.assertRaisesRegex(InputGap,'step'):integrate_span(lambda x:1,0,1,0)
        self.assertEqual(import_time(1000,100,.5,2,3),43)
        self.assertEqual(hybrid_time(1,2,3,4),10)
        a=run('paper-tables-r7',['workload.sample_calls=1']);b=run('paper-tables-r7',['workload.sample_calls=1','r7.integration_step=128'])
        for key,local in [('turn_speedup','local_prefill_s'),('oneshot_ingest','local_s')]:
            rows=table(a,key)['rows']
            for x,y in zip(rows,table(b,key)['rows']):self.assertAlmostEqual(x[local]/y[local],1,delta=1e-4)
            for i in range(0,len(rows),6):self.assertEqual([x['transfer_s'] for x in rows[i:i+6]],sorted((x['transfer_s'] for x in rows[i:i+6]),reverse=True))
        rows=table(a,'turn_speedup')['rows']
        for x in rows:
            if x['state_format']=='f32':
                y=next(y for y in rows if y['state_format']=='bf16' and all(y[k]==x[k] for k in ('depth','portion','link_mbit')))
                self.assertLess(y['transfer_s'],x['transfer_s']);self.assertEqual(y['local_prefill_s'],x['local_prefill_s'])

    # Fixed overhead/last-token zero are explicit valid controls; nonfinite values, unknown paths and unsupported quant changes alarm or reject clearly.
    def test_overrides_and_zero(self):
        from hybridcalc.inputs import InputError
        with self.assertRaisesRegex(InputError,'unknown override'):run('paper-tables-r7',['r7.typo=1'])
        for expr in ('r7.import_efficiency=NaN','r7.last_token_tokens=Infinity','r7.turn.portions.0=0','owners.client_quant=Q3'):
            r=run('paper-tables-r7',['workload.sample_calls=1',expr]);self.assertTrue(any(x['input']==expr.split('=')[0] for x in r['alarms']))
        zero=run('paper-tables-r7',['workload.sample_calls=1','r7.last_token_tokens=0','r7.import_fixed_s=0'])
        self.assertEqual(table(zero,'turn_speedup')['rows'][0]['last_token_s'],0)

    # A source gap in one architecture config alarms that model's dependent fields; unrelated models keep their own geometry.
    def test_architecture_gap_and_relation(self):
        r=self.changed(lambda d:d['r7']['arch']['models']['glimmer']['sliding'].pop('window'))
        rows=table(r,'arch_compare')['rows']
        for x in rows:
            if x['model']=='Muse Glimmer 30B':self.assertIn('alarm',x['delta_10k_mb'])
            else:self.assertIsInstance(x['delta_10k_mb'],float)
        r=run('paper-tables-r7',['workload.sample_calls=1','r7.arch.models.glimmer.sliding.window=0'])
        x=next(x for x in table(r,'arch_compare')['rows'] if x['model']=='Muse Glimmer 30B')
        self.assertIn('alarm',x['delta_1k_mb'])


class R7InputTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        parts=path.split('.');cur=data
        for part in parts[:-1]:cur=cur[int(part)] if isinstance(cur,list) else cur[part]
        return cur,int(parts[-1]) if isinstance(cur,list) else parts[-1]

    # Every new quantity is consumed; deletion alarms each declared dependent cell at its exact path, with no code fallback.
    def test_every_new_input_gap(self):
        import json
        from hybridcalc.engine import load
        from hybridcalc.inputs import DATA,leaves
        from hybridcalc.paper_tables_r7 import calculate
        scenario,inputs=load('paper-tables-r7',['workload.sample_calls=1']);before=calculate(scenario,inputs)
        for path,q in leaves(json.loads((DATA/'paper-tables-r7.json').read_text())):
            cells=[(t['id'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
            with self.subTest(path=path):
                self.assertTrue(cells,'new quantity not consumed')
                _,inputs=load('paper-tables-r7',['workload.sample_calls=1']);parent,key=self.parent(inputs.data,path)
                if isinstance(parent,list):parent[key]=None
                else:del parent[key]
                after=calculate(scenario,inputs);by_id={t['id']:t for t in after['tables']}
                self.assertTrue(any(a['input']==path for a in after['alarms']))
                for id,cell in cells:
                    row,column=cell.split('.',1);v=by_id[id]['rows'][int(row)][column]
                    self.assertIsInstance(v,dict,(path,id,cell));self.assertTrue(any(a['input']==path for a in v['alarm']),(path,id,cell))

    # Every new quantity rejects null/nonfinite/negative, bad units and absent provenance; explicit zero-permitted contracts have valid zero controls.
    def test_quantity_contracts(self):
        import copy,json
        from hybridcalc.engine import load
        from hybridcalc.inputs import DATA,InputGap,leaves,match
        _,inputs=load('paper-tables-r7')
        for path,q in leaves(json.loads((DATA/'paper-tables-r7.json').read_text())):
            original=copy.deepcopy(inputs.locate(path));self.assertEqual(inputs.get(path),original['value'])
            for field,value in [('value',None),('value',float('nan')),('value',float('inf')),('value',-1),('unit','wrong'),('provenance',None)]:
                with self.subTest(path=path,field=field):
                    parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original);parent[key][field]=value
                    with self.assertRaises(InputGap) as e:inputs.get(path)
                    self.assertEqual(e.exception.path,path)
            parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original)
            pattern='.'.join('*' if x.isdigit() else x for x in path.split('.'))
            rule=next(v for k,v in inputs._contracts.items() if match(k,pattern))
            parent[key]['value']=0
            if rule.get('minimum',0)==0 and not rule.get('exclusive_minimum',False):self.assertEqual(inputs.get(path),0)
            else:
                with self.assertRaises(InputGap):inputs.get(path)
            parent[key]=copy.deepcopy(original)

    # A malformed grid alarms shape-dependent cells without losing independent charts, and no list shrink silently selects an alternative transfer bandwidth.
    def test_container_gaps(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables_r7 import calculate
        for path in ('r7.links','r7.turn.depths','r7.turn.portions','r7.oneshot.contexts','r7.decode.links','r7.decode.scales','r7.arch.links'):
            for value in (None,[],{}):
                s,i=load('paper-tables-r7',['workload.sample_calls=1']);parent,key=self.parent(i.data,path);parent[key]=value
                result=calculate(s,i)
                self.assertTrue(any(x['input']==path for x in result['alarms']));self.assertGreater(result['computed_metrics'],0)

    # Unknown query-head count does not change independent cache geometry/bytes; precise dependencies preserve computable architecture metrics.
    def test_architecture_independent_geometry(self):
        a=run('paper-tables-r7',['workload.sample_calls=1'])
        b=R7CornerTests.changed(lambda d:d['r7']['arch']['models']['glimmer']['full'].pop('q_heads'))
        for x,y in zip(table(a,'arch_compare')['rows'],table(b,'arch_compare')['rows']):
            if x['model']=='Muse Glimmer 30B':
                for k in ('kv_full_bytes_token','fixed_mb','delta_1k_mb','delta_10k_mb'):self.assertEqual(x[k],y[k])
                self.assertIn('alarm',y['client_prefill_1k_131k_s'])
            else:self.assertEqual(x,y)

    # Four R7 CSVs and namespaced sidecars retain exact numeric/alarm cells, round-trip deterministically and never overwrite R5/R6 files.
    def test_export(self):
        import csv,json,tempfile
        from hybridcalc.export import write_tables
        r=run('paper-tables-r7',['workload.sample_calls=1'])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for f in ('manifest.json','r6_manifest.json','perimeter_cost.csv'):(p/f).write_text('prior artifact')
            write_tables(r,p)
            for f in ('manifest.json','r6_manifest.json','perimeter_cost.csv'):self.assertEqual((p/f).read_text(),'prior artifact')
            self.assertEqual(len(json.loads((p/'r7_manifest.json').read_text())['tables']),4)
            for t in r['tables']:
                rows=list(csv.DictReader((p/(t['id']+'.csv')).read_text().splitlines()));self.assertEqual(len(rows),len(t['rows']))
                for x,y in zip(rows,t['rows']):
                    for k,v in y.items():
                        if isinstance(v,dict):self.assertEqual(x[k],'nan');self.assertEqual(x['status'],'alarm')
                        elif type(v) in (int,float):self.assertEqual(float(x[k]),v)
            before={f.name:f.read_bytes() for f in p.iterdir()};write_tables(r,p)
            self.assertEqual(before,{f.name:f.read_bytes() for f in p.iterdir()})


class R7PhysicsTests(unittest.TestCase):
    # Exact bandwidth efficiency one is valid; values above it cannot become a useful unchanged-traffic capacity. Higher prefill compute cannot make server time increase.
    def test_bandwidth_and_compute_limits(self):
        from hybridcalc.paper_tables_r7 import scale_guard
        from hybridcalc.inputs import InputGap
        self.assertEqual(scale_guard(2,.5,'input'),2)
        with self.assertRaisesRegex(InputGap,'raw bandwidth'):scale_guard(2.01,.5,'input')
        a=run('paper-tables-r7',['workload.sample_calls=1'])
        b=run('paper-tables-r7',['workload.sample_calls=1','service.mfu=0.6'])
        for x,y in zip(table(a,'turn_speedup')['rows'],table(b,'turn_speedup')['rows']):
            self.assertAlmostEqual(y['server_prefill_s']*2,x['server_prefill_s'])
            self.assertEqual(x['local_prefill_s'],y['local_prefill_s'])
            self.assertLessEqual(y['hybrid_s'],x['hybrid_s'])
        invalid=run('paper-tables-r7',['workload.sample_calls=1','service.mfu=0'])
        x=table(invalid,'turn_speedup')['rows'][0];self.assertIn('alarm',x['server_prefill_s']);self.assertIsInstance(x['local_prefill_s'],float)

    # Anchor gain is observed, not an assumption multiplied by the requested speed factor; actual modeled four-stream aggregate retains that gain at32k.
    def test_actual_four_stream_gain(self):
        r=run('paper-tables-r7',['workload.sample_calls=1'])
        for x in table(r,'decode_sensitivity')['rows']:
            self.assertAlmostEqual(x['four_aggregate_tok_s_32k']/x['single_tok_s_32k'],1.665015442445748)
            self.assertGreaterEqual(x['min_streams'],1);self.assertLessEqual(x['max_streams'],4)
