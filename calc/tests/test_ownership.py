"""Owners' economics contracts; physical gaps must remain visible in each dependent output."""
import copy
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load, run


def table(result, name):
    return next(t for t in result['tables'] if t['name'].startswith(name))


class OwnershipTests(unittest.TestCase):
    # Every summary cohort compares the same open calls, labels 100% academic, and reports capped excess explicitly.
    def test_summary_shares_and_capacity(self):
        r=run('owners-economics',['workload.sample_calls=232'])
        rows=table(r,'Paper summary')['rows']
        self.assertEqual({x['share'] for x in rows},{.2,.5,1})
        self.assertEqual({x['team'] for x in rows},{5,10,20,50,100,200,500,1000,5000,20000})
        for x in rows:
            self.assertEqual(x['bound']=='academic bound',x['share']==1)
            self.assertAlmostEqual(x['served_day']+x['excess_day'],2500*x['share'])
            self.assertLessEqual(x['served_day'],x['capacity_day'])
            self.assertGreaterEqual(x['cluster_boxes'],1)

    # Residual endpoints are admissible, one person works, and ownership savings are computed from the shown API baseline.
    def test_residual_endpoints_and_team_one(self):
        for residual in (0,1):
            r=run('owners-economics',['workload.sample_calls=1','owners.teams.0=1','owners.residuals.0='+str(residual)])
            rows=table(r,'Owned residual')['rows']
            row=next(x for x in rows if x['team']==1 and x['server_residual']==residual and x['client_residual']==residual)
            self.assertAlmostEqual(row['savings_median'],1-row['hybrid_user']/row['api_median_user'])
            self.assertIsInstance(row['hybrid_user'],float)

    # First sustained crossover is independently reconstructed from all later summary rows, without encoding an expected team threshold.
    def test_derived_equilibrium(self):
        r=run('owners-economics',['workload.sample_calls=232'])
        rows=table(r,'Paper summary')['rows']
        for row in table(r,'Derived own-cluster')['rows']:
            group=[x for x in rows if x['share']==row['share']]
            candidates=[x['team'] for i,x in enumerate(group) if all(y['own_cluster_user']<=y[row['api']] for y in group[i:])]
            expected=min(candidates) if candidates else 'none on supplied grid'
            self.assertEqual(row['first_sustained_team'],expected)

    # Empty workload alarms means/capacity/costs, while static memory-fit estimates remain computable.
    def test_empty_call_mix(self):
        r=run('owners-economics',['workload.sample_calls=0'])
        self.assertTrue(any(a['input']=='workload.sample_calls' for a in r['alarms']))
        self.assertIn('alarm',table(r,'Paper summary')['rows'][0]['hybrid_user'])
        self.assertIsInstance(table(r,'Client fit')['rows'][0]['required'],float)

    # Buying is compared with integer warm rentals; crossover is capex net of residual / positive operating savings.
    def test_buy_rent_formula(self):
        r=run('owners-economics',['workload.sample_calls=232'])
        rows=table(r,'Buy versus rent')['rows']
        self.assertEqual({x['hours_day'] for x in rows},{10,24})
        for x in rows:
            if isinstance(x['months_to_buy'],(int,float)):
                self.assertAlmostEqual(x['months_to_buy'],x['net_capex']/(x['rent_month']-x['own_opex_month']))

    # Fit output accounts for each byte class; larger contexts cannot improve fit, and impossible GLM laptops alarm.
    def test_fit_components_and_rejection(self):
        r=run('owners-economics',['workload.sample_calls=1'])
        rows=table(r,'Client fit')['rows']
        self.assertEqual(len(rows),96)
        for x in rows:
            self.assertAlmostEqual(x['required'],x['weights']+x['kv']+x['state']+x['reserve'])
            if x['required']>x['memory']:
                self.assertIn('alarm',x['sessions'])
            else:
                self.assertGreaterEqual(x['sessions'],1)
        self.assertTrue(all('alarm' in x['sessions'] for x in rows if x['model']=='GLM-5.3-Flash'))

    # All small-team options enforce model placement, while API cost and client sessions survive a server that cannot fit.
    def test_small_teams_memory_alarm(self):
        r=run('owners-economics',['workload.sample_calls=232'])
        rows=table(r,'Small teams')['rows']
        self.assertEqual({x['team'] for x in rows},{5,10,50})
        bad=next(x for x in rows if x['model']=='GLM-5.3-Flash' and x['option']=='L40S on demand')
        self.assertIn('alarm',bad['cost_session'])
        self.assertGreater(bad['sessions_mac'],0)
        self.assertGreater(bad['api_session'],0)

    # Break-even includes GPU, egress and front, then divides by one minus margin; a 100% margin alarms.
    def test_break_even_margin(self):
        r=run('owners-economics',['workload.sample_calls=232'])
        for x in table(r,'Break-even')['rows']:
            self.assertAlmostEqual(x['price_1000'],(x['gpu_1000']+x['egress_1000']+x['front_1000'])/(1-x['margin']))
        bad=run('owners-economics',['workload.sample_calls=1','owners.margin=1'])
        self.assertIn('alarm',table(bad,'Break-even')['rows'][0]['price_1000'])

    # Zero utilisation alarms rather than dividing by zero; unrelated client fit data remain identical.
    def test_zero_load_independence(self):
        a=run('owners-economics',['workload.sample_calls=1'])
        b=run('owners-economics',['workload.sample_calls=1','owners.load=0'])
        self.assertEqual(table(a,'Client fit'),table(b,'Client fit'))
        self.assertIn('alarm',table(b,'Paper summary')['rows'][0]['hybrid_user'])


