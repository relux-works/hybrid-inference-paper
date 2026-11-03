"""Offline run14 exports, immutable-history audit and paper-site replacements."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
from history_fixtures import snapshot_files, snapshot_read
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hybridcalc.engine import run
from hybridcalc.export import write_tables,generator_identity
from r11_audit import CASES

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calc/out/run14'
BASE='49a1c1d38233f8edbbc1150c3e28dd69adb72997'
R4='785334ab5d3ad145ecd9f6d2621d34e9a6314c24'


def frozen():
    counts={}
    for directory,count in (('calc/out/paper',150),('calc/out/run13',252)):
        files=snapshot_files('r13-exports', directory)
        names=sorted(files)
        assert len(names)==count,(directory,len(names))
        for name in names:
            old=files[name]
            assert (ROOT/name).read_bytes()==old,name
        assert set(names)=={str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file()}
        counts[directory]=len(names)
    return counts


def read(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


def write(path,records):
    with path.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(records)


def quotes():
    records=[]
    sections={str(p.relative_to(ROOT)):p.read_text() for p in (ROOT/'paper').rglob('*.tex')}
    for previous in sorted((ROOT/'calc/out/run13/base').glob('*.csv')):
        current=OUT/'base'/previous.name
        if not current.exists():continue
        before,after=read(previous),read(current)
        assert len(before)==len(after),(previous.name,'row coordinates changed')
        embedded=ROOT/'paper/data/engine'/previous.name
        paper_rows=read(embedded) if embedded.exists() else []
        for index,(a,b) in enumerate(zip(before,after)):
            for column,old in a.items():
                try:float(old)
                except (ValueError,TypeError):continue
                new=b[column]
                if old==new:continue
                source=str(current.relative_to(ROOT))
                # Include every changed engine cell, with precise embedded
                # table coordinates and actual TeX consumers when present.
                sites=['paper/data/engine/'+previous.name+'[row={}].{}'.format(index,column)]
                sites += [path+':'+str(i) for path,text in sections.items() for i,line in enumerate(text.splitlines(),1)
                          if previous.name in line]
                for site in sites:
                    records.append(dict(paper_site=site,engine_key=previous.name+'[row={}].{}'.format(index,column),
                                        old=old,new=new,paper_current=paper_rows[index].get(column,'') if index<len(paper_rows) else '',source=source))
    # Explicitly map the headline client gains discussed by the owner to the
    # tab:clients site even when the CSV is read through the table helper.
    old=read(ROOT/'calc/out/run13/base/client_sessions_day.csv')
    new=read(OUT/'base/client_sessions_day.csv')
    for a,b in zip(old,new):
        if a['gain']!=b['gain']:
            records.append(dict(paper_site='paper/sections/05-clients.tex :: tab:clients',engine_key=a['client']+'; link='+a['link_mbit']+' Mbit/s; gain',old=a['gain'],new=b['gain'],paper_current='see tab:clients',source='calc/out/run14/base/client_sessions_day.csv'))
    for record in records:record['comparison']='r13_to_r14_r5'
    # R5 must also expose changes to the R4-only tables and every earlier R14
    # output, so the writer can distinguish this correction from the R13 move.
    paths=sorted(snapshot_files('r14-r4', 'calc/out/run14'))
    for path in paths:
        if not path.endswith('.csv'):continue
        current=ROOT/path
        if not current.exists():continue
        before=list(csv.DictReader(io.StringIO(snapshot_read('r14-r4', path).decode())))
        after=read(current)
        assert len(before)==len(after),(path,'r4 row coordinates changed')
        for i,(a,b) in enumerate(zip(before,after)):
            for column,value in a.items():
                if column not in b or value==b[column]:continue
                records.append(dict(paper_site='engine correction :: '+path+'[row={}].{}'.format(i,column),
                    engine_key=Path(path).name+'[row={}].{}'.format(i,column),old=value,new=b[column],paper_current='see r13_to_r14_r5 / embedded paper data',source=path,comparison='r14_r4_to_r14_r5'))
    write(ROOT/'calc/ENGINE-QUOTES-R14-261102.csv',records)
    return len(records)


def changed_outputs():
    paths=sorted(snapshot_files('r14-r4', 'calc/out/run14'))
    records=[]
    for path in paths:
        old=snapshot_read('r14-r4', path)
        current=ROOT/path
        new=current.read_bytes() if current.exists() else b''
        if old!=new:records.append(dict(path=path,change='changed' if current.exists() else 'removed',r4_sha256=hashlib.sha256(old).hexdigest(),r5_sha256=hashlib.sha256(new).hexdigest()))
    for p in sorted(OUT.rglob('*')):
        path=str(p.relative_to(ROOT))
        if p.is_file() and path not in paths:records.append(dict(path=path,change='added',r4_sha256='',r5_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    write(ROOT/'calc/R14-R5-CHANGED-OUTPUTS-261102.csv',records)
    return len(records)


def conclusions():
    path='calc/out/run14/base/perimeter_cost.csv'
    before=list(csv.DictReader(io.StringIO(snapshot_read('r14-r4', path).decode())))
    after=read(ROOT/path)
    keys=('profile','team','route','client','basis')
    selected=lambda rs:{tuple(r[k] for k in keys):r for r in rs if r['selected']=='1' and r['route']!='Macs only'}
    old,new=selected(before),selected(after);records=[]
    for key,row in new.items():
        previous=old.get(key,{})
        records.append(dict(zip(keys,key),old_server=previous.get('server','gap: no selected admissible head'),new_server=row['server'],
            old_storage_tier='HBM resident' if row['route']=='all server' else 'RAM',new_storage_tier=row['storage_tier'],
            old_person_month=previous.get('person_month','nan'),new_person_month=row['person_month'],
            old_prefill_mean_s=previous.get('prefill_mean_s','nan'),new_prefill_mean_s=row['prefill_mean_s'],
            old_prefill_p90_s=previous.get('prefill_p90_s','nan'),new_prefill_p90_s=row['prefill_p90_s'],
            old_units=previous.get('units','nan'),new_units=row['units'],source=path))
    write(ROOT/'calc/R14-R5-CONCLUSIONS-261102.csv',records)
    return len(records)


def import_effect():
    """Isolate import from the depth correction on the identical R5 workload."""
    from hybridcalc.engine import load
    from hybridcalc.paper_tables import Context,client_table,offload_table
    from hybridcalc.measurements_r14 import agents_table
    scenario,inputs=load('paper-tables-r14');c=Context(scenario,inputs)
    c.client_import=lambda key='m3max':lambda tokens:0.0
    client_table(c);offload_table(c)
    tables={t['id']:t['rows'] for t in c.g.result('R5 zero-import sensitivity')['tables']}
    tables['client_agents_day']=agents_table(c)
    records=[]
    metrics=dict(client_sessions_day=('local_sessions_day','hybrid_sessions_day','gain'),
                 offload_by_link=('share_calls','saved_seconds_call','saved_seconds_offloaded'),
                 client_agents_day=('local_sessions_day','hybrid_sessions_day','gain','local_agent_s','hybrid_agent_s'))
    for table,before in tables.items():
        after=read(OUT/'base'/(table+'.csv'))
        assert len(before)==len(after)
        for index,(a,b) in enumerate(zip(before,after)):
            for metric in metrics[table]:
                if type(a[metric]) not in (int,float):continue
                new=float(b[metric]);old=a[metric]
                records.append(dict(table=table,row=index,client=b.get('client','M3 Max'),link_mbit=b['link_mbit'],
                    agents=b.get('agents','4' if table=='client_sessions_day' else ''),state_bits=b.get('state_bits',''),
                    metric=metric,no_import=old,with_import=new,delta=new-old))
    write(ROOT/'calc/R14-R5-IMPORT-EFFECT-261102.csv',records)
    return len(records)


def main():
    print('historical byte audit',frozen(),flush=True)
    write_tables(run('server-options-r14'),OUT/'measurements')
    for name,_ in CASES:
        scenario=name+'-r14'
        manifest=write_tables(run(scenario),OUT/'base')
        print(scenario,len(manifest['tables']),'tables',manifest['alarm_cells'],'explicit gap cells',flush=True)
    print('quotes',quotes(),flush=True)
    index=dict(baseline=BASE,generator=generator_identity(),frozen=frozen(),
               files={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='INDEX.json'})
    (OUT/'INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
    print('r4 changed/new outputs',changed_outputs(),flush=True)
    print('selected own-server/hybrid conclusions',conclusions(),flush=True)
    print('isolated import effect cells',import_effect(),flush=True)


if __name__=='__main__':main()
