"""Pinned historical provenance without a private-history runtime dependency.

Hashes bind frozen bytes; canonical/compressed content supports semantic old/new
comparisons. Available private objects cross-check the same pinned evidence.
"""
from pathlib import Path
import gzip,hashlib,json,os,subprocess
import ledger_storage as ledgers
ROOT=Path(__file__).resolve().parents[1]
STORE=ROOT/'calc/tests/data/history-evidence'
MANIFEST_SHA256='447ef9b00a4f372adae2718e543f1f2fee3e2cf175806f11796601057104abfb'
PORT_SHA256='be5e658192cd8cdee59fd4cddf3961b988384f8b836f59296f7f8cc70fa78f69'
ACCEPTED_PAPER='f33c5df3d650e2f09dd6c498d44711eb393331eb'
_manifest=None
_manifest_stamp=None
_checked=set()
_announced=set()
_available={}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def payload(path):
    path=Path(path)
    return os.readlink(path).encode() if path.is_symlink() else ledgers.read_bytes(path)
def manifest():
    global _manifest,_manifest_stamp
    stat=(STORE/'manifest.json.gz').stat();stamp=(str(STORE),stat.st_size,stat.st_mtime_ns)
    if _manifest is not None and stamp==_manifest_stamp:return _manifest
    raw=(STORE/'manifest.json.gz').read_bytes()
    assert digest(raw)==MANIFEST_SHA256,'history evidence manifest SHA256 mismatch'
    _manifest=json.loads(gzip.decompress(raw));_manifest_stamp=stamp
    return _manifest

def revision(value):
    rows=manifest()['revisions'];found=[r for r,v in rows.items() if value==r or value in v['aliases']]
    assert len(found)==1,('unknown historical revision',value)
    return found[0]

def _git(*args,input=None):
    # This is the only production private-object gateway. No fetch is allowed.
    return subprocess.check_output(['git',*args],cwd=ROOT,input=input,env=dict(os.environ,GIT_NO_LAZY_FETCH='1'))

def private_available(value):
    full=revision(value);key=(full,os.environ.get('GIT_DIR'),os.environ.get('PATH'))
    if key not in _available:
        probe=_git('cat-file','--batch-check',input=(full+'^{commit}\n').encode()).decode().strip()
        if probe==full+'^{commit} missing':present=False
        else:
            fields=probe.split();assert len(fields)==3 and fields[0]==full and fields[1]=='commit',('invalid Git availability result',probe)
            present=True
        _available[key]=present
        if key not in _announced:
            print('history evidence: '+full+'; '+('private Git cross-check'if present else'fixture mode (private object absent)'),flush=True);_announced.add(key)
    return _available[key]

def _selected(files,prefixes):
    return sorted(n for n in files if not prefixes or any(n==p or n.startswith(p.rstrip('/')+'/')for p in prefixes))

def snapshot_paths(value,*prefixes):
    full=revision(value);row=manifest()['revisions'][full];names=_selected(row['files'],prefixes)
    assert names,('empty history selection',value,prefixes)
    key=('paths',full,prefixes,os.environ.get('GIT_DIR'),os.environ.get('PATH'))
    if private_available(full) and key not in _checked:
        actual=[]
        for item in _git('ls-tree','-rlz',full,*prefixes).split(b'\0'):
            if not item:continue
            header,name=item.split(b'\t',1);mode,kind,oid,size=header.decode().split();name=name.decode();actual.append(name)
            entry=row['files'][name]
            assert kind=='blob' and (mode,oid,int(size))==(entry['mode'],entry['oid'],entry['bytes']),('history object metadata differs from private Git',full,name)
        assert actual==names,('history file set differs from private Git',full,prefixes);_checked.add(key)
    return names

def snapshot_hash(value,name):
    full=revision(value);entry=manifest()['revisions'][full]['files'][str(name)]
    key=('blob',entry['oid'],os.environ.get('GIT_DIR'),os.environ.get('PATH'))
    if private_available(full) and key not in _checked:
        raw=_git('show',full+':'+str(name))
        assert len(raw)==entry['bytes'] and digest(raw)==entry['sha256'],('history fixture differs from private Git',full,name);_checked.add(key)
    return entry['sha256']

def snapshot_read(value,name):
    full=revision(value);entry=manifest()['revisions'][full]['files'][str(name)]
    expected=snapshot_hash(full,name)
    if entry.get('canonical'):
        raw=payload(ROOT/entry['canonical'])
    else:
        assert entry.get('object'),('history content not provisioned',full,name)
        packed=(STORE/'objects'/entry['object']).read_bytes()
        assert digest(packed)==entry['compressed_sha256'],('history content compressed SHA256 mismatch',full,name)
        raw=gzip.decompress(packed)
    assert len(raw)==entry['bytes'] and digest(raw)==expected,('history content SHA256 mismatch',full,name)
    return raw

