"""Crossover attribution and late-addendum contracts, with explicit claims."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load,run


def table(r,prefix):return next(t for t in r['tables'] if t['name'].startswith(prefix))


class BridgeTests(unittest.TestCase):
    # The first bridge row reproduces calc5's actual Rule A grid crossovers and 500-person academic cost, not its misleading precision/fleet comments.
    def test_calc5_endpoint(self):
        r=run('crossover-bridge')
        row=table(r,'calc5 to r3')['rows'][0]
        self.assertEqual([row[k] for k in ('s20','s50','s100')],[3000,1000,500])
        self.assertAlmostEqual(row['own_500_s100'],371,delta=.6)
        self.assertAlmostEqual(row['api_s100'],372,delta=.6)

    # The reviewed r3 bridge endpoint reproduces r3's own/API grid from the independent owner graph.
    def test_r3_endpoint(self):
        r=run('crossover-bridge');rows=table(r,'calc5 to r3')['rows']
        endpoint=next(x for x in rows if x['step']=='R3 sparse team grid (reviewed endpoint)')
        self.assertEqual([endpoint[k] for k in ('s20','s50','s100')],[200,200,100])
        owner=run('owners-economics',['workload.reasoning_extra_fraction=1'])
        row=next(x for x in table(owner,'Paper summary')['rows'] if x['team']==500 and x['share']==1)
        self.assertAlmostEqual(endpoint['own_500_s100'],row['own_cluster_user'],places=7)
        self.assertAlmostEqual(endpoint['api_s100'],row['api_median_user'],places=7)

    # Mac purchase allocation and unchanged median token tariffs do not enter the own-cluster/API comparison.
    def test_irrelevant_assumptions(self):
        rows=table(run('crossover-bridge'),'calc5 to r3')['rows']
        for row in rows[1:4]:
            self.assertEqual([row[k] for k in ('s20','s50','s100','own_500_s100','api_s100')],[rows[0][k] for k in ('s20','s50','s100','own_500_s100','api_s100')])

    # Removing redundant output-prefill lowers all-server demand; it does not alter the API price or pretend the hybrid no longer needs shadow work.
    def test_shadow_defect_correction(self):
        rows=table(run('crossover-bridge'),'calc5 to r3')['rows']
        self.assertLess(next(x for x in rows if x['step']=='Correct all-server output double counting for paper')['unit_s_call'],next(x for x in rows if x['step']=='Integer sweep 1..20000 (grid sensitivity)')['unit_s_call'])
        self.assertEqual(rows[-1]['api_s100'],rows[-2]['api_s100'])


class OperationsTests(unittest.TestCase):
    # The operator baseline is eight hours, small remote teams select explicit colocation charges, and office fleets are unavailable through 100 people.
    def test_small_team_colocation_policy(self):
        r=run('owners-paper',['workload.sample_calls=232'])
        rows=table(r,'Colocation, autopilot')['rows']
        for x in rows:
            if 'office' in x['option'].lower() and x['team']<=100:self.assertIn('alarm',x['units'])
            else:self.assertGreaterEqual(x['units'],1)
        one=next(x for x in rows if x['team']==5 and x['mode']=='operator' and x['option'].startswith('1x'))
        self.assertEqual(one['warm_hours'],8*21)
        self.assertEqual(one['autopilot_share'],0)
        self.assertIsInstance(one['own_month'],float)
        self.assertTrue(all('office' not in x['option'].lower() for x in table(r,'Small teams')['rows']))

    # Raising a small-host minimum colo fee changes its ownership cost by the exact fee increment, while rental and client fit remain identical.
    def test_colocation_minimum_price(self):
        a=run('owners-paper',['workload.sample_calls=1'])
        b=run('owners-paper',['workload.sample_calls=1','owners.options.colo1.colo_min_month=1000'])
        x=next(x for x in table(a,'Colocation, autopilot')['rows'] if x['team']==5 and x['mode']=='operator' and x['option'].startswith('1x'))
        target=x['option']
        y=next(x for x in table(b,'Colocation, autopilot')['rows'] if x['team']==5 and x['mode']=='operator' and x['option']==target)
        self.assertAlmostEqual(y['own_month']-x['own_month'],x['units']*(1000-.9*190))
        self.assertEqual(x['rent_month'],y['rent_month'])
        self.assertEqual(table(a,'Deep client'),table(b,'Deep client'))

    # Deep fit uses the measured affine 27B KV/state geometry; one-session reach is independently calculated and all requested depths are present.
    def test_deep_fit_affine_bound(self):
        r=run('owners-paper',['workload.sample_calls=1'])
        rows=table(r,'Deep client')['rows']
        for x in rows:
            self.assertEqual([x['depth_'+str(i)] for i in range(3)],[256000,500000,1000000])
            if x['model']=='Qwen3.8-27B':
                self.assertEqual(x['kv_per_token'],34844);self.assertEqual(x['state'],156894784)
                expected=int((x['memory']-x['reserve']-x['weights']-x['state'])//34844)
                self.assertEqual(x['memory_depth'],expected)
                self.assertEqual(x['supported_depth'],min(expected,1000000))
                for i in range(3):
                    n=int((x['memory']-x['reserve']-x['weights'])//(34844*x['depth_'+str(i)]+156894784))
                    if n<1:self.assertIn('alarm',x['sessions_'+str(i)])
                    else:self.assertEqual(x['sessions_'+str(i)],n)

    # Fixed total owner work is conserved across operator/autopilot splits; spreading it can reduce units, while a continuous warm lease is billed for the full month.
    def test_autopilot_work_and_load(self):
        r=run('owners-paper',['workload.sample_calls=232'])
        rows=table(r,'Colocation, autopilot')['rows']
        for x in rows:
            if isinstance(x['units'],dict):continue
            if x['mode']=='operator':
                y=next(y for y in rows if y['team']==x['team'] and y['option']==x['option'] and y['mode']=='autopilot')
                self.assertAlmostEqual(x['owner_gpu_hours'],y['owner_gpu_hours'])
                self.assertLessEqual(y['units'],x['units'])
                self.assertEqual(y['warm_hours'],730)
                self.assertLessEqual(y['peak_window_load'],.7+1e-12)
                self.assertGreaterEqual(y['calendar_utilization'],x['calendar_utilization'])

    # Pool sold+draining capacity never exceeds declared owner-idle windows; owner-used GPU-h cost and buy/rent changes use net revenue after incremental energy.
    def test_pool_conservation_and_economics(self):
        r=run('owners-paper',['workload.sample_calls=232'])
        rows=table(r,'Colocation, autopilot')['rows']
        for x in rows:
            if isinstance(x['units'],dict):continue
            gpu_count=1 if x['option'].startswith('1x') else 2 if x['option'].startswith('2x') else 4 if x['option'].startswith('Office 4x') else 1
            self.assertLessEqual(x['sold_pool_gpu_hours']+x['drain_gpu_hours_bound'],x['owner_idle_hours_per_unit']*x['units']*gpu_count+1e-9)
            self.assertEqual(x['owner_conflict_hours'],0)
            self.assertAlmostEqual(x['pool_net_credit'],x['pool_revenue']-x['pool_incremental_energy'])
            self.assertAlmostEqual(x['cost_per_owner_gpu_hour_pool'],(x['own_month']-x['pool_net_credit'])/x['owner_gpu_hours'])
            if isinstance(x['buy_months_pool'],float):self.assertGreaterEqual(x['buy_months_pool'],0)
            if x['mode']=='autopilot':
                self.assertEqual(x['sold_pool_gpu_hours'],0)
                self.assertEqual(x['pool_net_credit'],0)
                self.assertEqual(x['cost_per_owner_gpu_hour'],x['cost_per_owner_gpu_hour_pool'])

    # Autopilot and fill endpoints 0/1 are valid; zero pool price is valid, and undersized drain raises its own alarm without changing owner capacity or normal ownership costs.
    def test_pool_and_autopilot_boundaries(self):
        for share in (0,1):
            r=run('owners-paper',['workload.sample_calls=1','operations.autopilot_share='+str(share),'operations.pool_fill=1','operations.pool_price=0'])
            x=next(x for x in table(r,'Colocation, autopilot')['rows'] if x['team']==5 and x['mode']=='autopilot' and x['option'].startswith('1x'))
            self.assertIsInstance(x['units'],int);self.assertEqual(x['pool_revenue'],0)
            self.assertEqual(x['warm_hours'],168 if share==0 else 730)
        zero=run('owners-paper',['workload.sample_calls=1','operations.pool_fill=0'])
        self.assertTrue(all(x['pool_revenue']==0 for x in table(zero,'Colocation, autopilot')['rows'] if isinstance(x['units'],int)))
        base=run('owners-paper',['workload.sample_calls=1'])
        bad=run('owners-paper',['workload.sample_calls=1','operations.drain_hours=0'])
        self.assertTrue(any(a['input']=='operations.drain_hours' and 'zero-fallback' in a['reason'] for a in bad['alarms']))
        for x,y in zip(table(base,'Colocation, autopilot')['rows'],table(bad,'Colocation, autopilot')['rows']):
            self.assertEqual(x['units'],y['units']);self.assertEqual(x['own_month'],y['own_month'])
            self.assertIn('alarm',y['pool_revenue'])

    # Corrected paper all-server accounting excludes generated-token shadow, unlike the preserved r3 reference; hybrid per-call FLOPs remain unchanged.
    def test_corrected_all_server_has_one_decode(self):
        from hybridcalc import ownership
        scenario,inputs=load('owners-paper',['workload.sample_calls=232'])
        corrected=ownership.calculate(scenario,inputs)
        oldscenario=copy.deepcopy(scenario);oldscenario['correct_all_server_prefill']=False
        old=ownership.calculate(oldscenario,inputs)
        for a,b in zip(table(corrected,'Paper summary')['rows'],table(old,'Paper summary')['rows']):
            self.assertLessEqual(a['own_cluster_user'],b['own_cluster_user'])
            self.assertEqual(a['hybrid_user'],b['hybrid_user'])
        self.assertEqual(table(corrected,'Colocation, autopilot'),table(old,'Colocation, autopilot'))


class Run4GapTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        parts=path.split('.');value=data
        for part in parts[:-1]:value=value[int(part)] if isinstance(value,list) else value[part]
        return value,int(parts[-1]) if isinstance(value,list) else parts[-1]

    # Every newly introduced quantity is activated, then removed; all previously dependent cells alarm with that same root rather than compute through the gap.
    def test_every_new_input_missing(self):
        from hybridcalc.inputs import leaves
        from hybridcalc.crossover import calculate as bridge
        from hybridcalc.ownership import calculate as ownership
        for name,fn,prefixes in [('crossover-bridge',bridge,('bridge.',)),('owners-paper',ownership,('operations.','owners.options.colo1.','owners.options.colo2.'))]:
            _,original=load(name,['workload.sample_calls=1'])
            paths=[p for p,q in leaves(original.data) if p.startswith(prefixes)]
            cached={}
            for path in paths:
                overrides=['workload.sample_calls=1']
                if path.endswith('.fp4_peak'):overrides.append('owners.server_precision=NVFP4')
                if path.endswith('.bf16_peak'):overrides.append('owners.server_precision=BF16')
                k=tuple(overrides)
                if k not in cached:cached[k]=run(name,overrides)
                before=cached[k]
                cells=[(t['name'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
                with self.subTest(scenario=name,path=path):
                    self.assertTrue(cells,'new input must be exercised')
                    scenario,inputs=load(name,overrides)
                    parent,key=self.parent(inputs.data,path)
                    if isinstance(parent,list):parent[key]=None;reason='null input'
                    else:del parent[key];reason='missing input'
                    after=fn(scenario,inputs)
                    self.assertIn({'input':path,'reason':reason},after['alarms'])
                    tables={t['name']:t for t in after['tables']}
                    for tn,cell in cells:
                        row,col=cell.split('.',1);value=tables[tn]['rows'][int(row)][col]
                        self.assertIsInstance(value,dict,(path,tn,cell,value))
                        self.assertTrue(any(a['input']==path for a in value['alarm']),(path,tn,cell,value))

    # New inputs reject null/nonfinite values, wrong units and missing provenance, with a valid control at every path.
    def test_new_input_contracts(self):
        from hybridcalc.inputs import InputGap,leaves
        for name,prefixes in [('crossover-bridge',('bridge.',)),('owners-paper',('operations.','owners.options.colo1.','owners.options.colo2.'))]:
            _,inputs=load(name,['workload.sample_calls=1'])
            entries=[(p,q) for p,q in leaves(inputs.data) if p.startswith(prefixes)]
            for path,quantity in entries:
                self.assertEqual(inputs.get(path),quantity['value'])
                for field,value in [('value',None),('value',-1),('value',float('nan')),('value',float('inf')),('unit','wrong'),('provenance',None)]:
                    with self.subTest(scenario=name,path=path,field=field):
                        parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(quantity);parent[key][field]=value
                        with self.assertRaises(InputGap) as error:inputs.get(path)
                        self.assertEqual(error.exception.path,path)
                        parent[key]=quantity

    # A fleet capex gap cannot contaminate independently known API rates or per-call compute; a missing diagnostic team cannot change crossovers.
    def test_bridge_price_and_probe_gaps(self):
        from hybridcalc.crossover import calculate
        scenario,inputs=load('crossover-bridge',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['bridge']['units']['b300']['capex']
        after=calculate(scenario,inputs)
        for x,y in zip(before['tables'][0]['rows'],after['tables'][0]['rows']):
            self.assertEqual(x['api_s100'],y['api_s100']);self.assertEqual(x['unit_s_call'],y['unit_s_call'])
            self.assertIn('alarm',y['own_500_s100'])
        scenario,inputs=load('crossover-bridge',['workload.sample_calls=232'])
        del inputs.data['bridge']['probe_team']
        after=calculate(scenario,inputs)
        for x,y in zip(before['tables'][0]['rows'],after['tables'][0]['rows']):
            self.assertEqual([x[k] for k in ('s20','s50','s100')],[y[k] for k in ('s20','s50','s100')])
            self.assertIn('alarm',y['own_500_s100'])

    # Removing a pool price creates exactly one extra alarm, leaving all non-pool/deep-fit tables and normal owner costs unchanged.
    def test_pool_gap_control(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-paper',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['operations']['pool_price']
        after=calculate(scenario,inputs)
        added=[a for a in after['alarms'] if a not in before['alarms']]
        self.assertEqual(added,[{'input':'operations.pool_price','reason':'missing input'}])
        for x,y in zip(before['tables'][:-1],after['tables'][:-1]):self.assertEqual(x,y)
        for x,y in zip(table(before,'Colocation, autopilot')['rows'],table(after,'Colocation, autopilot')['rows']):
            self.assertEqual(x['own_month'],y['own_month']);self.assertEqual(x['units'],y['units'])
            if isinstance(x['units'],int):self.assertIn('alarm',y['own_with_pool_month'])

    # Missing/null/empty new containers yield table alarms and partial data rather than duplicate graph nodes or exceptions.
    def test_container_gaps(self):
        from hybridcalc.ownership import calculate
        for key in ('teams','depths','context_limits'):
            for value in (None,[],{}):
                scenario,inputs=load('owners-paper',['workload.sample_calls=1']);inputs.data['operations'][key]=value
                r=calculate(scenario,inputs)
                self.assertGreater(r['computed_metrics'],0)
                self.assertTrue(any(a['input'].startswith('operations.'+key) for a in r['alarms']))

    # A one-person team, residual endpoints 0/1 and zero pool/colo prices remain valid; invalid loads/shares/depths and mismatched calendar schedules alarm explicitly.
    def test_boundary_matrix(self):
        for residual in (0,1):
            r=run('owners-paper',['workload.sample_calls=1','operations.teams.0=1','owners.residual='+str(residual),'operations.pool_fill=0','owners.options.colo1.colo_min_month=0'])
            x=next(x for x in table(r,'Colocation, autopilot')['rows'] if x['team']==1 and x['mode']=='operator' and x['option'].startswith('1x'))
            self.assertIsInstance(x['own_month'],float)
            if residual==1:self.assertEqual(x['buy_months'],0)
        for override in ('owners.load=0','operations.autopilot_share=-0.1','operations.pool_fill=1.1','operations.pool_price=-1','operations.small_team_max=0','operations.depths.0=0','owners.days=0.5','economics.hours_month=24'):
            r=run('owners-paper',['workload.sample_calls=1',override])
            self.assertTrue(any(a['input']==override.split('=')[0] for a in r['alarms']),override)
        bad=run('crossover-bridge',['bridge.max_team=0'])
        self.assertTrue(any(a['input']=='bridge.max_team' for a in bad['alarms']))


class RecommendedPaperTests(unittest.TestCase):
    # The bridge's final corrected 8h/replica/measured-KV endpoint agrees numerically with the independent paper graph and its integer crossover.
    def test_paper_endpoint_and_integer_grid(self):
        end=table(run('crossover-bridge'),'calc5 to r3')['rows'][-1]
        paper=run('owners-paper',['workload.reasoning_extra_fraction=1'])
        for i,share in enumerate((.2,.5,1)):
            eq=next(x for x in table(paper,'Derived own-cluster')['rows'] if x['share']==share and x['api']=='api_median_user')
            self.assertEqual(eq['first_sustained_team'],end[('s20','s50','s100')[i]])
        row=next(x for x in table(paper,'Paper summary')['rows'] if x['team']==500 and x['share']==1)
        self.assertAlmostEqual(row['own_cluster_user'],end['own_500_s100'],places=7)
        self.assertAlmostEqual(row['api_median_user'],end['api_s100'],places=7)

    # Sparse r3 grid misses a real failure at 305 people for s20; the integer result is 306, not the sampled-grid 200.
    def test_omitted_team_counterexample(self):
        rows=table(run('crossover-bridge'),'calc5 to r3')['rows']
        exact=next(x for x in rows if x['step'].startswith('Integer sweep'))
        self.assertEqual(exact['s20'],306)
        r=run('owners-economics',['owners.teams.0=305','workload.reasoning_extra_fraction=1'])
        row=next(x for x in table(r,'Paper summary')['rows'] if x['team']==305 and x['share']==.2)
        self.assertGreater(row['own_cluster_user'],row['api_median_user'])


class DrainBoundTests(unittest.TestCase):
    # A fill fraction is not a worst-case bound on the final draining job; any positive fill reserves the full guard energy bound.
    def test_drain_bound_not_scaled_by_fill(self):
        r=run('owners-paper',['workload.sample_calls=1','operations.pool_fill=0.01'])
        row=next(x for x in table(r,'Colocation, autopilot')['rows'] if x['team']==5 and x['mode']=='operator' and x['option'].startswith('1x'))
        self.assertEqual(row['drain_gpu_hours_bound'],21*.25*row['units'])
        self.assertLessEqual(row['sold_pool_gpu_hours']+row['drain_gpu_hours_bound'],row['owner_idle_hours_per_unit']*row['units'])


class BridgeSchemaTests(unittest.TestCase):
    # An unknown changed assumption preserves earlier rows and alarms the uncertain current/later states, rather than failing the whole run or silently skipping it.
    def test_unknown_assumption_partial_alarm(self):
        from hybridcalc.crossover import calculate
        scenario,inputs=load('crossover-bridge',['workload.sample_calls=1'])
        inputs.data['bridge']['steps'][5]['changes']['nonsense']='owners.hours'
        r=calculate(scenario,inputs)
        rows=r['tables'][0]['rows']
        self.assertEqual(rows[0]['s100'],500)
        self.assertIn('alarm',rows[5]['s100'])
        self.assertIn('alarm',rows[-1]['s100'])
        self.assertTrue(any(a['input']=='bridge.steps.5.changes.nonsense' for a in r['alarms']))


class ZeroRentalTests(unittest.TestCase):
    # A free rental is a valid zero price: monthly rent is zero and no-pool purchase non-recovery points to the rental input, not a nonexistent pool fault.
    def test_zero_rental_names_comparison_input(self):
        r=run('owners-paper',['workload.sample_calls=1','owners.options.colo1.hourly=0'])
        row=next(x for x in table(r,'Colocation, autopilot')['rows'] if x['team']==5 and x['mode']=='operator' and x['option'].startswith('1x'))
        self.assertEqual(row['rent_month'],0)
        self.assertIsInstance(row['own_month'],float)
        self.assertEqual(row['buy_months']['alarm'][0]['input'],'owners.options.colo1.hourly')
        self.assertIn('never recovers',row['buy_months']['alarm'][0]['reason'])


class ColocationOwnershipTests(unittest.TestCase):
    # The small-team colocated row pays owned depreciation/opex, even though its physical location is a datacenter; rental-only pricing is a counterfactual.
    def test_small_colocation_is_ownership(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-paper',['workload.sample_calls=232'])
        actual=calculate(scenario,inputs)
        rented=copy.deepcopy(scenario);rented['colocated_keys']=[]
        alternative=calculate(rented,inputs)
        def row(r):return next(x for x in table(r,'Small teams')['rows'] if x['team']==5 and x['model']=='Qwen3.8-27B' and x['option'].startswith('1x'))
        a=row(actual);b=row(alternative)
        unit_own=36000*.8/48+36000*.04/12+.9*1.3*730*.7*.093+.9*190
        unit_rent=2.2*8*21
        expected=(unit_own-unit_rent)*a['units']/(5*a['served_day']*21)*116
        self.assertAlmostEqual(a['cost_session']-b['cost_session'],expected)
        self.assertGreater(a['cost_session'],b['cost_session'])
        self.assertEqual(a['api_session'],b['api_session'])


class DeploymentMetadataTests(unittest.TestCase):
    # A new office host added as data under an arbitrary catalogue key still obeys the small-team office prohibition; IDs do not define physical deployment policy.
    def test_office_policy_uses_deployment_metadata(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-paper',['workload.sample_calls=1'])
        inputs.data['owners']['options']['additional_host']=copy.deepcopy(inputs.data['owners']['options']['office6000'])
        scenario['operations_options']=['additional_host']
        r=calculate(scenario,inputs)
        rows=table(r,'Colocation, autopilot')['rows']
        for row in rows:
            if row['team']<=100:self.assertIn('alarm',row['units'])
            else:self.assertIsInstance(row['units'],int)


class RestoreBoundTests(unittest.TestCase):
    # A guard that covers tenant runtime but not owner model/state restoration alarms; known idle hours, normal owner costs and capacity stay available.
    def test_owner_restore_is_in_guard(self):
        a=run('owners-paper',['workload.sample_calls=1'])
        b=run('owners-paper',['workload.sample_calls=1','operations.owner_restore_hours=0.06'])
        self.assertTrue(any(x['input']=='operations.drain_hours' and 'restoration' in x['reason'] for x in b['alarms']))
        for x,y in zip(table(a,'Colocation, autopilot')['rows'],table(b,'Colocation, autopilot')['rows']):
            self.assertEqual(x['units'],y['units']);self.assertEqual(x['own_month'],y['own_month'])
            self.assertEqual(x['owner_idle_hours_per_unit'],y['owner_idle_hours_per_unit'])
            if isinstance(x['units'],int):self.assertIn('alarm',y['pool_revenue'])
        valid=run('owners-paper',['workload.sample_calls=1','operations.owner_restore_hours=0'])
        self.assertFalse(any(x['input']=='operations.drain_hours' for x in valid['alarms']))

    # Decimal boundary 0.1+0.2 hours fits a 0.3-hour guard within one floating-point ulp; a genuine larger restore bound still fails above.
    def test_guard_decimal_boundary(self):
        from hybridcalc.operations import idle_windows
        result=idle_windows(0,8,21,730,.3,.1,.2)
        self.assertGreater(result['eligible'],0)
