"""Run8 review regressions, measured sampler calibration and paper example claims."""
import json,math,sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run
from hybridcalc.inputs import DATA,Inputs,InputGap,leaves,match
from hybridcalc.paper_tables_r8 import calculate


def table(result,key):return next(t for t in result['tables'] if t.get('id')==key)
def quantity(value,unit,reason):return dict(value=value,unit=unit,provenance=dict(kind='estimate',reason=reason))


class ReviewRegressionTests(unittest.TestCase):
    # The review's historical output-plus-reasoning original-mix fleet boundary needs two B300 nodes when every client call is shadowed; HBM isolates this from cold-tier migration.
    def test_full_shadow_two_node_boundary(self):
        from hybridcalc.paper_tables_r6 import calculate
        s,i=load('paper-tables-r6',['workload.reasoning_extra_fraction=1'])
        i.data['sampler']['mode']=quantity('legacy_lognormal','sampler law','Regression isolates the independently reviewed original mix.')
        i.data.setdefault('hosting',{})['tier']=quantity('HBM','storage tier','Isolate shadow accounting from cold-tier reload work.')
        r=calculate(s,i)
        x=next(x for x in table(r,'perimeter_cost')['rows'] if x['profile']=='light' and x['team']==5000 and x['client'].startswith('M5 Max 64') and x['basis']=='Mac already owned' and x['server'].startswith('Owned HGX'))
        self.assertEqual(x['units'],2)

    # The current paper mix must match measured token-mass tails, rather than a twice-heavy >=10k/>=30k lognormal tail.
    def test_measured_token_tail(self):
        from hybridcalc.paper_tables import Context
        s,i=load('paper-tables');c=Context(s,i);calls=c.g.resolve(c.valid).value
        stats=i.measured_json('stats')['agents']['all'];total=sum(x[1] for x in calls)
        for cutoff,label in [(2000,'>=2k'),(5000,'>=5k'),(10000,'>=10k'),(30000,'>=30k')]:
            self.assertAlmostEqual(sum(x[1] for x in calls if x[1]>=cutoff)/total,stats['share_of_new_tokens_in_calls'][label],delta=.015)
        self.assertAlmostEqual(total/len(calls),stats['new_in_per_call']['mean'],delta=12)

    # A positive cold-tier session budget must appear explicitly in GPU/person pricing; compute-only billing is the old forbidden behavior.
    def test_hosting_is_in_gpu_month(self):
        r=run('paper-tables',['workload.sample_calls=232'])
        x=table(r,'person_cost_s20')['rows'][0]
        self.assertIn('hosting_month',x)
        self.assertGreater(x['hosting_month'],0)
        self.assertAlmostEqual(x['gpu_month'],x['compute_month']+x['hosting_month'])
        self.assertAlmostEqual(x['hosting_month'],x['storage_month']+x['migration_month'])

    # Recalibrated bins retain the measured depth dependence and all three global means, on the pooled all-agent corpus.
    def test_conditional_means_and_global_means(self):
        from hybridcalc.paper_tables import Context
        s,i=load('paper-tables');c=Context(s,i);rows=c.g.resolve(c.valid).value
        stats=i.measured_json('stats')['agents']['all']
        for cutoff,upper,label in [(0,50000,'<50k'),(50000,100000,'50-100k'),(100000,200000,'100-200k'),(200000,float('inf'),'200k+')]:
            values=[n for d,n,o,t in rows if cutoff<=d<upper]
            self.assertAlmostEqual(sum(values)/len(values),stats['new_in_by_depth'][label]['mean'],delta=20)
        depths=sorted(x[0] for x in rows)
        for probability,label in [(.1,'p10'),(.25,'p25'),(.5,'p50'),(.75,'p75'),(.9,'p90'),(.99,'p99')]:
            self.assertAlmostEqual(depths[int(probability*len(depths))],stats['depth_per_call'][label],delta=300)
        for column,target in [(0,stats['depth_per_call']['mean']),(1,stats['new_in_per_call']['mean']),(2,stats['output_per_call']['mean'])]:
            self.assertAlmostEqual(sum(x[column] for x in rows)/len(rows),target,places=6)


