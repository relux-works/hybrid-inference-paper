#!/usr/bin/env python3
"""Fail on every introduced blob >=100 MiB; warn for blobs >50 MiB."""
import argparse,subprocess,sys
LIMIT=104857600
WARNING=52428800

def check(base,target,cwd=None):
    listing=subprocess.run(['git','rev-list','--objects',base+'..'+target],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if listing.returncode:raise RuntimeError(listing.stderr.decode())
    metadata=subprocess.run(['git','cat-file','--batch-check=%(objecttype) %(objectsize) %(rest)'],cwd=cwd,input=listing.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if metadata.returncode:raise RuntimeError(metadata.stderr.decode())
    failures=[];largest={'path':'','bytes':0};blobs=0
    for line in metadata.stdout.decode().splitlines():
        parts=line.split(' ',2)
        if len(parts)<2:raise ValueError('invalid object metadata: '+line)
        if parts[0]!='blob':continue
        size=int(parts[1]);path=parts[2]if len(parts)>2 else '<unnamed>';blobs+=1
        if size>largest['bytes']:largest={'path':path,'bytes':size}
        if size>WARNING:print(f'WARNING introduced blob: {path} {size} B',flush=True)
        if size>=LIMIT:
            failures.append({'path':path,'bytes':size});print(f'FAIL introduced blob: {path} {size} B (limit {LIMIT} B)',flush=True)
    print(f'Introduced blobs checked: {blobs}; largest: {largest["path"]} {largest["bytes"]} B; failures: {len(failures)}',flush=True)
    return {'blobs':blobs,'largest':largest,'failures':failures}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base');p.add_argument('target');args=p.parse_args()
    try:result=check(args.base,args.target)
    except (OSError,ValueError,RuntimeError)as exc:print(str(exc),file=sys.stderr);sys.exit(2)
    sys.exit(1 if result['failures']else 0)
