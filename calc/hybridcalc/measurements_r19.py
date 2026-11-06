"""Measured Qwen prefill nodes, bounded residency and matched backend costs."""
import hashlib
import json
import math
from pathlib import Path

from .inputs import InputGap,ROOT
from . import measurements_r16 as r16,measurements_r17 as r17,measurements_r18 as r18
from .session_hosting import route

CONFIG=Path(__file__).parent/'data/run19-measurements.json'
KV=34816
STATE=156893184


def config():return json.loads(CONFIG.read_text())


def checked_price(cfg):
    info=cfg['price_evidence'];content=(ROOT/info['path']).read_bytes()
    if hashlib.sha256(content).hexdigest()!=info['sha256']:
        raise InputGap('run19.price','price evidence byte identity mismatch')
    record=json.loads(content);source=record['sources'][0]
    if (source['price_usd']!=cfg['office']['card_usd'] or source['availability']!='Sold Out' or
        cfg['office']['price_basis']!='sold_out_list_price_plus_estimated_host' or cfg['office']['host_usd']<=0):
        raise InputGap('run19.price','sold-out card listing and positive separate host allowance required')
    if cfg['rental']['price_basis']!='observed Vast offers; not market rates':
        raise InputGap('run19.price','observed rental offers cannot be relabelled as market rates')
    for price in cfg['rental']['observed_hourly_usd']:r18.positive(price,'observed_hourly_usd')
    return record


def integer(value,name,zero=False):
    r18.positive(value,name,zero)
    if int(value)!=value:raise InputGap('run19.'+name,'integer count required')
    return int(value)


def rental_basis(old):
    return old+'; conditional common measured subset10885/39904 (27.28%); normalized to52500 calls/person-month; full workload unsupported'


class Node:
    """One GPU replica: physical KV budget, configured context, measured rates."""
    def __init__(self,key,cfg=None):
        self.cfg=cfg or config();self.key=key
        if key not in ('rtx5090','pro6000'):raise InputGap('run19.node','unknown node')
        self.info=self.cfg['nodes'][key];self.free=self.info['session_budget_bytes']
        expected=13e9 if key=='rtx5090' else 96e9-18.97e9-8e9
        if self.free!=expected:raise InputGap('run19.capacity','qualified session budget cannot be enlarged')
        expected_basis={'rtx5090':'client_kit_same_llama_cpp_hybrid_binary_assumption',
            'pro6000':'kit1.6.5 PRO6000 same-weight prefill measured; hybrid-binary portability'}
        if self.info['rate_basis']!=expected_basis[key]:
            raise InputGap('run19.rates','qualified hybrid-binary portability assumption required')
        self.surface=r18.Client('rtx5090_qwen27') if key=='rtx5090' else r17.Surface('qwen27','server')
        self.records=self.surface.records;self.depths=list(r16.DEPTHS)
        self.context_limit=262144;self.rate_limit=249000
        self.slot_points={}
        for kind,count in (('slot_save','n_saved'),('slot_restore','n_restored')):
            rs=[r for r in self.records if r['kind']==kind]
            if len(rs)!=6 or {r.get('depth') for r in rs}!=set(self.depths):
                raise InputGap('run19.swap','complete measured save/restore ladder required')
            for r in rs:
                if r.get(count)!=r['depth'] or r.get('error'):
                    raise InputGap('run19.swap','exact successful slot token counts required')
                r18.positive(r.get('ms'),'slot_ms');r18.positive(r.get('bytes'),'slot_bytes')
            self.slot_points[kind]=sorted((r['depth'],r['ms']/1000) for r in rs)
        for d in self.depths:
            pair=[r for r in self.records if r.get('depth')==d and r['kind'] in self.slot_points]
            if pair[0]['bytes']!=pair[1]['bytes']:
                raise InputGap('run19.swap','save/restore byte counts disagree')

    @property
    def physical_token_limit(self):return math.floor((self.free-STATE)/KV)

    def session_bytes(self,depth,delta=0,output=0):
        for k,v in (('depth',depth),('delta',delta),('output',output)):r16.nonnegative(v,k)
        return (depth+delta+output)*KV+STATE

    def admit(self,depth,delta=0,output=0):
        size=self.session_bytes(depth,delta,output)
        if depth+delta+output>self.context_limit or size>self.free:
            raise InputGap('run19.capacity','one session exceeds configured context or per-GPU residency budget')
        return size

    def resident_slots(self,depth,delta=0,output=0):return math.floor(self.free/self.admit(depth,delta,output))

    def placement(self,count,depth,tier):
        count=integer(count,'sessions',True);slots=self.resident_slots(depth)
        if tier not in ('resident','RAM','NVMe'):raise InputGap('run19.swap','unknown residency tier')
        spill=max(0,count-slots)
        if spill and tier=='resident':raise InputGap('run19.swap','sessions beyond resident set must swap or refuse')
        return dict(resident=min(count,slots),swapped=spill)

    def rate(self,depth,delta):
        self.admit(depth,delta)
        if depth>self.rate_limit:raise InputGap('run19.rates','unmeasured node depth')
        # Same shallow endpoint assumption as R18; delta must stay in the kit grid.
        if not 512<=delta<=10000:raise InputGap('run19.rates','unmeasured node delta')
        return self.surface.for_delta(max(16000,depth),delta)

    def swap_seconds(self,depth,tier):
        self.admit(depth)
        if tier=='resident':return 0.0
        if tier not in ('RAM','NVMe'):raise InputGap('run19.swap','unknown residency tier')
        if depth>self.rate_limit:raise InputGap('run19.swap','restore depth beyond measured ladder')
        rate=min(self.cfg['tiers'][tier]['bandwidth_bytes_s'],self.cfg['pcie_bytes_s'])
        r18.positive(rate,'tier_bandwidth')
        # Full-slot server swap is a different endpoint from client delta import.
        # max keeps a tier-bandwidth floor without adding file IO twice.
        size=self.session_bytes(depth)
        return sum(max(r18.interpolate(self.slot_points[k],depth),size/rate) for k in self.slot_points)


