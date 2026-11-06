"""Narrowing API faults, bound to named regression witnesses."""
import argparse,sys,unittest
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'calc'));sys.path.insert(0,str(ROOT/'calc/tests'))
from run24 import api
from test_run24 import Run24Policy
FAULTS={'ignore_whole_window':'test_under95_whole_window_endpoint_is_never_admitted',
    'merge_cadences':'test_core_cadence_cannot_be_replaced_by_v1_with_raw_controls',
    'use_study_depth_mix':'test_study_mix_price_cannot_replace_paper_profile_price'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['control']+list(FAULTS));mode=p.parse_args().mode
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Run24Policy)if mode=='control'else unittest.TestSuite([Run24Policy(FAULTS[mode])])
    with ExitStack()as stack:
        if mode=='ignore_whole_window':
            original=api.availability
            def wrong(key,row,study):
                rate,basis,source=original(key,row,study);return (100 if source=='measured_whole_window'else rate),basis,source
            stack.enter_context(patch.object(api,'availability',wrong))
        elif mode in ('merge_cadences','use_study_depth_mix'):
            original=api.prices
            def wrong(*args,**kwargs):
                rows=original(*args,**kwargs)
                for row in rows:
                    if mode=='merge_cadences'and row['cadence']=='amendment_core'and row['provider']=='coreweave/nvfp4':row['cache_hit_fraction']=.24250831474973794
                    if mode=='use_study_depth_mix'and row['cache_point']=='measured'and row['study_usd_per_1000']!='':row['effective_usd_per_1000_calls']=float(row['study_usd_per_1000'])
                return rows
            stack.enter_context(patch.object(api,'prices',wrong))
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful()else 1)


if __name__=='__main__':main()
