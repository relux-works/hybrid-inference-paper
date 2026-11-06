"""Growing-task capacity, billing and metadata-only source extension controls."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc import growing_r21 as g, deep_r21 as d, server_economics_r20 as s
from hybridcalc.engine import load
from hybridcalc.inputs import InputGap
from hybridcalc.paper_tables import Context


class GrowthContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec,inputs=load('deep-economics-r21');context_spec,_=load('paper-tables-r17')
        cls.c=Context(context_spec,inputs);cls.q=d.Server('b300_fp8');cls.glm=g.GlmServer(cls.q,inputs)

    # The growing trace conserves all input+output tokens and reserves the
    # last answer inside the target context; invalid task limits refuse.
    def test_trace_refuses_out_of_context_growth_with_output_conservation(self):
        agent=d.checked_stats()['agents']['claude']
        for limit in (200000,1000000):
            calls=g.trace(agent,limit)
            self.assertAlmostEqual(sum(n+o for depth,n,o,t in calls),limit)
            self.assertAlmostEqual(sum(calls[-1][:3]),limit)
            self.assertTrue(all(depth+n+o<=limit for depth,n,o,t in calls))
            self.assertTrue(all(n>0 for depth,n,o,t in calls))
            if limit==1000000:self.assertEqual(next(n for depth,n,o,t in calls if depth>200000),689.7)
        with self.assertRaisesRegex(InputGap,'target must'):g.trace(agent,1000001)

    # A328GB FP8 model cannot be one288GB GPU. The model budgets two
    # GPUs/replica and four replicas per physical eight-GPU node.
    def test_glm_refuses_single_gpu_replica_and_impossible_resident_session(self):
        cfg=s.config();cfg['reservation_depth']=1000000
        e=g.Economics(self.c,[(900000,690,762,8)],{'glm_two_b300':self.glm},cfg,'glm')
        self.assertGreater(self.glm.weights,288e9)
        self.assertEqual(self.glm.slots(1000000),37)
        self.assertEqual(e.units['glm_two_b300','bought'][1],4)
        with self.assertRaisesRegex(InputGap,'two-GPU capacity'):self.glm.slots(1000000000)

    # New Studio pricing is full amortization, not a free existing device;
    # rented node billing is a whole calendar box, not just busy seconds.
    def test_growing_prices_refuse_free_new_client_and_work_only_rental(self):
        cfg=s.config();cfg['reservation_depth']=1000000
        e=g.Economics(self.c,[(900000,690,762,8)],{'glm_two_b300':self.glm},cfg,'glm')
        owned=e.hybrid('glm_two_b300',5,1,'owned','bought','office_gigabit')
        new=e.hybrid('glm_two_b300',5,1,'new','bought','office_gigabit')
        self.assertAlmostEqual(new['person_month']-owned['person_month'],8000*.65/48)
        rent=e.hybrid('glm_two_b300',5,1,'owned','rented','office_gigabit')
        self.assertEqual(rent['unit_month'],76*730)
        self.assertGreater(rent['person_month'],76*730/5)
        with self.assertRaisesRegex(InputGap,'owned/new'):e.hybrid('glm_two_b300',5,1,'free','bought','office_gigabit')

    # Captioned57min is an estimate; the growing client actually prices only
    # newly-prefilled tokens, while output is charged separately to decode.
    def test_glm_prefill_refuses_output_as_new_input_with_separate_decode_control(self):
        calls=g.trace(d.checked_stats()['agents']['claude'],1000000)
        prepared=g.GlmPrepared(calls,self.glm,self.c)
        self.assertGreater(sum(prepared.own),0)
        self.assertLess(sum(prepared.own),57*60)
        self.assertGreater(sum(prepared.decode_device),0)
        self.assertEqual(prepared.wire[0],calls[0][1]*5984+152600000)


class GrowthCustody(unittest.TestCase):
    # Only an unused added module may refresh the conservative generator
    # identity; changing an existing numeric source refuses without writes.
    def test_metadata_extension_refuses_changed_existing_source_with_unchanged_payload_control(self):
        import r21_growth_audit as a
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);payload=b'x\n1\n';(root/'numeric.csv').write_bytes(payload)
            old={'engine.py':'a'*64};current=dict(old,**{'calc/hybridcalc/growing_r21.py':'b'*64})
            m=dict(generator=old,files={'numeric.csv':hashlib.sha256(payload).hexdigest()})
            (root/'r21_manifest.json').write_text(json.dumps(m))
            index=dict(generator=old,files={'numeric.csv':hashlib.sha256(payload).hexdigest(),'r21_manifest.json':hashlib.sha256((root/'r21_manifest.json').read_bytes()).hexdigest()})
            (root/'INDEX.json').write_text(json.dumps(index));before={p.name:p.read_bytes()for p in root.iterdir()}
            bad=dict(current,**{'engine.py':'c'*64})
            with self.assertRaisesRegex(AssertionError,'recomputation required'):a.extend_main_identity(root,bad)
            self.assertEqual(before,{p.name:p.read_bytes()for p in root.iterdir()})
            receipt=a.extend_main_identity(root,current)
            self.assertEqual(receipt['numeric_changes'],0)
            self.assertEqual((root/'numeric.csv').read_bytes(),payload)
            self.assertEqual(json.loads((root/'r21_manifest.json').read_text())['generator'],current)

    # Each growing task/export has a quote; dropping a quote or losing the
    # output portion cannot silently preserve a published comparison.
    def test_growing_exports_refuse_missing_quotes_and_unadmitted_glm_prices(self):
        import r21_growth_audit as a
        self.assertEqual(a.frozen(),931);self.assertEqual(a.verify_tables(),7)
        quotes=a.read(a.LEDGER);self.assertEqual(a.verify_quotes(quotes),len(quotes))
        with self.assertRaisesRegex(AssertionError,'quote coordinates'):a.verify_quotes(quotes[:-1])
        rows=a.read(a.OUT/'growing_task_economics.csv');self.assertEqual(len(rows),864)
        self.assertEqual({x['profile']for x in rows},{'existing_combined','claude_deep'})
        self.assertEqual({x['server']for x in rows},{'b300_fp8','b300_fp8_kv','glm_two_b300'})
        self.assertEqual({x['target_depth']for x in rows},{'200000','1000000'})
        schema=json.loads((a.OUT/'growth21_schema.json').read_text())['growing_task_economics']['columns']
        for key,value in (('target_depth','token'),('tasks_day','task/person/day'),('calls_per_task','call/task'),('usd_per_task','USD/task')):
            self.assertEqual(schema[key],value)
        self.assertTrue(all(x['api_cheapest_person_month']=='nan'for x in rows if x['model']=='glm'))
        traces=a.read(a.OUT/'growing_trace_summary.csv')
        for row in traces:
            self.assertAlmostEqual(float(row['new_tokens'])+float(row['output_tokens']),float(row['target_depth']))
        self.assertTrue(any(x['api_cheapest_person_month']!='nan'for x in rows if x['model']=='qwen'))


if __name__=='__main__':unittest.main()
