"""Semantic row matching against frozen run22; no rounded-value comparisons."""
import csv
import io
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'calc/out/run22'
FAMILY=('profile','scope_tier','transport','load','share','client','basis','server','billing')
KEYS={
    **{n:FAMILY+('team',)for n in ('small_team_cost','main_economics','dedicated_multiples','shared_multiples','idleness')},
    'team_break_even':FAMILY+('reference',),
    'api_admission':('profile','scope_tier','availability_scenario','cache_point','provider'),
    'workload_coverage':('profile','scope_tier'), 'workload_profiles':('profile','metric','statistic'),
    'link_thresholds':('model','server','client','transport','depth','delta','link'),
    'full_resync':('depth','transport','link'), 'decode_scaling':('server','depth','requested_streams'),
    'server_decode_measured':('server','depth','streams'), 'decode_ceiling':('client','depth'),
    'client_measurements':('model','client','source','source_row','delta'),
    'quality_evidence':('evidence',),'policy':('key',),'heavy_sensitivity':('profile',),
    'direct_mac_pending':('client','depth','delta')}


def read(path):
    with path.open(newline='')as f:return list(csv.DictReader(f))


def key(name,row):
    values=tuple(str(row.get(k,''))for k in KEYS[name])
    if name=='link_thresholds':
        basis=row['rate_basis']
        variant='analyst' if basis.startswith('analyst') else 'first_restore' if basis.startswith('first-restore') else 'primary'
        values+=(variant,)
    return values


def index(name,rows):
    result={}
    for number,row in enumerate(rows):
        identity=key(name,row)
        assert identity not in result,('duplicate comparison identity',name,identity)
        result[identity]=(number,row)
    return result


def numeric(value):
    if value in ('True','False'):return int(value=='True')
    try:value=float(value)
    except (TypeError,ValueError):return None
    return value if math.isfinite(value)else None


def reason(name,column):
    if name in ('api_admission','workload_coverage','workload_profiles','quality_evidence','client_measurements'):
        return 'unchanged run22 inputs/policy; no new provider cache result'
    if name=='link_thresholds':return 'M3 deep local time measured at1.04M; full-slot warm LaCie recovery charged as explicit proxy, not delta-import measurement; PRO1M impossible'
    if name in ('server_decode_measured','decode_scaling'):return 'PRO multi-depth decode/residency measurements and stated interpolation replace sparse/modelled points; B300 remains modelled'
    if name=='decode_ceiling':return 'normal-priority1.04M decode replaces background-priority1.67; actual measured depth retained'
    if name=='full_resync':return 'historical llama.cpp slot builder only; not a feasible PRO vLLM1M server'
    return 'measured/interpolated PRO decode and resident batch limits change own-cluster/generation/fleet economics; other policies unchanged'


def cell(name,identity,column,old,new,old_row,new_row,why=None):
    a,b=numeric(old),numeric(new)
    return dict(table=name,row_key=json.dumps(identity,separators=(',',':')),column=column,old=old,new=new,
        absolute_delta=b-a if a is not None and b is not None else '',
        percent_delta=100*(b/a-1) if a not in (None,0) and b is not None else '',
        old_row=old_row,new_row=new_row,changed=old!=new,
        why=(why or reason(name,column)) if old!=new else 'unchanged on the same coordinate/basis')


def build(tables,csv_bytes):
    before={name:read(OLD/(name+'.csv'))for name in KEYS}
    after={name:(list(csv.DictReader(io.StringIO(csv_bytes(tables[name]).decode()))) if csv_bytes else tables[name])for name in KEYS}
    lookup_old={name:index(name,rows)for name,rows in before.items()}
    lookup_new={name:index(name,rows)for name,rows in after.items()}
    diffs=[];summary=[]
    for name in KEYS:
        changed_rows=set();shared=set(lookup_old[name])&set(lookup_new[name])
        for identity in sorted(shared):
            oi,a=lookup_old[name][identity];ni,b=lookup_new[name][identity]
            for column in sorted(a.keys()&b.keys()):
                if a[column]!=b[column] and (numeric(a[column])is not None or numeric(b[column])is not None or column in ('from_people','statement','verdict','status','alarm_inputs')):
                    diffs.append(cell(name,identity,column,a[column],b[column],oi,ni));changed_rows.add(identity)
        summary.append(dict(table=name,old_rows=len(before[name]),new_rows=len(after[name]),matched_rows=len(shared),
            rows_with_numeric_or_verdict_change=len(changed_rows),added_rows=len(lookup_new[name].keys()-lookup_old[name].keys()),
            removed_rows=len(lookup_old[name].keys()-lookup_new[name].keys()),why=reason(name,'')))
    # Every numerical quotation in the accepted report is accounted for. Include
    # unchanged numbers too, so the gate cannot silently omit a headline change.
    abstract=[];seen=set()
    for quote in read(ROOT/'calc/ENGINE-REPORT-QUOTES-R22-261103.csv'):
        name=Path(quote['source']).stem
        if name not in KEYS or numeric(quote['source_value'])is None:continue
        oi=int(quote['row']);a=before[name][oi];identity=key(name,a);column=quote['column']
        coordinate=(name,identity,column)
        if coordinate in seen:continue
        seen.add(coordinate)
        assert identity in lookup_new[name],('missing abstract-bound row',name,identity)
        ni,b=lookup_new[name][identity]
        assert column in b,('missing abstract-bound column',name,column)
        abstract.append(cell(name,identity,column,a[column],b[column],oi,ni))
    # The earlier report also stated these deep timings/ceilings in prose.
    for name,columns in (('link_thresholds',('local_prefill_s','import_s')),('decode_ceiling',('measured_decode_tok_s','ceiling_tok_s'))):
        for identity,(oi,a)in lookup_old[name].items():
            if name=='link_thresholds' and not(a['model']=='qwen' and a['server']=='b300_fp8_kv' and a['client']=='m3max' and a['depth']=='1000000' and a['transport']=='bf16' and float(a['bytes_s'])==5190000 and a['rate_basis'].startswith('measured_anchor')):continue
            ni,b=lookup_new[name][identity]
            for column in columns:
                abstract.append(cell(name,identity,column,a[column],b[column],oi,ni))
    # Sustained crossings are quoted in sentences, so their counts need explicit
    # old/new accounting even when 'no crossing' is a blank numeric cell.
    for identity,(oi,a)in lookup_old['team_break_even'].items():
        if not all(a[k]==v for k,v in dict(scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8').items()):continue
        ni,b=lookup_new['team_break_even'][identity]
        abstract.append(cell('team_break_even',identity,'statement',a['statement'],b['statement'],oi,ni))
    for name in ('quality_evidence','workload_profiles','main_economics'):
        for identity,(oi,a)in lookup_old[name].items():
            if name=='main_economics' and not all(a[k]==v for k,v in dict(scope_tier='measured_ladder',transport='bf16',share='0.2',client='m5max64',basis='owned',server='pro6000_fp8',team='50').items()):continue
            ni,b=lookup_new[name][identity]
            columns=('unit_month','boxes','own_cluster_boxes','own_cluster_person_month','service_utilization','calendar_utilization') if name=='main_economics' else sorted(a.keys()&b.keys())
            for column in columns:
                if numeric(a[column])is not None:
                    abstract.append(cell(name,identity,column,a[column],b[column],oi,ni))
    abstract=list({(r['table'],r['row_key'],r['column']):r for r in abstract}.values())
    return dict(changed_against_run22=diffs,change_summary=summary,abstract_bound_changes=abstract)
