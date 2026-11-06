"""Owner-defined closed perimeter: retain component scope and unmeasured waits."""
import hashlib,json,re,unittest
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d7-2026-11-05'

class PaperV5d7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d7_off',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text()for p in cls.off.SECTIONS.glob('*.tex')}

    # Exact successor predicates retain all earlier named claims; applied
    # omissions must be rejected at the declared locus, without another-site fallback.
    def test_each_successor_and_new_site_rejects_applied_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        keys=list(json.loads((D/'successors.json').read_text()))+['v5d7 '+r['name']for r in json.loads((D/'sites.json').read_text())]
        for key in keys:
            f,m,w=self.off.expected()[key];t=self.texts[f];part=next(p for p in t.split('\n\n')if m in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key);self.assertNotEqual(bad,part,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:t.replace(part,bad,1)})),key)

    # A closed20% component requires an internal equal-cost80% remainder.
    # These text contracts cannot establish optimal full/mixed economics.
    def test_twenty_percent_requires_internal_equal_cost_remainder(self):
        for f,marker in [('01-introduction.tex',r'\item \textbf{Закрытый контур.}'),('14-conclusion.tex',r'\textbf{Границы применимости.}')]:
            t=next(p for p in self.texts[f].split('\n\n')if marker in p)
            for w in ('20\\%','80\\%','внутренн','в обоих вариантах'):self.assertIn(w,t,f)
            self.assertNotIn('остальные облачные',t);self.assertNotIn('не образует закрытого контура',t)
        self.assertIn('внутренняя большая модель обслуживает остальные 80',self.texts['01-introduction.tex'])
        self.assertNotIn(r'смешанная схема \pending',self.texts['01-introduction.tex'])
        t=self.texts['07-economics.tex']
        for w in ('её стоимость одинакова в обоих вариантах','Общая цена большой модели одинакова и сокращается','Основная база полной доли 100\\% запрещает серверу подменять генерацию клиента'):self.assertIn(w,t)

    # Abstracts retain the native5/2 component figures, internal remainder and
    # pending full/mixed result, rather than a fully closed economic promise.
    def test_bilingual_abstracts_keep_full_and_mixed_waits(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        for w in ('с 4 человек при лёгкой','с 2 при средней','доле Qwen 100%','не дешевле самого дешёвого допущенного API'):self.assertIn(w,ru)
        for w in ('from 4 people at light','2 at medium','100% Qwen scenario','heavy load exceeds client capacity','never costs less than the cheapest admitted API'):self.assertIn(w,en)

    # Task share is an input scenario; the old engine normalizes calls, so it
    # must not silently become a measured share of tasks or work.
    def test_internal_task_share_does_not_promote_call_share(self):
        t=self.texts['07-economics.tex']
        for w in ('Доля $s$ означает долю задач средней модели внутри контура.','нормирует число вызовов; соответствие доле задач не измерено.','Если клиентов нет, их покупка входит в цену гибрида.','сначала'):
            if w=='сначала':self.assertIn('Сначала организация выбирает класс модели, затем способ исполнения.',t)
            else:self.assertIn(w,t)
        self.assertIn('в смешанной схеме доля 20',self.texts['14-conclusion.tex'])

    # The model map measures Qwen components only. GLM/Ultra/cluster options
    # are scenarios, with no GPU or multi-model deployment measurement claim.
    def test_model_map_preserves_measured_and_scenario_boundary(self):
        t=self.texts['07-economics.tex'];part=t.split(r'\subsection{Закрытый контур}',1)[1].split(r'\textbf{Уже имеющийся',1)[0]
        for w in ('Компоненты измерены на 64~ГБ','Только расчёт; замеры ожидаются','2 B300 на реплику','M5 Max 64/128~ГБ','Studio 256/512~ГБ','Неприменим','без замера этой реплики','M5 Ultra с 256--512~ГБ','Конфигурации облачного класса и MoE'):self.assertIn(w,part)
        self.assertIn('сотен миллиардов до триллионов',part)
        self.assertNotIn('Studio измерен',part)

    # Every owner-added wait is executable inventory, not silently inferred
    # measurements or unaccepted engine25 data. Existing physical waits remain.
    def test_new_waits_and_unaccepted_engine_are_explicit(self):
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        for body in ('GLM на Studio: decode и prefill; GLM prefill на B300; раскладка состояния и импорт.','доля задач среднего класса и качество замены: входной сценарий, без измерения.'):
            self.assertIn('\\pending{'+body+'}',self.texts['07-economics.tex'])
        self.assertIn('M5 Ultra задан как удвоенные вычисления M5 Max',self.texts['07-economics.tex'])
        self.assertTrue((ROOT/'calc/out/run25').exists());self.assertTrue((ROOT/'calc/out/run26').exists())
        self.assertIn('Большая модель на собственном многоузловом кластере',self.texts['13-outlook.tex'])
        self.assertIn('не являются измерениями',self.texts['13-outlook.tex'])

    # Documentary source hashes are pinned independently of publication prose.
    def test_owner_source_and_new_evidence_have_custody(self):
        r=json.loads((D/'acceptance.json').read_text())
        self.assertEqual(hashlib.sha256((D/'OWNER-BRIEF.md').read_bytes()).hexdigest(),r['owner_brief_sha256'])
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
