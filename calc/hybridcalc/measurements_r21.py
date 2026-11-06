"""Two workload profiles and conditional million-token economics, CPU only."""
import copy
import hashlib
import json
import math

from .inputs import ROOT, InputGap
from . import deep_r21 as d, measurements_r20 as old
from . import measurements_r16 as r16, measurements_r19 as r19
from . import server_economics_r20 as s


def unit(key,value):
    if key.endswith('_depth'):return 'token'
    if key=='tasks_day':return 'task/person/day'
    if key=='calls_per_task':return 'call/task'
    if key=='bytes_s':return 'B/s'
    if key=='threshold_MB_s':return 'MB/s (decimal)'
    if key=='warm_rental_floor_node_month':return 'USD/node-month'
    return old.unit(key,value)


class Prepared(old.Prepared):
    """R20 routing/accounting with explicitly extrapolated Mac prefill."""
    def __init__(self,calls,server,client,context,bridge,measurements):
        self.calls=calls;self.server=server;self.client=client;self.context=context
        self.bridge=bridge;self.measurements=measurements
        self.own=[];self.pre=[];self.shadow=[];self.output=[]
        self.wire=[];self.imports=[];self.rebuild=[]
        cl=context.client(client,'hardware.links.wan.bandwidth','r21')
        self.streams=context.g.resolve(cl['streams']).value
        self.memory=context.g.resolve(cl['memory']).value
        self.decoder=context.g.resolve(cl['decoder']).value
        self.profiles={x['key']:x for x in r19.links(context.inputs)}
        self.decode_device=[];self.decode_occupied=[];self.wait_weight=[]
        importer=r16.ClientImport()
        for depth,n,o,tool in calls:
            server.slots(depth+n+o)
            self.own.append(d.mac_prefill(context,client,depth,n))
            self.pre.append(server.cached(depth,n,bridge))
            base=server.cached(depth,n)
            self.shadow.append(base*(n+o)/n if n else server.cached(depth,o))
            self.output.append(base*o/n if n else server.cached(depth,o))
            self.wire.append(n*r19.KV+r19.STATE)
            self.imports.append(importer.at_depth(n,depth))
            self.rebuild.append(server.cold(depth))
            k=min(self.streams,self.memory(depth+n+o))
            if k<1:raise InputGap('run21.client','complete session does not fit client')
            rate=self.decoder(k,depth+n)
            self.decode_device.append(o/(k*rate))
            self.decode_occupied.append((o/rate+tool)/k);self.wait_weight.append(1/k)


class Economics(old.Economics):
    def __init__(self,context,calls,servers,cfg,api):
        plain=copy.deepcopy(cfg);plain['server_decode']={'measurements':[]}
        super().__init__(context,calls,servers,plain,api)
        self.measurements=d.decode_measurements(cfg['server_decode'],servers)
        for key,server in servers.items():
            for client in ('m5max64','m5max'):
                self.prepared[key,client,'measured_envelope']=Prepared(calls,server,client,context,'measured_envelope',self.measurements)


def scope(common,total,monthly,profile):
    return ('{}: conditional reconstructed/fitted calls {}/{} ({:.2f}%); normalized to {:g} calls/person-month; '.format(profile,common,total,100*common/total,monthly)+
        'full original workload unsupported; deep rates extrapolated; sufficient hybrid fleet, not minimal')


def profile_api(calls,indices,profile,cfg,chunk):
    # Previous generated output belongs to the original normalization group,
    # including when its call is excluded from the hardware-common subset.
    billed=old.billing_calls(calls,indices,chunk)
    needed=math.ceil(max(depth+n+o for depth,n,o,t in billed))
    return d.api_baselines(billed,profile,cfg,needed)


def profile_reservation(calls,minimum,servers):
    depth=max(minimum,max(a+b+c for a,b,c,t in calls))
    for server in servers.values():server.slots(depth)
    return depth


def decode_table(servers,measurements):
    rows=[]
    for key,server in servers.items():
        for depth in (16000,64000,164000,512000,1000000):
            for streams in (1,8,32):
                try:
                    anchors=[x for x in measurements if x['server']==key and x['streams']==min(streams,server.slots(depth))]
                    use=anchors and min(x['depth']for x in anchors)<=depth<=max(x['depth']for x in anchors)
                    dec=server.decode(depth,streams,measurements if use else None)
                except InputGap as exc:
                    if 'one complete session does not fit'not in str(exc):raise
                    dec=dict(batch=s.alarm(str(exc)),single_tok_s=s.alarm(str(exc)),aggregate_tok_s=s.alarm(str(exc)),gain=s.alarm(str(exc)),basis='capacity refusal')
                rows.append(dict(server=key,model='qwen',depth=depth,requested_streams=streams,**dec,
                    context_basis=d.extension_basis('qwen','server'),session_bytes=server.session_bytes(depth)))
    return rows


