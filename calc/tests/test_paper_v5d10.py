"""Accepted near-tie and attempt-5 limits, with finite publication regressions."""
import gzip,hashlib,json,re,unittest
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d10-2026-11-06'
class PaperV5d10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d10_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
    def paragraph(self,file,marker):
        parts=[p for p in self.texts[file].split('\n\n') if marker in p]
        self.assertEqual(len(parts),1,marker);return parts[0]
    # Every finite new/superseded claim has an applied omission rejection.
    def test_current_predicates_reject_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        keys=list(json.loads((D/'successors.json').read_text()))+['v5d10 '+r['name']for r in json.loads((D/'sites.json').read_text())]
        for k in keys:
            f,m,w=self.off.expected()[k];p=self.paragraph(f,m)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',p,count=1)
            self.assertEqual(n,1,k);self.assertIn(k,self.off.missing(dict(self.texts,**{f:self.texts[f].replace(p,bad,1)})),k)
    # Greedy choices are deterministic within a partition; reduction-order noise
    # may flip near-ties without random sampling or an architecture-proof claim.
    def test_greedy_mechanism_excludes_random_sampling(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Близкие кандидаты и смена ответов.}')
        for w in ('температурой 0','повтор той же разбивки побитово совпадает','порядок\nсложения чисел с плавающей точкой','последние биты логитов','меняется argmax'):self.assertIn(w,t)
    # The denominator is changed answers; complement preservation is forbidden.
    def test_content_flip_lower_bound_has_correct_denominator(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Близкие кандидаты и смена ответов.}')
        for w in ('41/480 изменившихся ответов','1/188','Правило даёт нижнюю границу','оставшаяся доля не доказывает сохранность содержания'):self.assertIn(w,t)
        self.assertAlmostEqual(100*41/480,8.54,places=2);self.assertAlmostEqual(100/188,.53,places=2)
        a=self.paragraph('90-appendix.tex','Температура 0 и фиксированный seed')
        for w in ('22/255 (8.63','19/225 (8.44','0/66, 1/62 и 0/60','Сохранность содержания дополнения к этой доле не установлена'):self.assertIn(w,a)
    # Longer outputs prevent treating answer-level churn as a per-token rate.
    def test_answer_change_ratio_is_not_per_token_ratio(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Близкие кандидаты и смена ответов.}')
        for w in ('примерно вдвое больше токенов','не задаёт отношения близких кандидатов на токен'):self.assertIn(w,t)
    # Softcap is an untested hypothesis; either exact prompts or a separately
    # declared new experiment is needed, not an unrecorded replacement dataset.
    def test_softcap_hypothesis_preserves_two_prompt_routes(self):
        t=self.paragraph('90-appendix.tex','Glimmer является плотной моделью из 52 слоёв')
        for w in ('39 со скользящим окном 2048 и 13 глобальных','без маршрутизатора MoE','softcap логитов 20','16 слоёв внимания и 48 рекуррентных','есть гипотеза','GPU-опыт не запускался','только 2 из 26','промптов из закреплённых данных','точным сравнением хэшей','нового набора промптов','объявленного отдельным опытом до запуска'):self.assertIn(w,t)
    # Census metadata cannot imply that older sessions never existed or that
    # contents were read; live Claude dates do not replace export-cohort dates.
    def test_census_is_metadata_only_and_keeps_date_limits(self):
        t=self.paragraph('90-appendix.tex',r'\textbf{Перепись дат локального хранилища.}')
        for w in ('имён файлов и времени изменения','без открытия содержимого','ровно один rollout Codex','2025-09-22','ни одного за октябрь 2025','раньше живого хранилища Mac','сохранность таких времён при копировании не установлена','архивы не распаковывались'):self.assertIn(w,t)
        raw=gzip.decompress((D/'facts-census.md.gz').read_bytes()).decode();self.assertIn('Whether they existed and were removed',raw);self.assertIn('9,631',raw)
    # Workload amendment precedes attempt5; synthetic attempt4 is retained as a
    # separate failure rather than silently relabelled as natural text.
    def test_natural_amendment_precedes_run_and_keeps_synthetic_failure(self):
        t=self.paragraph('06-server.tex',r'\textbf{Пятая попытка vLLM на естественном тексте.}')
        self.assertIn('до запуска при неизменном критерии качества',t)
        a=self.paragraph('90-appendix.tex',r'\textbf{Поправка и пятая попытка vLLM.}')
        for w in ('объявлена, подписана и проверена до попытки','собственное продолжение каждого документа','FP8-Q4-SESSION-KL-1','отдельные результаты'):self.assertIn(w,a)
        prior=self.paragraph('90-appendix.tex',r'\textbf{Узел vLLM для длинной сессии.}')
        self.assertIn('Четвёртая попытка',prior);self.assertIn('0.3286 нат против границы 0.03',prior)
    # All four rows match the accepted source; eviction and turn4-only-top1
    # failure are preserved, with no inference that the session reached64k.
    def test_attempt_rows_keep_eviction_and_stopping_rule(self):
        t=self.paragraph('90-appendix.tex',r'\label{tab:vllm-natural-five}')
        expected=[(1,22385,.0196,.0164,'61/64','допуск'),(2,28417,.0171,.0135,'64/64','допуск'),(3,34449,.0156,.0128,'63/64','допуск'),(4,40481,.0034,.0023,'58/64','отказ')]
        rows=re.findall(r'(?m)^(\d) & (\d+) & ([.\d]+) & ([.\d]+) & (\d+/64) & (допуск|отказ)',t)
        self.assertEqual([(int(i),int(d),float(k),float(e),n,v)for i,d,k,e,n,v in rows],expected)
        self.assertIn('Третий ход включает принудительное вытеснение',t)
        main=self.paragraph('06-server.tex',r'\textbf{Пятая попытка vLLM на естественном тексте.}')
        self.assertIn('Сессия не достигла 64 тысяч',main)
    # Small KL does not override the frozen top1 bound; all six flips are near
    # ties, not proof that a new unseen-document criterion would pass.
    def test_near_ties_do_not_override_frozen_quality_gate(self):
        t=self.paragraph('90-appendix.tex','Контроль другой разбивки дал KL')
        for w in ('Наименьший KL попытки не отменяет отказ по top-1','0.006 / 0.031 / 0.041 / 0.107 / 0.109 / 0.179','0.07--0.51','23 из 64','0.0032 / 0.0035 / 0.0028 / 0.0011','требует 60/64 и отказывает при 58/64','заранее и проверить на невиденных документах','без квалификации','одноформатный путь llama.cpp остаётся квалифицированным','Всеобщая невозможность переноса не установлена'):self.assertIn(w,t)
        self.assertLess(.0034,min(.0196,.0171,.0156));self.assertLess(58,60)
    # Printed combined capacity uses the bottleneck, not GPU-only people.
    def test_review_rounding_and_combined_people_are_arithmetic(self):
        t=self.paragraph('02-workload.tex',r'\textbf{Ёмкость сервера для начал, оценка.}')
        for w in ('340--480 человек','2800 началами в сутки, то есть около 280 человек','при десяти началах на человека'):self.assertIn(w,t)
        forecast=self.paragraph('90-appendix.tex',r'\textbf{Предварительная проверка модели времени.}')
        self.assertIn('25.6--28.4',forecast)
        self.assertAlmostEqual(100*3353.665/13084.935,25.6,delta=.05);self.assertAlmostEqual(100*3353.665/11790.457,28.4,delta=.05)
        self.assertEqual(2800/10,280)
    # Complete custody is hash checked; existing RULER128k waits are retained.
    def test_custody_and_pending_inventory_are_exact(self):
        for row in json.loads((D/'custody.json').read_text()):
            packed=(D/row['compressed']).read_bytes();raw=gzip.decompress(packed)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(packed).hexdigest(),row['compressed_sha256'])
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        self.assertIn('после отказа пятой попытки на естественном тексте',self.texts['06-server.tex'])
        self.assertNotIn('Exact macros: paper-v5d8-pending.json.',(ROOT/'UNRESOLVED_QUESTIONS.md').read_text())
        self.assertNotIn('natural-text diagnostic measured; the long session remains unqualified',(ROOT/'README.md').read_text())
