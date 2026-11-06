#!/usr/bin/env python3
"""Rebuild pinned evidence from local Git objects; no fetch, checkout or archive."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];STORE=ROOT/'calc/tests/data/history-evidence'
PORT_FILES=('calc/run22/README.md','calc/run23/README.md','calc/tests/test_run12.py','bench/tests/test_mac_import.py','bench/tests/test_restream.py','calc/run25/export.py','calc/run25/finish.py','calc/run26/export.py','calc/run22/export.py','calc/run23/export.py','calc/run24/export.py','calc/run24/curves.py','calc/tests/r14_publication.py','calc/tests/r15_sentences.py')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def disk():
    free=int(subprocess.check_output(['df','-B1','--output=avail',str(ROOT)],text=True).splitlines()[-1]);assert free>28*1024**3,('disk below28GiB',free)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,env=dict(os.environ,GIT_NO_LAZY_FETCH='1'))
def refresh_code():
    files={n:sha((ROOT/n).read_bytes())for n in PORT_FILES}
    raw=(json.dumps({'basis':'explicit provenance adapters and r22d portable-test migrations; computation/input files have no exception','files':files},indent=2)+'\n').encode()
    (STORE/'port-code.json').write_bytes(raw)
    p=ROOT/'calc/history_evidence.py';s=p.read_text();s=re.sub(r"PORT_SHA256='[^']+'",f"PORT_SHA256='{sha(raw)}'",s);p.write_text(s)

def generate(check=False):
    disk();spec=json.loads((STORE/'revisions.json').read_text());revisions={};objects={};current={}
    for full,info in spec['revisions'].items():
        files={}
        for row in git('ls-tree','-rlz',full).split(b'\0'):
            if not row:continue
            header,name=row.split(b'\t',1);mode,kind,oid,size=header.decode().split();name=name.decode()
            assert kind=='blob',('unsupported submodule',full,name)
            files[name]={'oid':oid,'mode':mode,'bytes':int(size)};objects.setdefault(oid,[]).append((full,name))
        revisions[full]={'aliases':info['aliases'],'used_by':info['used_by'],'files':files}
    anchor=revisions[spec['base']]['files']
    (STORE/'objects').mkdir(exist_ok=True)
    process=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    packed_total=0
    for number,(oid,uses)in enumerate(objects.items(),1):
        process.stdin.write((oid+'\n').encode());process.stdin.flush();header=process.stdout.readline().decode().split();assert header[0]==oid and header[1]=='blob'
        size=int(header[2]);raw=process.stdout.read(size);assert len(raw)==size and process.stdout.read(1)==b'\n';digest=sha(raw);packed=None
        for full,name in uses:
            entry=revisions[full]['files'][name];entry['sha256']=digest
            # Canonical references are tied to the fixed accepted anchor,
            # not the mutable working tree, so release edits cannot drift them.
            same_anchor=name in anchor and anchor[name]['oid']==oid
            immutable=name.startswith(('calc/out/','data/measurements/','calc/hybridcalc/data/'))
            textual=Path(name).suffix in ('.py','.json','.csv','.tex','.md')
            if same_anchor and immutable:entry['canonical']=name
            elif textual or size<=10*1024*1024:
                if packed is None:packed=gzip.compress(raw,compresslevel=9,mtime=0)
                target=STORE/'objects'/(digest+'.gz');entry.update(object=target.name,compressed_sha256=sha(packed))
                if check:assert target.read_bytes()==packed,('fixture content drift',full,name)
                elif not target.exists():disk();target.write_bytes(packed);packed_total+=len(packed)
        if number%500==0:print('objects',number,'of',len(objects),'new compressed bytes',packed_total,flush=True)
    process.stdin.close();assert process.wait()==0
    result={'schema':1,'producer_base':spec['base'],'revisions':revisions};raw=gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),compresslevel=9,mtime=0)
    ports=(json.dumps({'basis':'explicit provenance adapters and r22d portable-test migrations; computation/input files have no exception','files':{n:sha((ROOT/n).read_bytes())for n in PORT_FILES}},indent=2)+'\n').encode()
    if check:
        assert (STORE/'manifest.json.gz').read_bytes()==raw,'history fixture manifest drift';assert (STORE/'port-code.json').read_bytes()==ports,'adapter code pin drift'
    else:
        disk();(STORE/'manifest.json.gz').write_bytes(raw);(STORE/'port-code.json').write_bytes(ports)
        p=ROOT/'calc/history_evidence.py';s=p.read_text();s=re.sub(r"MANIFEST_SHA256='[^']+'",f"MANIFEST_SHA256='{sha(raw)}'",s);s=re.sub(r"PORT_SHA256='[^']+'",f"PORT_SHA256='{sha(ports)}'",s);p.write_text(s)
    print(json.dumps({'revisions':len(revisions),'unique_blobs':len(objects),'manifest_bytes':len(raw),'new_compressed_bytes':packed_total,'check':check}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--code-only',action='store_true');args=p.parse_args();refresh_code()if args.code_only else generate(args.check)
