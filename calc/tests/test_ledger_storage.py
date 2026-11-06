"""Finite lossless representation, authenticated content and exact custody fences."""
from pathlib import Path
from unittest.mock import patch
import contextlib,gzip,hashlib,io,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import ledger_storage as s
import history_evidence as h

class LedgerStorageTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);name='calc/accepted.csv';p=root/(name+'.gz');p.parent.mkdir();data=b'a,b\n1,2\n';raw=self.pack(data);p.write_bytes(raw)
            rows={name:{'stored_path':name+'.gz','content_bytes':len(data),'content_sha256':s.digest(data),'gzip_sha256':s.digest(raw)}}
            with patch.object(s,'ROOT',root),patch.object(s,'registry',return_value=rows):yield root,name,p,rows,data
    @staticmethod
    def pack(data):
        out=io.BytesIO()
        with gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=9,mtime=0)as f:f.write(data)
        return out.getvalue()

    # Exactly two accepted revision/path/hash/size pairs authorize the transform;
    # private originals cross-check when present, fixtures authenticate otherwise.
    def test_only_two_accepted_content_identities(self):
        expected={'calc/ENGINE-QUOTES-R22-261103.csv':(193921511,'1a30e9259704cbba6690c5c7f4f0d0894d9eae25811bc438ea45a0a7ad1ec1d8'), 'calc/ENGINE-QUOTES-R23-261104.csv':(214481624,'4d4e570c333a4a95087c5e9b1a543a65abe52d8a3d5b3becadbee2368a7cb295')}
        self.assertEqual(set(s.registry()),set(expected))
        for n,(size,sha)in expected.items():
            row=s.registry()[n];self.assertEqual((row['content_bytes'],row['content_sha256']),(size,sha));self.assertEqual(row['transform'],s.TRANSFORM)
            self.assertEqual(h.snapshot_hash(row['source_revision'],n),sha)
            self.assertEqual(len(s.read_bytes(s.ROOT/n)),size)

    # Valid content is accepted; even a repinned gzip hash cannot authorize a
    # changed decompressed byte. Committed gzip bytes have an independent fence.
    def test_changed_content_and_changed_compression_reject(self):
        with self.fixture()as(root,n,p,rows,data):
            self.assertEqual(s.read_bytes(root/n),data)
            bad=self.pack(data.replace(b'1',b'9'));rows[n]['gzip_sha256']=s.digest(bad);p.write_bytes(bad)
            with self.assertRaisesRegex(ValueError,'content mismatch'):s.read_bytes(root/n)
            p.write_bytes(self.pack(data));rows[n]['gzip_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'gzip SHA256 mismatch'):s.read_bytes(root/n)

    # Reject truncated and multi-member streams independently of committed hash;
    # ordinary gzip.decompress would accept the concatenated-member mutant.
    def test_truncated_and_multimember_gzip_reject(self):
        with self.fixture()as(root,n,p,rows,data):
            self.assertEqual(s.read_bytes(root/n),data);good=p.read_bytes()
            for bad in (good[:-2],good+self.pack(b''),good+b'trailing'):
                p.write_bytes(bad);rows[n]['gzip_sha256']=s.digest(bad)
                with self.assertRaisesRegex(ValueError,'truncated or multi-member'):s.read_bytes(root/n)

    # A dual representation is refused in filesystem and index; the finite path
    # map cannot swallow a third renamed file or an unrelated changed byte.
    def test_custody_rejects_dual_third_path_and_other_byte(self):
        with self.fixture()as(root,n,p,rows,data):
            old={'mode':'100644','sha256':s.digest(data)};other='other.txt';(root/other).write_bytes(b'accepted')
            files={n:old,other:{'mode':'100644','sha256':s.digest(b'accepted')}};full=h.ACCEPTED_PAPER
            with patch.object(h,'ROOT',root),patch.object(h,'snapshot_paths',return_value=sorted(files)),patch.object(h,'manifest',return_value={'revisions':{full:{'files':files}}}),patch.object(h,'revision',return_value=full),patch.object(h,'expected_current_hash',side_effect=lambda rev,name,ports:files[name]['sha256']),patch.object(h,'_git',return_value=(n+'.gz\n'+other+'\n').encode())as git:
                self.assertEqual(h.unchanged(full),'')
                (root/other).write_bytes(b'changed')
                with self.assertRaisesRegex(AssertionError,'changed historical bytes'):h.unchanged(full)
                (root/other).write_bytes(b'accepted');git.return_value=(n+'.gz\n'+other+'\nthird.csv.gz\n').encode()
                with self.assertRaisesRegex(AssertionError,'changed historical path set'):h.unchanged(full)
                git.return_value=(n+'\n'+n+'.gz\n'+other+'\n').encode()
                with self.assertRaisesRegex(ValueError,'dual ledger representation'):h.unchanged(full)
            (root/n).write_bytes(data)
            with self.assertRaisesRegex(ValueError,'plain ledger path forbidden'):s.read_bytes(root/n)

    # Writer compares generated content, not zlib-specific gzip bytes; a valid
    # existing committed member stays exact, a generated payload change rejects.
    def test_writer_preserves_committed_gzip_and_refuses_changed_content(self):
        with self.fixture()as(root,n,p,rows,data):
            before=p.read_bytes()
            original=gzip.GzipFile
            @contextlib.contextmanager
            def other_compressor(*args,**kw):
                with original(*args,**kw)as packed:yield packed
                # Another valid gzip OS byte models different compressor bytes,
                # independently of the accepted decompressed CSV identity.
                raw=kw['fileobj'];raw.seek(9);raw.write(b'\x03');raw.seek(0,2)
            self.assertNotEqual(before[9],3)
            with patch.object(gzip,'GzipFile',other_compressor):
                with s.open_text(root/n)as f:f.write(data.decode())
            self.assertEqual(p.read_bytes(),before)
            with self.assertRaisesRegex(ValueError,'content mismatch'):
                with s.open_text(root/n)as f:f.write('changed\n')
            self.assertEqual(p.read_bytes(),before)

    # A fresh generated ledger need not reproduce committed compressor bytes.
    # Repeated regeneration compares content; exact custody remains independent.
    def test_fresh_regeneration_compares_content_but_custody_pins_gzip(self):
        with self.fixture()as(root,n,p,rows,data):
            p.unlink()
            with s.open_text(root/n)as f:f.write(data.decode())
            alternate=bytearray(p.read_bytes());alternate[9]=3;p.write_bytes(alternate)
            self.assertNotEqual(s.digest(p.read_bytes()),rows[n]['gzip_sha256'])
            try:text=s.read_text(root/n)
            except ValueError as exc:self.fail('fresh regeneration incorrectly requires committed gzip bytes: '+str(exc))
            self.assertEqual(text,data.decode())
            with self.assertRaisesRegex(ValueError,'gzip SHA256 mismatch'):h.payload(root/n)
            generated=p.read_bytes()
            with s.open_text(root/n)as f:f.write(data.decode())
            self.assertEqual(p.read_bytes(),generated)
            bad=self.pack(data.replace(b'1',b'9'));p.write_bytes(bad)
            with self.assertRaisesRegex(ValueError,'content mismatch'):s.read_text(root/n)
