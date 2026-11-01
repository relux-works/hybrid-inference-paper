#!/usr/bin/env python3
"""Tests for bench/*/scripts/kitlib.py: the depth ladder, the record check and the scrub-and-pack step.
Run from the repository root: python3 -m unittest discover -s bench/tests"""
import filecmp
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITLIB = os.path.join(ROOT, 'gpu', 'scripts', 'kitlib.py')
spec = importlib.util.spec_from_file_location('kitlib', KITLIB)
kitlib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kitlib)


def run(*args):
    return subprocess.run([sys.executable, KITLIB] + list(args), capture_output=True, text=True)


class Copies(unittest.TestCase):
    # Claim: both kits ship the same helper, so a fix in one reaches the other.
    def test_identical(self):
        self.assertTrue(filecmp.cmp(KITLIB, os.path.join(ROOT, 'mac', 'scripts', 'kitlib.py'), shallow=False))


class DepthList(unittest.TestCase):
    # Claim: the ladder ends at 249k at the reference context, and at the deepest level that leaves room for the
    # three deltas and their decoded tokens on smaller cards; a deepest level within 10% of a base level is dropped.
    def test_levels(self):
        self.assertEqual(kitlib.depth_list(262144), '16k,50k,100k,150k,200k,249k')
        self.assertEqual(kitlib.depth_list(101376), '16k,50k,88k')
        self.assertEqual(kitlib.depth_list(65536), '16k,50k')
        self.assertEqual(kitlib.depth_list(20000), '')

    # Claim: the last turn of the deepest level fits in the context (no overflow at the top of the ladder).
    def test_last_turn_fits(self):
        for ctx in (262144, 131072, 101376, 32768):
            deepest = int(kitlib.depth_list(ctx).split(',')[-1][:-1]) * 1000
            self.assertLessEqual(deepest + sum(kitlib.DELTAS) + kitlib.GEN * len(kitlib.DELTAS), ctx)


class CheckRecords(unittest.TestCase):
    def write(self, d, name, records):
        path = os.path.join(d, name)
        with open(path, 'w') as f:
            f.write('\n'.join(json.dumps(r) for r in records) + '\n')
        return path

    # Claim: error, interrupted and invalid-round records fail the check; a clean file and a reuse warning pass.
    def test_verdicts(self):
        with tempfile.TemporaryDirectory() as d:
            ok = self.write(d, 'ok.jsonl', [{'kind': 'meta'}, {'kind': 'segment'}])
            warn = self.write(d, 'warn.jsonl', [{'kind': 'round', 'streams': 2, 'valid': True, 'restore_reused': False}])
            self.assertEqual(run('check-jsonl', ok, warn).returncode, 0)
            # A round of agent sessions with re-reads passes with a warning that names them.
            rr = self.write(d, 'rr.jsonl', [{'kind': 'round', 'agents': 4, 'valid': True, 'rereads': 2}])
            r = run('check-jsonl', rr)
            self.assertEqual(r.returncode, 0)
            self.assertIn('re-read the context', r.stdout)
            for bad in ({'kind': 'error', 'error': 'x'}, {'kind': 'interrupted'}, {'kind': 'round', 'valid': False}):
                path = self.write(d, 'bad.jsonl', [{'kind': 'meta'}, bad])
                self.assertEqual(run('check-jsonl', path).returncode, 1, bad)


