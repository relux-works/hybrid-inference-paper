"""Service estimates are grounded in engine calls, explicit precision and tariff contracts."""
import math
from pathlib import Path
import sys
import unittest
CALC=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CALC))
from hybridcalc.engine import run


def named(result,prefix):
    return next(t for t in result['tables'] if t['name'].startswith(prefix))


class ServiceTests(unittest.TestCase):
    # Derived reference FLOPs/downloads round to calc8, and both API baselines use its same calls/cache-write convention.
    def test_derived_calc8_reference(self):
        result=run('service-fp8',['workload.reasoning_extra_fraction=1'])
        row=named(result,'Service reference')['rows'][0]
        self.assertAlmostEqual(row['prefill_flop']/1e12,196.69,places=2)
        self.assertEqual(round(row['download_bytes']/1e6),67)
        self.assertEqual(row['calls'],39904)
        apis=named(result,'Service API')['rows']
        flash=next(r for r in apis if r['profile']=='light' and r['users']==10 and r['api']=='Qwen3.8-Flash')
        dense=next(r for r in apis if r['profile']=='light' and r['users']==10 and r['api']=='27B median')
        self.assertAlmostEqual(flash['per_1000_calls'],3.42,places=2)
        self.assertAlmostEqual(dense['per_1000_calls'],10.51,places=2)

    # Integer capacity covers demand at <=70% load, with one minimum GPU; full-window billing and each egress price are independent arithmetic.
    def test_integer_capacity_and_billing(self):
        result=run('service-fp8')
        rows=named(result,'Service GPU')['rows']
        self.assertEqual(len(rows),60)
        for row in rows:
            self.assertGreaterEqual(row['gpus'],1)
            self.assertGreaterEqual(row['gpus']*10*3600*.7,row['users']*row['calls_day']*row['gpu_s_call'])
            self.assertEqual(row['egress_0'],0)
            self.assertAlmostEqual(row['egress_5'],row['tb_month']*5)
            self.assertAlmostEqual(row['egress_50'],row['tb_month']*50)
            self.assertAlmostEqual(row['total_month'],row['gpu_month']+row['egress_selected'])
            self.assertAlmostEqual(row['per_user_month'],row['total_month']/row['users'])
            if row['option']=='H100 SXM on demand':
                self.assertAlmostEqual(row['gpu_month'],row['gpus']*3.99*10*21)

    # BF16 halves H100 compute rate and doubles GPU-seconds, without changing derived client wire bytes or API workload.
    def test_precision_and_l40s_capacity_alarm(self):
        fp8=run('service-fp8')
        bf16=run('service-bf16-academic')
        a=named(fp8,'Service GPU')['rows'];b=named(bf16,'Service GPU')['rows']
        self.assertEqual(named(fp8,'Service API'),named(bf16,'Service API'))
        for first,second in zip(a,b):
            self.assertEqual(first['tb_month'],second['tb_month'])
            if second['option']=='L40S on demand':
                self.assertIn('alarm',second['gpus'])
                self.assertIn('54',str(second['gpus']))
                self.assertIsInstance(second['gpu_s_call'],float)  # Arithmetic is known, placement is not feasible.
                self.assertIn('alarm',second['gpu_month'])
            elif second['option'] in ('H100 SXM on demand','H100 PCIe on demand','Koyeb H100 warm serverless'):
                self.assertAlmostEqual(second['gpu_s_call'],2*first['gpu_s_call'])
                self.assertIsInstance(second['gpus'],int)
        self.assertEqual(len(bf16['alarms']),1)

    # Monthly tariffs include EUR conversion and setup independently; setup is shown upfront and amortized over the stated horizon.
    def test_monthly_currency_and_setup(self):
        r=run('service-fp8',['workload.sample_calls=232'])
        row=next(row for row in named(r,'Service GPU')['rows'] if row['option']=='Hetzner RTX PRO 6000 monthly')
        self.assertAlmostEqual(row['recurring_month'],row['gpus']*999*1.1130)
        self.assertAlmostEqual(row['setup_upfront'],row['gpus']*999*1.1130)
        self.assertAlmostEqual(row['gpu_month'],row['recurring_month']+row['setup_upfront']/12)
        self.assertAlmostEqual(row['first_month'],row['recurring_month']+row['setup_upfront']+row['egress_selected'])

    # Zero load and nonfinite MFU never yield GPU counts/costs; tariffs for unrelated options and API billing remain available.
    def test_load_and_mfu_alarms(self):
        for override in ('service.target_load=0','service.mfu=NaN','service.mfu=Infinity'):
            result=run('service-fp8',['workload.sample_calls=232',override])
            self.assertTrue(result['alarms'])
            for row in named(result,'Service GPU')['rows']:
                self.assertIn('alarm',row['gpus'])
                self.assertIn('alarm',row['gpu_month'])
                self.assertIsInstance(row['tb_month'],float)
            for row in named(result,'Service API')['rows']:
                self.assertIsInstance(row['month'],float)
        valid=run('service-fp8',['workload.sample_calls=232','service.target_load=1','service.egress_price=0'])
        self.assertFalse(valid['alarms'])
        for row in named(valid,'Service GPU')['rows']:
            self.assertEqual(row['egress_selected'],0)
            self.assertEqual(row['gpus'],max(1,math.ceil(row['users']*row['calls_day']*row['gpu_s_call']/(10*3600))))

    # Missing transfer bandwidth prevents byte/egress estimates but cannot change FLOP demand, GPU count, GPU tariff or API prices.
    def test_transfer_gap_preserves_gpu_and_api(self):
        from hybridcalc.engine import load
        from hybridcalc.service import calculate
        scenario,inputs=load('service-fp8',['workload.sample_calls=232'])
        before=calculate(scenario,inputs)
        del inputs.data['service']['transfer']['bandwidth']
        after=calculate(scenario,inputs)
        self.assertEqual(after['alarms'],[{'input':'service.transfer.bandwidth','reason':'missing input; offload impossible'}])
        self.assertEqual(named(before,'Service API'),named(after,'Service API'))
        for a,b in zip(named(before,'Service GPU')['rows'],named(after,'Service GPU')['rows']):
            self.assertEqual(a['gpus'],b['gpus'])
            self.assertEqual(a['gpu_month'],b['gpu_month'])
            self.assertIn('alarm',b['total_month'])




