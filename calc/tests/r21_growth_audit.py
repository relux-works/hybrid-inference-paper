"""Run21-only export, immutable history and coordinate-qualified quote ledger."""
import csv
import hashlib
import io
import json
import os
import tempfile
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.growing_r21 import calculate
from hybridcalc.export import generator_identity,write_tables

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run21/growing'
BASE='b6ac5abcdf60b72582be87c7ad075ee460e7cc78'
LEDGER=ROOT/'calc/ENGINE-QUOTES-R21-GROWING-261103.csv'


import history_evidence as history

def extend_main_identity(directory,current):
    """Only an unused new module may extend the conservative global identity.

    Existing numeric sources/payloads must be byte-identical. This is a
    metadata-only addition; changed old code requires actual recomputation.
    """
    manifest_path=directory/'r21_manifest.json';index_path=directory/'INDEX.json'
    manifest=json.loads(manifest_path.read_text());index=json.loads(index_path.read_text());before=manifest['generator']
    assert all(current.get(k)==v for k,v in before.items()),'changed existing numerical source; recomputation required'
    added=set(current)-set(before)
    assert added in (set(),{'calc/hybridcalc/growing_r21.py'}),'unexpected generator extension'
    assert index['generator']==before,'stale main index before extension'
    for name,digest in index['files'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest,'changed main payload before extension'
    if not added:return dict(added=[],numeric_changes=0)
    manifest['generator']=current;index['generator']=current
    content=json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    index['files']['r21_manifest.json']=hashlib.sha256(content.encode()).hexdigest()
    with tempfile.TemporaryDirectory(dir=directory)as tmp:
        p=Path(tmp);(p/'r21_manifest.json').write_text(content)
        (p/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
        os.replace(p/'r21_manifest.json',manifest_path);os.replace(p/'INDEX.json',index_path)
    return dict(added=sorted(added),numeric_changes=0)


def read(p):return list(csv.DictReader(io.StringIO(p.read_text())))


def frozen():
    names=history.snapshot_paths(BASE,'calc/out')
    # R14 authorizes R20 labels; r14_publication separately checks its cells.
    names=[n for n in names if not n.startswith('calc/out/run20/')]
    historical_roots={Path(n).parts[2] for n in names}
    current={str(p.relative_to(ROOT)) for p in (ROOT/'calc/out').rglob('*') if p.is_file() and OUT not in p.parents and p.relative_to(ROOT/'calc/out').parts[0] in historical_roots}
    assert current==set(names),'historical export file set changed'
    for name in names:
        assert history.digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),name+' changed historical bytes'
    for name in ('calc/hybridcalc/data/workload.json','calc/hybridcalc/data/sampler.json','data/measurements/ivmbp-2026-10-30/stats.json'):
        assert history.digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),name+' changed existing profile bytes'
    return len(names)


def quote_cells():
    records=[]
    coords=('profile','model','server','target_depth','team','tasks_day','client_basis','billing','link')
    for p in sorted(OUT.glob('*.csv')):
        for index,row in enumerate(read(p)):
            for key,value in row.items():
                records.append(dict(paper_site='Run21 report; paper prose unchanged',
                    engine_key=p.name+'[row={}].{}; '.format(index,key)+'; '.join(k+'='+row[k] for k in coords if k in row),
                    old='<new growing-task projection>',new=value,source=str(p.relative_to(ROOT)),comparison='new_run21'))
    return records


def verify_quotes(records):
    fields=('source','engine_key','old','new','comparison')
    expected={tuple(r[k] for k in fields) for r in quote_cells()}
    actual={tuple(r[k] for k in fields) for r in records}
    assert len(actual)==len(records) and actual==expected,'unreported or forged quote coordinates'
    return len(records)


def verify_tables():
    p=OUT/'growth21_manifest.json';m=json.loads(p.read_text())
    assert m['scenario']=='million-growth-r21','wrong scenario'
    assert m['generator']==generator_identity(),'stale generator'
    from r21_export_labels import verify
    verify(OUT,'growth21','growing_api_admission')
    for name,digest in m['files'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name+' changed export bytes'
    assert set(m['files'])|{p.name,'INDEX.json'}=={p.name for p in OUT.iterdir() if p.is_file()},'run21 file set'
    return len(m['files'])+1


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen before',frozen(),flush=True)
    if not sys.argv[1:]:
        print('main identity extension',extend_main_identity(ROOT/'calc/out/run21',generator_identity()),flush=True)
        result=calculate()
        m=write_tables(result,OUT)
        from r21_export_labels import apply
        apply(OUT,'growth21','growing_api_admission')
        print('tables',len(m['tables']),'explicit alarm cells',m['alarm_cells'],flush=True)
        records=quote_cells()
        with LEDGER.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
        index=dict(baseline=BASE,generator=generator_identity(),frozen_files=frozen(),
            files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='INDEX.json'})
        (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('new files',verify_tables(),flush=True)
    print('quote records',verify_quotes(read(LEDGER)),flush=True)
    index=json.loads((OUT/'INDEX.json').read_text())
    assert index['generator']==generator_identity(),'stale index'
    assert index['files']=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='INDEX.json'},'index file mismatch'
    print('frozen after',frozen(),flush=True)


if __name__=='__main__':main()
