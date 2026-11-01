#!/usr/bin/env python3
"""Helpers for the benchmark kit scripts. Python 3.8+, standard library only.

  kitlib.py restream-slot IN OUT --streams N
      Validate a c21284cd hybrid sequence file and expand one attention stream to N.
      IN is read-only; OUT must not exist. Print both SHA-256 values.
  kitlib.py low-power-mode
      Read pmset -g from stdin; print 1 when low power is on, 0 when a known value says it is off, and unknown
      (with a warning) when pmset reports no known value.
  kitlib.py depth-list CTX
      The depth ladder for one slot of CTX tokens: 16k, 50k, 100k, 150k and 200k where they fit, then the deepest
      level that still leaves room for the three turn deltas and their decoded tokens (249k at 262,144, as in the
      reference run).
  kitlib.py check-jsonl FILE...
      Exit 1 if a benchmark record says error or interrupted, or a parallel round is invalid; warn about rounds whose
      restored slot was not reused.
  kitlib.py scrub-pack --results DIR --stage DIR --replace OLD=NEW ... [--user NAME] [--host NAME ...] [--meta K=V ...]
      Copy DIR into STAGE with every OLD path replaced by NEW (longest first, only at path boundaries), the user and
      host names masked, and MANIFEST.json written. Exit 3 without a manifest, listing where, if after masking any
      of these remains: an absolute path under a personal-looking root, the user or host name as a word inside a
      path, a file with an unexpected type, or a subdirectory. Paths inside the kit's own folders, already replaced
      by <kit>, <work>, <models> or <results>, are not checked again. --allow PATH (repeatable) accepts a listed path
      the owner has looked at; MANIFEST.json records it.
"""
import argparse
import datetime
import errno
import hashlib
import json
import struct
import tempfile
import os
import re
import shutil
import signal
import sys

DELTAS = (512, 2000, 10000)
GEN = 128
BASE_LEVELS = (16000, 50000, 100000, 150000, 200000)
TEXT_SUFFIXES = ('.log', '.txt', '.md', '.json', '.jsonl', '.csv', '.out')
# Absolute paths under these roots usually name a person or an organisation; none may remain in an archive. There is
# deliberately no left boundary, so paths glued to compiler flags (-I/data/..., -L/scratch/...) are caught as well.
PERSONAL = re.compile(r'/(?:home|Users|data|scratch|mnt|Volumes|media|srv|workspace|root|private|nfs|work)/[^\s:\'",)\]]+')
PATH_TOKEN = re.compile(r'/[^\s\'"<>:,;()\[\]]+')
URL = re.compile(r'\bhttps?://\S+', re.I)
# Account and host names that identify nobody (cloud images, containers, ordinary words in the kit's own paths); the
# name check skips them, and host masking leaves them alone.
GENERIC_NAMES = {'root', 'ubuntu', 'admin', 'user', 'runner', 'debian', 'ec2-user', 'centos', 'cloud-user', 'nvidia',
                 'jovyan', 'coder', 'vscode', 'app', 'docker', 'ec2', 'azureuser', 'gpu', 'localhost', 'linux', 'server',
                 'build', 'llama', 'qwen', 'host', 'node', 'worker', 'instance', 'container', 'default', 'machine',
                 'workstation', 'desktop', 'laptop', 'studio', 'macbook', 'mac', 'compute', 'box', 'models', 'work',
                 'results', 'kit', 'bench', 'cuda'}
# Files Finder and exFAT drives add on a Mac; they are left out of the archive without an error.
SKIP_FILES = ('.DS_Store',)
SKIP_PREFIXES = ('._',)
# A replaced path may follow the start of a line, a separator or a compiler flag, never another path character.
LEFT = r'(?:(?<=^)|(?<=[\s"\'=:,(\[])|(?<=-I)|(?<=-L)|(?<=-isystem)|(?<=-Wl,))'


