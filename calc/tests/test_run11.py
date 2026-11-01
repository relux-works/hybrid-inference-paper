"""Output counters include reasoning: generation, billing and timing must not sum it twice."""
import math
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import load, scenarios
from hybridcalc.paper_tables import Context, api_vector


class Run11Tests(unittest.TestCase):
    # All current base scenarios count output once; the bridge alone intentionally reproduces historical accounting.
    def test_base_scenario_accounting(self):
        for scenario in scenarios():
            if scenario['kind'] in ('legacy', 'bridge'):
                continue
            with self.subTest(scenario=scenario['name']):
                _, inputs = load(scenario['name'])
                self.assertEqual(inputs.get('workload.reasoning_extra_fraction'), 0)
                reason = inputs.locate('workload.reasoning_extra_fraction')['provenance']['reason']
                for evidence in ('126/126', '4577/4577', '93%', '1528194', 'Muse', 'unverified'):
                    self.assertIn(evidence, reason)

    # Independent measured output mean is the generated call field consumed by decode, API billing and timing.
    # This proves aggregate accounting on the fitted sample, not real session chronology or Muse's provider contract.
    def test_base_generated_tokens_are_output(self):
        scenario, inputs = load('paper-tables')
        context = Context(scenario, inputs)
        resolved = context.g.resolve(context.valid)
        self.assertFalse(resolved.alarms)
        calls = resolved.value
        measured = inputs.measured_json('stats')['agents']['all']
        mean = sum(row[2] for row in calls) / len(calls)
        self.assertAlmostEqual(mean, measured['output_per_call']['mean'], places=6,
                               msg='base generation must equal output_per_call alone')
        self.assertGreater(measured['reasoning_per_call']['mean'], 0)
        self.assertNotAlmostEqual(mean, measured['output_per_call']['mean'] +
                                  measured['reasoning_per_call']['mean'], places=1)
        # With zero input/cache tariffs, the actual API path bills exactly the generated output once.
        prices = dict(cache_write=0, cache_read=0, output=2)
        billed = api_vector(calls, prices, inputs.get('workload.chunk_calls'))
        self.assertAlmostEqual(sum(billed) / len(billed), mean * 2 / 1e6, places=12)

    # Switching only the explicit upper-bound fraction preserves every depth, new-token and tool draw.
    def test_upper_bound_preserves_joint_input_mix(self):
        samples=[]
        for fraction in (0, 1):
            scenario, inputs = load('paper-tables', ['workload.reasoning_extra_fraction='+str(fraction)])
            context=Context(scenario,inputs)
            samples.append(context.g.resolve(context.valid).value)
        a,b=samples
        self.assertEqual([(d,n,t) for d,n,o,t in a], [(d,n,t) for d,n,o,t in b])
        self.assertTrue(all(y[2] >= x[2] for x,y in zip(a,b)))
        _,inputs=load('paper-tables')
        expected=inputs.measured_json('stats')['agents']['all']['reasoning_per_call']['mean']
        self.assertAlmostEqual(sum(y[2]-x[2] for x,y in zip(a,b))/len(a), expected, places=6)

    # The same actual-output oracle passes normally and fails with a planted sum, with no mutation to inputs/files.
    def test_planted_output_plus_reasoning_is_rejected(self):
        command=[sys.executable, str(Path(__file__).with_name('r11_controls.py')), 'output_sum']
        result=subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
        self.assertIn('test_base_generated_tokens_are_output', result.stderr)
        self.assertIn('base generation must equal output_per_call alone', result.stderr)
        self.assertIn('AssertionError', result.stderr)
        self.assertNotIn('ERROR:', result.stderr)


if __name__ == '__main__':
    unittest.main()
