"""Bounded review-r5d mutants; expected exit 1 is a named behavioral failure.

Production files/exports are never edited. Mutated functions execute with the
real module globals; the native-script plant changes only the bytes copied by
its live-generator test into its isolated execution directory.
"""
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from test_run13 import Run13Tests
import hybridcalc.measurements_r13 as measurements
from hybridcalc.inputs import ROOT


def changed_function(function,old,new):
    source=inspect.getsource(function)
    assert source.count(old)==1, 'mutation must apply exactly once'
    source=source.replace(old,new)
    namespace={}
    exec(compile(source,'<r13fix-mutant>','exec'),measurements.__dict__,namespace)
    return namespace[function.__name__]


def control(name):
    test='test_archive_custody_refusals'
    if name in ('M3','M9','M10'):
        source=inspect.getsource(measurements.MeasuredM5)
        old,new={
            'M3':('            no_swap(review, phase)','            pass'),
            'M9':("('40-run-depth', '50-run-parallel', '55-run-scaling')","('40-run-depth',)"),
            'M10':('            no_swap(review, phase)','            # comment-only control\n            no_swap(review, phase)')}[name]
        assert source.count(old)==1
        namespace={}
        exec(compile(source.replace(old,new),'<r13fix-mutant>','exec'),measurements.__dict__,namespace)
        context=patch.object(measurements.MeasuredM5,'__init__',namespace['MeasuredM5'].__init__)
        test='test_measured_m5_rejects_swap_in_admitted_archive_phases'
    elif name in ('M5','M6','link','duplicate'):
        old,new={
            'M5':("member.name.startswith('/') or '..' in parts or ",''),
            'M6':("if any(not PurePosixPath(n).name.startswith('._') for n in extra):",'if False:'),
            'link':(' or member.issym() or member.islnk()',''),
            'duplicate':('if member.name in members:','if False:')}[name]
        mutated=changed_function(measurements.verified_archive,old,new)
        # The tests import this function by name, while package() uses the module.
        context=patch('test_run13.verified_archive',mutated)
    elif name=='M8':
        original=Path.read_bytes
        target=ROOT/'paper/data/arch_compare.py'
        before=original(target)
        old=b'(10, 4, 512, 32, False)'
        assert before.count(old)==1
        after=before.replace(old,b'(10, 4, 512, 32, True)')
        context=patch.object(Path,'read_bytes',lambda path: after if path==target else original(path))
        test='test_live_architecture_generator_matches_csv'
    else:
        raise SystemExit('usage: r13fix_controls.py M3|M9|M5|M6|M8|link|duplicate|M10')
    Run13Tests.setUpClass()
    print('mutant',name,'applied; behavioral test',test,flush=True)
    with context:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Run13Tests(test)]))
    return 0 if result.wasSuccessful() else 2 if result.errors else 1


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: r13fix_controls.py MUTANT')
    raise SystemExit(control(sys.argv[1]))
