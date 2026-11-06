"""Run19-only export, immutable history and coordinate-qualified quote ledger."""
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
OUT=ROOT/'calc/out/run19'
BASE='f7aeef958fc3e61a178ce345daa163c769545cbb'
LEDGER=ROOT/'calc/ENGINE-QUOTES-R19-261103.csv'


import history_evidence as history

def generator_identity():
    # Run20 freezes the predecessor producer identity; R19 review pending at branching.
    head='3a1eed0dbb7962bca082e5941e0853122ae70a5e'
    names=history.snapshot_paths(head,'hybridcalc.py','calc/hybridcalc')
    names=[n for n in names if n.endswith('.py') or n.startswith('calc/hybridcalc/data/') and n.endswith('.json')]
    return {n:hashlib.sha256(history.snapshot_object(head+':'+n)).hexdigest() for n in names}


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
    coords=('client','node','tier','link','depth','delta','team','billing','option','hourly_usd')
    for p in sorted(OUT.glob('*.csv')):
        for index,row in enumerate(read(p)):
            for key,value in row.items():
                records.append(dict(paper_site='Run19 report; paper prose unchanged',
                    engine_key=p.name+'[row={}].{}; '.format(index,key)+'; '.join(k+'='+row[k] for k in coords if k in row),
                    old='<new 5090 node comparison>',new=value,source=str(p.relative_to(ROOT)),comparison='new_run19'))
    from hybridcalc.measurements_r19 import config,checked_price
    for row in checked_price(config())['sources']:
        records.append(dict(paper_site='Run19 bought card price evidence',engine_key=row['title'],old='<not previously priced>',
            new=str(row['price_usd']),source=row['url'],comparison='verified_public_price'))
    return records


def verify_quotes(records):
    fields=('source','engine_key','old','new','comparison')
    expected={tuple(r[k] for k in fields) for r in quote_cells()}
    actual={tuple(r[k] for k in fields) for r in records}
    assert len(actual)==len(records) and actual==expected,'unreported or forged quote coordinates'
    return len(records)


def verify_tables():
    p=OUT/'r19_manifest.json';m=json.loads(p.read_text())
    assert m['scenario']=='prefill-nodes-r19','wrong scenario'
    assert m['generator']==generator_identity(),'stale generator'
    for name,digest in m['files'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name+' changed export bytes'
    assert set(m['files'])|{p.name,'INDEX.json'}=={p.name for p in OUT.iterdir() if p.is_file()},'run19 file set'
    return len(m['files'])+1


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen before',frozen(),flush=True)
    if not sys.argv[1:]:
        m=write_tables(run('prefill-nodes-r19'),OUT)
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
