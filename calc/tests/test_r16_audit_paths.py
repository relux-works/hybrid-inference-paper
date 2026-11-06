"""Run16 quote coordinates are logical paths, independent of scratch location."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import r16_audit as audit

class Run16AuditPaths(unittest.TestCase):
    # An export outside the stand-in root still names the same accepted table;
    # omitting its changed cell must raise the coverage assertion, not a path error.
    def test_external_export_keeps_canonical_source_and_rejects_omitted_cell(self):
        with tempfile.TemporaryDirectory(prefix='r16-path-') as d:
            temp=Path(d);root=temp/'repo';out=temp/'external'/'run16'
            old=root/'calc/out/run15/base';old.mkdir(parents=True)
            (old/'tiny.csv').write_text('depth,value\n100,1\n')
            for variant in ('base','bounded_undo'):
                (out/variant).mkdir(parents=True)
                (out/variant/'tiny.csv').write_text('depth,value\n100,2\n')
            with patch.object(audit,'ROOT',root),patch.object(audit,'OUT',out):
                cells=audit.changed_cells()
                self.assertEqual(len(cells),2)
                self.assertEqual({r['source'] for r in cells},{'calc/out/run16/base/tiny.csv','calc/out/run16/bounded_undo/tiny.csv'})
                self.assertTrue(all(r['old']=='1' and r['new']=='2' for r in cells))
                quotes=[dict(source=r['source'],engine_key=audit.cell_key(r),old=r['old'],new=r['new']) for r in cells]
                self.assertEqual(audit.verify_quote_coverage(quotes),2)
                with self.assertRaisesRegex(AssertionError,'unreported changed cells'):
                    audit.verify_quote_coverage(quotes[:-1])
            self.assertEqual((out/'base/tiny.csv').read_text(),'depth,value\n100,2\n')