def million_links(context,servers,cfg):
    rows=[];depth=1000000;n=690
    for key,server in servers.items():
        for client in ('m3max','m5max64'):
            for variant in ('measured_anchor_flop_extension','analyst_120s_at_1M'):
                local=d.mac_prefill(context,client,depth,n,variant)
                pre=server.cached(depth,n,'measured_envelope')
                imp=r16.ClientImport().at_depth(n,depth)
                wire=n*r19.KV+r19.STATE
                for link in cfg['links']:
                    budget=local-pre-imp-link['rtt_s']
                    remote=pre+imp+link['rtt_s']+wire/link['bytes_s']
                    try:server.slots(depth+n);fits=True
                    except InputGap:fits=False
                    threshold=wire/budget/1e6 if budget>0 and fits else s.alarm('nonpositive budget or server session capacity refusal')
                    rows.append(dict(server=key,client=client,depth=depth,delta=n,link=link['key'],bytes_s=link['bytes_s'],
                        wire_bytes=wire,transfer_s=wire/link['bytes_s'],local_prefill_s=local,server_prefill_s=pre,import_s=imp,
                        remote_s=remote,threshold_MB_s=threshold,offload=fits and remote<local,
                        rate_basis=variant+'; no measured1M delta-prefill; Mac depth-import slope extrapolated',
                        link_basis=link['basis'],extension_basis=d.extension_basis('qwen','client')))
    return rows


def glm_batch(depth,streams,inputs):
    """Two B300 GPUs per FP8 GLM replica; expert union read once per step."""
    r19.integer(streams,'streams')
    p='models.glm.';get=lambda k:inputs.get(p+k)
    weights=get('server_weights');kv=get('kv');state=get('state')
    free=2*288e9-weights-2*8e9
    slots=math.floor(free/(kv*depth+state));k=min(streams,slots)
    if k<1:raise InputGap('run21.glm','complete GLM session does not fit two-GPU replica')
    def traffic(b):
        union=get('experts')*(1-(1-get('active_experts')/get('experts'))**b)
        return get('server_shared_bytes')+get('server_routed_bytes')*union/get('active_experts')+b*(kv*depth+state)
    bw=2*8e12*.7
    single=bw/traffic(1);aggregate=k*bw/traffic(k)
    return dict(batch=k,single_tok_s=single,aggregate_tok_s=aggregate,gain=aggregate/single,
        session_bytes=kv*depth+state,weights_bytes=weights,replica_gpus=2,
        basis='modelled expert union + full per-session KV/state; ideal two-GPU bandwidth sum, communication omitted; no GLM vLLM measurement')


def million_own(context,server,model,demand,pre,cold,team=50):
    """Finite team concurrency and integer complete replicas, R20 two bounds."""
    r19.integer(team,'team');s.r18.positive(demand,'demand')
    depth=1000000;o=762;tool=8.1
    if model=='qwen':
        replicas_box=8;decode=lambda k:server.decode(depth,k)
        slot=server.session_bytes(depth);slots=server.slots(depth)
    elif model=='glm':
        replicas_box=4;decode=lambda k:glm_batch(depth,k,context.inputs)
        slot=5984*depth+152600000;slots=math.floor((2*288e9-328e9-2*8e9)/slot)
    else:raise InputGap('run21.million','unknown model')
    offered=4*team;budget=context.inputs.get('paper_tables.hours')*3600*.7
    for boxes in range(1,501):
        replicas=boxes*replicas_box
        resident=replicas*slots;spilled=max(0,offered-resident)
        if spilled*slot>boxes*900e9:continue
        active=min(replicas,offered);streams=min(offered,active*min(32,slots))
        lo,extra=divmod(streams,active)
        aggregate=(active-extra)*decode(lo)['aggregate_tok_s']+(extra*decode(lo+1)['aggregate_tok_s']if extra else 0)
        seconds=max(pre/active+o/aggregate,(pre+o/(aggregate/streams)+tool)/streams)+(spilled/offered)*cold/active
        if team*demand*seconds<=budget:
            return dict(person_month=boxes*s.unit_month(server,context.inputs,'bought')[0]/team,
                boxes=boxes,total_streams=streams,spill_share=spilled/offered,batch_min=lo)
    return dict(person_month=s.alarm('finite concurrency or500-box scan cannot serve million demand'),
        boxes=s.alarm('no sufficient million fleet'),total_streams=offered,spill_share=0,batch_min=0)


