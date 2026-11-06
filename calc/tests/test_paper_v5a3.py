"""Analyst corrections: witnessed collection paths, endpoints and M5 measurements."""
from test_paper_v5a2 import current_changelog
import hashlib
import json
import re
import unittest
from r13_audit import ROOT,module
SOURCE=ROOT/'data/measurements/paper-v5a3-2026-11-03'


def excluded_cache_probe(text):
    return bool(re.search(r'(?:Chutes|OpenRouter)[^.\n]{0,120}(?:three[- ]call|тр[её]х\s*вызов|три\s+(?:вызов|запрос)|3\s*(?:вызов|запрос))',text,re.I))


class PaperV5a3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5a3_guard',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    # Every new measurement/qualifier has an applied omission rejected at the
    # named site. These are finite publication contracts, not hardware tests.
    def test_each_analyst_site_rejects_named_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for name,(file,marker,phrase) in self.off.v5a3_expected().items():
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,name)
            self.assertIn(name,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # The observed RULER score equality cannot become bit identity of answers.
    # Import is followed by local sampling; node batching is not guessed.
    def test_ruler_paths_and_score_identity_do_not_imply_bit_identity(self):
        text=self.texts['11-limitations.tex'];book=(SOURCE/'RULER-RUNBOOK.md').read_text()
        for phrase in ('The offload arm imports prefill state, then samples locally','--batch 64 --ubatch 64','--batch 256 --ubatch 256'):
            self.assertIn(phrase,book)
        for phrase in ('prefill на узле по собственной разбивке','batch и ubatch 64, другая локальная разбивка 256',
                       'совпадение оценок не означает побитового совпадения ответов'):
            self.assertIn(phrase,text)
        key='v5a3 conclusion endpoints';file,marker,phrase=self.off.expected()[key]
        bad=self.texts[file].replace('Побитовое равенство ответов RULER не заявляется.','Побитовое равенство ответов RULER заявляется.')
        self.assertNotEqual(bad,self.texts[file]);self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))
        for file in ('00-abstract.tex','14-conclusion.tex'):
            self.assertIn('20 документах',self.texts[file])

    # Post-result margin choice cannot be labelled a confirmatory 8k/32k
    # registration; Glimmer remains exploratory under extended analysis rules.
    def test_registration_and_glimmer_exploratory_scope(self):
        text=self.texts['11-limitations.tex']
        for phrase in ('14:36 UTC после получения результатов Qwen на 8 и 32 тысячах',
                       'Сбор 64 тысяч начался после регистрации',
                       'Результаты Glimmer исследовательские',r'оффлоад $+1.22$ п.п., другая разбивка $+1.17$ п.п.',
                       'числа не отделяют вклад оффлоада от вклада смены пути prefill'):
            self.assertIn(phrase,text)
        key='v5a ruler detail 2';file,marker,phrase=self.off.expected()[key]
        bad=text.replace('после получения результатов','до получения результатов',1)
        self.assertNotEqual(bad,text);self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # All accepted M5 ladder cells and parallel aggregates follow literal FACTS;
    # normal priority is witnessed during the run, not inferred afterwards.
    def test_full_m5_rows_follow_facts_and_recorded_priority(self):
        data=json.loads((SOURCE/'m5-pri31.json').read_text());facts=(SOURCE/'FACTS-M5.md').read_text();text=self.texts['05-clients.tex']
        for model in ('Qwen','Glimmer'):
            for r in data[model]:
                source=' / '.join(f'{v:.1f}' for v in r[1:5]);self.assertIn(source,facts)
                printed=model+' & '+str(r[0])+' & '+' & '.join(f'{v:.1f}' for v in r[1:5])+' & '+f'{r[5]:.2f}'
                self.assertIn(printed,text)
        self.assertIn('nice 0 во всех 36 и 31 отсчётах',self.texts['90-appendix.tex'])
        self.assertIn('M5 1.6.7: PRI~31 записан вместе с предками процесса',self.texts['90-appendix.tex'])
        self.assertNotIn('M5 Max, 1.6.6 &',text)
        self.assertIn('новые измерения M5 при PRI~31 приведены отдельно',self.texts['91-calculation-history.tex'])

    # Ratios use each series' own single-stream baseline; a separate np4
    # control must not replace the main Qwen128k median to inflate its gain.
    def test_m5_batch_gains_and_two_regressions_are_arithmetic(self):
        d=json.loads((SOURCE/'m5-pri31.json').read_text())['parallel']
        for model,depth,index,gain in [('Qwen','32',5,2.71),('Qwen','64',3,2.02),('Qwen','128',2,1.28),('Glimmer','32',5,3.24),('Glimmer','64',5,2.66),('Glimmer','129',4,2.36)]:
            row=d[model][depth];self.assertAlmostEqual(row[index]/row[0],gain,places=2)
        self.assertAlmostEqual(100*(57.089/62.78-1),-9.1,places=1)
        self.assertAlmostEqual(100*(62.727/65.54-1),-4.3,places=1)
        for phrase in ('контроль не заменяет медиану 20.778','Серверный выигрыш vLLM на PRO 6000 измерен'):
            self.assertIn(phrase,self.texts['05-clients.tex'])

    # Abstract drops lab procedure while retaining bounds and deferred costs;
    # a shallow 14x headline or a lossless bf16 claim must fail its named site.
    def test_abstract_profile_gap_lab_details_and_lossy_bf16_boundary(self):
        abstract=self.texts['00-abstract.tex']
        for word in ('PRI','код выхода','инструментирован','14 раз'):self.assertNotIn(word,abstract)
        self.assertIn('10.1--10.8',self.texts['06-server.tex']);self.assertIn('около 14 раз',self.texts['06-server.tex'])
        self.assertLessEqual(len(self.off.abstract_text(abstract)),1920)
        self.assertEqual(len(json.loads((ROOT/'data/measurements/paper-v5b-2026-11-03/r20-migration.json').read_text())),26)
        self.assertEqual(self.off.r20_signatures(self.texts),[])
        for key,old,new in [('abstract profile','10.1--10.8','14'),('abstract bf16','bf16 округляет','bf16 передаёт состояние без потерь')]:
            name='v5a3 '+key;file,_,phrase=self.off.expected()[name]
            bad=self.texts[file].replace(old,new,1);self.assertNotEqual(bad,self.texts[file]);self.assertIn(name,self.off.missing(dict(self.texts,**{file:bad})))

    # Excluded three-call probe cannot leak into current prose or release notes;
    # ordinary listed API/cache prices and pending provider admission are valid.
    def test_excluded_three_call_cache_probe_is_absent(self):
        current='\n'.join(self.texts.values())+'\n'+current_changelog((ROOT/'CHANGELOG.md').read_text())
        self.assertFalse(excluded_cache_probe(current))
        for plant in ('Chutes: три вызова подтвердили кэш.','OpenRouter three-call cache probe.'):
            self.assertTrue(excluded_cache_probe(current+'\n'+plant))
        self.assertFalse(excluded_cache_probe('Chutes: вход $0.039, выход $1.25; попадания ожидаются.'))
        self.assertIn('own cluster was recalculated on vLLM',(ROOT/'CHANGELOG.md').read_text())

    # Archived-source SHA custody is separate from the live publication pins.
    def test_v5a3_evidence_identity(self):
        readme=(SOURCE/'README.md').read_text()
        for p in SOURCE.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
