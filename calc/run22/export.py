"""Deterministic run22 exporter, frozen-history and quote/sentence gates."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from hybridcalc.export import generator_identity
from run22 import engine,sentences

BASE='b6316e8a12c47526c9815cc08ebc6de78eec162b'
OUT=ROOT/'calc/out/run22'
LEDGER=ROOT/'calc/ENGINE-QUOTES-R22-261103.csv'


import history_evidence as history
import ledger_storage

def digest(content):
    return hashlib.sha256(content).hexdigest()


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def source_identity():
    paths=[p for p in (ROOT/'calc/run22').rglob('*') if p.is_file() and p.suffix in ('.py','.json','.csv','.md')]
    paths.append(ROOT/'calc/tests/test_run22.py')
    paths.append(ROOT/'calc/prices-2026-10-29/qwen_qwen3.8-27b.json')
    paths.append(ROOT/'data/measurements/ivmbp-2026-10-30/stats.json')
    from hybridcalc import server_economics_r20 as s
    owner=json.loads(s.EVIDENCE.read_text())['owner_cache']
    paths.extend((s.EVIDENCE,ROOT/owner['path']))
    return {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(paths)}


def frozen():
    names=history.snapshot_paths(BASE,'calc/out')
    roots={Path(n).parts[2]for n in names}
    current={str(p.relative_to(ROOT))for p in (ROOT/'calc/out').rglob('*')if p.is_file()and p.relative_to(ROOT/'calc/out').parts[0]in roots}
    assert current==set(names),'historical export file set changed'
    for name in names:
        assert digest((ROOT/name).read_bytes())==history.snapshot_hash(BASE,name),'historical bytes changed: '+name
    return len(names)


def csv_bytes(rows):
    columns=list(dict.fromkeys(k for r in rows for k in r))
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=columns+['status','alarm_inputs'],lineterminator='\n')
    writer.writeheader()
    for row in rows:
        output={};alarms=[]
        for key in columns:
            value=row.get(key,'')
            if isinstance(value,dict) and 'alarm' in value:
                output[key]='nan';alarms+=value['alarm']
            else:
                assert value is not None,'missing value must be explicitly pending'
                output[key]=value
        output['status']='alarm' if alarms else 'ok'
        output['alarm_inputs']='; '.join(sorted({a['input']+': '+a['reason'] for a in alarms}))
        writer.writerow(output)
    return stream.getvalue().encode()


def read(path):
    return list(csv.DictReader(io.StringIO(ledger_storage.read_text(path))))


def paper_tables(tables):
    selected={name:tables[name] for name in ('small_team_cost','team_break_even','dedicated_multiples','shared_multiples','main_economics')}
    out={}
    for name,rows in selected.items():
        assert all(r['server'] in sentences.SERVERS for r in rows),'paper contains forbidden server'
        out[name]=rows
    out['paper_claims']=[dict(r,claim_table=name) for name in ('team_break_even','dedicated_multiples','shared_multiples') for r in selected[name]]
    return out


def quote_records(directory=None):
    directory=OUT if directory is None else directory
    records=[]
    for path in sorted(directory.rglob('*.csv')):
        rel=str(path.relative_to(ROOT))
        for index,row in enumerate(read(path)):
            for key,value in row.items():
                # Enumerate all published sentence surfaces and the numerical
                # tables quoted by the report. Other cells remain manifest-bound;
                # this ledger does not claim to duplicate every engine cell.
                quantitative={'link_thresholds.csv','full_resync.csv','client_measurements.csv','decode_scaling.csv','decode_ceiling.csv','quality_evidence.csv',
                    'api_admission.csv','workload_coverage.csv','workload_profiles.csv','idleness.csv','server_decode_measured.csv'}
                cost_fields={'person_month','own_cluster_person_month','boxes','own_cluster_boxes','service_utilization','calendar_utilization','own_service_utilization','own_calendar_utilization'}
                if (key not in ('sentence','short_sentence') and path.name not in quantitative and
                        not (path.name in ('small_team_cost.csv','main_economics.csv','idleness.csv','heavy_sensitivity.csv') and
                             (key in cost_fields or key.startswith('api_') or key.endswith('person_month')))):
                    continue
                records.append(dict(paper_site='Run22 report / RC4 paper tables',engine_key=rel+'[row={}].{}'.format(index,key),
                    old='<new RC4 bf16-default / dedicated-primary result; historical exports frozen>',new=value,source=rel,comparison='run22_successor'))
    return records


def write(tables):
    payload={name+'.csv':csv_bytes(rows) for name,rows in tables.items()}
    for name,rows in paper_tables(tables).items():
        payload['paper/'+name+'.csv']=csv_bytes(rows)
    from hybridcalc.measurements_r20 import unit
    schema={}
    for name,rows in tables.items():
        columns=list(dict.fromkeys(k for row in rows for k in row))
        units={key:('fraction of installed GPU time' if 'utilization' in key and not key.endswith('basis') else
            'MB/s decimal' if key=='threshold_MB_s' else 'mixed; see row unit' if key=='value' and name=='quality_evidence' else
            unit(key,next((r[key] for r in rows if key in r),''))) for key in columns}
        schema[name]=dict(rows=len(rows),columns=columns,units=units)
    payload['r22_schema.json']=encoded(schema)
    manifest=dict(scenario='rc4-economics-r22',base=BASE,base_review='Muse r5x3 ACCEPT, no findings; generated short prose form advice applied',
        generator=generator_identity(),extension=source_identity(),historical_files=frozen(),
        notes=['bf16 transport default; f32 control; resident recurrent state still f32',
            'dedicated bought/rented team server PRIMARY; supplementary shared resident-work/full-utilization limit',
            'only PRO6000/B300 servers in economics and paper; normal-priority M5 archive verified; M3 Glimmer accepted FACTS transcription, incident archive unavailable',
            'API three cache points are scenarios, not provider performance verdicts; same availability window, no mixed-window minima',
            'measured-shape coverage is fraction of calls inside ladder, not a fraction of workload; all selected shapes normalized per person-month; physical deep sensitivity is not measured coverage',
            'PRO6000 default-KV decode measured at16384 only,1/8/32/39 streams; remaining pending CSVs contain headers only; deeper vLLM, Mac1M and GLM predictions remain labelled estimates'],
        files={name:digest(value) for name,value in sorted(payload.items())})
    payload['r22_manifest.json']=encoded(manifest)
    OUT.mkdir(parents=True,exist_ok=True)
    # Stage before atomic replacement; manifest replaced last. The verifier
    # rejects interruption rather than treating a partially refreshed set as valid.
    with tempfile.TemporaryDirectory(prefix='.r22-',dir=OUT) as temporary:
        for name,value in payload.items():
            path=Path(temporary)/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
        for name in payload:
            path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True);os.replace(Path(temporary)/name,path)
    records=quote_records()
    with ledger_storage.open_text(LEDGER,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');writer.writeheader();writer.writerows(records)
    return manifest


def verify(records=None):
    manifest=json.loads((OUT/'r22_manifest.json').read_text())
    assert manifest['base']==BASE and manifest['scenario']=='rc4-economics-r22','wrong producer'
    assert manifest['generator']==generator_identity(),'changed historical generator'
    assert manifest['extension']==history.accepted_identity('9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0',source_identity()),'stale run22 source or input'
    assert set(manifest['files'])|{'r22_manifest.json'}=={str(p.relative_to(OUT)) for p in OUT.rglob('*') if p.is_file()},'run22 file set'
    for name,expected in manifest['files'].items():
        assert digest((OUT/name).read_bytes())==expected,'changed export '+name
    for row in read(OUT/'idleness.csv'):
        assert row['billing']=='bought' and row['shared_billing']=='shared resident-work rental allocation','idleness dedicated/shared billing mismatch'
        assert row['link']=='office125 MB/s RTT1 ms assumed for both sides','idleness comparison link mismatch'
    for path in (OUT/'paper').glob('*.csv'):
        for row in read(path):
            assert row.get('server') in sentences.SERVERS,'rtx5090/unknown server in paper'
            if 'sentence' in row:
                sentences.validate(row['sentence'],row)
                sentences.validate_short(row['short_sentence'],row)
            for field in ('person_month','own_cluster_person_month'):
                if field in row and row[field] not in ('','nan') and row['billing'] in ('bought','rented'):
                    util='service_utilization' if field=='person_month' else 'own_service_utilization'
                    assert row.get(util) not in (None,''),'dedicated cost lacks utilization'
    expected=quote_records()
    records=read(LEDGER) if records is None else records
    assert records==expected,'missing, changed or duplicate quote coordinates'
    return dict(historical_files=frozen(),quote_cells=len(records),new_files=len(manifest['files'])+1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-only',action='store_true')
    args=parser.parse_args()
    if not args.audit_only:
        print('frozen before',frozen(),flush=True)
        identity=source_identity();historical=generator_identity()
        tables=engine.calculate()
        assert source_identity()==identity and generator_identity()==historical,'source changed during calculation; refuse publication'
        write(tables)
    print(json.dumps(verify(),sort_keys=True),flush=True)


if __name__=='__main__':main()
