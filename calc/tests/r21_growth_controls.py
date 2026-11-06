"""Process-only faults for growing tasks and source-extension custody."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_run21_growth
from hybridcalc import growing_r21 as g
import r21_growth_audit as a

mode=sys.argv[1]
if mode=='drop_outputs':
    original=g.trace
    g.trace=lambda *args:[(d,n,0,t)for d,n,o,t in original(*args)]
    names=['GrowthContracts.test_trace_refuses_out_of_context_growth_with_output_conservation']
elif mode=='eight_glm_replicas':
    original=g.Economics.__init__
    def wrong(self,*args,**kwargs):
        original(self,*args,**kwargs)
        for key in self.units:
            month,count=self.units[key];self.units[key]=(month,8)
    g.Economics.__init__=wrong
    names=['GrowthContracts.test_glm_refuses_single_gpu_replica_and_impossible_resident_session']
elif mode=='free_device':
    original=g.Economics.hybrid
    def wrong(self,key,team,demand,basis,billing,link):return original(self,key,team,demand,'owned',billing,link)
    g.Economics.hybrid=wrong
    names=['GrowthContracts.test_growing_prices_refuse_free_new_client_and_work_only_rental']
elif mode=='accept_changed_main_source':
    a.extend_main_identity=lambda *args:dict(added=[],numeric_changes=0)
    names=['GrowthCustody.test_metadata_extension_refuses_changed_existing_source_with_unchanged_payload_control']
else:
    assert mode=='control'
    names=['GrowthContracts','GrowthCustody.test_metadata_extension_refuses_changed_existing_source_with_unchanged_payload_control']
suite=unittest.defaultTestLoader.loadTestsFromNames(['test_run21_growth.'+n for n in names])
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful()else 1)
