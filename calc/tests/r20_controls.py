"""Process-only faults target named independent R20 contract assertions."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_run20
from hybridcalc import server_economics_r20 as s,measurements_r20 as r

mode=sys.argv[1]
if mode=='shared_kv':
    original=s.Server.decode
    def wrong(self,depth,streams=32,measurements=None):
        result=original(self,depth,streams,measurements);result['gain']=result['batch'];return result
    s.Server.decode=wrong;names=['ServerContracts.test_decode_refuses_depth_independent_gain_and_shared_kv']
elif mode=='pooled_memory':
    s.Server.slots=lambda self,depth:32
    names=['ServerContracts.test_decode_memory_refuses_pooled_capacity_and_impossible_single_session']
elif mode=='unvetted_api':
    s.admission=lambda row,context:[]
    names=['AdmissionContracts.test_context_admission_refuses_short_providers_with_boundary_control']
elif mode=='free_cache_misses':
    original=s.api_cost;s.api_cost=lambda row,means,hit:original(row,means,1)
    names=['AdmissionContracts.test_effective_price_rejects_free_cache_misses_and_bad_fraction']
elif mode=='free_bridge':
    original=s.Server.cached;s.Server.cached=lambda self,d,n,bridge='none':original(self,d,n,'none')
    names=['ServerContracts.test_bridge_refuses_free_cost_unknown_assumption_and_corrupt_evidence']
elif mode=='free_retention':
    r.Economics.retention=lambda *args:(0,0)
    names=['EconomicsContracts.test_retention_refuses_host_overflow_and_charges_residency_misses']
elif mode=='duplicate_concurrency':
    original=r.Economics.fleet_stats
    def wrong(self,*args):
        result=dict(original(self,*args));result['total_streams']*=8;return result
    r.Economics.fleet_stats=wrong
    names=['EconomicsContracts.test_fleet_batching_refuses_duplicated_team_concurrency']
elif mode=='double_catchup':
    original=r.Prepared.stats
    def wrong(self,spill,link):
        before=self.shadow;out=self.output
        self.shadow=[x/(1-spill) for x in before];self.output=[x/(1-spill) for x in out]
        try:return original(self,spill,link)
        finally:self.shadow=before;self.output=out
    r.Prepared.stats=wrong
    names=['EconomicsContracts.test_economics_refuses_free_new_client_calendar_rental_and_overflow']
elif mode=='nonminimal_own':
    original=r.Economics.own
    def wrong(self,*args):
        result=dict(original(self,*args))
        if isinstance(result['boxes'],int):result['boxes']+=1
        return result
    r.Economics.own=wrong
    names=['EconomicsContracts.test_economics_refuses_free_new_client_calendar_rental_and_overflow']
elif mode=='rental_missing_scope':
    r.conditional_scope=lambda *args:'observed offers; no persistence; shared work price lower bound'
    names=['EconomicsContracts.test_rental_basis_missing_coverage_regression_with_positive_control']
elif mode=='first_crossing':
    def wrong(a,b):return dict(from_people=next((i+1 for i,(x,y)in enumerate(zip(a,b))if x<y),s.alarm('none')),scan_max=len(a))
    r.break_even=wrong;names=['EconomicsContracts.test_break_even_refuses_first_lucky_crossing_and_unbounded_prose']
else:
    assert mode=='control';names=['AdmissionContracts','ServerContracts','EconomicsContracts']
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_run20.'+name for name in names])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful()else 1)
