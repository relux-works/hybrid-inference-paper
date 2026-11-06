"""Run20 same-mix vLLM, admitted API and integer small-team economics."""
import functools
import hashlib
import json
import math

from .inputs import InputGap,ROOT
from . import server_economics_r20 as s,measurements_r16 as r16,measurements_r19 as r19
from .session_hosting import route
from .paper import throughput


def capacity_result(kind):
    """Unserviceable demand is an explicit alarm row, never a free price."""
    fields={'own':('person_month','boxes','gpu_s_call','spill_share','decode_s_call','batch_min','unit_month'),
        'hybrid':('person_month','boxes','unit_month','device_month','client_energy_month','front_month','server_person_month','storage_person_month','served_day','server_decode_overflow_day','spill_share','offload_share','client_capacity_day','prefill_gpu_s_day','decode_overflow_gpu_s_day','pending_s_offload')}
    def decorate(fn):
        @functools.wraps(fn)
        def checked(*args,**kwargs):
            try:return fn(*args,**kwargs)
            except InputGap as exc:
                if 'finite team concurrency cannot serve' not in str(exc):raise
                return {key:s.alarm(str(exc)) for key in fields[kind]}
        return checked
    return decorate


def ratio(a,b):
    if isinstance(a,dict)or isinstance(b,dict):return s.alarm('price ratio unavailable: capacity-refused alternative')
    return a/b


def best_own(econ,keys,team,demand):
    own={k:econ.own(k,team,demand) for k in keys}
    admitted=[k for k,v in own.items() if isinstance(v['person_month'],(int,float))]
    if not admitted:return 'none_capacity_admitted',dict(person_month=s.alarm('no all-server configuration serves demand'),boxes=s.alarm('no all-server configuration serves demand'))
    key=min(admitted,key=lambda k:own[k]['person_month']);return key,own[key]


class Prepared:
    def __init__(self,calls,server,client,context,bridge,measurements):
        self.calls=calls;self.server=server;self.client=client;self.context=context;self.bridge=bridge;self.measurements=measurements
        self.own=[];self.pre=[];self.shadow=[];self.output=[];self.wire=[];self.imports=[];self.rebuild=[]
        for d,n,o,t in calls:
            server.slots(d+n+o)
            rate=context.measured_m5.prefill(d)
            self.own.append(n/rate);self.pre.append(server.cached(d,n,bridge))
            base=server.cached(d,n)
            self.shadow.append(base*(n+o)/n);self.output.append(base*o/n)
            self.wire.append(n*r19.KV+r19.STATE);self.imports.append(r16.ClientImport().at_depth(n,d))
            self.rebuild.append(server.cold(d))
        p='hardware.clients.'+client
        cl=context.client(client,'hardware.links.wan.bandwidth','r20')
        self.streams=context.g.resolve(cl['streams']).value
        self.memory=context.g.resolve(cl['memory']).value
        self.decoder=context.g.resolve(cl['decoder']).value
        self.profiles={x['key']:x for x in r19.links(context.inputs)}
        self.decode_device=[];self.decode_occupied=[];self.wait_weight=[]
        # Complete end-of-call KV fits before throughput may credit any stream.
        for d,n,o,tool in calls:
            k=min(self.streams,self.memory(d+n+o))
            if k<1:raise InputGap('run20.client','full end-of-call session does not fit client')
            rate=self.decoder(k,d+n)
            self.decode_device.append(o/(k*rate));self.decode_occupied.append((o/rate+tool)/k);self.wait_weight.append(1/k)

    @functools.lru_cache(maxsize=None)
    def stats(self,spill,link_key):
        s.fraction(spill,'spill');link=self.profiles[link_key]
        remote=[a+spill*c+b/link['bytes_s']+link['rtt_s']+i for a,c,b,i in zip(self.pre,self.rebuild,self.wire,self.imports)]
        steps=route(self.own,remote,[(1-spill)*x for x in self.shadow],[(1-spill)*x for x in self.output],self.wire,self.imports,'at_offload')
        count=sum(x[3]for x in steps);N=len(steps)
        gpu=sum(a+steps.pending_seconds+spill*c for a,c,x in zip(self.pre,self.rebuild,steps)if x[3])/N
        # Match the existing throughput's two bounds while admitting end depth.
        device=sum(x[1]+d for x,d in zip(steps,self.decode_device))
        occupied=sum(x[0]*w+d for x,w,d in zip(steps,self.wait_weight,self.decode_occupied))
        capacity=self.context.inputs.get('paper_tables.hours')*3600/(max(device,occupied)/N)
        return dict(offload_share=count/N,gpu_s_call=gpu,client_capacity_day=capacity,
            wire_bytes_call=sum(x[2]for x in steps)/N,pending_s_offload=steps.pending_seconds,
            prefill_wait_s_call=sum(x[0]for x in steps)/N,spill_share=spill)


