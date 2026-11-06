"""Post-review factual boundaries and independent model-byte/resource arithmetic."""
import csv,gzip,hashlib,json,re,unittest
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d9-2026-11-05'
class PaperV5d9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d9_off',ROOT/'paper/data/offload_bound.py');cls.texts={p.name:p.read_text()for p in cls.off.SECTIONS.glob('*.tex')}
    # All new/superseded prose predicates must reject applied, finite omissions.
    def test_each_current_boundary_rejects_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        keys=list(json.loads((D/'successors.json').read_text()))+['v5d9 '+r['name']for r in json.loads((D/'sites.json').read_text())]
        for k in keys:
            f,m,w=self.off.expected()[k];t=self.texts[f];p=next(p for p in t.split('\n\n')if m in p)
            bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'ПОДМЕНЕНО',p,count=1);self.assertEqual(n,1,k)
            self.assertIn(k,self.off.missing(dict(self.texts,**{f:t.replace(p,bad,1)})),k)
    # Identical Metal partitions do not calibrate the cancelled1M depth or undo
    # the historical refusal/post-hoc bound. Cross-device noise is identified.
    def test_partial_calibration_preserves_refusal_and_cancelled_depth(self):
        t=self.texts['08-million.tex'];a=self.texts['90-appendix.tex']
        for w in ('превысил границу 1.0','После отказа границу подняли до 4.0','Граница 4.0 не калибрована','шум равен 0','CUDA против Metal воспроизвела исторические 1.08298','среднем KL 0.000329','максимальном KL 0.001754','top-1 64/64','Калибровка не завершена','владелец отменил продолжение','разность 3.01402 остаётся необъяснённой'):self.assertIn(w,t)
        self.assertNotRegex(t,r'повтор (?:с 4\.0 )?прош[её]л')
        for w in ('B(524288)=0','0.000399 / 0.002281','не относятся к свободной машине','Калибровка частичная'):self.assertIn(w,a)
        raw=gzip.decompress((D/'facts-calibration.md.gz').read_bytes()).decode();self.assertIn('| 1.08298 | 0.000329 | 0.001754 | 64/64 |',raw);self.assertIn('1,040,000 never started',raw)
    # Exact transport/codec/append controls cannot become quality qualification;
    # failure persists with full-server prefix and beyond the first five positions.
    def test_vllm_exact_mechanics_do_not_clear_quality_gate(self):
        t=next(p for p in self.texts['90-appendix.tex'].split('\n\n')if r'\textbf{Узел vLLM для длинной сессии.}'in p)
        for w in ('0 из 112','Преобразование NumPy совпало побайтово','добавление к серверному префиксу совпало с полным серверным импортом','0.2649 и top-1 53/64','0.3286 и 51/64','0.0017 и 64/64','Все варианты передачи отказали неизменному допуску','оставшиеся 59 позиций','средний KL 0.320','прежнюю локализацию дефекта в append','Длинная сессия vLLM не квалифицирована','одноформатный путь llama.cpp остаётся квалифицированным','Это один документ, диагностическая проверка, без квалификации длинной сессии'):self.assertIn(w,t)
        for w in ('хвосты 356 / 662 вместо 1','8196 / 32806 вместо 22385','учителя из генерации гибрида вместо фиксированных',r'\mathrm{KL}(H\|L)',r'\mathrm{KL}(L\|H)'):self.assertIn(w,t)
        self.assertNotIn('Различие локализовано после экспорта, на пути добавочного импорта',t)
        self.assertIn('всеобщую невозможность',t)
    # One natural-text document narrows workload-specific failure but does not
    # qualify the full session; full-server still refuses the unchanged top1.
    def test_natural_text_is_one_document_not_long_session_qualification(self):
        t=next(p for p in self.texts['90-appendix.tex'].split('\n\n')if r'\textbf{Узел vLLM для длинной сессии.}'in p)
        for w in ('Pride and Prejudice','0.00651, избыток 0.00558, top-1 60/64','0.0085, избыток 0.00757, top-1 58/64','отказ только по top-1','0.00093 и top-1 62/64','один документ, диагностическая проверка, без квалификации длинной сессии','повторяющемуся синтетическому промпту','проходящего свидетельства длинной сессии нет'):self.assertIn(w,t)
        raw=gzip.decompress((D/'facts-vllm.md.gz').read_bytes()).decode();self.assertIn('Muse r5x15 ACCEPT',raw);self.assertIn('qualified=false',raw);self.assertIn('0.00651',raw)
    # The committed pre-probe numbers are forecasts; actual-probe commitment and
    # inference remain separate. Total15% does not mean active-time15%.
    def test_preprobe_forecast_is_not_result_or_final_commitment(self):
        t=next(p for p in self.texts['90-appendix.tex'].split('\n\n')if r'\textbf{Предварительная проверка модели времени.}'in p)
        for w in ('Подписан предварительный численный прогноз до проверки канала','13\\,084.935','11\\,992.112 / 11\\,882.400 / 11\\,790.457','15 / 20 / 28','RTT 80','3353.665','без результата запуска','второе подписанное численное обязательство','ошибки активного времени и фаз','\\le0.15'):self.assertIn(w,t)
        self.assertAlmostEqual(13084.935/3600,3.63,places=2)
        for total in (11992.112,11882.400,11790.457):self.assertTrue(.20<.15*total/(total-3353.665)<.22)
        self.assertIn('полный прогон ещё не выполнен',t)
    # The save-size envelope already includes SWA; four exchanges must charge
    # four live windows, independently of the measured slot's per-token ratio.
    def test_architecture_bytes_and_four_windows_match_native_geometry(self):
        with(ROOT/'calc/out/run17/architectures/sliding_geometry.csv').open()as f:r=next(x for x in csv.DictReader(f)if x['model']=='glimmer30')
        self.assertEqual((int(r['full_kv_bytes_token']),int(r['window_bytes']),int(r['recurrent_bytes'])),(7072,43450368,0))
        a=json.loads((D/'arithmetic.json').read_text());self.assertEqual(a['qwen_bytes'],100000*34816+4*78446592);self.assertEqual(a['glimmer_bytes'],100000*7072+4*43450368)
        self.assertEqual(a['qwen_bytes'],3795386368);self.assertEqual(a['glimmer_bytes'],881001472)
        self.assertEqual((13*544,39*2048*544),(7072,43450368))
        t=self.texts['91-calculation-history.tex']
        for w in ('отношение уже включает живое скользящее окно','не является приростом сетевого объёма','4\\times43450368=881001472','без повторов, обрамления и подготовки'):self.assertIn(w,t)
        self.assertIn('Различие задаёт архитектура модели',self.texts['02-workload.tex'])
    # Time/volume are arithmetic without RTT/fees. Daily link capacity at0.9GB
    # must be12000, never11000; the conservative1GB point is distinct.
    def test_transfer_and_metering_arithmetic_has_correct_daily_denominators(self):
        a=json.loads((D/'arithmetic.json').read_text())
        for rate in (125,20,5):
            for model in ('qwen','glimmer'):self.assertAlmostEqual(a['traffic_seconds'][str(rate)][model],a[model+'_bytes']/rate/1e6)
        self.assertEqual(a['link_contexts_day']['glimmer_rounded_point9'],12000);self.assertEqual(a['link_contexts_day']['glimmer_conservative1'],10800)
        t=self.texts['91-calculation-history.tex'];main=self.texts['02-workload.tex']
        for w in ('30.4 & 7.0','189.8 & 44.1','759.1 & 176.2','37.95 & 8.81','При округлённых 0.9~ГБ это 12\\,000, при 1~ГБ 10\\,800'):self.assertIn(w,t)
        for w in ('Десять таких начал в день','при оплате трафика объём входит и в цену','Сетевого измерения этих сумм нет'):self.assertIn(w,main)
    # GPU-only capacity is conditional on qualified vLLM and uniform arrivals;
    # Glimmer uses its own llama.cpp rates, not unmeasured vLLM rates.
    def test_start_capacity_keeps_component_and_arrival_limits(self):
        a=json.loads((D/'arithmetic.json').read_text());self.assertAlmostEqual(a['gpu_seconds'],24000/7100+35000/5400+20000/4300+12000/4000)
        self.assertAlmostEqual(a['glimmer_gpu_seconds'],24.83,places=2);self.assertEqual(86400/18,4800);self.assertAlmostEqual(.7*4800,3360)
        t=self.texts['91-calculation-history.tex'];main=self.texts['02-workload.tex']
        for w in ('7144 / 4598 / 3130','5377 / 4264 / 4042','общий префикс 9624 считается один раз','17.51','условии квалификации полного пути','4221 / 3712 / 3126','vLLM для Glimmer не измерена','реальные дни имеют пики','без наблюдённой частоты'):self.assertIn(w,t)
        for w in ('при полной занятости и 3400 при 70','минимум вычисления и передачи','длинная сессия vLLM остаётся неквалифицированной'):self.assertIn(w,main)
    # Archived source bytes and pending macros are complete; README distinguishes
    # real snapshot whitespace diagnostics from content-delta checks.
    def test_custody_pending_and_whitespace_disclosure_are_exact(self):
        for row in json.loads((D/'custody.json').read_text()):
            packed=(D/row['compressed']).read_bytes();raw=gzip.decompress(packed);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(packed).hexdigest(),row['compressed_sha256'])
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme)
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        root=(ROOT/'README.md').read_text();self.assertIn('exits 2 on five byte-identical accepted run26',root);self.assertNotIn('No paper/code/output whitespace exemption applies.',root)
