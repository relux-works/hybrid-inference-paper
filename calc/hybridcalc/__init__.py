"""Data-driven hybrid inference economics, Python 3.9+ standard library only."""
from .engine import run
from .inputs import InputError


def legacy_main(scenario):
    import sys
    sys.stdout.write(run(scenario)['legacy_text'])