class Economics:
    def __init__(self,context,calls,servers,cfg,api):
        self.context=context;self.inputs=context.inputs;self.calls=calls;self.servers=servers;self.cfg=cfg;self.api=api
        self.days=self.inputs.get('owners.days');self.hours=self.inputs.get('paper_tables.hours');self.load=self.inputs.get('owners.load')
        self.sessions=self.inputs.get('hosting.sessions_per_person');self.concurrency=self.inputs.get('paper_tables.streams');self.measurements=s.decode_measurements(cfg['server_decode'],servers)
        self.prepared={};self.own_cache={};self.units={};self.fleet_cache={};self.decode_vectors={}
        for key,server in servers.items():
            for billing in ('bought','rented'):self.units[key,billing]=s.unit_month(server,self.inputs,billing)
        self.base_prefill={key:sum(server.cached(d,n)for d,n,o,t in calls)/len(calls)for key,server in servers.items()}
        self.cold={key:sum(server.cold(d)for d,n,o,t in calls)/len(calls)for key,server in servers.items()}

    def retention(self,server,team,boxes,gpus):
        slot=server.session_bytes(self.cfg['reservation_depth']);resident=server.slots(self.cfg['reservation_depth'])*boxes*gpus
        total=team*self.sessions;miss=max(0,1-resident/total);host=max(0,total-resident)*slot
        if host>boxes*self.cfg['host_nvme_bytes']:raise InputGap('run20.retention','retained sessions exceed per-node NVMe capacity')
        return miss,host

    def storage_boxes(self,server,team,gpus):
        slot=server.session_bytes(self.cfg['reservation_depth'])
        capacity=server.slots(self.cfg['reservation_depth'])*gpus+math.floor(self.cfg['host_nvme_bytes']/slot)
        if capacity<1:raise InputGap('run20.retention','no complete retained session fits')
        return max(1,math.ceil(team*self.sessions/capacity))

    def own_stats(self,server,concurrent):
        key=server.key,concurrent
        if key in self.own_cache:return self.own_cache[key]
        seconds=decode=occupied=0;batch_min=concurrent
        for d,n,o,t in self.calls:
            k=min(concurrent,server.slots(d+n))
            anchors=[x for x in self.measurements if x['server']==server.key and x['streams']==k]
            measured=bool(anchors) and min(x['depth'] for x in anchors)<=d+n<=max(x['depth'] for x in anchors)
            dec=server.decode(d+n,concurrent,self.measurements if measured else None)
            k=dec['batch'];batch_min=min(batch_min,k);dec_s=o/dec['aggregate_tok_s'];pre=server.cached(d,n)
            # Tool pauses consume session occupancy even when weights are shared.
            seconds+=max(pre+dec_s,(pre+o/(dec['aggregate_tok_s']/k)+t)/k)
            decode+=dec_s;occupied+=(pre+o/(dec['aggregate_tok_s']/k)+t)/k
        N=len(self.calls);result=dict(seconds=seconds/N,decode_s_call=decode/N,occupied_s_call=occupied/N,batch_min=batch_min)
        self.own_cache[key]=result;return result

    def fleet_stats(self,server,team,boxes,gpus):
        # A fixed team supplies at most4T concurrent sessions across ALL GPUs.
        active=min(boxes*gpus,int(team*self.concurrency));offered=min(int(team*self.concurrency),32*active)
        key=server.key,active,offered
        if key in self.fleet_cache:return self.fleet_cache[key]
        if server.key not in self.decode_vectors:
            vectors=[]
            for d,n,o,tool in self.calls:
                slots=server.slots(d+n+o);rates={}
                for k in range(1,min(32,slots)+1):
                    anchors=[x for x in self.measurements if x['server']==server.key and x['streams']==k]
                    measured=bool(anchors) and min(x['depth'] for x in anchors)<=d+n<=max(x['depth'] for x in anchors)
                    rates[k]=server.decode(d+n,k,self.measurements if measured else None)['aggregate_tok_s']
                vectors.append((server.cached(d,n),o,tool,min(32,slots),rates))
            self.decode_vectors[server.key]=vectors
        total=dec_total=0;minimum=32;max_total=0
        for pre,o,tool,slots,rates in self.decode_vectors[server.key]:
            streams=min(offered,active*slots);lo,extra=divmod(streams,active)
            aggregate=(active-extra)*rates[lo]+(extra*rates[lo+1] if extra else 0)
            # Balanced integer batches; spare GPUs never invent extra sessions.
            seconds=max(pre/active+o/aggregate,(pre+o/(aggregate/streams)+tool)/streams)
            total+=seconds;dec_total+=o/aggregate;minimum=min(minimum,lo);max_total=max(max_total,streams)
        result=dict(fleet_s_call=total/len(self.calls),decode_fleet_s_call=dec_total/len(self.calls),active_gpus=active,batch_min=minimum,total_streams=max_total)
        self.fleet_cache[key]=result;return result

    @functools.lru_cache(maxsize=None)
    @capacity_result('own')
    def own(self,key,team,demand,billing='bought'):
        r19.integer(team,'team');s.r18.positive(demand,'demand')
        server=self.servers[key];month,gpus=self.units[key,billing]
        low=self.storage_boxes(server,team,gpus);budget=self.hours*3600*self.load
        # Grow an upper bracket, then use monotonic aggregate bandwidth and
        # residency to find the smallest sufficient integer fleet.
        def evaluate(boxes):
            spill,host=self.retention(server,team,boxes,gpus);stat=self.fleet_stats(server,team,boxes,gpus)
            seconds=stat['fleet_s_call']+spill*self.cold[key]/stat['active_gpus']
            return team*demand*seconds<=budget,spill,host,stat,seconds
        high=low
        while not evaluate(high)[0]:
            if high>=1000000:raise InputGap('run20.fleet','finite team concurrency cannot serve demand in the active window')
            # If every offered stream has a GPU, more boxes cannot cure a
            # session-occupancy limit. Report refusal instead of growing forever.
            if high*gpus>=team*self.concurrency and self.retention(server,team,high,gpus)[0]==0:
                raise InputGap('run20.fleet','finite team concurrency cannot serve demand in the active window')
            high*=2
        while low<high:
            mid=(low+high)//2
            if evaluate(mid)[0]:high=mid
            else:low=mid+1
        boxes=low;_,spill,host,stat,seconds=evaluate(boxes)
        storage=host/1e9*self.inputs.get('hosting.tiers.NVMe.price') if billing=='rented'else 0
        return dict(person_month=boxes*month/team+storage/team,boxes=boxes,gpu_s_call=seconds*stat['active_gpus'],spill_share=spill,
            decode_s_call=stat['decode_fleet_s_call']*stat['active_gpus'],batch_min=stat['batch_min'],unit_month=month)

    @functools.lru_cache(maxsize=None)
    @capacity_result('hybrid')
    def hybrid(self,key,team,demand,client,basis,billing,bridge):
        r19.integer(team,'team');s.r18.positive(demand,'demand')
        server=self.servers[key];month,gpus=self.units[key,billing];pk=key,client,bridge
        if pk not in self.prepared:self.prepared[pk]=Prepared(self.calls,server,client,self.context,bridge,self.measurements)
        prepared=self.prepared[pk];boxes=self.storage_boxes(server,team,gpus)
        while True:
            spill,host=self.retention(server,team,boxes,gpus);stat=prepared.stats(spill,'office_gigabit' if billing=='bought' else 'engine_wan')
            served=min(demand,stat['client_capacity_day']);overflow=demand-served
            full=self.fleet_stats(server,team,boxes,gpus)
            overflow_gpu=(full['fleet_s_call']*full['active_gpus']+spill*self.cold[key])
            work=served*stat['gpu_s_call']+overflow*overflow_gpu
            needed=max(1,math.ceil(team*work/(self.hours*3600*self.load*full['active_gpus'])*boxes))
            if needed>boxes and boxes*gpus>=team*self.concurrency and spill==0:
                raise InputGap('run20.fleet','finite team concurrency cannot serve hybrid demand in the active window')
            if needed<=boxes:break
            boxes=needed
        p='hardware.clients.'+client
        if basis not in ('owned','new'):raise InputGap('run20.client','owned or full new purchase basis required')
        device=0 if basis=='owned'else self.inputs.get(p+'.purchase_price')*(1-self.inputs.get('economics.client_residual'))/(12*self.inputs.get('owners.years'))
        energy=self.inputs.get(p+'.power')*self.hours*self.days*self.inputs.get('prices.energy_client')
        front=self.inputs.get('owners.front_month')
        storage=host/1e9*self.inputs.get('hosting.tiers.NVMe.price') if billing=='rented'else 0
        total=boxes*month/team+storage/team+device+energy+front
        return dict(person_month=total,boxes=boxes,unit_month=month,device_month=device,client_energy_month=energy,front_month=front,
            server_person_month=boxes*month/team,storage_person_month=storage/team,served_day=served,server_decode_overflow_day=overflow,
            spill_share=spill,offload_share=stat['offload_share'],client_capacity_day=stat['client_capacity_day'],
            prefill_gpu_s_day=served*stat['gpu_s_call'],decode_overflow_gpu_s_day=overflow*overflow_gpu,
            pending_s_offload=stat['pending_s_offload'])


