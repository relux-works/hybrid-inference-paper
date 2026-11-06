"""Label-only R20/R21 republication and explicitly scoped paper projections.

Underlying numerical producer identities stay unchanged. The correction ledger
compares every original cell against the reviewed git objects, independently of
the new publisher. Paper tables have their own source and file hashes.
"""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r15_sentences import conditions,validate_sentence,alarm_clause,policy as sentence_policy
BASE={20:'b6ac5abcdf60b72582be87c7ad075ee460e7cc78',21:'3bc587529e305ab48a21284badaa6043d225e900'}
SERVERS={'pro6000_fp8','b300_fp8','b300_fp8_kv','llama_pro6000','llama_b300'}
LLAMA='native llama.cpp; vLLM-to-llama bridge not applicable; bridge enum is a duplicate sensitivity, not a measured bridge effect'
ALLOWED={'workload_scope','availability_basis','basis','paper_use'}

import history_evidence as history

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return list(csv.DictReader(io.StringIO(path.read_text())))
def blob(head,path):return history.snapshot_object(head+':'+str(path))
def original(run,name):return list(csv.DictReader(io.StringIO(blob(BASE[run],f'calc/out/run{run}/{name}').decode())))
def dump(path,rows):
    assert rows,'cannot publish an empty table'
    with path.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n')

def availability(row):
    fields=(('5m','uptime_last_5m'),('30m','uptime_last_30m'),('1d','uptime_last_1d'))
    recorded=['{}={:g}%'.format(label,row[key])for label,key in fields if row.get(key)is not None]
    missing=[label for label,key in fields if row.get(key)is None]
    return 'recorded windows: '+('/'.join(recorded)or'none')+'; missing windows: '+('/'.join(missing)or'none')+'; admission checks recorded windows only; missing availability unverified'

def labels20(name,rows):
    providers={x['tag']:x for x in json.loads((ROOT/'calc/prices-2026-10-29/qwen_qwen3.8-27b.json').read_text())['data']['endpoints']}
    for row in rows:
        if name=='api_admission.csv':
            row['workload_scope']='conditional common measured subset 10885/39904 (27.28%); billed means from this subset; normalized to1000 same-scenario calls; full workload unsupported; million profile rescales context within the same conditional output mix'
            row['availability_basis']=availability(providers[row['tag']])
        if name in ('server_prefill.csv','engine_sensitivity.csv')and row['engine']=='llama_cpp':
            row['basis']=row['basis']+'; '+LLAMA
        if 'server'in row:
            row['paper_use']='not used in the paper'if row['server']=='rtx5090'else'eligible server; quote the scoped paper projections'
        if name=='paper_claims.csv':row['paper_use']='archival mixed-server statement; not used in the paper; use paper/paper_claims.csv'
    return rows

def differences(run,directory):
    """Reject deletions, reordered rows and any non-allowlisted cell change."""
    changes=[]
    for path in sorted(directory.glob('*.csv')):
        old=original(run,path.name);new=read(path)
        assert len(old)==len(new),'original row count changed'
        for index,(a,b)in enumerate(zip(old,new)):
            assert set(a)<=set(b),'original column deleted'
            for key in b:
                if a.get(key)!=b[key]:
                    assert key in ALLOWED,'non-label cell changed: '+path.name+'/'+key
                    changes.append(dict(table=path.name,row=index,column=key,old=a.get(key,'<absent>'),new=b[key]))
    return changes

def verify_labels20(directory):
    for path in directory.glob('*.csv'):
        expected=labels20(path.name,original(20,path.name))
        assert read(path)==expected,'missing coverage, availability, bridge or paper-use label: '+path.name
    return True

