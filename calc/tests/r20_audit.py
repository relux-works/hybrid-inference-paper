"""Run20-only export, immutable history and coordinate-qualified quote ledger."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.engine import run
from hybridcalc.export import write_tables

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run20'
BASE='3a1eed0dbb7962bca082e5941e0853122ae70a5e'
LEDGER=ROOT/'calc/ENGINE-QUOTES-R20-261103.csv'


import history_evidence as history

def generator_identity():
    # Run21 freezes the predecessor producer identity; R20 review pending at branching.
    head='b6ac5abcdf60b72582be87c7ad075ee460e7cc78'
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
                records.append(dict(paper_site='Run20 report; paper prose unchanged',
                    engine_key=p.name+'[row={}].{}; '.format(index,key)+'; '.join(k+'='+row[k] for k in coords if k in row),
                    old='<new vLLM/admitted API comparison>',new=value,source=str(p.relative_to(ROOT)),comparison='new_run20'))
    return records


def verify_quotes(records):
    fields=('source','engine_key','old','new','comparison')
    expected={tuple(r[k] for k in fields) for r in quote_cells()}
    actual={tuple(r[k] for k in fields) for r in records}
    assert len(actual)==len(records) and actual==expected,'unreported or forged quote coordinates'
    return len(records)


def verify_tables():
    p=OUT/'r20_manifest.json';m=json.loads(p.read_text())
    assert m['scenario']=='server-economics-r20','wrong scenario'
    assert m['generator']==generator_identity(),'stale generator'
    from r14_publication import verify_labels20
    verify_labels20(OUT)
    for name,digest in m['files'].items():
        assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name+' changed export bytes'
    assert set(m['files'])|{p.name,'INDEX.json','batching_gain.svg','batching_figure.json'}=={p.name for p in OUT.iterdir() if p.is_file()},'run20 file set'
    return len(m['files'])+1


def verify_figure():
    meta=json.loads((OUT/'batching_figure.json').read_text())
    assert meta['source_sha256']==hashlib.sha256((OUT/'decode_scaling.csv').read_bytes()).hexdigest(),'figure source mismatch'
    assert meta['svg_sha256']==hashlib.sha256((OUT/'batching_gain.svg').read_bytes()).hexdigest(),'figure SVG mismatch'
    import xml.etree.ElementTree as ET
    ET.fromstring((OUT/'batching_gain.svg').read_bytes())
    return True


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen before',frozen(),flush=True)
    if not sys.argv[1:]:
        result=run('server-economics-r20')
        m=write_tables(result,OUT)
        from hybridcalc.figure_r20 import batching_svg
        table=next(t for t in result['tables'] if t['id']=='decode_scaling')
        svg=batching_svg(table['rows']);(OUT/'batching_gain.svg').write_text(svg)
        meta=dict(source='decode_scaling.csv',source_sha256=hashlib.sha256((OUT/'decode_scaling.csv').read_bytes()).hexdigest(),svg_sha256=hashlib.sha256(svg.encode()).hexdigest(),basis='modelled bandwidth/capacity; 1M extrapolation')
        (OUT/'batching_figure.json').write_text(json.dumps(meta,indent=2)+'\n')
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
    assert verify_figure()
    print('frozen after',frozen(),flush=True)


if __name__=='__main__':main()