class OwnershipInputTests(unittest.TestCase):
    @staticmethod
    def parent(data,path):
        parts=path.split('.');value=data
        for part in parts[:-1]:value=value[int(part)] if isinstance(value,list) else value[part]
        return value,int(parts[-1]) if isinstance(value,list) else parts[-1]

    # Each new numeric/enum owner input is read in a matching configuration: removing it alarms every previously dependent cell.
    # Nonselected format/throughput fields are deliberately activated, so unused-input rejection cannot pass this control.
    def test_every_owner_input_missing(self):
        from hybridcalc.inputs import leaves
        from hybridcalc.ownership import calculate
        _,initial=load('owners-economics',['workload.sample_calls=1'])
        paths=[p for p,q in leaves(initial.data) if p.startswith('owners.')]
        baseline={}
        for path in paths:
            overrides=['workload.sample_calls=1']
            if path.startswith('owners.formats.'):
                quant=path.rsplit('.',1)[-1]
                overrides+=['owners.client_quant=Q3'] if quant=='Q3' else ['owners.server_precision='+quant]
            if path.endswith('.bf16_peak'):overrides+=['owners.server_precision=BF16']
            if path.endswith('.fp4_peak'):overrides+=['owners.server_precision=NVFP4']
            cache=tuple(overrides)
            if cache not in baseline:baseline[cache]=run('owners-economics',overrides)
            before=baseline[cache]
            declared=[(t['name'],cell) for t in before['tables'] for cell,d in t['dependencies'].items() if path in d['inputs']]
            with self.subTest(path=path):
                self.assertTrue(declared,'input must be exercised by an output')
                scenario,inputs=load('owners-economics',overrides)
                parent,key=self.parent(inputs.data,path)
                if isinstance(parent,list):parent[key]=None;reason='null input'
                else:del parent[key];reason='missing input'
                after=calculate(scenario,inputs)
                self.assertIn({'input':path,'reason':reason},after['alarms'])
                outputs={t['name']:t for t in after['tables']}
                for name,cell in declared:
                    row,col=cell.split('.',1)
                    result=outputs[name]['rows'][int(row)][col]
                    self.assertIsInstance(result,dict,(path,name,cell,result))
                    self.assertTrue(any(a['input']==path for a in result['alarm']),(path,name,cell,result))

    # Every new owner quantity rejects NaN, infinity, wrong units and absent provenance at its own path, with valid positive controls.
    def test_every_owner_quantity_contract(self):
        from hybridcalc.inputs import InputGap, leaves
        _,inputs=load('owners-economics',['workload.sample_calls=1'])
        entries=[(p,q) for p,q in leaves(inputs.data) if p.startswith('owners.')]
        for path,quantity in entries:
            self.assertEqual(inputs.get(path),quantity['value'])
            for field,value in [('value',float('nan')),('value',float('inf')),('value',None),('unit','wrong'),('provenance',None)]:
                with self.subTest(path=path,field=field,value=value):
                    parent,key=self.parent(inputs.data,path);parent[key]=copy.deepcopy(quantity);parent[key][field]=value
                    with self.assertRaises(InputGap) as error:inputs.get(path)
                    self.assertEqual(error.exception.path,path)
                    self.assertNotIn('KeyError',str(error.exception))
                    parent[key]=quantity

    # A zero acquisition price, energy/egress price, front price, reserve, SSD latency or margin is valid and does not invent an alarm for that input.
    def test_nonnegative_zero_controls(self):
        paths=['owners.front_month','owners.client_price','owners.client_cost_fraction','owners.client_reserve',
               'owners.client_power','owners.margin','owners.ssd_token_latency','owners.options.h100.capex',
               'owners.options.h100.hourly','owners.options.h100.power']
        for path in paths:
            r=run('owners-economics',['workload.sample_calls=1',path+'=0'])
            # Zero tariff can legitimately mean buying never recovers costs, or zero API price can make a ratio undefined.
            self.assertFalse(any(a['input']==path and ('must be' in a['reason'] or 'finite' in a['reason']) for a in r['alarms']))
        zero=run('owners-economics',['workload.sample_calls=1','prices.egress=0','owners.margin=0'])
        for row in table(zero,'Break-even')['rows']:
            self.assertEqual(row['egress_1000'],0)
            self.assertAlmostEqual(row['price_1000'],row['gpu_1000']+row['front_1000'])

    # Invalid new positive domains fail their named contracts; input boundaries at unity remain admissible.
    def test_domain_boundaries(self):
        bad=['owners.load=0','owners.parallel_agents=0','owners.teams.0=0','owners.years=0','owners.client_memory=0',
             'owners.client_efficiency=0','owners.residual=-0.1','owners.residual=1.01','owners.shares.0=1.01',
             'owners.client_quant=Q8','owners.server_precision=FP16','owners.hours=25']
        for override in bad:
            r=run('owners-economics',['workload.sample_calls=1',override])
            self.assertTrue(any(a['input']==override.split('=')[0] for a in r['alarms']),override)
        r=run('owners-economics',['workload.sample_calls=1','owners.load=1','owners.client_efficiency=1','owners.shares.0=0'])
        self.assertIn('alarm',table(r,'Break-even')['rows'][0]['front_1000'])
        self.assertEqual(table(r,'Paper summary')['rows'][0]['served_day'],0)
        self.assertFalse(any(a['input']=='owners.load' for a in r['alarms']))

    # A planted front-price gap changes exactly dependent cells and leaves workload-independent fit and all buy/rent tables byte-structurally identical.
    def test_planted_front_gap_control(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-economics',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['owners']['front_month']
        after=calculate(scenario,inputs)
        added=[a for a in after['alarms'] if a not in before['alarms']]
        self.assertEqual(added,[{'input':'owners.front_month','reason':'missing input'}])
        for prefix in ('Client fit','Buy versus rent','Measured decode','Client capacity','Derived own-cluster'):
            self.assertEqual(table(before,prefix),table(after,prefix))
        self.assertIn('alarm',table(after,'Paper summary')['rows'][0]['hybrid_user'])
        self.assertEqual(table(before,'Paper summary')['rows'][0]['own_cluster_user'],table(after,'Paper summary')['rows'][0]['own_cluster_user'])

    # The measured native 16k interval is read from the pinned package; efficiency, quantization, prefill and parallel streams each change usable capacity.
    def test_client_calibration_and_capacity_inputs(self):
        base=run('owners-economics',['workload.sample_calls=232'])
        anchor=table(base,'Measured decode')['rows'][0]
        self.assertAlmostEqual(anchor['min'],7.480838303918422)
        self.assertAlmostEqual(anchor['max'],8.820042859852366)
        self.assertAlmostEqual(anchor['coordinate'],.34)
        self.assertGreater(anchor['raw_byte_efficiency'],.37)  # The supplied GGUF-byte bound differs from the owner's calibrated coordinate.
        def capacity(overrides):
            return table(run('owners-economics',['workload.sample_calls=232']+overrides),'Client capacity')['rows'][0]['capacity_day']
        self.assertGreater(capacity(['owners.client_efficiency=0.37']),capacity(['owners.client_efficiency=0.30']))
        self.assertGreater(capacity(['owners.client_quant=Q3']),capacity(['owners.client_quant=Q4']))
        self.assertGreaterEqual(capacity(['owners.parallel_agents=4']),capacity(['owners.parallel_agents=1']))
        self.assertGreaterEqual(capacity(['owners.client_prefill_scale=10']),capacity(['owners.client_prefill_scale=1']))

    # Q4/Q6/Q8 server weights change placement and decode traffic, not INT8/FP8 prefill class; NVFP4 needs a Blackwell option.
    def test_server_quantization_and_blackwell(self):
        def small(precision):return table(run('owners-economics',['workload.sample_calls=232','owners.server_precision='+precision]),'Small teams')['rows']
        q4=small('Q4');q8=small('Q8');nv=small('NVFP4')
        a=next(x for x in q4 if x['model']=='GLM-5.3-Flash' and x['option']=='B300 288 GB hourly')
        b=next(x for x in q8 if x['model']==a['model'] and x['option']==a['option'])
        self.assertIsInstance(a['cost_session'],float)
        self.assertIn('alarm',b['cost_session'])
        self.assertGreater(b['weight_bytes'],a['weight_bytes'])
        bad=next(x for x in nv if x['option']=='H100 SXM on demand')
        good=next(x for x in nv if x['option']=='B300 288 GB hourly' and x['model']=='Qwen3.8-27B')
        self.assertIn('alarm',bad['cost_session'])
        self.assertIsInstance(good['cost_session'],float)

    # Flash-Next SSD placement subtracts exactly 51B n-gram parameters at the chosen format; a zero SSD latency is explicit.
    def test_flash_ngram_both_placements(self):
        r=run('owners-economics',['workload.sample_calls=1'])
        rows=table(r,'Client fit')['rows']
        for quant,bpp in [('Q3',.4375),('Q4',.5625)]:
            a=next(x for x in rows if x['model']=='Qwen3.8-Flash-Next' and x['quant']==quant and x['memory']==96e9 and x['context']==32000 and x['placement']=='all weights in RAM')
            b=next(x for x in rows if x['model']==a['model'] and x['quant']==quant and x['memory']==a['memory'] and x['context']==a['context'] and x['placement']=='ngram on SSD')
            self.assertAlmostEqual(a['weights']-b['weights'],51e9*bpp)
            self.assertEqual(a['parameters'],125e9);self.assertEqual(a['active_parameters'],6e9)
            self.assertEqual(a['ssd_latency'],0);self.assertGreater(b['ssd_latency'],0)

    # A missing/corrupt native benchmark alarms client rate/capacity while static fit and dedicated server acquisition comparisons remain available.
    def test_measurement_gap_independence(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-economics',['workload.sample_calls=1'])
        before=calculate(scenario,inputs)
        inputs.data['measurements']['normalized']['sha256']='0'*64
        after=calculate(scenario,inputs)
        self.assertIn({'input':'measurements.normalized','reason':'measurement sha256 mismatch'},after['alarms'])
        self.assertEqual(table(before,'Client fit'),table(after,'Client fit'))
        self.assertIn('alarm',table(after,'Client capacity')['rows'][0]['capacity_day'])

    # GLM parallel agents read an expert union: per-stream decode falls, while aggregate rate gains are bounded below linear scaling.
    def test_glm_parallel_expert_union(self):
        def rate(agents):
            r=run('owners-economics',['workload.sample_calls=232','owners.parallel_agents='+str(agents)])
            return next(x['tok_s_stream'] for x in table(r,'Small teams')['rows'] if x['model']=='GLM-5.3-Flash')
        single=rate(1);four=rate(4)
        self.assertLess(four,single)
        self.assertGreater(4*four,single)
        self.assertLess(4*four,4*single)

    # Inconsistent architecture quantities alarm at the offending input, instead of making negative traffic or an oversized SSD subtraction look like a fit.
    def test_inconsistent_model_parameters(self):
        active=run('owners-economics',['workload.sample_calls=1','owners.models.glm.active_parameters=400000000000'])
        self.assertTrue(any(a['input']=='owners.models.glm.active_parameters' for a in active['alarms']))
        bad=next(x for x in table(active,'Small teams')['rows'] if x['model']=='GLM-5.3-Flash')
        self.assertIn('alarm',bad['tok_s_stream'])
        ngram=run('owners-economics',['workload.sample_calls=1','owners.models.flashnext.ngram=200000000000'])
        self.assertTrue(any(a['input']=='owners.models.flashnext.ngram' for a in ngram['alarms']))
        for x in table(ngram,'Client fit')['rows']:
            if x['model']=='Qwen3.8-Flash-Next' and x['placement']=='ngram on SSD':self.assertIn('alarm',x['weights'])

    # Removing a required benchmark retains its comparison rows and raises its named alarm rather than shrinking the table.
    def test_missing_benchmark_keeps_row(self):
        from hybridcalc.ownership import calculate
        scenario,inputs=load('owners-economics',['workload.sample_calls=1'])
        before=calculate(scenario,inputs)
        del inputs.data['owners']['benchmarks']['mimo_flash']
        after=calculate(scenario,inputs)
        self.assertEqual(len(table(before,'Break-even')['rows']),len(table(after,'Break-even')['rows']))
        rows=[x for x in table(after,'Break-even')['rows'] if x['api']=='mimo_flash']
        self.assertEqual(len(rows),3)
        for x in rows:
            self.assertEqual(x['api_1000'],{'alarm':[{'input':'owners.benchmarks.mimo_flash','reason':'missing input'}]})
            self.assertIsInstance(x['price_1000'],float)

    # Whole missing/null/empty array or catalogue inputs retain partial tables and named alarms without duplicate graph nodes or a raw exception.
    def test_missing_owner_catalogues_preserve_partial_results(self):
        from hybridcalc.ownership import calculate
        arrays=('teams','shares','residuals','windows','small_teams','memories','contexts')
        records=('models','options','benchmarks')
        for key in arrays+records:
            for mode in ('missing','null','empty'):
                with self.subTest(key=key,mode=mode):
                    scenario,inputs=load('owners-economics',['workload.sample_calls=1'])
                    if mode=='missing':del inputs.data['owners'][key]
                    else:inputs.data['owners'][key]=None if mode=='null' else ([] if key in arrays else {})
                    r=calculate(scenario,inputs)
                    self.assertGreater(r['computed_metrics'],0)
                    self.assertTrue(any(a['input'].startswith('owners.'+key) for a in r['alarms']))
                    self.assertEqual(len(r['tables']),9)


if __name__=='__main__':unittest.main()