def depth_list(ctx):
    deepest = (ctx - sum(DELTAS) - GEN * len(DELTAS) - 32) // 1000 * 1000
    levels = [x for x in BASE_LEVELS if x <= deepest]
    # The deepest level that fits is added unless it is within 10% of the last base level.
    if deepest >= BASE_LEVELS[0] and (not levels or deepest > levels[-1] * 1.1):
        levels.append(deepest)
    return ','.join('%dk' % (x // 1000) for x in levels)


def check_jsonl(paths):
    bad, warn = [], []
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as f:
            for n, line in enumerate(f, 1):
                try:
                    r = json.loads(line)
                except ValueError:
                    bad.append('%s:%d: unreadable record' % (os.path.basename(path), n))
                    continue
                kind = r.get('kind')
                if kind in ('error', 'interrupted'):
                    bad.append('%s:%d: %s %s' % (os.path.basename(path), n, kind, r.get('error', '')))
                elif kind == 'round' and r.get('valid') is False:
                    bad.append('%s:%d: invalid round with %s streams' % (os.path.basename(path), n, r.get('streams')))
                elif kind == 'round' and r.get('restore_reused') is False:
                    warn.append('%s:%d: round with %s streams re-read the context (restore_reused false)'
                                % (os.path.basename(path), n, r.get('streams')))
                elif kind == 'round' and r.get('rereads'):
                    warn.append('%s:%d: round with %s sessions had %s calls that re-read the context'
                                % (os.path.basename(path), n, r.get('agents') or r.get('streams'), r.get('rereads')))
    for w in warn:
        print('warning: ' + w)
    for b in bad:
        print('error: ' + b)
    return 1 if bad else 0


def boundary_replace(text, old, new):
    """Replace old only where it is a whole path: after a separator or a compiler flag, and followed by '/', the end
    or a non-path character."""
    if not old or old == '/':
        return text
    return re.sub(LEFT + re.escape(old) + r'(?=/|$|[^\w.-])', lambda m: new, text, flags=re.M)


# Placeholders the kit itself writes for its own folders. Paths that continue one of them were scrubbed already; paths
# after "~", "<user>", "<host>" or any other ">" are checked like every other path.
KIT_PLACEHOLDERS = ('<kit>', '<work>', '<models>', '<results>')


USED_ALLOW = set()


def allowed(token, allow):
    """True when the owner accepted this path or a folder above it; empty and root entries accept nothing. Entries
    that accepted something are remembered, so the manifest records only those."""
    for a in allow:
        b = a.rstrip('/')
        if b and (token == b or token.startswith(b + '/')):
            USED_ALLOW.add(a)
            return True
    return False


def leaks(line, names, allow=()):
    """Personal paths, and paths that hold one of names as a word (case-insensitive), in one line of text."""
    line = URL.sub(' ', line)
    found = []
    for m in PERSONAL.finditer(line):
        token = m.group(0)
        if not line[:m.start()].endswith(KIT_PLACEHOLDERS) and not allowed(token, allow):
            found.append(token)
    for m in PATH_TOKEN.finditer(line):
        token = m.group(0)
        if line[:m.start()].endswith(KIT_PLACEHOLDERS) or allowed(token, allow) or token in found:
            continue
        low = token.lower()
        if any(re.search(r'(?<![a-z])' + re.escape(n) + r'(?![a-z])', low) for n in names):
            found.append(token)
    return found


def scrub_pack(args):
    pairs = []
    for item in args.replace:
        old, _, new = item.partition('=')
        old = old.rstrip('/')
        if old and old != '/' and old not in [p[0] for p in pairs]:
            pairs.append((old, new))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    user = args.user if args.user and len(args.user) >= 2 else None
    hosts = sorted({h for h in args.host if h and len(h) >= 3}, key=len, reverse=True)
    names = sorted({n.lower() for n in [user or ''] + hosts if len(n) >= 3 and n.lower() not in GENERIC_NAMES})
    hosts = [h for h in hosts if h.lower() not in GENERIC_NAMES]
    if os.path.exists(args.stage):
        shutil.rmtree(args.stage)
    os.makedirs(args.stage)
    problems = []
    for name in sorted(os.listdir(args.results)):
        src = os.path.join(args.results, name)
        if name == 'MANIFEST.json' or name in SKIP_FILES or name.startswith(SKIP_PREFIXES):
            continue
        if not os.path.isfile(src):
            problems.append('%s: a subdirectory or special file in results/; move it out or ask the owner' % name)
            continue
        dst = os.path.join(args.stage, name)
        if not name.endswith(TEXT_SUFFIXES):
            problems.append('%s: a file of a type the kit does not write; move it out or ask the owner' % name)
            continue
        with open(src, encoding='utf-8', errors='replace') as f:
            text = f.read()
        for old, new in pairs:
            text = boundary_replace(text, old, new)
        if user:
            text = re.sub(r'(?<=/)' + re.escape(user) + r'(?=/|$|[^\w.-])', '<user>', text, flags=re.M)
        for host in hosts:
            text = re.sub(r'(?<![\w.-])' + re.escape(host) + r'(?![\w-])', '<host>', text)
        for n, line in enumerate(text.splitlines(), 1):
            for leak in leaks(line, names, args.allow):
                problems.append('%s:%d: %s' % (name, n, leak))
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(text)
    if problems:
        print('Personal-looking paths or unexpected files remain after scrubbing; the archive was not made.')
        print('Show this list to the owner. Paths the owner accepts can be allowed with SCRUB_ALLOW (see the prompt):')
        for p in problems[:50]:
            print('  ' + p)
        if len(problems) > 50:
            print('  ... and %d more' % (len(problems) - 50))
        return 3
    files = {}
    for name in sorted(os.listdir(args.stage)):
        path = os.path.join(args.stage, name)
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for block in iter(lambda: f.read(1 << 20), b''):
                h.update(block)
        files[name] = {'bytes': os.path.getsize(path), 'sha256': h.hexdigest()}
    manifest = {'created_utc': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
                .isoformat().replace('+00:00', 'Z')}
    for item in args.meta:
        k, _, v = item.partition('=')
        manifest[k] = v
    if USED_ALLOW:
        manifest['scrub_allowed'] = sorted(USED_ALLOW)
    manifest['files'] = files
    with open(os.path.join(args.stage, 'MANIFEST.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    return 0



# Pinned to llama.cpp c21284cd, sequence magic GGSQ/version 3. The file has no model
# descriptor: accept the kit's dense-attention + recurrent hybrid layout, without PLE
# history or missing V tensors. No scanning for byte markers or opaque tail copying.
SLOT_MAGIC = 0x67677371
# ggml type -> (block width, block bytes), cache types supported by this kit/parser.
CACHE_TYPES = {0: (1, 4), 1: (1, 2), 30: (1, 2), 2: (32, 18),
               3: (32, 20), 6: (32, 22), 7: (32, 24), 8: (32, 34)}


class SlotError(ValueError):
    pass


class SlotReader:
    def __init__(self, file):
        self.file = file
        self.size = os.fstat(file.fileno()).st_size
        file.seek(0)

    def take(self, n):
        if n < 0 or n > self.size - self.file.tell():
            raise SlotError('truncation or size field exceeds file')
        self.file.seek(n, 1)

    def number(self, fmt):
        n = struct.calcsize('<' + fmt)
        if n > self.size - self.file.tell():
            raise SlotError('truncated scalar')
        return struct.unpack('<' + fmt, self.file.read(n))[0]

    def u32(self):
        return self.number('I')

    def row(self, cells, recurrent=False):
        typ, size = self.number('i'), self.number('Q')
        if typ not in CACHE_TYPES or (recurrent and typ != 0):
            raise SlotError('unsupported tensor type')
        if size == 0 or size % CACHE_TYPES[typ][1]:
            raise SlotError('invalid tensor row size')
        self.take(cells * size)
        return typ, size


def _parse_slot(file, cell_ext):
    r = SlotReader(file)
    if r.u32() != SLOT_MAGIC or r.u32() != 3:
        raise SlotError('wrong sequence magic or version (expected c21284cd version 3)')
    tokens = r.u32()
    if not tokens:
        raise SlotError('empty token list')
    r.take(4 * tokens)
    stream_offset = file.tell()
    streams = r.u32()
    if not 1 <= streams <= 256:
        raise SlotError('unsupported stream count')
    nonempty, insertion, attention_layers = 0, None, None
    source_seq = None
    counts = []
    for stream in range(streams):
        cells = r.u32()
        counts.append(cells)
        if not cells:
            continue
        nonempty += 1
        if nonempty > 1 or stream != 0 or cells > tokens:
            raise SlotError('expected exactly one non-empty first stream')
        previous = -1
        for _ in range(cells):
            pos, nseq = r.number('i'), r.u32()
            if pos <= previous or pos >= tokens or nseq != 1:
                raise SlotError('invalid single-sequence attention metadata')
            previous = pos
            r.take(cell_ext)  # llama_kv_cell_ext: i32 x, y, tok, or absent
            seq = r.number('i')
            if seq < 0 or (source_seq is not None and source_seq != seq):
                raise SlotError('multiple or invalid sequence ids')
            source_seq = seq
        v_trans, layers = r.u32(), r.u32()
        if v_trans not in (0, 1):
            raise SlotError('unknown v_trans layout')
        if not 1 <= layers <= 1024:
            raise SlotError('invalid attention layer count')
        attention_layers = layers
        keys = [r.row(cells) for _ in range(layers)]
        if len(set(keys)) != 1:
            raise SlotError('inconsistent key row sizes/types')
        values = []
        for _ in range(layers):
            if not v_trans:
                values.append(r.row(cells))
            else:
                typ, element, embd = r.number('i'), r.u32(), r.u32()
                if typ not in (0, 1, 30) or element != CACHE_TYPES[typ][1] or not embd:
                    raise SlotError('unknown v_trans element layout or size')
                r.take(cells * element * embd)
                values.append((typ, element, embd))
        if len(set(values)) != 1:
            raise SlotError('inconsistent value row sizes/types')
        insertion = file.tell()
    if nonempty != 1:
        raise SlotError('expected one non-empty stream')
    # A sequence save writes one recurrent cell, no seq ids, then s_trans=0 and
    # the TOTAL layer count. Qwen hybrids have R and S only on recurrent layers.
    if r.u32() != 1:
        raise SlotError('expected one recurrent cell')
    pos, nseq = r.number('i'), r.u32()
    if pos != previous or nseq != 0:
        raise SlotError('invalid recurrent sequence metadata')
    s_trans, total_layers = r.u32(), r.u32()
    if s_trans != 0 or not attention_layers < total_layers <= 1024:
        raise SlotError('unsupported recurrent layout/layer count')
    recurrent_layers = total_layers - attention_layers
    for _ in range(2):  # all R rows, then all S rows; no PLE conv-history rows
        rows = [r.row(1, recurrent=True) for _ in range(recurrent_layers)]
        if len(set(rows)) != 1:
            raise SlotError('inconsistent recurrent row sizes/types')
    if file.tell() != r.size:
        raise SlotError('trailing bytes or unsupported hybrid layout')
    return dict(token_words=tokens, streams=streams, counts=counts, stream_offset=stream_offset,
                insertion=insertion, cell_ext=cell_ext, bytes=r.size)


def parse_slot(file):
    # has_cell_ext() is not serialized. Require exactly one full valid interpretation.
    valid, errors = [], []
    for ext in (0, 12):
        try:
            valid.append(_parse_slot(file, ext))
        except SlotError as e:
            errors.append(str(e))
    if len(valid) != 1:
        raise SlotError('ambiguous or unsupported slot: ' + '; '.join(errors))
    return valid[0]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def restream_slot(src, dst, streams, input_sha256=None):
    # The step hashes its unchanged import once and reuses it across fallback attempts.
    if input_sha256 is not None and not re.fullmatch(r'[0-9a-f]{64}', input_sha256):
        raise SlotError('invalid cached IN sha256')
    if not 1 <= streams <= 256:
        raise SlotError('streams must be between 1 and 256')
    if os.path.realpath(src) == os.path.realpath(dst) or os.path.lexists(dst):
        raise SlotError('OUT must be a new path, distinct from IN')
    tmp = None
    try:
        with open(src, 'rb') as original:
            info = parse_slot(original)
            if info['streams'] != 1:
                raise SlotError('IN n_stream must be 1')
            expected = info['bytes'] + 4 * (streams - 1)
            parent = os.path.dirname(os.path.abspath(dst))
            if shutil.disk_usage(parent).free < expected:
                raise OSError(errno.ENOSPC, 'not enough free disk for restreamed slot')
            with tempfile.NamedTemporaryFile(dir=parent, prefix='.restream-', delete=False) as out:
                tmp = out.name
                original.seek(0)
                # Copy bounded chunks; slots may be tens of GB on a 64 GB Mac.
                def copy(n):
                    while n:
                        block = original.read(min(n, 1 << 20))
                        if not block:
                            raise SlotError('IN truncated during copy')
                        out.write(block)
                        n -= len(block)
                copy(info['stream_offset'])
                original.seek(4, 1)
                out.write(struct.pack('<I', streams))
                copy(info['insertion'] - original.tell())
                out.write(b'\0' * (4 * (streams - 1)))
                copy(info['bytes'] - original.tell())
                if out.tell() != expected or original.read(1):
                    raise SlotError('length changed during restream')
            with open(tmp, 'rb') as candidate:
                check = parse_slot(candidate)
            if check['streams'] != streams or check['counts'] != [info['counts'][0]] + [0] * (streams - 1):
                raise SlotError('output stream layout mismatch')
            # Exclusive publication also refuses an OUT created since the initial check.
            os.link(tmp, dst)
            print('IN  sha256 %s  %s' % (input_sha256 or sha256_file(src), src))
            print('OUT sha256 %s  %s' % (sha256_file(dst), dst))
            return 0
    finally:
        if tmp is not None:
            os.unlink(tmp)


def low_power_mode(text):
    """Legacy lowpowermode or macOS 26 powermode: 1 if any known value says low power, 0 if known values all say
    it is off, None when pmset reports no known value (missing keys or values this kit does not know)."""
    known, unknown = [], []
    for key, value in re.findall(r'^\s*(lowpowermode|powermode)\s+(\S+)\s*$', text, re.M):
        if (key == 'lowpowermode' and value not in ('0', '1')) or value not in ('0', '1', '2'):
            unknown.append('%s %s' % (key, value))
        else:
            known.append(int(value == '1'))
    if any(known):
        return 1
    if unknown:
        print('warning: unknown pmset value (%s); low_power_mode recorded as unknown' % ', '.join(unknown),
              file=sys.stderr)
        return None
    if not known:
        print('warning: pmset reports neither lowpowermode nor powermode; low_power_mode recorded as unknown',
              file=sys.stderr)
        return None
    return 0


def main():
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    d = sub.add_parser('depth-list')
    d.add_argument('ctx', type=int)
    c = sub.add_parser('check-jsonl')
    c.add_argument('paths', nargs='*')
    s = sub.add_parser('scrub-pack')
    s.add_argument('--results', required=True)
    s.add_argument('--stage', required=True)
    s.add_argument('--replace', action='append', default=[])
    s.add_argument('--user')
    s.add_argument('--host', action='append', default=[])
    s.add_argument('--meta', action='append', default=[])
    s.add_argument('--allow', action='append', default=[])
    r = sub.add_parser('restream-slot')
    r.add_argument('src')
    r.add_argument('dst')
    r.add_argument('--streams', type=int, required=True)
    r.add_argument('--input-sha256', help='reuse a SHA-256 already computed for the unchanged IN file')
    sub.add_parser('low-power-mode')
    args = ap.parse_args()
    if args.cmd == 'restream-slot':
        try:
            return restream_slot(args.src, args.dst, args.streams, args.input_sha256)
        except (OSError, ValueError) as e:
            print('restream-slot: ' + str(e), file=sys.stderr)
            return 3 if isinstance(e, OSError) and e.errno == errno.ENOSPC else 1
    if args.cmd == 'low-power-mode':
        mode = low_power_mode(sys.stdin.read())
        print('unknown' if mode is None else mode)
        return 0
    if args.cmd == 'depth-list':
        print(depth_list(args.ctx))
        return 0
    if args.cmd == 'check-jsonl':
        return check_jsonl(args.paths)
    if args.cmd == 'scrub-pack':
        return scrub_pack(args)
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
