"""R6 chart contracts and forbidden external routes, with independent formula checks."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run


def table(result,key):return next(t for t in result['tables'] if t['id']==key)


class R6TablesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=run('paper-tables-r6',['workload.sample_calls=232'])

    # All requested tables and three profile charts are named; profile rows are exact aggregate subsets.
    def test_named_tables(self):
        self.assertEqual({t['id'] for t in self.result['tables']},{'perimeter_cost','perimeter_cost_light','perimeter_cost_medium','perimeter_cost_heavy','glm_utilization','decode_scaling'})
        rows=table(self.result,'perimeter_cost')['rows']
        for profile in ('light','medium','heavy'):
            self.assertEqual(table(self.result,'perimeter_cost_'+profile)['rows'],[r for r in rows if r['profile']==profile])

    # Every requested perimeter call is either client-served, turbo-served or explicitly unserved; external tariff inputs are forbidden.
    def test_perimeter_conservation(self):
        t=table(self.result,'perimeter_cost')
        for x in t['rows']:
            self.assertEqual(x['share'],1)
            self.assertAlmostEqual(x['requested_day'],x['client_served_day']+x['turbo_day']+x['unserved_day'])
            self.assertEqual(x['external_calls_day'],0)
            if x['route']=='Macs only':self.assertEqual(x['turbo_day'],0)
            else:self.assertEqual(x['unserved_day'],0)
        roots={p for d in t['dependencies'].values() for p in d['inputs']}
        self.assertFalse(any(p.startswith('prices.apis') or p.endswith('.hourly') or p=='prices.egress' for p in roots))

    # Perimeter totals pay for a whole combined owned fleet, and its turbo reference plus adjustment exactly reconciles the fleet budget.
    def test_perimeter_fleet_budget(self):
        for x in table(self.result,'perimeter_cost')['rows']:
            self.assertAlmostEqual(x['person_month'],x['device_month']+x['client_energy_month']+x['front_month']+x['fleet_person_month']+x['hosting_storage_month'])
            if x['route']=='hybrid':
                self.assertAlmostEqual(x['fleet_person_month'],x['prefill_reference_month']+x['turbo_reference_month']+x['fleet_adjustment_month'])
                self.assertAlmostEqual(x['turbo_reference_month'],x['turbo_day']*21*x['all_server_call'])
            if x['route']!='Macs only':
                self.assertIsInstance(x['units'],int);self.assertGreaterEqual(x['units'],1)
                self.assertAlmostEqual(x['fleet_person_month'],x['units']*x['unit_month']/x['team'])

    # Studio sharing buys ceil(N/users_per_Studio) devices; demand/capacity are conserved and overflow is API-priced, never free.
    def test_studio_sharing(self):
        for x in table(self.result,'glm_utilization')['rows']:
            self.assertEqual(x['studios'],math.ceil(x['team']/x['users_per_studio']))
            self.assertLessEqual(x['served_team_day'],x['studios']*x['capacity_studio_day']+1e-8)
            self.assertAlmostEqual(x['served_team_day']+x['overflow_team_day'],x['requested_team_day'])
            self.assertAlmostEqual(x['hybrid_session'],x['hybrid_base_session']+x['overflow_api_session'])
            if x['demand_mode']=='capacity':self.assertAlmostEqual(x['utilization'],1)
            if x['overflow_team_day']>0:self.assertGreater(x['overflow_api_session'],0)

    # Decode projection is exactly the raw bandwidth bound at every K/depth; fitted resident memory independently determines fit.
    def test_decode_bound(self):
        rows=table(self.result,'decode_scaling')['rows']
        self.assertEqual(len(rows),42)
        for x in rows:
            if x['kind']=='measured':continue
            expected=x['streams']*x['bandwidth']/(x['weights']+x['streams']*(x['depth']*x['wire_kv']+2*x['state']))
            self.assertAlmostEqual(x['bandwidth_bound_aggregate'],expected)
            fits=x['weights']+x['reserve']+x['streams']*(x['depth']*x['resident_kv']+x['state'])<=x['memory']
            self.assertEqual(x['fits'],int(fits))
            if fits:self.assertEqual(x['aggregate_tok_s'],expected)
            else:self.assertIn('alarm',x['aggregate_tok_s'])

    # The only measured rows are actual single/four-stream M3 Max 32k measurements, never predictions for new depths or streams.
    def test_decode_anchors(self):
        rows=[x for x in table(self.result,'decode_scaling')['rows'] if x['kind']=='measured']
        self.assertEqual([(x['depth'],x['streams']) for x in rows],[(32000,1),(32000,4)])
        self.assertAlmostEqual(rows[0]['aggregate_tok_s'],8.440946539830035)
        self.assertAlmostEqual(rows[1]['aggregate_tok_s'],14.054306337676012)


class R6CornerTests(unittest.TestCase):
    @staticmethod
    def changed(mutate,overrides=('workload.sample_calls=1',)):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables_r6 import calculate
        scenario,inputs=load('paper-tables-r6',overrides)
        mutate(inputs.data)
        return calculate(scenario,inputs)

    # External APIs/rental/egress cannot change any perimeter output; all calls remain on owned infrastructure even when these inputs are absent.
    def test_no_external_price_dependency(self):
        baseline=run('paper-tables-r6',['workload.sample_calls=1'])
        def remove(d):
            d['prices'].pop('apis');d['prices'].pop('egress')
            for option in d['owners']['options'].values():option.pop('hourly',None)
        changed=self.changed(remove)
        for key in ('perimeter_cost','perimeter_cost_light','perimeter_cost_medium','perimeter_cost_heavy'):
            self.assertEqual(table(baseline,key),table(changed,key))
        self.assertIn('alarm',table(changed,'glm_utilization')['rows'][0]['api_session'])

    # A planted local-front gap has exactly one new root alarm; unrelated GLM/decode tables and hybrid cells remain byte-for-byte structured-equal.
    def test_gap_control(self):
        a=run('paper-tables-r6',['workload.sample_calls=1'])
        b=self.changed(lambda d:d['r6']['perimeter'].pop('local_front_month'))
        self.assertEqual([x for x in b['alarms'] if x not in a['alarms']],[{'input':'r6.perimeter.local_front_month','reason':'missing input'}])
        for key in ('glm_utilization','decode_scaling'):self.assertEqual(table(a,key),table(b,key))
        for x,y in zip(table(a,'perimeter_cost')['rows'],table(b,'perimeter_cost')['rows']):
            if x['route']=='Macs only':self.assertIn('alarm',y['person_month'])
            else:self.assertEqual(x,y)

    # A one-user team, shared Studio ceil and residual endpoints are valid; zero load is an alarm and never a division by zero.
    def test_team_load_residual(self):
        for residual in (0,1):
            r=run('paper-tables-r6',['workload.sample_calls=1','paper_tables.teams.0=1','r6.utilization.teams.0=1','owners.residual='+str(residual),'economics.client_residual='+str(residual)])
            self.assertEqual(table(r,'perimeter_cost')['rows'][0]['team'],1)
            self.assertIsInstance(table(r,'perimeter_cost')['rows'][0]['person_month'],float)
            shared=next(x for x in table(r,'glm_utilization')['rows'] if x['team']==1 and x['users_per_studio']==2)
            self.assertEqual(shared['studios'],1)
            self.assertAlmostEqual(shared['served_team_day']+shared['overflow_team_day'],shared['requested_team_day'])
        invalid=run('paper-tables-r6',['workload.sample_calls=1','owners.load=0'])
        self.assertTrue(any(a['input']=='owners.load' for a in invalid['alarms']))
        self.assertIn('alarm',table(invalid,'perimeter_cost')['rows'][0]['person_month'])
        self.assertIsInstance(table(invalid,'decode_scaling')['rows'][0]['bandwidth_bound_aggregate'],float)

    # Empty workload raises per-call alarms but leaves decode geometry intact; a single call and depth zero remain valid positive controls.
    def test_empty_single_depth_zero(self):
        a=run('paper-tables-r6',['workload.sample_calls=0'])
        b=run('paper-tables-r6',['workload.sample_calls=1','r6.decode.depths.0=0'])
        self.assertTrue(any(x['input']=='workload.sample_calls' for x in a['alarms']))
        self.assertIsInstance(table(b,'perimeter_cost')['rows'][0]['person_month'],float)
        x=table(b,'decode_scaling')['rows'][0]
        self.assertEqual(x['depth'],0);self.assertEqual(x['fits'],1)
        self.assertIsInstance(table(a,'decode_scaling')['rows'][0]['aggregate_tok_s'],float)

    # New sidecars are namespaced; exporting R6 preserves all R5 charts/sidecars and remains deterministic with numeric nan alarms.
    def test_export_coexistence(self):
        import csv,json,tempfile
        from hybridcalc.export import write_tables
        r=run('paper-tables-r6',['workload.sample_calls=1'])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in ('manifest.json','schema.json','alarms.json','sources.json','person_cost_s20.csv'):(p/name).write_text('R5 foreign bytes')
            write_tables(r,p)
            for name in ('manifest.json','schema.json','alarms.json','sources.json','person_cost_s20.csv'):self.assertEqual((p/name).read_text(),'R5 foreign bytes')
            manifest=json.loads((p/'r6_manifest.json').read_text())
            self.assertEqual(len(manifest['tables']),6);self.assertIn('r6_sources.json',manifest['files'])
            rows=list(csv.DictReader((p/'decode_scaling.csv').read_text().splitlines()))
            self.assertTrue(any(x['aggregate_tok_s']=='nan' and x['status']=='alarm' for x in rows))
            before={f.name:f.read_bytes() for f in p.iterdir()};write_tables(r,p)
            self.assertEqual(before,{f.name:f.read_bytes() for f in p.iterdir()})

    # A safe namespace is required before writes; path traversal may not overwrite a parent file.
    def test_export_namespace_rejection(self):
        import tempfile
        from hybridcalc.export import write_tables
        from hybridcalc.inputs import InputError
        with tempfile.TemporaryDirectory() as tmp:
            for ns in ('../bad',True,[],['bad']):
                with self.subTest(namespace=ns):
                    with self.assertRaisesRegex(InputError,'namespace'):write_tables({'export_namespace':ns,'tables':[]},tmp)
            self.assertEqual(list(Path(tmp).iterdir()),[])

    # Missing/corrupt packages raise their exact root alarms; measured anchors do not depend on a prefill-curve file or on modeled decode efficiencies.
    def test_measurements_and_bounds_independence(self):
        for field,value in [('path','.temp/hybrid-calc-r6-261030/absent.json'),('sha256','0'*64)]:
            r=self.changed(lambda d:d['measurements']['normalized'].__setitem__(field,value))
            rows=table(r,'decode_scaling')['rows']
            self.assertIsInstance(rows[0]['aggregate_tok_s'],float)
            self.assertIn('alarm',rows[-1]['aggregate_tok_s'])
            self.assertTrue(any(a['input']=='measurements.normalized' for a in r['alarms']))
        r=self.changed(lambda d:d['measurements']['depth'].__setitem__('sha256','0'*64))
        self.assertIn('alarm',table(r,'decode_scaling')['rows'][0]['fits'])
        self.assertIsInstance(table(r,'decode_scaling')['rows'][-1]['aggregate_tok_s'],float)
        a=run('paper-tables-r6',['workload.sample_calls=1'])
        b=run('paper-tables-r6',['workload.sample_calls=1','owners.client_efficiency=0.1','analysis.decode_calibration_scale=0.5'])
        self.assertEqual(table(a,'decode_scaling'),table(b,'decode_scaling'))

    # Nonfit clients/servers and impossible or missing links alarm dependent metrics while independent API rates and theoretical bounds survive.
    def test_nonfit_and_link(self):
        for path,value in [('owners.models.qwen27.weights_q4',300000000000),('owners.options.rack1.memory',1000000000),('hardware.links.wan.bandwidth',0),('hardware.links.wan.bandwidth',None)]:
            r=run('paper-tables-r6',['workload.sample_calls=1',path+'='+('null' if value is None else str(value))])
            self.assertTrue(any(a['input']==path or ('memory' in a['input'] if path.endswith('weights_q4') else False) for a in r['alarms']))
            self.assertGreater(r['computed_metrics'],0)
        r=run('paper-tables-r6',['workload.sample_calls=1','hardware.clients.ultra256.memory=128000000000'])
        x=table(r,'glm_utilization')['rows'][0];self.assertIn('alarm',x['hybrid_session']);self.assertGreater(x['api_session'],0)

    # Requested capacity means one shared-device budget: two users do not double output; saturating either sharing layout reaches utilization one.
    def test_shared_capacity_modes(self):
        from hybridcalc.paper_tables_r6 import shared_demand
        self.assertEqual(shared_demand(2,2,6,4),(1,8,6,2))
        self.assertEqual(shared_demand(3,2,6,None),(2,12,12,0))
        self.assertEqual(shared_demand(3,2,6,1),(2,3,3,0))

    # Warm fleet sizing is an integer ceiling with minimum one; proportional work and target-load headroom determine the next unit boundary.
    def test_integer_fleet_threshold(self):
        from hybridcalc.paper_tables_r6 import fleet_units,route_counts,wait_stats
        self.assertEqual(fleet_units(0,8,.7),1)
        self.assertEqual(fleet_units(8*3600*.7,8,.7),1)
        self.assertEqual(fleet_units(8*3600*.7+1,8,.7),2)
        self.assertEqual(route_counts(200,.5,150),(100,100))
        self.assertEqual(wait_stats([(1,),(2,),(3,),(4,)]),(2.5,4))

    # Unknown overrides still fail clearly; nonfinite/window/load/capacity contracts produce alarms rather than useful numbers built on gaps.
    def test_invalid_override(self):
        from hybridcalc.inputs import InputError
        with self.assertRaisesRegex(InputError,'unknown override'):run('paper-tables-r6',['r6.typo=1'])
        for expr in ('r6.decode.streams.0=NaN','r6.utilization.sessions_day.0=Infinity','owners.hours=0','r6.perimeter.share=0.5','r6.perimeter.overlap_min=101'):
            r=run('paper-tables-r6',['workload.sample_calls=1',expr])
            self.assertTrue(any(a['input']==expr.split('=')[0] for a in r['alarms']))


class R6InputTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        cur=data;parts=path.split('.')
        for p in parts[:-1]:cur=cur[int(p)] if isinstance(cur,list) else cur[p]
        return cur,int(parts[-1]) if isinstance(cur,list) else parts[-1]

    # Each new data quantity is consumed in its active precision; removing it alarms every declared dependent cell, never a silent fallback.
    def test_every_new_input_gap(self):
        import json
        from hybridcalc.inputs import DATA,leaves
        from hybridcalc.engine import load
        from hybridcalc.paper_tables_r6 import calculate
        for path,q in leaves(json.loads((DATA/'paper-tables-r6.json').read_text())):
            precision='BF16' if path.endswith('.bf16_peak') else 'NVFP4' if path.endswith('.fp4_peak') else 'Q4'
            overrides=['workload.sample_calls=1','owners.server_precision='+precision]
            scenario,inputs=load('paper-tables-r6',overrides);before=calculate(scenario,inputs)
            cells=[(t['id'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
            with self.subTest(path=path):
                self.assertTrue(cells,'new quantity not consumed')
                _,inputs=load('paper-tables-r6',overrides);parent,key=self.parent(inputs.data,path)
                if isinstance(parent,list):parent[key]=None
                else:del parent[key]
                after=calculate(scenario,inputs);by_id={t['id']:t for t in after['tables']}
                self.assertTrue(any(a['input']==path for a in after['alarms']))
                for id,cell in cells:
                    row,column=cell.split('.',1);value=by_id[id]['rows'][int(row)][column]
                    self.assertIsInstance(value,dict,(path,id,cell))
                    self.assertTrue(any(a['input']==path for a in value['alarm']),(path,id,cell))

    # New quantities reject null/nonfinite/negative, bad units and missing provenance; zero is accepted only by its explicit contract.
    def test_new_input_contracts(self):
        import copy,json
        from hybridcalc.inputs import DATA,InputGap,leaves,match
        from hybridcalc.engine import load
        _,inputs=load('paper-tables-r6')
        for path,q in leaves(json.loads((DATA/'paper-tables-r6.json').read_text())):
            original=copy.deepcopy(inputs.locate(path));self.assertEqual(inputs.get(path),q['value'])
            for field,value in [('value',None),('value',float('nan')),('value',float('inf')),('value',-1),('unit','wrong'),('provenance',None)]:
                with self.subTest(path=path,field=field):
                    parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original);parent[key][field]=value
                    with self.assertRaises(InputGap) as e:inputs.get(path)
                    self.assertEqual(e.exception.path,path)
            parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(original)
            normalized='.'.join('*' if x.isdigit() else x for x in path.split('.'))
            rule=next(v for k,v in inputs._contracts.items() if match(k,normalized))
            parent[key]['value']=0
            valid='enum' not in rule and rule.get('minimum',0)==0 and not rule.get('exclusive_minimum',False)
            if valid:self.assertEqual(inputs.get(path),0)
            else:
                with self.assertRaises(InputGap):inputs.get(path)
            parent[key]=copy.deepcopy(original)

    # Missing/empty/malformed new list containers report shape alarms without crashing or discarding independent charts.
    def test_container_gaps(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables_r6 import calculate
        for path in ('r6.decode.streams','r6.decode.memories','r6.decode.depths','r6.utilization.contexts','r6.utilization.teams','r6.utilization.sessions_day','r6.utilization.users_per_studio'):
            for value in (None,[],{}):
                s,i=load('paper-tables-r6',['workload.sample_calls=1']);parent,key=self.parent(i.data,path);parent[key]=value
                r=calculate(s,i)
                self.assertTrue(any(a['input'].startswith(path) for a in r['alarms']));self.assertGreater(r['computed_metrics'],0)


class R6RoutingTests(unittest.TestCase):
    # Removing turbo work from a shared owned pool would underbuy hardware; work includes full demand minus client-decode work plus selected shadow prefill.
    def test_turbo_pool_work(self):
        from hybridcalc.paper_tables_r6 import pool_work
        from hybridcalc.inputs import InputGap
        self.assertEqual(pool_work(200,2,100,1,.5),350)
        self.assertEqual(pool_work(200,2,200,2,.5),100)
        self.assertEqual(pool_work(200,2,0,1,.5),400)
        with self.assertRaisesRegex(InputGap,'negative'):pool_work(200,1,200,2,.5)

    # Policy override authorizes small internal racks and exposes both paths at 50 users; selected rows minimize monthly cost only among eligible whole-fleet candidates.
    def test_perimeter_selection_and_overlap(self):
        r=run('paper-tables-r6',['workload.sample_calls=1']);rows=table(r,'perimeter_cost')['rows']
        for x in rows:
            self.assertEqual(x['office_policy'],'closed_perimeter_own_rack')
            if x['route']=='Macs only':continue
            if x['server'].startswith('Owned HGX'):self.assertEqual(x['eligible'],int(x['team']>=50))
            else:self.assertEqual(x['eligible'],int(x['team']<=100))
            if x['selected']:
                candidates=[y for y in rows if all(y[k]==x[k] for k in ('team','profile','route','client','basis')) and y['eligible']]
                self.assertEqual(x['person_month'],min(y['person_month'] for y in candidates))
        overlap=[x for x in rows if x['route']=='all server' and x['team']==50 and x['profile']=='light']
        self.assertEqual(sum(x['eligible'] for x in overlap),3)

    # The 8-hour perimeter window controls both client and fleet capacity; mean/p90 local wait is measured-curve compute-scaled service time, not queue delay.
    def test_window_and_local_wait(self):
        a=run('paper-tables-r6',['workload.sample_calls=232'])
        b=run('paper-tables-r6',['workload.sample_calls=232','owners.hours=4'])
        old=table(a,'perimeter_cost')['rows'];new=table(b,'perimeter_cost')['rows']
        for x,y in zip(old,new):
            if x['route']=='Macs only':
                self.assertAlmostEqual(x['client_capacity_day'],2*y['client_capacity_day'])
                self.assertGreaterEqual(x['prefill_p90_s'],x['prefill_mean_s'])
                self.assertEqual(x['prefill_mean_s'],y['prefill_mean_s'])
        m3=next(x for x in old if x['route']=='Macs only' and x['client'].startswith('M3'))
        m4=next(x for x in old if x['route']=='Macs only' and x['client'].startswith('M4'))
        self.assertGreater(m3['prefill_mean_s'],m4['prefill_mean_s'])
        absent=R6CornerTests.changed(lambda d:d['hardware']['links']['wan'].pop('bandwidth'),overrides=('workload.sample_calls=232',))
        for x,y in zip(old,table(absent,'perimeter_cost')['rows']):
            if x['route']=='Macs only':self.assertEqual(x,y)
            if x['route']=='hybrid':self.assertIn('alarm',y['person_month'])

    # With one Studio per person and two sessions/day, R6 retains the R5 physical capacities and requested-session economics on the same call sample.
    def test_glm_r5_reference(self):
        a=run('paper-tables',['workload.sample_calls=232'])
        b=run('paper-tables-r6',['workload.sample_calls=232'])
        for x in table(b,'glm_utilization')['rows']:
            if x['users_per_studio']!=1 or x['demand_mode']!='fixed' or x['requested_user_day']!=2:continue
            y=next(y for y in table(a,'glm_long_sessions')['rows'] if y['team']==x['team'] and y['context']==x['context'])
            for left,right in [('capacity_studio_day','hybrid_capacity_sessions_day'),('hybrid_session','hybrid_session'),('own_cluster_session','own_cluster_session'),('api_session','api_session')]:
                self.assertAlmostEqual(x[left],y[right])


class R6ResidualTests(unittest.TestCase):
    # Perimeter premiums use the same 20% owners-paper residual as servers; the separate R5 Studio occupancy reference retains its 35% client residual.
    def test_perimeter_owner_residual(self):
        r=run('paper-tables-r6',['workload.sample_calls=1'])
        x=next(x for x in table(r,'perimeter_cost')['rows'] if x['route']=='Macs only' and x['client'].startswith('M3') and x['basis']=='Mac premium bought')
        self.assertAlmostEqual(x['device_month'],(6000-2499)*.8/48)
        studio=table(r,'glm_utilization')['rows'][0]
        self.assertAlmostEqual(studio['studio_month'],10799*.65/48+.1*8*21*.15)


class R6WaitTests(unittest.TestCase):
    # Turbo mean wait includes each routed call's own-server prefill and internal RTT; client calls retain their actual policy wait, without pricing or serving a different demand.
    def test_weighted_prefill_wait(self):
        from hybridcalc.paper_tables_r6 import routed_wait
        self.assertEqual(routed_wait(200,100,4,2,2),3)
        self.assertEqual(routed_wait(200,0,4,2,2),2)
        self.assertEqual(routed_wait(200,200,4,2,2),4)
        a=run('paper-tables-r6',['workload.sample_calls=1'])
        b=run('paper-tables-r6',['workload.sample_calls=1','hardware.links.wan.latency=1.4'])
        for x,y in zip(table(a,'perimeter_cost')['rows'],table(b,'perimeter_cost')['rows']):
            if x['route']=='all server':self.assertAlmostEqual(y['prefill_mean_s']-x['prefill_mean_s'],1)
            if x['route']=='Macs only':self.assertEqual(x,y)