def links(inputs):
    wifi=r16.source_json('PREFLIGHT-ROUTE-PLAN.json.gz')
    wan=r16.source_json('TIMING-EXTRACT.json.gz')['measured_link']
    return [dict(key='office_gigabit',bytes_s=125e6,rtt_s=.001,rental=False,basis='ideal application goodput; 1ms RTT assumption'),
            dict(key='office_10gbe',bytes_s=1250e6,rtt_s=.001,rental=False,basis='ideal application goodput; 1ms RTT assumption'),
            dict(key='measured_wifi_wan',bytes_s=wifi['actual_measured_downstream_bytes_s'],rtt_s=wifi['actual_measured_warm_rtt_s'],rental=True,basis='measured Wi-Fi plus WAN/SSH path; replay, not office-LAN measurement'),
            dict(key='measured_5g_wan',bytes_s=wan['downstream_bytes_per_second'],rtt_s=wan['warm_rtt_seconds'],rental=True,basis='measured 5G WAN/SSH path replay'),
            dict(key='engine_wan',bytes_s=inputs.get('hardware.links.wan.bandwidth')*inputs.get('hardware.links.wan.goodput')/8,rtt_s=inputs.get('hardware.links.wan.latency'),rental=True,basis='existing engine WAN bandwidth/goodput/RTT estimate')]


def local_rate(client,depth,delta,context):
    if client=='m3max':return context.r16_single.for_delta(max(16000,depth),delta)
    if client=='m5max64':return context.measured_m5.prefill(depth)
    raise InputGap('run19.client','unqualified client')


