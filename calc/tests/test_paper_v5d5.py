"""Analyst abstracts and cost-per-work boundaries, from accepted immutable sources."""
import csv,hashlib,json,re,subprocess,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d5-2026-11-05'

import history_evidence as history

def rows(path):
    with (ROOT/path).open() as s:return list(csv.DictReader(s))

def select(data,**kw):
    found=[r for r in data if all(r.get(k)==str(v) for k,v in kw.items())]
    assert len(found)==1,(kw,len(found))
    return found[0]

class PaperV5d5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d5_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
        cls.english=(ROOT/'paper/abstract.en.txt').read_text().strip()

    # Omission must reject the intended finite site, with clean prose as a
    # positive control. These checks do not measure unseen tasks or providers.
    def test_new_sites_have_applied_named_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for r in json.loads((D/'sites.json').read_text()):
            key='v5d5 '+r['name'];f,m,w=self.off.expected()[key];text=self.texts[f]
            part=next(p for p in text.split('\n\n') if m in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key);self.assertNotEqual(changed,part)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:text.replace(part,changed,1)})))

    # The source model-index classes independently reproduce calls and bills.
    # Paired scenario endpoints, not cross-mixed extrema, give4.6-4.8 percent.
    def test_model_class_arithmetic_and_frontier_reference_are_exact(self):
        r=json.loads((ROOT/'paper/data/year-bill-summary.json').read_text());a=r['by_class']['at_or_below'];e=r['by_class']['effort'];f=r['by_class']['above']
        self.assertEqual(a['calls']+e['calls'],260201);self.assertEqual(r['calls'],1530739)
        self.assertEqual(f"{100*(a['calls']+e['calls'])/r['calls']:.1f}",'17.0')
        self.assertEqual(f"{a['low']+e['low']:.2f}",'5429.87');self.assertEqual(f"{a['high']+e['high']:.2f}",'5732.85')
        self.assertEqual(f"{100*(a['low']+e['low'])/r['low']:.1f}",'4.8');self.assertEqual(f"{100*(a['high']+e['high'])/r['high']:.1f}",'4.6')
        self.assertEqual(f"{100*f['calls']/r['calls']:.1f}",'81.5')
        for key,want in [('low','106836.72'),('high','118452.94'),('qwen_low','15061.07'),('qwen_high','24456.49')]:self.assertEqual(f'{f[key]:.2f}',want);self.assertIn(want,self.texts['07-economics.tex'])
        self.assertIn('способность Qwen решать эти задачи в работе не проверена.',self.texts['07-economics.tex'])
        self.assertIn('не зависит от серверного движка и допуска API',self.texts['07-economics.tex'])
        self.assertIn('Цена вызова не является ценой выполненной работы',self.texts['07-economics.tex'])

    # Dedicated ownedM5/bf16/s20% crossings use the accepted native rows.
    # The measured median point has long pauses; absent cheapest is not zero.
    def test_abstract_crossings_keep_exact_basis_cadence_and_cheapest_bound(self):
        common=dict(profile='existing_combined',scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8',billing='bought')
        for load,want in [('medium','5'),('heavy','2')]:self.assertEqual(select(rows('calc/out/run23/paper/team_break_even.csv'),**common,load=load,reference='own_cluster')['from_people'],want)
        data=rows('calc/out/run24/paper/measured_crossings.csv');point=dict(common,cadence='v1_long_pause',cache_point='measured')
        self.assertEqual(select(data,**point,load='heavy',api_role='median')['from_people'],'5')
        for load in ('light','medium','heavy'):self.assertEqual(select(data,**point,load=load,api_role='cheapest')['from_people'],'')
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=self.english
        # Engine26 now prices the full share; native20% controls above remain intact.
        for phrase in ('имеющемся M5 Max','выделенном офисном PRO 6000','доле Qwen 100%','с 4 человек','не дешевле самого дешёвого допущенного API','Наборы цен неполны'):self.assertIn(phrase,ru)
        for phrase in ('owned M5 Max','dedicated office PRO 6000','100% Qwen scenario','from 4 people','never costs less than the cheapest admitted API','Price cohorts are partial'):self.assertIn(phrase,en)
        self.assertIn('одинакова и сокращается',self.texts['07-economics.tex'])

    # Completed score bounds cover8k/32k/64k;128k is withheld despite a passing
    # registered interval. Post-result margin/text limitations remain explicit.
    def test_bilingual_ruler_and_bf16_claims_are_bounded(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=self.english
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        self.assertIn('на 8, 32 и 64 тысячах',ru);self.assertIn('на 128 тысячах эквивалентность не установлена',ru);self.assertIn('at 8k/32k',en)
        self.assertIn('граница выбрана после результатов',ru);self.assertIn('margin chosen after 8k/32k',en)
        self.assertLessEqual(len('граница выбрана после результатов'.split()),8)
        self.assertNotRegex(ru,r'на 8.{0,5}128 тысяч');self.assertNotIn('at 8k/128k',en)
        self.assertIn('bf16 округляет',ru);self.assertIn('bf16 rounds and halves',en)
        self.assertIn('эффекта на KL',ru);self.assertIn('no measurable KL effect',en)
        self.assertNotIn('без потерь',ru);self.assertNotIn('lossless',en)
        self.assertEqual(156893184,2*78446592)
        self.assertIn('Получены 390/390 пар',self.texts['11-limitations.tex']);self.assertIn('95.90',ru)
        self.assertIn('Эквивалентность текста при 2 п.п. не установлена',self.texts['11-limitations.tex'])

    # Every numerical abstract statement has a retained body condition. The
    #26-percent result is one fresh call, not the instrumented long session.
    def test_removed_lab_details_remain_in_body_and_first_call_is_finite(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=self.english
        self.assertEqual(round(10000/44.4),225);self.assertIn('225 секунд',ru);self.assertIn('225 s',en)
        self.assertIn('20 документах',ru);self.assertIn('20 documents',en)
        self.assertIn('из 40 ходов',ru);self.assertIn('выполнено 2 хода',ru);self.assertIn('но ускорения не показала',ru)
        self.assertIn('40-turn',en);self.assertIn('only 2 turns ran remotely',en);self.assertIn('showed no speedup',en)
        self.assertEqual(round(100*(271.5-201.655)/271.5),26)
        for phrase in (r'39\,504',r'16.0~МБ/с',r'110~мс','фоновый приоритет'):self.assertIn(phrase,self.texts['04-channel.tex'])
        body=self.texts['11-limitations.tex']
        for value in ('7.905','-0.000298','-0.001076','+0.000390','bootstrap вырожден','после получения результатов Qwen на 8 и 32 тысячах'):self.assertIn(value,body)
        self.assertIn('10.1--10.8',self.texts['06-server.tex']);self.assertIn('PRI~31',self.texts['90-appendix.tex'])
        for removed in ('7.905','10.1','-0.000298','PRI','RTT'):self.assertNotIn(removed,ru);self.assertNotIn(removed,en)

    # Current successors require exact tuples; immutable older evidence and
    #native engine/code/output authority remain separate from refreshed pins.
    def test_source_custody_successors_and_pending_inventory(self):
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.name!='README.md' and p.is_file():self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
        latest=json.loads((ROOT/'data/measurements/paper-v5d6-2026-11-05/successors.json').read_text())
        for k,r in json.loads((D/'abstract-successors.json').read_text()).items():
            if k in latest:self.assertEqual(latest[k]['from'],r['to'])
            self.assertEqual(list(self.off.expected()[k]),list(self.off._publication_locus({k:tuple(latest[k]['to']if k in latest else r['to'])})[k]))
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        self.assertEqual(history.unchanged('ad21d3b2727f9de1392ca001e530201b69f431ce',*history.snapshot_paths('ad21d3b2727f9de1392ca001e530201b69f431ce','calc/out'),'calc/hybridcalc','calc/run24','data/measurements/paper-v5d4-2026-11-05','paper/data/year-bill-summary.json','paper/data/year_bill.py','paper/data/owner-model-usage-2026-10-30.json',allow_ports=True),'')
