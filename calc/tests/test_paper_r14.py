"""Finite publication migration controls; hardware measurements are not rerun."""
import csv
import json
import re
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from publication_v2 import ROOT, SOURCE_REVISION, check_publication, read_texts
from r13_audit import module


class PaperR14Tests(unittest.TestCase):
    # r5j repeats r5h m2: the day-capacity sentence must name its client.
    # Restoring the orphan pronoun must lose this exact wording guard.
    def test_traffic_day_sentence_names_client_r5h_m2(self):
        offload = module('r5j_traffic_subject', ROOT/'paper/data/offload_bound.py')
        texts = {p.name: p.read_text() for p in offload.SECTIONS.glob('*.tex')}
        self.assertFalse(offload.missing(texts))
        name = '04-channel.tex'
        clean = 'За восьмичасовой день клиент успевает обслужить'
        bad = texts[name].replace(clean, 'За восьмичасовой день он успевает обслужить', 1)
        self.assertNotEqual(bad, texts[name])
        self.assertIn('run14 traffic day client subject',
                      offload.missing(dict(texts, **{name: bad})))

    # Each printed B300 amount requires exactly one light-load row and one node.
    # Duplicate equal prices, missing rows and larger fleets cannot pass.
    def test_b300_light_reference_requires_unique_one_node_row(self):
        ranges = module('r5j_b300_uniqueness', ROOT/'paper/data/check_ranges.py')
        original = ranges.rows
        clean = original('perimeter_cost.csv')
        for team in (5, 20):
            row = next(r for r in clean if r['route'] == 'all server' and
                       r['server'] == ranges.B300 and r['profile'] == 'light' and r['team'] == str(team))
            for plant, data, message in (
                ('duplicate equal price', clean + [dict(row)], 'exactly one row'),
                ('duplicate different price', clean + [dict(row, person_month='1')], 'exactly one row'),
                ('missing light row', [r for r in clean if r is not row], 'exactly one row'),
                ('two-node light fleet', [dict(r, units='2') if r is row else r for r in clean], 'one node'),
            ):
                with self.subTest(team=team, plant=plant), patch.object(
                        ranges, 'rows', lambda name: data if name == 'perimeter_cost.csv' else original(name)):
                    with self.assertRaisesRegex(AssertionError, f'B300 light profile: {message}.*{team}'):
                        ranges.values(ranges.model())
        self.assertEqual(ranges.values(ranges.model())['B300 node per person, five people'], r'\$3\,373')
        self.assertEqual(ranges.values(ranges.model())['B300 node per person, twenty people'], r'\$845')

    # A cheaper medium/heavy profile cannot supply the explicitly light-load price.
    def test_b300_light_reference_ignores_other_profiles(self):
        ranges = module('r5j_b300_profiles', ROOT/'paper/data/check_ranges.py')
        original = ranges.rows
        def changed(name):
            data = original(name)
            if name != 'perimeter_cost.csv':
                return data
            return [dict(r, person_month='1') if r['route'] == 'all server' and
                    r['server'] == ranges.B300 and r['profile'] != 'light' else r for r in data]
        with patch.object(ranges, 'rows', changed):
            values = ranges.values(ranges.model())
        self.assertEqual(values['B300 node per person, five people'], r'\$3\,373')
        self.assertEqual(values['B300 node per person, twenty people'], r'\$845')

    # Each price site keeps its profile/node scope; the caption keeps both the
    # measured M5 Max basis and the limits on transfer to 128 GB and Ultra.
    def test_r5j_economics_scope_and_m5_basis_reject_stale_wording(self):
        offload = module('r5j_economics_wording', ROOT/'paper/data/offload_bound.py')
        texts = {p.name: p.read_text() for p in offload.SECTIONS.glob('*.tex')}
        self.assertFalse(offload.missing(texts))
        name = '07-economics.tex'
        for key in ('B300 light reference five', 'B300 light reference five comparison',
                    'B300 light reference twenty comparison', 'economics M5 measured basis'):
            key = 'run14 ' + key
            file, marker, phrase = offload.expected()[key]
            self.assertEqual(file, name)
            # Restrict the plant to the guard's own paragraph/sentence site.
            start = texts[name].index(marker)
            pattern = r'\s+'.join(map(re.escape, phrase.split()))
            match = re.search(pattern, texts[name][start:])
            self.assertIsNotNone(match)
            at, end = start + match.start(), start + match.end()
            bad = texts[name][:at] + 'УСТАРЕВШАЯ ОСНОВА' + texts[name][end:]
            self.assertIn(key, offload.missing(dict(texts, **{name: bad})))

    # Every producer payload remains the exact reviewed input; the audit also
    # reruns the producer at its own text revision (recorded in the gap map).
    def test_engine_payloads_and_embedded_snapshot_keep_exact_bytes(self):
        paths = subprocess.check_output([
            'git', 'ls-tree', '-r', '--name-only', SOURCE_REVISION,
            'hybridcalc.py', 'calc/hybridcalc', 'calc/out/run14',
            'calc/ENGINE-REPORT-R14-261102.md', 'calc/ENGINE-QUOTES-R14-261102.csv',
        ], cwd=ROOT, text=True).splitlines()
        paths += subprocess.check_output(['git', 'ls-tree', '-r', '--name-only',
            SOURCE_REVISION, 'calc'], cwd=ROOT, text=True).splitlines()
        paths = sorted({p for p in paths if p.startswith(('calc/hybridcalc/', 'calc/out/run14/',
            'calc/R14-R5-', 'calc/ENGINE-REPORT-R14-', 'calc/ENGINE-QUOTES-R14-')) or p == 'hybridcalc.py'})
        self.assertGreater(len(paths), 100)
        for name in paths:
            with self.subTest(file=name):
                self.assertEqual((ROOT/name).read_bytes(), subprocess.check_output(
                    ['git', 'show', SOURCE_REVISION+':'+name], cwd=ROOT))
        source = ROOT/'calc/out/run14/base'
        embedded = ROOT/'paper/data/engine'
        self.assertEqual({p.name for p in source.glob('*.csv')}, {p.name for p in embedded.glob('*.csv')})
        for p in source.glob('*.csv'):
            self.assertEqual(p.read_bytes(), (embedded/p.name).read_bytes(), p.name)

    # The existing site count and offload names cannot shrink during migration.
    # Changed direction names are explicitly mapped, rather than waived.
    def test_no_prior_range_or_offload_site_is_removed(self):
        migration = json.loads((ROOT/'calc/tests/data/paper-r14-migration.json').read_text())
        ranges = module('r14_ranges_inventory', ROOT/'paper/data/check_ranges.py')
        offload = module('r14_offload_inventory', ROOT/'paper/data/offload_bound.py')
        renamed = migration['range_renames']
        for key, count in migration['range_values'].items():
            self.assertEqual(len(ranges.SITES[renamed.get(key, key)]), count, key)
        for key, count in migration['range_directions'].items():
            self.assertEqual(len(ranges.DIRECTION_SITES[renamed.get(key, key)]), count, key)
        self.assertLessEqual(set(migration['offload_names']), set(offload.expected()))
        self.assertEqual(sum(map(len, ranges.SITES.values())) + sum(map(len, ranges.DIRECTION_SITES.values())), 156)

    # A mismatched retention or latency budget and an artificial large-team cap
    # each lose the named constraint; the untouched snapshot is the control.
    def test_symmetric_budget_guard_rejects_each_asymmetry(self):
        ranges = module('r14_symmetric_controls', ROOT/'paper/data/check_ranges.py')
        self.assertTrue(ranges.symmetric_budgets())
        original = ranges.rows
        for field, bad in [('retained_sessions', '1'), ('latency_p90_limit_s', '1'),
                           ('office_policy', 'cap RTX at100')]:
            def changed(name, field=field, bad=bad):
                data = original(name)
                if name.startswith('symmetric_storage_candidates'):
                    data = [dict(r, **{field: bad}) if r['route'] == 'hybrid' and
                            r['team'] == '500' and r['client'] == ranges.CLIENT else r for r in data]
                return data
            with self.subTest(field=field), patch.object(ranges, 'rows', changed):
                self.assertFalse(ranges.symmetric_budgets())
        self.assertTrue(ranges.symmetric_budgets())

    # The optimized team chart is independently selected from the producer rows;
    # neither a fixed-B300 reference nor an API cost may replace its series.
    def test_team_chart_uses_symmetric_selected_rows_at_all_sizes(self):
        def read(name):
            with (ROOT/name).open() as stream:
                return list(csv.DictReader(stream))
        chart = read('paper/data/team-perimeter.csv')
        source = read('calc/out/run14/base/perimeter_cost.csv')
        self.assertEqual([int(r['team']) for r in chart], [5, 10, 20, 50, 500, 5000])
        for row in chart:
            for profile in ('light', 'medium', 'heavy'):
                for route, suffix in [('all server', 'own'), ('hybrid', 'hybrid')]:
                    options = [r for r in source if r['team'] == row['team'] and r['profile'] == profile
                        and r['route'] == route and r['selected'] == '1' and (route == 'all server' or
                        (r['client'] == 'M5 Max 64 GB' and r['basis'] == 'Mac already owned'))]
                    self.assertEqual(len(options), 1)
                    self.assertEqual(float(row[profile+'_'+suffix]), round(float(options[0]['person_month']), 2))
        text = (ROOT/'paper/sections/07-economics.tex').read_text()
        figure = text[text.index('\\begin{figure}', text.index('Команды от 5')):]
        figure = figure[:figure.index('\\end{figure}')]
        self.assertIn('data/team-perimeter.csv', figure)
        self.assertNotIn('data/team-cost-s20.csv', figure)
        self.assertNotIn('data/team-cost-s50.csv', figure)

    # Both price verdicts are required: rejecting every threshold must fail the
    # near-zero M5 50% positive case; the M3 20% zero-price floor must still block.
    def test_price_boundary_preserves_exception_and_no_break_even(self):
        with (ROOT/'calc/out/run14/base/breakeven_prefill_price.csv').open() as stream:
            data = list(csv.DictReader(stream))
        def select(client, share):
            return next(r for r in data if r['client'] == client and r['share'] == share and
                r['storage_policy'] == 'default' and r['basis'] == 'owned' and r['target'] == 'cheapest API')
        blocked = select('M3 Max 128 GB (measured)', '0.2')
        self.assertGreater(float(blocked['zero_prefill_price_month']), float(blocked['api_month']))
        self.assertEqual(blocked['verdict'], 'no break-even')
        admitted = select('M5 Max 64 GB', '0.5')
        self.assertEqual(admitted['verdict'], 'break-even')
        self.assertGreater(float(admitted['price_usd_mtoken']), 0)
        self.assertLess(float(admitted['price_usd_mtoken']), .016)
        check_publication()
        texts = read_texts()
        name = 'paper/sections/07-economics.tex'
        for old, bad in [('накладные расходы даже при бесплатном prefill', 'цена prefill'),
                         ('server-only', 'qualified hybrid'), ('0.016', '0.160')]:
            planted = texts[name].replace(old, bad, 1)
            self.assertNotEqual(planted, texts[name])
            with self.subTest(plant=old), self.assertRaises(AssertionError):
                check_publication(texts=dict(texts, **{name: planted}))


if __name__ == '__main__':
    unittest.main()
