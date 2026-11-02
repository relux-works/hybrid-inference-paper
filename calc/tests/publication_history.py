"""Read-only local fixture of the engine producer's pre-v2 publication contract."""
from contextlib import contextmanager
import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
from r13_audit import ROOT

REVISION = '49a1c1d38233f8edbbc1150c3e28dd69adb72997'


@contextmanager
def historical_fixture():
    # Exact source objects, never a download, checkout mutation or regenerated ledger.
    with tempfile.TemporaryDirectory(prefix='paper-history-') as directory:
        root = Path(directory)
        paths = ['paper', 'calc/tests', 'calc/hybridcalc', 'hybridcalc.py', 'calc/ENGINE-QUOTES-R13-261101.csv']
        payload = subprocess.check_output(['git', 'archive', REVISION, *paths], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            archive.extractall(root, filter='data')
        (root/'calc/out').symlink_to(ROOT/'calc/out', target_is_directory=True)
        (root/'data').symlink_to(ROOT/'data', target_is_directory=True)
        # Git reads must resolve the existing local object database, even if
        # the caller chooses a TMPDIR outside this checkout.
        gitdir = subprocess.check_output(['git','rev-parse','--absolute-git-dir'],cwd=ROOT,text=True).strip()
        (root/'.git').write_text('gitdir: '+gitdir+'\n')
        yield root
