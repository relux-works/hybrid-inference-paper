"""Bounded in-process faults; never edit the candidate or measurement bytes."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc import run14_r5 as r5,session_hosting as hosting
from hybridcalc.measurements_r14 import ParallelAnchors


def main(fault):
    if fault in ('negative_price','missing_option','zero_price_floor','double_catchup'):
        from hybridcalc import prefill_price_r14 as price
        if fault=='negative_price':
            price.monthly_cost=lambda p,m,f:f+p*m
            name='test_price_parity_and_negative_price_refusal'
        elif fault=='missing_option':
            price.require_option=lambda options,key:options.get(key,next(iter(options.values())))
            name='test_measured_option_missing_and_negative_rental_refuse'
        elif fault=='double_catchup':
            price.prefilled_token_mean=lambda calls:sum(n+2*o for d,n,o,t in calls)/len(calls)
            name='test_prefilled_volume_rejects_prefix_and_duplicate_output_charge'
        else:
            original=price.price_threshold
            def threshold(*args):
                result=original(*args)
                if result['verdict']=='no break-even':result.update(price=0,verdict='break-even')
                return result
            price.price_threshold=threshold
            name='test_zero_price_floor_and_storage_counterfactual'
        import test_prefill_price_r14
        result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test_prefill_price_r14.PrefillPriceTests(name)]))
        return 0 if result.wasSuccessful() else 1
    if fault=='flat_depth':
        original=ParallelAnchors.lookup
        def lookup(self,k,d):
            result=original(self,k,d)
            deepest=max(p['depth'] for p in self.points if p['streams']==result['measured_streams'])
            if d>deepest:result['aggregate_tok_s']=self.measured_lookup(result['measured_streams'],deepest)['aggregate_tok_s']
            return result
        ParallelAnchors.lookup=lookup
        name='test_depth_law_rejects_32k_reanchor_and_flat_clamp'
    elif fault=='upper_count':
        original=ParallelAnchors.lookup
        ParallelAnchors.lookup=lambda self,k,d:original(self,4 if k==3 else k,d)
        name='test_count_hole_rejects_upper_neighbor_and_above_max'
    elif fault=='zero_foreground':
        original=hosting.route
        hosting.route=lambda own,remote,shadow,output,wire,foreground,mode:original(own,remote,shadow,output,wire,[0]*len(foreground),mode)
        name='test_import_rejects_zero_device_time_and_nonwinning_offload'
    elif fault=='free_reload':
        original=r5.full_server_stats
        r5.full_server_stats=lambda c,calls,server,tier:original(c,calls,server,'HBM')
        name='test_symmetric_reload_rejects_free_eviction_and_nonfit'
    elif fault=='ignore_latency':
        r5.choose_candidate=lambda candidates,*limits:min(candidates,key=lambda r:r['person_month'])
        name='test_cheapest_admission_rejects_latency_violation'
    elif fault=='unchecked_cuda':
        data=r5.cuda_import_rows()
        r5.cuda_import_rows=lambda:data
        name='test_cuda_import_refuses_unverified_bytes_or_mac_rate'
    elif fault=='erase_reread':
        original=r5.step57_check
        def check(c,records=None):
            if records:
                records=copy.deepcopy(records)
                for r in records:
                    if r['kind']=='call':r['reread']=False
            return original(c,records)
        r5.step57_check=check
        name='test_step57_refuses_rereads_and_missing_calls'
    elif fault=='control':
        name=None
    else:raise ValueError(fault)
    import test_run14_r5
    suite=(unittest.defaultTestLoader.loadTestsFromTestCase(test_run14_r5.Run14R5Tests) if name is None else
           unittest.TestSuite([test_run14_r5.Run14R5Tests(name)]))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
