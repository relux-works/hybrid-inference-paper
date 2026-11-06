"""Run14 corrections and held-out checks; no historical scenario opts in."""
import copy
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from .inputs import InputGap
from .performance import flop, payload, transfer, import_at, local_rate_at
from .server_prefill import compute_at, mean_seconds


@lru_cache(maxsize=1)
def evidence():
    return json.loads((Path(__file__).parent/'data/run14-r5.json').read_text())


def import_seconds(tokens, variant='baseline'):
    record = evidence()['client_import'][variant]
    if record.get('gate') != 'measured':
        raise InputGap('measurements.client_import.'+variant, 'Mac gate pending; no admitted rate')
    if not math.isfinite(tokens) or tokens < 0:
        raise InputGap('measurements.client_import', 'finite nonnegative token count required')
    return record['fixed_s']+tokens*record['seconds_token']


def cuda_import_rows():
    """Admit only the preserved PR9 bytes, never a guessed CUDA import rate."""
    from .inputs import ROOT
    info=evidence()['cuda_pr9'];content=(ROOT/info['path']).read_bytes()
    if hashlib.sha256(content).hexdigest()!=info['sha256']:
        raise InputGap('measurements.cuda_import','PR9 byte identity mismatch')
    records=[json.loads(line) for line in content.splitlines()]
    records=[r for r in records if r.get('stage')=='call' and r.get('import_ms',0)>0]
    if not records:raise InputGap('measurements.cuda_import','no positive recorded import times')
    return records


def first_call_check(c):
    """Predict the old chunked protocol, without fitting the unallocated wall time."""
    from .paper_tables import integrate
    e=evidence()['first_call'];n=e['tokens'];m=c.model('qwen27')
    server=c.server('rtx6000',m)
    compute=c.g.resolve(server['compute']).value
    local=c.g.resolve(c.local_rate('m3max',m)).value
    # Old protocol sent the recurrent state four times. The measured wire
    # byte count additionally includes framing; it is not a fitted payload.
    size=n*e['kv_bytes_token']+e['chunks']*e['state_bytes']
    prediction=dict(server_prefill=integrate(lambda d:flop(c.g.resolve(m['flop']).value,d)/compute_at(compute,d),n,512),
                    transfer=e['rtt_s']+size/e['down_bytes_s']+n*4/e['up_bytes_s'],
                    client_import=import_at(c.client_import(),n,0),local=integrate(lambda d:1/(local.cold(d) if hasattr(local,'cold') else local(d)),n,512))
    prediction['total']=sum(prediction[k] for k in ('server_prefill','transfer','client_import'))
    prediction['unallocated']=0.0
    measured=dict(e['measured']);measured['unallocated']=measured['total']-sum(measured[k] for k in ('server_prefill','transfer','client_import'))
    return [dict(component=key,predicted_s=prediction[key],measured_s=value,
                 error_s=prediction[key]-value,error_fraction=(prediction[key]/value-1) if value else 0.0,
                 basis='same PRO6000/M3; old four-state-copy wire; no fitted residual')
            for key,value in measured.items()]


