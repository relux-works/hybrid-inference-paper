"""R7 bounded controls: intended named assertion is exit1, setup error2, survivor0."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc import paper_tables_r7 as engine
import test_paper_r7 as tests


def main(name):
    if name=='free_import':
        engine.hybrid_time=lambda server,wire,imp,last:server+wire+last
        tests.R7TablesTests.setUpClass();test=tests.R7TablesTests('test_turn_components')
    elif name=='drop_sliding':
        engine.arch_delta=lambda geometry,window,state,portion:portion*geometry[0]+state
        test=tests.R7ArchitectureTests('test_attached_script_numbers')
    elif name=='scale_gain':
        original=engine.measured_rate
        def ideal(*args):
            base=original(*args)
            return lambda k,d:base(1,d)
        engine.measured_rate=ideal
        tests.R7TablesTests.setUpClass();test=tests.R7PhysicsTests('test_actual_four_stream_gain')
    else:raise ValueError('unknown control')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
    if result.errors:return 2
    return 1 if len(result.failures)==1 and 'AssertionError' in result.failures[0][1] else 0


if __name__=='__main__':sys.exit(main(sys.argv[1]))