def conditional_scope(common,original,monthly_calls):
    for key,value in (('common',common),('original',original)):r19.integer(value,key)
    s.r18.positive(monthly_calls,'monthly_calls')
    if common>original:raise InputGap('run20.workload','common calls exceed original workload')
    return ('conditional common measured subset {}/{} ({:.2f}%); normalized to {:g} calls/person-month; '.format(common,original,100*common/original,monthly_calls)+
        ('full workload unsupported' if common<original else 'full workload covered within declared envelope'))


def billing_calls(calls,indices,chunk):
    selected=set(indices);previous=0;out=[]
    for i,(d,n,o,tool) in enumerate(calls):
        if i%chunk==0:previous=0
        if i in selected:out.append((d,n+previous,o,tool))
        previous=o
    return out


def break_even(costs,reference):
    """Sustained strict improvement on a finite integer scan, not first lucky box step."""
    wins=[isinstance(a,(int,float)) and isinstance(b,(int,float)) and a<b for a,b in zip(costs,reference)]
    start=None
    for i in range(len(wins)-1,-1,-1):
        if not wins[i]:break
        start=i+1
    return dict(from_people=start if start is not None else s.alarm('no sustained crossing within scanned team sizes'),
        statement=('cheaper from '+str(start)+' people through '+str(len(wins))+' scanned people')if start is not None else'no sustained crossing through '+str(len(wins))+' people',
        any_counterexample=not all(wins),scan_max=len(wins))


