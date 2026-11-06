"""RC4 remaining measurements: finite FACTS-bound results, accepted engine24 pricing with immutable earlier measurements."""
import csv,hashlib,json,re,subprocess,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d1-2026-11-05'
BASE='ae9645d359b40626b0008ffd54a6e9acd7d77bf1'

import history_evidence as history

class PaperV5d1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d1_offload',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
        cls.sites={'v5d1 '+r['name']:r for r in json.loads((ROOT/'data/measurements/paper-v5d4-2026-11-05/v5d1-sites-current.json').read_text())}

    def plant(self,key,old,new):
        r=self.sites[key];text=self.texts[r['file']]
        part=next(p for p in text.split('\n\n') if r['marker'] in p)
        self.assertIn(old,r['phrase']);changed,n=re.subn(r'\s+'.join(map(re.escape,r['phrase'].split())),lambda _:r['phrase'].replace(old,new,1),part,count=1)
        self.assertEqual(n,1);self.assertNotEqual(changed,part)
        return dict(self.texts,**{r['file']:text.replace(part,changed,1)})

    # All new sites have actually applied omission controls with the nearby
    # clean current text; CLI controls also require exact first-digit attribution.
    def test_all_new_sites_have_named_applied_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for k,r in self.sites.items():self.assertIn(k,self.off.missing(self.plant(k,r['phrase'],'УДАЛЕНО')))
        self.assertEqual(self.off.missing(self.texts),[])

    # FACTS table gives each series' own N1 baseline, peak and largest tested N;
    # the capped grid is not evidence of a hardware capacity maximum.
    def test_m3_peak_gains_and_full_capped_grid_follow_facts(self):
        facts=(D/'FACTS-m3-capped.md').read_text();text=self.texts['05-clients.tex']
        self.assertIn('предельную вместимость машины таблица не устанавливает',text)
        rx=r'\| ([\d,]+) \| ([\d.]+) \| ([\d.]+) at N = (\d+), x([\d.]+) \| ([\d.]+) at N = (\d+), x([\d.]+) \|'
        data=re.findall(rx,facts);self.assertEqual(len(data),3)
        for depth,one,peak,np,gain,last,largest,lastgain in data:
            self.assertAlmostEqual(float(peak)/float(one),float(gain),places=3)
            self.assertAlmostEqual(float(last)/float(one),float(lastgain),places=3)
            self.assertIn(depth.replace(',','')+' & '+one,text)
            for value in (peak,last):self.assertIn(value,text)
        for values in ('22.561 / 34.104 / 48.708 / 49.096 / 44.767','17.652 / 26.913 / 31.696 / 29.314','13.766 / 17.674'):
            self.assertIn(values,facts)
            for value in values.split(' / '):self.assertIn(value,text)
        for f in ('01-introduction.tex','14-conclusion.tex'):
            self.assertIn('3.588/2.557/1.583',self.texts[f]);self.assertIn('2.71/2.02/1.28',self.texts[f]);self.assertIn('15.15/5.07/2.21/1.75',self.texts[f])
        self.assertAlmostEqual(100*(17.694/17.732-1),-.21,places=2)

    # Positive pageouts inside64MiB must remain visible, and the original32
    # refusal must not be relabelled a completed23-shape or universal no-pageout run.
    def test_m3_memory_bound_and_original_refusal_are_disclosed(self):
        text=self.texts['05-clients.tex'];self.assertIn('Ранний запуск 64 тысячи/32 потока был отклонён',text)
        self.assertIn('Положительная выгрузка страниц остаётся условием измерения',text)
        self.assertIn('2455 страниц (38.36',text)
        self.assertIn('исходная сетка из 23 форм не завершалась',text)
        self.assertAlmostEqual(2455*16384/2**20,38.36,places=2);self.assertAlmostEqual(2313*16384/2**20,36.14,places=2)
        for key,a,b in [('M3 capped grid and refusal','не завершалась','завершилась'),('M3 bounded memory','2455 страниц','0 страниц'),('M3 gains and control','Контроль не заменяет медиану сетки','Контроль заменяет медиану сетки')]:
            key='v5d1 '+key;self.assertIn(key,self.off.missing(self.plant(key,a,b)))

    # Replayed journals/boundaries isolate accumulated client-side effects;
    # neither free-history equivalence nor bf16-policy timing is measured.
    def test_bf16_rehearsal_keeps_fixed_journal_and_routing_scope(self):
        text=self.texts['11-limitations.tex'];self.assertIn('те же границы маршрутизации f32',text)
        self.assertIn('на одной карте, без сравнения скорости',text)
        self.assertIn('побитовая точность bf16 не заявляется',text)
        for key,a,b in [('bf16 rehearsal design','те же границы маршрутизации f32','новые границы маршрутизации bf16'),('bf16 checkpoints','не разошлась за 64 токена','не разошлась за все 40 ходов')]:
            key='v5d1 '+key;self.assertIn(key,self.off.missing(self.plant(key,a,b)))

    # All four f32/noise/bf16 rows quote the independent FACTS table, preserving
    # nonzero differences and the64-position/64-token continuation bounds.
    def test_bf16_checkpoint_rows_match_f32_and_partition_controls(self):
        facts=(D/'FACTS-bf16-rehearsal.md').read_text();text=self.texts['11-limitations.tex']
        lines=[line for line in facts.splitlines() if re.match(r'\s*\| (f32 rehearsal|local partition|bf16 replay)',line)]
        self.assertEqual(len(lines),4)
        for line in lines:
            vals=line.split('|')[2].strip().split(' / ');self.assertEqual(len(vals),4)
            for value in vals:self.assertIn(value,text)
        for value in ('0.00329','0.004457','0.53--0.82','0.76--1.06','0.51--1.12','5 / 9 / 12 / 18'):self.assertIn(value,text)
        self.assertIn(r'\texttt{lossy}',self.texts['90-appendix.tex'])
        self.assertIn('прошёл численный допуск',self.texts['90-appendix.tex'])

    # 742 confirmed plus1 unverified is743 accepted, not universal agreement;
    # committed spending is an upper bound rather than a debit observation.
    def test_api_window_spend_and_cost_crosscheck_keep_unknown_call(self):
        text=self.texts['07-economics.tex'];self.assertIn('один вызов остался непроверенным',text)
        self.assertIn('Резерв обязательств не является измеренным списанием',text)
        self.assertEqual(742+1,743);self.assertLess(29.3068,44.9799);self.assertLess(44.9799,45)
        key='v5d1 API window spend crosscheck'
        self.assertIn(key,self.off.missing(self.plant(key,'один вызов остался непроверенным','все вызовы проверены')))

    # Cache and availability use different inclusion rules. A high-cache but
    # unavailable endpoint cannot qualify from its hit fraction alone.
    def test_api_cadence_identity_and_availability_are_separate(self):
        text=self.texts['07-economics.tex'];self.assertIn('но исключается из метрик кэша',text)
        self.assertIn('повторного воспроизведения вызовов нет',text)
        self.assertGreater(.987,.95);self.assertLess(.875,.95)
        facts=(D/'FACTS-api-final.md').read_text()
        for value in ('0.286','0.429','0.451','0.509','0.517','0.757','0.014','0.141','0.987','0.997','0.998','0.094','0.55','0.846','0.80','0.875','0.452','0.932','0.780','0.474'):
            self.assertIn(value,facts);self.assertIn(value,text)
        key='v5d1 API restarts identity availability'
        self.assertIn(key,self.off.missing(self.plant(key,'но исключается из метрик кэша','и включается в метрики кэша')))
        key='v5d1 API cadence scope';self.assertIn(key,self.off.missing(self.plant(key,'не переносятся между поставщиками и расписаниями','переносятся на всех поставщиков')))

    # Descriptive pooled GLM pricing is not a Qwen or article-profile quote.
    # Earlier native exports/code remain at accepted23; accepted24 adds API-only prices.
    def test_engine24_economic_point_stays_pending_and_native_exports_frozen(self):
        self.assertEqual(history.unchanged(BASE,'calc/out/run23','calc/hybridcalc','calc/run22','calc/run23',allow_ports=True),'')
        self.assertTrue((ROOT/'calc/out/run24').exists());self.assertEqual(history.unchanged('ca7f228acd789380bf46016fd87acc33e1b07aef','calc/out/run24','calc/run24',allow_ports=True),'')
        text=self.texts['07-economics.tex'];self.assertIn('У Qwen на миллионе все три измеренных поставщика ниже порога доступности',text)
        self.assertIn('прогоном 24',self.texts['90-appendix.tex']);self.assertIn('частичные наборы оценимых цен',text)
        key='v5d1 API pooled descriptive only';self.assertIn(key,self.off.missing(self.plant(key,'GLM-5.3-flash','Qwen3.8-27B')))
        # Detailed conditional crossings remain in the plain-language blocks;
        # the measurement-led abstract retains the cheapest-API applicability bound.
        for f in ('01-introduction.tex','14-conclusion.tex'):
            for value in ('98.1','45'):self.assertIn(value,self.texts[f])
        self.assertIn('ни в одной оценимой измеренной точке Qwen',self.texts['00-abstract.tex'])

    # Completed capped grid/rehearsal/study leave only their economic or Mac
    # successors pending. Saved interim deeper RULER does not close full-depth analysis.
    def test_pending_cutoff_and_owner_stopped_ruler_are_not_promoted(self):
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        inv=json.loads((ROOT/'calc/tests/data/paper-v5d4-pending.json').read_text())
        pending=' '.join(r['body'] for r in inv)
        for stale in ('шаг 55 выполняется','репетиция Qwen bf16 на GPU','измеренные доли кэша OpenRouter'):
            self.assertNotIn(stale,pending)
        self.assertIn('по решению владельца 2026-11-04',pending);self.assertIn('2026-11-05 12:00 UTC',pending)
        # Complete64k closes that wait;128k resumes on another host with original build.
        for f in ('11-limitations.tex','90-appendix.tex'):
            self.assertIn('узле A',self.texts[f]);self.assertIn('узла B',self.texts[f]);self.assertNotIn('результаты не собраны',self.texts[f])
        self.assertIn('390/390',self.texts['11-limitations.tex'])
        self.assertIn('модельным: аренда не запустила контейнер',self.texts['06-server.tex'])
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)

    # Current evidence custody is independent of exact-byte publication pins;
    # predecessor source/measurement archives remain unchanged and independently tested.
    def test_v5d1_sources_have_sha_custody(self):
        readme=(D/'README.md').read_text()
        receipt=json.loads((D/'source-receipt.json').read_text())
        self.assertTrue(receipt['api_report_sha256'].startswith('2485e7f2'))
        for endpoint in receipt['additional_excluded_endpoint_variants_from_FACTS_evidence']:
            self.assertIn(endpoint.split(' / ')[1],self.texts['07-economics.tex'])
        for p in D.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
