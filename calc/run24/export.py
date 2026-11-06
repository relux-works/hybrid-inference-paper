"""API-only run24 publication with immutable run13–23 and run23 hardware controls."""
import argparse,csv,hashlib,io,json,os,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'calc'))
from run24 import engine,inputs,sentences,api
from run23.export import source_identity as parent_identity

BASE='9064701a9a07bd2726f76cefb6a05aa6aa428c0d'
OUT=ROOT/'calc/out/run24';LEDGER=ROOT/'calc/ENGINE-QUOTES-R24-261105.csv'


import history_evidence as history

def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(x):return (json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def read(path):
    with path.open(newline='')as f:return list(csv.DictReader(f))


def csv_bytes(rows):
    columns=list(dict.fromkeys(k for r in rows for k in r));f=io.StringIO(newline='')
    w=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');w.writeheader()
    for row in rows:
        assert all(v is not None for v in row.values()),'unknown values must be explicit blank'
        w.writerow(row)
    return f.getvalue().encode()


def source_identity():
    paths=[p for p in (ROOT/'calc/run24').rglob('*')if p.is_file()]
    paths += [ROOT/k for k in parent_identity()]
    paths += [ROOT/'calc/tests/test_run24.py',ROOT/'calc/ENGINE-REPORT-QUOTES-R23-261104.csv',ROOT/'calc/out/run23/r23_manifest.json',ROOT/'calc/hybridcalc/data/run21-deep.json']
    return {str(p.relative_to(ROOT)):digest(p.read_bytes())for p in sorted(set(paths))}


def frozen():
    names=history.snapshot_paths(BASE,'calc/out')
    roots={Path(n).parts[2]for n in names}
    current={str(p.relative_to(ROOT))for p in (ROOT/'calc/out').rglob('*')if p.is_file()and p.relative_to(ROOT/'calc/out').parts[0]in roots}
    assert current==set(names),'historical export file set changed'
    for name in names:
        assert digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),'historical bytes changed: '+name
    return len(names)


def inherit():
    return [dict(source=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),basis='accepted run23 historical control, unchanged; new measured API overlays are separate')for p in sorted((ROOT/'calc/out/run23').rglob('*.csv'))]


def numeric(x):
    if x in ('True','False'):return True
    try:return __import__('math').isfinite(float(x))
    except (ValueError,TypeError):return False


