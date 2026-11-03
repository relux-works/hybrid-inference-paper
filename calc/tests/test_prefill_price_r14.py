"""Prefill-price parity, zero-price floors and measured-option admission."""
import csv
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap,ROOT
from hybridcalc.paper_tables import Context
from hybridcalc.prefill_price_r14 import monthly_cost,price_threshold,rental_cost_per_mtoken,require_option,server_options,client_budget,prefilled_token_mean,active_storage_price


class PrefillPriceTests(unittest.TestCase):
    # Delta plus eventual output catch-up is charged once. Prefix depth and
    # duplicate output shadow must not inflate the billed prefill volume.
    def test_prefilled_volume_rejects_prefix_and_duplicate_output_charge(self):
        calls=[(1000000,10,5,0),(0,30,15,0)]
        self.assertEqual(prefilled_token_mean(calls),30)
        self.assertEqual(prefilled_token_mean([(0,n,o,t) for d,n,o,t in calls]),30)
        with self.assertRaisesRegex(InputGap,'nonnegative delta/output'):prefilled_token_mean([(0,10,-1,0)])

    # The analytic root equals the API bill and switches cost ordering on
    # either side; a negative provider price is forbidden, not a subsidy.
    def test_price_parity_and_negative_price_refusal(self):
        result=price_threshold(100,40,dict(storage=10,power=10),100)
        self.assertEqual(result['price'],2)
        self.assertEqual(monthly_cost(2,40,20),100)
        self.assertLess(monthly_cost(1.99,40,20),100)
        self.assertGreater(monthly_cost(2.01,40,20),100)
        self.assertEqual(monthly_cost(0,40,20),20)
        with self.assertRaisesRegex(InputGap,'nonnegative price'):monthly_cost(-.01,40,20)

    # Equality at zero is a valid boundary. A higher fixed floor has no
    # nonnegative prefill root; storage can fix only a storage-caused excess,
    # and free active RAM cannot erase separately charged inactive NVMe.
    def test_zero_price_floor_and_storage_counterfactual(self):
        self.assertEqual(price_threshold(20,40,dict(storage=10,power=10),100)['price'],0)
        storage=price_threshold(100,40,dict(storage=50,power=70),100)
        self.assertEqual(storage['verdict'],'no break-even')
        self.assertEqual(storage['required_storage_price'],.3)
        self.assertEqual(storage['blocker'],'storage at its current price')
        other=price_threshold(100,40,dict(storage=10,client_device=110),100)
        self.assertEqual(other['required_storage_price'],'no nonnegative storage price')
        self.assertIn('client_device',other['blocker'])
        self.assertAlmostEqual(active_storage_price(.3,'tiered',.2,.1),1.1)
        self.assertEqual(active_storage_price(.3,'ram_month',.2,.1),.3)
        self.assertIn('no nonnegative',active_storage_price(.01,'tiered',.2,.1))

    # Missing components, invalid volumes and negative component prices
    # cannot be hidden by a positive total. A normal positive budget works.
    def test_incomplete_or_negative_budget_refuses(self):
        self.assertEqual(price_threshold(100,1,dict(storage=0,power=0),1)['price'],100)
        for components in ({'power':1},{'storage':10,'power':-1}):
            with self.assertRaisesRegex(InputGap,'component'):price_threshold(100,1,components,1)
        with self.assertRaisesRegex(InputGap,'no client-served'):price_threshold(100,0,dict(storage=0),1)

    # Real archived options are present; neither a missing measured KV arm
    # nor a negative tariff can be replaced by a peak-ratio estimate.
    def test_measured_option_missing_and_negative_rental_refuse(self):
        s,i=load('paper-tables-r14');c=Context(s,i);options=server_options(c)
        self.assertEqual(set(options),{'llamacpp_pro6000','vllm_pro6000','vllm_b300_auto','vllm_b300_fp8kv'})
        self.assertEqual(require_option(options,'llamacpp_pro6000')['server_only'],0)
        self.assertEqual(require_option(options,'vllm_b300_fp8kv')['server_only'],1)
        with self.assertRaisesRegex(InputGap,'missing measured server option'):require_option(options,'unmeasured')
        self.assertAlmostEqual(rental_cost_per_mtoken(.001,2.52,.7),1)
        self.assertEqual(rental_cost_per_mtoken(.001,0,.7),0)
        with self.assertRaisesRegex(InputGap,'nonnegative rental price'):rental_cost_per_mtoken(.001,-1,.7)
        with patch.object(c.b300,'vllm',[]):
            with self.assertRaisesRegex(InputGap,'missing measured server option'):server_options(c)

    # Capacity-only desktop entries reuse explicit per-node whole-device
    # budgets; absent power refuses instead of turning into a free client.
    def test_desktop_budget_missing_power_refuses(self):
        _,i=load('paper-tables-r14')
        self.assertEqual(client_budget(i,'strix')['power'],.15)
        self.assertEqual(client_budget(i,'spark')['power'],.24)
        i.override('hardware.glm_family.strix2.power=null')
        with self.assertRaisesRegex(InputGap,'hardware.glm_family.strix2.power'):client_budget(i,'strix')


class PrefillPriceExportTests(unittest.TestCase):
    # Every client/share/policy/purchase/API combination has an exact price
    # root or an explicit nonnegative-price impossibility, with separate costs.
    def test_all_threshold_rows_and_cost_reconciliation(self):
        rows=list(csv.DictReader(io.StringIO((ROOT/'calc/out/run14/base/breakeven_prefill_price.csv').read_text())))
        self.assertEqual(len(rows),192)
        self.assertEqual(len({r['client'] for r in rows}),8)
        self.assertEqual({r['storage_policy'] for r in rows},{'default','cautious'})
        self.assertEqual({float(r['share']) for r in rows},{.2,.5,1})
        for row in rows:
            components=sum(float(row[k]) for k in ('storage_month','transfer_month','client_power_month','client_device_month','front_month','migration_month','overflow_api_month'))
            self.assertAlmostEqual(components,float(row['zero_prefill_price_month']))
            if row['verdict']=='break-even':
                self.assertAlmostEqual(monthly_cost(float(row['price_usd_mtoken']),float(row['prefilled_mtokens_month']),components),float(row['api_month']))
            else:
                self.assertEqual(row['price_usd_mtoken'],'no break-even')
                self.assertGreater(components,float(row['api_month']))
            self.assertEqual(row['llamacpp_pro6000_server_only'],'0')
            for option in ('vllm_pro6000','vllm_b300_auto','vllm_b300_fp8kv'):
                self.assertEqual(row[option+'_server_only'],'1')
                self.assertIn('server-only',row[option+'_basis'])
                self.assertGreater(float(row[option+'_usd_mtoken']),0)


if __name__=='__main__':unittest.main()