class QuantizedServiceTests(unittest.TestCase):
    # Production service default is Q4; Q4/Q6/Q8/FP8 share compute class, while weight admission tracks format size.
    def test_quantized_default_and_precision_memory(self):
        from hybridcalc.engine import scenarios
        names={x['name'] for x in scenarios()}
        self.assertNotIn('service-bf16',names)
        self.assertIn('service-bf16-academic',names)
        base=run('service-quantized',['workload.sample_calls=232'])
        fp8=run('service-fp8',['workload.sample_calls=232'])
        self.assertFalse(base['alarms'])
        self.assertTrue(all(r['precision']=='Q4' for r in named(base,'Service GPU')['rows']))
        for quant in ('Q6','Q8'):
            r=run('service-quantized',['workload.sample_calls=232','service.precision='+quant])
            self.assertFalse(r['alarms'])
            self.assertEqual([r['gpu_s_call'] for r in named(r,'Service GPU')['rows']],[r['gpu_s_call'] for r in named(fp8,'Service GPU')['rows']])
        nv=run('service-quantized',['workload.sample_calls=232','service.precision=NVFP4'])
        self.assertIn('alarm',named(nv,'Service GPU')['rows'][0]['gpus'])
        het=next(r for r in named(nv,'Service GPU')['rows'] if r['option']=='Hetzner RTX PRO 6000 monthly')
        self.assertIsInstance(het['gpus'],int)

    # Every added service format coefficient and FP4 throughput field has a named missing-input alarm in its selected scenario.
    def test_new_service_inputs_missing(self):
        from hybridcalc.engine import load
        from hybridcalc.service import calculate
        from hybridcalc.inputs import InputGap
        for quant in ('Q4','Q6','Q8','NVFP4'):
            scenario,inputs=load('service-quantized',['workload.sample_calls=1','service.precision='+quant])
            quantity=inputs.data['service']['bytes_per_parameter'][quant]
            original=dict(quantity)
            for field,value in [('value',0),('value',None),('value',float('nan')),('value',float('inf')),('unit','wrong'),('provenance',None)]:
                inputs.data['service']['bytes_per_parameter'][quant]=dict(original)
                inputs.data['service']['bytes_per_parameter'][quant][field]=value
                with self.assertRaises(InputGap):inputs.get('service.bytes_per_parameter.'+quant)
            del inputs.data['service']['bytes_per_parameter'][quant]
            r=calculate(scenario,inputs)
            self.assertIn({'input':'service.bytes_per_parameter.'+quant,'reason':'missing input'},r['alarms'])
        for option in ('h100_sxm','h100_pcie','l40s','koyeb','hetzner'):
            scenario,inputs=load('service-quantized',['workload.sample_calls=1','service.precision=NVFP4'])
            path='service.options.'+option+'.fp4_peak'
            quantity=inputs.data['service']['options'][option]['fp4_peak']
            for value in (None,float('nan'),float('inf'),-1):
                quantity['value']=value
                with self.assertRaises(InputGap):inputs.get(path)
            del inputs.data['service']['options'][option]['fp4_peak']
            self.assertIn({'input':path,'reason':'missing input'},calculate(scenario,inputs)['alarms'])


if __name__=='__main__':unittest.main()
