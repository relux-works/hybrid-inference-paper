"""Bounded R13 child-calibration mutant: expected AssertionError exit 1."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import hybridcalc.paper_tables_r8 as r8
from hybridcalc.paper_tables import Context
from test_run13 import Run13Tests


def without_measured_child(scenario,inputs):
    candidate=copy.deepcopy(scenario)
    candidate.pop('run13',None)
    return Context(candidate,inputs)


if __name__=='__main__':
    if sys.argv[1:]!=['unmeasured_child']:
        raise SystemExit('usage: r13_controls.py unmeasured_child')
    # Only the accounting helper's child Context is replaced; the ordinary
    # parent, raw measurements and all repository files remain untouched.
    with patch.object(r8,'Context',without_measured_child):
        result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([
            Run13Tests('test_accounting_child_retains_measured_m5')]))
    raise SystemExit(0 if result.wasSuccessful() else 2 if result.errors else 1)
