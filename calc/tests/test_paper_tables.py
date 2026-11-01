"""Paper chart claims, routing conservation, calibration and explicit alarm contracts."""
import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run
from hybridcalc.inputs import InputGap,leaves


def table(result,name):return next(t for t in result['tables'] if t['id']==name)


class PaperTablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=run('paper-tables',['workload.sample_calls=232'])

    # Three share tables each cover six clients, two bases and the ordered six-team grid including 20 people.
    def test_named_tables(self):
        self.assertEqual({t['id'] for t in self.result['tables']},{'person_cost_s20','person_cost_s50','person_cost_academic_s100','crossover_explanation','remote_rent_buy','client_sessions_day','offload_by_link','traffic_user_month','glm_long_sessions','client_fit_deep'})
        for key in ('s20','s50','academic_s100'):
            t=table(self.result,'person_cost_'+key)
            self.assertEqual(len(t['rows']),72)
            self.assertEqual({x['team'] for x in t['rows']},{5,10,20,50,500,5000})
            self.assertEqual(len({x['client'] for x in t['rows']}),6)
            self.assertEqual({x['basis'] for x in t['rows']},{'Mac already owned','Mac premium bought'})
            self.assertTrue(all((x['bound']=='academic bound')==(key=='academic_s100') for x in t['rows']))

    # Each priced alternative covers all requested calls: served+overflow, and both API overflow costs are explicitly added to the same non-overflow hybrid budget.
    def test_overflow_cost_conservation(self):
        witness=False
        for t in self.result['tables']:
            if not t['id'].startswith('person_cost'):continue
            for x in t['rows']:
                self.assertAlmostEqual(x['served_day']+x['overflow_day'],x['requested_day'])
                self.assertAlmostEqual(x['hybrid_median'],x['hybrid_without_overflow']+x['overflow_median'])
                self.assertAlmostEqual(x['hybrid_cheapest'],x['hybrid_without_overflow']+x['overflow_cheapest'])
                self.assertGreaterEqual(x['overflow_median'],x['overflow_cheapest'])
                if x['overflow_day']>1:
                    witness=True;self.assertGreater(x['overflow_cheapest'],0)
        self.assertTrue(witness)

    # The actual 32k measurement gives exactly 1.665015442 aggregate gain at four streams; other clients use the same law scaled only by bandwidth for decode.
    def test_measured_stream_anchor(self):
        rows=table(self.result,'client_sessions_day')['rows']
        m=next(x for x in rows if x['client'].startswith('M3 Max') and x['link_mbit']==1000)
        self.assertEqual(m['streams'],4)
        self.assertAlmostEqual(m['aggregate_gain_32k'],1.665015442445748,places=12)
        self.assertAlmostEqual(m['single_tok_s_32k'],8.440946539830035,places=12)
        for x in rows:
            self.assertAlmostEqual(x['tok_s_stream_32k']/m['tok_s_stream_32k'],x['bandwidth']/m['bandwidth'])

    # Buying a premium adds only the declared residual-adjusted premium; it does not change API/overflow or consume a different call count.
    def test_mac_purchase_basis(self):
        rows=table(self.result,'person_cost_s50')['rows']
        for x in rows:
            if x['basis']!='Mac already owned':continue
            y=next(y for y in rows if y['team']==x['team'] and y['client']==x['client'] and y['basis']=='Mac premium bought')
            self.assertAlmostEqual(y['hybrid_cheapest']-x['hybrid_cheapest'],y['device_month'])
            self.assertEqual(x['device_month'],0)
            for key in ('requested_day','served_day','overflow_cheapest','api_median','own_cluster'):self.assertEqual(x[key],y[key])

    # The short crossover reference retains r4's exact endpoints and explicitly distinguishes the historical reference from current client capacity.
    def test_crossover_reference(self):
        rows=table(self.result,'crossover_explanation')['rows']
        self.assertEqual([rows[0][k] for k in ('s20','s50','academic_s100')],[3000,1000,500])
        self.assertEqual([rows[-1][k] for k in ('s20','s50','academic_s100')],[612,245,123])
        self.assertTrue(all(x['paper_uses'] for x in rows))

    # Remote choices have integer fleets, positive colocation, monotone residual cost and a numeric buy/rent decision; small-team office cells alarm.
    def test_remote_rent_buy(self):
        rows=table(self.result,'remote_rent_buy')['rows']
        for x in rows:
            if x['deployment']=='office':
                self.assertIn('alarm',x['monthly_cost']);self.assertIn('alarm',x['buy_beats_rent']);continue
            self.assertGreaterEqual(x['units'],1)
            self.assertIn(x['buy_beats_rent'],(0,1))
            self.assertEqual(x['buy_beats_rent'],int(x['owned_month']<x['rent_month']))
            if x['option'].startswith(('1x','2x')):self.assertGreater(x['colo_month'],0)
        owned=[x for x in rows if x['option'].startswith('1x') and x['team']==5 and x['hours']==10]
        self.assertEqual(len(owned),3)
        self.assertGreater(owned[0]['owned_month'],owned[-1]['owned_month'])

    # Local/hybrid session counts use the same measured calls and eight-hour day; a faster link cannot reduce hybrid capacity, and hybrid never loses under its admission rule.
    def test_client_sessions_day(self):
        rows=table(self.result,'client_sessions_day')['rows']
        self.assertEqual(len(rows),24)
        for x in rows:
            self.assertGreaterEqual(x['hybrid_sessions_day'],x['local_sessions_day'])
            self.assertAlmostEqual(x['gain'],x['hybrid_sessions_day']/x['local_sessions_day'])
        for client in {x['client'] for x in rows}:
            group=sorted((x for x in rows if x['client']==client),key=lambda x:x['link_mbit'])
            self.assertEqual([x['hybrid_sessions_day'] for x in group],sorted(x['hybrid_sessions_day'] for x in group))

    # Each offload saving is averaged over all calls, and 16-bit state cannot have worse offload share or saving at the same link than 32-bit state.
    def test_offload_links(self):
        rows=table(self.result,'offload_by_link')['rows'];self.assertEqual(len(rows),8)
        for x in rows:
            self.assertGreaterEqual(x['share_calls'],0);self.assertLessEqual(x['share_calls'],1)
            self.assertAlmostEqual(x['saved_seconds_call'],x['share_calls']*x['saved_seconds_offloaded'])
            if x['state_bits']==32:
                y=next(y for y in rows if y['link_mbit']==x['link_mbit'] and y['state_bits']==16)
                self.assertGreaterEqual(y['share_calls'],x['share_calls']);self.assertGreaterEqual(y['saved_seconds_call'],x['saved_seconds_call'])

    # Traffic is dimensioned in decimal TB and priced linearly; offered traffic and capacity-limited hybrid traffic are explicitly distinct.
    def test_traffic_user_month(self):
        rows=table(self.result,'traffic_user_month')['rows'];self.assertEqual(len(rows),3)
        for x in rows:
            self.assertLessEqual(x['hybrid_tb_month'],x['offered_tb_month'])
            self.assertAlmostEqual(x['served_day']+x['overflow_day'],x['calls_day'])
            for j,price in enumerate((0,5,50,90)):
                self.assertEqual(x['egress_'+str(j)],x['hybrid_tb_month']*price)
                self.assertEqual(x['offered_egress_'+str(j)],x['offered_tb_month']*price)

    # Five GLM contexts cover all six teams (30 rows); fleets, purchased Studios, overflow and both ingest times remain explicit.
    def test_glm_long_sessions(self):
        rows=table(self.result,'glm_long_sessions')['rows'];self.assertEqual(len(rows),30)
        for x in rows:
            self.assertEqual(x['final_depth'],x['context'])
            self.assertGreaterEqual(x['sessions_fit'],1)
            self.assertGreater(x['decode_tok_s_stream'],0)
            self.assertGreater(x['ingest_1m_local_s'],x['ingest_1m_server_s'])
            self.assertAlmostEqual(x['hybrid_session'],x['hybrid_without_overflow_session']+x['overflow_api_session'])
            self.assertGreater(x['studio_month'],0)
            self.assertGreaterEqual(x['own_units'],1)
        for d in {x['context'] for x in rows}:
            group=[x for x in rows if x['context']==d]
            self.assertEqual(len({x['api_session'] for x in group}),1)

    # Deep fit reports all Mac sizes/formats/depths including known nonfit alarms, instead of silently dropping unsupported models.
    def test_client_fit_deep(self):
        rows=table(self.result,'client_fit_deep')['rows'];self.assertEqual(len(rows),32)
        for x in rows:
            if x['model']=='Qwen3.8-27B':
                self.assertEqual(x['kv_per_token'],34844);self.assertAlmostEqual(x['state_bytes'],156894784)
                self.assertEqual(x['memory_depth'],int((x['memory']-x['reserve']-x['weights']-x['state_bytes'])//34844))
        self.assertTrue(any(isinstance(x['sessions_256k'],dict) for x in rows))

    # Per-chart export preserves every row/number, uses nan plus explicit status for alarms, and writes units/provenance/alarms without mutating other files.
    def test_csv_export(self):
        from hybridcalc.export import write_tables
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'keep.txt').write_text('foreign')
            record=write_tables(self.result,p)
            self.assertEqual(len(record['tables']),10)
            for t in self.result['tables']:
                rows=list(csv.DictReader(io.StringIO((p/(t['id']+'.csv')).read_text())))
                self.assertEqual(len(rows),len(t['rows']))
                raw_lines=(p/(t['id']+'.csv')).read_text().splitlines()
                self.assertTrue(all(len(line.split(','))==len(raw_lines[0].split(',')) for line in raw_lines))
                self.assertFalse(any('\"' in line for line in raw_lines))
                for raw,source in zip(rows,t['rows']):
                    for k,v in source.items():
                        if isinstance(v,dict):self.assertEqual(raw[k],'nan');self.assertEqual(raw['status'],'alarm')
                        elif type(v) in (int,float):self.assertEqual(float(raw[k]),v)
            self.assertEqual((p/'keep.txt').read_text(),'foreign')
            self.assertTrue(json.loads((p/'alarms.json').read_text()))
            before={x.name:x.read_bytes() for x in p.iterdir()};write_tables(self.result,p)
            self.assertEqual(before,{x.name:x.read_bytes() for x in p.iterdir()})


class PaperCornerTests(unittest.TestCase):
    # An empty mix alarms only workload-dependent tables; pure fit, historical crossover and numerical ingest remain independently available. A single call is a valid control.
    def test_empty_and_single(self):
        empty=run('paper-tables',['workload.sample_calls=0'])
        self.assertTrue(any(a['input']=='workload.sample_calls' for a in empty['alarms']))
        self.assertEqual(table(empty,'client_fit_deep'),table(run('paper-tables',['workload.sample_calls=1']),'client_fit_deep'))
        one=run('paper-tables',['workload.sample_calls=1'])
        self.assertIsInstance(table(one,'person_cost_s20')['rows'][0]['hybrid_cheapest'],float)

    # Link zero/absence, load zero, NaN/infinity and unknown overrides never turn a missing physical input into a useful zero or traceback.
    def test_invalid_overrides(self):
        for expr in ('paper_tables.links.0=0','owners.load=0','paper_tables.hours=NaN','paper_tables.glm.sessions_day=Infinity'):
            r=run('paper-tables',['workload.sample_calls=1',expr]);self.assertTrue(any(a['input']==expr.split('=')[0] for a in r['alarms']))
        from hybridcalc.inputs import InputError
        with self.assertRaisesRegex(InputError,'unknown override'):run('paper-tables',['paper_tables.typo=1'])

    # Residual 0/1, one-person teams, zero open share/egress/API prices are valid; zero-baseline ratios alarm only the undefined ratio.
    def test_boundaries(self):
        r=run('paper-tables',['workload.sample_calls=1','paper_tables.teams.0=1','paper_tables.shares.s20=0','owners.residual=1','prices.egress=0'])
        row=table(r,'person_cost_s20')['rows'][0]
        self.assertEqual(row['requested_day'],0);self.assertEqual(row['overflow_median'],0)
        self.assertEqual(row['team'],1)
        for residual in (0,1):
            x=run('paper-tables',['workload.sample_calls=1','owners.residuals.0='+str(residual)])
            self.assertIsInstance(table(x,'remote_rent_buy')['rows'][0]['owned_month'],float)

    # A planted median overflow-price gap produces the expected root alarm, leaves capacity/traffic/fit unchanged, and retains cheapest totals.
    def test_gap_control(self):
        a=run('paper-tables',['workload.sample_calls=1'])
        from hybridcalc.paper_tables import calculate
        scenario,inputs=load('paper-tables',['workload.sample_calls=1'])
        del inputs.data['prices']['apis']['qwen_median']['output']
        b=calculate(scenario,inputs)
        self.assertEqual([x for x in b['alarms'] if x not in a['alarms']],[{'input':'prices.apis.qwen_median.output','reason':'missing input'}])
        for key in ('client_sessions_day','traffic_user_month','client_fit_deep'):self.assertEqual(table(a,key),table(b,key))
        for x,y in zip(table(a,'person_cost_s50')['rows'],table(b,'person_cost_s50')['rows']):
            self.assertEqual(x['hybrid_cheapest'],y['hybrid_cheapest']);self.assertIn('alarm',y['hybrid_median'])

    # Truncated long sessions conserve delta+output growth, reject nonprogress/invalid target and keep numerical ingest stable under step refinement.
    def test_growth_and_integration(self):
        from hybridcalc.paper_tables import growing_calls,integrate
        calls=[(0,5,3,2),(100,4,6,1)]
        rows=growing_calls(calls,0,20,100)
        self.assertEqual(rows[-1][0]+rows[-1][1]+rows[-1][2],20)
        self.assertEqual(sum(x[1]+x[2] for x in rows),20)
        with self.assertRaisesRegex(InputGap,'progress'):growing_calls([(0,0,0,1)],0,20,100)
        with self.assertRaisesRegex(InputGap,'context'):growing_calls(calls,0,101,100)
        self.assertAlmostEqual(integrate(lambda x:2*x+3,100,7),10300,places=8)




class PaperInputTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        parts=path.split('.');cur=data
        for part in parts[:-1]:cur=cur[int(part)] if isinstance(cur,list) else cur[part]
        return cur,int(parts[-1]) if isinstance(cur,list) else parts[-1]

    # Every new quantity is actually exercised; removing it alarms every declared dependent cell instead of reusing a default or cached number.
    def test_every_new_input_gap(self):
        from hybridcalc.paper_tables import calculate
        from hybridcalc.inputs import DATA
        added=list(leaves(json.loads((DATA/'paper-tables.json').read_text())))
        scenario,inputs=load('paper-tables',['workload.sample_calls=1']);before=calculate(scenario,inputs)
        for path,q in added:
            with self.subTest(path=path):
                cells=[(t['id'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
                self.assertTrue(cells,'new quantity must be consumed')
                _,changed=load('paper-tables',['workload.sample_calls=1']);parent,key=self.parent(changed.data,path)
                if isinstance(parent,list):parent[key]=None
                else:del parent[key]
                after=calculate(scenario,changed);by_id={t['id']:t for t in after['tables']}
                self.assertTrue(any(a['input']==path for a in after['alarms']))
                for id,cell in cells:
                    row,column=cell.split('.',1);value=by_id[id]['rows'][int(row)][column]
                    self.assertIsInstance(value,dict,(path,id,cell,value))
                    self.assertTrue(any(a['input']==path for a in value['alarm']),(path,id,cell,value))

    # New quantities have valid positive/zero controls and reject null, nonfinite, negative, wrong-unit and missing-provenance values at the exact path.
    def test_new_quantity_contracts(self):
        from hybridcalc.inputs import DATA
        _,inputs=load('paper-tables',['workload.sample_calls=1'])
        for path,q in leaves(json.loads((DATA/'paper-tables.json').read_text())):
            original=copy.deepcopy(inputs.locate(path));self.assertEqual(inputs.get(path),original['value'])
            for field,value in [('value',None),('value',float('nan')),('value',float('inf')),('value',-1),('unit','wrong'),('provenance',None)]:
                with self.subTest(path=path,field=field):
                    parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original);parent[key][field]=value
                    with self.assertRaises(InputGap) as e:inputs.get(path)
                    self.assertEqual(e.exception.path,path)
                    parent[key]=copy.deepcopy(original)
            # Economic zeros, zero share and a cold depth-zero start are valid; capacity/rate/depth/stream zeros are invalid.
            allow_zero=(path.startswith('paper_tables.shares.') or path=='paper_tables.sizing_share' or path.startswith('paper_tables.egress_prices.') or path=='paper_tables.glm.start_depth' or path.endswith(('.purchase_price','.premium_credit')))
            parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original);parent[key]['value']=0
            if allow_zero:self.assertEqual(inputs.get(path),0)
            else:
                with self.assertRaises(InputGap) as e:inputs.get(path)
                self.assertEqual(e.exception.path,path)
            parent[key]=copy.deepcopy(original)
            if original['unit']=='1':
                parent[key]['value']=1;self.assertEqual(inputs.get(path),1)
                parent[key]['value']=1.1
                with self.assertRaises(InputGap):inputs.get(path)
                parent[key]=copy.deepcopy(original)

    # Whole missing/new list containers retain partial results, and invalid reference selection is an alarm rather than a raw indexing error.
    def test_container_gaps(self):
        from hybridcalc.paper_tables import calculate
        for path in ('paper_tables.teams','paper_tables.links','paper_tables.glm.contexts','paper_tables.crossover_steps'):
            for val in (None,[],{}):
                scenario,inputs=load('paper-tables',['workload.sample_calls=1']);parent,key=self.parent(inputs.data,path);parent[key]=val
                r=calculate(scenario,inputs)
                self.assertGreater(r['computed_metrics'],0);self.assertTrue(any(a['input'].startswith(path) for a in r['alarms']))

    # Missing or hash-corrupt prefill packages alarm their consumers; full-demand API costs still compute from the independent call-mix package.
    def test_measurement_gaps(self):
        from hybridcalc.paper_tables import calculate
        for field,value in [('path','.temp/hybrid-calc-r5-261030/absent-measurement.jsonl'),('sha256','0'*64)]:
            scenario,inputs=load('paper-tables',['workload.sample_calls=1']);inputs.data['measurements']['depth'][field]=value
            r=calculate(scenario,inputs)
            self.assertTrue(any(a['input']=='measurements.depth' for a in r['alarms']))
            row=table(r,'person_cost_s50')['rows'][0];self.assertIn('alarm',row['hybrid_cheapest']);self.assertIsInstance(row['api_cheapest'],float)

    # A too-large model or beyond-anchor stream count alarms; GLM API/session growth remain available independently of server/client admission.
    def test_nonfit_and_stream_bound(self):
        big=run('paper-tables',['workload.sample_calls=1','owners.models.glm.weights_q4=300000000000'])
        row=table(big,'glm_long_sessions')['rows'][0];self.assertIn('alarm',row['sessions_fit']);self.assertIn('alarm',row['hybrid_session']);self.assertIsInstance(row['api_session'],float)
        streams=run('paper-tables',['workload.sample_calls=1','paper_tables.streams=5'])
        self.assertTrue(any(a['input']=='paper_tables.streams' and 'measured' in a['reason'] for a in streams['alarms']))
        unsupported=run('paper-tables',['workload.sample_calls=1','paper_tables.state_bits.0=8'])
        self.assertTrue(any(a['input'].startswith('paper_tables.state_bits') for a in unsupported['alarms']))

    # The historical owners-economics fraction1 reference already included cheapest spill; both variants retain that original total and expose the precise price difference.
    def test_existing_overflow_witness(self):
        r=run('owners-economics',['workload.reasoning_extra_fraction=1']);x=next(x for x in r['tables'][0]['rows'] if x['team']==5 and x['share']==.5)
        self.assertAlmostEqual(x['excess_day'],348.43569322240216)
        self.assertGreater(x['overflow_cheapest_user'],0)
        self.assertEqual(x['hybrid_user'],x['hybrid_cheapest_user'])
        self.assertAlmostEqual(x['hybrid_median_user']-x['hybrid_cheapest_user'],x['overflow_median_user']-x['overflow_cheapest_user'])

    # Deleting a GPU tariff/capex does not invalidate independently known client capacity or API prices; there are no implicit zero prices.
    def test_price_gap_independence(self):
        a=run('paper-tables',['workload.sample_calls=1'])
        b=run('paper-tables',['workload.sample_calls=1','owners.options.b300.hourly=null','owners.options.b300.capex=null'])
        self.assertEqual(table(a,'client_sessions_day'),table(b,'client_sessions_day'))
        for x,y in zip(table(a,'person_cost_s50')['rows'],table(b,'person_cost_s50')['rows']):
            self.assertEqual(x['api_median'],y['api_median']);self.assertIn('alarm',y['hybrid_median'])

    # API overflow prices follow the actual routed calls, preserving cache boundaries; a high-context unsupported call cannot be billed at the cheaper supported-call mean.
    def test_selective_overflow_price(self):
        from hybridcalc.paper_tables import api_vector,overflow_cost
        calls=[(0,10,1,0),(1000,20,2,0),(2000,30,3,0)];p={'cache_read':1,'cache_write':2,'output':3}
        prices=api_vector(calls,p,3)
        self.assertEqual(prices,[(20+3)/1e6,(1000+42+6)/1e6,(2000+64+9)/1e6])
        self.assertAlmostEqual(overflow_cost(3,2,[0,1],prices,1),prices[2])
        self.assertAlmostEqual(overflow_cost(3,1,[0,1],prices,1),prices[2]+.5*(prices[0]+prices[1]))

    # Measured prefill scales by declared compute until the roofline binds; cold-ingest quadrature is stable under refinement and a zero target/load is rejected where undefined.
    def test_prefill_and_ingest_refinement(self):
        a=run('paper-tables',['workload.sample_calls=1'])
        b=run('paper-tables',['workload.sample_calls=1','paper_tables.glm.integration_step=500'])
        x=table(a,'glm_long_sessions')['rows'][-1];y=table(b,'glm_long_sessions')['rows'][-1]
        self.assertAlmostEqual(x['ingest_1m_local_s']/y['ingest_1m_local_s'],1,delta=1e-4)
        self.assertAlmostEqual(x['ingest_1m_server_s']/y['ingest_1m_server_s'],1,delta=1e-6)
        c=run('paper-tables',['workload.sample_calls=1','hardware.clients.m4max.compute=14000000000000'])
        rows=table(c,'client_sessions_day')['rows'];m3=next(x for x in rows if x['client'].startswith('M3') and x['link_mbit']==1000);m4=next(x for x in rows if x['client'].startswith('M4') and x['link_mbit']==1000)
        self.assertEqual(m3['prefill_compute_scale'],m4['prefill_compute_scale'])


class ParallelEnvelopeTests(unittest.TestCase):
    # The new parallel envelope matches the measured endpoint, is monotone in available streams at all requested depths, and stays within the calibrated bandwidth bound.
    def test_parallel_depth_envelope(self):
        from hybridcalc.paper_tables import measured_rate
        w=18973870432;k=34844;s=156894784;b=400e9;eff=.43;passes=2
        rate=measured_rate(w,k,s,b,eff,1.665015442445748,4,passes)
        for depth in (0,32000,256000,500000,1000000):
            values=[n*rate(n,depth) for n in range(1,5)]
            self.assertEqual(values,sorted(values))
            for n,value in enumerate(values,1):self.assertLessEqual(value,b*eff*n/(w+n*(k*depth+passes*s)))
        self.assertAlmostEqual(4*rate(4,32000)/rate(1,32000),1.665015442445748)

    # Increasing memory with identical compute/bandwidth cannot lower full-mix throughput once both memories fit all calls; this catches the old deep-context batching reversal.
    def test_memory_capacity_monotonic(self):
        a=run('paper-tables',['workload.sample_calls=232'])
        b=run('paper-tables',['workload.sample_calls=232','hardware.clients.ultra96.memory=256000000000'])
        for x,y in zip(table(a,'client_sessions_day')['rows'],table(b,'client_sessions_day')['rows']):
            if x['client']=='M5 Ultra 96 GB':
                self.assertEqual(x['fit_share'],y['fit_share']);self.assertGreaterEqual(y['local_sessions_day'],x['local_sessions_day']);self.assertGreaterEqual(y['hybrid_sessions_day'],x['hybrid_sessions_day'])


class PaperAdditionalCorners(unittest.TestCase):
    # Explicit historical sampler/HBM reproduces the frozen calc9 D percentages and seconds; current calibrated/cold-tier charts intentionally differ.
    def test_offload_legacy_d(self):
        r=run('paper-tables',['sampler.mode=legacy_lognormal','hosting.tier=HBM','hosting.catch_up=per_call']);rows=table(r,'offload_by_link')['rows']
        for x,p,s in zip(rows,[27.3,48.2,67.7,77.3,39.0,59.8,75.4,81.5],[19.3,24.0,26.3,27.0,21.3,25.1,26.7,27.2]):
            self.assertEqual(round(x['share_calls']*100,1),p);self.assertEqual(round(x['saved_seconds_call'],1),s)

    # At effectively unusable but positive bandwidth no call is offloaded: unconditional saving is correctly zero and conditional saving alarms.
    def test_no_offload_corner(self):
        r=run('paper-tables',['workload.sample_calls=1','paper_tables.offload_links.0=1'])
        x=table(r,'offload_by_link')['rows'][0]
        self.assertEqual(x['share_calls'],0);self.assertEqual(x['saved_seconds_call'],0);self.assertIn('alarm',x['saved_seconds_offloaded'])

    # Free API prices yield a valid zero overflow cost, while absent prices alarm; a single requested stream gives unit aggregate gain.
    def test_zero_api_and_single_stream(self):
        r=run('paper-tables',['workload.sample_calls=1','paper_tables.streams=1','prices.apis.qwen_cheap.cache_read=0','prices.apis.qwen_cheap.cache_write=0','prices.apis.qwen_cheap.output=0'])
        for row in table(r,'person_cost_s50')['rows']:
            self.assertEqual(row['api_cheapest'],0);self.assertEqual(row['overflow_cheapest'],0)
        self.assertTrue(all(x['aggregate_gain_32k']==1 for x in table(r,'client_sessions_day')['rows']))

    # GLM overflow is actually paid under a high offered-session load; bought Studio/server costs and the spill use the same requested-session denominator.
    def test_glm_overflow_priced(self):
        r=run('paper-tables',['workload.sample_calls=232','paper_tables.glm.sessions_day=100'])
        for x in table(r,'glm_long_sessions')['rows']:
            self.assertAlmostEqual(x['overflow_api_session'],x['overflow_sessions_day']/100*x['api_session'])
            self.assertAlmostEqual(x['hybrid_session'],x['hybrid_without_overflow_session']+x['overflow_api_session'])
        self.assertGreater(table(r,'glm_long_sessions')['rows'][-1]['overflow_api_session'],0)

    # Unsafe or duplicate CSV IDs are rejected before any destination write; export cannot overwrite an unrelated path through traversal.
    def test_export_rejects_ids_before_write(self):
        from hybridcalc.export import write_tables
        from hybridcalc.inputs import InputError
        r=run('paper-tables',['workload.sample_calls=1'])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'keep').write_text('safe')
            for ids in (('../escape','ok'),('duplicate','duplicate')):
                bad=copy.deepcopy(r);bad['tables'][0]['id']=ids[0];bad['tables'][1]['id']=ids[1]
                with self.assertRaisesRegex(InputError,'unique safe'):write_tables(bad,p)
                self.assertEqual(list(p.iterdir()),[p/'keep']);self.assertEqual((p/'keep').read_text(),'safe')
            collision=copy.deepcopy(r);collision['tables'][0]['rows'][0]['client']='A,B';collision['tables'][0]['rows'][1]['client']='A;B'
            with self.assertRaisesRegex(InputError,'display-label collision'):write_tables(collision,p)
            self.assertEqual(list(p.iterdir()),[p/'keep'])





class PaperFleetCorners(unittest.TestCase):
    # At load one, fleets remain integer and no larger than at half load; a longer active window cannot require more units for unchanged work.
    def test_load_one_and_windows(self):
        a=run('paper-tables',['workload.sample_calls=1','owners.load=0.5','owners.calls_day=100000'])
        b=run('paper-tables',['workload.sample_calls=1','owners.load=1','owners.calls_day=100000'])
        for x,y in zip(table(a,'remote_rent_buy')['rows'],table(b,'remote_rent_buy')['rows']):
            if x['deployment']=='office':continue
            self.assertIsInstance(y['units'],int);self.assertLessEqual(y['units'],x['units'])
            z=next(z for z in table(b,'remote_rent_buy')['rows'] if z['team']==y['team'] and z['option']==y['option'] and z['residual']==y['residual'] and z['hours']==24)
            if y['hours']==10:self.assertLessEqual(z['units'],y['units'])

    # A nonfitting BF16 GLM replica is labelled academic and alarms own/hybrid cost; invalid expert counts cannot create a plausible server price.
    def test_glm_server_fit_and_experts(self):
        bad=run('paper-tables',['workload.sample_calls=1','owners.server_precision=BF16'])
        x=table(bad,'glm_long_sessions')['rows'][0]
        self.assertEqual(x['server_precision'],'BF16 (academic reference)')
        self.assertIn('alarm',x['own_cluster_session']);self.assertIn('alarm',x['hybrid_session']);self.assertIsInstance(x['api_session'],float)
        invalid=run('paper-tables',['workload.sample_calls=1','models.glm.active_experts=300'])
        y=table(invalid,'glm_long_sessions')['rows'][0]
        self.assertIn('alarm',y['own_cluster_session']);self.assertIn('alarm',y['decode_tok_s_stream'])
        self.assertTrue(any(a['input']=='models.glm.active_experts' for a in invalid['alarms']))





class PaperCsvLabelTests(unittest.TestCase):
    # CSV-safe display punctuation preserves exact original labels in schema metadata, with no quoted/multiline records for a simple plot reader.
    def test_csv_label_source(self):
        from hybridcalc.export import write_tables
        r=run('paper-tables',['workload.sample_calls=1'])
        original='Mac, "lab"\nname';r['tables'][0]['rows'][0]['client']=original
        with tempfile.TemporaryDirectory() as tmp:
            write_tables(r,tmp);p=Path(tmp)
            schema=json.loads((p/'schema.json').read_text());labels=schema['person_cost_s20']['csv_labels']['client']
            safe=next(k for k,v in labels.items() if v==original)
            self.assertFalse(any(c in safe for c in (',','"','\n','\r')))
            rows=list(csv.DictReader(io.StringIO((p/'person_cost_s20.csv').read_text())))
            self.assertEqual(rows[0]['client'],safe)


if __name__=='__main__':unittest.main()
