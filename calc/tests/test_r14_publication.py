"""R5x regression witnesses with nearby valid controls; no new GPU work."""
import copy
import csv
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import r14_publication as p


class PublicationContracts(unittest.TestCase):
    # Actual R20 prices require counted population provenance; removing only
    # the scope must fail while the same unmodified price rows pass.
    def test_r5x_repeat_api_scope_refuses_missing_counts_with_price_control(self):
        directory=p.ROOT/'calc/out/run20';self.assertTrue(p.verify_labels20(directory))
        old=p.read(directory/'api_admission.csv');bad=copy.deepcopy(old);bad[0]['workload_scope']=''
        def changed(path):return bad if path.name=='api_admission.csv'else p.read_original(path)
        with patch.object(p,'read_original',p.read,create=True),patch.object(p,'read',side_effect=changed):
            with self.assertRaisesRegex(AssertionError,'missing coverage'):p.verify_labels20(directory)
        for row in old:
            for text in('10885/39904','27.28%','1000','full workload unsupported'):self.assertIn(text,row['workload_scope'])

    # Novita lacks5m, Cloudflare lacks5m/30m. Neither can inherit a complete
    # availability label; a provider with all three windows is a positive control.
    def test_r5x_partial_availability_refuses_hidden_novita_cloudflare_windows(self):
        rows=p.read(p.ROOT/'calc/out/run20/api_admission.csv')
        for tag,text in(('novita','missing windows: 5m;'),('cloudflare','missing windows: 5m/30m;')):
            row=next(x for x in rows if x['tag']==tag);self.assertIn(text,row['availability_basis'])
        self.assertIn('missing windows: none',p.availability(dict(uptime_last_5m=100,uptime_last_30m=100,uptime_last_1d=100)))

    # Native llama duplicates are explicitly non-applicable bridge enums;
    # vLLM rows retain the measured-envelope portability sensitivity.
    def test_native_llama_duplicate_bridge_rows_cannot_claim_a_measured_effect(self):
        for table in('server_prefill','engine_sensitivity'):
            rows=p.read(p.ROOT/f'calc/out/run20/{table}.csv')
            llama=[r for r in rows if r['engine']=='llama_cpp'];self.assertTrue(llama)
            self.assertTrue(all(p.LLAMA in r['basis']for r in llama))
            self.assertTrue(all(p.LLAMA not in r['basis']for r in rows if r['engine']=='vllm'))

    # The checker compares original cells, rather than merely trusting an
    # allowlist declaration. A one-price-cell mutation must be rejected.
    def test_label_only_diff_refuses_a_numeric_change_and_accepts_new_labels(self):
        directory=p.ROOT/'calc/out/run20';changes=p.differences(20,directory)
        self.assertTrue(changes);self.assertTrue(all(x['column']in p.ALLOWED for x in changes))
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);rows=p.read(directory/'api_admission.csv');rows[0]['effective_usd_per_1000_calls']='0'
            p.dump(root/'api_admission.csv',rows)
            with self.assertRaisesRegex(AssertionError,'non-label cell changed'):p.differences(20,root)

    # Scope/bridge labels are not permission to alter an admission boolean.
    def test_label_only_diff_refuses_an_admission_change(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);rows=p.read(p.ROOT/'calc/out/run20/api_admission.csv');rows[0]['admitted']='False'
            p.dump(root/'api_admission.csv',rows)
            with self.assertRaisesRegex(AssertionError,'non-label cell changed'):p.differences(20,root)

    # Planting a5090 server is rejected. A5090 client on a permitted PRO
    # server remains valid: the owner's exclusion concerns servers only.
    def test_paper_exports_refuse_5090_server_with_pro_b300_positive_controls(self):
        for run in(20,21):
            self.assertTrue(p.verify_paper(run))
            rows=p.read(p.ROOT/f'calc/out/run{run}/paper/shared_multiples.csv')
            self.assertEqual({r['server']for r in rows},{'pro6000_fp8','b300_fp8','b300_fp8_kv'})
            bad=dict(rows[0],server='rtx5090')
            with self.assertRaisesRegex(AssertionError,'5090'):p.require_paper([bad])
            self.assertTrue(p.require_paper([dict(rows[0],client='rtx5090')]))

    # An empty/reject-everything projection or missing basis cannot satisfy
    # the paper contract. Both runs keep populated PRO small-team grids.
    def test_paper_projection_refuses_empty_or_unscoped_costs(self):
        with self.assertRaisesRegex(AssertionError,'empty'):p.require_paper([])
        for run,count in((20,288),(21,576)):
            rows=p.read(p.ROOT/f'calc/out/run{run}/paper/small_team_cost.csv');self.assertEqual(len(rows),count)
            self.assertEqual({r['server']for r in rows},{'pro6000_fp8'})
            self.assertTrue(p.require_paper(rows))
            for field in('workload_scope','cost_basis'):
                with self.assertRaisesRegex(AssertionError,'missing'):p.require_paper([dict(rows[0],**{field:''})])

    # The R20 closed-perimeter claims must not inherit5090's crossings.
    # Values below independently reproduce the accepted review's witnesses.
    def test_pro_break_even_claims_refuse_archival_5090_crossings(self):
        rows=p.read(p.ROOT/'calc/out/run20/paper/team_break_even.csv')
        selected=[r for r in rows if float(r['share'])==1 and r['client']=='m5max64'and r['basis']=='owned'and r['billing']=='bought']
        for row in selected:
            expected={'light':'4','medium':'2','heavy':'nan'}[row['load']]if row['reference']=='own_cluster'else'nan'
            self.assertEqual(row['from_people'],expected)
            self.assertIn('98.1%',row['sentence']);self.assertIn('10885/39904',row['sentence'])
        self.assertEqual(len(selected),9)

    # Shared and dedicated figures never share an unlabeled denominator.
    # Existing heavy R20 shared multiples remain equal to their source cells.
    def test_shared_work_refuses_dedicated_calendar_basis_and_preserves_anchor(self):
        directory=p.ROOT/'calc/out/run20';shared=p.read(directory/'paper/shared_multiples.csv')
        for row in shared:
            self.assertIn('lower bound',row['cost_basis']);self.assertIn('not a measured short-turn',row['bridge_basis'])
            if row['load']=='heavy':
                old=next(r for r in p.original(20,'engine_sensitivity.csv')if r['server']==row['server']and float(r['share'])==float(row['share'])and r['bridge']=='measured_envelope')
                self.assertEqual(float(row['hybrid_person_month']),float(old['resident_work_hybrid_person_month']))
                self.assertAlmostEqual(float(row['median_multiple']),float(old['resident_work_median_multiple']),places=12)
        for run in(20,21):
            dedicated=p.read(p.ROOT/f'calc/out/run{run}/paper/dedicated_multiples.csv')
            self.assertTrue(all('dedicated'in r['cost_basis']for r in dedicated))
            self.assertEqual({r['load']for r in dedicated},{'light','medium','heavy'})
            shared=p.read(p.ROOT/f'calc/out/run{run}/paper/shared_multiples.csv')
            self.assertEqual(len(shared),27 if run==20 else 54)
            if run==21:self.assertEqual({r['profile']for r in shared},{'existing_combined','claude_deep'})

    # R21 already carried the two API disclosures. The new paper projection
    # must retain every full-export cell, and catch a substituted main price.
    def test_run21_original_cells_refuse_a_changed_cost_with_unchanged_control(self):
        self.assertEqual(p.differences(21,p.ROOT/'calc/out/run21'),[])
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);rows=p.read(p.ROOT/'calc/out/run21/main_economics.csv');rows[0]['person_month']='0'
            p.dump(root/'main_economics.csv',rows)
            with self.assertRaisesRegex(AssertionError,'non-label cell changed'):p.differences(21,root)

    # The original full table retains the archival5090 data with a visible
    # owner-decision label, while permitted server rows remain quotable.
    def test_full_exports_refuse_unlabelled_archival_5090_server_rows(self):
        rows=p.read(p.ROOT/'calc/out/run20/small_team_cost.csv')
        self.assertEqual(sum(r['server']=='rtx5090'for r in rows),288)
        self.assertTrue(all(r['paper_use']=='not used in the paper'for r in rows if r['server']=='rtx5090'))
        self.assertTrue(all('eligible'in r['paper_use']for r in rows if r['server']=='pro6000_fp8'))

    # Paper quote coverage is checked against all published cells. Deleting a
    # single quote must fail even though all numeric CSVs remain untouched.
    def test_paper_quote_ledger_refuses_a_missing_cell_with_full_control(self):
        for run in(20,21):
            self.assertGreater(p.verify_quotes(run),0)
            original=p.read
            def missing(path):
                rows=original(path)
                return rows[:-1]if path.name==f'ENGINE-QUOTES-R{run}-PAPER-261103.csv'else rows
            with patch.object(p,'read',side_effect=missing):
                with self.assertRaisesRegex(AssertionError,'paper quote'):p.verify_quotes(run)

if __name__=='__main__':unittest.main()
