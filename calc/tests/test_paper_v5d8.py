"""Accepted economic cells and proposed lifecycle boundaries, not new inference."""
import csv,gzip,hashlib,json,re,unittest
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d8-2026-11-05'
def rows(path):
    with(ROOT/path).open()as f:return list(csv.DictReader(f))
def one(data,**kw):
    found=[r for r in data if all(r.get(k)==str(v)for k,v in kw.items())];assert len(found)==1,(kw,len(found));return found[0]
def archived(name):return gzip.decompress((D/name).read_bytes())

class PaperV5d8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d8_off',ROOT/'paper/data/offload_bound.py');cls.texts={p.name:p.read_text()for p in cls.off.SECTIONS.glob('*.tex')}

    # Exact finite omissions must fail at the declared locus, never by fallback.
    def test_each_successor_and_new_boundary_rejects_applied_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        keys=list(json.loads((D/'successors.json').read_text()))+['v5d8 '+r['name']for r in json.loads((D/'sites.json').read_text())]
        for key in keys:
            f,m,w=self.off.expected()[key];t=self.texts[f];part=next(p for p in t.split('\n\n')if m in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',part,count=1)
            self.assertEqual(n,1,key);self.assertNotEqual(bad,part,key)
            self.assertIn(key,self.off.missing(dict(self.texts,**{f:t.replace(part,bad,1)})),key)

    # Native26 cells distinguish no sustained crossing from client-capacity refusal.
    # The expensive cloud floor is capacity only, not service or task throughput.
    def test_full_and_mixed_crossings_have_exact_native_basis(self):
        rr=rows('calc/out/run26/crossings.csv');base=dict(profile='existing_combined',model='qwen',server='pro6000_fp8',client='m5max64',client_basis='owned',billing='bought',share='1.0',glm_prefill_slowdown='')
        for load,n in [('light','4'),('medium','2'),('heavy','')]:self.assertEqual(one(rr,**base,load=load)['sustained_from'],n)
        heavy=one(rr,**base,load='heavy');self.assertEqual(heavy['team50_status'],'client_decode_capacity_shortfall')
        for share,values in [('0.2',('','5','2')),('0.5',('8','3',''))]:
            for load,n in zip(('light','medium','heavy'),values):self.assertEqual(one(rr,**dict(base,share=share),load=load)['sustained_from'],n)
        new128=one(rr,**dict(base,client='m5max',client_basis='new'),load='light');self.assertEqual(new128['sustained_from'],'20')
        mixed=rows('calc/out/run26/mixed_scheme.csv');self.assertEqual(len(mixed),3072)
        self.assertTrue(all(r['hybrid_common_large_person_month']==r['own_common_large_person_month']for r in mixed))
        t=self.texts['07-economics.tex']
        for w in ('сервер выполняет только prefill','отказ есть недостаточная ёмкость клиента','положительный'):
            if w!='положительный':self.assertIn(w,t)
        self.assertIn('тяжёлую клиент не вмещает',self.off.abstract_text(self.texts['00-abstract.tex']))
        self.assertNotIn('ожидают расчёта 26',t)
        cloud=rows('calc/out/run26/cloud_affordability.csv')
        for billing,n,cost in [('bought','34',674.032342),('rented','111',2219.19576)]:
            r=one(cloud,billing=billing,retention_basis='weights_only_floor');self.assertEqual(r['first_affordable'],n);self.assertAlmostEqual(float(r['team50_person_month']),cost,places=2)
        self.assertIn('без квалифицированной производительности, хранения и межсоединения',t)

    # Zero-offload GLM is projected local compute, not measured prefill speedup;
    # purchased never means no sustained crossing even if isolated point wins exist.
    def test_glm_projection_keeps_zero_offload_and_purchase_scope(self):
        rr=rows('calc/out/run26/crossings.csv');base=dict(profile='existing_combined',model='glm',client='ultra256',client_basis='owned',billing='bought',share='1.0',glm_prefill_slowdown='1')
        selected=[r for r in rr if all(r.get(k)==v for k,v in base.items())];self.assertEqual(len(selected),3)
        self.assertEqual([one(selected,load=x)['sustained_from']for x in ('light','medium','heavy')],['','346','68'])
        purchased=[r for r in rr if all(r.get(k)==v for k,v in dict(base,client_basis='new').items())];self.assertEqual(len(purchased),3);self.assertTrue(all(not r['sustained_from']for r in purchased))
        self.assertTrue(any(r['first_win']for r in purchased))
        m=[r for r in rows('calc/out/run26/middle_cost.csv')if r['model']=='glm'and r['team']=='50'and r['hybrid_status']=='feasible_prefill_only'];self.assertTrue(m);self.assertTrue(all(float(r['offload_share'])==0 for r in m))
        t=self.texts['07-economics.tex']
        for w in ('GLM/Ultra полностью расчётная','оффлоад равен 0\\%','без ускорения prefill','покупка Studio не даёт устойчивого пересечения','197 / 63'):self.assertIn(w,t)

    # Native25 is an unmeasured retention sensitivity, separate from table18.
    # The fitted coverage cells cannot be relabelled observed per-call shares.
    def test_fleet_retention_and_fit_coverage_are_not_new_headlines(self):
        self.assertEqual((249000*65536+156893184),16475357184);self.assertEqual(900_000_000_000//16475357184,54);self.assertEqual((200+56)//57,4)
        rr=rows('calc/out/run25/fleet_summary.csv');base=dict(profile='existing_combined',weighting='accepted_shapes',share='0.2',load='light',restore_slowdown='1',team='50')
        for storage,prices in [('expanded_nvme',(19.95,32.38,57.23)),('all_ram_warm',(23.47,39.42,71.31))]:
            for n,p in zip((1,2,4),prices):self.assertAlmostEqual(float(one(rr,**base,storage_case=storage,fleet_policy=n)['person_month']),p,places=2)
        coverage=one(rows('calc/out/run25/coverage.csv'),profile='existing_combined')
        for col,v in [('fitted_call_shape_share',27.28),('fitted_input_token_share',20.52),('fitted_output_token_share',27.38),('fitted_work_seconds_share',28.68)]:self.assertAlmostEqual(100*float(coverage[col]),v,places=2)
        for col in ('observed_log_call_share','observed_log_input_token_share','observed_log_work_share'):self.assertEqual(coverage[col],'')
        t=self.texts['07-economics.tex']
        for w in ('Округление $\\lceil200/57\\rceil=4$ задаёт хранение','Это отдельная чувствительность с неизмеренными','таблица~\\ref{tab:r22-dedicated50} остаётся на прежней базе','исходные доли по отдельным вызовам недоступны'):self.assertIn(w,t)
        self.assertIn('только общему профилю при $s=20\\%$ и лёгкой нагрузке',t)

    # The frozen artifact independently reproduces phases, common-cache boundary,
    # final depth and tail distortion; it is neither task-success nor inference evidence.
    def test_lifecycle_artifact_and_shared_prefix_fairness_are_exact(self):
        raw=gzip.decompress(archived('r49g-lifecycle-session.json.gz.gz'));q=json.loads(raw);turns=q['turns'];self.assertEqual(len(turns),116);self.assertEqual(turns[0]['depth_before'],0);self.assertEqual(turns[-1]['depth_after'],228388)
        self.assertEqual(len(turns[0]['input_ids']),34002);self.assertEqual(turns[0]['timed_input_tokens'],24378)
        for phase,n,total,output,wait in [('start',4,91214,919,33.307826),('deep',112,69080,57551,3320.357490)]:
            a=[r for r in turns if r['phase']==phase];self.assertEqual(len(a),n);self.assertEqual(sum(r['timed_input_tokens']for r in a),total);self.assertEqual(sum(len(r['output_ids'])for r in a),output);self.assertAlmostEqual(sum(r['pause_seconds']for r in a),wait,places=5)
        volume=sum(len(t['input_ids'])for t in turns[1:]);large=sum(len(t['input_ids'])for t in turns[1:]if len(t['input_ids'])>=10000);self.assertAlmostEqual(100*large/volume,49.17,places=2)
        t=self.texts['90-appendix.tex']
        for w in ('оба'):
            self.assertIn('Оба клиента восстанавливают один нативный снимок Mac',t)
        for w in ('верхняя сценарная граница','без измеренной доли стабильного системного промпта','49.17 & 21.30','создания и восстановления кэша','Подписан предварительный численный прогноз до проверки канала'):self.assertIn(w,t)
        self.assertIn('переменная часть первого запроса $34002-9624=24378$',t)

    # Observed continuation sizes exclude first/reset calls; rare deep frequency
    # is fitted. Different source cohorts cannot become measured context arrivals.
    def test_phase_inference_keeps_observed_fitted_and_cohort_limits(self):
        t=self.texts['02-workload.tex'];a=self.texts['90-appendix.tex'];b=self.texts['91-calculation-history.tex']
        self.assertIn(r'13\,175 контекстов парсера',t);self.assertIn('По неколичественной характеристике владельца',t)
        for w in ('6215 / 5344 / 2329 / 1448','исключают первые запросы и сбросы','0.43\\%','оценка совместного распределения','не равен точному трафику prefill'):self.assertIn(w,t)
        for w in ('Дат полного full04 нет','full05','233 активные даты UTC','73.66 / 18.70 / 7.64','домена','не восстанавливают'):
            if w!='не восстанавливают':self.assertIn(w,a)
        self.assertIn('смешивает числитель full04 с активными датами full05',b);self.assertIn('дополнительное предположение интенсивности',b)
        self.assertIn('без наблюдённого бюджета GPU',b)
        self.assertAlmostEqual(24378/8122+(91214-24378)/5000,16.37,places=2);self.assertAlmostEqual(24378/8122+(91214-24378)/3000,25.28,places=2)
        self.assertAlmostEqual(91214/200/60,7.60,places=2);self.assertEqual(100000*34816,3481600000)

    # Network qualification is not inference qualification. Turn1's predeclared
    # vLLM quality refusal stays visible despite byte-identical server exports.
    def test_transport_and_vllm_gate_do_not_become_end_to_end_success(self):
        t=self.texts['90-appendix.tex'];main=self.texts['06-server.tex']
        transport=next(p for p in t.split('\n\n')if r'\textbf{Транспорт до сквозного опыта.}'in p)
        for w in ('1 из 6 строк','все 6 из 6','80\\%','0.941/0.908/0.878','0.918/0.881/0.843','без результата инференса'):self.assertIn(w,transport)
        self.assertIn('полный прогон ещё не выполнен',t)
        for w in ('KL 0.3286 нат','границе 0.03','проходящего свидетельства нет','vLLM в длинной сессии в работе'):self.assertIn(w,main)
        for w in ('0 из 112','2026-11-08 04:00 UTC','51/64 против требуемых 60/64','Предварительная проверка модели времени','\\le0.15','до первого варианта инференса'):self.assertIn(w,t)
        self.assertIn('ускорения длинной сессии этот опыт не показал',self.texts['14-conclusion.tex'])
        self.assertIn('парный сквозной запуск квантильной сессии',self.texts['13-outlook.tex'])
        self.assertNotIn('опыт уже проведён',t)

    # Old numerical claims keep their body conditions; new abstracts state only
    # the accepted full-Qwen basis, not unmeasured work success or GLM timings.
    def test_abstracts_have_current_economics_and_keep_budgets(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        for w in ('доле Qwen 100%','с 4 человек','с 2 при средней','тяжёлую клиент не вмещает','не дешевле самого дешёвого допущенного API','но ускорения не показала'):self.assertIn(w,ru)
        for w in ('100% Qwen scenario','from 4 people at light','2 at medium','heavy load exceeds client capacity','never costs less than the cheapest admitted API'):self.assertIn(w,en)
        self.assertNotIn('await calculation',en);self.assertNotIn('ожидают расчёта',ru)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        import history_evidence as history
        expected=set(history.snapshot_paths('ca7f228acd789380bf46016fd87acc33e1b07aef','calc/out'))|set(history.snapshot_paths('397432dd','calc/out/run25','calc/out/run26'))
        actual={str(p.relative_to(ROOT))for p in (ROOT/'calc/out').rglob('*')if p.is_file()}
        self.assertEqual(actual,expected)
        self.assertEqual(history.unchanged('397432dd','calc/out/run25','calc/out/run26'),'')

    # Every new documentary source is authenticated, including owner attribution
    # where the provided FACTS snapshot does not contain the tensor diagnostic.
    def test_source_custody_and_pending_registry_are_exact(self):
        for row in json.loads((D/'custody.json').read_text()):
            packed=(D/row['compressed']).read_bytes();raw=gzip.decompress(packed);self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);self.assertEqual(hashlib.sha256(packed).hexdigest(),row['compressed_sha256'])
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
