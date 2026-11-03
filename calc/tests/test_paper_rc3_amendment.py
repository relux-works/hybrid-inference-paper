"""Finite author and EXO/framing controls for the owner's rc.3 amendment."""
import re
import unittest
from r13_audit import ROOT, module

RU = 'Иван Опарин, Алексей Григорьев, Тимур Качкан, Сергей Щепетков'
EN = 'Ivan Oparin, Alexey Grigoriev, Timur Kackan and Sergei Shchepetkov'


def authors_valid(texts):
    tex = texts['paper/hybrid-inference.ru.tex']
    return (f'pdfauthor={{{RU}}}' in tex and f'{RU}\\\\' in tex
            and all(f'Authors: {EN} (Relux Works).' in texts[n]
                    for n in ('README.md', 'paper/README.md')))


class Rc3AmendmentTests(unittest.TestCase):
    # Four authors and Cyrillic PDF metadata must survive independently on
    # every current author surface. Historical changelog attribution stays historical.
    def test_authors_and_metadata_reject_missing_or_latin_names(self):
        texts = {n:(ROOT/n).read_text() for n in
                 ('paper/hybrid-inference.ru.tex', 'README.md', 'paper/README.md')}
        self.assertTrue(authors_valid(texts))
        for name, old, bad in (
            ('paper/hybrid-inference.ru.tex', f'pdfauthor={{{RU}}}',
             f'pdfauthor={{{RU.replace("Тимур Качкан", "Timur Kackan")}}}'),
            ('paper/hybrid-inference.ru.tex', RU+'\\\\', RU.rsplit(', ',1)[0]+'\\\\'),
            ('README.md', EN, EN.replace(' and Sergei Shchepetkov','')),
            ('paper/README.md', EN, EN.replace(' and Sergei Shchepetkov','')),
        ):
            with self.subTest(surface=name, plant=bad):
                self.assertIn(old, texts[name])
                self.assertFalse(authors_valid(dict(texts, **{name:texts[name].replace(old,bad,1)})))

    # Every new source/framing site rejects its own removed wording with an
    # exact named verdict. The checker CLI additionally mutates each site's first number/word.
    def test_new_sites_reject_removed_contracts(self):
        off = module('rc3_guard', ROOT/'paper/data/offload_bound.py')
        texts = {p.name:p.read_text() for p in off.SECTIONS.glob('*.tex')}
        self.assertEqual(off.missing(texts), [])
        for name, (file, marker, wording) in off.rc3_amendment_expected().items():
            pattern = r'\s+'.join(map(re.escape, wording.split()))
            changed, count = re.subn(pattern, 'УДАЛЕНО', texts[file], count=1)
            self.assertEqual(count, 1, name)
            self.assertEqual(off.missing(dict(texts, **{file:changed})), [name], name)

    # The EXO column compares seven mechanisms with NО for undocumented
    # session/recurrent behavior; the citation must resolve to the fetched page.
    def test_exo_comparison_and_reference(self):
        related = (ROOT/'paper/sections/12-related.tex').read_text()
        mechanisms = related.split(r'\begin{tabular}', 1)[1].split(r'\end{tabular}', 1)[0]
        rows = [s for s in mechanisms.splitlines() if ' & ' in s and s.endswith(r' \\')]
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(len(s.split(' & ')) == 7 for s in rows))
        self.assertIn(r'EXO Labs \cite{exolabsSpark}', rows[0])
        self.assertIn('KV послойно во время prefill', rows[2])
        self.assertIn('Оба механизма НО', rows[4])
        self.assertIn('EXO Labs', related)
        bib = (ROOT/'paper/references.bib').read_text()
        self.assertIn('@misc{exolabsSpark,', bib)
        self.assertIn('https://blog.exolabs.net/nvidia-dgx-spark/', bib)

    # Mechanical style checks cover the edited Russian prose; numeric ranges
    # and word hyphens remain permitted. Pronoun antecedents require prose review.
    def test_edited_prose_has_no_dash_connectors_or_guillemets(self):
        for file in ('00-abstract.tex','01-introduction.tex','12-related.tex'):
            text = (ROOT/'paper/sections'/file).read_text()
            self.assertNotRegex(text, '[«»—–]|\\s---?\\s', file)
            self.assertNotRegex(text, r'\bне\s+[^.\n,]{1,80},\s+а\s|,\s+а\s+не\b', file)