class R8TablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=run('paper-tables-r8',['workload.sample_calls=232'])

    # The four requested charts are named, rectangular and carry transitive input declarations for every metric.
    def test_named_tables(self):
        self.assertEqual({t['id']:len(t['rows']) for t in self.result['tables']},{'people_per_gpu':6,'transcript_example':6,'flop_per_byte':432,'reasoning_on_top_sensitivity':16})
        for t in self.result['tables']:
            for j,row in enumerate(t['rows']):
                self.assertEqual(set(row),set(t['columns']))
                for col,value in row.items():
                    self.assertIn(str(j)+'.'+col,t['dependencies'])
                    if type(value) in (float,int):self.assertTrue(math.isfinite(value))

    # Each new table exports its exact structured numeric values, while context alarms become nan with detailed sidecar reasons; a second export is byte-stable.
    def test_csv_export(self):
        import csv,tempfile
        from hybridcalc.export import write_tables
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);manifest=write_tables(self.result,directory)
            self.assertEqual(len(manifest['tables']),4)
            for t in self.result['tables']:
                rows=list(csv.DictReader((directory/(t['id']+'.csv')).read_text().splitlines()))
                self.assertEqual(len(rows),len(t['rows']))
                for actual,expected in zip(rows,t['rows']):
                    for col,value in expected.items():
                        if type(value) in (float,int):self.assertEqual(float(actual[col]),value)
                        elif isinstance(value,dict):self.assertEqual(actual[col],'nan');self.assertEqual(actual['status'],'alarm')
            before={p.name:p.read_bytes() for p in directory.iterdir()};write_tables(self.result,directory)
            self.assertEqual(before,{p.name:p.read_bytes() for p in directory.iterdir()})

    # People-per-GPU rounds DOWN and charges full input/output shadow plus cold migration, without applying a Mac capacity cap.
    def test_people_per_gpu(self):
        rows=table(self.result,'people_per_gpu')['rows']
        for x in rows:
            budget=x['hours']*3600*x['load'];demand=x['calls_user_day']
            self.assertEqual(demand,2500*x['share'])
            self.assertEqual(x['people_compute_only'],math.floor(budget/demand/x['shadow_gpu_s_call']))
            self.assertEqual(x['people_with_hosting'],math.floor(budget/demand/(x['shadow_gpu_s_call']+x['migration_gpu_s_call'])))
            self.assertLessEqual(x['people_with_hosting'],x['people_compute_only'])
        for option in {x['gpu'] for x in rows}:
            xs=[x['people_with_hosting'] for x in rows if x['gpu']==option];self.assertEqual(xs,sorted(xs,reverse=True))

    # Transcript TTFT pays all four cold-ingest components and totals add exactly 3000 single-stream decoded tokens once; tariffs use fresh input.
    def test_transcript_example(self):
        rows=table(self.result,'transcript_example')['rows'];_,i=load('paper-tables-r8')
        for x in rows:
            self.assertAlmostEqual(x['hybrid_ttft_s'],sum(x[k] for k in ('server_prefill_s','transfer_s','import_s','last_token_s')))
            self.assertAlmostEqual(x['local_total_s'],x['local_ttft_s']+x['summary_decode_s'])
            self.assertAlmostEqual(x['hybrid_total_s'],x['hybrid_ttft_s']+x['summary_decode_s'])
            for column,api in [('api_median','qwen_median'),('api_cheapest','qwen_cheap')]:
                expected=(70000*i.get('prices.apis.'+api+'.cache_write')+3000*i.get('prices.apis.'+api+'.output'))/1e6
                self.assertEqual(x[column],expected)
        for client in {x['client'] for x in rows}:
            a,b=[x for x in rows if x['client']==client]
            self.assertGreater(a['hybrid_ttft_s'],b['hybrid_ttft_s']);self.assertEqual(a['local_ttft_s'],b['local_ttft_s'])

    # Intensity includes the fixed 1k delta, uses peak/link byte throughput and alarms every unsupported context rather than extrapolating configs.
    def test_flop_per_byte(self):
        rows=table(self.result,'flop_per_byte')['rows']
        for x in rows:
            self.assertAlmostEqual(x['client_flop_byte'],x['client_peak_flop_s']/(x['link_mbit']*1e6/8))
            if x['depth']>x['context_limit']:
                for k in ('flop_new_token','model_flop_byte','ratio','beats_ideal_local'):self.assertIn('alarm',x[k])
            else:
                self.assertAlmostEqual(x['model_flop_byte'],x['flop_new_token']*x['portion_tokens']/x['delta_bytes'])
                self.assertAlmostEqual(x['ratio'],x['model_flop_byte']/x['client_flop_byte'])
                self.assertEqual(x['beats_ideal_local'],int(x['ratio']>1))
        q=next(x for x in rows if x['model']=='Qwen3.8-27B')
        self.assertEqual(q['delta_bytes'],1000*34844+156894784)

    # Output-only has the identical input mix but lower decoded demand, greater client capacity and lower API/shadow bills; output-only is the base and fraction 1 is an upper bound.
    def test_output_only_sensitivity(self):
        rows=table(self.result,'reasoning_on_top_sensitivity')['rows']
        self.assertEqual({x['reasoning_extra_fraction'] for x in rows},{0,1})
        for x in rows:
            if x['reasoning_extra_fraction']!=0:continue
            y=next(y for y in rows if y['reasoning_extra_fraction']==1 and all(y[k]==x[k] for k in ('client','share','basis')))
            self.assertGreater(x['capacity_day'],y['capacity_day'])
            self.assertLess(x['compute_per_call'],y['compute_per_call'])
            self.assertLess(x['api_median'],y['api_median']);self.assertLess(x['api_cheapest'],y['api_cheapest'])
            self.assertLessEqual(x['hybrid_median'],y['hybrid_median'])
        _,i=load('paper-tables-r8');self.assertEqual(i.get('workload.reasoning_extra_fraction'),0)


