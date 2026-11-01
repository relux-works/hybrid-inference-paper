"""Historical transcripts are pinned independently of formatter implementation."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

CALC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALC))
from hybridcalc.engine import run

GOLDEN = json.loads((CALC / 'tests/golden.json').read_text())


class GoldenTests(unittest.TestCase):
    # Each complete wrapper transcript equals its independently hashed lane output, including whitespace.
    def assert_golden(self, stem, overrides=()):
        expected = (CALC / (stem + '.out')).read_bytes()
        self.assertEqual(hashlib.sha256(expected).hexdigest(), GOLDEN[stem], 'reference output changed')
        actual = run(stem, overrides)['legacy_text'].encode('utf-8')
        self.assertEqual(actual, expected)

    # A controlled one-input mutation is rejected by the SAME equality assertion as the positive golden.
    def test_planted_input_breaks_matching_golden(self):
        self.assert_golden('hybrid_calc9_m3max_measured')
        from hybridcalc.engine import load
        _, inputs = load('hybrid_calc9_m3max_measured')
        key = next(k for k in inputs.data['legacy']['fleet'] if k.startswith('PEAK16_') and inputs.data['legacy']['fleet'][k]['value'] == 14e12)
        with self.assertRaises(AssertionError):
            self.assert_golden('hybrid_calc9_m3max_measured', ['legacy.fleet.{}=28000000000000'.format(key)])

    # Every engine, wrapper and test parses using Python 3.9 grammar; this is not a 3.9 runtime test.
    def test_python39_syntax(self):
        for path in CALC.rglob('*.py'):
            with self.subTest(path=path):
                ast.parse(path.read_text(), filename=str(path), feature_version=(3, 9))


def make_test(stem):
    def test(self):
        self.assert_golden(stem)
    return test


for _stem in GOLDEN:
    setattr(GoldenTests, 'test_' + _stem, make_test(_stem))


if __name__ == '__main__':
    unittest.main()
