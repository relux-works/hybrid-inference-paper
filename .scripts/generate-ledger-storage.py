#!/usr/bin/env python3
"""Rebuild the declared representation from accepted local Git; never fetch."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'calc'))
import history_evidence as history
SOURCES={'calc/ENGINE-QUOTES-R22-261103.csv':'9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0','calc/ENGINE-QUOTES-R23-261104.csv':'9064701a9a07bd2726f76cefb6a05aa6aa428c0d'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main(check):
    import ledger_storage as storage
    if check:
        rows=storage.registry()
        if set(rows)!=set(SOURCES):raise ValueError('undeclared ledger transform')
        for name,rev in SOURCES.items():
            row=rows[name];entry=history.manifest()['revisions'][rev]['files'][name]
            if row['source_revision']!=rev or row['source_blob']!=entry['oid'] or row['content_bytes']!=entry['bytes'] or row['content_sha256']!=history.snapshot_hash(rev,name):raise ValueError('accepted ledger provenance changed')
            storage.read_bytes(ROOT/name)
        print('two accepted ledger transforms and available Git originals verified');return
    rows={}
    for name,rev in SOURCES.items():
        expected=history.snapshot_hash(rev,name);target=ROOT/(name+'.gz')
        if not history.private_available(rev):raise ValueError('local accepted Git original required for generation')
        fd,pending=tempfile.mkstemp(prefix='ledger-',suffix='.gz',dir=target.parent);os.close(fd);pending=Path(pending)
        proc=subprocess.Popen(['git','show',rev+':'+name],cwd=ROOT,stdout=subprocess.PIPE)
        h=hashlib.sha256();size=0
        with pending.open('wb')as out,gzip.GzipFile(filename='',mode='wb',fileobj=out,compresslevel=9,mtime=0)as packed:
            while block:=proc.stdout.read(1024*1024):h.update(block);size+=len(block);packed.write(block)
        proc.stdout.close()
        if proc.wait()!=0 or h.hexdigest()!=expected:
            pending.unlink();raise ValueError('accepted Git content mismatch')
        os.replace(pending,target)
        rows[name]={'transform':storage.TRANSFORM,'source_revision':rev,'source_path':name,'source_blob':history.manifest()['revisions'][rev]['files'][name]['oid'],'content_bytes':size,'content_sha256':expected,'stored_path':name+'.gz','gzip_sha256':sha(target.read_bytes()),'gzip_bytes':target.stat().st_size}
    raw=(json.dumps({'schema':1,'compression':'gzip, level 9, no filename, mtime 0, one member','files':rows},indent=2)+'\n').encode();storage.REGISTRY.write_bytes(raw)
    p=ROOT/'calc/ledger_storage.py';p.write_text(re.sub(r"REGISTRY_SHA256='[^']+'",f"REGISTRY_SHA256='{sha(raw)}'",p.read_text()))
    print(json.dumps(rows,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');main(parser.parse_args().check)