def step57_check(c, records=None):
    """Apply throughput's two resource bounds to the held-out per-call trace.

    This is a steady saturated-capacity prediction of a finite uneven batch,
    not a simulation of llama.cpp scheduling or a fit to elapsed_s.
    """
    from .measurements_r14 import package,one_file,rows,day_bounds
    if records is None:
        _,content=one_file(package('mac')[1],'agents-loop')
        records=rows(content)
    result=[];m=c.model('qwen27');fm=c.g.resolve(m['flop']).value
    local=c.g.resolve(c.local_rate('m3max',m)).value
    server=c.server('rtx6000',m);compute=c.g.resolve(server['compute']).value
    h=c.g.resolve(server['hardware']).value;kv=c.g.resolve(m['kv']).value;state=c.g.resolve(m['state']).value
    weights=c.g.resolve(m['server_weights']).value
    eff=c.inputs.get('owners.server_bw_efficiency');batch=c.inputs.get('owners.server_batch')
    for count in (1,2,4,8):
        trace=[r for r in records if r['kind']=='call' and r['agents']==count]
        summary=next((r for r in records if r['kind']=='round' and r['agents']==count),None)
        if (summary is None or not summary['valid'] or summary['errors'] or summary['rereads'] or
                len(trace)!=summary['calls'] or any(r['reread'] or r['new']<0 or r['gen']<=0 for r in trace)):
            raise InputGap('measurements.step57','invalid held-out trace or reread')
        calls=[(r['depth_before'],r['new'],r['gen'],0) for r in trace]
        steps=[(n/local_rate_at(local,d,n),n/local_rate_at(local,d,n),0,False) for d,n,o,t in calls]
        bounds=day_bounds(calls,steps,count,lambda d:count,c.parallel,1)
        predicted=len(calls)*3600/bounds['calls_day']
        # The existing server model uses a declared batch32 bandwidth bound,
        # never a measured multi-agent server anchor. Expose that limitation.
        server_pred=sum(n*flop(fm,d)/compute_at(compute,d)+o*(weights/batch+(d+n)*kv+2*state)/(h['bandwidth']*eff)
                        for d,n,o,t in calls)
        for device,pred,actual,basis in (
                ('M3 Max',predicted,summary['elapsed_s'],'steady saturated two-bound model; finite-batch drain/queue unmodelled'),
                ('PRO 6000',server_pred,evidence()['step57_server_seconds'][str(count)],'analytical batch32 resource bound; not a server scheduler prediction')):
            result.append(dict(device=device,sessions=count,calls=len(calls),new_tokens=sum(r['new'] for r in trace),
                               generated_tokens=sum(r['gen'] for r in trace),predicted_s=pred,measured_s=actual,
                               error_s=pred-actual,error_fraction=pred/actual-1,basis=basis))
    return result


def full_server_stats(c,calls,server,tier):
    """Resource seconds plus foreground prefills, with separately paid storage.

    Retained HBM/RAM/NVMe is priced as the same incremental session pool for
    both architectures. Active decode residency is charged; tool-idle retention
    is paid in the pool rather than charged a second time as compute occupancy.
    """
    if tier not in ('HBM','RAM','NVMe'):
        raise InputGap('hosting.tier','unsupported symmetric storage tier')
    m=c.model('qwen27');g=c.g
    fm=g.resolve(m['flop']).value;kv=g.resolve(m['kv']).value;state=g.resolve(m['state']).value
    h=g.resolve(server['hardware']).value;free=g.resolve(server['free']).value
    compute=g.resolve(server['compute']).value;weights=g.resolve(m['server_weights']).value
    rate=math.inf if tier=='HBM' else min(c.inputs.get('hosting.pcie_bandwidth'),c.inputs.get('hosting.tiers.'+tier+'.bandwidth'))
    efficiency=c.inputs.get('owners.server_bw_efficiency')
    batch=c.inputs.get('owners.server_batch')
    latency=c.inputs.get('hardware.links.wan.latency')
    decode=residence=migration=0.0;wait=[]
    for d,n,o,t in calls:
        size=(d+n+o)*kv+state
        if size>free:raise InputGap(server['prefix']+'.memory','full session does not fit one replica')
        single=(c.b300.decode(d+n) if server['prefix'].endswith(('b300','b300_node')) else
                h['bandwidth']*efficiency/(weights/batch+(d+n)*kv+2*state))
        decode+=o/single
        residence+=size*(o/single)/free
        reload=0 if d==0 else (d*kv+state)/rate
        migration+=reload+((n+o)*kv+state)/rate
        wait.append(n*flop(fm,d)/compute_at(compute,d)+reload+latency)
    pre=mean_seconds(calls,fm,compute,shadow=False)
    seconds=(pre+(decode+residence+migration)/len(calls))/(h['gpus']*h['shard_efficiency'])
    return dict(seconds=seconds,wait=wait,migration_s=migration/len(calls))


def choose_candidate(candidates,mean_limit,p90_limit):
    admitted=[r for r in candidates if r['prefill_mean_s']<=mean_limit and r['prefill_p90_s']<=p90_limit]
    if not admitted:raise InputGap('r14.symmetric.latency','no configuration meets the common mean/p90 prefill limits')
    return min(admitted,key=lambda r:(r['person_month'],r['server'],r['storage_tier']))


