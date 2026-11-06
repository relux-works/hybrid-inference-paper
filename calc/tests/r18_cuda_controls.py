"""Bounded in-process CUDA faults: control exits0; named mutants exit1."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_run18
import test_r18_cuda_import_depth
from hybridcalc import measurements_r18 as r18,measurements_r16 as r16
from hybridcalc.run14_r5 import import_seconds

mode=sys.argv[1]
if mode=='mac_slope':
    # Recreate the reviewed defect without modifying any source or export.
    r18.cuda_import=lambda delta,depth,model:import_seconds(delta,'cuda_pr9')+r16.depth_fit()[1]*depth
    names=['test_r18_cuda_import_depth.CudaImportDepth.test_model_matches_pr9_cuda_measurements_at_depth']
elif mode=='allow_mac':
    original=r18.cuda_import
    r18.cuda_import=lambda delta,depth,model,**kw:original(delta,depth,model)
    names=['test_run18.Run18Contracts.test_cuda_import_refuses_mac_slope_on_cuda_host']
elif mode=='marginal_intercept':
    original=r18.cuda_depth_fit
    def wrong_fit():
        a,b,c=original()
        return import_seconds(0,'cuda_pr9'),b,c
    r18.cuda_depth_fit=wrong_fit
    names=['test_run18.Run18Contracts.test_cuda_joint_fit_refuses_rank_deficiency_and_negative_costs']
else:
    assert mode=='control','unknown control'
    names=['test_r18_cuda_import_depth.CudaImportDepth',
           'test_run18.Run18Contracts.test_cuda_import_refuses_mac_slope_on_cuda_host',
           'test_run18.Run18Contracts.test_cuda_joint_fit_refuses_rank_deficiency_and_negative_costs']
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
