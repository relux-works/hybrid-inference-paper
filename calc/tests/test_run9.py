"""Run 9 protocol regression witnesses and published hosting cases."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run
from hybridcalc.paper_tables import Context

def table(r,id):return next(t for t in r['tables'] if t['id']==id)

class ProtocolTests(unittest.TestCase):
    # Past KV positions are immutable: spill appends1700 new/decoded positions and overwrites only the recurrent state, independent of old depth.
    def test_append_only_spill(self):
        s,i=load('paper-tables',['workload.sample_calls=1']);c=Context(s,i)
        calls=c.label('fixture.calls',[(150000,1000,700,0)]);kv=c.label('fixture.kv',34844);state=c.label('fixture.state',156894784)
        vector=c.hosting.vector('fixture',calls,kv,state);reload,spill=c.g.resolve(vector).value[0]
        self.assertEqual(spill,(1700*34844+156894784)/50e9)
        self.assertEqual(reload,(150000*34844+156894784)/50e9)

    # A marginal offload must be rejected after pending local input/output and prior offloaded output move onto its critical path; the final set is stable.
    def test_pending_compute_enters_decision(self):
        from hybridcalc.session_hosting import route
        args=([1,10,100],[2,9,1],[2,3,6],[1,1,1],[10,10,10],[0,0,0])
        per=route(*args,'per_call');design=route(*args,'at_offload')
        self.assertEqual([x[3] for x in per],[False,True,True])
        self.assertEqual([x[3] for x in design],[False,False,True])
        self.assertEqual(design[-1][0],7);self.assertEqual(design.pending_seconds,6);self.assertEqual(design.pending_calls,2)
        # All input/output compute is allocated once; latency placement adds no extra total GPU work.
        self.assertEqual(5+design.pending_seconds,sum(args[2]))

    # Zero/all offload boundaries are finite: local-only still gets a daily tail catch-up, while every offload carries preceding output.
    def test_zero_and_all_offload(self):
        from hybridcalc.session_hosting import route
        local=route([1,1],[2,2],[2,2],[1,1],[1,1],[0,0],'at_offload')
        self.assertFalse(any(x[3] for x in local));self.assertEqual(local.pending_seconds,0)
        remote=route([10,10],[1,1],[2,2],[1,1],[1,1],[0,0],'at_offload')
        self.assertEqual(remote.pending_seconds,1);self.assertEqual(remote.pending_calls,0)
        self.assertEqual([x[0] for x in remote],[2,2])

    # Design reloads are offloaded calls+one per active session-day; state overwrites are amortized at those flushes, KV positions append once.
    def test_daily_reload_spill_conservation(self):
        for mode in ('at_offload','per_call'):
            s,i=load('paper-tables',['workload.sample_calls=232','hosting.catch_up='+mode]);c=Context(s,i)
            cl=c.client('m5max64','hardware.links.wan.bandwidth','test');host=cl['hosting']
            calls=c.g.resolve(cl['matched']).value;steps=c.g.resolve(cl['steps']).value
            n=500;node=c.label('fixture.day',n);daily=c.hosting.daily('fixture.day',host,node)
            rate=50e9;read=sum(d*34844+156894784 for d,new,o,t in calls)/len(calls)/rate
            append=sum((new+o)*34844 for d,new,o,t in calls)/len(calls)/rate;p=sum(x[3] for x in steps)/len(calls)
            count=n if mode=='per_call' else n*p+4
            expected=n*append+sum((d*34844+156894784)/rate for (d,new,o,t),step in zip(calls,steps) if step[3])*n/len(calls)+4*read if mode=='at_offload' else n*(read+append)
            expected+=count*156894784/rate
            self.assertAlmostEqual(c.g.resolve(daily).value,expected)
            no_calls=c.label('fixture.none',0);self.assertEqual(c.g.resolve(c.hosting.daily('fixture.none',host,no_calls)).value,0)

    # Tiered storage uses each row's actual active window; daily NVMe promotion is background only and cannot change the GPU bill.
    def test_retention_windows_and_promotion(self):
        for hours in (8,24):
            s,i=load('paper-tables',['workload.sample_calls=232']);c=Context(s,i)
            b=c.label('fixture.bytes',1e9);h=c.label('fixture.hours',hours)
            storage=c.hosting.storage('fixture',b,h)
            expected=4*((hours*21/730)*.5+(1-hours*21/730)*.1)
            self.assertAlmostEqual(c.g.resolve(storage).value,expected)
        a=run('paper-tables-r8',['workload.sample_calls=232']);b=run('paper-tables-r8',['workload.sample_calls=232','hosting.tiers.NVMe.bandwidth=1'])
        for x,y in zip(table(a,'reasoning_on_top_sensitivity')['rows'],table(b,'reasoning_on_top_sensitivity')['rows']):
            self.assertEqual(x['gpu_month'],y['gpu_month']);self.assertGreater(y['promotion_s_day'],x['promotion_s_day'])
        bad=run('paper-tables',['workload.sample_calls=1','paper_tables.hours=24','economics.hours_month=100'])
        self.assertTrue(any(x['input']=='economics.hours_month' for x in bad['alarms']))


class PublishedCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary=run('paper-tables',['workload.sample_calls=232']);cls.conservative=run('paper-tables-conservative',['workload.sample_calls=232'])

    # Parallel conservative CSVs preserve primary row coordinates and complete bills; per-call compute is identical across policies.
    def test_person_and_parallel_cases(self):
        for t in self.conservative['tables']:
            original=table(self.primary,t['id'].removesuffix('_conservative'))
            self.assertEqual(len(t['rows']),len(original['rows']))
            for x,y in zip(original['rows'],t['rows']):
                for key in ('team','client','basis','profile','state_bits','link_mbit','context','option'):
                    if key in x:self.assertEqual(x[key],y[key])
        for key in ('s20','s50','academic_s100'):
            for a,b in zip(table(self.primary,'person_cost_'+key)['rows'],table(self.conservative,'person_cost_'+key+'_conservative')['rows']):
                self.assertEqual(a['compute_per_call'],b['compute_per_call']);self.assertLess(a['storage_month'],b['storage_month'])
                for row in (a,b):
                    self.assertAlmostEqual(row['gpu_month'],row['compute_month']+row['storage_month']+row['migration_month'])
                    self.assertAlmostEqual(row['hybrid_median'],row['hybrid_without_overflow']+row['overflow_median'])
                self.assertAlmostEqual(a['reloads_day'],a['served_day']*a['offload_share']+min(4,a['served_day']))
                self.assertAlmostEqual(b['reloads_day'],b['served_day'])

    # Routing/capacity/offload tables share the new pending-work policy; the conservative foreground path retains the old per-call behavior.
    def test_offload_and_client_capacity(self):
        for a,b in zip(table(self.primary,'offload_by_link')['rows'],table(self.conservative,'offload_by_link_conservative')['rows']):
            self.assertLessEqual(a['share_calls'],b['share_calls']);self.assertLessEqual(a['saved_seconds_call'],b['saved_seconds_call'])
            self.assertAlmostEqual(a['saved_seconds_call'],a['share_calls']*a['saved_seconds_offloaded'])
        for a,b in zip(table(self.primary,'client_sessions_day')['rows'],table(self.conservative,'client_sessions_day_conservative')['rows']):
            self.assertLessEqual(a['hybrid_sessions_day'],b['hybrid_sessions_day']);self.assertEqual(a['local_sessions_day'],b['local_sessions_day'])

    # Retention for remote10h/24h rows is price-weighted separately, and append-only migration is included in each integer prefill budget.
    def test_remote_windows(self):
        rows=table(self.primary,'remote_rent_buy')['rows']
        for a in rows:
            if a['mode']!='hourly rental':continue
            same=[b for b in rows if all(b[k]==a[k] for k in ('team','option','residual'))]
            for b in same:
                ratio=(.1+.4*float(b['hours'])*21/730)/(.1+.4*float(a['hours'])*21/730)
                self.assertAlmostEqual(b['hosting_storage_month'],a['hosting_storage_month']*ratio)

    # Both published GLM families retain matched physical sessions; shared Studio demand and own-fleet accounting remain reconciled.
    def test_perimeter_and_glm_cases(self):
        primary=run('paper-tables-r6',['workload.sample_calls=232']);other=run('paper-tables-r6-conservative',['workload.sample_calls=232'])
        self.assertEqual({t['id'] for t in other['tables']},{'perimeter_cost_conservative','perimeter_cost_light_conservative','perimeter_cost_medium_conservative','perimeter_cost_heavy_conservative','glm_utilization_conservative'})
        for key in ('perimeter_cost','glm_utilization'):
            a=table(primary,key)['rows'];b=table(other,key+'_conservative')['rows'];self.assertEqual(len(a),len(b))
            for x,y in zip(a,b):
                for field in ('team','profile','route','client','basis','server','context','users_per_studio','demand_mode'):
                    if field in x:self.assertEqual(x[field],y[field])
        for x in table(primary,'perimeter_cost')['rows']:
            if x['route']=='hybrid':
                self.assertAlmostEqual(x['person_month'],x['fleet_person_month']+x['device_month']+x['client_energy_month']+x['front_month']+x['hosting_storage_month'])
                self.assertGreaterEqual(x['units'],1)
        for r in (self.primary,self.conservative):
            key='glm_long_sessions'+('_conservative' if r is self.conservative else '')
            for x in table(r,key)['rows']:self.assertAlmostEqual(x['hybrid_session'],x['hybrid_without_overflow_session']+x['overflow_api_session'])

    # Compute-only users/GPU is preserved exactly, while effective migration includes the actual routing share and daily-tail overhead for each daily share.
    def test_people_per_gpu(self):
        a=run('paper-tables-r8',['workload.sample_calls=232']);b=run('paper-tables-r8-conservative',['workload.sample_calls=232'])
        for x,y in zip(table(a,'people_per_gpu')['rows'],table(b,'people_per_gpu_conservative')['rows']):
            self.assertEqual(x['people_compute_only'],y['people_compute_only'])
            for row in (x,y):
                import math
                self.assertEqual(row['people_with_hosting'],math.floor(row['hours']*3600*row['load']/row['calls_user_day']/(row['shadow_gpu_s_call']+row['migration_gpu_s_call'])))

    # All four portion/state combinations exist; bf16 halves fixed recurrent state only, large portions reduce fixed bytes/token, and unsupported depths still alarm.
    def test_intensity_variants(self):
        r=run('paper-tables-r8',['workload.sample_calls=1']);rows=table(r,'flop_per_byte')['rows']
        self.assertEqual(len(rows),432);self.assertEqual({(x['portion_tokens'],x['state_bits']) for x in rows},{(1000,32),(1000,16),(10000,32),(10000,16)})
        q=[x for x in rows if x['model']=='Qwen3.8-27B' and x['depth']==110000 and x['client'].startswith('M3') and x['link_mbit']==200]
        for x in q:
            self.assertEqual(x['state_bytes'],156894784*x['state_bits']/32)
            self.assertEqual(x['delta_bytes'],x['portion_tokens']*34844+x['state_bytes'])
            if x['state_bits']==16:self.assertIn('estimated',x['state_basis'])
        a=next(x for x in q if x['state_bits']==32 and x['portion_tokens']==1000);b=next(x for x in q if x['state_bits']==32 and x['portion_tokens']==10000)
        self.assertGreater(b['model_flop_byte'],a['model_flop_byte'])
        for x in rows:
            if x['depth']>x['context_limit']:self.assertIn('alarm',x['ratio'])

class PolicyGapTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        parts=path.split('.');obj=data
        for key in parts[:-1]:obj=obj[int(key)] if isinstance(obj,list) else obj[key]
        return obj,int(parts[-1]) if isinstance(obj,list) else parts[-1]

    # Deleting any new enum/coordinate alarms every declared dependent cell at its exact path; nearby complete controls compute normally.
    def test_every_new_input_gap(self):
        from hybridcalc.paper_tables_r8 import calculate
        paths=['hosting.catch_up','hosting.retention','r9.large_portion','r9.state_bits.0','r9.state_bits.1']
        for path in paths:
            s,i=load('paper-tables-r8',['workload.sample_calls=232']);before=calculate(s,i)
            cells=[(t['id'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
            self.assertTrue(cells,path)
            s,i=load('paper-tables-r8',['workload.sample_calls=232']);parent,key=self.parent(i.data,path)
            if isinstance(parent,list):parent[key]=None
            else:del parent[key]
            result=calculate(s,i)
            for id,cell in cells:
                row,col=cell.split('.',1);value=table(result,id)['rows'][int(row)][col]
                self.assertIsInstance(value,dict,(path,id,cell));self.assertTrue(any(a['input']==path for a in value['alarm']),(path,value))

    # New inputs reject null, nonfinite, negative, wrong-unit and unprovenanced values; enum typos/unsupported24-bit formats and zero portions are explicit alarms.
    def test_new_contracts_and_corners(self):
        import copy
        from hybridcalc.inputs import InputGap
        from hybridcalc.paper_tables_r8 import calculate
        for path in ('hosting.catch_up','hosting.retention','r9.large_portion','r9.state_bits.0','r9.state_bits.1'):
            s,i=load('paper-tables-r8',['workload.sample_calls=1']);original=copy.deepcopy(i.locate(path));parent,key=self.parent(i.data,path)
            self.assertIsNotNone(i.get(path))
            for field,value in [('value',None),('value',float('nan')),('value',float('inf')),('value',-1),('unit','wrong'),('provenance',None)]:
                parent[key]=copy.deepcopy(original);parent[key][field]=value
                with self.assertRaises(InputGap) as caught:i.get(path)
                self.assertEqual(caught.exception.path,path)
        for expr in ('hosting.catch_up=typo','hosting.retention=typo','r9.large_portion=0','r9.state_bits.0=24'):
            r=run('paper-tables-r8',['workload.sample_calls=1',expr]);self.assertTrue(any(x['input']==expr.split('=')[0] for x in r['alarms']))
        for count in (0,1):
            r=run('paper-tables-r8',['workload.sample_calls='+str(count)])
            if count==0:self.assertTrue(table(r,'people_per_gpu')['alarms'])
            else:self.assertFalse(table(r,'people_per_gpu')['alarms'])

    # Retention gaps affect storage/total bills, not routing, compute or immutable-copy geometry; RAM-only ignores unused NVMe prices.
    def test_retention_gap_control(self):
        a=run('paper-tables-r8',['workload.sample_calls=232']);b=run('paper-tables-r8',['workload.sample_calls=232','hosting.retention=null'])
        for id in ('transcript_example','flop_per_byte'):self.assertEqual(table(a,id),table(b,id))
        for x,y in zip(table(a,'reasoning_on_top_sensitivity')['rows'],table(b,'reasoning_on_top_sensitivity')['rows']):
            for col in ('capacity_day','compute_month','migration_month'):self.assertEqual(x[col],y[col])
            for col in ('storage_month','hybrid_median','hybrid_cheapest'):self.assertIn('alarm',y[col])
        r=run('paper-tables-conservative',['workload.sample_calls=232','hosting.tiers.NVMe.price=null','hosting.tiers.NVMe.bandwidth=null'])
        self.assertFalse(any('NVMe' in x['input'] for x in r['alarms']))
        r=run('paper-tables',['workload.sample_calls=232','hosting.tiers.RAM.price=0'])
        self.assertGreater(table(r,'person_cost_s20')['rows'][0]['storage_month'],0)

    # Output-only generation retains full shadow, measured input mix and transcript; it raises the compute-only user/GPU headline grid.
    def test_accepted_compute_only_headline(self):
        r=run('paper-tables-r8');rows=table(r,'people_per_gpu')['rows']
        self.assertEqual([x['people_compute_only'] for x in rows],[69,27,13,308,123,61])

    # Catch-up gaps alarm client-dependent waits and budgets, while local-only perimeter capacities and the accepted compute-only bounds remain available.
    def test_catchup_gap_control(self):
        r=run('paper-tables-r8',['workload.sample_calls=232','hosting.catch_up=null'])
        for x in table(r,'people_per_gpu')['rows']:
            self.assertIsInstance(x['people_compute_only'],int);self.assertIn('alarm',x['people_with_hosting'])
        r=run('paper-tables-r6',['workload.sample_calls=232','hosting.catch_up=null'])
        for x in table(r,'perimeter_cost')['rows']:
            if x['route']=='Macs only':self.assertIsInstance(x['client_capacity_day'],float)