def thresholds(context,nodes,profiles):
    out=[];imp=r16.ClientImport()
    for client in ('m3max','m5max64'):
        for node in nodes:
            for tier in ('resident','RAM','NVMe'):
                for link in profiles:
                    for d in r17.DEPTHS:
                        for n in r17.DELTAS:
                            own=n/local_rate(client,d,n,context);server=n/node.rate(d,n);swap=node.swap_seconds(d,tier)
                            imported=imp.at_depth(n,d);size=KV*n+STATE
                            budget=own-server-swap-imported-link['rtt_s']
                            value=size/budget/1e6 if budget>0 else {'alarm':[dict(input='downstream',reason='no finite winning downstream rate')]}
                            out.append(dict(client=client,node=node.key,tier=tier,link=link['key'],depth=d,delta=n,
                                local_prefill_s=own,node_prefill_s=server,swap_s=swap,client_import_s=imported,
                                rtt_s=link['rtt_s'],wire_bytes=size,budget_s=budget,break_even_downstream_mb_s=value,
                                break_even_downstream_mbit_s=value*8 if budget>0 else value,
                                threshold_status='finite' if budget>0 else 'never_nonpositive_budget',
                                link_mb_s=link['bytes_s']/1e6,offload_at_link=budget>0 and link['bytes_s']>size/budget,
                                basis='isolated turn; current server prefix; no pending catchup; Mac R16 prototype import; M5 portability estimate'))
    return out


class Prepared:
    """Invariant call vectors; box counts change only the expected swap share."""
    def __init__(self,calls,client,node,context):
        self.calls=calls;self.client=client;self.node=node
        self.own=[];self.prefill=[];self.shadow=[];self.output=[];self.wire=[];self.imports=[]
        self.swap={tier:[] for tier in ('resident','RAM','NVMe')}
        for d,n,o,t in calls:
            node.admit(d,n,o);rate=node.rate(d,n)
            self.own.append(n/local_rate(client,d,n,context));self.prefill.append(n/rate)
            self.shadow.append((n+o)/rate);self.output.append(o/rate)
            self.wire.append(n*KV+STATE);self.imports.append(r16.ClientImport().at_depth(n,d))
            for tier in self.swap:
                # Save at the final server prefix; output shadow is deferred by route.
                self.swap[tier].append(node.swap_seconds(d+n+o,tier))

    def routed(self,link,tier,spill_share):
        r16.nonnegative(spill_share,'spill_share')
        if spill_share>1 or (tier=='resident' and spill_share!=0):raise InputGap('run19.swap','invalid spill probability')
        remote=[s+spill_share*sw+b/link['bytes_s']+link['rtt_s']+i
                for s,sw,b,i in zip(self.prefill,self.swap[tier],self.wire,self.imports)]
        steps=route(self.own,remote,self.shadow,self.output,self.wire,self.imports,'at_offload')
        count=sum(r[3] for r in steps);N=len(steps)
        gpu=sum((pre+steps.pending_seconds+spill_share*sw) for pre,sw,r in zip(self.prefill,self.swap[tier],steps) if r[3])/N
        return dict(offload_share=count/N,offload_calls=count,calls=N,gpu_s_call=gpu,
                    migration_s_call=sum(spill_share*sw for sw,r in zip(self.swap[tier],steps) if r[3])/N,
                    wire_bytes_call=sum(r[2] for r in steps)/N,pending_s_offload=steps.pending_seconds,
                    prefill_wait_s_call=sum(r[0] for r in steps)/N,local_prefill_s_call=sum(self.own)/N)


