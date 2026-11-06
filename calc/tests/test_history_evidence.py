"""Public-squash provenance preserves old byte, semantic and rejection contracts."""
import ast,gzip,hashlib,io,json,sys,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import history_evidence as history
import public_history_guard as guard

class PublicHistoryContracts(unittest.TestCase):
    # Exact reviewed Git-bearing modules are the positive control. An added
    # private object lookup cannot be hidden behind a public one-commit HEAD.
    def test_repository_has_no_unported_private_git_reads(self):
        self.assertEqual(guard.violations(),[])

    def test_guard_rejects_planted_private_git_show(self):
        self.assertEqual(guard.violations(),[])
        plant="import subprocess\nsubprocess.check_output(['git','show','ca7f228acd789380bf46016fd87acc33e1b07aef:calc/out/run24/r24_manifest.json'])\n"
        found=guard.violations({'calc/tests/planted_private_lookup.py':plant})
        self.assertTrue(any(r['kind']=='private revision outside evidence gateway'for r in found),found)

    # A miniature authenticated fixture uses actual Git absence, never a
    # skipped assertion. Corrupt gzip data must fail its specific SHA control.
    def test_fixture_only_content_rejects_corruption_with_positive_control(self):
        with tempfile.TemporaryDirectory()as tmp:
            store=Path(tmp);(store/'objects').mkdir();raw=b'accepted historical payload\n';packed=gzip.compress(raw,mtime=0);sha=hashlib.sha256(raw).hexdigest();rev='0'*40
            entry={'oid':'1'*40,'mode':'100644','bytes':len(raw),'sha256':sha,'object':sha+'.gz','compressed_sha256':hashlib.sha256(packed).hexdigest()}
            payload=gzip.compress(json.dumps({'revisions':{rev:{'aliases':[rev],'files':{'x':entry}}}}).encode(),mtime=0);(store/'manifest.json.gz').write_bytes(payload);(store/'objects'/entry['object']).write_bytes(packed)
            with patch.object(history,'STORE',store),patch.object(history,'MANIFEST_SHA256',hashlib.sha256(payload).hexdigest()):
                output=io.StringIO()
                with redirect_stdout(output):self.assertEqual(history.snapshot_read(rev,'x'),raw)
                self.assertIn('fixture mode (private object absent)',output.getvalue())
                (store/'objects'/entry['object']).write_bytes(packed+b'corrupt')
                with self.assertRaisesRegex(AssertionError,'compressed SHA256 mismatch'):history.snapshot_read(rev,'x')

    # Adapters are a finite pinned migration, not permission to change inputs
    # or falsely stamp future writers with a historical producer identity.
    def test_accepted_producer_and_live_adapter_identities_are_separate(self):
        names=history.port_hashes();live={name:history.digest(history.payload(history.ROOT/name))for name in names}
        accepted={}
        for name,value in live.items():
            source='ec28e37c'if name.startswith('calc/run25/')else'397432dd'if name.startswith('calc/run26/')else history.ACCEPTED_PAPER
            accepted.update(history.accepted_identity(source,{name:value}))
        self.assertNotEqual(accepted,live)
        bad=dict(live);bad['calc/run24/export.py']='0'*64
        with self.assertRaisesRegex(AssertionError,'unapproved current producer/input bytes'):history.accepted_identity(history.ACCEPTED_PAPER,{name:value for name,value in bad.items()if name in history.manifest()['revisions'][history.ACCEPTED_PAPER]['files']})
        name='calc/hybridcalc/engine.py';old=history.snapshot_hash(history.ACCEPTED_PAPER,name)
        with self.assertRaisesRegex(AssertionError,'unapproved current producer/input bytes'):history.accepted_identity(history.ACCEPTED_PAPER,{name:'0'*64})
        self.assertEqual(history.accepted_identity(history.ACCEPTED_PAPER,{name:old}),{name:old})

    # Available objects must cross-check fixture SHA values. In the actual
    # public layout, the same test uses and authenticates in-tree content.
    def test_private_git_crosscheck_or_explicit_fixture_mode(self):
        full=history.revision(history.ACCEPTED_PAPER);name='calc/tests/r15_sentences.py'
        self.assertTrue(history.snapshot_read(full,name))
        if history.private_available(full):
            entry=history.manifest()['revisions'][full]['files'][name];key=('blob',entry['oid'],__import__('os').environ.get('GIT_DIR'),__import__('os').environ.get('PATH'));history._checked.discard(key)
            original=history._git;applied=[]
            def corrupt(*argv,**kw):
                value=original(*argv,**kw)
                if argv[0]=='show':applied.append(argv);return value+b'changed'
                return value
            with patch.object(history,'_git',side_effect=corrupt),self.assertRaisesRegex(AssertionError,'differs from private Git'):history.snapshot_hash(full,name)
            self.assertEqual(len(applied),1)
        else:
            self.assertFalse(history.private_available(full));self.assertEqual(len(history.snapshot_hash(full,name)),64)

    # Only provenance readers/verifiers change in the legacy publishers; their
    # actual calculation, encoding and live writer identity functions are exact.
    def test_only_provenance_function_bodies_change(self):
        permitted={
            'calc/run25/export.py':{'frozen'},
            'calc/run25/finish.py':{'audit'},
            'calc/run26/export.py':{'frozen','audit'},
            'calc/run22/export.py':{'frozen','verify'},
            'calc/run23/export.py':{'frozen','verify'},
            'calc/run24/export.py':{'frozen','verify'},
            'calc/run24/curves.py':{'load'},
            'calc/tests/r14_publication.py':{'blob','verify_paper'},
            'calc/tests/r15_sentences.py':{'before','sentence_diff','refresh_reports'},
        }
        for name,allowed in permitted.items():
            old=ast.parse(history.snapshot_read('ec28e37c'if name.startswith('calc/run25/')else'397432dd'if name.startswith('calc/run26/')else history.ACCEPTED_PAPER,name).decode())
            new=ast.parse((history.ROOT/name).read_text())
            functions=lambda tree:{n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
            # Only the declared ledger I/O spelling is normalized; every other
            # writer/calculation AST remains the accepted original.
            class LedgerIO(ast.NodeTransformer):
                def visit_Call(self,node):
                    self.generic_visit(node)
                    if isinstance(node.func,ast.Attribute) and isinstance(node.func.value,ast.Name) and node.func.value.id=='ledger_storage':
                        if node.func.attr=='read_text' and len(node.args)==1:
                            return ast.Call(func=ast.Attribute(value=node.args[0],attr='read_text',ctx=ast.Load()),args=[],keywords=[])
                        if node.func.attr=='open_text' and node.args and isinstance(node.args[0],ast.Name) and node.args[0].id=='LEDGER':
                            return ast.Call(func=ast.Attribute(value=node.args[0],attr='open',ctx=ast.Load()),args=node.args[1:],keywords=node.keywords)
                    return node
            if name in ('calc/run22/export.py','calc/run23/export.py'):new=LedgerIO().visit(new)
            before,after=functions(old),functions(new)
            self.assertEqual(set(before),set(after),name)
            for function in before:
                if function not in allowed:self.assertEqual(before[function],after[function],name+':'+function)

    # The old git-diff contract rejects executable/type drift as well as bytes.
    # A bounded filesystem fixture controls only the historical/index inputs.
    def test_unchanged_rejects_mode_and_content_with_positive_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'x';p.write_bytes(b'accepted\n');p.chmod(0o644)
            full=history.ACCEPTED_PAPER;entry={'mode':'100644','oid':'1'*40,'sha256':history.digest(p.read_bytes())}
            records={'revisions':{full:{'aliases':[full],'files':{'x':entry}}}}
            with patch.object(history,'ROOT',root),patch.object(history,'manifest',return_value=records),patch.object(history,'private_available',return_value=False),patch.object(history,'_git',return_value=b'x\n'):
                self.assertEqual(history.unchanged(full), '')
                p.chmod(0o755)
                with self.assertRaisesRegex(AssertionError,'changed historical mode'):history.unchanged(full)
                p.chmod(0o644);p.write_bytes(b'changed\n')
                with self.assertRaisesRegex(AssertionError,'changed historical bytes'):history.unchanged(full)

    # The accepted full team grid keeps its original producer/cache hashes;
    # changing live calculation inputs must still fail the same cache guard.
    def test_run24_cache_identity_accepts_only_verified_adapter_migration(self):
        from run24 import curves
        self.assertEqual(curves.load()['sample_controls'],5184)
        original=curves.baseline_identity();changed=dict(original)
        changed['calc/run23/economics.py']='0'*64
        with patch.object(curves,'baseline_identity',return_value=changed):
            with self.assertRaisesRegex(AssertionError,'unapproved current producer/input bytes'):curves.load()
