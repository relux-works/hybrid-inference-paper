"""Finite R16 publication regressions; no hardware qualification is inferred."""
import csv
import re
import unittest
from r13_audit import ROOT, module


class PaperV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off = module('v4_measurement_guard', ROOT/'paper/data/offload_bound.py')
        cls.texts = {p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # Current singleton rates must follow the PRI31 source; the old segment
    # ladder is a real regression witness, even if all other prose is correct.
    def test_pri31_cold_ladder_rejects_background_regression(self):
        with (ROOT/'paper/data/engine/client_prefill_segments.csv').open() as stream:
            rates = [r['prefill_tok_s'] for r in csv.DictReader(stream) if r['client']=='M3 Max']
        row = 'Prefill, токенов/с & '+' & '.join(rates)+r' \\'
        self.assertIn(row,self.texts['02-workload.tex'])
        self.assertNotIn('173.6 & 93.7 & 49.9 & 41.2 & 27.7 & 22.2',self.texts['02-workload.tex'])
        source = (ROOT/'data/measurements/paper-v4-2026-11-03/FACTS.md').read_text()
        self.assertIn('Across all 18 cells, Δ-prefill rose 9-85% and decode 28-203%',source)
        self.assertIn('обычном приоритете',self.texts['02-workload.tex']);self.assertIn('PRI~31',self.texts['90-appendix.tex'])

    # Missing background/M5 priority labels, a production-residual claim and
    # a false completed Mac checkpoint each fail the actual named checker.
    def test_measurement_qualification_plants_are_detected(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for suffix in ('clients capacity','agents capacity','gains interim','economic capacity',
                       'free prefill capacity','traffic capacity','SWA background',
                       'M5 priority client table','M5 priority sweep table','residual limit',
                       'Mac checkpoint measured','Mac recheck uncalibrated','bounded undo future'):
            key='run16 '+suffix
            file,marker,phrase=self.off.expected()[key]
            pattern=r'\s+'.join(map(re.escape,phrase.split()))
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            plant,count=re.subn(pattern,'ОШИБОЧНАЯ КВАЛИФИКАЦИЯ',part,count=1)
            changed=self.texts[file].replace(part,plant,1)
            self.assertEqual(count,1,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:changed})))

    # The three observed residuals equal TTFT minus synchronous captures,
    # within the printed 0.1-second precision; they never become a fourth arm.
    def test_snapshot_residual_rows_follow_trace_derived_export(self):
        with (ROOT/'paper/data/engine/growing_5g_validation.csv').open() as stream:
            rows=[r for r in csv.DictReader(stream) if r['import_variant']=='prototype_depth']
        self.assertEqual([r['turn'] for r in rows],['0','7','31'])
        for r in rows:
            self.assertAlmostEqual(float(r['measured_ttft_s'])-float(r['instrumentation_capture_s']),float(r['measured_residual_s']),places=9)
            key='run16 instrumentation row '+r['turn']
            file,_,phrase=self.off.expected()[key]
            self.assertIn(phrase,self.texts[file])
            bad=self.texts[file].replace(phrase,phrase.replace(' & ',' & 9999',1),1)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # Equal scores do not prove 2pp equivalence. The retained paired-plan
    # reviewer sites now reject overclaims about the completed 8k experiment.
    def test_ruler_scores_text_changes_and_unestablished_equivalence(self):
        source=(ROOT/'data/measurements/paper-v4-2026-11-03/FACTS.md').read_text()
        self.assertIn('RULER score: 97.01% in all three arms',source)
        self.assertIn('Equivalence at the\n    declared 2 pp margin is not established at this n.',source)
        for n,d,printed in ((34,390,'8.72'),(32,390,'8.21')):
            self.assertEqual(f'{100*n/d:.2f}',printed)
        for key in ('rc3 review2 abstract paired plan','rc3 review2 limitations paired plan'):
            file,_,phrase=self.off.expected()[key]
            bad=self.texts[file].replace(phrase,'ЭКВИВАЛЕНТНОСТЬ ДОКАЗАНА',1)
            self.assertNotEqual(bad,self.texts[file])
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))
        for suffix in ('RULER score','RULER CUDA design','RULER text changes','RULER paired interval','RULER deeper pending'):
            key='run16 '+suffix;file,_,phrase=self.off.expected()[key]
            pattern=r'\s+'.join(map(re.escape,phrase.split()))
            bad,n=re.subn(pattern,'НЕВЕРНО',self.texts[file],count=1)
            self.assertEqual(n,1)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # Unguarded prose once retained old M5 gains, autopilot and GLM ingestion
    # numbers while their tables had changed. Each real stale value now fails.
    def test_m5_and_glm_prose_reject_stale_values(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for suffix,current,stale in (
            ('M5 gains prose','28--29','11--13'),
            ('M5 gains conclusion',r'на 29\%',r'на 11\%'),
            ('autopilot capacity',r'3\,020 вместо 1\,010',r'2\,460 вместо 820'),
            ('GLM cold local','42 минуты','57 минут'),
        ):
            key='run16 '+suffix
            file,marker,phrase=self.off.expected()[key]
            self.assertIn(current,phrase)
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed=part.replace(current,stale,1)
            self.assertNotEqual(changed,part)
            planted=self.texts[file].replace(part,changed,1)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:planted})))

    # Updated payback bars must fit the existing figure's explicit upper bound;
    # this is a numeric clipping check, not a visual-layout qualification.
    def test_payback_plot_does_not_clip_updated_months(self):
        text=self.texts['91-calculation-history.tex']
        ceiling=float(re.search(r'height=50mm, ymin=0, ymax=([0-9.]+)',text)[1])
        with (ROOT/'paper/data/payback.csv').open() as stream:
            months=[float(r[k]) for r in csv.DictReader(stream) for k in ('premium_months','whole_months')]
        self.assertGreaterEqual(ceiling,max(months))

    # New Russian prose rejects the mechanical forbidden forms. Semantic
    # pronoun antecedents and judgement-free measurements also need review.
    def test_v4_prose_has_no_forbidden_rhetorical_forms(self):
        for name in ('00-abstract.tex','01-introduction.tex','02-workload.tex','04-channel.tex',
                     '05-clients.tex','05b-models.tex','07-economics.tex','08-million.tex',
                     '11-limitations.tex','12-related.tex','14-conclusion.tex','90-appendix.tex'):
            text=re.sub(r'\\begin\{(?:tabular|tikzpicture)\}.*?\\end\{(?:tabular|tikzpicture)\}', '', self.texts[name], flags=re.S)
            self.assertNotRegex(text,r'[«»—–]|\s---?\s',name)
            self.assertNotRegex(text,r'\bне\s+[^.\n,]{1,80},\s+а\s|,\s+а\s+не\b',name)
