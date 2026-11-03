"""Public-clone regression controls for immutable historical inputs."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import history_fixtures as fixtures
from publication_history import historical_fixture
from r13_audit import ROOT


class HistoryFixtureTests(unittest.TestCase):
    # Every snapshot and the exact object set verify, including all three incident refs.
    def test_complete_store_and_incident_provenance(self):
        self.assertEqual(fixtures.verify_store(), (13, 821))
        commits = {s['original_commit'] for s in fixtures.manifest().values()}
        self.assertTrue({
            '49a1c1d38233f8edbbc1150c3e28dd69adb72997',
            '2d457aed87d415043a2c0566f7a185607f11487e',
            '1a45cd2269fa8ea1a7027936a1f0bb35586460de',
        } <= commits)

    # Reviewed v2 bytes are immutable fixtures. The exact authorized v3 delta
    # is enumerated; every other current file must retain its reviewed bytes.
    def test_reviewed_paper_bytes_preserved(self):
        from publication_v2 import historical_delta
        delta = historical_delta('reviewed-paper')
        before = fixtures.snapshot_files('reviewed-paper')
        actual_changed = set()
        for name, data in before.items():
            with self.subTest(file=name):
                current = (ROOT/name).read_bytes()
                if name in delta:
                    actual_changed.add(name)
                    self.assertNotEqual(current, data)
                    self.assertEqual(hashlib.sha256(data).hexdigest(), delta[name]['before'])
                    self.assertEqual(hashlib.sha256(current).hexdigest(), delta[name]['after'])
                else:
                    self.assertEqual((ROOT/name).read_bytes(), data)
        self.assertEqual(set(delta), actual_changed)

    def isolated_selection(self, directory):
        store = Path(directory)
        (store/'sha256').mkdir()
        shutil.copyfile(fixtures.STORE/'manifest.json', store/'manifest.json')
        name = 'paper/data/arch-compare.csv'
        entry = fixtures.manifest()['r12-architecture']['files'][name]
        target = store/'sha256'/entry['sha256']
        shutil.copyfile(fixtures.STORE/'sha256'/entry['sha256'], target)
        return store, name, target

    # A single altered byte is rejected by SHA256; extraction leaves no partial output.
    def test_altered_object_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            store, name, target = self.isolated_selection(directory)
            clean = fixtures.snapshot_read('r12-architecture', name, store)
            target.write_bytes(clean[:-1] + bytes([clean[-1] ^ 1]))
            with self.assertRaisesRegex(AssertionError, 'fixture hash mismatch'):
                fixtures.snapshot_read('r12-architecture', name, store)
            destination = store/'extracted'
            with patch.object(fixtures, 'STORE', store):
                with self.assertRaisesRegex(AssertionError, 'fixture hash mismatch'):
                    fixtures.extract_snapshot('r12-architecture', destination)
            self.assertFalse(destination.exists())

    # A missing object cannot fall back to git, regenerate content or silently skip a comparison.
    def test_missing_object_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store, name, target = self.isolated_selection(directory)
            self.assertTrue(fixtures.snapshot_read('r12-architecture', name, store))
            target.unlink()
            with self.assertRaises(FileNotFoundError):
                fixtures.snapshot_read('r12-architecture', name, store)

    # Editing the manifest to authorize altered content fails its independent code pin.
    def test_manifest_rewrite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store, name, target = self.isolated_selection(directory)
            data = json.loads((store/'manifest.json').read_text())
            changed = b'forged fixture\n'
            data['snapshots']['r12-architecture']['files'][name] = {
                'sha256': hashlib.sha256(changed).hexdigest(), 'bytes': len(changed)}
            (store/'manifest.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(AssertionError, 'fixture manifest hash mismatch'):
                fixtures.snapshot_read('r12-architecture', name, store)

    # Unknown snapshots and unrecorded objects are refused; no broad directory waiver exists.
    def test_unknown_snapshot_and_extra_object_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'unknown historical fixture'):
            fixtures.snapshot_files('unrecorded')
        with tempfile.TemporaryDirectory() as directory:
            store, _, _ = self.isolated_selection(directory)
            for snapshot in fixtures.manifest().values():
                for entry in snapshot['files'].values():
                    (store/'sha256'/entry['sha256']).touch()
            (store/'sha256'/('0'*64)).write_bytes(b'extra')
            with self.assertRaisesRegex(AssertionError, 'fixture object set mismatch'):
                fixtures.verify_store(store)

    # Historical tests are pristine. I/O adapters preserve every original assert AST.
    # This bounds adapter changes; the historical subprocess tests exercise their behavior.
    def test_historical_assertions_and_tests_are_preserved(self):
        original = fixtures.snapshot_files('r13-publication')
        adapters = fixtures.snapshot_files('r13-io-adapters')
        def assertions(data):
            return [ast.dump(node) for node in ast.walk(ast.parse(data)) if isinstance(node, ast.Assert)]
        for name, data in adapters.items():
            self.assertEqual(assertions(original[name]), assertions(data), name)
            self.assertNotIn("['git'", data.decode(), name)
        with historical_fixture() as root:
            self.assertFalse((root/'.git').exists())
            for name in ('test_run13.py', 'test_r13_reverse.py'):
                path = 'calc/tests/'+name
                self.assertEqual((root/path).read_bytes(), original[path])


if __name__ == '__main__':
    unittest.main()
