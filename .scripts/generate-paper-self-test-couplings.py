#!/usr/bin/env python3
"""Freeze exact finite diagnostic couplings from literal publication loci.

This authoring command never calls missing(). It predicts each existing digit
plant's affected verbatim predicates from their explicitly declared paragraphs.
Runtime self-tests still require every exact declared diagnostic and reject
extras, missing predicates, non-applied plants and pending-inventory changes.
"""
import hashlib,importlib.util,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'paper/data'),str(ROOT/'calc')]
import offload_bound as off
texts={p.name:p.read_text()for p in off.SECTIONS.glob('*.tex')};expected=off.expected();coupled={}
for name,(f,marker,w)in expected.items():
 m=re.search(r'\d',w);bad=w[:m.start()]+str((int(m[0])+1)%10)+w[m.end():]if m else'ПОДМЕНА '+w.split(maxsplit=1)[-1]
 part=next(p for p in texts[f].split('\n\n')if marker in p)
 changed,n=re.subn(r'\s+'.join(map(re.escape,w.split())),lambda _:bad,part,count=1);assert n==1 and changed!=part,name
 altered=texts[f].replace(part,changed,1);affected=[]
 for other,(of,om,ow)in expected.items():
  if of!=f:continue
  locus=next((p for p in altered.split('\n\n')if om in p),None)
  if locus is None or not re.search(r'\s+'.join(map(re.escape,ow.split())),locus):affected.append(other)
 assert name in affected,(name,affected)
 if affected!=[name]:coupled[name]={'diagnostics':affected,'reason':'Finite verbatim predicates overlap in this owner-authorized publication locus; every named diagnostic remains mandatory.'}
p=ROOT/'data/measurements/paper-v5d11-2026-11-06/self-test-couplings.json';p.write_text(json.dumps(coupled,ensure_ascii=False,indent=2)+'\n');raw=p.read_bytes();source=ROOT/'paper/data/offload_bound.py';source.write_text(re.sub(r"SELF_TEST_COUPLINGS_SHA256='[^']+'","SELF_TEST_COUPLINGS_SHA256='"+hashlib.sha256(raw).hexdigest()+"'",source.read_text()));print(json.dumps({'coupled_plants':len(coupled),'named_sites':len(expected)}))
