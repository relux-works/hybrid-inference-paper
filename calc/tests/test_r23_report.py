"""Report publication checker detects corruption through its real read paths."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('report23',ROOT/'calc/r23_report.py')
report=importlib.util.module_from_spec(spec);spec.loader.exec_module(report)


class Report23Contracts(unittest.TestCase):
    def audit(self):
        with patch.object(sys,'argv',[str(ROOT/'calc/r23_report.py'),'--audit-only']),contextlib.redirect_stdout(io.StringIO()):
            report.main()

    # A correct report/ledger pair is a control; changing the report through the
    # actual file read must fail before it can be described as verified prose.
    def test_report_refuses_changed_text_with_published_control(self):
        self.audit()
        original=Path.read_text
        def changed(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            return text.replace('# Engine run23','# Engine run99',1) if path==report.REPORT else text
        with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'changed report quotation'):
            self.audit()

    # Deleting a genuine ledger entry in the file read is detected, while the
    # same untouched published ledger remains a positive control.
    def test_report_refuses_missing_quote_with_published_control(self):
        self.audit()
        original=Path.read_text
        def missing(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            return text[:text.rfind('\n',0,len(text)-1)+1] if path==report.QUOTES else text
        with patch.object(Path,'read_text',missing),self.assertRaisesRegex(AssertionError,'missing/changed report quote'):
            self.audit()


if __name__=='__main__':unittest.main()