def million_economics(context,servers,cfg):
    """Same task and load; work allocation and calendar floor shown separately."""
    # Reserve answer within the API's advertised total context.
    n=690;o=762;depth=1000000-n-o
    calls=[(depth,n,o,8.1)]
    apis,selected=d.api_baselines(calls,'million',cfg,1000000)
    rows=[]
    for model in ('qwen','glm'):
        if model=='qwen':
            server=servers['b300_fp8_kv'];batch=server.decode(depth,32)
            pre=server.cached(depth,n,'measured_envelope');gpu_count=1
            decode_s=o/1.67;client_cost=0;client_basis='already owned M3 Max;1.67tok/s measured at1.04M background priority, reused at1M'
            wire=n*r19.KV+r19.STATE;local=120*n/690
            basis='vLLM Qwen deep TTFT extrapolated; FP8 KV bridge portability unmeasured;1M local delta120s analyst estimate'
            cold=server.cold(depth)
        else:
            batch=glm_batch(depth,32,context.inputs);gpu_count=2
            ratio=(context.inputs.get('models.glm.base_flop')+context.inputs.get('models.glm.attention_slope')*depth+context.inputs.get('models.glm.sparse_slope')*8192)/(54e9+393216*depth)
            pre=servers['b300_fp8_kv'].cached(depth,n,'measured_envelope')*ratio
            client_single=.4*819.2e9/(context.inputs.get('models.glm.shared_bytes')+context.inputs.get('models.glm.routed_bytes')+context.inputs.get('models.glm.kv')*depth+context.inputs.get('models.glm.state'))
            decode_s=o/client_single;client_cost=8000*.65/48
            client_basis='unmeasured M5 Ultra256GB:819.2GB/s*40%,181.4GB Q4 weights; $8000 new device estimate'
            wire=n*context.inputs.get('models.glm.kv')+context.inputs.get('models.glm.state')
            local=n/(1000000/(57*60))
            basis='GLM B300 prefill carried from Qwen by architecture FLOP ratio; unmeasured; Studio1M in57min is estimate, cold average reused as delta sensitivity'
            cold=servers['b300_fp8_kv'].cold(depth)*ratio
        for load in ('light','medium','heavy'):
            demand=context.inputs.get('service.profiles.'+load);monthly=demand*context.inputs.get('owners.days')
            hours=context.inputs.get('paper_tables.hours')
            own=million_own(context,servers['b300_fp8_kv'],model,demand,pre,cold)
            for link in cfg['links']:
                imp=r16.ClientImport().at_depth(n,depth) # GLM endpoint portability remains unmeasured.
                remote=pre+imp+wire/link['bytes_s']+link['rtt_s'];offload=remote<local
                capacity=hours*3600/((remote if offload else local)+decode_s+8.1)
                served=min(demand,capacity);overflow=demand-served
                own_seconds=pre+o/batch['aggregate_tok_s']
                work_gpu=(served*pre*offload+overflow*own_seconds)*gpu_count
                allocation=work_gpu*context.inputs.get('owners.days')*76/(8*3600*.7)
                cheapest=selected[model]['cheapest'];median=selected[model]['median']
                api_cheap=cheapest*monthly if isinstance(cheapest,(int,float))else cheapest
                api_median=median*monthly if isinstance(median,(int,float))else median
                rows.append(dict(profile='million',model=model,load=load,link=link['key'],depth=depth,delta=n,output_tokens=o,team=50,
                    batch=batch['batch'],batch_gain=batch['gain'],own_decode_s_call=o/batch['aggregate_tok_s'],
                    prefill_s=pre,wire_bytes=wire,offload=offload,served_local_day=served,server_decode_overflow_day=overflow,
                    hybrid_work_person_month=allocation+client_cost,client_month=client_cost,
                    warm_rental_floor_node_month=76*730,own_cluster_person_month=own['person_month'],own_cluster_boxes=own['boxes'],
                    own_total_streams=own['total_streams'],own_spill_share=own['spill_share'],
                    api_cheapest_person_month=api_cheap,api_median_person_month=api_median,
                    hybrid_work_usd_per_1000_calls=(allocation+client_cost)/monthly*1000,
                    basis=basis+'; resident shared-work allocation lower bound; dedicated calendar floor separate; no replica communication/persistence/startup guarantee; GLM import uses Mac Qwen proxy',
                    client_basis=client_basis,extension_basis=d.extension_basis(model,'client')))
    return rows,apis


