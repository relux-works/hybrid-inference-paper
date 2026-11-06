"""The publishability boundary includes hidden intermediate blobs, not just HEAD."""
from pathlib import Path
from unittest.mock import patch
import contextlib,importlib.util,io,os,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('blob_gate',ROOT/'.scripts/check-introduced-blobs.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

class IntroducedBlobTests(unittest.TestCase):
    # Real synthetic blobs straddle the exact >=100MiB limit. They live only in
    # a tiny compressed local object store; no 100MiB working copy is created.
    # A removed oversized intermediate blob must still reject its descendant.
    def test_exact_size_boundary_and_removed_intermediate_blob(self):
        with tempfile.TemporaryDirectory()as tmp:
            env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
            for k in tuple(env):
                if k.startswith('GIT_')and k not in ('GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL','GIT_AUTHOR_NAME','GIT_AUTHOR_EMAIL','GIT_COMMITTER_NAME','GIT_COMMITTER_EMAIL'):env.pop(k)
            def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=tmp,env=env,input=input).decode().strip()
            git('init','-q');empty=git('mktree',input=b'');base=git('commit-tree',empty,input=b'base\n')
            def blob(size):
                p=subprocess.Popen(['git','hash-object','-w','--stdin'],cwd=tmp,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                block=b'x'*(1024*1024)
                while size:p.stdin.write(block[:min(size,len(block))]);size-=min(size,len(block))
                p.stdin.close();oid=p.stdout.read().decode().strip();p.stdout.close();self.assertEqual(p.wait(),0);return oid
            def commit(size,parent):
                oid=blob(size);tree=git('mktree',input=f'100644 blob {oid}\tboundary.bin\n'.encode());return git('commit-tree',tree,'-p',parent,input=b'boundary\n')
            below=commit(gate.LIMIT-1,base);at=commit(gate.LIMIT,base)
            # Clear inherited public-layout Git selection for the real fixture.
            with patch.dict(os.environ,env,clear=True),contextlib.redirect_stdout(io.StringIO())as log:
                self.assertEqual(gate.check(base,below,tmp)['failures'],[])
                result=gate.check(base,at,tmp);self.assertEqual(result['failures'],[{'path':'boundary.bin','bytes':gate.LIMIT}])
                removed=git('commit-tree',empty,'-p',at,input=b'remove oversized blob\n')
                self.assertEqual(gate.check(base,removed,tmp)['failures'],result['failures'])
                self.assertIn('WARNING introduced blob:',log.getvalue())
