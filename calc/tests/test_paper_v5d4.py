"""Independent-review bounds: actual E2E timing, finite quality and archived arithmetic."""
import csv,gzip,hashlib,json,re,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d4-2026-11-05'

class PaperV5d4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d4_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # Named omission controls exercise the published bound, with an unchanged
    # positive control; this does not certify an unmeasured production session.
    def test_all_review_sites_reject_applied_named_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for row in json.loads((D/'sites.json').read_text()):
            key='v5d4 '+row['name'];f,marker,phrase=self.off.expected()[key]
            text=self.texts[f];part=next(p for p in text.split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key);self.assertNotEqual(changed,part)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:text.replace(part,changed,1)})))

    # Raw accepted receipts independently distinguish 40 turns, two offloads,
    # and aggregate catch-up from the fields on the two offload calls.
    def test_timing_receipts_do_not_promote_subtraction_or_catchup(self):
        r=json.loads(gzip.decompress((ROOT/'data/measurements/paper-v4c-2026-11-03/TIMING-EXTRACT.json.gz').read_bytes()))
        calls=[x for x in r['calls'] if x['arm']=='hybrid' and x['stage']!='start'];off=[x for x in calls if x['path']=='offload']
        self.assertEqual((len(calls),len(off)),(40,2))
        self.assertAlmostEqual(sum(x.get('catchup_seconds',0) or 0 for x in calls),134.8794721,places=5)
        self.assertEqual(sum(bool(x.get('catchup_seconds',0)) for x in calls),32)
        self.assertAlmostEqual(sum(x.get('catchup_seconds',0) or 0 for x in off),7.0877387,places=5)
        self.assertAlmostEqual(3646.4-425.6-455.2,2765.6)
        self.assertAlmostEqual((271.5-201.655)/271.5*100,25.7,places=1)
        self.assertIn('но ускорения не показала',self.texts['00-abstract.tex'])
        self.assertIn('ускорения длинной сессии',self.texts['14-conclusion.tex']);self.assertIn('опыт не показал',self.texts['14-conclusion.tex'])
        self.assertIn('без подготовки базы',self.texts['04-channel.tex'])
        self.assertIn('не является задержкой только двух оффлоадов',self.texts['04-channel.tex'])

    # Frozen run16 says 19.25 calls unserved, not19 percent; current24 has a
    # different M5 basis and must not inherit this archival percentage.
    def test_archived_19_calls_and_98_percent_use_same_row(self):
        with (ROOT/'calc/out/run16/base/perimeter_cost_medium.csv').open() as s:rows=list(csv.DictReader(s))
        candidates=[r for r in rows if any(abs(float(v)-.9759347180853518)<1e-10 for v in r.values() if re.fullmatch(r'\d*\.\d+',v or ''))]
        self.assertTrue(candidates)
        self.assertAlmostEqual((800-780.7478)/800*100,2.41,places=2)
        self.assertIn(r'19.2522/800=2.41\%',self.texts['91-calculation-history.tex'])
        self.assertNotIn(r'не отвечают на 19\%',self.texts['91-calculation-history.tex'])
        self.assertNotIn('2.6--2.7',self.texts['08-million.tex'])

    # Existing cost-floor arithmetic supports only the stated light-load case;
    # workload model-index classes are not measured task-completion rates.
    def test_free_prefill_and_workload_class_bounds_are_finite(self):
        self.assertGreater(2.52+5,3.604082737*840/1000)
        self.assertLess(2.52+5,3.604082737*10500/1000)
        r=json.loads((ROOT/'paper/data/year-bill-summary.json').read_text())
        self.assertAlmostEqual((r['by_class']['at_or_below']['calls']+r['by_class']['effort']['calls'])/r['calls']*100,17.0,places=1)
        t=self.texts['07-economics.tex'];self.assertIn('вывод ограничен указанной лёгкой нагрузкой',t)
        self.assertIn('Классификация по индексу не измеряет',t)
        # The shorter analyst abstract leaves cost per completed work in the body.
        for f in ('07-economics.tex','01-introduction.tex','11-limitations.tex','14-conclusion.tex'):
            self.assertIn('цена вызова не является ценой',self.texts[f].lower())

    # Contribution text acknowledges known phase disaggregation and leaves
    # reference-state auditing outside the production path.
    def test_predecessors_and_future_audit_are_explicit(self):
        for f in ('01-introduction.tex','12-related.tex','14-conclusion.tex'):
            self.assertRegex(self.texts[f],r'\\cite\{[^}]*exolabsSpark');self.assertRegex(self.texts[f],r'\\cite\{[^}]*li2026ppd')
        related=self.texts['12-related.tex'];self.assertIn('2.8 раза',related);self.assertIn('4x в заголовке',related)
        self.assertIn('Дата страницы не указана',related);self.assertIn('v1 от 2026-03-09',related)
        self.assertIn('не входит в производственный маршрут',self.texts['13-outlook.tex'])
        self.assertIn('в производственном режиме сверки состояния с эталоном нет',self.texts['01-introduction.tex'])
        for f,t in self.texts.items():
            if int(f[:2])<90:self.assertNotRegex(t,r'PRI\s*~?\s*(?:4|31)\b')

    # Relocation is an exact finite ledger, not an anywhere-in-paper fallback;
    # older evidence snapshots and all prior test names have separate custody.
    def test_evidence_and_explicit_loci_are_bound(self):
        for name,row in json.loads((D/'relocations.json').read_text()).items():
            self.assertIn(name,self.off.expected());self.assertIn(row['to'],('90-appendix.tex','91-calculation-history.tex',row['from']))
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
