"""Deterministic chart CSVs, explicit alarm cells and auditable generation metadata."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
from .inputs import InputError,ROOT


def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()


def generator_identity():
    paths=sorted([ROOT/'hybridcalc.py']+list((ROOT/'calc/hybridcalc').rglob('*.py'))+list((ROOT/'calc/hybridcalc/data').rglob('*.json')))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def write_tables(result,directory):
    """Only named generated files are replaced; unrelated files are preserved.

    Alarm cells are nan, never zero/empty. Manifest is replaced last; consumers
    verify its content hashes to reject stale or interrupted generations.
    """
    namespace=result.get('export_namespace','')
    if not isinstance(namespace,str) or (namespace and not re.fullmatch(r'[a-z][a-z0-9_]*',namespace)):
        raise InputError('CSV export requires a safe sidecar namespace')
    prefix=namespace+'_' if namespace else ''
    payloads={};schema={};alarms=[];ids=set()
    for table in result['tables']:
        key=table.get('id')
        if not isinstance(key,str) or not re.fullmatch(r'[a-z][a-z0-9_]*',key) or key in ids:
            raise InputError('CSV export requires unique safe table IDs')
        ids.add(key);columns=list(table['columns'])
        label_maps={column:{} for column in columns}
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=columns+['status','alarm_inputs'],lineterminator='\n')
        writer.writeheader()
        for index,row in enumerate(table['rows']):
            output={};row_alarms=[]
            for column in columns:
                value=row[column]
                if isinstance(value,dict) and 'alarm' in value:
                    output[column]='nan';row_alarms.extend(value['alarm'])
                    alarms.append({'table':key,'row':index,'column':column,'alarms':value['alarm']})
                elif value is None:
                    raise InputError(key+'.'+column+': null output is not an alarm')
                elif isinstance(value,str):
                    safe=value.translate(str.maketrans({',':';','\"':"'",'\n':' ','\r':' '}))
                    previous=label_maps[column].get(safe)
                    if previous is not None and previous!=value:raise InputError(key+'.'+column+': CSV display-label collision')
                    label_maps[column][safe]=value
                    output[column]=safe
                else:output[column]=value
            output['status']='alarm' if row_alarms else 'ok'
            output['alarm_inputs']='; '.join(sorted({a['input'] for a in row_alarms}))
            writer.writerow(output)
        payloads[key+'.csv']=stream.getvalue().encode()
        schema[key]={'name':table['name'],'columns':table['columns'],'rows':len(table['rows']),
                     'status':'ok or alarm; nan represents a noncomputable cell, never a numeric zero',
                     'csv_labels':{column:{safe:raw for safe,raw in mapping.items() if safe!=raw} for column,mapping in label_maps.items() if any(safe!=raw for safe,raw in mapping.items())}}
    payloads[prefix+'schema.json']=encoded(schema)
    payloads[prefix+'alarms.json']=encoded(alarms)
    payloads[prefix+'sources.json']=encoded({'inputs':result['sources'],'files':result['files']})
    manifest={'scenario':result['scenario'],'tables':{key:key+'.csv' for key in sorted(ids)},'notes':result.get('notes',[]),
              'result_sha256':hashlib.sha256(encoded(result)).hexdigest(),'generator':generator_identity(),
              'alarm_cells':len(alarms),'alarms':result.get('alarms',[]),
              'files':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(payloads.items())}}
    payloads[prefix+'manifest.json']=encoded(manifest)
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    # Stage all bytes before replacing any destination; each rename is atomic on this filesystem.
    with tempfile.TemporaryDirectory(prefix='.hybridcalc-',dir=str(directory)) as tmp:
        for name,data in payloads.items():(Path(tmp)/name).write_bytes(data)
        for name in payloads:os.replace(str(Path(tmp)/name),str(directory/name))
    return manifest
