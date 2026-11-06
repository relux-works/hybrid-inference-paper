"""Run21 publication provenance; prices and admission verdicts are immutable."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[2]


def read(path):return list(csv.DictReader(io.StringIO(path.read_text())))


def scope(profile,common,total):
    assert 0<common<=total,'positive original/common coverage required'
    return ('{}; conditional scenario calls {}/{} ({:.2f}%); normalized to1000 same-scenario calls; full observed workload unsupported'.format(profile,common,total,100*common/total))


def availability(row):
    fields=(('5m','uptime_last_5m'),('30m','uptime_last_30m'),('1d','uptime_last_1d'))
    recorded=['{}={:g}%'.format(label,row[key])for label,key in fields if row.get(key)is not None]
    missing=[label for label,key in fields if row.get(key)is None]
    return 'recorded windows: '+('/'.join(recorded)or'none')+'; missing windows: '+('/'.join(missing)or'none')+'; admission checks recorded windows only; missing availability unverified'


def expected(directory,table):
    q=json.loads((ROOT/'calc/prices-2026-10-29/qwen_qwen3.8-27b.json').read_text())['data']['endpoints']
    cfg=json.loads((ROOT/'calc/hybridcalc/data/run21-deep.json').read_text())
    providers={(x['model_id'],x['tag']):x for x in q+cfg['glm_endpoints']['endpoints']}
    counts={}
    if table=='api_admission':
        for row in read(directory/'workload_coverage.csv'):
            counts[row['profile']]=(int(row['common_calls']),int(row['source_calls']))
        counts['million']=(1,1)
    else:
        for row in read(directory/'growing_trace_summary.csv'):
            counts[row['profile'],row['target_depth']]=(int(row['calls']),int(row['calls']))
    def labels(row):
        key=row['profile']if table=='api_admission'else(row['growing_profile'],row['target_depth'])
        assert key in counts,'unknown API coverage profile'
        model='qwen/qwen3.8-27b'if row['model']=='qwen'else'z-ai/glm-5.3-flash'
        provider=providers[model,row['tag']]
        name=key if isinstance(key,str)else'/'.join(key)
        return dict(workload_scope=scope(name,*counts[key]),availability_basis=availability(provider))
    return labels


def apply(directory,namespace,table):
    manifest_path=directory/(namespace+'_manifest.json');schema_path=directory/(namespace+'_schema.json')
    manifest=json.loads(manifest_path.read_text());schema=json.loads(schema_path.read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest,'changed payload before label publication'
    path=directory/(table+'.csv');rows=read(path);labels=expected(directory,table)
    before=[{k:v for k,v in row.items()if k not in ('workload_scope','availability_basis')}for row in rows]
    for row in rows:row.update(labels(row))
    assert before==[{k:v for k,v in row.items()if k not in ('workload_scope','availability_basis')}for row in rows],'label publication changed price/admission cells'
    fields=[k for k in rows[0]if k not in ('status','alarm_inputs')]+['status','alarm_inputs']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    schema[table]['columns']['workload_scope']='text'
    payloads={path.name:out.getvalue().encode(),schema_path.name:(json.dumps(schema,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()}
    for name,content in payloads.items():manifest['files'][name]=hashlib.sha256(content).hexdigest()
    manifest['publication_labels']=dict(source='calc/tests/r21_export_labels.py',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        table=table,numeric_and_admission_changes=0,core_result_hash_basis='pre-publication calculation; CSV label enrichment independently file-hashed')
    payloads[manifest_path.name]=(json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
    index_path=directory/'INDEX.json'
    if index_path.exists():
        index=json.loads(index_path.read_text());index['generator']=manifest['generator']
        index['files']={p.name:hashlib.sha256(payloads.get(p.name,p.read_bytes())).hexdigest()for p in directory.iterdir()if p.is_file()and p.name!='INDEX.json'}
        payloads['INDEX.json']=(json.dumps(index,indent=2)+'\n').encode()
    with tempfile.TemporaryDirectory(dir=directory)as tmp:
        for name,content in payloads.items():(Path(tmp)/name).write_bytes(content)
        for name in payloads:os.replace(Path(tmp)/name,directory/name)
    return dict(rows=len(rows),numeric_and_admission_changes=0)


def verify(directory,namespace,table):
    manifest=json.loads((directory/(namespace+'_manifest.json')).read_text())
    record=manifest.get('publication_labels',{})
    assert record.get('sha256')==hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'missing or stale API publication provenance'
    labels=expected(directory,table)
    for row in read(directory/(table+'.csv')):
        for key,value in labels(row).items():assert row.get(key)==value,'API coverage or missing-availability label omitted'
    return True