def publish_labels20(directory):
    manifest_path=directory/'r20_manifest.json';m=json.loads(manifest_path.read_text())
    for name,h in m['files'].items():assert digest(directory/name)==h,'changed payload before publication'
    differences(20,directory) # Refuse changed prices/admission before any writes.
    schema=json.loads((directory/'r20_schema.json').read_text())
    for path in sorted(directory.glob('*.csv')):
        rows=labels20(path.name,original(20,path.name));dump(path,rows)
        for key in rows[0]:
            if key not in schema[path.stem]['columns']:schema[path.stem]['columns'][key]='text'
    js(directory/'r20_schema.json',schema)
    changes=differences(20,directory);paper=directory/'paper';paper.mkdir(exist_ok=True)
    dump(paper/'label_changes.csv',changes)
    m['files']={name:digest(directory/name)for name in m['files']}
    m['r14_publication']=dict(policy='calc/tests/r14_publication.py',sha256=digest(Path(__file__)),
        reviewed_numeric_head=BASE[20],numeric_and_admission_changes=0,cell_diff='paper/label_changes.csv',cell_diff_sha256=digest(paper/'label_changes.csv'),
        core_result_hash_basis='unchanged pre-publication numerical calculation; presentation labels separately hashed')
    js(manifest_path,m)
    figure=json.loads((directory/'batching_figure.json').read_text());figure['source_sha256']=digest(directory/'decode_scaling.csv');js(directory/'batching_figure.json',figure)
    refresh_index(directory)
    return len(changes)

def refresh_index(directory):
    path=directory/'INDEX.json';index=json.loads(path.read_text())
    index['files']={p.name:digest(p)for p in sorted(directory.iterdir())if p.is_file()and p.name!='INDEX.json'}
    js(path,index)

def require_paper(rows):
    assert rows,'paper table cannot be empty'
    for row in rows:
        assert row.get('server')in SERVERS,'5090 or unknown server in paper table'
        assert row.get('workload_scope'),'paper row missing coverage'
        assert row.get('cost_basis'),'paper row missing cost basis'
    return True

def enrich(run,table,rows):
    out=[]
    for index,row in enumerate(rows):
        if row.get('server')not in SERVERS:continue
        r=dict(row);r['load']=row.get('load',row.get('profile','heavy'))
        if run==20:r['profile']='common_measured_r20'
        r['cost_basis']='dedicated integer fleet; hybrid sufficient, not minimal; own cluster minimal in its model; calendar rental when billing=rented'
        r['cache_basis']='98.1% owner commercial token-cache allowance; provider behaviour unverified; 1.9% misses billed'
        r['bridge_basis']=(LLAMA if row.get('engine')=='llama_cpp'else'zero extra bridge lower bound'if row.get('bridge')=='none'else'token-weighted PR16 smoke projected through origin, not a short-turn fit or upper confidence bound; portability estimated')
        r['source']=f'calc/out/run{run}/{table}.csv[row={index}]'
        r['rate_basis']=row.get('rate_basis','R20 common measured prefill envelope; 128GB M5 rate portability estimated; decode batching modelled')
        out.append(r)
    return out

def conclusion(row):
    value=float(row['from_people']);cross=('cheaper from {} people through 500 scanned'.format(int(value))if math.isfinite(value)else'no sustained crossing through 500 people')
    return ('{profile}: {server} hybrid versus {reference}: {cross}; {conditions}; dedicated fleet; hybrid fleet sufficient, not minimal; deep rates extrapolated where beyond measured ladder.').format(
        **{k:row[k]for k in ('profile','server','reference')},cross=cross,conditions=conditions(row))

def dedicated(rows):
    out=[]
    for row in rows:
        fields=('profile','load','share','client','basis','server','billing','team','api_median_person_month','api_cheapest_person_month','cache_basis','workload_scope','bridge_basis','rate_basis','source')
        r={k:row[k]for k in fields}
        r['cost_basis']='dedicated integer fleet; sufficient hybrid provisioning; not minimal'
        r['median_multiple']=row['median_over_hybrid'];r['cheapest_multiple']=row['cheapest_over_hybrid']
        r['hybrid_person_month']=row.get('person_month',row.get('hybrid_person_month'))
        out.append(r)
    return out

