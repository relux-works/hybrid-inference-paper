"""Strict c21284cd hybrid sequence fixtures, independent of the parser's writer."""
import contextlib
import errno
import hashlib
import io
import os
from pathlib import Path
import struct
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from test_kitlib import kitlib, run


def u32(*values):
    return struct.pack('<' + 'I' * len(values), *values)


def fixture(ext=12, trans=0, cache_type=1, row_bytes=4):
    """Four tokens/cells, one attention layer, one recurrent layer (no PLE)."""
    offsets = {}
    data = bytearray(u32(0x67677371, 3, 4, 10, 20, 30, 40))
    def add(name, value):
        offsets[name] = len(data)
        data.extend(value)
    add('streams', u32(1))
    add('cells', u32(4))
    for pos in range(4):
        add('meta%d' % pos, u32(pos, 1) + (u32(100, 200, 300) if ext else b'') + u32(0))
    add('trans', u32(trans))
    add('attn_layers', u32(1))
    add('key_type', u32(cache_type))
    add('key_size', struct.pack('<Q', row_bytes))
    add('keys', b'K' * (4 * row_bytes))
    add('value_type', u32(1))
    if trans:
        add('value_element', u32(2))
        add('value_embd', u32(2))
    else:
        add('value_size', struct.pack('<Q', 4))
    add('values', b'V' * 16)
    offsets['insertion'] = len(data)
    add('rec_cells', u32(1))
    add('rec_meta', u32(3, 0))
    add('rec_trans', u32(0))
    add('rec_layers', u32(2))
    add('r_type', u32(0))
    add('r_size', struct.pack('<Q', 8))
    add('r', b'R' * 8)
    add('s_type', u32(0))
    add('s_size', struct.pack('<Q', 16))
    add('s', b'S' * 16)
    return bytes(data), offsets


def large_fixture(path):
    """Valid 1.56 GiB sparse import; no large allocation or model download."""
    data, off = fixture()
    row_bytes = 400 * 1024 * 1024
    with path.open('wb') as f:
        f.write(data[:off['key_size']])
        f.write(struct.pack('<Q', row_bytes))
        f.seek(4 * row_bytes, 1)
        f.write(data[off['values']-12:])


def wait_for_copy(process, directory):
    """Wait for actual partial-copy bytes, not a timing-only signal guess."""
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        for path in directory.glob('**/.restream-*'):
            if path.stat().st_size >= 8 * 1024 * 1024:
                return path
        if process.poll() is not None:
            raise AssertionError('restream exited before a partial copy was observed')
        time.sleep(.005)
    raise AssertionError('restream never produced partial-copy bytes')