def abstract_changes(tables):
    records=[];seen=set();cache={}
    for quote in read(ROOT/'calc/ENGINE-REPORT-QUOTES-R23-261104.csv'):
        coordinate=(quote['source'],quote['row'],quote['column'])
        if coordinate in seen:continue
        seen.add(coordinate);source,row,column=coordinate
        if source not in cache:cache[source]=read(ROOT/source)
        value=cache[source][int(row)][column];assert value==quote['source_value']
        records.append(dict(old_source=source,old_row=row,column=column,old=value,new_source=source,new_row=row,new=value,changed=False,
            why='inherited accepted run23 control unchanged, including hardware costs/routing and historical snapshot/owner981 basis; measured-cadence overlay is separate'))
    # Explicitly distinguish newly available measured points from a change to
    # the frozen owner981/snapshot control. No invented old measured value.
    for i,row in enumerate(tables['api_rankings']):
        if row['cache_point']!='measured':continue
        records.append(dict(old_source='run23 measured-provider interface pending',old_row='',column='usd_per_1000_calls',old='',
            new_source='calc/out/run24/api_rankings.csv',new_row=i,new=row['usd_per_1000_calls'],changed=row['usd_per_1000_calls']!='',
            why='final study measured point; cadence='+row['cadence']+', model='+row['model']+', profile='+row['profile']+', tier='+row['scope_tier']+', role='+row['role']+'; no qualified provider remains unknown'))
    for i,row in enumerate(tables['measured_crossings']):
        if row['comparison_kind']!='same-model Qwen comparison'or not all(str(row[k])==v for k,v in dict(scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8').items()):continue
        records.append(dict(old_source='accepted run23 owner981 snapshot control',old_row='',column='statement',old=row['historical_owner_981_statement'],
            new_source='calc/out/run24/measured_crossings.csv',new_row=i,new=row['statement'],changed=row['statement']!=row['historical_owner_981_statement'],
            why='different API point/admission/cohort, not a hardware or causal cache-only change; cadence='+row['cadence']+', profile='+row['profile']+', load='+row['load']+', billing='+row['billing']+', role='+row['api_role']))
    return records


def paper_tables(tables):
    out={'api_rankings':tables['api_rankings'],'million_measured':tables['million_measured']}
    for name in ('measured_crossings','measured_multiples','shared_measured_crossings'):
        out[name]=[r for r in tables[name]if r['comparison_kind']=='same-model Qwen comparison'and r['scope_tier']=='measured_ladder']
    return out


def quote_records():
    out=[]
    selected={'api_rankings.csv','million_measured.csv','abstract_bound_changes.csv'}
    for p in sorted(OUT.rglob('*.csv')):
        if p.name not in selected and p.parent.name!='paper':continue
        for index,row in enumerate(read(p)):
            for column,value in row.items():
                if column not in ('sentence','short_sentence','statement')and not numeric(value)and p.name not in selected:continue
                out.append(dict(source=str(p.relative_to(ROOT)),row=index,column=column,value=value))
    return out


def verify():
    m=json.loads((OUT/'r24_manifest.json').read_text());assert m['base']==BASE and m['source']==history.accepted_identity('ca7f228acd789380bf46016fd87acc33e1b07aef',source_identity()),'stale run24 source/input'
    assert set(m['files'])|{'r24_manifest.json'}=={str(p.relative_to(OUT))for p in OUT.rglob('*')if p.is_file()},'run24 file set'
    for name,h in m['files'].items():assert digest((OUT/name).read_bytes())==h,'changed run24 export '+name
    for row in read(OUT/'baseline_inheritance.csv'):assert digest((ROOT/row['source']).read_bytes())==row['sha256'],'run23 control changed'
    for row in read(OUT/'api_prices.csv'):
        if row['availability_source']=='measured_whole_window'and float(row['availability_percent'])<95:
            assert row['admitted']=='False'and row['effective_usd_per_1000_calls']=='','under95 endpoint admitted/priced'
    for path in (OUT/'paper').glob('*.csv'):
        for row in read(path):
            if 'server'in row:
                assert row['server']in sentences.inherited.SERVERS,'paper forbidden server'
                assert row['api_model']==inputs.QWEN and row['comparison_kind']=='same-model Qwen comparison','paper cross-model claim'
                sentences.validate(row['sentence'],row);sentences.validate(row['short_sentence'],row,True)
    required={(r['source'],r['row'],r['column'])for r in read(ROOT/'calc/ENGINE-REPORT-QUOTES-R23-261104.csv')}
    coverage={(r['old_source'],r['old_row'],r['column'])for r in read(OUT/'abstract_bound_changes.csv')}
    assert required<=coverage,'missing abstract-bound run23 coordinate, including quoted sentences'
    raw=read(OUT/'million_measured.csv')
    for row in raw:
        if row['model']==inputs.QWEN:assert row['usd_per_1000_calls']==''and row['qualified_providers']=='0','invented qualified Qwen1M point'
        else:assert row['qualified_providers']=='15'and abs(float(row['usd_per_1000_calls'])-60.35482127067251)<1e-10,'wrong GLM1M aggregate'
    expected=quote_records();assert read(LEDGER)==[{k:str(v)for k,v in r.items()}for r in expected],'missing/changed API quote coordinate'
    return dict(historical_files=frozen(),new_files=len(m['files'])+1,quote_cells=len(expected))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audit-only',action='store_true');args=p.parse_args()
    if not args.audit_only:
        identity=source_identity();assert frozen()==1046
        tables=engine.calculate();tables['baseline_inheritance']=inherit();tables['abstract_bound_changes']=abstract_changes(tables)
        payload={name+'.csv':csv_bytes(rows)for name,rows in tables.items()}
        payload.update({'paper/'+name+'.csv':csv_bytes(rows)for name,rows in paper_tables(tables).items()})
        assert identity==source_identity(),'source changed during overlay'
        manifest=dict(base=BASE,base_review='Muse r5x5 ACCEPT',source=identity,scope='API-only final-study overlay; accepted run23 hardware costs/routing and snapshot-control headlines unchanged',
            files={name:digest(value)for name,value in payload.items()})
        payload['r24_manifest.json']=encoded(manifest);OUT.mkdir(exist_ok=True,parents=True)
        with tempfile.TemporaryDirectory(prefix='.r24-',dir=OUT)as tmp:
            for name,value in payload.items():
                q=Path(tmp)/name;q.parent.mkdir(exist_ok=True,parents=True);q.write_bytes(value)
            for name in payload:
                q=OUT/name;q.parent.mkdir(exist_ok=True,parents=True);os.replace(Path(tmp)/name,q)
        records=quote_records();LEDGER.write_bytes(csv_bytes(records))
    print(json.dumps(verify(),sort_keys=True))


if __name__=='__main__':main()
