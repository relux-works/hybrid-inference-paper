"""CPU-only R17 exporter, frozen-byte audit and complete changed-cell ledger."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run
from hybridcalc.export import generator_identity, write_tables

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run17'
BASE='e51942d3'
CASES=(('architectures-r17','architectures'),('paper-tables-r17','f32'),('paper-tables-r17-bf16','bf16'))
LEDGER=ROOT/'calc/ENGINE-QUOTES-R17-261103.csv'


import history_evidence as history

def read(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


def frozen():
    names=history.snapshot_paths(BASE,'calc/out')
    historical_roots={str(Path(n).parent).split('/')[2] for n in names}
    current={str(p.relative_to(ROOT)) for p in (ROOT/'calc/out').rglob('*') if p.is_file() and OUT not in p.parents and p.relative_to(ROOT/'calc/out').parts[0] in historical_roots}
    assert set(names)==current,'changed historical file set'
    for name in names:
        assert history.digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),name+' changed historical bytes'
    return len(names)


def accepted_generator_identity():
    accepted='714fe72135819ededd7c270dd661c1359acfa6c3'
    names=history.snapshot_paths(accepted,'hybridcalc.py','calc/hybridcalc')
    names=[n for n in names if n.endswith('.py') or n.startswith('calc/hybridcalc/data/') and n.endswith('.json')]
    return {n:hashlib.sha256(history.snapshot_object(accepted+':'+n)).hexdigest() for n in names}


def verify_tables():
    files=set();identity=accepted_generator_identity()
    for scenario,folder in CASES:
        manifests=list((OUT/folder).glob('*_manifest.json'))
        assert len(manifests)==1,(folder,'manifest count')
        manifest=json.loads(manifests[0].read_text())
        assert manifest['scenario']==scenario,(folder,'scenario mismatch')
        assert manifest['generator']==identity,(folder,'stale generator')
        for name,digest in manifest['files'].items():
            p=OUT/folder/name
            assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(folder,name,'changed export bytes')
            files.add(str(p.relative_to(OUT)))
        files.add(str(manifests[0].relative_to(OUT)))
    assert files=={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file() and p.name!='INDEX.json'},'run17 file set'
    return len(files)


def changed_cells():
    result=[]
    coords=('model','role','client','basis','team','profile','depth','delta','state_format','link_mbit','streams','agents','downstream_mb_s','fixed_mb','kv_kib_token')
    for _,folder in CASES:
        for p in sorted((OUT/folder).glob('*.csv')):
            old=(ROOT/'calc/out/run16/base'/p.name) if folder=='f32' else OUT/'f32'/p.name
            before=read(old) if folder!='architectures' and old.exists() else []
            after=read(p)
            assert not before or len(before)==len(after),(str(p),'row identity changed')
            for i,b in enumerate(after):
                a=before[i] if before else {}
                for column in sorted(b):
                    if a.get(column,'<absent>')!=b[column]:
                        key=p.name+'[row={}].{}; '.format(i,column)+'; '.join(k+'='+b[k] for k in coords if k in b)
                        result.append(dict(paper_site='engine replacement; report R17 tables; paper prose unchanged',engine_key=key,
                            old=a.get(column,'<absent>'),new=b[column],source=str(p.relative_to(ROOT)),
                            comparison='r16_to_r17_f32' if folder=='f32' else 'r17_f32_to_bf16' if folder=='bf16' else 'new_architecture_estimate'))
    return result+facts_quotes()


def facts_quotes():
    """Six FACTS cells round an already-rounded kit display a second time."""
    from hybridcalc.measurements_r17 import Surface, config
    result=[]
    for model,depth,metric,printed in (
            ('qwen27',50000,'decode','57.3'),('qwen27',150000,'delta512','1382'),
            ('gemma31',150000,'delta512','746'),('gemma31',249000,'delta2000','511'),
            ('glimmer30',16000,'segment','4468'),('glimmer30',118000,'delta10000','2936')):
        s=Surface(model,'server')
        if metric=='decode':
            value=sum(r['predicted_n']*1000/r['predicted_ms'] for r in s.turns if r['level']==depth)/3
        elif metric=='segment':
            r=next(r for r in s.records if r['kind']=='segment' and r['depth']==depth)
            value=r['prompt_n']*1000/r['prompt_ms']
        else:value=s.for_delta(depth,int(metric[5:]))
        result.append(dict(paper_site='data/measurements/run16-2026-11-03/FACTS-261103.md section1a; R17 rounding correction',
            engine_key='model={}; depth={}; metric={}; raw tok/s before single rounding'.format(model,depth,metric),
            old=printed,new=str(value),source=config()['sources'][model+'_server']['path']+'::'+s.source,
            comparison='facts_double_round_to_raw_once'))
    return result


def verify_quotes(records):
    fields=('source','engine_key','old','new','comparison')
    expected={tuple(r[k] for k in fields) for r in changed_cells()}
    actual={tuple(r[k] for k in fields) for r in records}
    assert len(actual)==len(records),'duplicate quote cells'
    assert expected==actual,'unreported or forged changed cells'
    return len(expected)


def main():
    assert sys.argv[1:] in ([],['--audit-only'])
    print('frozen',frozen(),flush=True)
    if not sys.argv[1:]:
        for scenario,folder in CASES:
            m=write_tables(run(scenario),OUT/folder)
            print(scenario,len(m['tables']),'tables',m['alarm_cells'],'explicit alarm cells',flush=True)
        records=changed_cells()
        with LEDGER.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
        index=dict(baseline=BASE,generator=generator_identity(),frozen_files=frozen(),
            files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'})
        (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('verified new files',verify_tables(),flush=True)
    print('quote cells',verify_quotes(read(LEDGER)),flush=True)
    index=json.loads((OUT/'INDEX.json').read_text())
    assert index['generator']==accepted_generator_identity(),'stale index'
    assert index['files']=={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'},'index mismatch'
    print('frozen after',frozen(),flush=True)


if __name__=='__main__':main()