class ScrubPack(unittest.TestCase):
    def pack(self, files, user='alice', hosts=('gpu-box.example.org', 'gpu-box'), home='/home/alice', subdir=False):
        d = tempfile.mkdtemp()
        results, stage = os.path.join(d, 'results'), os.path.join(d, 'stage')
        os.makedirs(results)
        for name, text in files.items():
            with open(os.path.join(results, name), 'w') as f:
                f.write(text)
        if subdir:
            os.makedirs(os.path.join(results, 'nested'))
        args = ['scrub-pack', '--results', results, '--stage', stage, '--replace', '/home/alice/kit=<kit>',
                '--replace', '/home/alice/kit/work=<work>', '--replace', home + '=~', '--user', user]
        for h in hosts:
            args += ['--host', h]
        r = run(*args)
        staged = {}
        if r.returncode == 0:
            for name in os.listdir(stage):
                with open(os.path.join(stage, name), errors='replace') as f:
                    staged[name] = f.read()
        return r, staged

    # Claim: known folders, the home folder (also after -I), the user name as a path component and the host name are
    # replaced, a generic account name in an OS string is not a false alarm, URLs are ignored, and a manifest is written.
    def test_positive(self):
        r, staged = self.pack({
            'kit.log': 'args --slot-save-path /home/alice/kit/work/slots\nbuilt on gpu-box by /opt/x/alice/bin\n',
            'build.log': 'cc -I/home/alice/include -c x.c\nfetched https://huggingface.co/data/models/x.gguf\n',
            'system.json': '{"os": "Ubuntu 24.04 LTS"}\n'}, user='alice')
        self.assertEqual(r.returncode, 0, r.stdout)
        joined = ''.join(staged.values())
        self.assertNotIn('/home/alice', joined)
        self.assertIn('<work>/slots', joined)
        self.assertIn('-I~/include', joined)
        self.assertIn('/opt/x/<user>/bin', joined)
        self.assertIn('<host>', joined)
        self.assertIn('MANIFEST.json', staged)
        r, _ = self.pack({'system.json': '{"os": "Ubuntu 24.04 LTS"}\n'}, user='ubuntu', home='/home/ubuntu')
        self.assertEqual(r.returncode, 0, r.stdout)

    # Claim: each leak the first re-review found makes packing refuse with exit 3 and no manifest: the user name
    # inside a path component, paths glued to -I/-L under personal roots, another person's home, a file of an
    # unexpected type and a subdirectory.
    def test_refusals(self):
        cases = {
            'name inside component': {'b.log': 'cuda at /opt/conda/envs/alice-cuda/bin\n'},
            'name with suffix': {'b.log': 'tools in /nfs/tools/alice_cuda/include\n'},
            'name with digits': {'b.log': 'build in /work2/alice2025/build\n'},
            'glued -I': {'b.log': 'cc -I/data/acme-secret/include\n'},
            'glued -L': {'b.log': 'ld -L/scratch/proj-x/lib\n'},
            'other home': {'b.log': 'model at /home/bob/models/x.gguf\n'},
            'unexpected type': {'server.log.gz': 'binary'},
        }
        for label, files in cases.items():
            r, staged = self.pack(files)
            self.assertEqual(r.returncode, 3, (label, r.stdout))
            self.assertEqual(staged, {}, label)
        r, _ = self.pack({'a.log': 'fine\n'}, subdir=True)
        self.assertEqual(r.returncode, 3, r.stdout)

    # Claim: the leaks the third re-review found are refused: names inside paths under the home folder, a personal root
    # whose user component was masked, and other homes glued to '2>' or '->'.
    def test_refusals_under_home_and_after_arrows(self):
        cases = {
            'user inside a component under home': {'b.log': 'cuda: /home/alice/miniconda3/envs/alice-cuda/bin/nvcc\n'},
            'host inside a component under home': {'b.log': 'data in /home/alice/gpu-box_data/x\n'},
            'masked user under a personal root': {'b.log': 'cc from /scratch/alice/acme-merger/spack/bin/gcc\n'},
            'other home after 2>': {'b.log': 'cmd 2>/home/bob/err.log\n'},
            'other home after ->': {'b.log': 'link ->/home/bob/notes\n'},
        }
        for label, files in cases.items():
            r, staged = self.pack(files)
            self.assertEqual(r.returncode, 3, (label, r.stdout))

    # Claim: ordinary kit output packs for user and host names that occur inside common words or the kit's own paths
    # (the second re-review's false refusals): the model file, CUDA and Xcode paths, the kit's server logs.
    def test_no_false_refusals(self):
        files = {
            'server-depth-1.log': 'llama_model_loader: loaded meta data with 40 key-value pairs from /home/{u}/kit/work/models/Qwen3.8-27B-Q4_K_M.gguf\n',
            'build-configure.log': '-- CUDA include: /usr/local/cuda/targets/x86_64-linux/include\n-- C compiler: /Library/Developer/CommandLineTools/usr/bin/cc\n',
            'kit.log': 'llama-server exited during start; see results/server-depth-1.log\nargs --slot-save-path /home/{u}/kit/work/slots\n',
        }
        for user, host in (('wen', 'gpu-box'), ('cal', 'gpu-box'), ('lin', 'gpu-box'), ('dev', 'studio'), ('eve', 'studio'),
                           ('alice', 'server'), ('alice', 'qwen'), ('alice', 'linux')):
            fx = {k: v.replace('{u}', user) for k, v in files.items()}
            d = tempfile.mkdtemp()
            results, stage = os.path.join(d, 'results'), os.path.join(d, 'stage')
            os.makedirs(results)
            for name, text in fx.items():
                with open(os.path.join(results, name), 'w') as f:
                    f.write(text)
            r = run('scrub-pack', '--results', results, '--stage', stage, '--replace', '/home/%s/kit=<kit>' % user,
                    '--replace', '/home/%s/kit/work=<work>' % user, '--replace', '/home/%s/kit/work/models=<models>' % user,
                    '--replace', '/home/%s=~' % user, '--user', user, '--host', host)
            self.assertEqual(r.returncode, 0, (user, host, r.stdout))

    # Claim: a path the owner has looked at can be accepted with --allow, and only that path.
    def test_allow(self):
        r, _ = self.pack({'b.log': 'cuda at /opt/conda/envs/alice-cuda/bin\n'})
        self.assertEqual(r.returncode, 3)
        d = tempfile.mkdtemp()
        results, stage = os.path.join(d, 'results'), os.path.join(d, 'stage')
        os.makedirs(results)
        with open(os.path.join(results, 'b.log'), 'w') as f:
            f.write('cuda at /opt/conda/envs/alice-cuda/bin\nand /home/bob/x\n')
        r = run('scrub-pack', '--results', results, '--stage', stage, '--user', 'alice', '--allow', '/opt/conda/envs/alice-cuda')
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn('/home/bob/x', r.stdout)
        self.assertNotIn('alice-cuda', r.stdout)
        # An empty or root entry accepts nothing.
        r = run('scrub-pack', '--results', results, '--stage', stage + '2', '--user', 'alice', '--allow', '/', '--allow', '')
        self.assertEqual(r.returncode, 3, r.stdout)
        # An accepted path is recorded in the manifest.
        with open(os.path.join(results, 'b.log'), 'w') as f:
            f.write('cuda at /opt/conda/envs/alice-cuda/bin\n')
        r = run('scrub-pack', '--results', results, '--stage', stage + '3', '--user', 'alice', '--allow', '/opt/conda/envs/alice-cuda')
        self.assertEqual(r.returncode, 0, r.stdout)
        with open(os.path.join(stage + '3', 'MANIFEST.json')) as f:
            self.assertEqual(json.load(f)['scrub_allowed'], ['/opt/conda/envs/alice-cuda'])
        # An entry in unscrubbed form matches nothing and is not recorded, so it cannot carry the user name.
        r = run('scrub-pack', '--results', results, '--stage', stage + '4', '--replace', '/home/alice=~', '--user', 'alice',
                '--allow', '/opt/conda/envs/alice-cuda', '--allow', '/home/alice/private-project')
        self.assertEqual(r.returncode, 0, r.stdout)
        with open(os.path.join(stage + '4', 'MANIFEST.json')) as f:
            self.assertEqual(json.load(f)['scrub_allowed'], ['/opt/conda/envs/alice-cuda'])

    # Claim: Finder's .DS_Store and exFAT ._ files are left out without an error; a file:// URL is still checked.
    def test_finder_files_and_file_urls(self):
        r, staged = self.pack({'a.log': 'fine\n', '.DS_Store': 'x', '._a.log': 'x'})
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn('.DS_Store', staged)
        r, _ = self.pack({'a.log': 'see file:///home/bob/notes\n'})
        self.assertEqual(r.returncode, 3, r.stdout)

    # Claim: a home folder is replaced only as a whole path, so /srv/home/al... is not rewritten, and the leftover
    # personal path is then refused rather than hidden.
    def test_left_boundary(self):
        r, _ = self.pack({'a.log': 'see /srv/home/al/x\n'}, user='al', home='/home/al')
        self.assertEqual(r.returncode, 3, r.stdout)


if __name__ == '__main__':
    unittest.main()
