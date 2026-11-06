"""RC4 review corrections: finite published claims, accepted inputs and named negatives."""
import csv,hashlib,json,re,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d6-2026-11-05'

class PaperV5d6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d6_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text()for p in cls.off.SECTIONS.glob('*.tex')}

    # Each finite successor must reject one applied omission at its declared locus.
    # This is a transcription guard, not a rerun of hardware/provider measurements.
    def test_all_declared_successors_reject_named_omissions(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for key,row in json.loads((D/'successors.json').read_text()).items():
            f,m,w=self.off.expected()[key];self.assertEqual([f,m,w],list(self.off._publication_locus({key:tuple(row['to'])})[key]))
            text=self.texts[f];part=next(p for p in text.split('\n\n')if m in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key);self.assertNotEqual(bad,part,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:text.replace(part,bad,1)})),key)

    # New result boundaries must reject omissions independently of byte pins.
    def test_new_review_boundaries_reject_each_named_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for row in json.loads((D/'sites.json').read_text()):
            key='v5d6 '+row['name'];f,m,w=self.off.expected()[key]
            text=self.texts[f];part=next(p for p in text.split('\n\n')if m in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:text.replace(part,bad,1)})),key)

    # Fixed identical11-provider cohorts reverse the apparent median inversion.
    # Native ranked output and source arithmetic independently fix the result.
    def test_like_for_like_cohort_explains_median_inversion(self):
        source=ROOT/'calc/out/run24/api_prices.csv';r=json.loads((D/'arithmetic.json').read_text())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),r['source_sha256'])
        with source.open()as s:rows=list(csv.DictReader(s))
        g=[x for x in rows if all(x[k]==v for k,v in dict(model='qwen/qwen3.8-27b',profile='existing_combined',scope_tier='measured_ladder',cadence='v1_long_pause',admitted='True').items())]
        cohorts={p:{x['provider']:float(x['effective_usd_per_1000_calls'])for x in g if x['cache_point']==p and x['effective_usd_per_1000_calls']}for p in ('no_cache','measured')}
        self.assertEqual((len(cohorts['no_cache']),len(cohorts['measured'])),(15,11))
        same={k:v for k,v in cohorts['no_cache'].items()if k in cohorts['measured']}
        self.assertAlmostEqual(sorted(cohorts['no_cache'].values())[7],8.68082670435457)
        self.assertAlmostEqual(sorted(same.values())[5],19.711326477535152)
        self.assertAlmostEqual(sorted(cohorts['measured'].values())[5],12.549870329346795)
        self.assertTrue(all(cohorts['measured'][k]<=same[k]+1e-10 for k in same))
        t=self.texts['07-economics.tex']
        for w in ('11 оценимых поставщиков, второй 15','19.71','12.55','одно тёплое наблюдение','8.1~с и p90 60.6~с','сравнение смещено в пользу гибрида'):self.assertIn(w,t)

    # Peak bandwidth is an estimate, using weights+per-tokenKV+f32 state.
    # It does not diagnose the cause of measured slowdown or claim delta TTFT.
    def test_bandwidth_limit_and_interactive_boundary_are_recomputed(self):
        r=json.loads((D/'arithmetic.json').read_text())['bandwidth'];kv=34816*1040000
        ceiling=400e9/(18973870432+kv+156893184)
        self.assertEqual(json.loads((ROOT/'data/measurements/ivmbp-2026-10-30/qwen27b-bench/normalized-results.json').read_text())['model_bytes'],18973870432)
        self.assertEqual(kv,36208640000);self.assertAlmostEqual(ceiling,7.228122709642542)
        self.assertAlmostEqual(ceiling/1.6638,4.344345900656647)
        self.assertAlmostEqual(512/1.6638,307.72929438634454)
        self.assertEqual(r['kv_bytes'],kv);self.assertEqual(r['ceiling_tok_s'],ceiling)
        for x in ('1.66','5.13','4.34','7.23','0.875','0.452','0.846','421.54','768','61.97','56.62'):self.assertIn(x,self.texts['08-million.tex'])
        self.assertIn('Фоновый приоритет не объясняет',self.texts['08-million.tex'])
        self.assertIn('слишком медленна для интерактивного агента',self.texts['08-million.tex'])
        self.assertIn('36208640000',self.texts['91-calculation-history.tex'])

    # The first refusal remains visible, and raising a bound is not calibration.
    # A planted passed-after-raising assertion must fail this named boundary.
    def test_mac_bound_history_never_becomes_calibrated_acceptance(self):
        t=self.texts['08-million.tex']
        self.assertIn('1.08298',t);self.assertIn('превысил границу 1.0',t)
        self.assertIn('После отказа границу подняли до 4.0',t)
        self.assertIn('Граница 4.0 не калибрована',t)
        self.assertNotRegex(t,r'повтор (?:с 4\.0 )?прош[её]л')
        self.assertIn('два локальных запуска с разной разбивкой',t)
        self.assertIn('0.00032912',t);self.assertIn('3.01402',t)

    # Both deep depths are complete, distinct from archived serial prefixes.
    # Host changes preserve within-example pairing;128k claim remains withheld.
    def test_complete64k_and_host_changed128k_keep_distinct_verdicts(self):
        t=self.texts['11-limitations.tex'];q=t.split(r'\section{Ограничения}')[0]
        for x in ('390/390 пар','97.18','0.5716','[-5.51,+3.49]','21 пример к 369','Проверка всего манифеста','узла B на узел A','внутри примера','на 128 тысячах не установлена'):self.assertIn(x,q)
        self.assertNotIn('Сохранено пар из 390 & 368',q)
        self.assertIn('Пар из 390 & 390 & 390',q)
        self.assertIn('сбор 128 тысяч пересёк регистрацию',q.lower());self.assertIn('не является подтверждающим',q)
        self.assertIn('включён по решению владельца',q)

    # Closed-perimeter thresholds at20% must not be promoted to100%. Both
    # abstracts remove the measured-v1 median promise, while body keeps cadence.
    def test_closed_contour_and_cache_gains_remain_conditional(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        self.assertIn('доле Qwen 100%',ru);self.assertIn('100% Qwen scenario',en)
        self.assertIn('с 4 человек',ru);self.assertIn('from 4 people',en)
        self.assertIn('не дешевле самого дешёвого допущенного API',ru);self.assertIn('never costs less than the cheapest admitted API',en)
        intro=self.texts['01-introduction.tex']
        for w in ('остальные 80','внутренняя большая модель обслуживает остальные 80','27.28','это доли восстановленного профиля','0.00','8.1','60.6'):self.assertIn(w,intro)
        for f,t in self.texts.items():
            if int(f[:2])<90:self.assertNotRegex(t,r'нагрузк[аиуы].{0,25}типичн')
        self.assertEqual(self.off.pending_gaps(self.texts),[])

    # The seven removed appendix bodies remain byte-equal to their sole current
    # main-text copies; unique caption methods stay as appendix prose.
    def test_duplicate_tables_are_removed_without_losing_measurements(self):
        bodies=lambda s:[' '.join(m[0].split())for m in re.finditer(r'\\begin\{tabular\}.*?\\end\{tabular\}',s,re.S)]
        archived=bodies((D/'duplicate-tables-before.tex').read_text());self.assertEqual(len(archived),7)
        main=[b for f,t in self.texts.items()if int(f[:2])<90 for b in bodies(t)]
        appendix=bodies(self.texts['90-appendix.tex'])
        for b in archived:self.assertEqual(main.count(b),1);self.assertNotIn(b,appendix)
        self.assertEqual(len(main+appendix),len(set(main+appendix)))

    # Published preregistration is a future paired replay, not completed Metal
    # timing or task-quality evidence. Swarm reference follows actual E2E result.
    def test_preregistration_and_readability_preserve_end_to_end_boundary(self):
        t=self.texts['11-limitations.tex'];self.assertIn('не устанавливают полное время пути до Metal',t)
        self.assertIn('опыт запланирован, но ещё не проведён',t)
        self.assertIn('c2df294e',self.texts['13-outlook.tex'])
        self.assertIn('does not measure agent task success',(D/'PREREG-E2E.md').read_text())
        c=self.texts['14-conclusion.tex'];self.assertGreater(c.index('Swarm Inference'),c.index('ускорения длинной сессии этот опыт не показал'))
        self.assertNotIn('3.604082737',self.texts['07-economics.tex']);self.assertNotIn('426606592',self.texts['01-introduction.tex'])
        self.assertNotIn('аренда не запустила контейнер',self.texts['01-introduction.tex'])

    # The publication receipt must count the complete numeric registry, not
    # the four architecture chart rows checked later in the same function.
    def test_publication_receipt_counts_all_registered_numbers(self):
        import publication_v2
        summary=publication_v2.check_publication()
        self.assertEqual(summary['scanned_numbers'],len(publication_v2.records()))
        self.assertGreater(summary['scanned_numbers'],1000)

    # An applied overlapping plant must require both diagnostics. Removing a
    # co-affected predicate or adding an unrelated one must fail the same gate.
    def test_coupled_controls_reject_missing_and_extra_diagnostics(self):
        coupled=json.loads((ROOT/'data/measurements/paper-v5d11-2026-11-06/self-test-couplings.json').read_text())
        name=next(iter(coupled));f,m,w=self.off.expected()[name]
        digit=re.search(r'\d',w)
        bad=w[:digit.start()]+str((int(digit[0])+1)%10)+w[digit.end():]if digit else'ПОДМЕНА '+w.split(maxsplit=1)[-1]
        text=self.texts[f];part=next(p for p in text.split('\n\n')if m in p)
        changed,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:bad,part,count=1);self.assertEqual(n,1)
        planted=text.replace(part,changed,1)
        actual=self.off.missing(dict(self.texts,**{f:planted}))
        pending=lambda s:re.findall(r'\\pending\{([^{}]*)\}',s,re.S)
        wanted=(['v4b pending inventory']if pending(text)!=pending(planted)else[])+coupled[name]['diagnostics']
        self.off.assert_control_diagnostics(name,actual,wanted)
        missing=[x for x in wanted if x!=next(x for x in wanted if x!=name and x!='v4b pending inventory')]
        with self.assertRaisesRegex(AssertionError,re.escape(name)):
            self.off.assert_control_diagnostics(name,actual,missing)
        with self.assertRaisesRegex(AssertionError,re.escape(name)):
            self.off.assert_control_diagnostics(name,actual,wanted+['UNRELATED'])

    # Every new documentary input has a recorded content hash; immutable old
    # fixtures and engine sources are checked by existing custody gates.
    def test_new_evidence_has_explicit_custody(self):
        import gzip
        for row in json.loads((D/'compressed-custody.json').read_text()):
            raw=gzip.decompress((D/row['compressed']).read_bytes())
            self.assertEqual(len(raw),row['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['original_sha256'])
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