def fleet(prepared,link,tier,team,calls_day,hours,load,sessions_per_person,cfg):
    for k,v in (('team',team),('sessions_per_person',sessions_per_person)):integer(v,k)
    for k,v in (('calls_day',calls_day),('hours',hours),('load',load)):r18.positive(v,k)
    if load>1:raise InputGap('run19.fleet','target load must not exceed one')
    node=prepared.node;reserved=cfg['reservation_depth'];slot=node.admit(reserved);slots=node.resident_slots(reserved)
    sessions=team*sessions_per_person
    if tier not in ('resident','RAM','NVMe'):raise InputGap('run19.swap','unknown residency tier')
    boxes=math.ceil(sessions/slots) if tier=='resident' else max(1,math.ceil(sessions/(slots+math.floor(cfg['tiers'][tier]['capacity_bytes']/slot))))
    # Monotone upper sizing: stop only when the routed demand actually fits.
    # More slots may admit additional offloads, so recompute after every increase.
    while True:
        spill=0 if tier=='resident' else max(0,1-boxes*slots/sessions)
        stats=prepared.routed(link,tier,spill)
        if not stats['offload_calls']:
            return dict(stats,boxes=0,resident_only_boxes=math.ceil(sessions/slots),resident_slots_box=slots,
                        retained_sessions=sessions,spill_share=0,host_bytes=0,compute_boxes=0)
        needed=max(1,math.ceil(team*calls_day*stats['gpu_s_call']/(hours*3600*load)))
        if needed<=boxes:break
        boxes=needed
    host_sessions=max(0,sessions-boxes*slots)
    if tier!='resident' and host_sessions*slot>boxes*cfg['tiers'][tier]['capacity_bytes']:
        raise InputGap('run19.fleet','host cache capacity exceeded')
    return dict(stats,boxes=boxes,resident_only_boxes=math.ceil(sessions/slots),resident_slots_box=slots,
                retained_sessions=sessions,spill_share=spill,host_bytes=host_sessions*slot,compute_boxes=needed)


def unit_month(node,inputs,cfg):
    if node.key=='rtx5090':
        checked_price(cfg);capex=cfg['office']['card_usd']+cfg['office']['host_usd'];power=cfg['office']['box_kw']
    else:capex=inputs.get('owners.options.office6000.capex');power=inputs.get('owners.options.office6000.power')
    month=capex*(1-inputs.get('owners.residual'))/(12*inputs.get('owners.years'))
    month+=power*inputs.get('economics.pue')*inputs.get('economics.hours_month')*inputs.get('owners.office_load')*inputs.get('prices.energy_client')
    month+=capex*inputs.get('owners.office_support')/12
    return capex,month


