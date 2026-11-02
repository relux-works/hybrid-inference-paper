"""Offline measured-server export, immutable run11 audit and complete quote comparison."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hybridcalc.engine import run,load
from hybridcalc.export import write_tables
from hybridcalc.server_prefill import fit
from r11_audit import CASES,read_rows,write_csv,quotes,number

ROOT=Path(__file__).resolve().parents[2]
BASELINE='a57db67'
PUBLISHED=ROOT/'calc/out/paper'
SCRATCH=ROOT/'.temp/hybrid-calc-r12-261101'


def frozen_files():
    # Historical engine artifacts retain their original immutable revision.
    # Current paper bytes are guarded separately by publication_v2.
    hashes={}
    for revision,root in ((BASELINE,'calc/out/paper'),):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',revision,root],cwd=ROOT,text=True).splitlines()
        for p in paths:
            if p in ('paper/data/arch-compare.csv','paper/data/arch_compare.py'):continue
            hashes[p]=hashlib.sha256(subprocess.check_output(['git','show',revision+':'+p],cwd=ROOT)).hexdigest()
    return hashes


def check_frozen():
    from publication_v2 import check_publication
    check_publication()
    hashes=frozen_files()
    for name,digest in hashes.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'run11 frozen file changed: '+name
    return hashes


def export():
    before=check_frozen()
    for scenario,prefix in CASES:
        name=scenario+'-measured-server'
        result=run(name)
        manifest=write_tables(result,PUBLISHED)
        print(name,len(manifest['tables']),'tables;',manifest['alarm_cells'],'inherited alarm cells',flush=True)
    assert check_frozen()==before


def changes():
    files={};ledger=[];summary=[]
    for path in sorted(PUBLISHED.glob('*_measured_server.csv')):
        name=path.name.replace('_measured_server','')
        if not (PUBLISHED/name).exists():continue
        before=read_rows((PUBLISHED/name).read_bytes());after=read_rows(path.read_bytes())
        assert len(before)==len(after),(name,'row count changed')
        policy='conservative' if '_conservative' in name else 'default'
        changed=0;numeric=0
        for index,(a,b) in enumerate(zip(before,after)):
            assert list(a)==list(b),(name,'columns changed')
            for col in a:
                x,y=a[col],b[col];isnum=number(x) is not None or number(y) is not None
                changed+=int(x!=y);numeric+=int(isnum)
                if isnum or x!=y:
                    fx,fy=number(x),number(y)
                    delta=fy-fx if fx is not None and fy is not None else ''
                    ledger.append(dict(csv=name,measured_csv=path.name,policy=policy,row=index,column=col,r11=x,measured_server=y,delta=delta,change='unchanged' if x==y else 'changed'))
        files[name]=(before,after)
        summary.append(dict(csv=name,measured_csv=path.name,rows=len(after),numeric_cells=numeric,changed_cells=changed,r11_sha256=hashlib.sha256((PUBLISHED/name).read_bytes()).hexdigest(),measured_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    assert len(files)==42,'all42 run11 charts require measured siblings'
    write_csv(ROOT/'calc/ENGINE-CHANGES-R12-261101.csv',ledger,['csv','measured_csv','policy','row','column','r11','measured_server','delta','change'])
    write_csv(ROOT/'calc/ENGINE-DIFF-R12-261101.csv',summary,['csv','measured_csv','rows','numeric_cells','changed_cells','r11_sha256','measured_sha256'])
    return files,summary


def quoted(files):
    # Reuse run11's exact claim definitions, with an explicit separate destination.
    old=quotes(files,SCRATCH/'quote-intermediate.csv');rows=[]
    for row in old:
        out={k:v for k,v in row.items() if k not in ('r10','r11')}
        out.update(r11=row['r10'],measured_server=row['r11']);rows.append(out)
    # Extend the earlier quote inventory with every GLM, people/GPU and timing numeric cell.
    for name,(before,after) in files.items():
        if not name.startswith(('glm_','people_per_gpu','turn_speedup','oneshot_ingest','transcript_example')):continue
        for index,(a,b) in enumerate(zip(before,after)):
            coords='; '.join(k+'='+b[k] for k in ('context','team','users_per_studio','demand_mode','requested_user_day','gpu','share','state_format','depth','portion','client','link_mbit') if k in b)
            for col in b:
                if number(b[col]) is not None:
                    rows.append(dict(policy='conservative' if '_conservative' in name else 'default',category='million_token' if name.startswith('glm_') else 'people_per_gpu' if name.startswith('people_') else 'timing_example',coordinates=coords+'; row='+str(index),metric=col,r11=a[col],measured_server=b[col],unit='see source schema',source=name))
    for row in rows:
        a,b=number(row['r11']),number(row['measured_server'])
        row['delta']=b-a if a is not None and b is not None else ''
        row['change']='unchanged' if str(row['r11'])==str(row['measured_server']) else 'changed'
    columns=['policy','category','coordinates','metric','r11','measured_server','delta','change','unit','source']
    write_csv(ROOT/'calc/ENGINE-QUOTES-R12-261101.csv',rows,columns)
    for policy,suffix in [('default',''),('conservative','_conservative')]:
        pay=[r for r in rows if r['category']=='payback' and r['policy']==policy]
        write_csv(PUBLISHED/('payback'+suffix+'_measured_server.csv'),pay,columns)
    return rows


def fit_audit():
    _,inputs=load('paper-tables-measured-server')
    raw=[json.loads(s) for s in inputs.measured('gpu_server').decode().splitlines()]
    a,b,points=fit(raw);peak=inputs.get('hardware.servers.rtx1.peak');bpeak=inputs.get('owners.options.b300.fp8_peak')
    rows=[]
    for p in points:
        d=p['depth'];observed=p['seconds_token'];predicted=a+b*d
        f=54e9+393216*d;util=f/observed/peak
        rows.append(dict(kind='bulk_turn',depth=d,actual_start_depth=p['actual_depth'],delta=p['delta'],observed=observed,predicted=predicted,residual_pct=100*(predicted/observed-1),unit='s/token',fp8_fraction_observed=util,fp16_fraction_observed=2*util,b300_fp8_estimate_tok_s=1/observed*bpeak/peak,b300_fp16_estimate_tok_s=1/observed*bpeak/peak))
    result_dir=ROOT/'data/measurements/vast-2026-11-01/qwen27b-gpu-bench/results'
    for path in sorted(result_dir.glob('*-slot*.jsonl')):
        data=[json.loads(s) for s in path.read_text().splitlines()]
        p=next(r for r in data if r['kind']=='prefill');n=p['depth'];observed=p['prompt_ms']/1000;predicted=a*n+b*n*n/2
        rows.append(dict(kind='held_out_fill_yarn_x4' if n>262144 else 'held_out_fill',depth=n,actual_start_depth=0,delta=n,observed=observed,predicted=predicted,residual_pct=100*(predicted/observed-1),unit='s',fp8_fraction_observed=(54e9*n+393216*n*n/2)/observed/peak,fp16_fraction_observed=2*(54e9*n+393216*n*n/2)/observed/peak,b300_fp8_estimate_tok_s='',b300_fp16_estimate_tok_s=''))
    write_csv(ROOT/'calc/SERVER-FIT-R12-261101.csv',rows,list(rows[0]))
    return dict(intercept_seconds_token=a,slope_seconds_token_depth=b,bulk_tolerance_pct=2,held_out_fill_tolerance_pct=15,rows=rows)


def flips(files):
    rows=[]
    for name,(before,after) in files.items():
        for index,(a,b) in enumerate(zip(before,after)):
            coords='; '.join(k+'='+b[k] for k in ('team','profile','route','client','basis','share','server','context','users_per_studio','demand_mode','requested_user_day','depth','portion','state_format','link_mbit','option') if k in b)
            comparisons=[]
            if name.startswith('person_cost_'):
                comparisons=[('API minus hybrid '+api,'api_'+api,'hybrid_'+api) for api in ('median','cheapest')]
                comparisons += [('owned minus hybrid median','own_cluster','hybrid_median')]
            if name.startswith('glm_'):
                comparisons=[('API minus hybrid session','api_session','hybrid_session'),('owned minus hybrid session','own_cluster_session','hybrid_session'),('API minus owned session','api_session','own_cluster_session')]
            for label,left,right in comparisons:
                x=float(a[left])-float(a[right]);y=float(b[left])-float(b[right])
                if math.isfinite(x) and math.isfinite(y) and (x>0)!=(y>0):
                    rows.append(dict(csv=name,row=index,comparison=label,r11=x,measured_server=y,coordinates=coords))
            if name.startswith('perimeter_cost') and a['selected']!=b['selected']:
                rows.append(dict(csv=name,row=index,comparison='selected owned fleet',r11=a['selected'],measured_server=b['selected'],coordinates=coords))
            if name.startswith('remote_rent_buy') and a['buy_beats_rent']!=b['buy_beats_rent']:
                rows.append(dict(csv=name,row=index,comparison='buy beats rent',r11=a['buy_beats_rent'],measured_server=b['buy_beats_rent'],coordinates=coords))
            if 'speedup' in a:
                x,y=float(a['speedup']),float(b['speedup'])
                if math.isfinite(x) and math.isfinite(y) and (x>1)!=(y>1):
                    rows.append(dict(csv=name,row=index,comparison='hybrid speedup crosses1',r11=x,measured_server=y,coordinates=coords))
    write_csv(ROOT/'calc/ENGINE-FLIPS-R12-261101.csv',rows,['csv','row','comparison','r11','measured_server','coordinates'])
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit-only',action='store_true');args=parser.parse_args()
    SCRATCH.mkdir(parents=True,exist_ok=True)
    if not args.audit_only:export()
    hashes=check_frozen();files,summary=changes();claims=quoted(files);fit_result=fit_audit();directions=flips(files)
    result=dict(frozen_files=len(hashes),chart_csvs=len(summary),numeric_cells=sum(r['numeric_cells'] for r in summary),changed_cells=sum(r['changed_cells'] for r in summary),quote_records=len(claims),direction_records=len(directions),fit=fit_result)
    (SCRATCH/'publication-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fit'},indent=2))


if __name__=='__main__':main()
