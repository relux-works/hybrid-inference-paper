#!/usr/bin/env python3
"""Regenerate the frozen float-field schema with the reference interpreter only."""
import hashlib,json,platform,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'calc'),str(ROOT/'calc/tests')]
from hybridcalc.engine import run
from r11_audit import CASES
assert platform.python_implementation()=='CPython' and sys.version_info[:3]==(3,14,4),'use reference CPython3.14.4'
files={}
for name,_ in CASES:
    for t in run(name)['tables']:
        files[t['id']+'.csv']=[key for key in t['columns'] if any(type(row[key]) is float for row in t['rows']) and t['columns'][key]!='text']
assert len(files)==42
raw=(json.dumps({'reference':'CPython3.14.4','scope':'42 run12 design CSVs; integer lexemes, headers and text remain exact','files':files},indent=2,sort_keys=True)+'\n').encode()
p=ROOT/'calc/tests/data/regeneration-floats.json';p.write_bytes(raw)
p=ROOT/'calc/tests/regeneration.py';p.write_text(re.sub(r"SCHEMA_SHA256 = '[^']*'","SCHEMA_SHA256 = '"+hashlib.sha256(raw).hexdigest()+"'",p.read_text()))
print('Regeneration reference schema:',len(files),'files;',len(raw),'bytes')