def multiple_sentence(row):
    return ('{profile}: {server} hybrid costs ${cost:.3f}/person-month, giving API/hybrid multiples {median:.3f} ({api_median_provider}) and {cheap:.3f} ({api_cheapest_provider}), at {team} people; {conditions}; {cost_basis}; {bridge_basis}; {rate_basis}; {api_median_basis}{alarm}.').format(
        **{k:row[k]for k in ('profile','server','team','cost_basis','bridge_basis','rate_basis','api_median_provider','api_cheapest_provider','api_median_basis')},
        cost=float(row['hybrid_person_month']),median=float(row['median_multiple']),cheap=float(row['cheapest_multiple']),conditions=conditions(row),alarm=alarm_clause(row))

def projections(run,shared):
    directory=ROOT/f'calc/out/run{run}';paper=directory/'paper';paper.mkdir(exist_ok=True)
    apis=read(directory/'api_admission.csv')
    def api_labels(row):
        profile='main'if run==20 else row['profile']
        selected=[r for r in apis if r['profile']==profile and r['role']in('cheapest','median')]
        row.update({'api_'+r['role']+'_provider':r['tag']for r in selected})
        row['api_median_basis']='admitted snapshot median; upper middle for even endpoint counts; tariff discount treated as already reflected, unverified interpretation'
    small=enrich(run,'small_team_cost',read(directory/'small_team_cost.csv'))
    dump(paper/'small_team_cost.csv',[r for r in small if r['server']=='pro6000_fp8'])
    breaks=enrich(run,'team_break_even',read(directory/'team_break_even.csv'))
    for row in breaks:
        api_labels(row);row['sentence']=conclusion(row)+' '+row['rate_basis']+'; '+row['api_median_basis']+'.'
    dump(paper/'team_break_even.csv',breaks)
    if run==20:
        raw=enrich(run,'engine_sensitivity',read(directory/'engine_sensitivity.csv'))
        for row in raw:row['client']='m5max64';row['basis']='owned';row['billing']='bought';row['load']='heavy'
        ds=dedicated(raw+small)
    else:ds=dedicated(enrich(run,'main_economics',read(directory/'main_economics.csv'))+small)
    for row in ds+shared:
        api_labels(row);row['sentence']=multiple_sentence(row)
    dump(paper/'dedicated_multiples.csv',ds)
    dump(paper/'shared_multiples.csv',shared)
    claims=[]
    fields=('profile','load','share','client','basis','server','billing','cost_basis','cache_basis','workload_scope','bridge_basis','sentence','source')
    for row in breaks+ds+shared:
        claims.append({k:row[k]for k in fields})
    dump(paper/'paper_claims.csv',claims)
    for name in ('small_team_cost','team_break_even','paper_claims','dedicated_multiples','shared_multiples'):require_paper(read(paper/(name+'.csv')))
    m=dict(run=run,policy='calc/tests/r14_publication.py',policy_sha256=digest(Path(__file__)),
        numeric_producer_head=BASE[run],sources={str(p.relative_to(ROOT)):digest(p)for p in directory.glob('*.csv')},
        files={p.name:digest(p)for p in paper.glob('*.csv')},
        basis='5090 server excluded by owner; PRO6000 and B300; original numerical cells unchanged; new shared projections use existing R20 resident-work equation')
    from hybridcalc.export import generator_identity
    m['shared_calculation_generator']=generator_identity()
    m['sentence_policy']=sentence_policy()
    m['sources'][str((directory/f'r{run}_sources.json').relative_to(ROOT))]=digest(directory/f'r{run}_sources.json')
    js(paper/'manifest.json',m)
    return m

