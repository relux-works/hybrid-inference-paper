"""Reference-byte and two-ulp regeneration contracts, independent CSV examples."""
import math
import contextlib
import io
import platform
import sys
import unittest
from unittest.mock import patch
import regeneration as r


class RegenerationTests(unittest.TestCase):
    # Claim: only the named reference auto-selects bytes; unqualified versions use
    # the explicitly announced bounded mode, rather than silently skipping a test.
    def test_interpreter_selects_explicit_mode(self):
        with patch.object(r.platform,'python_implementation',return_value='CPython'):
            for version,mode in [((3,14,4),'bytes'),((3,12,3),'ulp'),((3,9,0),'ulp'),((3,14,5),'ulp')]:
                with patch.object(r.sys,'version_info',version):self.assertEqual(r.selected_mode(),mode)

    # Claim: intact CSV passes in each mode; one/two representable steps in either
    # direction pass only in tolerance mode, including negative values and binades.
    def test_positive_control_each_mode(self):
        for value in (1.0,2.0,-1.0,-2.0,1e-300):
            old=('id,value,label\n42,%r,cost\n'%value).encode()
            for mode in ('bytes','ulp'):r.compare_csv(old,old,{(1,1)},mode=mode)
            for direction in (math.inf,-math.inf):
                new=value
                for _ in range(2):
                    new=math.nextafter(new,direction)
                    actual=('id,value,label\n42,%r,cost\n'%new).encode()
                    r.compare_csv(actual,old,{(1,1)},mode='ulp')
                    with self.assertRaisesRegex(AssertionError,'reference CSV bytes differ'):
                        r.compare_csv(actual,old,{(1,1)},mode='bytes')

    # Claim: three representable steps fail specifically at the two-ulp bound.
    # This narrowing mutant cannot turn a material numerical change into success.
    def test_beyond_two_ulp_perturbation_is_rejected(self):
        new=1.0
        for _ in range(3):new=math.nextafter(new,math.inf)
        with self.assertRaisesRegex(AssertionError,'exceeds 2 ulp'):
            r.compare_csv(('x\n%r\n'%new).encode(),b'x\n1.0\n',{(1,0)},mode='ulp')

    # Claim: label/header/integer-byte changes are rejected in both modes, even
    # when numeric magnitude is close; neither tolerance nor quoting masks them.
    def test_changed_non_float_byte_is_rejected_in_either_mode(self):
        old=b'id,value,label\n42,1.0,cost\n'
        for actual in (old.replace(b'cost',b'costs'),old.replace(b'id',b'ID'),old.replace(b'42',b'43')):
            for mode in ('bytes','ulp'):
                with self.assertRaises(AssertionError):r.compare_csv(actual,old,{(1,1)},mode=mode)
        with self.assertRaisesRegex(AssertionError,'float encoding'):
            r.compare_csv(b'x\n42.0\n',b'x\n42\n',{(1,0)},mode='ulp')

    # Claim: no row/column/line-ending change, nonfinite replacement, changed sign
    # of zero or nonnumeric/quoted values can hide behind the float exception.
    def test_structure_and_special_values_fail_closed(self):
        old=b'x\n1.0\n'
        for actual in (b'x\n1.0,2\n',b'x\r\n1.0\r\n',b'x\nnan\n',b'x\ninf\n',b'x\n"1.0"\n'):
            with self.assertRaises(AssertionError):r.compare_csv(actual,old,{(1,0)},mode='ulp')
        with self.assertRaisesRegex(AssertionError,'zero spelling/sign'):
            r.compare_csv(b'x\n-0.0\n',b'x\n0.0\n',{(1,0)},mode='ulp')

    # Claim: the frozen reference schema controls types independently of regenerated
    # values: a float-looking text label and integer team ID stay outside tolerance.
    def test_reference_schema_excludes_text_and_integer_fields(self):
        header=(r.Path(__file__).resolve().parents[1]/'out/paper/person_cost_s50.csv').read_bytes().splitlines()[0]
        columns=header.decode().split(',')
        values=['50' if k=='team' else '1.0' if k=='basis' else '2.0' if k=='hybrid_without_overflow' else '0' for k in columns]
        raw=header+b'\n'+','.join(values).encode()+b'\n'
        self.assertEqual(r.reference_float_cells(raw,'person_cost_s50.csv'),{(1,columns.index('hybrid_without_overflow'))})
        with self.assertRaisesRegex(AssertionError,'non-float bytes'):
            r.compare_csv(raw.replace(b',1.0,',b',1.0000000000000002,'),raw,
                          r.reference_float_cells(raw,'person_cost_s50.csv'),mode='ulp')

    # Claim: automatic comparisons report their own resolved mode even after both
    # explicit controls; the running reference rejects drift, other runtimes bound it.
    def test_automatic_mode_is_attributed_and_enforced(self):
        old = b'x\n1.0\n'
        for mode in ('bytes', 'ulp'):
            with contextlib.redirect_stdout(io.StringIO()):
                r.compare_csv(old, old, {(1, 0)}, 'control.csv', mode=mode)
        expected = 'bytes' if platform.python_implementation() == 'CPython' and sys.version_info[:3] == (3, 14, 4) else 'ulp'
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            r.compare_csv(old, old, {(1, 0)}, 'actual-run12.csv', mode=None)
        line = capture.getvalue()
        self.assertIn('CSV regeneration [actual-run12.csv]: automatic ' + expected + ';', line)
        self.assertEqual(line.count('CSV regeneration'), 1)
        if expected == 'bytes': self.assertNotIn('ulp', line)
        new = ('x\n%r\n' % math.nextafter(1.0, math.inf)).encode()
        with contextlib.redirect_stdout(io.StringIO()):
            if expected == 'bytes':
                with self.assertRaisesRegex(AssertionError, 'reference CSV bytes differ'):
                    r.compare_csv(new, old, {(1, 0)}, mode=None)
            else:
                r.compare_csv(new, old, {(1, 0)}, mode=None)

    # Claim: default dispatch calls the resolver and announces/enforces each result;
    # forcing tolerance by default or removing the real announcement is rejected.
    def test_automatic_dispatch_uses_resolver_in_both_modes(self):
        old = b'x\n1.0\n'
        new = ('x\n%r\n' % math.nextafter(1.0, math.inf)).encode()
        for mode in ('bytes', 'ulp'):
            capture = io.StringIO()
            with patch.object(r, 'selected_mode', return_value=mode) as resolver, contextlib.redirect_stdout(capture):
                if mode == 'bytes':
                    with self.assertRaisesRegex(AssertionError, 'reference CSV bytes differ'):
                        r.compare_csv(new, old, {(1, 0)}, 'dispatch.csv')
                else:
                    r.compare_csv(new, old, {(1, 0)}, 'dispatch.csv')
            resolver.assert_called_once_with()
            self.assertIn('CSV regeneration [dispatch.csv]: automatic ' + mode + ';', capture.getvalue())
            if mode == 'bytes': self.assertNotIn('ulp', capture.getvalue())

    # Claim: a matching version alone cannot declare a different Python implementation
    # byte-equivalent; CPython is a positive control at the same version.
    def test_reference_version_requires_cpython_implementation(self):
        with patch.object(r.sys, 'version_info', (3, 14, 4)):
            for implementation, mode in (('PyPy', 'ulp'), ('CPython', 'bytes')):
                with patch.object(r.platform, 'python_implementation', return_value=implementation):
                    self.assertEqual(r.selected_mode(), mode)

    # Claim: tolerance admits only repr(binary64) spelling, even for unchanged fields;
    # alternate signs, padding, trailing zeroes and exponent spellings are rejected.
    def test_ulp_rejects_noncanonical_float_spelling(self):
        old = b'x\n0.5\n'
        with contextlib.redirect_stdout(io.StringIO()):
            r.compare_csv(old, old, {(1, 0)}, mode='ulp')
            for spelling in (b'+0.5', b'00.5', b'0.50', b'0.5e0', b'0.50000000000000001'):
                actual = b'x\n' + spelling + b'\n'
                for reference in (old, actual):
                    with self.assertRaisesRegex(AssertionError, 'noncanonical float spelling'):
                        r.compare_csv(actual, reference, {(1, 0)}, mode='ulp')
