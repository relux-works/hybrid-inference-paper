"""Published run25 admission gates and bounded-write controls."""
import copy
from collections import namedtuple
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run25 import export, finish, model, publication


class Run25ExportContracts(unittest.TestCase):
    # CSV unknowns remain unknown; float-valued enrichment can render beside
    # original string cells without crashing or changing numeric identifiers.
    def test_unavailable_publication_number_cannot_become_finite_with_mixed_control(self):
        rows=publication.typed([dict(cost=1.5,utilization='0.25',fleet_policy='1',missing='NaN')])
        self.assertEqual(rows[0]['cost'],1.5)
        self.assertEqual(rows[0]['utilization'],.25)
        self.assertEqual(rows[0]['fleet_policy'],'1')
        self.assertEqual(rows[0]['missing'],'NaN')

    # An accepted-looking row cannot hide a storage shortfall; a real row passes.
    def test_published_storage_shortfall_refuses_with_positive_control(self):
        rows = finish.load('fleet_summary')
        good = next(r for r in rows if r['status']=='feasible')
        finish.audit_rows([good])
        bad = dict(good,storage_capacity_copies='0')
        with self.assertRaisesRegex(AssertionError,'declared storage shortfall'):
            finish.audit_rows([bad])

    # The gate catches an undercharged collision queue independently of model tests.
    def test_published_latency_shortfall_refuses_with_positive_control(self):
        good = next(r for r in finish.load('fleet_summary') if r['status']=='feasible')
        finish.audit_rows([good])
        bad = dict(good,actual_mean_queue_s=str(float(good['charged_mean_queue_s'])+1))
        with self.assertRaisesRegex(AssertionError,'latency budget below collision queue'):
            finish.audit_rows([bad])

    # Below-floor output is refused before either final or partial bytes exist.
    def test_disk_floor_refuses_output_without_partial_file_with_control(self):
        floor = model.config()['free_floor_bytes']
        usage = namedtuple('usage','total used free')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bounded.csv'; checks=[]
            with patch.object(export.shutil,'disk_usage',return_value=usage(2*floor,floor,floor)):
                with self.assertRaisesRegex(RuntimeError,'disk floor: refusing output write'):
                    export.write(path,b'123',checks)
            self.assertFalse(path.exists())
            self.assertFalse(path.with_name(path.name+'.r25-tmp').exists())
            self.assertEqual(checks,[])
            # Keep the target under ROOT because the actual receipt binds its path.
            path = export.ROOT/'.temp/hybrid-e-r20-261105/write-positive-control.csv'
            try:
                with patch.object(export.shutil,'disk_usage',return_value=usage(2*floor,floor,floor+2*1024**2)):
                    export.write(path,b'a,b\n1,2\n',checks)
                self.assertEqual(path.read_bytes(),b'a,b\n1,2\n')
                self.assertEqual(len(checks),1)
            finally:
                path.unlink(missing_ok=True)

    # s20 cannot silently be relabelled all-in-house on the exported read path.
    def test_published_s20_cannot_claim_closed_contour_with_control(self):
        original = finish.load
        rows = original('closed_contour')
        bad = copy.deepcopy(rows)
        next(r for r in bad if r['share']=='0.2')['contour']='all in-house'
        with patch.object(finish,'load',side_effect=lambda name:bad if name=='closed_contour' else original(name)):
            with self.assertRaises(AssertionError):
                finish.audit()
        finish.audit()

    # Aggregate-derived model fractions never become observed raw-log shares.
    def test_published_modelled_work_cannot_claim_observed_logs_with_control(self):
        original = finish.load
        rows = original('coverage'); bad=copy.deepcopy(rows)
        bad[0]['observed_log_work_share']=bad[0]['fitted_work_seconds_share']
        with patch.object(finish,'load',side_effect=lambda name:bad if name=='coverage' else original(name)):
            with self.assertRaises(AssertionError):
                finish.audit()
        finish.audit()


if __name__=='__main__':
    unittest.main()