def calculate(scenario,inputs):
    from .engine import load
    from .paper_tables import Context
    cfg=s.config();spec,_=load('paper-tables-r17');c=Context(spec,inputs)
    calls=c.g.resolve(c.valid).value
    idx=[i for i,(d,n,o,t)in enumerate(calls)if d+n+o<=249000 and 512<=n<=10000]
    common=[calls[i]for i in idx]
    if not common:raise InputGap('run20.workload','no common measured workload')
    c.valid=c.label('r20.common',common)
    # Preserve original normalization-group previous-output boundaries before
    # selecting indices; the98.1% allowance changes token billing, not the mix.
    chunk=inputs.get('workload.chunk_calls');billed=billing_calls(calls,idx,chunk)
    api_rows,api=s.api_baselines(billed,cfg);servers={key:s.Server(key,cfg)for key in cfg['servers']};econ=Economics(c,common,servers,cfg,api)
    decode=[];prefill=[];bridge=[]
    measurements=s.decode_measurements(cfg['server_decode'],servers)
    for key,server in servers.items():
        for depth in (16000,64000,164000,1000000):
            for streams in (1,8,32):
                try:dec=server.decode(depth,streams,measurements if depth<=164000 else None)
                except InputGap as exc:
                    if 'one complete session does not fit' not in str(exc):raise
                    dec=dict(batch=s.alarm(str(exc)),single_tok_s=s.alarm(str(exc)),aggregate_tok_s=s.alarm(str(exc)),gain=s.alarm(str(exc)),basis='capacity refusal; theoretical throughput not admitted')
                decode.append(dict(server=key,engine=server.engine,depth=depth,requested_streams=streams,**dec,
                    weights_bytes=server.weights,kv_bytes_token=server.kv,state_bytes=server.state,session_bytes=server.session_bytes(depth),
                    memory_bytes=server.info['memory_bytes'],workspace_bytes=server.info['workspace_bytes'],
                    context_basis='bandwidth/capacity extrapolation; not measured vLLM context admission'if depth==1000000 else'modelled decode; measured prefill envelope'))
        for depth in (16000,64000,164000,249000):
            for delta in (512,2343,10000):
                for variant in ('none','measured_envelope'):
                    seconds=server.cached(depth,delta,variant)
                    prefill.append(dict(server=key,engine=server.engine,depth=depth,delta=delta,bridge=variant,prefill_s=seconds,delta_tok_s=delta/seconds,
                        prefill_usd_million=seconds/delta*1e6*server.info['hourly_usd']/(3600*.7*(8 if server.info['host']=='b300'else 1)),
                        basis='measured elapsed TTFT interpolation; delta<2000 extension and shallow hold estimated; bridge envelope portability estimated'if server.engine=='vllm'else'R19/14 llama.cpp sensitivity'))
        if server.engine=='vllm':bridge.append(dict(server=key,**server.bridge,basis='full smoke server_prefill_ms per converted token; includes gather/conversion; max with vLLM TTFT; same-GPU/depth/delta portability assumption; heterogeneous checker5'))
    rows=[];summaries=[];breaks=[];claims=[];rental=[]
    small_keys=('pro6000_fp8','rtx5090')
    for profile in ('light','medium','heavy'):
        for share in cfg['shares']:
            demand=inputs.get('service.profiles.'+profile)*share
            for client in ('m5max64','m5max'):
                for basis in ('owned','new'):
                    for key in small_keys:
                        for billing in ('bought','rented'):
                            for team in cfg['teams']:
                                stat=econ.hybrid(key,team,demand,client,basis,billing,'measured_envelope')
                                best_key,best=best_own(econ,('pro6000_fp8','b300_fp8','b300_fp8_kv'),team,demand)
                                base=dict(profile=profile,share=share,client=client,basis=basis,server=key,billing=billing,team=team,bridge='measured_envelope',requested_day=demand,
                                    api_cheapest_person_month=api['main']['cheapest']*demand*econ.days,api_median_person_month=api['main']['median']*demand*econ.days,
                                    own_cluster_person_month=best['person_month'],own_cluster_server=best_key,own_cluster_boxes=best['boxes'],**stat)
                                base['median_over_hybrid']=ratio(base['api_median_person_month'],base['person_month']);base['cheapest_over_hybrid']=ratio(base['api_cheapest_person_month'],base['person_month'])
                                base['usd_per_1000_calls']=ratio(stat['person_month'],demand*econ.days/1000)
                                rows.append(base)
                            # Scan exact integer teams once per configuration; no persistence of900k rows.
                            hs=[];refs={k:[]for k in ('api_cheapest','api_median','own_cluster')}
                            for team in range(1,cfg['scan_team_max']+1):
                                hs.append(econ.hybrid(key,team,demand,client,basis,billing,'measured_envelope')['person_month'])
                                refs['api_cheapest'].append(api['main']['cheapest']*demand*econ.days);refs['api_median'].append(api['main']['median']*demand*econ.days)
                                refs['own_cluster'].append(best_own(econ,('pro6000_fp8','b300_fp8','b300_fp8_kv'),team,demand)[1]['person_month'])
                            for ref,vs in refs.items():breaks.append(dict(profile=profile,share=share,client=client,basis=basis,server=key,billing=billing,reference=ref,**break_even(hs,vs)))
    # Direct engine sensitivity on the same conditional workload at50people/s20.
    for key,server in servers.items():
        for bridge_variant in ('none','measured_envelope'):
            for share in cfg['shares']:
                demand=2500*share;team=50
                h=econ.hybrid(key,team,demand,'m5max64','owned','bought',bridge_variant)
                own=econ.own(key,team,demand)
                hot=econ.prepared[(key,'m5max64',bridge_variant)].stats(0,'engine_wan')
                gpu_hour=server.info['hourly_usd']/(8 if server.info['host']=='b300' else 1)
                served_hot=min(demand,hot['client_capacity_day'])
                hot_compute=hot['gpu_s_call']*served_hot*econ.days*gpu_hour/(3600*econ.load)
                hot_decode=max(0,demand-served_hot)*econ.own_stats(server,min(32,int(team*econ.sessions)))['seconds']*econ.days*gpu_hour/(3600*econ.load)
                hot_storage=4*server.session_bytes(cfg['reservation_depth'])/1e9*inputs.get('hosting.tiers.NVMe.price')
                client_base=inputs.get('hardware.clients.m5max64.power')*econ.hours*econ.days*inputs.get('prices.energy_client')+inputs.get('owners.front_month')
                work_month=hot_compute+hot_decode+hot_storage+hot['wire_bytes_call']*served_hot*econ.days/1e12*inputs.get('prices.egress')+client_base
                summaries.append(dict(server=key,engine=server.engine,bridge=bridge_variant,team=team,share=share,
                    resident_work_prefill_person_month=hot_compute,resident_work_decode_overflow_person_month=hot_decode,resident_work_hybrid_person_month=work_month,resident_work_median_multiple=api['main']['median']*demand*econ.days/work_month,resident_work_cheapest_multiple=api['main']['cheapest']*demand*econ.days/work_month,
                    hybrid_person_month=h['person_month'],own_cluster_person_month=own['person_month'],
                    hybrid_boxes=h['boxes'],own_cluster_boxes=own['boxes'],own_decode_s_call=own['decode_s_call'],
                    hybrid_prefill_person_month=h['prefill_gpu_s_day']*econ.days*server.info['hourly_usd']/(3600*econ.load*(8 if server.info['host']=='b300'else 1)),
                    api_cheapest_person_month=api['main']['cheapest']*demand*econ.days,api_median_person_month=api['main']['median']*demand*econ.days,
                    median_over_hybrid=ratio(api['main']['median']*demand*econ.days,h['person_month']),cheapest_over_hybrid=ratio(api['main']['cheapest']*demand*econ.days,h['person_month']),
                    basis='integer fleet; own minimal monotone search; hybrid sufficient R19 provision policy; resident_work is shared work-price lower bound; conditional workload'))
                if server.engine=='vllm':
                    rent=econ.hybrid(key,team,demand,'m5max64','owned','rented',bridge_variant)
                    rental.append(dict(server=key,bridge=bridge_variant,team=team,share=share,**rent,usd_per_1000_calls=ratio(rent['person_month'],demand*econ.days/1000),
                        price_basis=cfg['rental_basis']))
    # The finite scan makes universal prose falsifiable; full-mix claims remain unqualified.
    for profile,old in (('heavy','cheaper at every team size'),('light','cheaper from50'),('medium','cheaper from10')):
        selected=[r for r in breaks if r['profile']==profile and r['share']==1 and r['client']=='m5max64'and r['basis']=='owned'and r['billing']=='bought'and r['reference']=='own_cluster']
        claims.append(dict(profile=profile,previous_claim=old,scope='conditional common measured workload; closed perimeter; cheapest PRO6000/5090 hybrid versus cheapest PRO/B300 vLLM cluster; owned64GB client',
            statement='; '.join(r['server']+': '+r['statement']for r in selected),unconditional_claim='not established: full fitted mix exceeds common measured node envelope',
            counterexample_in_scan=any(r['any_counterexample']for r in selected)))
    result=dict(scenario=scenario['name'],tables=[],alarms=[],notes=[cfg['engine_basis'],cfg['rental_basis'],
        'All cost comparisons share R19 common measured indices and normalize to requested calls. Non-open commercial share is an equal omitted addend, not free service. New client basis amortizes full purchase, not premium. No universal full-mix claim is admitted.',
        'Bought office125MB/s1ms; rented existing engine WAN112.5MB/s400ms assumptions. Four retained/concurrent sessions/person; own cluster batch is min32/team*4/per-GPU capacity. Retention spills rebuild vLLM cold prefixes or use measured llama slot timings. Server GPU time plus occupancy; client overflow decodes fully on server. Host NVMe900GB/node assumption; bought included in chassis; rented billed separately. No inter-rental persistence.',
        'vLLM bridge main=max measured cached TTFT and smoke server-seconds/token envelope. This retains measured bridge work but extrapolates smoke geometry; none is a zero-extra-bridge lower bound. FP8→Q4 quality remains heterogeneous/uncalibrated. M5 128GB uses measured64GB SoC rate portability estimate.'],computed_metrics=0,export_namespace='r20')
    coverage=[dict(original_calls=len(calls),common_calls=len(common),common_fraction=len(common)/len(calls),max_end_depth=249000,delta_min=512,delta_max=10000,
        owner_cache_fraction=cfg['owner_cache_fraction'],source='data/measurements/run20-2026-11-03/owner-cache-notes-excerpt.txt',
        full_workload_cost=s.alarm('unconditioned mix exceeds measured server envelope; no silent coverage expansion'))]
    for name,data in (('api_admission',api_rows),('server_prefill',prefill),('vllm_bridge_evidence',bridge),('decode_scaling',decode),('small_team_cost',rows),('team_break_even',breaks),('engine_sensitivity',summaries),('rented_vllm_prefill',rental),('paper_claims',claims),('workload_coverage',coverage)):
        if name in ('small_team_cost','team_break_even','engine_sensitivity','rented_vllm_prefill'):
            for row in data:
                demand=inputs.get('service.profiles.'+row.get('profile','heavy'))*row['share']
                row['workload_scope']=conditional_scope(len(common),len(calls),demand*econ.days)
        r16.add_table(result,name,data)
    for table in result['tables']:
        for k in table['columns']:
            v=next((row[k]for row in table['rows']if not isinstance(row[k],dict)),None)
            table['columns'][k]=unit(k,v)
    r18_sources(inputs)
    return result


