"""Bounded expected-red controls. Exit 1 only for the named assertion; setup errors are 2."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc import paper_tables_r6 as engine
import test_paper_r6 as checks


def main(name):
    if name=='free_turbo':
        engine.pool_work=lambda requested,seconds,served,eligible,shadow:served*shadow
        test=checks.R6RoutingTests('test_turbo_pool_work')
    elif name=='double_shared_capacity':
        original=engine.shared_demand
        engine.shared_demand=lambda team,sharing,capacity,requested:original(team,sharing,capacity*sharing,requested)
        test=checks.R6CornerTests('test_shared_capacity_modes')
    elif name=='project_efficiency':
        original=engine.decode_bound
        engine.decode_bound=lambda *args:original(*args)*.34
        checks.R6TablesTests.setUpClass()
        test=checks.R6TablesTests('test_decode_bound')
    else:raise ValueError('unknown control')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
    if result.errors:return 2
    return 1 if len(result.failures)==1 and 'AssertionError' in result.failures[0][1] else 0


if __name__=='__main__':sys.exit(main(sys.argv[1]))
