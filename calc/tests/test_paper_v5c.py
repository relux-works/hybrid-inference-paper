"""R23 publication boundaries: accepted rows and finite descriptive measurements."""
import csv,hashlib,json,re,subprocess,unittest
from pathlib import Path
from r13_audit import ROOT,module
D=ROOT/'data/measurements/paper-v5c-2026-11-04'
ENGINE='9064701a9a07bd2726f76cefb6a05aa6aa428c0d'

import history_evidence as history

def rows(name):
    with (ROOT/'calc/out/run23'/name).open(newline='') as f:return list(csv.DictReader(f))

class PaperV5cTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5c_offload',ROOT/'paper/data/offload_bound.py')
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}
        cls.sites={'v5c '+r['name']:r for r in json.loads((ROOT/'data/measurements/paper-v5d4-2026-11-05/v5c-sites-current.json').read_text())}
        # Analyst successors move only the named current publication locus.
        for k,r in cls.sites.items():
            r.update(zip(('file','marker','phrase'),cls.off.expected()[k]))

    def plant(self,key,old,new):
        r=self.sites[key];text=self.texts[r['file']]
        part=next(p for p in text.split('\n\n') if r['marker'] in p)
        self.assertIn(old,r['phrase']);changed,n=re.subn(r'\s+'.join(map(re.escape,r['phrase'].split())),lambda _:r['phrase'].replace(old,new,1),part,count=1)
        self.assertEqual(n,1);self.assertNotEqual(changed,part)
        return dict(self.texts,**{r['file']:text.replace(part,changed,1)})

    # Every new site has an actually applied omission; the clean current text
    # is the nearby valid control. CLI self-tests also require exact attribution.
    def test_all_new_sites_have_applied_named_omission_controls(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for k,r in self.sites.items():
            bad=self.plant(k,r['phrase'],'УДАЛЕНО')
            self.assertIn(k,self.off.missing(bad))
        self.assertEqual(self.off.missing(self.texts),[])

    # Exact engine custody includes input prose and schema-valid context refusals;
    # a published health status must never be promoted to a native measurement.
    def test_accepted_run23_and_prior_exports_are_byte_identical(self):
        paths=['calc/run23','calc/out/run23','calc/r23_report.py','calc/ENGINE-REPORT-R23-261104.md','calc/ENGINE-QUOTES-R23-261104.csv','calc/tests/test_run23.py','calc/tests/test_r23_report.py']
        self.assertEqual(history.unchanged(ENGINE,*paths,allow_ports=True),'')
        self.assertIn(ENGINE,history.manifest()['revisions'])
        for row in rows('mac_direct_measurements.csv'):
            self.assertEqual(row['cache_state'],'warm_no_purge');self.assertEqual(row['priority'],'normal_priority')
            self.assertEqual(row['raw_logit_bound'],'4.0');self.assertEqual(row['earlier_bound'],'1.0')
            if row['depth']=='1040000' and row['delta']=='10000':
                self.assertEqual(row['measurement_status'],'refused_context');self.assertEqual(row['prefill_s'],'')
            else:self.assertEqual(row['measurement_status'],'measured')

    # All measured Mac prefill/decode/restore cells quote their own depth. The
    # post-refusal bound4 is disclosed and cannot be called calibrated.
    def test_mac_cells_and_both_gate_attempts_keep_their_scope(self):
        text=self.texts['08-million.tex']
        self.assertIn('Граница 4.0 не калибрована',text)
        for depth,times,decode in [('524288',[48.255,161.768,843.260],3.8409),('1040000',[72.408,296.966],1.6638)]:
            rs=[r for r in rows('mac_direct_measurements.csv') if r['depth']==depth and r['measurement_status']=='measured']
            self.assertEqual([float(r['prefill_s']) for r in rs],times)
            self.assertTrue(all(float(r['decode_tok_s'])==decode for r in rs))
            for r in rs:self.assertIn(f"{float(r['prefill_s']):.3f}",text)
        for old,new in [('Граница 4.0 не калибрована','Граница 4.0 калибрована'),('границу 1.0','границу 4.0'),('превысил','не превысил')]:
            key='v5c Mac gate attempts';self.assertIn(key,self.off.missing(self.plant(key,old,new)))
        self.assertAlmostEqual((72.408/70.53-1)*100,2.7,places=1)

    # Wire/budget recomputation proves the four stated thresholds and the two
    # sensitivities, not delta-import portability or an end-to-end Mac run.
    def test_routing_thresholds_charge_one_labelled_full_slot_proxy(self):
        data=rows('link_thresholds.csv')
        for depth,fmt,want in [('1000000','bf16',3.351),('1000000','f32',5.916),('1040000','bf16',3.356),('1040000','f32',5.925)]:
            rs=[r for r in data if all(r[k]==v for k,v in dict(client='m3max',server='b300_fp8_kv',depth=depth,delta='690',transport=fmt,link='historical_home_wifi',primary='True').items())]
            self.assertEqual(len(rs),1);r=rs[0]
            self.assertEqual(r['measurement_depth'],'1040000');self.assertEqual(r['recovery_kind'],'full_slot_restore_proxy')
            self.assertEqual(float(r['import_s']),40.479);self.assertEqual(float(r['local_prefill_s']),72.408)
            self.assertAlmostEqual(float(r['wire_bytes'])/float(r['budget_s'])/1e6,want,places=3)
        for fmt,want in [('bf16',1.311),('f32',2.314)]:
            rs=[r for r in data if all(r[k]==v for k,v in dict(client='m3max',server='b300_fp8_kv',depth='1000000',delta='690',transport=fmt,link='historical_home_wifi').items()) and r['rate_basis'].startswith('analyst earlier120s')]
            self.assertEqual(len(rs),1);self.assertEqual(rs[0]['primary'],'False');self.assertAlmostEqual(float(rs[0]['threshold_MB_s']),want,places=3)

    # Source points, intermediate assumptions and the B300 model remain distinct.
    # This does not certify deep B300 decoding or a different resident batch.
    def test_server_surface_and_model_boundaries_are_not_interchanged(self):
        data=rows('server_decode_measured.csv');text=self.texts['06-server.tex']
        for depth,count,gain in [('16384','39',15.15),('65536','12',5.07),('164000','5',2.21),('256000','3',1.75)]:
            r=next(r for r in data if r['depth']==depth and r['streams']==count)
            self.assertAlmostEqual(float(r['gain']),gain,places=2)
            self.assertIn(f"{depth} & {count}",text)
        self.assertIn('Промежуточные координаты остаются расчётом',text)
        self.assertIn('Пакет vLLM B300 остаётся модельным',text)
        key='v5c PRO decode interpolation'
        self.assertIn(key,self.off.missing(self.plant(key,'остаётся модельным','измерен')))
        b=[r for r in rows('decode_scaling.csv') if r['server'].startswith('b300')]
        self.assertTrue(b);self.assertTrue(all('modelled' in r['basis'] for r in b))

    # The PRO capacity refusal is finite and independent of the llama.cpp slot
    # builder. A plausible transfer price cannot turn no-fit into a remote path.
    def test_pro_million_refusal_is_not_hidden_by_the_slot_builder(self):
        self.assertIn('требует 61.97~ГиБ KV',self.texts['08-million.tex'])
        data=[r for r in rows('link_thresholds.csv') if r['server']=='pro6000_fp8' and int(r['depth'])>=1000000]
        self.assertTrue(data);self.assertTrue(all(r['feasible']=='False' and r['threshold_MB_s']=='' and r['remote_s']=='' for r in data))
        key='v5c PRO million refusal'
        self.assertIn(key,self.off.missing(self.plant(key,'61.97','51.97')))

    # Same-device exactness is descriptive, with all partition controls printed;
    # it is never a network, cross-device or unmeasured-depth equivalence claim.
    def test_depth_quality_retains_five_exact_cases_and_partition_controls(self):
        text=self.texts['11-limitations.tex'];self.assertIn('на одной GPU, без сети',text);facts=(D/'FACTS-excerpts.md').read_text()
        for x in ('0.0285748','0.0037251','0.0082421','0.0101671','0.0077366'):
            self.assertIn(x,text);self.assertIn(x,facts)
        key='v5c depth quality exactness'
        for old,new in [('на одной GPU, без сети','на разных устройствах через сеть'),('пяти случаях','всех глубинах'),('вывод об эквивалентности за этими случаями не делается','эквивалентность установлена для всех глубин')]:
            self.assertIn(key,self.off.missing(self.plant(key,old,new)))

    # Coordinate changes preserve the unchanged bought-office headlines. The
    # rental Claude crossing still discloses local-only, zero-offload economics.
    def test_change_ledger_and_claude_crossing_remain_conditioned(self):
        changes=rows('abstract_bound_changes.csv');self.assertEqual(len(changes),377)
        self.assertEqual(sum(r['changed']=='True' for r in changes),39)
        r=next(r for r in changes if r['table']=='team_break_even' and r['old_row']=='4330' and r['column']=='statement')
        self.assertIn('87',r['old']);self.assertIn('73',r['new'])
        text=self.texts['07-economics.tex'];self.assertIn('10.12/2.33',text);self.assertNotIn('10.13/2.33',text);self.assertIn('сдвинулось с 87 до 73',text);self.assertIn('Доля оффлоада остаётся нулевой',text)
        self.assertNotIn('требует нового расчёта',self.texts['14-conclusion.tex'])

    # Completed measurements leave no corresponding pending macro. Provider
    # economic use and stopped RULER64/128 remain pending; completed studies do not.
    def test_pending_abstract_and_review_note_contracts(self):
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        inventory=json.loads((ROOT/'calc/tests/data/paper-v5d4-pending.json').read_text())
        self.assertFalse(any('импорт, проверка логитов' in r['body'] for r in inventory))
        for x in ('64 и 128','bf16'):self.assertIn(x,' '.join(r['body'] for r in inventory))
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLess(len(en),1800)
        # The analyst keeps the deep-result clause in the body, outside both abstracts.
        self.assertIn('пяти случаях',self.texts['11-limitations.tex']);self.assertIn('На одной GPU',self.texts['11-limitations.tex'])
        self.assertIn('20 documents',en)
        self.assertNotIn(';\nЭти',self.texts['07-economics.tex'])
        self.assertIn('Строка с несовпавшим поставщиком',self.texts['07-economics.tex'])

    # Evidence custody is separate from the generated current publication pins.
    def test_v5c_sources_have_explicit_hash_custody(self):
        readme=(D/'README.md').read_text()
        for p in D.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
