"""Exactly two accepted CSV-to-single-gzip custody transforms.

Compressed identity authenticates committed bytes; content identity authenticates
historical CSV bytes. Regeneration retains an existing content-authenticated gzip when
its regenerated content matches, independent of the interpreter's zlib build.
"""
from contextlib import contextmanager
from pathlib import Path
import gzip,hashlib,io,json,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'calc/ledger-storage.json'
REGISTRY_SHA256='9cbc02a48739fe0ab5560fd68ac61fd87f12408a48d9adfd8db881db908d9534'
TRANSFORM='accepted-csv-to-single-gzip-v1'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def registry():
    raw=REGISTRY.read_bytes()
    if digest(raw)!=REGISTRY_SHA256:raise ValueError('ledger registry SHA256 mismatch')
    return json.loads(raw)['files']

def logical_name(path):
    try:name=str(Path(path).relative_to(ROOT))
    except ValueError:return None
    files=registry()
    if name in files:return name
    return next((n for n,r in files.items()if r['stored_path']==name),None)

def physical(path):
    name=logical_name(path)
    if name is None:return Path(path)
    row=registry()[name];plain=ROOT/name;packed=ROOT/row['stored_path']
    if plain.exists() or plain.is_symlink():raise ValueError('plain ledger path forbidden (dual representation or unmigrated): '+name)
    return packed

def decode(raw):
    # One member, no optional name/time/header fields, no trailing bytes. zlib
    # verifies the member CRC and length; unused_data rejects concatenated gzip.
    if raw[:9]!=b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02':raise ValueError('noncanonical gzip header')
    decoder=zlib.decompressobj(31)
    try:content=decoder.decompress(raw)+decoder.flush()
    except zlib.error as exc:raise ValueError('invalid gzip member') from exc
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('truncated or multi-member gzip')
    return content

def validate(raw,row,committed=True):
    content=decode(raw)
    if len(content)!=row['content_bytes'] or digest(content)!=row['content_sha256']:raise ValueError('accepted ledger content mismatch')
    if committed and digest(raw)!=row['gzip_sha256']:raise ValueError('committed ledger gzip SHA256 mismatch')
    return content

def read_bytes(path,committed=True):
    name=logical_name(path)
    if name is None:return Path(path).read_bytes()
    return validate(physical(path).read_bytes(),registry()[name],committed=committed)

def read_text(path):
    # Export/regeneration compares accepted CSV content. Historical custody uses
    # read_bytes's default committed=True and independently pins gzip bytes.
    return read_bytes(path,committed=False).decode('utf-8')

def historical_names(names):
    # Path-set equivalence is finite: a third rename is never accepted.
    aliases={r['stored_path']:n for n,r in registry().items()}
    normalized=[aliases.get(n,n)for n in names]
    if len(set(normalized))!=len(normalized):raise ValueError('dual ledger representation in index')
    return sorted(normalized)

def expanded_prefixes(prefixes):
    return tuple(prefixes)+tuple(r['stored_path']for n,r in registry().items()if n in prefixes)

@contextmanager
def open_text(path,mode='w',newline=''):
    name=logical_name(path)
    if name is None or mode!='w':raise ValueError('only declared ledger writes are supported')
    target=physical(path);row=registry()[name]
    with tempfile.TemporaryDirectory(prefix='ledger-gzip-')as tmp:
        pending=Path(tmp)/'ledger.gz'
        with pending.open('wb')as raw:
            with gzip.GzipFile(filename='',fileobj=raw,mode='wb',compresslevel=9,mtime=0)as packed:
                with io.TextIOWrapper(packed,encoding='utf-8',newline=newline)as text:yield text
        validate(pending.read_bytes(),row,committed=False)
        if target.exists():
            # Preserve existing content-authenticated compression, rather than a
            # zlib-dependent rewrite. Custody separately pins committed bytes.
            validate(target.read_bytes(),row,committed=False)
        else:
            with pending.open('rb')as src,target.open('wb')as dst:
                while block:=src.read(1024*1024):dst.write(block)