class R8GapCornerTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        cur=data;parts=path.split('.')
        for p in parts[:-1]:cur=cur[int(p)] if isinstance(cur,list) else cur[p]
        return cur,int(parts[-1]) if isinstance(cur,list) else parts[-1]
    @staticmethod
    def changed(path,value=None,missing=False):
        s,i=load('paper-tables-r8',['workload.sample_calls=232'])
        parent,key=R8GapCornerTests.parent(i.data,path)
        if missing:
            if isinstance(parent,list):parent[key]=None
            else:del parent[key]
        else:parent[key]['value']=value
        return calculate(s,i)

    # Every new quantity is consumed in an active tier and every directly declared dependent cell alarms when it is removed; other paths cannot fabricate a value.
    def test_every_new_input_gap(self):
        layers=['paper-tables-r8.json','hosting.json'];quantities=[]
        for file in layers:quantities.extend(leaves(json.loads((DATA/file).read_text())))
        sampler=json.loads((DATA/'sampler.json').read_text());quantities.extend((p,q) for p,q in leaves(sampler) if p=='sampler.mode' or p.startswith('sampler.fit.'))
        for path,q in quantities:
            tier=path.split('.')[2] if path.startswith('hosting.tiers.') else 'RAM'
            overrides=['workload.sample_calls=232','hosting.tier='+tier]
            s,i=load('paper-tables-r8',overrides);before=calculate(s,i)
            cells=[(t['id'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
            with self.subTest(path=path):
                self.assertTrue(cells,'unused new input')
                s,i=load('paper-tables-r8',overrides);parent,key=self.parent(i.data,path)
                if isinstance(parent,list):parent[key]=None
                else:del parent[key]
                after=calculate(s,i);by_id={t['id']:t for t in after['tables']}
                self.assertTrue(any(a['input']==path for a in after['alarms']),after['alarms'])
                for id,cell in cells:
                    row,col=cell.split('.',1);value=by_id[id]['rows'][int(row)][col]
                    self.assertIsInstance(value,dict,(path,id,cell))
                    self.assertTrue(any(a['input']==path for a in value['alarm']),(path,id,cell,value))

    # Every new numeric contract rejects null, nonfinite, negative, wrong-unit and unprovenanced inputs; permitted zero is checked against its declared contract.
    def test_new_input_contracts(self):
        import copy
        s,i=load('paper-tables-r8')
        quantities=[]
        for file in ('paper-tables-r8.json','hosting.json','sampler.json'):
            quantities.extend(leaves(json.loads((DATA/file).read_text())))
        for path,q in quantities:
            original=copy.deepcopy(i.locate(path))
            for field,value in [('value',None),('value',float('nan')),('value',float('inf')),('value',-1),('unit','wrong'),('provenance',None)]:
                with self.subTest(path=path,field=field):
                    parent,key=self.parent(i.data,path);parent[key]=copy.deepcopy(original);parent[key][field]=value
                    with self.assertRaises(InputGap) as caught:i.get(path)
                    self.assertEqual(caught.exception.path,path)
            parent,key=self.parent(i.data,path);parent[key]=copy.deepcopy(original)
            if isinstance(q['value'],str):continue
            rule=next(v for k,v in i._contracts.items() if match(k,'.'.join('*' if x.isdigit() else x for x in path.split('.'))))
            parent[key]['value']=0
            if rule.get('minimum',0)>0 or rule.get('exclusive_minimum'):
                with self.assertRaises(InputGap):i.get(path)
            else:self.assertEqual(i.get(path),0)
            parent[key]=original

    # A missing hosting price must leave client capacity, compute-only billing and all non-cost example tables unchanged, while hosting/total costs alarm.
    def test_hosting_price_gap_control(self):
        before=run('paper-tables-r8',['workload.sample_calls=232']);after=self.changed('hosting.tiers.RAM.price',missing=True)
        for id in ('transcript_example','flop_per_byte'):self.assertEqual(table(before,id),table(after,id))
        a=table(before,'reasoning_on_top_sensitivity')['rows'][0];b=table(after,'reasoning_on_top_sensitivity')['rows'][0]
        for k in ('capacity_day','compute_month','compute_per_call','api_median','api_cheapest'):self.assertEqual(a[k],b[k])
        for k in ('hosting_month','gpu_month','hybrid_median','hybrid_cheapest'):self.assertIn('alarm',b[k])
        self.assertEqual({x['input'] for x in after['alarms']}-{x['input'] for x in before['alarms']},{'hosting.tiers.RAM.price','output_sensitivity_0.hosting.tiers.RAM.price','output_sensitivity_1.hosting.tiers.RAM.price'})

    # HBM residency needs no PCIe path; cold tiers require a positive PCIe input and account for both reload and spill, including background calls.
    def test_tier_reload_and_pcie_gap(self):
        from hybridcalc.paper_tables import Context
        for tier in ('RAM','NVMe','HBM'):
            s,i=load('paper-tables',['workload.sample_calls=232','hosting.tier='+tier]);c=Context(s,i);cl=c.client('m3max','hardware.links.wan.bandwidth','test')
            calls=c.g.resolve(cl['matched']).value;v=c.g.resolve(cl['hosting']['vector']).value
            if tier=='HBM':self.assertTrue(all(a==b==0 for a,b in v))
            else:
                rate=min(i.get('hosting.pcie_bandwidth'),i.get('hosting.tiers.'+tier+'.bandwidth'))
                for (d,n,o,t),(a,b) in zip(calls,v):
                    self.assertAlmostEqual(a,(d*34844+156894784)/rate)
                    self.assertAlmostEqual(b,((n+o)*34844+156894784)/rate)
            del i.data['hosting']['pcie_bandwidth']
            other=Context(s,i);cc=other.client('m3max','hardware.links.wan.bandwidth','test')
            self.assertEqual(bool(other.g.resolve(cc['capacity']).alarms),tier!='HBM')

    # Zero storage price/fraction are valid without erasing paid migration; zero bandwidth/load and NaN produce exact-path alarms, never infinities.
    def test_zero_and_nonfinite(self):
        for path in ('hosting.tiers.RAM.price','hosting.month_fraction'):
            r=run('paper-tables-r8',['workload.sample_calls=232','hosting.tiers.RAM.price=0','hosting.tiers.NVMe.price=0']) if path=='hosting.tiers.RAM.price' else self.changed(path,0);x=table(r,'reasoning_on_top_sensitivity')['rows'][0]
            self.assertEqual(x['storage_month'],0);self.assertGreater(x['migration_month'],0)
        for path,value in [('hosting.pcie_bandwidth',0),('owners.load',0),('r8.links.0',0),('r8.transcript.links.0',float('inf')),('r8.portion',float('nan'))]:
            with self.subTest(path=path):self.assertTrue(any(x['input']==path for x in self.changed(path,value)['alarms']))

    # The Air's standard developer reserve cannot fit the transcript; its explicit appliance budget is valid, with zero summary and depth-zero neighbors.
    def test_transcript_fit_and_zero_summary(self):
        r=self.changed('r8.transcript.air_reserve',12e9)
        rows=[x for x in table(r,'transcript_example')['rows'] if x['client'].startswith('M5 Air')]
        for x in rows:
            for k in ('local_ttft_s','hybrid_ttft_s','summary_decode_s','local_total_s','hybrid_total_s'):self.assertIn('alarm',x[k])
            self.assertIsInstance(x['server_prefill_s'],float)
        r=self.changed('r8.transcript.summary',0)
        for x in table(r,'transcript_example')['rows']:self.assertEqual(x['summary_decode_s'],0)
        r=self.changed('r8.depths.0',0)
        self.assertTrue(all(type(x['ratio']) is float for x in table(r,'flop_per_byte')['rows'] if x['depth']==0))

    # The sensitivity handles a team of one and invalid/missing sweep shapes with alarms; no raw lookup escapes to CLI.
    def test_sensitivity_corners(self):
        r=self.changed('r8.sensitivity_team',1)
        self.assertEqual({x['team'] for x in table(r,'reasoning_on_top_sensitivity')['rows']},{1})
        for path in ('r8.sensitivity_team','r8.output_fractions.0'):
            r=self.changed(path,missing=True);self.assertTrue(any(x['input']==path for x in r['alarms']))
        s,i=load('paper-tables-r8',['workload.sample_calls=1']);del i.data['r8']['output_fractions'];r=calculate(s,i)
        self.assertTrue(any(x['input']=='r8.output_fractions' for x in r['alarms']))

    # The fitted sampler rejects impossible supports/quantiles and nonconvergence, and preserves empty/single-call behavior as a declared finite-sample limit.
    def test_sampler_corners(self):
        for expr in ('sampler.fit.thresholds.0=2001','sampler.fit.representatives.0=20000','sampler.fit.low_probabilities.1=0.05','sampler.fit.iterations=1'):
            r=run('paper-tables-r8',['workload.sample_calls=232',expr]);self.assertTrue(any(x['input'].startswith('sampler.fit.') for x in r['alarms']))
        for count in (0,1):
            r=run('paper-tables-r8',['workload.sample_calls='+str(count)])
            if count==0:self.assertTrue(any(x['input']=='workload.sample_calls' for x in r['alarms']))
            else:self.assertFalse(table(r,'people_per_gpu')['alarms'])

    # Missing/hash-corrupt measurements alarm the new tables' actual consumers; missing whole namespaces and an unknown override do not escape as lookups.
    def test_measurement_and_layer_gaps(self):
        from hybridcalc.inputs import InputError
        with self.assertRaisesRegex(InputError,'unknown override'):run('paper-tables-r8',['r8.typo=1'])
        for key in ('stats','depth','normalized'):
            for name,value in [('path','.temp/hybrid-calc-r8-261030/absent.json'),('sha256','0'*64)]:
                s,i=load('paper-tables-r8',['workload.sample_calls=1']);i.data['measurements'][key][name]=value
                r=calculate(s,i);self.assertTrue(any(x['input'].endswith('measurements.'+key) for x in r['alarms']));self.assertGreater(r['computed_metrics'],0)
        for namespace in ('r8','workload','paper_tables','hosting'):
            s,i=load('paper-tables-r8',['workload.sample_calls=1']);del i.data[namespace]
            r=calculate(s,i);self.assertTrue(r['alarms']);self.assertGreater(r['computed_metrics'],0)

    # A bounded speed/price invariant checks that larger PCIe reduces paid migration, while doubling storage price doubles only the storage bill.
    def test_hosting_monotonic_and_linear(self):
        baseline=table(run('paper-tables-r8',['workload.sample_calls=232']),'reasoning_on_top_sensitivity')['rows'][0]
        price=table(run('paper-tables-r8',['workload.sample_calls=232','hosting.tiers.RAM.price=1','hosting.tiers.NVMe.price=0.2']),'reasoning_on_top_sensitivity')['rows'][0]
        fast=table(self.changed('hosting.pcie_bandwidth',100e9),'reasoning_on_top_sensitivity')['rows'][0]
        self.assertAlmostEqual(price['storage_month'],2*baseline['storage_month']);self.assertEqual(price['migration_month'],baseline['migration_month'])
        self.assertLessEqual(fast['migration_month'],baseline['migration_month']);self.assertGreaterEqual(fast['capacity_day'],baseline['capacity_day'])
