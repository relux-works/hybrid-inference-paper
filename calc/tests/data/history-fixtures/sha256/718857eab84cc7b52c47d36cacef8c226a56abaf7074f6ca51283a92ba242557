"""Small-team grid and byte-preserving paper publication contract."""
import json
from pathlib import Path
import unittest
import gzip
import hashlib
import io
import os
import subprocess
import tarfile
import tempfile
from r10_controls import (BASELINE, HISTORY, ROOT, audit_revision, compare, git_blob_id, history_present, records,
                          require_additions_only, revision_csv)

R10 = '1e8f897c4f82092c632507b520515cefa7eecab5'


class Run10Tests(unittest.TestCase):
    # The provenance-bearing grid is ordered and includes exactly the requested six teams.
    def test_team_grid(self):
        grid = json.loads((ROOT / 'calc/hybridcalc/data/paper-tables.json').read_text())['paper_tables']['teams']
        self.assertEqual([row['value'] for row in grid], [5, 10, 20, 50, 500, 5000])
        self.assertEqual(grid[2]['provenance'], {'kind': 'estimate', 'reason':
            'owner request 2026-10-31, small-team own-server case'})

    # The immutable signed-R10 publication retains its R9 records byte for byte; R11 intentionally changes generation.
    def test_published_csv_byte_identity(self):
        summaries, added = audit_revision(R10)
        self.assertEqual(len(summaries), 42)
        self.assertTrue(added)
        for summary in summaries:
            with self.subTest(file=summary['file']):
                require_additions_only(summary)

    # The same gate accepts the actual published table and rejects a planted cost change on its team-5 row.
    def test_planted_team5_change_fails_byte_identity(self):
        name = 'perimeter_cost_light.csv'
        original = (ROOT / 'calc/out/paper' / name).read_bytes()
        summary, _ = compare(name, original, original)
        require_additions_only(summary)
        _, rows = records(original, name)
        row, raw = next(value for value in rows.values()
                        if value[0]['team'] == '5' and value[0]['route'] == 'all server')
        changed_raw = raw.replace(row['person_month'].encode(), b'0.123456789')
        self.assertNotEqual(changed_raw, raw)
        planted = original.replace(raw, changed_raw, 1)
        summary, _ = compare(name, original, planted)
        self.assertEqual(summary['changed'], 1)
        self.assertEqual(summary['removed'], 0)
        with self.assertRaisesRegex(AssertionError, 'byte identity'):
            require_additions_only(summary)

    # Reformatting unchanged numeric values, deleting/reordering old rows and adding team 30 also violate the gate.
    def test_forbidden_neighbor_changes(self):
        old = b'team,client,basis,person_month\n5,Mac,owned,1.0\n10,Mac,owned,2.0\n'
        for candidate in (old.replace(b'1.0', b'1.00'),
                          old.replace(b'5,Mac,owned,1.0\n', b''),
                          old.splitlines(keepends=True)[0] + b'10,Mac,owned,2.0\n5,Mac,owned,1.0\n',
                          old + b'30,Mac,owned,3.0\n'):
            summary, _ = compare('person_cost_s20.csv', old, candidate)
            with self.assertRaises(AssertionError):
                require_additions_only(summary)


    # The archived R9/R10 CSVs match their recorded git blob ids and SHA-256, so the audits above run in a public clone
    # that lacks the authors' history. Where that history is present, the archive also equals git byte for byte.
    def test_history_archive_matches_record_and_git(self):
        for revision in (BASELINE, R10):
            with self.subTest(revision=revision):
                stored = revision_csv(revision, source='archive')
                self.assertEqual(len(stored), 42)
                if history_present(revision):
                    self.assertEqual(revision_csv(revision, source='git'), stored)

    # Unverified history never reaches the audit: an unknown revision, an altered byte, a missing file and an
    # unexpected member are each refused with their own reason. The intact copy above is the positive control.
    def test_history_archive_rejects_unrecorded_or_altered_bytes(self):
        with self.assertRaisesRegex(AssertionError, 'no recorded history'):
            revision_csv('0' * 40, source='archive')
        with tarfile.open(HISTORY / 'paper-csv-history.tar.gz') as source:
            members = [(m, source.extractfile(m).read()) for m in source.getmembers()]
        first = next(i for i, (m, _) in enumerate(members) if m.name.startswith(R10 + '/'))
        def write(path, entries):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer, mode='w') as target:
                for member, data in entries:
                    info = tarfile.TarInfo(member.name)
                    info.size = len(data)
                    target.addfile(info, io.BytesIO(data))
            path.write_bytes(gzip.compress(buffer.getvalue()))
        member, data = members[first]
        cases = (('altered', members[:first] + [(member, data[:-1] + bytes([data[-1] ^ 1]))] + members[first + 1:],
                  'historical CSV bytes differ'),
                 ('missing', members[:first] + members[first + 1:], 'file set differs'),
                 ('nested', members + [(tarfile.TarInfo(R10 + '/sub/extra.csv'), b'x')], 'unexpected archive member'))
        with tempfile.TemporaryDirectory() as directory:
            for label, entries, reason in cases:
                with self.subTest(case=label):
                    path = Path(directory) / (label + '.tar.gz')
                    write(path, entries)
                    with self.assertRaisesRegex(AssertionError, reason):
                        revision_csv(R10, source='archive', archive=path)


    # Historical reads never contact a remote. In a blob:none partial clone whose promisor remote would serve every
    # object, a commit with missing blobs and an absent commit both come from the archive, history_present is False,
    # source='git' is refused, and the git trace shows no fetch. Full local history is read from git (positive
    # control). The trace detector is itself shown to catch a real lazy fetch in a second clone (instrument control).
    def test_history_reads_never_fetch(self):
        def git(*args, cwd, env=None):
            return subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'user.name=t', '-c', 'user.email=t@t']
                                  + list(args), cwd=cwd, env=env, check=True, capture_output=True, text=True).stdout
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            (source / 'calc/out/paper').mkdir(parents=True)
            git('init', '-q', cwd=source)
            git('config', 'uploadpack.allowFilter', 'true', cwd=source)
            contents = {'a.csv': b'x,y\n1,2\n', 'b.csv': b'x,y\n3,4\n'}
            for name, data in contents.items():
                (source / 'calc/out/paper' / name).write_bytes(data)
            git('add', '-A', cwd=source)
            git('commit', '-q', '-m', 'one', cwd=source)
            first = git('rev-parse', 'HEAD', cwd=source).strip()
            for clone in ('partial', 'control'):
                git('clone', '-q', '--no-checkout', '--filter=blob:none', 'file://' + str(source), str(root / clone),
                    cwd=root)
            (source / 'calc/out/paper/b.csv').write_bytes(b'x,y\n5,6\n')
            git('commit', '-q', '-am', 'two', cwd=source)
            second = git('rev-parse', 'HEAD', cwd=source).strip()
            record, members = {}, []
            for revision in (first, second):
                files = {}
                for name in contents:
                    data = git('show', revision + ':calc/out/paper/' + name, cwd=source).encode()
                    files[name] = dict(git_blob=git_blob_id(data), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
                    members.append((revision + '/' + name, data))
                record[revision] = dict(label=revision[:7], path='calc/out/paper', files=files)
            (root / 'record.json').write_text(json.dumps(record))
            with tarfile.open(root / 'archive.tar.gz', 'w:gz') as stored:
                for name, data in members:
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    stored.addfile(info, io.BytesIO(data))
            options = dict(archive=root / 'archive.tar.gz', record=root / 'record.json')
            trace = root / 'trace.txt'
            saved = os.environ.get('GIT_TRACE')
            os.environ['GIT_TRACE'] = str(trace)
            try:
                partial = root / 'partial'
                self.assertFalse(history_present(first, partial), 'missing blobs became present: a presence check fetched')
                self.assertFalse(history_present(second, partial), 'an absent commit became present: a presence check fetched')
                for revision in (first, second):
                    self.assertEqual(set(revision_csv(revision, repo=partial, **options)), set(contents))
                with self.assertRaisesRegex(AssertionError, 'not fully present in local git'):
                    revision_csv(first, source='git', repo=partial, **options)
                self.assertTrue(history_present(second, source))
                self.assertEqual(revision_csv(second, source='git', repo=source, **options),
                                 revision_csv(second, source='archive', repo=source, **options))
            finally:
                if saved is None:
                    os.environ.pop('GIT_TRACE', None)
                else:
                    os.environ['GIT_TRACE'] = saved
            def fetched(text):
                return any(word in text for word in (' fetch ', 'fetch-pack', 'upload-pack', 'not allowed'))
            self.assertTrue(trace.read_text())
            self.assertFalse(fetched(trace.read_text()), 'a historical read tried to fetch')
            control = root / 'control.txt'
            blob = record[first]['files']['a.csv']['git_blob']
            plain = {k: v for k, v in os.environ.items() if k not in ('GIT_NO_LAZY_FETCH', 'GIT_ALLOW_PROTOCOL')}
            git('cat-file', '-p', blob, cwd=root / 'control', env=dict(plain, GIT_TRACE=str(control)))
            self.assertTrue(fetched(control.read_text()), 'the trace detector missed a real lazy fetch')


if __name__ == '__main__':
    unittest.main()
