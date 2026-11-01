"""Small-team grid and byte-preserving paper publication contract."""
import json
from pathlib import Path
import unittest
from r10_controls import ROOT, audit_revision, compare, records, require_additions_only


class Run10Tests(unittest.TestCase):
    # The provenance-bearing grid is ordered and includes exactly the requested six teams.
    def test_team_grid(self):
        grid = json.loads((ROOT / 'calc/hybridcalc/data/paper-tables.json').read_text())['paper_tables']['teams']
        self.assertEqual([row['value'] for row in grid], [5, 10, 20, 50, 500, 5000])
        self.assertEqual(grid[2]['provenance'], {'kind': 'estimate', 'reason':
            'owner request 2026-10-31, small-team own-server case'})

    # The immutable signed-R10 publication retains its R9 records byte for byte; R11 intentionally changes generation.
    def test_published_csv_byte_identity(self):
        summaries, added = audit_revision('1e8f897c4f82092c632507b520515cefa7eecab5')
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


if __name__ == '__main__':
    unittest.main()
