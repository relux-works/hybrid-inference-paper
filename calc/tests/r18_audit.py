"""Run18-only export, immutable history and coordinate-qualified quote ledger."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run
from hybridcalc.export import write_tables

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run18'
BASE='714fe72135819ededd7c270dd661c1359acfa6c3'
REWORK_BASE='12f0c042bfdfbb12206ff83e30c223920f3ca372'
LEDGER=ROOT/'calc/ENGINE-QUOTES-R18-261103.csv'
FROZEN_HEAD='f7aeef958fc3e61a178ce345daa163c769545cbb'


import history_evidence as history

def generator_identity():
    # R19 freezes the supplied r10c producer head; review was pending at branching.
    names=history.snapshot_paths(FROZEN_HEAD,'hybridcalc.py','calc/hybridcalc')
    names=[n for n in names if n.endswith('.py') or n.startswith('calc/hybridcalc/data/') and n.endswith('.json')]
    return {n:hashlib.sha256(history.snapshot_object(FROZEN_HEAD+':'+n)).hexdigest() for n in names}



def read(p):return list(csv.DictReader(io.StringIO(p.read_text())))


def frozen():
    names=history.snapshot_paths(BASE,'calc/out')
    historical_roots={Path(n).parts[2] for n in names}
    current={str(p.relative_to(ROOT)) for p in (ROOT/'calc/out').rglob('*') if p.is_file() and OUT not in p.parents and p.relative_to(ROOT/'calc/out').parts[0] in historical_roots}
    assert current==set(names),'historical export file set changed'
    for name in names:
        assert history.digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),name+' changed historical bytes'
    return len(names)


def quote_cells():
    records=[]
    coords=('client','model','state_format','depth','actual_depth','delta','streams','server_np','workload','price_case','billing')
    for p in sorted(OUT.glob('*.csv')):
        old_text=history.snapshot_object(REWORK_BASE+':'+str(p.relative_to(ROOT))).decode()
        previous=list(csv.DictReader(io.StringIO(old_text)))
        for index,row in enumerate(read(p)):
            for key,value in row.items():
                record=dict(paper_site='new Run18 table; paper prose unchanged',
                    engine_key=p.name+'[row={}].{}; '.format(index,key)+'; '.join(k+'='+row[k] for k in coords if k in row),
                    old='<new GPU/rental comparison>',new=value,source=str(p.relative_to(ROOT)),comparison='new_run18')
                records.append(record)
                if previous[index][key]!=value:
                    records.append(dict(record,paper_site='R18 CUDA import review correction; paper prose unchanged',
                        old=previous[index][key],comparison='r18_cuda_import_rework_vs_'+REWORK_BASE[:8]))
    from hybridcalc.measurements_r18 import config
    for name,info in config()['sources'].items():
        if info.get('facts_previous_abbreviation'):
            records.append(dict(paper_site='FACTS section2 archive checksum; canonical correction2026-11-03',
                engine_key=name+'.sha256',old=info['facts_previous_abbreviation'],new=info['sha256'],
                source=info['path'],comparison='recorded_FACTS_checksum_correction'))
    return records


def verify_quotes(records):
    fields=('source','engine_key','old','new','comparison')
    expected={tuple(r[k] for k in fields) for r in quote_cells()}
    actual={tuple(r[k] for k in fields) for r in records}
    assert len(actual)==len(records) and actual==expected,'unreported or forged quote coordinates'
    return len(records)


def verify_tables():
    p=OUT/'r18_manifest.json';m=json.loads(p.read_text())
    assert m['scenario']=='discrete-clients-r18','wrong scenario'
    assert m['generator']==generator_identity(),'stale generator'
    for name,digest in m['files'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name+' changed export bytes'
    assert set(m['files'])|{p.name,'INDEX.json'}=={p.name for p in OUT.iterdir() if p.is_file()},'run18 file set'
    return len(m['files'])+1


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen before',frozen(),flush=True)
    if not sys.argv[1:]:
        m=write_tables(run('discrete-clients-r18'),OUT)
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