def snapshot_object(spec):
    value,name=spec.split(':',1)
    return snapshot_read(value,name)

def port_hashes():
    raw=(STORE/'port-code.json').read_bytes();assert digest(raw)==PORT_SHA256,'port-code pin mismatch'
    return json.loads(raw)['files']

def expected_current_hash(value,name,allow_ports=False):
    old=snapshot_hash(value,name)
    return port_hashes().get(str(name),old)if allow_ports else old

def accepted_identity(value,current):
    # Historical producer hashes stay historical. Current adapters are checked
    # independently; computational/input bytes have no permitted migration.
    old={name:snapshot_hash(value,name)for name in current}
    for name,actual in current.items():
        assert actual==expected_current_hash(value,name,True),('unapproved current producer/input bytes',name)
    return old

def historical_code_hash(name):
    old=snapshot_hash(ACCEPTED_PAPER,name)
    assert digest(payload(ROOT/name))==expected_current_hash(ACCEPTED_PAPER,name,True),('unapproved history adapter bytes',name)
    return old

def unchanged(value,*prefixes,allow_ports=False):
    names=snapshot_paths(value,*prefixes)
    current=ledgers.historical_names(_git('ls-files','--',*ledgers.expanded_prefixes(prefixes)).decode().splitlines())
    assert current==names,('changed historical path set',value,prefixes)
    for name in names:
        path=ledgers.physical(ROOT/name)
        mode='120000' if path.is_symlink() else '100755' if path.stat().st_mode&0o100 else '100644'
        assert mode==manifest()['revisions'][revision(value)]['files'][name]['mode'],('changed historical mode',name)
        assert digest(payload(ROOT/name))==expected_current_hash(value,name,allow_ports),('changed historical bytes',name)
    return ''


def verify_all():
    seen=set();counts={'revisions':0,'private_crosschecks':0,'fixture_revisions':0,'content_blobs':0,'hash_only_blobs':0}
    for full,row in manifest()['revisions'].items():
        names=snapshot_paths(full);counts['revisions']+=1
        counts['private_crosschecks'if private_available(full)else'fixture_revisions']+=1
        for name in names:
            entry=row['files'][name];snapshot_hash(full,name)
            if entry['sha256'] in seen:continue
            seen.add(entry['sha256'])
            if entry.get('canonical')or entry.get('object'):
                snapshot_read(full,name);counts['content_blobs']+=1
            else:counts['hash_only_blobs']+=1
    port_hashes()
    return counts

# New engines freeze a whole sibling tree. Keep its original bytes in history;
# each pre-existing/current paper divergence must have an exact explicit successor.
ENGINE_PARENT_MIGRATIONS_SHA256='2aa30d0296df38e86a191069694dd16fcbb225c6f4d7aadff7bac226249f7485'

def engine_parent_migrations():
    raw=(STORE/'engine-parent-migrations.json').read_bytes()
    assert digest(raw)==ENGINE_PARENT_MIGRATIONS_SHA256,'engine parent migration pin mismatch'
    return json.loads(raw)

def verify_current_manifest():
    lines=(ROOT/'MANIFEST.sha256').read_text().splitlines()
    found={}
    for line in lines:
        checksum,name=line.split('  ',1);name=name.removeprefix('./')
        assert name not in found,('duplicate manifest entry',name)
        found[name]=checksum
    expected=_git('ls-files',':!MANIFEST.sha256').decode().splitlines()
    assert sorted(found)==sorted(expected),'current manifest path set changed'
    for name,value in found.items():
        assert digest((ROOT/name).read_bytes())==value,('current manifest hash changed',name)

def verify_engine_parent(value):
    full=revision(value);names=snapshot_paths(full);rows=engine_parent_migrations()['revisions'][full];ports=port_hashes()
    for name in names:
        original=snapshot_hash(full,name);path=ledgers.physical(ROOT/name)
        mode='120000'if path.is_symlink()else'100755'if path.stat().st_mode&0o100 else'100644'
        assert mode==manifest()['revisions'][full]['files'][name]['mode'],('parent mode changed',name)
        if name=='MANIFEST.sha256':
            assert digest(snapshot_read(full,name))==original
            verify_current_manifest();continue
        current=digest(payload(ROOT/name))
        if name in ports:assert current==ports[name],('unapproved current parent adapter',name)
        elif name in rows:
            row=rows[name];assert row['original_sha256']==original,('original parent changed',name)
            assert snapshot_hash(engine_parent_migrations()['accepted_paper_baseline'],name)==row['accepted_paper_sha256'],('accepted paper baseline changed',name)
            assert current==row['current_sha256'],('unapproved paper migration',name)
        else:assert current==original,('accepted engine parent bytes changed',name)
    assert set(rows)<=set(names),'migration outside original parent'
    return names
