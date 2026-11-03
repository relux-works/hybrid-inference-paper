"""Exact historical regression source with verified, content-only I/O adapters."""
from contextlib import contextmanager
from pathlib import Path
import tempfile
from history_fixtures import STORE, extract_snapshot
from r13_audit import ROOT


@contextmanager
def historical_fixture():
    with tempfile.TemporaryDirectory(prefix='paper-history-') as directory:
        root = Path(directory)
        extract_snapshot('r13-publication', root)
        extract_snapshot('r13-io-adapters', root)
        (root/'calc/out').symlink_to(ROOT/'calc/out', target_is_directory=True)
        (root/'data').symlink_to(ROOT/'data', target_is_directory=True)
        (root/'calc/tests/history_fixtures.py').write_bytes((ROOT/'calc/tests/history_fixtures.py').read_bytes())
        (root/'calc/tests/data/history-fixtures').symlink_to(STORE, target_is_directory=True)
        yield root
