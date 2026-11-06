"""Completed RULER transcription and frozen-claim limits, without redoing statistics."""
import gzip,hashlib,json,re,unittest
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5d11-2026-11-06'
def snapshot(name):return json.loads(gzip.decompress((D/(name+'.json.gz')).read_bytes()))
class PaperV5d11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5d11_off',ROOT/'paper/data/offload_bound.py');cls.texts={p.name:p.read_text()for p in cls.off.SECTIONS.glob('*.tex')};cls.qwen=snapshot('qwen');cls.bf16=snapshot('qwen-bf16')
    def paragraph(self,file,marker):
        parts=[p for p in self.texts[file].split('\n\n')if marker in p];self.assertEqual(len(parts),1,marker);return parts[0]
    # Every resolved/new predicate must reject a real omission at its current locus.
    def test_finite_successors_and_results_reject_omission(self):
        self.assertEqual(self.off.missing(self.texts),[])
        keys=list(json.loads((D/'successors.json').read_text()))+['v5d11 '+r['name']for r in json.loads((D/'sites.json').read_text())]
        for k in keys:
            f,m,w=self.off.expected()[k];p=self.paragraph(f,m);bad,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'УДАЛЕНО',p,count=1)
            self.assertEqual(n,1,k);self.assertIn(k,self.off.missing(dict(self.texts,**{f:self.texts[f].replace(p,bad,1)})),k)
    # The full390 population replaces225 early needles, never a relabelled prefix.
    # Scores/text counts reproduce independent committed frozen-tool output.
    def test_128k_full_descriptives_match_frozen_output(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Qwen RULER на 128 тысячах, полный сбор.}')
        r=next(x for x in self.qwen['secondary']if x['depth']==131072 and x['task']=='ALL')
        self.assertEqual(r['n'],390);self.assertEqual((r['offload_changed'],r['partition_changed']),(32,27))
        for w in ('390/390 пар','95.81 / 95.90 / 95.90','32/390','27/390','13/8','0.3833','[-2.69,+5.21]','373 / 374 / 374','05:56:57'):self.assertIn(w,t)
        self.assertAlmostEqual(100*r['excess'],1.28,places=2);self.assertAlmostEqual(r['mcnemar_p'],.3833,places=4)
        self.assertFalse(r['equivalent_at_margin']);self.assertIn('Эквивалентность текста',t)
        for arm in ('local','offload','local_partition'):self.assertIn(f'{100*r["score_means"][arm]:.2f}',t)
    # Both arm families carry separate registered and supplementary Holm numbers;
    # no p=1 placeholders remain in the completed f32 analysis.
    def test_four_depth_holm_table_matches_both_arm_families(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Холм по четырём завершённым глубинам Qwen.}')
        rows=re.findall(r'(?m)^(8|32|64|128) & (Оффлоад|Другая разбивка) & ([\d.]+) & ([\d.]+) & (.+?) \\\\',t)
        self.assertEqual(len(rows),8)
        labels={'Оффлоад':'offload-local','Другая разбивка':'local_partition-local'};depths={8:8192,32:32768,64:65536,128:131072}
        for d,p,reg,claim,v in rows:
            r=next(x for x in self.qwen['primary']if x['depth']==depths[int(d)]and x['pair']==labels[p])
            self.assertEqual(float(reg),round(r['holm_p'],4));self.assertEqual(float(claim),round(r['claim_holm_p'],4))
            self.assertEqual('не установлено'not in v,r['equivalent_holm']);self.assertEqual(r['pending_depths'],[]);self.assertFalse(r['family_incomplete']);self.assertEqual(r['n'],390)
    # A passing registered128k interval cannot bypass the already frozen guard;
    # binary sidecar alone is insufficient and neither pair gets a claim.
    def test_128k_registered_pass_does_not_override_frozen_guard(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{128 тысяч: интервал и замороженный допуск.}')
        for w in ('[-0.6838,+0.8547]','[-2.2429,+2.2429]','[-1.0493,+1.6307]','правило требует оба','0.0482095, выше 0.025','эквивалентность на 128 тысячах не установлена','Общего утверждения об эквивалентности на всех четырёх глубинах нет','Эквивалентность текста при 2 п.п. не установлена'):self.assertIn(w,t)
        for r in self.qwen['primary']:
            if r['depth']!=131072:continue
            self.assertTrue(r['registered_interval_inside_margin']);self.assertLess(r['holm_p'],.025);self.assertFalse(r['equivalent_holm']);self.assertGreater(r['claim_holm_p'],.025)
            self.assertGreater(100*r['sidecars']['exact_unseen_departures']['interval95'][1],2);self.assertTrue(r['sidecars']['fully_correct_newcombe']['equivalent_unadjusted'])
    # Post-observation margin, straddling bound, host identity and post-cutoff
    # completions are all disclosed; zero-or-one is not asserted to equal one.
    def test_registration_and_host_custody_preserve_four_disclosures(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Сбор и регистрация глубины 128 тысяч.}');criterion=self.paragraph('11-limitations.tex',r'\textbf{Зарегистрированный критерий.}')
        for w in ('после получения результатов Qwen на 8 и 32','Сбор 64 тысяч начался после регистрации','сбор 128 тысяч пересёк регистрацию','не является подтверждающим'):self.assertIn(w,criterion)
        for w in ('14:29:06','14:36','не более чем одна строка','ноль или один','строки 1--226','227--390','бинарными файлами B','парность сохраняется внутри примера','Все 225 строк и манифест','неизменные 226 строк и весь манифест','Оба завершения, 64 и 128 тысяч','после исходного среза RC4 2026-11-05 12:00'):self.assertIn(w,t)
        self.assertNotIn('Строго предварительно зарегистрированы только глубины Qwen 64 и 128',criterion)
    # Zero bootstrap intervals cannot certify8k; both observed sidecars must
    # support the claim. Text equivalence remains false at every observed depth.
    def test_8k_sidecars_and_all_depth_text_limits_remain_explicit(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Холм по четырём завершённым глубинам Qwen.}')
        for w in ('bootstrap вырожден','не служат основанием эквивалентности','[-0.9414,+0.9414]','[-1.0387,+1.0387]','Оба интервала входят','0.0095531'):self.assertIn(w,t)
        for r in self.qwen['primary']:
            if r['depth']==8192:self.assertTrue(r['degenerate']);self.assertEqual(len(r['sidecars']),2);self.assertTrue(all(x['equivalent_unadjusted']for x in r['sidecars'].values()))
        rows=[r for r in self.qwen['secondary']if r['task']=='ALL'];self.assertEqual(len(rows),4);self.assertTrue(all(not r['equivalent_at_margin']for r in rows))
    # bf16 covers exactly two observed depths and two pairs; absent higher
    # depths stay p1 upper bounds, never described as measured or equivalent.
    def test_bf16_results_do_not_extend_to_unmeasured_depths(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Зарегистрированный анализ bf16.}')
        for w in ('bf16 к локальному и bf16 к f32-оффлоаду','по 390 совпавших оценок','0.0076683','0.0095531','На 64 и 128 тысячах bf16 никогда не измерялся','с $p=1$','верхними границами','Ни одно четырёхглубинное семейство bf16 не завершено'):self.assertIn(w,t)
        rs=[r for r in self.bf16['primary']if r['pair'].startswith('bf16-')];self.assertEqual(len(rs),4)
        self.assertEqual({r['depth']for r in rs},{8192,32768})
        for r in rs:self.assertEqual(r['n'],390);self.assertEqual(r['difference'],0);self.assertTrue(r['equivalent_holm']);self.assertTrue(r['family_incomplete']);self.assertEqual(r['pending_depths'],[65536,131072]);self.assertTrue(r['holm_p_is_upper_bound']);self.assertAlmostEqual(r['claim_holm_p'],.00955311695)
        p=snapshot('bf16-input-provenance')
        for family in p['families'].values():
            for r in family:
                if r['depth']in(65536,131072):self.assertFalse(r['measured']);self.assertEqual(r['registered_holm_input'],1);self.assertEqual(r['claim_holm_input'],1)
    # Timing bounds cannot become measured timestamps or a confirmatory8k label;
    # the adapter changes arm naming/provenance without changing statistical code.
    def test_bf16_adapter_and_timing_have_bounded_scope(self):
        t=self.paragraph('11-limitations.tex',r'\textbf{Время и входы анализа bf16.}')
        for w in ('меняет только имя варианта','Статистический код сохранён','начало неизвестно','сбор мог начаться после регистрации или пересечь регистрацию','не является подтверждающей','начался не ранее 15:14:06','не означает неполного варианта'):self.assertIn(w,t)
        rs=[r for r in self.bf16['primary']if r['pair'].startswith('bf16-')]
        for r in rs:self.assertEqual(r['registration_timing']['timing'],'unknown'if r['depth']==8192 else'after')
    # Summaries must include64k support and128k non-claim; the other14 pending
    # bodies are exact copies of the prior inventory, not silently resolved.
    def test_summaries_and_unrelated_pending_are_preserved(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip();c=self.texts['14-conclusion.tex']
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        for w in ('оценки RULER для f32','на 8, 32 и 64 тысячах','на 128 тысячах эквивалентность не установлена','95.90% против 95.81%','граница выбрана после результатов 8 и 32'):self.assertIn(w,ru)
        for w in ('RULER f32 scores','at 8k/32k/64k','at 128k equivalence is not established','95.90% versus 95.81%'):self.assertIn(w,en)
        for w in ('на 8, 32 и 64 тысячах','на 128 тысячах вывод','не установлен','95.90','95.81','общего четырёхглубинного вывода нет'):self.assertIn(w,c)
        prior=json.loads((ROOT/'calc/tests/data/paper-v5d10-pending.json').read_text());now=json.loads((ROOT/'calc/tests/data/paper-v5d11-pending.json').read_text())
        filtered=[(r['file'],r['body'])for r in prior if not(r['body'].startswith('полные 390 пар и первичный анализ')or r['body'].startswith('Qwen RULER 128 тысяч:'))]
        self.assertEqual([(r['file'],r['body'])for r in now],filtered);self.assertEqual(len(now),14);self.assertEqual(self.off.pending_gaps(self.texts),[])
    # Current data boundary includes the three late completions, while the
    # superseded serial-prefix arithmetic and source custody remain intact.
    def test_cutoff_archive_fence_and_snapshot_custody_are_exact(self):
        t=self.paragraph('90-appendix.tex','Предельный срез данных этого выпуска')
        for w in ('2026-11-06 06:00 UTC','первоначального среза 2026-11-05 12:00 UTC','RULER 64 и 128 тысяч и пятая попытка vLLM','05:56:57'):self.assertIn(w,t)
        archive=self.paragraph('91-calculation-history.tex',r'\subsection{Архив неполной RULER до возобновления}')
        for w in ('заменённый сохранённый срез','архив не служит текущим вердиктом','В прежнем первичном анализе','полный анализ заменяет этот снимок'):self.assertIn(w,archive)
        readme=(D/'README.md').read_text()
        for row in json.loads((D/'custody.json').read_text()):
            packed=(D/row['compressed']).read_bytes();raw=gzip.decompress(packed);self.assertEqual(len(raw),row['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);self.assertEqual(hashlib.sha256(packed).hexdigest(),row['compressed_sha256'])
        for p in D.iterdir():
            if p.is_file()and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme)
        self.assertEqual(self.qwen['analysis_sha256'],self.bf16['analysis_sha256'])
    # Resolved RULER/cutoff plants must not normalize unrelated multiline pending
    # bodies and invent an inventory verdict. Actual pending-content changes still fail.
    def test_resolved_locus_plants_preserve_unrelated_pending_signatures(self):
        for name in ('v5d11 four depth completion status','v5d11 release cutoff'):
            f,m,w=self.off.expected()[name];p=self.paragraph(f,m);self.assertNotIn(r'\pending{',p)
            match=re.search(r'\d',w);self.assertIsNotNone(match);bad=w[:match.start()]+str((int(match[0])+1)%10)+w[match.end():]
            changed,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:bad,p,count=1);self.assertEqual(n,1)
            planted=self.texts[f].replace(p,changed,1);bodies=lambda t:re.findall(r'\\pending\{([^{}]*)\}',t,re.S)
            self.assertEqual(bodies(self.texts[f]),bodies(planted));gaps=self.off.missing(dict(self.texts,**{f:planted}));self.assertIn(name,gaps);self.assertNotIn('v4b pending inventory',gaps)
        f='90-appendix.tex';p=self.texts[f];old='калибровка гетерогенного допуска CUDA и Metal';self.assertEqual(p.count(old),1)
        changed=p.replace(old,'отмена гетерогенного допуска CUDA и Metal',1)
        self.assertIn('v4b pending inventory',self.off.missing(dict(self.texts,**{f:changed})))

    # Score support, post-observation margin and128k non-claim are independent
    # assertions: omission of one must report its own diagnostic only.
    def test_abstract_quality_contracts_have_independent_diagnostics(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for name in ('v5a2 abstract score basis','rc3 review2 abstract paired plan','v5d11 abstract 128k nonclaim'):
            f,m,w=self.off.expected()[name];p=self.paragraph(f,m)
            changed,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:'УДАЛЕНО',p,count=1)
            self.assertEqual(n,1,name)
            self.assertEqual(self.off.missing(dict(self.texts,**{f:self.texts[f].replace(p,changed,1)})),[name])

    # Accepted 8dd0577b identifies one partial fwe and two full qa_2 departures
    # in both 128k pairs. A task/index/sign substitution must not retain the claim.
    def test_128k_departure_identities_match_accepted_analysis(self):
        d=ROOT/'data/measurements/paper-v5d12-2026-11-06'
        metadata=(d/'departures.json').read_bytes()
        self.assertEqual(hashlib.sha256(metadata).hexdigest(),'342d2e1f25a8af3e695e133b8dd8fab1bbc76229f921bc430a6c6ebb82fd888e')
        r=json.loads(metadata);raw=gzip.decompress((d/'accepted-analysis.md.gz').read_bytes())
        self.assertEqual(r['revision'],'8dd0577b2df18685c54095b0bab22e882ac19eb8')
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'550feaf7c70a3c2b52f4cf7c2d39e03b9132ae9ab604d11b8437cf311e21940f')
        self.assertEqual(r['source_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(r['source_bytes'],len(raw));self.assertEqual(r['blob'],hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        paragraph=r['source_paragraph'];self.assertIn(paragraph,raw.decode())
        identities=re.findall(r'(fwe|qa_2) index (\d+) \(([+-](?:\d/\d|\d)); local ([0-9/]+) versus the other arm ([0-9/]+)\)',paragraph)
        self.assertEqual(identities,[('fwe','12','+1/3','2/3','1'),('qa_2','13','+1','0','1'),('qa_2','14','-1','1','0')])
        self.assertIn('identical for offload-local and partition-local',paragraph)
        self.assertEqual(r['pairs'],['offload-local','local_partition-local']);self.assertEqual(r['remaining_pairs'],388)
        self.assertEqual([(x['task'],str(x['index']),x['difference'],x['local'],x['other'])for x in r['departures']],identities)
        t=self.paragraph('11-limitations.tex',r'\textbf{128 тысяч: интервал и замороженный допуск.}')
        self.assertIn('Три расхождения среди остальных 388 одинаковы в обеих парах:',t)
        for task,index,difference,_,_ in identities:
            expected=r'\texttt{'+task.replace('_',r'\_')+r'} \#'+index+' ($'+difference+'$)'
            self.assertIn(expected,t)
        self.assertNotIn('три частичных',t)
        actual=re.findall(r'\\texttt\{(fwe|qa\\_2)\} \\#(\d+) \(\$([+-](?:\d/\d|\d))\$\)',t)
        self.assertEqual([(task.replace(r'\_', '_'),index,delta)for task,index,delta in actual],[(task,index,delta)for task,index,delta,_,_ in identities])
