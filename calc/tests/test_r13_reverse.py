"""Reverse-ledger regressions for r5e/r5f and the writer's numeric scope."""
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from r13_audit import ROOT
import r13_reverse as reverse
from r13_ledger import native_changes,paper_numbers
from history_fixtures import snapshot_read
from publication_v2 import check_publication,read_texts,records


def paper_texts():
    return read_texts()


def append_plant(texts,name,text):
    line=texts[name].count('\n')+2
    texts[name]+='\n'+text+'\n'
    return f'{name}:{line}'


class ReverseLedgerTests(unittest.TestCase):
    def assert_percent_copy_rejected(self,token):
        texts=paper_texts()
        site=append_plant(texts,'paper/sections/04-channel.tex',token)
        with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
            check_publication(texts=texts)

    # Each r5f fraction-percent copy at a new line must fail the real checker;
    # current numeric-site guard; original R3 tests also run in their source fixture.
    def test_reverse_guard_rejects_percent_45_6_same_file(self):
        self.assert_percent_copy_rejected(r'В облако уходит 45.6\% вызовов.')

    def test_reverse_guard_rejects_percent_72_3_same_file(self):
        self.assert_percent_copy_rejected(r'В облако уходит 72.3\% вызовов.')

    def test_reverse_guard_rejects_percent_95_4_same_file(self):
        self.assert_percent_copy_rejected(r'Клиенты обслуживают 95.4\% вызовов.')

    def test_reverse_guard_rejects_percent_30_5_same_file(self):
        self.assert_percent_copy_rejected(r'Клиенты обслуживают 30.5\% вызовов.')

    # A ledger row, reverse waiver and native collision admit only their own
    # line, even when an identical token remains elsewhere in the same file.
    def test_reverse_ledger_rejects_same_file_883_at_new_line(self):
        texts=paper_texts()
        site=append_plant(texts,'paper/sections/07-economics.tex','Клиент успевает 883 вызова в день.')
        with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
            check_publication(texts=texts)

    def test_reverse_waiver_rejects_same_file_30_percent_at_new_line(self):
        texts=paper_texts()
        site=append_plant(texts,'paper/sections/05-clients.tex',r'Сервер B300 работает при загрузке вычислителей 30\%.')
        with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
            check_publication(texts=texts)

    # Direct native_changes uses its original line-bound source for both the
    # accepted site and fresh copy; current v2 copies are independently guarded.
    def test_native_collision_rejects_same_file_21_6_at_new_line(self):
        texts=paper_texts()
        original_text = snapshot_read('r13-publication', 'paper/sections/04-channel.tex').decode()
        texts={'paper/sections/04-channel.tex':original_text}
        original=native_changes(paper_numbers(texts))
        self.assertFalse(any(r['paper_site']=='paper/sections/04-channel.tex:79' and r['old']=='21.6' for r in original))
        site=append_plant(texts,'paper/sections/04-channel.tex','Экономия Gemma составляет 21.6 секунды.')
        found=native_changes(paper_numbers(texts))
        self.assertTrue(any(r['paper_site']==site and r['old']=='21.6' for r in found))

    # The unchanged real paper passes with its existing rows/waivers, including
    # 20%/70% inputs. A waiver cannot silently stand in for a required row.
    def test_existing_percent_sites_and_unchanged_inputs_pass(self):
        texts=paper_texts()
        self.assertGreater(check_publication(texts=texts)['scanned_numbers'],0)
        for value in ('0.2','0.7'):
            pair=dict(engine_key='unchanged input',old=value,new=value,unit='1',source='fixture')
            text={'paper/input.tex':str(round(float(value)*100))+r'\%'}
            self.assertEqual(reverse.reverse_changes([],texts=text,pairs=[pair]),[])

    # Independent fraction fixtures prove x100 at printed precision for TeX,
    # literal and Russian percent suffixes, while retaining as-written matches.
    def test_fraction_percent_rendering_precision_and_suffixes(self):
        pair=dict(engine_key='fraction fixture',old='0.4561',new='0.4525',unit='1',source='fixture')
        for suffix in (r'\%','%',' процента',' процентов'):
            with self.subTest(suffix=suffix):
                found=reverse.reverse_changes([],texts={'paper/pct.tex':'45.6'+suffix},pairs=[pair])
                self.assertEqual([r['new'] for r in found],['45.2'])
        # Distinct fractions with the same printed percent require no row.
        pair['new']='0.4562'
        self.assertEqual(reverse.reverse_changes([],texts={'paper/pct.tex':r'45.6\%'},pairs=[pair]),[])
        pair.update(old='0.4561',new='0.4525')
        self.assertEqual(reverse.reverse_changes([],texts={'paper/scalar.tex':'45.6'},pairs=[pair]),[])
        self.assertTrue(reverse.reverse_changes([],texts={'paper/scalar.tex':'0.456'},pairs=[pair]))
        pair.update(old='45.61',new='45.25',unit='percent')
        self.assertEqual([r['new'] for r in reverse.reverse_changes([],texts={'paper/pct.tex':r'45.6\%'},pairs=[pair])],['45.2'])

    # Every copy is tested separately through the real checker at a fresh site.
    # The complete current publication is the positive control.
    def test_reverse_guard_rejects_copied_non_arch_changed_values(self):
        texts=read_texts()
        check_publication()  # Positive control for the same current byte/site guard.
        for token in ('883',r'\$24.1','около 880','1.16','221',r'11--17\%',r'30\%','22.5'):
            with self.subTest(token=token):
                with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
                    check_publication(texts=dict(texts, **{'paper/copied.tex':token}))

    # The historical 21.6-minute exception cannot authorize a new v2 file/line/token.
    # Exercise native_changes separately so the reverse guard cannot mask L3.
    def test_paper_ledger_waivers_are_site_bound(self):
        text={'paper/copied.tex':'Экономия Gemma: 21.6 секунды.'}
        self.assertTrue(any(r['old']=='21.6' for r in native_changes(paper_numbers(text))))
        texts=read_texts()
        check_publication()
        for token in ('21.6','11.5'):
            with self.subTest(waived_token=token):
                with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
                    check_publication(texts=dict(texts, **{'paper/copied.tex':token}))

    # Independent two-value fixtures establish normalization, precision and
    # sign behavior without drawing expected verdicts from the engine/checker.
    def test_writer_numeric_scope_and_unchanged_controls(self):
        cases=[('.66GB','663200000','880800000','B'),(',66GB','663200000','880800000','B'),('.66--.88','0.66--0.88','0.7--0.9',''),('21,6', '21.6','21.0',''),('1,234','1234','1400',''),
               ('1{,}234','1234','1400',''),(r'1\,234','1234','1400',''),
               ('1\u2009234','1234','1400',''),('1\u202f234','1234','1400',''),
               ('11--17','11--17','10--29',''),('11–17','11--17','10--29',''),
               ('11-17','11--17','10--29',''),(r'30\%','30','14.1','percent'),
               (r'\$24.1','24.07','30.07','USD'),('24,1 ₽','24.07','30.07','USD'),
               ('-2.8','-2.8','-4.5','s'),('+2.8','2.8','-2.8','s'),
               ('около 880','882.63','837.65','call/day')]
        # Literal physical scales keep the expected fixtures independent of the
        # registry under test; dropping/changing a unit cannot shrink coverage.
        units={'B':1,'KB':1000,'MB':1000000,'GB':1000000000,
               'KiB':1024,'MiB':1048576,'GiB':1073741824,
               'Б':1,'КБ':1000,'МБ':1000000,'ГБ':1000000000,
               'КиБ':1024,'МиБ':1048576,'ГиБ':1073741824}
        for unit,scale in units.items():
            cases.append(('1.23~'+unit,str(1230*scale/1000),str(1480*scale/1000),'B'))
            cases.append(('1.23'+unit,str(1230*scale/1000),str(1480*scale/1000),'B'))
        for text,old,new,unit in cases:
            pair=dict(engine_key='fixture',old=old,new=new,unit=unit,source='independent fixture')
            with self.subTest(text=text):
                self.assertTrue(reverse.reverse_changes([],texts={'paper/fixture.tex':text},pairs=[pair]))
                # Same old/new printed value requires no work-list row.
                pair['new']=pair['old']
                self.assertEqual(reverse.reverse_changes([],texts={'paper/fixture.tex':text},pairs=[pair]),[])
        pair=dict(engine_key='sign',old='-2.8',new='-4.5',unit='s',source='fixture')
        self.assertEqual(reverse.reverse_changes([],texts={'paper/fixture.tex':'2.8'},pairs=[pair]),[])
        pair.update(old='-2.8',new='2.8')
        self.assertTrue(reverse.reverse_changes([],texts={'paper/fixture.tex':'-2.8'},pairs=[pair]))
        # Value precision, rather than exact old spelling, drives comparison.
        pair.update(old='21.64',new='21.61')
        self.assertEqual(reverse.reverse_changes([],texts={'paper/fixture.tex':'21.6'},pairs=[pair]),[])

    # The inventory includes non-architecture keys, all cases, JSON API bills
    # and R12's measured-server reference. New-only measurement files are named.
    def test_reverse_inventory_spans_exports_and_keys(self):
        check_publication()
        pairs,files=reverse.export_changes()
        before=len(pairs)
        reverse.reverse_changes([],texts={},pairs=pairs)
        self.assertEqual(len(reverse.export_changes()[0]),before,'reverse scanning must not mutate cached raw export inventory')
        for case in ('base','earlier-run','checkpoints-on'):
            for table in ('person_cost_s20.csv','client_sessions_day.csv','people_per_gpu.csv','arch_compare.csv'):
                self.assertTrue(any('/'+case+'/'+table in r['engine_key'] for r in pairs),(case,table))
        self.assertTrue(any('api-baselines/paper-base.json' in r['engine_key'] for r in pairs))
        self.assertTrue(any('_measured_server.csv' in r['engine_key'] for r in pairs))
        # Removed numeric keys are changes too; R12's long-form payback delta
        # must not vanish when R13 exports a different schema.
        for policy in ('','_conservative'):
            old=reverse.read_csv(ROOT/('calc/out/paper/payback'+policy+'_measured_server.csv'))
            wanted={r['delta'] for r in old if reverse.decimal(r['delta']) is not None}
            actual={r['old'] for r in pairs if r['engine_key'].startswith('payback'+policy+'_measured_server.csv') and r['engine_key'].endswith('.delta')}
            self.assertTrue(wanted<=actual,(policy,wanted-actual))
        self.assertEqual(sum(r.get('new_only',False) for r in files),12)

    # Every current coordinate is required, including unchanged numeric tokens;
    # omitting one cannot be covered by an equal value elsewhere.
    def test_exact_printed_site_omission_is_rejected(self):
        check_publication()
        sites=records()
        target=next(r for r in sites if r['file']=='paper/sections/04-channel.tex')
        bad=[r for r in sites if r is not target]
        with self.assertRaisesRegex(AssertionError,'unregistered v2 numeric site'):
            check_publication(bad)

    # Word numerals, scales and multiplicative forms are listed for the writer;
    # they do not silently become automatic numeric-coverage claims.
    def test_number_words_are_explicit_manual_scope(self):
        text={'paper/words.tex':'Двадцати двух секунд; вдвое, тысяча и миллион.\nОдна-две и половина; 21.6.'}
        self.assertEqual([w for _,_,w in reverse.number_words(text)],
                         ['Двадцати','двух','вдвое','тысяча','миллион','Одна','две','половина'])
        self.assertEqual(reverse.number_words({'paper/words.tex':'сотрудник одинаковых размеров'}),[])
        self.assertEqual([w for _,_,w in reverse.number_words({'paper/words.tex':'Четвёртый в одном триллионе; тыс.'})],['Четвёртый','одном','триллионе','тыс'])


if __name__=='__main__':unittest.main()
