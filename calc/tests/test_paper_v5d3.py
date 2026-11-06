"""RC4 accepted API-only successor: cadence/cohort boundaries, no new performance claim."""
from test_paper_v5a2 import current_changelog
import csv,hashlib,json,re,subprocess,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d3-2026-11-05'
ENGINE='ca7f228acd789380bf46016fd87acc33e1b07aef'

import history_evidence as history

def rows(name):
    with (ROOT/'calc/out/run24/paper'/name).open() as stream:return list(csv.DictReader(stream))
def select(data,**wanted):
    found=[r for r in data if all(r[k]==str(v) for k,v in wanted.items())]
    assert len(found)==1,(wanted,len(found))
    return found[0]

class PaperV5d3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d3_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
        cls.sites={'v5d3 '+r['name']:r for r in json.loads((ROOT/'data/measurements/paper-v5d4-2026-11-05/v5d3-sites-current.json').read_text())}
        # Analyst successors move only the named current publication locus.
        for k,r in cls.sites.items():
            r.update(zip(('file','marker','phrase'),cls.off.expected()[k]))

    # Every new text/row has an actually applied omission and clean control;
    # checks bind publication transcription, not unseen providers or hardware.
    def test_new_sites_have_named_applied_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for k,r in self.sites.items():
            text=self.texts[r['file']];part=next(p for p in text.split('\n\n') if r['marker'] in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,r['phrase'].split())),lambda _:'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,k);self.assertNotEqual(bad,part,k)
            self.assertIn(k,self.off.missing(dict(self.texts,**{r['file']:text.replace(part,bad,1)})))

    # All12 side/measured rows use their own accepted cadence/cohort, retaining
    # unknown core prices instead of a v1 fallback or invented zero.
    def test_three_points_use_exact_cadence_and_partial_priceable_cohort(self):
        t=self.texts['07-economics.tex'];data=rows('api_rankings.csv')
        for model,label in [('qwen/qwen3.8-27b','Qwen'),('z-ai/glm-5.3-flash','GLM')]:
            for cadence,short in [('v1_long_pause','v1'),('amendment_core','короткий')]:
                for point,cache in [('no_cache',r'0\%'),('owner_981',r'98.1\%'),('measured','измеренный')]:
                    args=dict(model=model,profile='existing_combined',scope_tier='measured_ladder',cadence=cadence,cache_point=point)
                    lo=select(data,**args,role='cheapest');me=select(data,**args,role='median')
                    price=lambda r:f"{float(r['usd_per_1000_calls']):.3f}" if r['usd_per_1000_calls'] else 'неизвестно'
                    line=f"{label}, {short} & {cache} & {price(lo)} & {price(me)} & {lo['cohort_size']}/{lo['admitted_count']}"
                    self.assertIn(line,t)
        self.assertIn('частичные наборы оценимых цен',t);self.assertIn('перенос доли между глубинами есть допущение',t)
        self.assertIn('без глобального утверждения о самом дешёвом API',t)
        core=select(data,model='qwen/qwen3.8-27b',profile='existing_combined',scope_tier='measured_ladder',cadence='amendment_core',cache_point='measured',role='cheapest')
        self.assertEqual(core['cohort_size'],'0');self.assertEqual(core['usd_per_1000_calls'],'')

    # A single warm minimum is descriptive. Source-native depth-mix prices
    # and unmeasured GLM hybrid performance must not become Qwen profile claims.
    def test_thin_minimum_and_reference_model_limits_are_explicit(self):
        t=self.texts['07-economics.tex'];r=select(rows('api_rankings.csv'),model='qwen/qwen3.8-27b',profile='existing_combined',scope_tier='measured_ladder',cadence='v1_long_pause',cache_point='measured',role='cheapest')
        self.assertEqual(r['provider'],'ionstream/fp8');self.assertEqual(r['warm_calls'],'1')
        self.assertAlmostEqual(float(r['usd_per_1000_calls']),3.604,places=3)
        self.assertIn('одно тёплое наблюдение и остаётся описательным',t)
        self.assertIn('GLM здесь служит ценовым ориентиром API',t)
        self.assertIn('измерение гибридного исполнения GLM не заявляется',t)
        self.assertIn('разность пересечений не выделяет причинный эффект одного кэша',t)
        self.assertIn('пересечение не определено',t)

    # Crossings are dedicated, ownedM5, bf16,s20%, PRO6000, measured Qwenv1;
    # no light/medium/cheapest crossing and local-only Claude scope are retained.
    def test_measured_crossings_match_primary_rows_and_local_only_claude(self):
        data=rows('measured_crossings.csv');common=dict(scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8',cadence='v1_long_pause',cache_point='measured')
        for profile,billing,load,role,want in [('existing_combined','bought','heavy','median','5'),('existing_combined','bought','light','median',''),('existing_combined','bought','medium','median',''),('existing_combined','rented','heavy','median','443'),('claude_deep','rented','heavy','median','60'),('claude_deep','bought','heavy','median','5')]:
            r=select(data,**common,profile=profile,billing=billing,load=load,api_role=role);self.assertEqual(r['from_people'],want)
            if profile=='claude_deep':self.assertEqual(float(r['offload_share_max']),0)
        for load in ('light','medium','heavy'):
            self.assertEqual(select(data,**common,profile='existing_combined',billing='bought',load=load,api_role='cheapest')['from_people'],'')
        t=self.texts['07-economics.tex']
        for phrase in ('с 443 человек в объединённом профиле и с 60 в профиле Claude','контроль снимка при условных 98.1'+r'\% давал 30','Профиль Claude не выполняет оффлоад','контроль снимка при условных 98.1'+r'\% давал 45'):
            self.assertIn(phrase,t)
        for f in ('01-introduction.tex','14-conclusion.tex'):
            self.assertIn('при измеренном v1 с долгими паузами',self.texts[f]);self.assertIn('с 5 человек',self.texts[f]);self.assertIn('Самый дешёвый допущенный API дешевле гибрида во всех оценимых измеренных точках Qwen' if f=='01-introduction.tex' else 'самый дешёвый допущенный API ни в одной оценимой измеренной точке Qwen не дороже гибрида',self.texts[f])

    # Every attempted under95 variant in independent analysis is named and
    # excluded; a high hit fraction cannot override whole-window availability.
    def test_all_ten_attempted_under95_variants_remain_excluded(self):
        a=json.loads((ROOT/'calc/run24/data/analysis.json').read_text());bad=[r for r in a['providers'] if r.get('whole_window_availability',{}).get('attempts',0)>0 and r['whole_window_availability']['rate']<.95]
        self.assertEqual(len(bad),10);t=self.texts['07-economics.tex']
        self.assertIn('Всего 10 опробованных вариантов ниже 95'+r'\% за всё окно исключены',t)
        for r in bad:
            model,provider=r['provider'].split(' / ');label='Qwen' if model.startswith('qwen/') else 'GLM';line=label+' & '+provider+f" & {r['whole_window_availability']['rate']:.3f}"
            self.assertIn(line,t);self.assertEqual(r['eligibility'],'excluded-availability')
        self.assertIn('Для поставщиков без попыток сохранён явно обозначенный суточный снимок',t)
        self.assertIn('его тарифы не служат заменой измерений',t)

    # Measured1M Qwen has no admitted provider, irrespective of a cheap
    # excluded observed quote. The GLM pooled mean is a different source mix.
    def test_million_and_rc4_status_keep_real_pending_items(self):
        data=rows('million_measured.csv')
        for variant in ('with_alibaba','without_alibaba'):
            q=select(data,model='qwen/qwen3.8-27b',variant=variant);g=select(data,model='z-ai/glm-5.3-flash',variant=variant)
            self.assertEqual(q['qualified_providers'],'0');self.assertEqual(q['usd_per_1000_calls'],'')
            self.assertEqual(g['qualified_providers'],'15');self.assertAlmostEqual(float(g['usd_per_1000_calls']),60.354821,places=6)
        self.assertIn('ожидает допущенного поставщика',self.texts['08-million.tex'])
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        current='\n'.join(t for f,t in self.texts.items() if not f.startswith('91-'))
        self.assertNotIn('ожидает прогона 24',current);self.assertNotIn('ожидает пересчёта движка',current)
        log=current_changelog((ROOT/'CHANGELOG.md').read_text())
        for phrase in ('2026-11-05 12:00Z','RULER 128k and full Holm analysis are now complete','B300 decode','admitted measured Qwen 1M','hybrid-inference-data','snapshot follows RC 4'):self.assertIn(phrase,log)
        self.assertIn('RULER 64k completed on its original node at 14:28Z',log)
        self.assertNotIn('Pending: RULER 64k',log)

    # New abstract economics retains both the labelled historical control and
    # the measured v1 condition, within publication budgets in both languages.
    def test_abstracts_keep_measured_cadence_and_conditional_economics(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        for phrase in ('выделенном офисном PRO 6000','Наборы цен неполны','перенос долей кэша на профиль есть допущение'):self.assertIn(phrase,ru)
        for f in ('01-introduction.tex','14-conclusion.tex'):
            self.assertIn('45 человек' if f=='14-conclusion.tex' else 'с 45',self.texts[f]);self.assertIn('при измеренном v1 с долгими паузами',self.texts[f])
        self.assertIn('cohorts are partial',en);self.assertIn('transferring cache fractions to the workload is an assumption',en)
        self.assertIn('Гибрид не дешевле самого дешёвого допущенного API ни в одной оценимой измеренной точке Qwen',ru)

    # Exact accepted source/output bytes and inherited hardware are checked
    # independently of refreshed paper wording pins. Earlier archives stay frozen.
    def test_accepted_engine24_and_source_custody_are_exact(self):
        self.assertEqual(history.unchanged(ENGINE,*history.snapshot_paths(ENGINE,'calc/out'),'calc/run24','calc/run23','calc/hybridcalc','calc/tests/test_run24.py','calc/tests/test_r24_report.py','calc/r24_report.py',allow_ports=True),'')
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
        r=json.loads((D/'source-receipt.json').read_text());self.assertEqual(r['engine'],ENGINE)
        self.assertEqual(r['analysis_sha256'],hashlib.sha256((ROOT/'calc/run24/data/analysis.json').read_bytes()).hexdigest())
