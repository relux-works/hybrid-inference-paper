"""Plant old MFU only in the measured-server compute node; exit1 is intended red."""
import argparse
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hybridcalc.paper_tables as tables
from test_run12 import Run12Tests


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mutant',choices=('old_mfu',));parser.parse_args()
    tables.measured_compute=lambda rows,model,reference_peak,target_peak,precision:target_peak*.3
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Run12Tests('test_measured_server_timing_replaces_mfu')]))
    return 0 if result.wasSuccessful() else 2 if result.errors else 1


if __name__=='__main__':sys.exit(main())
