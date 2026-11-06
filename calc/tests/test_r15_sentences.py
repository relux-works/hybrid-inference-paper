"""Every liftable sentence carries its own economic conditions."""
import math
import re
import unittest
from unittest.mock import patch
import r14_publication as p
import r15_sentences as s


class SentenceContracts(unittest.TestCase):
    # The reviewer's exact omission must fail even when all other fields
    # remain. The same generated bought sentence is the valid control.
    def test_words_ready_missing_link_refuses_implicit_office_with_positive_control(self):
        row=p.read(p.ROOT/'calc/out/run20/paper/team_break_even.csv')[0]
        text=p.conclusion(row)
        parsed=s.validate_sentence(text,row)
        self.assertEqual((parsed['rate_MB_s'],parsed['rtt_ms']),(125,1))
        bad=re.sub(r'; link=[^;]+','',text)
        with self.assertRaisesRegex(AssertionError,'missing sentence condition: link'):s.validate_sentence(bad,row)

    # Each mandatory condition is parsed and bound to its row, rather than
    # accepting a billing/link keyword somewhere in unrelated prose.
    def test_every_exported_sentence_refuses_each_missing_condition(self):
        count=0;billings=set()
        for run in(20,21):
            for path in(p.ROOT/f'calc/out/run{run}/paper').glob('*.csv'):
                for row in p.read(path):
                    if 'sentence'not in row:continue
                    s.validate_sentence(row['sentence'],row);count+=1;billings.add(row['billing'])
        self.assertEqual(count,9006);self.assertEqual(billings,{'bought','rented','shared_work'})
        row=p.read(p.ROOT/'calc/out/run21/paper/shared_multiples.csv')[0];text=row['sentence']
        for field in s.FIELDS:
            with self.subTest(field=field):
                bad=re.sub(r'; '+re.escape(field)+r'=[^;]+','',text)
                with self.assertRaisesRegex(AssertionError,'missing sentence condition: '+field):s.validate_sentence(bad,row)

    # All three billing/link choices reproduce the engine's actual routing
    # profiles. A complete but incorrectly paired link still fails.
    def test_link_billing_refuses_wrong_rate_rtt_or_location_with_engine_control(self):
        from hybridcalc.engine import load
        from hybridcalc.measurements_r19 import links
        _,inputs=load('server-economics-r20');profiles={r['key']:r for r in links(inputs)}
        row=p.read(p.ROOT/'calc/out/run20/paper/dedicated_multiples.csv')[0]
        for billing,key in(('bought','office_gigabit'),('rented','engine_wan'),('shared_work','engine_wan')):
            fixture=dict(row,billing=billing);text=p.multiple_sentence(fixture);values=s.validate_sentence(text,fixture)
            self.assertEqual(values['rate_MB_s'],profiles[key]['bytes_s']/1e6)
            self.assertEqual(values['rtt_ms'],profiles[key]['rtt_s']*1000)
            wrong=text.replace(s.LINKS[billing][1],s.LINKS['rented'if billing=='bought'else'bought'][1])
            with self.assertRaisesRegex(AssertionError,'billing/link mismatch'):s.validate_sentence(wrong,fixture)
        for old,new in(('125 MB/s','124 MB/s'),('RTT 1 ms','RTT 2 ms'),('office office_gigabit','WAN office_gigabit')):
            text=p.multiple_sentence(dict(row,billing='bought'))
            with self.assertRaisesRegex(AssertionError,'billing/link mismatch'):s.validate_sentence(text.replace(old,new),dict(row,billing='bought'))

    # Capacity nan cells remain identical, while sentences keep the original
    # alarm visible. A finite-price row must not acquire an alarm claim.
    def test_capacity_alarm_sentences_keep_nan_and_disclose_source_status(self):
        rows=p.read(p.ROOT/'calc/out/run21/paper/dedicated_multiples.csv')
        alarms=[r for r in rows if not math.isfinite(float(r['hybrid_person_month']))]
        self.assertEqual(len(alarms),144)
        self.assertTrue(all('capacity alarm: source status=alarm, alarm_inputs=run20'in r['sentence']for r in alarms))
        finite=next(r for r in rows if math.isfinite(float(r['hybrid_person_month'])))
        self.assertNotIn('capacity alarm:',finite['sentence'])

    # Compare every original CSV cell recursively, including growing files.
    # A one-price-cell plant fails, while the sentence-only patch is accepted.
    def test_sentence_only_diff_refuses_numeric_change_and_preserves_growing(self):
        changes,unchanged=s.sentence_diff();self.assertEqual(len(changes),9006);self.assertGreater(unchanged,100000)
        original=p.read
        # A real existing numeric column, not an added column, is the witness.
        path=p.ROOT/'calc/out/run21/growing/growing_task_economics.csv'
        key=next(k for k in original(path)[0]if k.endswith('person_month'))
        def changed(path):
            rows=original(path)
            if str(path).endswith('run21/growing/growing_task_economics.csv'):rows[0][key]='0'
            return rows
        with patch.object(p,'read',side_effect=changed):
            with self.assertRaisesRegex(AssertionError,'non-sentence cell changed'):s.sentence_diff()

    # Both report prose and words-ready table cells are independently parsed;
    # a lifted report sentence cannot inherit its link from a nearby heading.
    def test_report_sentences_refuse_missing_link_without_surrounding_prose(self):
        self.assertEqual(s.verify_reports(),{20:27,21:48})
        text=next(line[2:]for line in(p.ROOT/'calc/ENGINE-REPORT-R20-261103.md').read_text().splitlines()if line.startswith('- ')and'; server='in line)
        self.assertIn('link',s.parse_sentence(text))
        with self.assertRaisesRegex(AssertionError,'missing sentence condition: link'):s.parse_sentence(re.sub(r'; link=[^;]+','',text))

if __name__=='__main__':unittest.main()