def calculate(scenario,inputs):
    from .engine import load
    from .paper_tables import Context
    cfg=d.config();stats=d.checked_stats(cfg);spec,_=load('paper-tables-r17');context=Context(spec,inputs)
    original=context.g.resolve(context.valid).value
    existing_hash=hashlib.sha256(json.dumps(original,separators=(',',':')).encode()).hexdigest()
    server_cfg=s.config();server_cfg['servers']={key:server_cfg['servers'][key]for key in d.SERVERS}
    server_cfg['reservation_depth']=cfg['reservation_depth'];server_cfg['server_decode']=cfg['server_decode']
    servers={key:d.Server(key,server_cfg)for key in d.SERVERS}
    measurements=d.decode_measurements(cfg['server_decode'],servers)
    result=dict(scenario=scenario['name'],tables=[],alarms=[],computed_metrics=0,export_namespace='r21',notes=[
        'R20 base b6ac5abc review pending. R13–20 export snapshots immutable. R19 F1 corrected successor view under run21; historical R20 5090 server rows not used in paper.',
        'Existing seeded combined profile unchanged. Claude-only aggregates support quantile reconstruction, not raw call replay; conditional mean delta per depth bin; output/pause ranks permuted independently. No recovered correlations or exact pauses.',
        'All rates beyond measured ladders, Mac depth-import slope, GLM and1M economics labelled extrapolations. YaRN factor4 required on hybrid; API extension unknown. API cache98.1% allowance from source-bound R20 owner notes, not provider verification.',
        '5090 excluded as server by owner; measured5090 client data/interface unchanged. Sufficient hybrid fleets are not minimal. Office zero boxes in historical R19 means policy bypass, not free service; historical share table is NVMe.'])
    small=[];main=[];breaks=[];apis=[];coverage=[];model_check=[]
    for profile,calls in (('existing_combined',original),('claude_deep',d.reconstruct(stats['agents']['claude'],cfg['quadrature_points'],cfg['active_gap_cap_s']))):
        for i,metric in enumerate(('depth_per_call','new_in_per_call','output_per_call','gap_seconds')):
            values=sorted(x[i]for x in calls)
            source=stats['agents']['all'if profile=='existing_combined'else'claude'][metric]
            model_check.append(dict(profile=profile,metric=metric,source_mean=source['mean'],model_mean=sum(values)/len(values),
                source_p50=source['p50'],model_p50=values[len(values)//2],source_p90=source['p90'],model_p90=values[int(len(values)*.9)],
                basis='existing seeded workload unchanged'if profile=='existing_combined'else'quantile+mean calibrated; conditional depth-bin delta mean; permuted ranks; active gap cap300s estimated, raw idle gap mean333s'))
        # Common hardware envelope protects identical API/hybrid/cluster mixes.
        max_end=min(d.LIMIT,min((server.free-server.state)/server.kv for server in servers.values()))
        indices=[i for i,(depth,n,o,t)in enumerate(calls)if depth+n+o<=max_end]
        common=[calls[i]for i in indices]
        if not common:raise InputGap('run21.profile','empty common physically admitted workload')
        api_rows,api=profile_api(calls,indices,profile,cfg,inputs.get('workload.chunk_calls'))
        apis+=api_rows
        profile_cfg=copy.deepcopy(server_cfg)
        profile_cfg['reservation_depth']=profile_reservation(common,cfg['reservation_depth'],servers)
        econ=Economics(context,common,servers,profile_cfg,{'main':api['qwen']})
        coverage.append(dict(profile=profile,source_calls=len(calls),common_calls=len(common),common_fraction=len(common)/len(calls),max_end_depth=max_end,
            reservation_depth=profile_cfg['reservation_depth'],
            sampler_basis='unchanged seeded existing calls'if profile=='existing_combined'else'aggregate quantile reconstruction; estimated joint law',
            existing_profile_sha256=existing_hash,full_workload_cost=s.alarm('unconditioned mix unsupported; common physical envelope excludes tail')))
        for load in ('light','medium','heavy'):
            for share in server_cfg['shares']:
                demand=inputs.get('service.profiles.'+load)*share
                for client in ('m5max64','m5max'):
                    for basis in ('owned','new'):
                        for key in d.SERVERS:
                            for billing in ('bought','rented'):
                                costs=[];refs={k:[]for k in ('api_cheapest','api_median','own_cluster')}
                                for team in range(1,cfg['scan_team_max']+1):
                                    h=econ.hybrid(key,team,demand,client,basis,billing,'measured_envelope')
                                    best_key,best=old.best_own(econ,d.SERVERS,team,demand)
                                    costs.append(h['person_month'])
                                    for ref,label in (('api_cheapest','cheapest'),('api_median','median')):
                                        price=api['qwen'][label];refs[ref].append(price*demand*econ.days if isinstance(price,(int,float))else price)
                                    refs['own_cluster'].append(best['person_month'])
                                    if team in (3,5,10,20,50,500):
                                        row=dict(profile=profile,load=load,share=share,client=client,basis=basis,server=key,billing=billing,team=team,
                                            **h,api_cheapest_person_month=refs['api_cheapest'][-1],api_median_person_month=refs['api_median'][-1],
                                            own_cluster_person_month=best['person_month'],own_cluster_server=best_key,
                                            median_over_hybrid=old.ratio(refs['api_median'][-1],h['person_month']),cheapest_over_hybrid=old.ratio(refs['api_cheapest'][-1],h['person_month']),
                                            usd_per_1000_calls=old.ratio(h['person_month'],demand*econ.days/1000),
                                            workload_scope=scope(len(common),len(calls),demand*econ.days,profile),
                                            rate_basis='vLLM measured<=249k; deeper/long delta extrapolated; M5 rates/decoder beyond ladder estimated; Mac import slope extrapolated')
                                        (small if team in (3,5,10,20)else main).append(row)
                                for ref,values in refs.items():
                                    breaks.append(dict(profile=profile,load=load,share=share,client=client,basis=basis,server=key,billing=billing,reference=ref,
                                        **old.break_even(costs,values),workload_scope=scope(len(common),len(calls),demand*econ.days,profile)))
    million,million_api=million_economics(context,servers,cfg);apis+=million_api
    glm=[]
    for depth in (16000,64000,164000,512000,1000000):
        for streams in (1,8,32):glm.append(dict(model='glm',depth=depth,requested_streams=streams,**glm_batch(depth,streams,inputs)))
    ceiling=d.mac_ceiling(1000000,inputs.get('hardware.clients.m3max.bandwidth'))
    ceiling_rows=[dict(client='m3max',depth=1000000,ceiling_tok_s=ceiling,measured_decode_tok_s=cfg['mac_1M_decode_measured'],
        measured_depth=cfg['mac_1M_decode_depth'],priority=cfg['mac_1M_decode_priority'],ceiling_over_measured=ceiling/cfg['mac_1M_decode_measured'],
        basis='raw memory bandwidth ceiling; complete Q4 weights + q8 KV + one state read; not achievable rate; measured gap and PRI31 qualification open')]
    tables=(('workload_profiles',d.profile_rows(stats)),('profile_model_check',model_check),('workload_coverage',coverage),('small_team_cost',small),('main_economics',main),
        ('team_break_even',breaks),('api_admission',apis),('decode_scaling',decode_table(servers,measurements)),('glm_decode_scaling',glm),
        ('million_link_thresholds',million_links(context,servers,cfg)),('million_economics',million),('decode_ceiling',ceiling_rows),
        ('r19_rented_prefill_corrected',d.corrected_r19()))
    for name,rows in tables:
        # Historical CSV display strings remain strings in its successor view.
        r16.add_table(result,name,rows)
        table=result['tables'][-1]
        for key in table['columns']:
            value=next((r[key]for r in rows if not isinstance(r[key],dict)),None)
            table['columns'][key]=unit(key,value)
        if name=='workload_profiles':table['columns']['value']='mixed; see value_unit'
        if name=='profile_model_check':
            for key in ('source_mean','model_mean','source_p50','model_p50','source_p90','model_p90'):
                table['columns'][key]='s for gap_seconds; token otherwise'
        if name=='r19_rented_prefill_corrected':
            table['columns']=json.loads((ROOT/'calc/out/run19/r19_schema.json').read_text())['rented_prefill_node']['columns']
    old.r18_sources(inputs)
    for path in (d.CONFIG,d.STATS,ROOT/'data/research/models-apis-2026-10.md',ROOT/'calc/out/run19/rented_prefill_node.csv'):
        name=str(path.relative_to(ROOT));inputs.files[name]=dict(path=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result
