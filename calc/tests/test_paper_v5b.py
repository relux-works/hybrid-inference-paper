"""Accepted run22 economics: finite row-bound publication claims, not hardware tests."""
import csv
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from r13_audit import ROOT,module

SOURCE=ROOT/'data/measurements/paper-v5b-2026-11-03'
ENGINE='9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0'


import history_evidence as history

def rows(name):
    with (ROOT/'calc/out/run23'/name).open(newline='') as f:return list(csv.DictReader(f))


def select(name,**kw):
    found=[r for r in rows(name) if all(r.get(k)==str(v) for k,v in kw.items())]
    assert len(found)==1,(name,kw,len(found))
    return found[0]


P=dict(profile='existing_combined',scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8',billing='bought')


class PaperV5bTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.off=module('v5b_offload',ROOT/'paper/data/offload_bound.py')
        from v5b_economics import expected
        cls.expected={k:v for k,v in cls.off.expected().items() if k.startswith('v5b ')}
        cls.texts={p.name:p.read_text() for p in cls.off.SECTIONS.glob('*.tex')}

    def plant(self,key,old,new):
        file,marker,phrase=self.expected[key]
        self.assertIn(old,phrase,key)
        part=next(p for p in self.texts[file].split('\n\n') if marker in p)
        changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:phrase.replace(old,new,1),part,count=1)
        self.assertEqual(n,1,key);self.assertNotEqual(changed,part,key)
        return dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})

    # Each new site has an applied omission control; the CLI self-test proves
    # independent first-digit attribution without hiding another failed site.
    def test_every_new_economic_site_has_named_omission_control(self):
        self.assertEqual(self.off.missing(self.texts),[])
        for name,(file,marker,phrase) in self.expected.items():
            part=next(p for p in self.texts[file].split('\n\n') if marker in p)
            changed,n=re.subn(r'\s+'.join(map(re.escape,phrase.split())),lambda _:'УДАЛЕНО',part,count=1)
            self.assertEqual(n,1,name)
            self.assertIn(name,self.off.missing(dict(self.texts,**{file:self.texts[file].replace(part,changed,1)})))

    # Accepted engine bytes include all original source excerpts. This keeps
    # their exact provenance while permitting paper-only wording migrations.
    def test_accepted_engine_bytes_and_all26_dispositions(self):
        self.assertEqual(history.unchanged(ENGINE,'calc/out/run22','calc/run22','calc/hybridcalc',allow_ports=True),'')
        self.assertIn(ENGINE,history.manifest()['revisions'])
        import v5b_economics as econ
        mapping=json.loads((SOURCE/'r20-migration.json').read_text())
        old=json.loads((ROOT/'calc/tests/data/paper-v5a-r20-sites.json').read_text())
        self.assertEqual([r['old'] for r in mapping],old);self.assertEqual(len(mapping),26)
        self.assertEqual(econ.migration_gaps(self.texts),[])
        # Narrowing plant changes one authority field via the real JSON read.
        read=Path.read_text
        def bad_source(path,*a,**kw):
            text=read(path,*a,**kw)
            return text.replace(ENGINE,'b6ac5abc',1) if path==SOURCE/'r20-migration.json' else text
        with patch.object(Path,'read_text',bad_source):
            self.assertEqual(econ.migration_gaps(self.texts),['v5a R20 deferred inventory'])
        self.assertEqual(econ.migration_gaps(self.texts),[])

    # Every primary cost row carries occupancy for both compared fleets. These
    # exact source rows are conditional selected-call calculations, not prices
    # measured at a provider or SM-utilization measurements.
    def test_primary_costs_and_occupancy_recompute_from_rows(self):
        text=self.texts['07-economics.tex']
        for load,label in [('light','Лёгкая'),('medium','Средняя'),('heavy','Тяжёлая')]:
            r=select('paper/main_economics.csv',**dict(P,load=load,team=50))
            self.assertAlmostEqual(float(r['person_month']),4*614.0575/50+2.52+5)
            self.assertEqual(r['boxes'],'4');self.assertEqual(r['device_month'],'0')
            vals=[float(r[k])*s for k,s in [('person_month',1),('service_utilization',100),('calendar_utilization',100),('own_cluster_person_month',1),('own_service_utilization',100),('own_calendar_utilization',100)]]
            self.assertIn(label+' & '+' & '.join(f'{v:.2f}' for v in vals)+r' \\',text)
            self.assertAlmostEqual(float(r['calendar_utilization'])/float(r['service_utilization']),21*8/730)
        self.assertNotIn('m3max',{r['client'] for r in rows('paper/main_economics.csv')})
        self.assertIn('Строк экономики M3 Max нет',text)
        key=next(k for k in self.expected if k.startswith('v5b r22-dedicated50 row'))
        file,_,phrase=self.expected[key];bad=text.replace(phrase,phrase.replace('3.61','70.00'),1)
        self.assertNotEqual(bad,text);self.assertIn(key,self.off.missing(dict(self.texts,**{file:bad})))

    # Crossings must remain sustained through500 and keep server/billing,
    # client ownership and cache-point coordinates; absent is not zero people.
    def test_crossings_and_bought_mac_are_the_accepted_coordinates(self):
        for billing in ('bought','rented'):
            for load,want in [('light','nan'),('medium','5'),('heavy','2')]:
                r=select('paper/team_break_even.csv',**dict(P,billing=billing,load=load,reference='own_cluster'))
                self.assertEqual(r['from_people'],want);self.assertEqual(r['scan_max'],'500')
            for load in ('light','medium','heavy'):
                med=select('paper/team_break_even.csv',**dict(P,billing=billing,load=load,reference='api_median_owner_981'))
                self.assertEqual(med['from_people'],'45' if load=='heavy' and billing=='bought' else 'nan')
                low=select('paper/team_break_even.csv',**dict(P,billing=billing,load=load,reference='api_cheapest_owner_981'))
                self.assertEqual(low['from_people'],'nan')
        self.assertEqual(select('paper/team_break_even.csv',**dict(P,load='heavy',reference='api_cheapest_no_cache'))['from_people'],'74')
        self.assertEqual(select('paper/team_break_even.csv',**dict(P,load='medium',basis='new',reference='own_cluster'))['from_people'],'34')
        old=select('paper/main_economics.csv',**dict(P,load='heavy',team=50));new=select('paper/main_economics.csv',**dict(P,load='heavy',team=50,basis='new'))
        self.assertAlmostEqual(float(new['person_month'])-float(old['person_month']),69.05,places=2)
        self.assertAlmostEqual(30000*.8/48+30000*.02/12+.9*1.3*730*.5*.15,float(old['unit_month']))
        key='v5b bought Mac';f,_,phrase=self.expected[key]
        self.assertIn(key,self.off.missing(self.plant(key,'34','5')))

    # Dedicated/shared contrasts retain their utilization/tariff qualifications;
    # the superseded run21 pair is an executable negative witness.
    def test_price_of_idleness_and_shared_full_utilization_limit(self):
        for load,dedicated,shared in [('light',.088,.313),('medium',.351,.934),('heavy',1.097,1.701)]:
            a=select('paper/dedicated_multiples.csv',**dict(P,load=load,team=50))
            b=select('paper/shared_multiples.csv',**dict(P,load=load,billing='shared_work'))
            self.assertAlmostEqual(float(a['api_median_over_hybrid']),dedicated,places=3)
            self.assertAlmostEqual(float(b['api_median_over_hybrid']),shared,places=3)
            self.assertEqual(float(b['service_utilization']),.7)
            self.assertLess(float(b['full_utilization_person_month']),float(b['person_month']))
        key='v5b idleness';f,_,phrase=self.expected[key]
        self.assertIn(key,self.off.missing(self.plant(key,'1.097 против 1.701','0.526 против 1.462')))
        self.assertIn('не выделяет причинный эффект одного простоя',self.texts[f])

    # Lowest and median prices are actual admitted providers, separately at
    # zero cache and the owner aggregate. Measured cohort prices remain blank.
    def test_api_points_and_million_windows_follow_exported_rows(self):
        for point,low,lv,med,mv in [('no_cache','darkbloom/fp4',5.505,'tenstorrent/fp4',19.519),('owner_981','chutes/fp8',1.213,'deepinfra/bf16',5.917)]:
            for provider,want,role in [(low,lv,'cheapest'),(med,mv,'median')]:
                r=select('api_admission.csv',profile='existing_combined',scope_tier='measured_ladder',availability_scenario='snapshot_1d',cache_point=point,role=role)
                self.assertEqual(r['provider'],provider);self.assertEqual(r['admitted'],'True')
                self.assertAlmostEqual(float(r['effective_usd_per_1000_calls']),want,places=3)
        for scenario,low,lv,med,mv in [('snapshot_1d','phala',54.715,'novita',93.581),('analyst_72h_with_alibaba','novita',93.581,'alibaba',95.351),('analyst_72h_without_alibaba','novita',93.581,'novita',93.581)]:
            for role,provider,want in [('cheapest',low,lv),('median',med,mv)]:
                r=select('api_admission.csv',profile='million',scope_tier='million_fixed_depth',availability_scenario=scenario,cache_point='owner_981',role='cheapest_and_median' if scenario=='analyst_72h_without_alibaba' else role)
                self.assertEqual(r['provider'],provider);self.assertAlmostEqual(float(r['effective_usd_per_1000_calls']),want,places=3)
        self.assertIn('Доступность считается по попыткам всего окна',self.texts['07-economics.tex'])
        self.assertIn('98.1'+r'\% не принято за измеренную долю каждого поставщика',self.texts['01-introduction.tex'])

    # M3 anchored 1M routing differs from a120s sensitivity; M5 cannot borrow
    # its threshold, and measured slot restore cannot close delta-import waits.
    def test_million_thresholds_are_estimated_client_specific_and_keep_mac_pending(self):
        # R22's previous Mac gap is now a measured local path; delta import
        # stays unmeasured and cannot be relabelled from full-slot recovery.
        data=rows('link_thresholds.csv')
        for fmt,threshold in [('bf16',3.351),('f32',5.916)]:
            chosen=[r for r in data if all(r[k]==v for k,v in dict(client='m3max',transport=fmt,server='b300_fp8_kv',depth='1000000',delta='690',link='historical_home_wifi').items()) and r['recovery_kind']=='full_slot_restore_proxy' and r['primary']=='True']
            self.assertEqual(len(chosen),1);r=chosen[0]
            self.assertAlmostEqual(float(r['threshold_MB_s']),threshold,places=3)
            self.assertEqual(r['measurement_depth'],'1040000')
            self.assertIn('NOT measured delta import',r['rate_basis'])
        key='v5b million routing';f,_,phrase=self.expected[key]
        self.assertIn(key,self.off.missing(self.plant(key,'Для M3 Max','Для M5 Max')))
        self.assertIn('Прямой замер Mac.',self.texts[f])
        self.assertNotIn(r'\pending{импорт, проверка логитов, генерация и добавочный prefill Mac',self.texts[f])

    # Exact measured points and stated interpolation replace R22 at depth;
    # out-of-surface and B300 gains remain modelled. Claude is local-only.
    def test_modelled_decode_and_zero_offload_profile_are_not_measurement_claims(self):
        data=rows('decode_scaling.csv')
        p=[r for r in data if r['server']=='pro6000_fp8' and r['requested_streams']=='32' and r['depth'] in ('16000','64000','164000','512000')]
        self.assertEqual([r['batch'] for r in p],['32','12','5','1'])
        self.assertGreater(float(p[0]['gain']),float(p[-1]['gain']))
        self.assertEqual(['modelled' in r['basis'] for r in p],[True,False,False,True])
        self.assertIn('interpolated',p[1]['basis']);self.assertIn('measured PRO',p[2]['basis'])
        c=[r for r in rows('paper/main_economics.csv') if all(r.get(k)==v for k,v in dict(P,profile='claude_deep').items())]
        self.assertTrue(c);self.assertTrue(all(float(r['offload_share'])==0 and float(r['service_utilization'])==0 for r in c))
        self.assertIn('между опорами интерполируется время на токен',self.texts['07-economics.tex'])
        key='v5b Claude local only';f,_,phrase=self.expected[key]
        self.assertIn(key,self.off.missing(self.plant(key,'0.00','100.00')))

    # Both abstracts keep hard budgets; economic claims travel with occupancy,
    # ownership and selected-call scope, while privacy/bandwidth prose stays.
    def test_plain_language_and_abstract_budgets_keep_conditions(self):
        ru=self.off.abstract_text(self.texts['00-abstract.tex']);en=(ROOT/'paper/abstract.en.txt').read_text().strip()
        self.assertLess(len(ru),1920);self.assertLessEqual(len(en),1800)
        # Detailed costs/occupancy stay in the main economics; abstract leads with measurements.
        for n in ('56.64','45.17','10.40','27.28','98.1'):self.assertIn(n,self.texts['07-economics.tex'])
        self.assertIn('выделенном офисном PRO 6000',ru);self.assertIn('dedicated office PRO 6000',en)
        for f in ('01-introduction.tex','14-conclusion.tex'):
            for clause in ('Чужой сервер prefill видит весь контекст пользователя','пока полоса памяти клиента покрывает генерацию','меньший KV на токен'):
                self.assertIn(clause,self.texts[f])
        self.assertEqual(self.off.pending_gaps(self.texts),[])
        self.assertEqual(self.off.r20_signatures(self.texts),[])

    # Current archival custody is separate from the paper's exact-byte pins.
    def test_v5b_evidence_hashes(self):
        readme=(SOURCE/'README.md').read_text()
        for p in SOURCE.iterdir():
            if p.is_file() and p.name!='README.md':self.assertIn(hashlib.sha256(p.read_bytes()).hexdigest(),readme,p.name)