def verify_paper(run):
    paper=ROOT/f'calc/out/run{run}/paper';m=json.loads((paper/'manifest.json').read_text())
    assert m['policy_sha256']==history.historical_code_hash('calc/tests/r14_publication.py'),'stale paper policy'
    assert m.get('sentence_policy')==dict(sentence_policy(),sha256=history.historical_code_hash('calc/tests/r15_sentences.py')),'stale sentence policy'
    from hybridcalc.export import generator_identity
    assert m['shared_calculation_generator']==generator_identity(),'stale shared calculation source'
    for name,h in m['sources'].items():assert digest(ROOT/name)==h,'changed paper source'
    for name,h in m['files'].items():
        assert digest(paper/name)==h,'changed paper payload'
        if name!='label_changes.csv':
            rows=read(paper/name);require_paper(rows)
            for row in rows:
                if 'sentence'in row:validate_sentence(row['sentence'],row)
    assert set(m['files'])=={p.name for p in paper.glob('*.csv')},'unlisted paper payload'
    if run==20:
        record=json.loads((paper.parent/'r20_manifest.json').read_text())['r14_publication']
        assert record['sha256']==history.historical_code_hash('calc/tests/r14_publication.py'),'stale R20 label policy'
        assert record['cell_diff_sha256']==digest(paper/'label_changes.csv'),'changed correction ledger'
        expected=[{k:str(v)for k,v in r.items()}for r in differences(20,paper.parent)]
        assert read(paper/'label_changes.csv')==expected,'correction ledger omitted changed cell'
    return True

def quotes(run):
    """Every new paper cell plus every changed archival quote has a coordinate."""
    directory=ROOT/f'calc/out/run{run}';rows=[]
    for path in sorted((directory/'paper').glob('*.csv')):
        for index,row in enumerate(read(path)):
            for key,value in row.items():
                rows.append(dict(source=str(path.relative_to(ROOT)),row=index,column=key,old='<new paper projection>',new=value))
    if run==20:
        for change in differences(run,directory):
            rows.append(dict(source=str((directory/change['table']).relative_to(ROOT)),row=change['row'],column=change['column'],old=change['old'],new=change['new']))
    return rows

def verify_quotes(run):
    path=ROOT/f'calc/ENGINE-QUOTES-R{run}-PAPER-261103.csv'
    expected=[{k:str(v)for k,v in r.items()}for r in quotes(run)]
    assert read(path)==expected,'missing or changed paper quote'
    return len(expected)

def shared_work(hot,demand,days,gpu_hour,load,decode_seconds,storage,client_base,egress):
    served=min(demand,hot['client_capacity_day'])
    pre=hot['gpu_s_call']*served*days*gpu_hour/(3600*load)
    overflow=max(0,demand-served)*decode_seconds*days*gpu_hour/(3600*load)
    return pre+overflow+storage+client_base+hot['wire_bytes_call']*served*days/1e12*egress

