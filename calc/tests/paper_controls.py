"""Isolated expected-red controls for the paper checks; no production files change.

Run `python3 calc/tests/paper_controls.py overflow|parallel|selection`.
Exit 1 with a named AssertionError is the intended killed mutant; exit 0 means
it survived, and exit 2 means setup/test error rather than mutation evidence.
"""
import argparse
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc import paper_tables as pt
from test_paper_tables import PaperTablesTests,PaperInputTests


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mutant',choices=('overflow','parallel','selection'))
    mutant=parser.parse_args(argv).mutant
    if mutant=='overflow':
        # Claim narrowed: a capacity spill must carry a nonzero bill at a positive tariff.
        pt.overflow_cost=lambda requested,served,indices,prices,days:0
        test=PaperTablesTests('test_overflow_cost_conservation')
    elif mutant=='parallel':
        # Claim narrowed: four decode streams cannot be reported as four ideal single streams.
        original=pt.measured_rate
        def ideal(*args):
            rate=original(*args)
            return lambda k,d:rate(1,d)
        pt.measured_rate=ideal
        test=PaperTablesTests('test_measured_stream_anchor')
    else:
        # Claim narrowed: unsupported high-context calls retain their actual price, not the full-mix average.
        pt.overflow_cost=lambda requested,served,indices,prices,days:(requested-served)*sum(prices)/len(prices)*days
        test=PaperInputTests('test_selective_overflow_price')
    result=unittest.TextTestRunner().run(unittest.TestSuite([test]))
    return 0 if result.wasSuccessful() else 2 if result.errors else 1


if __name__=='__main__':sys.exit(main())