class Restream(unittest.TestCase):
    def parse(self, data):
        with tempfile.TemporaryFile() as f:
            f.write(data)
            f.flush()
            return kitlib.parse_slot(f)

    # Claim: 2/4/8-stream outputs differ ONLY at n_stream and the inserted empty
    # entries, parse back to exactly one nonempty stream, and leave IN byte-identical.
    # Both supported metadata variants and V layouts, plus q8_0 rows, are exercised.
    def test_expansion(self):
        for ext, trans, typ, size in ((0, 0, 1, 4), (12, 0, 8, 34), (12, 1, 1, 4)):
            original, off = fixture(ext, trans, typ, size)
            for streams in (2, 4, 8):
                with self.subTest(ext=ext, trans=trans, streams=streams), tempfile.TemporaryDirectory() as d:
                    src, dst = Path(d)/'in', Path(d)/'out'
                    src.write_bytes(original)
                    result = run('restream-slot', str(src), str(dst), '--streams', str(streams))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    expected = (original[:off['streams']] + u32(streams)
                                + original[off['streams']+4:off['insertion']]
                                + u32(*([0] * (streams-1))) + original[off['insertion']:])
                    self.assertEqual(dst.read_bytes(), expected)
                    self.assertEqual(src.read_bytes(), original)
                    self.assertEqual(len(expected), len(original)+4*(streams-1))
                    parsed = self.parse(expected)
                    self.assertEqual(parsed['streams'], streams)
                    self.assertEqual(parsed['counts'], [4] + [0]*(streams-1))
                    for data in (original, expected):
                        self.assertIn(hashlib.sha256(data).hexdigest(), result.stdout)

    # Claim: c21284cd server_tokens' text wrapper makes the sequence header count
    # four extra words; those words stay intact and do not become attention cells.
    # Regression witness for the logical-token/header-word distinction in the CPU run.
    def test_server_token_words(self):
        original, off = fixture()
        packed = (original[:8] + u32(8, 0xffffffff, 1, 4) + original[12:28]
                  + u32(0) + original[28:])
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d)/'in', Path(d)/'out'
            src.write_bytes(packed)
            r = run('restream-slot', str(src), str(dst), '--streams', '4')
            self.assertEqual(r.returncode, 0, r.stderr)
            out = dst.read_bytes()
            self.assertEqual(out[:off['streams']+16], packed[:off['streams']+16])
            self.assertEqual(self.parse(out)['token_words'], 8)
            self.assertEqual(self.parse(out)['counts'], [4, 0, 0, 0])
            self.assertEqual(src.read_bytes(), packed)

    # Claim: even two successful layout interpretations must be refused, rather
    # than choosing the first; the real single-interpretation control still parses.
    def test_ambiguous_layout(self):
        original, _ = fixture()
        valid = self.parse(original)
        with patch.object(kitlib, '_parse_slot', return_value=valid):
            with self.assertRaisesRegex(kitlib.SlotError, 'ambiguous'):
                self.parse(original)

    # Claim: cached IN hashes preserve stdout values and exact file output while
    # only OUT is hashed per attempt; a malformed cache value cannot publish OUT.
    def test_cached_hash(self):
        original, _ = fixture()
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d)/'in', Path(d)/'out'
            src.write_bytes(original)
            digest = hashlib.sha256(original).hexdigest()
            with patch.object(kitlib, 'sha256_file', wraps=kitlib.sha256_file) as hashes:
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(kitlib.restream_slot(src, dst, 4, digest), 0)
                self.assertEqual(hashes.call_args_list, [unittest.mock.call(dst)])
            self.assertIn('IN  sha256 '+digest, output.getvalue())
            self.assertIn('OUT sha256 '+kitlib.sha256_file(dst), output.getvalue())
            dst.unlink()
            with self.assertRaisesRegex(kitlib.SlotError, 'cached IN sha256'):
                kitlib.restream_slot(src, dst, 4, 'bad')
            self.assertEqual(list(Path(d).iterdir()), [src])
            self.assertEqual(src.read_bytes(), original)

    # Claim: TERM during the real CLI's large-file copy unwinds Python's finally,
    # removes its hidden temporary file, publishes no OUT, and leaves IN unchanged.
    def test_term_during_copy(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            src, dst = d/'in', d/'out'
            large_fixture(src)
            before = kitlib.sha256_file(src)
            p = subprocess.Popen([sys.executable, str(Path(kitlib.__file__)), 'restream-slot',
                                  str(src), str(dst), '--streams', '4'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                partial = wait_for_copy(p, d)
                self.assertLess(partial.stat().st_size, src.stat().st_size)
                p.send_signal(signal.SIGTERM)
                stdout, stderr = p.communicate(timeout=20)
                self.assertEqual(list(d.iterdir()), [src])
                self.assertEqual(kitlib.sha256_file(src), before)
                self.assertEqual(p.returncode, 143, stdout+stderr)
            finally:
                if p.poll() is None:
                    p.terminate()
                p.communicate(timeout=20)

    # Claim: malformed header/count/meta/layout/size fields, trailing data, multiple
    # nonempty streams and EVERY truncation of a valid file fail closed. CLI refusal
    # creates no OUT and leaves IN unchanged; a valid control passes in test_expansion.
    def test_refusals(self):
        original, off = fixture()
        bad = {'magic': (0, 0), 'version': (4, 4), 'tokens': (8, 0xffffffff),
               'n_stream zero': (off['streams'], 0), 'n_stream two': (off['streams'], 2),
               'empty first stream': (off['cells'], 0), 'too many cells': (off['cells'], 5),
               'two sequences': (off['meta0']+4, 2), 'negative position': (off['meta0'], 0xffffffff),
               'duplicate position': (off['meta1'], 0), 'decreasing position': (off['meta2'], 0),
               'v_trans unknown': (off['trans'], 2), 'layer count': (off['attn_layers'], 0),
               'key type': (off['key_type'], 99), 'key size unaligned': (off['key_size'], 5),
               'key size aligned mismatch': (off['key_size'], 8),
               'key size zero': (off['key_size'], 0), 'value size': (off['value_size'], 8),
               'rec cell count': (off['rec_cells'], 2), 'rec metadata': (off['rec_meta']+4, 1),
               'rec trans': (off['rec_trans'], 1), 'rec layers': (off['rec_layers'], 1),
               'R size': (off['r_size'], 12), 'S size': (off['s_size'], 20)}
        cases = {label: original[:pos]+u32(value)+original[pos+4:] for label, (pos, value) in bad.items()}
        cases['trailing'] = original + b'junk'
        payload = original[off['cells']:off['insertion']]
        cases['two nonempty streams'] = (original[:off['streams']] + u32(2) + payload + payload
                                        + original[off['insertion']:])
        cases['already restreamed'] = (original[:off['streams']] + u32(2) + payload + u32(0)
                                      + original[off['insertion']:])
        transposed, at = fixture(trans=1)
        cases['transposed element mismatch'] = (transposed[:at['value_element']] + u32(4)
                                               + transposed[at['value_element']+4:])
        for n in range(len(original)):
            with self.subTest(truncated_at=n), self.assertRaises(kitlib.SlotError):
                self.parse(original[:n])
        for name, data in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as d:
                src, dst = Path(d)/'in', Path(d)/'out'
                src.write_bytes(data)
                result = run('restream-slot', str(src), str(dst), '--streams', '4')
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('restream-slot:', result.stderr)
                self.assertFalse(dst.exists())
                self.assertEqual(src.read_bytes(), data)
                self.assertEqual(list(Path(d).iterdir()), [src])

    # Claim: aliases/previous outputs/invalid stream counts and insufficient space
    # never overwrite IN or OUT; failed publication removes its temporary file.
    def test_path_disk_and_publish_refusals(self):
        original, _ = fixture()
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d)/'in', Path(d)/'out'
            src.write_bytes(original)
            for target in (src, dst):
                if target == dst:
                    dst.symlink_to(src)
                with self.assertRaises(kitlib.SlotError):
                    kitlib.restream_slot(src, target, 4)
            dst.unlink()
            dst.write_bytes(b'keep previous output')
            with self.assertRaises(kitlib.SlotError):
                kitlib.restream_slot(src, dst, 4)
            self.assertEqual(dst.read_bytes(), b'keep previous output')
            dst.unlink()
            os.link(src, dst)
            with self.assertRaises(kitlib.SlotError):
                kitlib.restream_slot(src, dst, 4)
            dst.unlink()
            for streams in (0, -1, 257):
                with self.assertRaises(kitlib.SlotError):
                    kitlib.restream_slot(src, dst, streams)
            with patch.object(kitlib.shutil, 'disk_usage') as space:
                space.return_value.free = 0
                with self.assertRaisesRegex(OSError, 'free disk') as raised:
                    kitlib.restream_slot(src, dst, 4)
                self.assertEqual(raised.exception.errno, errno.ENOSPC)
            with patch.object(kitlib.os, 'link', side_effect=OSError('copy/publish failure')):
                with self.assertRaises(OSError):
                    kitlib.restream_slot(src, dst, 4)
            self.assertEqual(src.read_bytes(), original)
            self.assertEqual(list(Path(d).iterdir()), [src])


class PowerMode(unittest.TestCase):
    # Claim: stored pmset samples cover legacy and macOS 26 modes; a known value 1 means low power and wins over
    # anything else; known values that all say off give 0; missing keys or unknown values give None (unknown) with
    # a warning, never 0. These are parser fixtures, not measurements from this Linux host.
    def test_samples(self):
        samples = Path(__file__).parent/'fixtures'
        for name, expected in (('pmset-legacy.txt', 1), ('pmset-26.txt', 1), ('pmset-absent.txt', None)):
            with self.subTest(sample=name), contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(kitlib.low_power_mode((samples/name).read_text()), expected)
                self.assertEqual('neither' in err.getvalue(), name == 'pmset-absent.txt')
        for value, expected in ((0, 0), (1, 1), (2, 0)):
            self.assertEqual(kitlib.low_power_mode(' powermode %d\n' % value), expected)
        self.assertEqual(kitlib.low_power_mode(' lowpowermode 0\n'), 0)
        self.assertEqual(kitlib.low_power_mode(' lowpowermode 0\n powermode 1\n'), 1)
        for key in ('lowpowermode', 'powermode'):
            for value in ('3', '-1', 'future'):
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertIsNone(kitlib.low_power_mode(' %s %s\n' % (key, value)))
                self.assertIn('unknown pmset', err.getvalue())
        # A known "on" is still reported when another key is unknown; a known "off" next to an unknown value is not
        # enough to say it is off.
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(kitlib.low_power_mode(' lowpowermode 1\n powermode 3\n'), 1)
            self.assertIsNone(kitlib.low_power_mode(' lowpowermode 0\n powermode 3\n'))


if __name__ == '__main__':
    unittest.main()
