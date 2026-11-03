"""Finite second-review source, summary and negative publication controls."""
import re
import unittest
from r13_audit import ROOT, module


class Rc3Review2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off = module('rc3_review2_guard', ROOT/'paper/data/offload_bound.py')
        cls.texts = {p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # Each new paragraph/table contract rejects deletion at its own named site;
    # the clean publication must pass before testing the planted omissions.
    def test_second_review_sites_reject_removed_contracts(self):
        self.assertEqual(self.off.missing(self.texts), [])
        for name, (file, marker, wording) in self.off.rc3_review2_expected().items():
            with self.subTest(site=name):
                pattern = r'\s+'.join(map(re.escape, wording.split()))
                changed, count = re.subn(pattern, 'УДАЛЕНО', self.texts[file], count=1)
                self.assertEqual(count, 1, name)
                self.assertEqual(self.off.missing(dict(self.texts, **{file:changed})), [name])

    # Explicit wrong claims cover finite realistic overclaims, incorrect wire
    # formats and thresholds, independent of the generic first-digit CLI plant.
    def test_quality_and_source_overclaims_are_rejected(self):
        cases = (
            ('abstract CUDA identity', 'при одинаковой разбивке prefill', 'при любой разбивке prefill'),
            ('abstract KL scope', 'собственные веса клиента', 'точность узла'),
            ('abstract task bound', 'не чаще', 'чаще'),
            ('abstract paired plan', 'не устанавливают эквивалентность задач', 'доказывают эквивалентность задач'),
            ('limitations CUDA identity', 'при одинаковой разбивке prefill', 'при любой разбивке prefill'),
            ('limitations KL scope', 'не даёт измеримого различия', 'даёт измеримое различие'),
            ('limitations task bound', 'тест эквивалентности не заявлен', 'эквивалентность доказана'),
            ('limitations paired plan', 'Запланирована', 'Завершена'),
            ('wire formats', 'f32', 'q4'),
            ('fixed recurrent cost', '157~МБ', '15~МБ'),
            ('Wi-Fi all local', '5.19', '51.9'),
            ('first offload threshold', '8.45', '4.85'),
            ('compression future work', 'оставлены на будущее', 'дали двукратное ускорение'),
            ('LMCache mode limit', 'ещё не реализован', 'реализован'),
            ('Marconi recurrent prefix', 'точного совпадения', 'частичного совпадения'),
            ('agent persistence', 'на диске в 4-битном', 'в памяти в 8-битном'),
        )
        for suffix, old, bad in cases:
            name = 'rc3 review2 '+suffix
            file, marker, wording = self.off.rc3_review2_expected()[name]
            self.assertIn(old, wording)
            pattern = r'\s+'.join(map(re.escape, wording.split()))
            changed, count = re.subn(pattern, lambda _:wording.replace(old,bad,1), self.texts[file], count=1)
            self.assertEqual(count, 1)
            self.assertIn(name, self.off.missing(dict(self.texts, **{file:changed})), suffix)

    # Seven bibliography targets and independent comparison rows must remain.
    # These are publication custody checks, not online source availability tests.
    def test_references_and_comparison_cells(self):
        bib = (ROOT/'paper/references.bib').read_text()
        for key, target in (
            ('liu2024cachegen','2310.07240'), ('lmcacheCachegen','https://docs.lmcache.ai/mp/cachegen.html'),
            ('pan2025marconi','2411.19379'), ('zhang2024edgeshard','2405.14371'),
            ('zhang2026picospec','2603.19133'), ('li2026authorizedkv','2607.13093v4'),
            ('shkolnikov2026agentmemory','2603.04428'),
        ):
            entry, = re.findall(r'@misc\{'+key+r',\n(.*?)\n\}', bib, re.S)
            self.assertIn(target, entry)
            self.assertIn(r'\cite{'+key+'}', '\n'.join(self.texts.values()))
        table = self.texts['12-related.tex'].split(r'\label{tab:cache-mechanisms}',1)[1].split(r'\end{table}',1)[0]
        rows = [s for s in table.splitlines() if ' & ' in s and s.endswith(r' \\')]
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(len(s.split(' & ')) == 5 for s in rows))

    # Mechanical Russian style controls are bounded to the edited sections;
    # semantic antecedents and every possible quality judgment need prose review.
    def test_second_review_prose_style(self):
        for file in ('00-abstract.tex','10-resilience.tex','11-limitations.tex','12-related.tex'):
            text = self.texts[file]
            self.assertNotRegex(text, '[«»—–]|\\s---?\\s', file)
            self.assertNotRegex(text, r'\bне\s+[^.\n,]{1,80},\s+а\s|,\s+а\s+не\b', file)