def r18_sources(inputs):
    from .measurements_r18 import record_sources
    from .measurements_r14 import record_packages
    record_sources(inputs);record_packages(inputs)
    for p in (s.CONFIG,s.SNAPSHOT,s.EVIDENCE,*[ROOT/r['path']for r in json.loads(s.EVIDENCE.read_text()).values()]):
        name=str(p.relative_to(ROOT));inputs.files[name]=dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def unit(k,v):
    if isinstance(v,str):return 'text'
    if isinstance(v,bool):return 'bool'
    if k.endswith('usd_per_1000_calls'):return 'USD/1000 conditional calls'
    if k.endswith('usd_million')or k=='prefill_usd_million':return 'USD/million tokens'
    if k=='unit_month':return 'USD/node-month'
    if k.endswith('_month')or k=='person_month':return 'USD/person-month (open-model component)'
    if k.endswith('_boxes')or k=='boxes':return 'box'
    if k.endswith('_bytes'):return 'B'
    if k=='kv_bytes_token':return 'B/token'
    if k.endswith('tok_s'):return 'token/s'
    if k in ('depth','delta','context_limit','max_end_depth','delta_min','delta_max','tokens')or k.endswith('_tokens'):return 'token'
    if k.endswith('_day')and's_gpu_'not in k and'gpu_s_'not in k:return 'call/person/day'
    if k.endswith('_s_call'):return 's/call'
    if k.endswith('_s_day'):return 'GPU s/person/day'
    if k.endswith('_s')or k=='pending_s_offload':return 's'
    if k=='seconds_token':return 's/token'
    if k in ('team','from_people','scan_max'):return 'person'
    return '1'