def shared_tables(runs=(20,21)):
    """R20's resident-work equation, freshly evaluated for each profile/load.

    Reuses one immutable import fit while preparing calls; no coefficient or
    numerical formula changes. Retained-slot cold rebuild/calendar floors are
    excluded, so this is explicitly a shared resident-work lower bound.
    """
    from unittest.mock import patch
    from hybridcalc.engine import load
    from hybridcalc.paper_tables import Context
    from hybridcalc import measurements_r20 as old,server_economics_r20 as s,measurements_r16 as r16
    import copy
    _,inputs=load('server-economics-r20');spec,_=load('paper-tables-r17')
    c=Context(spec,inputs)
    calls=c.g.resolve(c.valid).value;importer=r16.ClientImport();result={}
    for run in runs:
        cfg=s.config()
        if run==21:
            from hybridcalc import deep_r21 as deep,measurements_r21 as new
            deep_cfg=deep.config();stats=deep.checked_stats(deep_cfg)
            profiles={'existing_combined':calls,'claude_deep':deep.reconstruct(stats['agents']['claude'],deep_cfg['quadrature_points'],deep_cfg['active_gap_cap_s'])}
            servers={key:deep.Server(key,cfg)for key in deep.SERVERS}
        else:
            profiles={'common_measured_r20':calls};servers={key:s.Server(key,cfg)for key in ('pro6000_fp8','b300_fp8','b300_fp8_kv')}
        out=[]
        for profile,source_calls in profiles.items():
            max_end=249000 if run==20 else min(deep.LIMIT,min((server.free-server.state)/server.kv for server in servers.values()))
            indices=[i for i,(a,n,o,t)in enumerate(source_calls)if a+n+o<=max_end and(run==21 or 512<=n<=10000)]
            common=[source_calls[i]for i in indices]
            if run==20:_,apis=s.api_baselines(old.billing_calls(source_calls,indices,inputs.get('workload.chunk_calls')),cfg);api=apis['main'];ecfg=cfg;klass=old.Economics
            else:
                _,apis=new.profile_api(source_calls,indices,profile,deep_cfg,inputs.get('workload.chunk_calls'));api=apis['qwen'];ecfg=copy.deepcopy(cfg)
                ecfg['reservation_depth']=new.profile_reservation(common,deep_cfg['reservation_depth'],servers);klass=new.Economics
            with patch.object(r16,'ClientImport',return_value=importer):
                econ=klass(c,common,servers,ecfg,{'main':api})
                for key,server in servers.items():
                    prepared=econ.prepared.get((key,'m5max64','measured_envelope'))
                    if prepared is None:prepared=old.Prepared(common,server,'m5max64',c,'measured_envelope',econ.measurements)
                    hot=prepared.stats(0,'engine_wan');gpu_hour=server.info['hourly_usd']/(8 if server.info['host']=='b300'else 1)
                    storage=4*server.session_bytes(ecfg['reservation_depth'])/1e9*inputs.get('hosting.tiers.NVMe.price')
                    base=inputs.get('hardware.clients.m5max64.power')*econ.hours*econ.days*inputs.get('prices.energy_client')+inputs.get('owners.front_month')
                    seconds=econ.own_stats(server,min(32,int(50*econ.sessions)))['seconds']
                    for load in ('light','medium','heavy'):
                        for share in cfg['shares']:
                            demand=inputs.get('service.profiles.'+load)*share
                            price=shared_work(hot,demand,econ.days,gpu_hour,econ.load,seconds,storage,base,inputs.get('prices.egress'))
                            if run==20 and load=='heavy':
                                # Preserve the published heavy-row display values exactly.
                                anchor=next(r for r in original(20,'engine_sensitivity.csv')if r['server']==key and float(r['share'])==share and r['bridge']=='measured_envelope')
                                price=float(anchor['resident_work_hybrid_person_month'])
                            scope=old.conditional_scope(len(common),len(source_calls),demand*econ.days)if run==20 else new.scope(len(common),len(source_calls),demand*econ.days,profile)
                            out.append(dict(profile=profile,load=load,server=key,share=share,client='m5max64',basis='owned',billing='shared_work',team=50,
                                hybrid_person_month=price,api_median_person_month=api['median']*demand*econ.days,api_cheapest_person_month=api['cheapest']*demand*econ.days,
                                median_multiple=api['median']*demand*econ.days/price,cheapest_multiple=api['cheapest']*demand*econ.days/price,
                                cost_basis='shared resident-work lower bound; zero residency misses; GPU work at70% load; no dedicated fleet calendar or retained-slot occupancy charge',
                                cache_basis='98.1% owner token-cache allowance; provider behaviour unverified; 1.9% misses billed',workload_scope=scope,
                                bridge_basis='token-weighted PR16 smoke through origin; not a measured short-turn fit or upper confidence bound; portability estimated',
                                rate_basis='R20 measured envelope; R21 deeper rates extrapolated'if run==21 else'R20 measured common envelope',
                                source=f'run{run} existing resident-work equation; immutable numeric producer {BASE[run]}'))
        result[run]=out
    return result

def main():
    assert sys.argv[1:]in([],['--audit-only']),'unsupported arguments'
    if not sys.argv[1:]:
        print('label changes',publish_labels20(ROOT/'calc/out/run20'),flush=True)
        shared=shared_tables()
        for run in (20,21):
            projections(run,shared[run]);dump(ROOT/f'calc/ENGINE-QUOTES-R{run}-PAPER-261103.csv',quotes(run));print('paper run',run,flush=True)
    verify_labels20(ROOT/'calc/out/run20')
    for run in (20,21):
        differences(run,ROOT/f'calc/out/run{run}');verify_paper(run);verify_quotes(run)
    print('label-only and paper contracts verified',flush=True)

if __name__=='__main__':main()
