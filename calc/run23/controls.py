"""Process-local narrowing faults, each tied to a named regression witness."""
import argparse
from contextlib import ExitStack
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'));sys.path.insert(0,str(ROOT/'calc/tests'))
from run23 import economics as e, routing, sentences
from test_run23 import Run23Policy

FAULTS={
    'use_model_at_measurement':'test_measured_pro_point_never_replaced_by_model',
    'admit_pro_million':'test_pro_million_server_cannot_be_feasible',
    'double_restore':'test_mac_prefill_refuses_double_restore_with_measured_threshold_control',
    'hide_zero_offload':'test_zero_offload_sentence_refuses_missing_disclosure_with_control'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['control']+list(FAULTS));mode=parser.parse_args().mode
    suite=(unittest.defaultTestLoader.loadTestsFromTestCase(Run23Policy) if mode=='control'else unittest.TestSuite([Run23Policy(FAULTS[mode])]))
    with ExitStack()as stack:
        if mode=='use_model_at_measurement':
            stack.enter_context(patch.object(e.Server,'decode',lambda self,depth,streams=32,measurements=None:e.base.Server.decode(self,depth,streams,None)))
        elif mode=='admit_pro_million':
            original=e.Server.slots
            stack.enter_context(patch.object(e.Server,'require_capacity',lambda self,depth:None))
            stack.enter_context(patch.object(e.Server,'slots',lambda self,depth:1 if self.key=='pro6000_fp8'and depth>=1000000 else original(self,depth)))
        elif mode=='double_restore':
            original=routing.emit
            def wrong(server,client,depth,delta,local,recovery,transport,variant,links,measured=None,primary=True):
                if measured and isinstance(local,(int,float)):local+=recovery
                return original(server,client,depth,delta,local,recovery,transport,variant,links,measured,primary)
            stack.enter_context(patch.object(routing,'emit',wrong))
        elif mode=='hide_zero_offload':
            stack.enter_context(patch.object(sentences,'zero_offload',lambda row:''))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful()else 1)


if __name__=='__main__':main()
