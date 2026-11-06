"""Paper v3 evidence boundaries and run15 migration regression controls."""
import csv
import re
import unittest
from pathlib import Path
from r13_audit import ROOT, module


class PaperV3Tests(unittest.TestCase):
    # Each old r14 minute must fail at its named prose site while the correct
    # transcript table remains untouched. Source seconds are rounded once.
    def test_transcript_prose_old_minutes_rejected(self):
        off = module('v3_transcript_guard', ROOT/'paper/data/offload_bound.py')
        texts = {p.name: p.read_text() for p in off.SECTIONS.glob('*.tex')}
        self.assertEqual(off.missing(texts), [])
        for name, current, old in (
            ('summary minutes', 'ещё 4.1 минуты', 'ещё 6.9 минуты'),
            ('hybrid total minutes', 'задача занимает 5.3 минуты', 'задача занимает 9.2 минуты'),
            ('local total minutes', 'вместо 12.7.', 'вместо 18.3.'),
        ):
            with self.subTest(named_negative_plant='transcript_old_'+name):
                original = texts['90-appendix.tex']
                self.assertEqual(original.count(current), 1)
                planted = original.replace(current, old, 1)
                self.assertEqual(off.missing(dict(texts, **{'90-appendix.tex': planted})),
                                 ['run15 transcript prose '+name])
                print('named negative plant transcript_old_'+name+': rejected; clean control: pass')

    # All 22 cooled table cells match full-precision CSV medians at two
    # decimals. Both known double-rounding witnesses fail their named site.
    def test_measured_parallel_cells_round_csv_once(self):
        off = module('v3_rounding_guard', ROOT/'paper/data/offload_bound.py')
        texts = {p.name: p.read_text() for p in off.SECTIONS.glob('*.tex')}
        self.assertEqual(off.missing(texts), [])
        with (ROOT/'paper/data/engine/parallel_anchors.csv').open() as stream:
            anchors = {(int(r['depth']), int(r['streams'])): float(r['aggregate_tok_s'])
                       for r in csv.DictReader(stream)}
        with (ROOT/'paper/data/engine/parallel_historical_sensitivity.csv').open() as stream:
            anchors.update({(int(r['depth']),int(r['streams'])):float(r['aggregate_tok_s']) for r in csv.DictReader(stream) if 'kit1.6.6' in r['condition'] and r['streams']=='1'})
        lines = [line for line in texts['90-appendix.tex'].splitlines() if line.startswith('M3 Max, 1.6.6 &')]
        self.assertEqual(len(lines), 3)
        checked = 0
        for line, depth in zip(lines, (32784,65552,131088)):
            cells = [cell.strip() for cell in line.removesuffix(r' \\').split('&')]
            for cell, streams in zip(cells[2:], (1,2,4,6,8,12,16,24,32)):
                if cell:
                    self.assertEqual(cell, f'{anchors[depth,streams]:.2f}')
                    checked += 1
        self.assertEqual(checked, 22)
        for current, old in (('33.39','33.40'), ('38.46','38.47')):
            with self.subTest(named_negative_plant='double_round_'+old):
                original = texts['90-appendix.tex']
                self.assertEqual(original.count(current), 1)
                self.assertEqual(off.missing(dict(texts, **{'90-appendix.tex': original.replace(current,old,1)})),
                                 ['run15 cooled anchor 0'])

    # A six-agent number remains visible with its qualification. Dropping the
    # row or dagger, claiming measured coverage, or deleting the exclusion fails.
    def test_six_agent_row_is_retained_flagged_and_excluded(self):
        off = module('v3_six_guard', ROOT/'paper/data/offload_bound.py')
        texts = {p.name: p.read_text() for p in off.SECTIONS.glob('*.tex')}
        self.assertFalse(off.missing(texts))
        original = texts['91-calculation-history.tex']
        row = next(line for line in original.splitlines() if line.startswith(r'6\textsuperscript{†} &'))
        for name, plant, verdict in (
            ('six_row_removed', original.replace(row, ''), 'run14 agents 6'),
            ('six_dagger_removed', original.replace(r'6\textsuperscript{†} &', '6 &'), 'run14 agents 6'),
            ('six_false_measurement', original.replace('покрывает 0\\% вызовов;', 'покрывает 90\\% вызовов;'), 'run15 six coverage'),
            ('six_trend_exclusion_removed', original.replace('Строка сохраняется в таблице и исключена из трендов и отношений роста ёмкости по числу агентов.', ''), 'run15 six exclusion'),
        ):
            with self.subTest(named_negative_plant=name):
                self.assertNotEqual(plant, original)
                self.assertIn(verdict, off.missing(dict(texts, **{'91-calculation-history.tex': plant})))

    # Published gains from adding agents derive from the full-mix source rows;
    # the six-agent held-rate row is deliberately absent from these ratios.
    def test_capacity_ratio_and_zone_claims_match_engine(self):
        with (ROOT/'paper/data/engine/client_agents_day.csv').open() as stream:
            rows = {int(r['agents']): r for r in csv.DictReader(stream) if r['link_mbit']=='1000'}
        self.assertEqual(set(rows), {1,2,4,6,8,12,16})
        expected = {(1,4):('1.30','1.46'),(1,8):('1.46','1.72'),
                    (1,16):('1.57','1.92'),(4,16):('1.21','1.31')}
        for (a,b),values in expected.items():
            self.assertNotIn(6,(a,b))
            for key,value in zip(('local_sessions_day','hybrid_sessions_day'),values):
                self.assertEqual(f'{float(rows[b][key])/float(rows[a][key]):.2f}', value)
        self.assertEqual(float(rows[6]['measured_call_share']),0)
        self.assertEqual(f"{100*float(rows[6]['shallow_call_share']):.2f}",'90.67')
        self.assertEqual(f"{100*float(rows[16]['measured_call_share']):.2f}",'44.75')
        self.assertEqual(f"{100*float(rows[16]['measured_decode_time_share']):.2f}",'25.73')

    # Removed pending flags must stay removed; the unresolved CUDA-to-Metal
    # experiments remain explicit, and no stopped stage3 result is published.
    def test_completed_measurements_and_pending_boundaries(self):
        texts = {p.name:p.read_text() for p in (ROOT/'paper/sections').glob('*.tex')}
        all_text = '\n'.join(texts.values())
        for obsolete in ('% TODO(data): 27B KL study:', '% TODO(data): heterogeneous task-level',
                         '% TODO(data): sliding-window GPU qualification', '% TODO(data): kit 1.6.6 remeasurement'):
            self.assertNotIn(obsolete, all_text)
        self.assertNotIn('стадия 3',all_text)
        self.assertNotIn('оценка разнородных квантов',texts['14-conclusion.tex'])
        self.assertNotIn('оценка задач с разнородными квантами продолжаются',texts['00-abstract.tex'])
        self.assertIn(r'\textbf{Повтор checkpoint 10 на Metal.}',texts['90-appendix.tex'])
        self.assertIn(r'\pending{калибровка гетерогенного допуска CUDA и Metal на M3 Max',texts['90-appendix.tex'])
        self.assertIn('% TODO(data): CUDA-to-Metal calibration against BF16 reference.',texts['90-appendix.tex'])
        # Shown full-refresh arithmetic is bytes of attention KV, excluding
        # fixed state/framing; it restores node state, not local identity.
        self.assertEqual(34816*100000,3481600000)
        self.assertIn('Полное обновление attention-KV восстанавливает состояние узла',all_text)
        self.assertIn('без остальных данных состояния и обрамления',all_text)
