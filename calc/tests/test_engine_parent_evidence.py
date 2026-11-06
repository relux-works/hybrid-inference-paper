"""Whole-parent ports preserve original evidence and reject undeclared live drift."""
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import history_evidence as h

class EngineParentEvidenceTests(unittest.TestCase):
    # Source/input/output exceptions cannot be disguised as paper migrations.
    # Accepted historical divergence is bound to04c, all new drift is explicit.
    def test_migration_inventory_never_exempts_engine_computation(self):
        doc=h.engine_parent_migrations()
        self.assertEqual(set(doc['revisions']),{h.revision('ca7f228acd789380bf46016fd87acc33e1b07aef'),h.revision('ec28e37c')})
        for parent,rows in doc['revisions'].items():
            for name,row in rows.items():
                self.assertFalse(name.startswith(('calc/hybridcalc/','calc/run','calc/out/')),name)
                self.assertEqual(row['original_sha256'],h.snapshot_hash(parent,name))
                self.assertEqual(row['accepted_paper_sha256'],h.snapshot_hash('04c3e8de',name))
        # Claim: exactly the original nine provenance adapters and three named
        # portable-test repairs plus exactly two ledger README I/O migrations are
        # authorized; no computational file gains a waiver.
        self.assertEqual(set(h.port_hashes()), {
            'calc/run22/README.md','calc/run23/README.md',
            'calc/run25/export.py','calc/run25/finish.py','calc/run26/export.py',
            'calc/run22/export.py','calc/run23/export.py','calc/run24/export.py',
            'calc/run24/curves.py','calc/tests/r14_publication.py','calc/tests/r15_sentences.py',
            'calc/tests/test_run12.py','bench/tests/test_mac_import.py','bench/tests/test_restream.py'})

    # The same actual parent audit accepts the clean tree and rejects one
    # changed calculation payload, even while a current manifest is valid.
    def test_parent_audit_rejects_unapproved_math_with_positive_control(self):
        self.assertGreater(len(h.verify_engine_parent('ec28e37c')),1900)
        original=h.payload;target=h.ROOT/'calc/hybridcalc/engine.py';applied=[]
        def changed(path):
            if Path(path)==target:applied.append(str(path));return original(path)+b'\nchanged calculation\n'
            return original(path)
        with patch.object(h,'payload',side_effect=changed),self.assertRaisesRegex(AssertionError,'accepted engine parent bytes changed'):
            h.verify_engine_parent('ec28e37c')
        self.assertEqual(applied,[str(target)])

    # Original fixtures never substitute a stale/generated manifest as current
    # evidence. A concrete one-entry content drift must fail the manifest gate.
    def test_current_manifest_rejects_content_drift_with_positive_control(self):
        h.verify_current_manifest();original=Path.read_bytes;target=h.ROOT/'README.md';applied=[]
        def changed(path):
            if path==target:applied.append(str(path));return original(path)+b'changed\n'
            return original(path)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(AssertionError,'current manifest hash changed'):
            h.verify_current_manifest()
        self.assertEqual(applied,[str(target)])

    # Claim: a planted computation-file adapter fails the same exact inventory
    # assertion; the clean audit above is the positive control.
    def test_port_inventory_rejects_computation_exemption(self):
        ports=h.port_hashes()
        with patch.object(h,'port_hashes',return_value=dict(ports,**{'calc/hybridcalc/engine.py':'0'*64})):
            with self.assertRaisesRegex(AssertionError,'Items in the first set but not the second'):
                self.test_migration_inventory_never_exempts_engine_computation()
