"""Repository-root entry point for the package in calc/hybridcalc (no installation)."""
from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent / 'calc' / 'hybridcalc')]

from hybridcalc.engine import run  # noqa: E402
from hybridcalc.inputs import InputError  # noqa: E402

if __name__ == '__main__':
    from hybridcalc.__main__ import main
    main()
