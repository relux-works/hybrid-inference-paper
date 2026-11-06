"""R5y rework: bounded publication contracts from accepted CPU-readable evidence."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from r13_audit import ROOT, module

SOURCE = ROOT/'data/measurements/paper-v5a2-2026-11-03'


def current_changelog(changelog):
    """Newest nonempty section, including the candidate when Unreleased is absent."""
    parts = re.split(r'^## \[([^\]]+)\][^\n]*\n', changelog, flags=re.M)
    for index in range(1, len(parts), 2):
        if parts[index+1].strip():
            return parts[index+1]
    raise AssertionError('missing current changelog section')


def link_technology_hits(sections, changelog):
    """Current prose and candidate notes; older released sections stay frozen."""
    unreleased = current_changelog(changelog)
    return re.findall(r'5G|Wi-Fi|iPhone|Ethernet|10GbE|мобильн|проводн',
                      '\n'.join(sections.values())+'\n'+unreleased, re.I)


class PaperV5a2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off = module('v5a2_offload', ROOT/'paper/data/offload_bound.py')
        cls.texts = {p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # The original bypass must fail in Unreleased or the active release candidate.
    # Older released history is a positive control; a retitle cannot hide it.
    def test_r5y_unreleased_link_technology_regression(self):
        log = (ROOT/'CHANGELOG.md').read_text()
        self.assertEqual(link_technology_hits(self.texts, log), [])
        for header in ('Unreleased', '0.1.0-rc.4'):
            valid = '# Changes\n\n## ['+header+']\n\n### Changed\n- Link at 9.75 MB/s.\n'
            self.assertEqual(link_technology_hits({}, valid), [])
            self.assertIn('5G', link_technology_hits({}, valid.replace('9.75 MB/s', '5G')))
            self.assertEqual(link_technology_hits({}, valid+'\n## [0.1.0-rc.3]\n5G\n'), [])
        for tech in ('5G', 'Wi-Fi', 'iPhone', 'Ethernet', '10GbE'):
            bad = log.replace('### Changed', '### Changed\n- '+tech, 1)
            self.assertNotEqual(bad, log)
            self.assertIn(tech, link_technology_hits(self.texts, bad))
            historical = log+'\n## [old-history]\n'+tech+'\n'
            self.assertEqual(link_technology_hits(self.texts, historical), [])

    # Each new semantic claim has an applied omission rejected at its own site.
    # This checks source contracts, not hardware reproducibility or significance.
    def test_every_r5y_data_site_has_named_omission_control(self):
        self.assertEqual(self.off.missing(self.texts), [])
        for name, (file, marker, phrase) in self.off.v5a2_expected().items():
            part = next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed, count = re.subn(r'\s+'.join(map(re.escape, phrase.split())),
                                    lambda _: 'УДАЛЕНО', part, count=1)
            self.assertEqual(count, 1, name)
            self.assertIn(name, self.off.missing(dict(self.texts, **{
                file:self.texts[file].replace(part, changed, 1)})))

    # The basis label is required independently at entry, figure and conclusion;
    # a label elsewhere cannot turn a current-looking conclusion into a pass.
    def test_r5y_million_basis_reaches_caption_and_conclusion(self):
        for name, old in (('million basis', 'архивный сценарий'),
                          ('million caption', 'Архивный сценарий run 14'),
                          ('million conclusion', 'текущую экономику vLLM эти отношения не задают')):
            key = 'v5a2 '+name
            file, marker, phrase = self.off.v5a2_expected()[key]
            self.assertIn(old, phrase)
            bad = self.texts[file].replace(old, 'ТЕКУЩИЙ РАСЧЁТ', 1)
            self.assertNotEqual(bad, self.texts[file])
            self.assertIn(key, self.off.missing(dict(self.texts, **{file:bad})))

    # Primary JSON was accepted separately. Its binary/partial-credit and
    # degenerate sidecar distinctions must survive publication at each depth.
    def test_ruler_primary_cells_and_sidecar_basis_follow_accepted_json(self):
        text = self.texts['11-limitations.tex']
        for family in ('qwen', 'glimmer'):
            record = json.loads((SOURCE/f'ruler-primary-{family}.json').read_text())
            for row in record['primary']:
                if row.get('pending'):continue
                self.assertEqual(row['n'], 390)
                vals = [row['difference']]+row['interval95']
                for val in vals:self.assertIn(f'{abs(val)*100:.4f}', text)
                if family=='qwen' and row['depth']==8192:
                    self.assertTrue(row['degenerate'])
                    self.assertEqual(row['interval95'], [0.0, 0.0])
                    self.assertIn('sidecars', row['claim_basis'])
                    for sidecar in row['sidecars'].values():
                        for bound in sidecar['interval95']:
                            self.assertIn(f'{abs(bound)*100:.4f}', text)
                self.assertEqual(row['equivalent_holm'], family=='qwen')
                self.assertTrue(row['holm_p_is_upper_bound'])
                self.assertFalse(row['decision_can_reverse_with_pending'])
            self.assertEqual(record['family_named_in_registration'], family=='qwen')
        for phrase in ('bootstrap вырожден', 'не служат основанием эквивалентности',
                       'Основание Qwen 8k составляют два дополнительных интервала',
                       'Для Glimmer на 8 тысячах эквивалентность в пределах',
                       'Эквивалентность текста при 2 п.п. не установлена ни на одной'):
            self.assertIn(phrase, text)

    # Timing is witnessed, not inferred from depth; Glimmer is an extension and
    # straddles registration, so it cannot become a confirmatory registered run.
    def test_r5y_glimmer_registration_scope_and_timing(self):
        text = self.texts['11-limitations.tex']
        for family, timing in (('qwen','before'), ('glimmer','straddling')):
            record = json.loads((SOURCE/f'ruler-primary-{family}.json').read_text())
            for row in record['primary']:
                if row.get('pending'):continue
                r = row['registration_timing'];self.assertEqual(r['timing'], timing)
                for field in ('start','end'):
                    self.assertIn(r[field][11:16], text)
        for phrase in ('Glimmer в регистрации не названа.',
                       'сбор Glimmer не является подтверждающим зарегистрированную гипотезу.',
                       'Те же правила применены к Glimmer по расширению.'):
            self.assertIn(phrase, text)

    # KL and top1 use document-paired intervals to the BF16 reference. Zero
    # f32 differences cannot promote bf16 to lossless or clear GPU/Mac waits.
    def test_bf16_kl_accepted_rows_and_remaining_scope(self):
        rows = json.loads((SOURCE/'bf16-report.json').read_text())['rows']
        text = self.texts['11-limitations.tex']
        for r in rows:
            if r['scope']=='paired' and r.get('other')=='state-Q4-local':
                scale=100 if r['metric']=='top1' else 1
                places=3 if scale==100 else 6
                for field in ('mean','ci_low','ci_high'):
                    val=r[field]*scale
                    if r['arm']=='state-f32':self.assertEqual(val, 0)
                    else:self.assertIn(f'{abs(val):.{places}f}',text)
        self.assertEqual(sum(r['scope']=='document' and r['arm']=='state-Q4-local' and r['metric']=='kl_nats' for r in rows),20)
        self.assertIn('40'+r'\,960', text)
        for phrase in ('Эталон KL есть распределение полной модели BF16',
                       'с зафиксированных квитанций на той же GPU, сборке и моделях',
                       r'\pending{запуск Mac для качества и скорости передачи bf16.'):
            self.assertIn(phrase, text)
        self.assertIn('bf16 округляет состояние',self.texts['90-appendix.tex'])
        self.assertIn('точные контроли классифицируют перенос bf16 как передачу с потерями',self.texts['90-appendix.tex'])

    # New raw Glimmer rates replace only measurement cells. Engine thresholds
    # remain on their frozen PRI4 anchors with the named import estimate.
    def test_glimmer_pri31_cells_and_interim_engine_boundary(self):
        text = self.texts['05b-models.tex'];facts=(SOURCE/'FACTS.md').read_text()
        for row in json.loads((SOURCE/'glimmer-pri31.json').read_text()):
            for key in ('prefill','decode'):
                for value in row[key]:self.assertIn(str(value),facts)
            def triple(values):return ' / '.join(str(v) for v in values)
            phrase=f"{row['depth']//1000} & {triple(row['prefill'])} & {triple(row['decode'])} & {row['save']:.3f} / {row['restore']:.3f}"
            self.assertIn(phrase, text)
        for phrase in ('дельты последовательны', 'на внешнем диске LaCie',
                       'без сброса слота', 'промежуточные скорости при фоновом приоритете и оценку вставки Qwen'):
            self.assertIn(phrase, text)
        self.assertIn('Glimmer'+r'\textsuperscript{†}', self.texts['07-economics.tex'])
        self.assertTrue((ROOT/'calc/out/run22/paper').is_dir())

    # The interpolation uses reciprocal rates, and the measured full rebuild
    # sums two sequential spans; neither is a measured Mac production latency.
    def test_intro_interpolation_and_server_rebuild_arithmetic(self):
        for a,b,t in ((1284,1131,8.44),(1131,1010,9.50)):
            self.assertAlmostEqual(10000*(.38/a+.62/b),t,places=2)
            self.assertIn(f'{t:.2f}',self.texts['01-introduction.tex'])
        self.assertAlmostEqual((518.29+1295.48)/60,30.2,places=1)
        self.assertAlmostEqual(524288/518.29,1011.6,places=1)
        self.assertAlmostEqual(515712/1295.48,398.1,places=1)
        self.assertNotIn(r'\pending{импорт, проверка логитов, генерация и добавочный prefill Mac',self.texts['08-million.tex'])
        self.assertIn('Прямой замер Mac.',self.texts['08-million.tex'])
        self.assertEqual(len(json.loads((ROOT/'data/measurements/paper-v5b-2026-11-03/r20-migration.json').read_text())),26)
        self.assertEqual(self.off.r20_signatures(self.texts),[])

    # The duplicate constant is repaired without removing conclusion coverage;
    # all evidence bytes are pinned, independent of publication numeric pins.
    def test_checker_files_and_archived_evidence_custody(self):
        ranges=module('v5a2_ranges',ROOT/'paper/data/check_ranges.py')
        self.assertEqual(len(ranges.FILES),len(set(ranges.FILES)))
        self.assertIn('14-conclusion.tex',ranges.FILES)
        readme=(SOURCE/'README.md').read_text()
        for p in SOURCE.iterdir():
            if p.is_file() and p.name!='README.md':
                self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