def calculate(scenario,inputs):
    from .engine import load
    from .paper_tables import Context,api_vector
    spec,_=load('paper-tables-r17');context=Context(spec,inputs);cfg=config();checked_price(cfg)
    original=context.g.resolve(context.valid)
    if original.alarms:raise InputGap('run19.workload',str(original.alarms))
    calls=original.value
    if not calls:raise InputGap('run19.workload','positive fitted call set required')
    nodes=[Node(k,cfg) for k in ('rtx5090','pro6000')];profiles=links(inputs)
    indices=[i for i,(d,n,o,t) in enumerate(calls) if d+n+o<=249000 and 512<=n<=10000]
    if not indices:raise InputGap('run19.workload','no common measured calls')
    common=[calls[i] for i in indices]
    context.valid=context.label('r19.common_workload',common)
    month_calls=inputs.get('owners.calls_day')*inputs.get('owners.days')
    api={}
    for key in ('qwen_cheap','qwen_median'):
        tariff={k:inputs.get('prices.apis.'+key+'.'+k) for k in ('cache_read','cache_write','output')}
        vector=api_vector(calls,tariff,inputs.get('workload.chunk_calls'))
        api[key]=sum(vector[i] for i in indices)/len(indices)
    references=[];model=context.model('qwen27')
    for option in ('office6000','b300_node'):
        server=context.server(option,model)
        seconds=context.g.resolve(context.own_seconds('r19.ref.'+option,context.valid,model,server))
        month=context.g.resolve(context.unit_month('r19.ref.month.'+option,server,'owners.residual'))
        if seconds.alarms or month.alarms:raise InputGap('run19.reference',str(seconds.alarms+month.alarms))
        for team in (5,50,500):
            boxes=max(1,math.ceil(team*inputs.get('owners.calls_day')*seconds.value/(inputs.get('paper_tables.hours')*3600*inputs.get('owners.load'))))
            references.append(dict(option=option,team=team,boxes=boxes,usd_person_month=boxes*month.value/team,
                                   usd_per_1000_calls=boxes*month.value/team/month_calls*1000,
                                   basis='existing fully-local own_seconds incl output decode/residence; same conditional calls; no client purchase'))
    office=[];rental=[];routing=[]
    for client in ('m3max','m5max64'):
        for node in nodes:
            prepared=Prepared(common,client,node,context);capex,unit=unit_month(node,inputs,cfg)
            for link in profiles:
                for tier in ('resident','RAM','NVMe'):
                    stats=prepared.routed(link,tier,0 if tier=='resident' else 1)
                    routing.append(dict(client=client,node=node.key,link=link['key'],tier=tier,**stats,
                        basis='conditional common mix; resident or fully swapped diagnostic; expected at_offload catchup; no trace claim'))
                    for team in (5,50,500):
                        f=fleet(prepared,link,tier,team,inputs.get('owners.calls_day'),inputs.get('paper_tables.hours'),inputs.get('owners.load'),inputs.get('hosting.sessions_per_person'),cfg)
                        storage=0.0 # Owned RAM/NVMe is already included in the separate host capex.
                        cost=(f['boxes']*unit+storage)/team
                        office.append(dict(client=client,node=node.key,link=link['key'],tier=tier,team=team,**f,
                            box_capex_usd=capex,box_month_usd=unit,host_storage_month_usd=storage,
                            usd_person_month=cost,usd_per_1000_calls=cost/month_calls*1000,
                            api_cheapest_usd_person_month=api['qwen_cheap']*month_calls,
                            api_median_usd_person_month=api['qwen_median']*month_calls,
                            own_pro6000_usd_person_month=next(r['usd_person_month'] for r in references if r['team']==team and r['option']=='office6000'),
                            own_b300_usd_person_month=next(r['usd_person_month'] for r in references if r['team']==team and r['option']=='b300_node'),
                            basis='same conditional mix; Mac already owned; backend cost only; owned cache included in host capex; monotone sufficient box count, not proved minimal; uniform session popularity'))
                    if node.key=='rtx5090' and link['rental'] and tier!='resident':
                        # One-person priced service allocation; whole warm box idle cost
                        # is shown beside a utilization-priced GPU-work lower bound.
                        f=fleet(prepared,link,tier,1,inputs.get('owners.calls_day'),inputs.get('paper_tables.hours'),inputs.get('owners.load'),inputs.get('hosting.sessions_per_person'),cfg)
                        storage=f['host_bytes']/1e9*inputs.get('hosting.tiers.'+tier+'.price')
                        egress=f['wire_bytes_call']*month_calls/1e12*inputs.get('prices.egress')
                        for hourly in cfg['rental']['observed_hourly_usd']:
                            for billing in ('gpu_work_lower_bound','warm_calendar_node'):
                                hours=month_calls*f['gpu_s_call']/3600/inputs.get('owners.load') if billing=='gpu_work_lower_bound' else f['boxes']*inputs.get('economics.hours_month')
                                total=hours*hourly+storage+egress
                                rental.append(dict(client=client,node=node.key,link=link['key'],tier=tier,hourly_usd=hourly,billing=billing,**f,
                                    billed_hours_month=hours,storage_usd_month=storage,egress_usd_month=egress,
                                    usd_person_month=total,usd_per_1000_calls=total/month_calls*1000,
                                    api_cheapest_usd_person_month=api['qwen_cheap']*month_calls,
                                    api_median_usd_person_month=api['qwen_median']*month_calls,
                                    basis=rental_basis('observed Vast offers2026-11-03, not market rates; warm inference excludes first model fetch/startup; no persistence across lease ends; work price is a lower bound, calendar node pays idle')))
    coverage=[dict(original_calls=len(calls),common_calls=len(common),common_share=len(common)/len(calls),
        max_end_depth=249000,delta_min=512,delta_max=10000,normalized_calls_person_month=month_calls,
        full_workload_supported=len(common)==len(calls),
        full_workload_office_cost=('see office_node_economics; complete fitted mix' if len(common)==len(calls) else
            {'alarm':[dict(input='run19.workload',reason='unconditioned mix exceeds measured depth/delta and configured session limits')]}),
        basis='all alternatives use the same indices; original API cache-group prices selected without resetting boundaries; conditional mix normalized to a whole person-month, not full-workload claim')]
    capacity=[];slot_times=[]
    for node in nodes:
        for depth in (32000,64000,100000,200000,249000):
            capacity.append(dict(node=node.key,depth=depth,session_bytes=node.session_bytes(depth),resident_slots=node.resident_slots(depth),
                session_budget_bytes=node.free,physical_one_session_tokens=node.physical_token_limit,
                configured_context_limit=node.context_limit,measured_rate_depth_limit=node.rate_limit,
                basis=node.info['rate_basis']))
        for row in node.records:
            if row['kind'] in ('slot_save','slot_restore'):
                slot_times.append(dict(node=node.key,kind=row['kind'],depth=row['depth'],seconds=row['ms']/1000,bytes=row['bytes'],
                    basis='measured full-slot file backend; hybrid node portability/storage-tier assumption; not a client delta import'))
    result=dict(scenario=scenario['name'],tables=[],alarms=[],notes=[],computed_metrics=0,export_namespace='r19')
    for key,data in (('node_capacity',capacity),('node_swap_evidence',slot_times),('node_link_profiles',profiles),
                     ('node_link_threshold',thresholds(context,nodes,profiles)),('node_routing',routing),
                     ('office_node_economics',office),('rented_prefill_node',rental),('same_mix_own_references',references),('workload_coverage',coverage)):
        r16.add_table(result,key,data)
    for table in result['tables']:
        for key in table['columns']:
            if key.endswith('usd_per_1000_calls') or key=='usd_per_1000_calls':table['columns'][key]='USD/1000 conditional calls'
            elif key.endswith('usd_person_month'):table['columns'][key]='USD/person-month'
            elif 'usd' in key:table['columns'][key]='USD/hour' if key=='hourly_usd' else 'USD'
            elif key.endswith('_bytes') or key=='bytes':table['columns'][key]='B'
            elif key.endswith('_bytes_call'):table['columns'][key]='B/call'
            elif key.endswith('_s_call'):table['columns'][key]='s/call'
            elif key.endswith('_mb_s'):table['columns'][key]='MB/s (decimal)'
            elif key.endswith('_mbit_s'):table['columns'][key]='Mbit/s'
            elif key=='bytes_s':table['columns'][key]='B/s'
            elif key.endswith('_s') or key=='seconds' or key=='pending_s_offload':table['columns'][key]='s'
            elif key=='billed_hours_month':table['columns'][key]='GPU-machine hours/month'
            elif key in ('depth','delta','configured_context_limit','measured_rate_depth_limit','max_end_depth','delta_min','delta_max') or key.endswith('_tokens'):table['columns'][key]='token'
            elif key=='normalized_calls_person_month':table['columns'][key]='call/person-month'
            elif key.endswith('boxes') or key=='boxes':table['columns'][key]='box'
    result['notes'].append('Run19 conditional Qwen measured envelope. 5090 client-kit prefill reused for hybrid binary as an assumption. Configured262144 and measured249k bounds differ from about369k physical KV capacity. Resident overflow swaps or refuses; native server file save+restore costs and tier floors never replace/add to Mac delta-import calibration. Monotone fleet sizing rechecks route demand after residency changes. Four retained sessions/person and249k reservation; uniform popularity estimate. Card sold-out list price1999.99 plus1500 host estimate, not available box quote. Existing same-mix API prices preserve original cache groups; PRO6000/B300 fully-local reference costs remain separate. Rental work-pricing is an optimistic utilization allocation; persistent warm-calendar box includes idle but excludes initial model fetch/startup and assumes retention only during lease. No new runtime or quality qualification. R16b/SWA data interfaces retained; historical exports immutable.')
    r18.record_sources(inputs)
    for path in (CONFIG,ROOT/cfg['price_evidence']['path']):
        inputs.files[str(path.relative_to(ROOT))]=dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result
