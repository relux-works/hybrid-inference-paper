"""Bounded generated-output mutant: exit 1 is the intended named assertion, 2 a setup error."""
import argparse
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hybridcalc.analysis_graph as graph
from test_run11 import Run11Tests


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mutant', choices=('output_sum',))
    parser.parse_args()
    original=graph.sampled_calls
    def add_reasoning(inputs, settings, **kwargs):
        # Plant old output-plus-reasoning accounting in the actual base call field, after normal scenario loading.
        return original(inputs, dict(settings, reasoning_extra_fraction=1), **kwargs)
    graph.sampled_calls=add_reasoning
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([
        Run11Tests('test_base_generated_tokens_are_output')]))
    return 0 if result.wasSuccessful() else 2 if result.errors else 1


if __name__ == '__main__':
    sys.exit(main())
