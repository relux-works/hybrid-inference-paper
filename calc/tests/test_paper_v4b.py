"""Owner r20b: finite review regressions, independently sourced arithmetic."""
import csv
import json
import math
import re
import statistics
import unittest
from unittest.mock import patch
from r13_audit import ROOT, module


class PaperV4bTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('paper_v4b_guard',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # The current budget admits1920 and rejects1921 while every
    # existing scientific contract remains present; short text is a positive control.
    def test_abstract_arxiv_boundary_rejects_1921(self):
        self.assertEqual(self.off.missing(self.texts),[])
        source=self.texts['00-abstract.tex']
        self.assertLessEqual(len(self.off.abstract_text(source)),1920)
        for limit,want in ((1920,[]),(1921,['v4b abstract arXiv length'])):
            n=limit-len(self.off.abstract_text(source))-1
            changed=source.replace(r'\end{quote}','x'*n+'\n'+r'\end{quote}')
            self.assertEqual(len(self.off.abstract_text(changed)),limit)
            self.assertEqual(self.off.missing(dict(self.texts,**{'00-abstract.tex':changed})),want)

    # Each team amount is bound to selected, eligible rows of the named
    # already-owned client in both light-load policies, not to an arbitrary fleet.
    def test_light_teams_reject_stale_amounts_and_wrong_directions(self):
        expected=self.off.v4b_expected()
        for team in (5,10,20,50,500,5000):
            key='v4b light team '+str(team);file,marker,phrase=expected[key]
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            pattern=r'\s+'.join(map(re.escape,phrase.split()))
            changed,n=re.subn(pattern,'НЕВЕРНАЯ ЦЕНА',part,count=1)
            self.assertEqual(n,1,key)
            bad=dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})
            self.assertIn(key,self.off.missing(bad))
        original=self.off.rows
        # A duplicated selected row and an actual sign inversion must raise
        # their precise source-contract assertion, independently of prose checking.
        clean=original(self.off.ENGINE/'perimeter_cost_light.csv')
        for team in (5,10,20,50,500,5000):
            row=next(r for r in clean if r['team']==str(team) and r['route']=='hybrid' and r['selected']=='1' and r['client']=='M5 Max 64 GB' and r['basis']=='Mac already owned')
            own=next(float(r['person_month']) for r in clean if r['team']==str(team) and r['route']=='all server' and r['selected']=='1')
            for kind,data,error in (
                ('duplicate',clean+[dict(row)],'light-load selected row'),
                ('direction',[dict(r,person_month=str(own*(.5 if team<50 else 2))) if r is row else r for r in clean],
                 'small-team light direction' if team<50 else 'large-team light direction'),
            ):
                with self.subTest(team=team,plant=kind):
                    with patch.object(self.off,'rows',lambda path:data if path.name=='perimeter_cost_light.csv' else original(path)):
                        with self.assertRaisesRegex(AssertionError,error):self.off.v4b_expected()
        self.assertEqual(self.off.missing(self.texts),[])

    # Removed time/geometry/link/novelty qualifiers and a false recorded M5
    # priority are rejected by the actual named publication checker.
    def test_review_qualifiers_and_geometry_reject_omissions(self):
        expected=self.off.expected()
        for key in [k for k in expected if k.startswith('v4b ')] + ['run16 M5 priority client table','run16 M5 priority sweep table']:
            file,marker,phrase=expected[key]
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),'ОШИБОЧНЫЙ ВЫВОД',part,count=1)
            self.assertEqual(n,1,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))
        self.assertEqual(1024*435200,445644800)
        self.assertGreater(445644800,156900000)
        self.assertAlmostEqual(201.655-10.643-123.219-42.423,25.370)

    # All current pending sites match FACTS5; adding measured RULER8k as
    # pending or deleting a registered wait fails the inventory contract.
    def test_pending_inventory_rejects_measured_or_unregistered_waits(self):
        source=(ROOT/'data/measurements/paper-v4b-2026-11-03/FACTS.md').read_text().split('## 5. Pending:',1)[1].split('## 6.',1)[0]
        for fact in ('Paired RULER at 32k','checkpoint-10','full parallel curve','Glimmer 30B and Gemma 4','Engine run 16b','BF16 reference','vLLM state bridge','Bonsai 2 ladder'):
            self.assertIn(fact,source)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        for file,text in self.texts.items():
            for match in re.finditer(r'\\pending\{([^{}]*)\}',text,re.S):
                bad=dict(self.texts,**{file:text[:match.start()]+text[match.end():]})
                self.assertEqual(self.off.pending_gaps(bad),['v4b pending inventory'])
        for body in ('RULER 8 тысяч','время 40 ходов через 5G','исследование KL'):
            bad=dict(self.texts,**{'90-appendix.tex':self.texts['90-appendix.tex']+'\n\\pending{'+body+'}\n'})
            self.assertEqual(self.off.pending_gaps(bad),['v4b pending inventory'])

    # Recompute restored mean, median and p90 from all R16 normalized calls,
    # including zero-input calls. Dropping zeros is an intentional negative control.
    def test_restored_prefill_distribution_uses_all_calls(self):
        from hybridcalc.engine import load
        from hybridcalc.paper_tables import Context
        scenario,inputs=load('paper-tables-r16');context=Context(scenario,inputs)
        model=context.model('qwen27')
        rate=context.g.resolve(context.local_rate('m3max',model)).value
        calls=context.g.resolve(context.valid).value
        waits=sorted(n/rate(d) for d,n,o,t in calls)
        derived=json.loads((ROOT/'data/measurements/paper-v4b-2026-11-03/derived-prefill.json').read_text())
        self.assertEqual(len(waits),derived['calls'])
        self.assertAlmostEqual(statistics.mean(waits),derived['mean'],places=10)
        self.assertAlmostEqual(statistics.median(waits),derived['median'],places=10)
        self.assertAlmostEqual(waits[math.ceil(.9*len(waits))-1],derived['p90'],places=10)
        self.assertNotAlmostEqual(statistics.mean(x for x in waits if x>0),derived['mean'],places=1)

    # A legacy pending-site plant now violates two real contracts. Both named
    # diagnostics must remain; the CLI self-test must not suppress either.
    def test_pending_regression_keeps_both_named_diagnostics(self):
        key='run15 growing calibration pending';file,marker,phrase=self.off.expected()[key]
        part=next(p for p in self.texts[file].split('\n\n') if marker in p)
        pattern=r'\s+'.join(map(re.escape,phrase.split()))
        changed,n=re.subn(pattern,lambda m:m[0].replace('M3','M4',1),part,count=1)
        self.assertEqual(n,1)
        self.assertNotEqual(changed,part)
        bad=dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})
        self.assertEqual(self.off.missing(bad),['v4b pending inventory',key])
        self.assertEqual(self.off.missing(self.texts),[])