def perimeter_table(c):
    """Uncapped equal-retention, equal-latency owned fleet comparison."""
    from .paper_tables import Context,end_memory
    from .paper_tables_r6 import fleet_units,wait_stats,pool_work,routed_wait
    from .paper import throughput
    from .session_hosting import policy_with_reload
    from .server_prefill import mean_seconds
    tiers={};allrows=[];alternatives=[]
    # One common latency requirement for every option and architecture: the
    # pure-local M3 workload's mean and p90 prefill time, excluding queueing.
    calls=c.g.resolve(c.valid).value;m=c.model('qwen27')
    ref=c.g.resolve(c.local_rate('m3max',m)).value
    limits=wait_stats([(n/ref(d),) for d,n,o,t in calls])
    for tier in ('HBM','RAM','NVMe'):
        inp=copy.deepcopy(c.inputs);inp.override('hosting.tier='+tier)
        cc=Context(c.scenario,inp);mm=cc.model('qwen27');gg=cc.g
        rows=gg.resolve(cc.valid).value;kv=gg.resolve(mm['kv']).value;state=gg.resolve(mm['state']).value
        fm=gg.resolve(mm['flop']).value
        wire=dict(fm,kv=inp.get('owners.models.qwen27.kv'),wire_state=state)
        link={k:inp.get('hardware.links.wan.'+k) for k in ('bandwidth','goodput','latency')}
        servers={}
        for key in c.scenario['perimeter_options']:
            srv=cc.server(key,mm);month=gg.resolve(cc.unit_month('sym.'+key+'.month',srv,'owners.residual')).value
            stat=full_server_stats(cc,rows,srv,tier)
            meanbytes=sum((d+n+o)*kv+state for d,n,o,t in rows)/len(rows)
            store=gg.resolve(cc.hosting.storage('sym.'+key,cc.label('sym.'+key+'.bytes',meanbytes),'owners.hours')).value
            servers[key]=(srv,month,stat,store)
        clients={}
        for client in c.scenario['economics_clients']:
            cl=cc.client(client,'hardware.links.wan.bandwidth','symmetric')
            matched=gg.resolve(cl['matched']).value;local=gg.resolve(cl['local']).value
            memory=end_memory(matched,gg.resolve(cl['memory']).value);decoder=gg.resolve(cl['decoder']).value
            streams=gg.resolve(cl['streams']).value
            localsteps=gg.resolve(cl['local_steps']).value
            localcap=throughput(matched,localsteps,streams,memory,decoder,inp.get('owners.hours'))
            candidates={}
            for key,(srv,month,stat,store) in servers.items():
                vector=gg.resolve(cc.hosting.vector('sym.'+client+'.'+key,cl['matched'],mm['kv'],mm['state'])).value
                steps=policy_with_reload(matched,wire,gg.resolve(srv['compute']).value,link,local,vector,cc.client_import(client))
                hosting=cc.hosting.summary('sym.'+client+'.'+key+'.budget',cl['matched'],mm['kv'],mm['state'],cc.label('sym.'+client+'.'+key+'.steps',steps),'owners.hours')
                gpu=inp.get(srv['prefix']+'.gpus')*inp.get(srv['prefix']+'.shard_efficiency')
                shadow=mean_seconds(matched,fm,gg.resolve(srv['total_compute']).value)
                shadow+=gg.resolve(hosting['seconds']).value/gpu
                candidates[key]=dict(capacity=throughput(matched,steps,streams,memory,decoder,inp.get('owners.hours')),
                    shadow=shadow,eligible=full_server_stats(cc,matched,srv,tier),wait=wait_stats(steps),
                    storage=gg.resolve(hosting['storage']).value,tail=gg.resolve(hosting['flush_seconds']).value/gpu)
            clients[client]=(cl,matched,localsteps,localcap,candidates)
        tiers[tier]=(cc,servers,clients)
        c.inputs.used.update({k:v for k,v in inp.used.items() if k!='hosting.tier'})
    for ti,teamref in enumerate(c.positions('paper_tables.teams')):
        team=c.g.resolve(teamref).value
        for profile in c.scenario['traffic_profiles']:
            requested=c.inputs.get('service.profiles.'+profile)*c.inputs.get('r6.perimeter.share')
            common=dict(profile=profile,team=team,share=c.inputs.get('r6.perimeter.share'),case='closed perimeter; all calls open',office_policy='uncapped cheapest admissible fleet',
                server_precision=c.inputs.get('owners.server_precision'),requested_day=requested,external_calls_day=0,
                latency_mean_limit_s=limits[0],latency_p90_limit_s=limits[1],retention=c.inputs.get('hosting.retention'),
                retained_sessions=c.inputs.get('hosting.sessions_per_person'))
            own={}
            for key in c.scenario['perimeter_options']:
                choices=[]
                for tier,(cc,servers,clients) in tiers.items():
                    srv,month,stat,storage=servers[key];units=fleet_units(team*requested*stat['seconds'],c.inputs.get('owners.hours'),c.inputs.get('owners.load'))
                    fleet=units*month/team;cost=fleet+storage
                    mean,p90=wait_stats([(v,) for v in stat['wait']])
                    choices.append(dict(common,route='all server',client='not applicable',basis='server only',server=c.inputs.locate(srv['label']),
                        client_quant='not applicable',storage_tier=tier,eligible=1,selected=0,client_served_day=0,turbo_day=requested,unserved_day=0,client_served_share=0,client_capacity_day=0,
                        streams=0,min_streams=0,max_streams=0,p90_scope='all calls',prefill_mean_s=mean,prefill_p90_s=p90,units=units,unit_month=month,fleet_person_month=fleet,
                        all_server_call=cost/(requested*c.inputs.get('owners.days')),prefill_reference_month=0,turbo_reference_month=fleet,fleet_adjustment_month=0,
                        device_month=0,client_energy_month=0,front_month=0,hosting_storage_month=storage,person_month=cost))
                best=choose_candidate(choices,*limits)
                alternatives.extend(dict(r,tier_selected=int(r is best)) for r in choices)
                own[key]=best
            chosen=choose_candidate(list(own.values()),*limits)
            for row in own.values():row['selected']=int(row is chosen);allrows.append(row)
            for client in c.scenario['economics_clients']:
                for basis in ('owned','premium'):
                    prefix='hardware.clients.'+client
                    device=0 if basis=='owned' else max(0,c.inputs.get(prefix+'.purchase_price')-c.inputs.get(prefix+'.premium_credit'))*(1-c.inputs.get('owners.residual'))/(12*c.inputs.get('owners.years'))
                    energy=c.inputs.get(prefix+'.power')*c.inputs.get('owners.hours')*c.inputs.get('owners.days')*c.inputs.get('prices.energy_client')
                    cl,matched,localsteps,localcap,_=tiers['RAM'][2][client]
                    fraction=len(matched)/len(calls);served=min(requested*fraction,localcap)
                    base=dict(common,client=c.inputs.locate(prefix+'.label'),basis='Mac already owned' if basis=='owned' else 'Mac premium bought',client_quant=c.inputs.get('owners.client_quant'),
                        streams=c.g.resolve(c.client(client,'hardware.links.wan.bandwidth','symmetric-info')['streams']).value,
                        min_streams=tiers['RAM'][0].g.resolve(cl['min_streams']).value,max_streams=tiers['RAM'][0].g.resolve(cl['max_streams']).value,device_month=device,client_energy_month=energy)
                    mean,p90=wait_stats(localsteps)
                    allrows.append(dict(base,route='Macs only',server='not applicable',storage_tier='client',eligible=1,selected=1,client_served_day=served,turbo_day=0,unserved_day=requested-served,client_served_share=served/requested,client_capacity_day=localcap,
                        p90_scope='client-served subset',prefill_mean_s=mean,prefill_p90_s=p90,units=0,unit_month=0,fleet_person_month=0,all_server_call=0,prefill_reference_month=0,turbo_reference_month=0,fleet_adjustment_month=0,
                        front_month=c.inputs.get('r6.perimeter.local_front_month'),hosting_storage_month=0,person_month=device+energy+c.inputs.get('r6.perimeter.local_front_month')))
                    hybrid={}
                    for key in c.scenario['perimeter_options']:
                        choices=[]
                        for tier,(cc,servers,clients) in tiers.items():
                            srv,month,stat,store=servers[key];cl,matched,localsteps,localcap,candidates=clients[client];p=candidates[key]
                            served=min(requested*fraction,p['capacity']);turbo=requested-served
                            work=pool_work(requested,stat['seconds'],served,p['eligible']['seconds'],p['shadow'])+min(served,c.inputs.get('hosting.sessions_per_person'))*p['tail']
                            units=fleet_units(team*work,c.inputs.get('owners.hours'),c.inputs.get('owners.load'));fleet=units*month/team
                            # Turbo sessions retain state too; pool storage is
                            # charged for every offered session in both routes.
                            storage=store;front=c.inputs.get('owners.front_month')
                            mean=routed_wait(requested,served,p['wait'][0],sum(stat['wait'])/len(calls),sum(p['eligible']['wait'])/len(matched))
                            p90=max(p['wait'][1],wait_stats([(v,) for v in stat['wait']])[1])
                            choices.append(dict(base,route='hybrid',server=c.inputs.locate(srv['label']),storage_tier=tier,eligible=1,selected=0,client_served_day=served,turbo_day=turbo,unserved_day=0,
                                client_served_share=served/requested,client_capacity_day=p['capacity'],p90_scope='max of client and turbo p90',prefill_mean_s=mean,prefill_p90_s=p90,
                                units=units,unit_month=month,fleet_person_month=fleet,all_server_call=own[key]['all_server_call'],prefill_reference_month=fleet,turbo_reference_month=0,fleet_adjustment_month=0,
                                front_month=front,hosting_storage_month=storage,person_month=fleet+device+energy+front+storage))
                        best=choose_candidate(choices,*limits)
                        alternatives.extend(dict(r,tier_selected=int(r is best)) for r in choices)
                        hybrid[key]=best
                    chosen=choose_candidate(list(hybrid.values()),*limits)
                    for row in hybrid.values():row['selected']=int(row is chosen);allrows.append(row)
    def unit(k,v):
        return ('text' if isinstance(v,str) else 'person' if k=='team' else 'call/day' if k.endswith('_day') else
                's/call' if k.endswith('_s') else 'stream' if k.endswith('streams') else 'USD/server-month' if k=='unit_month' else
                'USD/call' if k=='all_server_call' else 'USD/person-month' if k.endswith('_month') else 'server unit' if k=='units' else '1')
    for name,rs in [('perimeter_cost',allrows),('symmetric_storage_candidates',alternatives)]+[('perimeter_cost_'+p,[r for r in allrows if r['profile']==p]) for p in c.scenario['traffic_profiles']]:
        units={k:unit(k,v) for k,v in rs[0].items()}
        # Retention is a real input to the precomputed candidate prices; keep
        # its graph dependency so conservative exports retain these tables.
        graphrows=[{k:c.add('sym.export.'+name+'.'+str(i)+'.'+k,['hosting.retention'],lambda retention,v=v:v) for k,v in r.items()} for i,r in enumerate(rs)]
        c.table(name,'Symmetric owned fleets: cheapest admissible hardware and retention tier',units,graphrows)


def append_checks(result,c):
    from .measurements_r14 import raw_table
    from .prefill_price_r14 import append_table
    if not c.scenario.get('export_suffix'):
        append_table(result,c)
    records=first_call_check(c)
    raw_table(result,'e2e_first_call_check',records,{k:'text' if isinstance(v,str) else 's' if k.endswith('_s') else '1' for k,v in records[0].items()})
    records=step57_check(c)
    raw_table(result,'step57_model_check',records,{k:'text' if isinstance(v,str) else 's' if k.endswith('_s') else '1' for k,v in records[0].items()})
    pending=dict(alarm=[dict(input='measurements.client_import.import_speed_v2',reason='Mac gate pending; CPU speedup is not a Mac rate')])
    cl=c.client('m3max','hardware.links.wan.bandwidth','import-sensitivity')
    capacity=c.g.resolve(cl['capacity']).value/c.inputs.get('workload.chunk_calls')
    record=evidence()['client_import']['baseline']
    records=[dict(variant='pre-import-speed-v2',tokens=record['tokens'],seconds=record['seconds'],fixed_s=record['fixed_s'],seconds_token=record['seconds_token'],m3_four_sessions_day=capacity,basis='M3 single point; fixed0 unidentified assumption; other Apple clients estimated same token rate'),
             dict(variant='import-speed-v2',tokens=pending,seconds=pending,fixed_s=pending,seconds_token=pending,m3_four_sessions_day=pending,basis='Mac gate pending')]
    raw_table(result,'client_import_sensitivity',records,dict(variant='text',tokens='token',seconds='s',fixed_s='s',seconds_token='s/token',m3_four_sessions_day='session/day',basis='text'))
    rows_=cuda_import_rows()
    records=[dict(mode=r['benchmark_mode'],depth=r['prompt_depth'],imported_tokens=r['remote_applied'],
                  bytes=r['wire_bytes'],import_s=r['import_ms']/1000,rate_bytes_s=r['wire_bytes']/(r['import_ms']/1000),
                  predicted_import_s=import_seconds(r['remote_applied'],'cuda_pr9'),
                  basis='PR9 PRO6000 CUDA Q4 client; separate from M3 rate')
             for r in rows_]
    raw_table(result,'cuda_client_import',records,dict(mode='text',depth='token',imported_tokens='token',bytes='B',import_s='s',rate_bytes_s='B/s',predicted_import_s='s',basis='text'))
