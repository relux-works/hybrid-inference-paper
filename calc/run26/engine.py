"""Small summaries, finite team crossings, shared internal-large-model component."""
import copy
import csv
import json
import math
from pathlib import Path

from hybridcalc import deep_r21 as deep, server_economics_r20 as s
from run23 import engine as r23, economics as e23
from run25 import model as fleet25, engine as r25
from . import model as m

ROOT=Path(__file__).resolve().parents[2]
SAMPLES=(1,3,5,10,20,50,100,500)


def source_profiles(c):
    stats=deep.checked_stats();original=c.g.resolve(c.valid).value
    for name,calls in [('existing_combined',original),('claude_deep',deep.reconstruct(stats['agents']['claude'],1000,300))]:
        selected=[x for x in calls if 16000<=x[0] and sum(x[:3])<=249000 and 512<=x[1]<=10000]
        yield dict(profile=name,selected_shapes=len(selected),source_shapes=len(calls),shape_fraction=len(selected)/len(calls),
                   coverage='share of fitted/reconstructed CALL SHAPES inside Qwen measured ladder; normalized per person-month; not token/work share; full log mix unsupported'),selected


def common(profile,model,server,client,basis,billing,load,share,slowdown=1):
    return dict(profile,model=model,server=server,client=client,client_basis=basis,billing=billing,
        link='bought office125MB/s RTT1ms' if billing=='bought' else 'rented engine WAN112.5MB/s RTT400ms estimated; approved internal trust boundary assumed',
        load=load,share=share,glm_prefill_slowdown=slowdown if model=='glm' else '',
        rate_basis=('Qwen M5 Max64 recorded PRI31;128GB same-SoC portability; measured prefill/decode anchors/interpolation; tails estimates; PRO decode measured, B300 decode modelled'
                    if model=='qwen' else 'UNMEASURED GLM; Ultra256/512 extrapolated from measured M5 Max Qwen,2x compute/2x inferred bandwidth; two-B300 replica; ideal bandwidth sum/uniform expert union, no communication; prefill FLOP portability x'+str(slowdown)),
        cache_basis='not applicable: both alternatives internal; no cloud API price component',
        intensity='owner2500 calls/day, heavy; typical loads are light/medium' if load=='heavy' else 'typical '+load,
        contour='all calls middle model in-house' if share==1 else 'middle share in-house; remaining tasks internal large model, same common cost in both alternatives')


def normalize(result):
    row=dict(result)
    for k,v in row.items():
        if isinstance(v,dict) or isinstance(v,float) and not math.isfinite(v):row[k]=None
    return row


def row_for(q,team,demand,h,own,capital=0):
    h=m.prefill_only(normalize(h));own=normalize(own)
    if m.finite(h.get('person_month')):h['person_month']+=capital
    row=dict(q,team=team,requested_middle_calls_day=demand,middle_calls_person_month=demand*21,
             hybrid_person_month=h.get('person_month'),own_person_month=own.get('person_month'),
             hybrid_status=h['status'],own_status='feasible' if m.finite(own.get('person_month')) else 'capacity_shortfall',
             hybrid_nodes=h.get('boxes'),own_nodes=own.get('boxes'),client_capital_month=capital,
             client_capacity_day=h.get('client_capacity_day'),offload_share=h.get('offload_share'),
             hybrid_service_utilization=h.get('service_utilization'),hybrid_calendar_utilization=h.get('calendar_utilization'),
             own_service_utilization=own.get('service_utilization'),own_calendar_utilization=own.get('calendar_utilization'),
             own_over_hybrid=(own['person_month']/h['person_month'] if m.finite(own.get('person_month')) and m.finite(h.get('person_month')) else None),
             server_decode_overflow_day=h.get('server_decode_overflow_day'),
             pricing_basis='PRIMARY dedicated calendar-billed node; sufficient inherited retained-copy policy; own server-only, hybrid adds client energy/front and new-client capital; prefill-only hybrid, no dropped generation')
    return row


def sweep(c,meta,calls,econ,key,clients,tables,projection=False):
    cfg=m.config()
    for billing in ('bought','rented'):
        for load in ('light','medium','heavy'):
            for share in cfg['shares']:
                demand=c.inputs.get('service.profiles.'+load)*share
                own=[]
                for team in range(1,501):
                    result=normalize(econ.own(key,team,demand,billing))
                    if projection:
                        month,replicas=econ.units[key,billing]
                        if m.finite(result.get('boxes')):
                            service=team*demand*result['gpu_s_call']/(result['boxes']*replicas*econ.hours*3600)
                            result.update(service_utilization=service,calendar_utilization=service*econ.hours*econ.days/730)
                    else:result.update(econ.utilization(key,team,demand,result,'own'))
                    own.append(result)
                for client in clients:
                    price=cfg['studio_price_proxy_usd'][client] if projection else c.inputs.get('hardware.clients.'+client+'.purchase_price')
                    both={basis:[] for basis in ('owned','new')};samples={basis:[] for basis in both}
                    for team in range(1,501):
                        if projection:
                            h=econ.hybrid(team,demand,client,'owned',billing)
                        else:
                            h=econ.hybrid(key,team,demand,client,'owned',billing,'measured_envelope')
                            h=dict(h,**econ.utilization(key,team,demand,h,'hybrid'))
                        for basis in both:
                            q=common(meta,'glm' if projection else 'qwen',key,client,basis,billing,load,share,
                                     econ.servers[key].slowdown if projection else 1)
                            row=row_for(q,team,demand,h,own[team-1],m.capital(price,c.inputs,basis))
                            both[basis].append(row['hybrid_person_month'])
                            if team in SAMPLES:
                                tables['middle_cost'].append(row);samples[basis].append(row)
                                if share<1:
                                    large=m.cloud_capacity(team,c.inputs,billing,1-share)
                                    tables['mixed_scheme'].append(dict(row,**m.mixed(row['hybrid_person_month'],row['own_person_month'],large['person_month']),
                                        large_capacity_floor_nodes=large['nodes'],middle_ratio_basis='middle segment only; not total internal cost ratio',large_cost_basis='COMMON 2.4T FP8 weight-capacity cost FLOOR, not full service price; unknown throughput/extra storage/communication cost identical in both alternatives; owned client energy charged full8h; s is task-success INPUT, not measured quality'))
                    for basis,costs in both.items():
                        q=common(meta,'glm' if projection else 'qwen',key,client,basis,billing,load,share,
                                 econ.servers[key].slowdown if projection else 1)
                        tables['crossings'].append(dict(q,**r25.compare(costs,[r.get('person_month') for r in own]),
                            comparison='middle hybrid vs same-model same-server same-billing own cluster; common internal-large part cancels for s<1',
                            team50_hybrid=costs[49],team50_own=own[49].get('person_month'),
                            team50_status=next(r['hybrid_status']for r in samples[basis]if r['team']==50)))
                    print('sweep',meta['profile'],key,billing,load,share,client,flush=True)


def fleet_variants(c,meta,calls,econ,tables):
    """Run25 IO/queue proxies for PRO, team50; purchased capital is additive."""
    cfg=fleet25.config();weights=[1/len(calls)]*len(calls)
    for client in ('m5max64','m5max'):
        # Compatibility view: R25's prepared lookup name is fixed to64GB. The
        # selected128GB memory/decoder vectors themselves are preserved here.
        view=copy.copy(econ);view.prepared=dict(econ.prepared)
        view.prepared['pro6000_fp8','m5max64','measured_envelope']=econ.prepared['pro6000_fp8',client,'measured_envelope']
        for case in cfg['storage_cases']:
            for speed in cfg['speed_factors']:
                fleet=fleet25.Fleet(view,weights,case,speed,'bought',cfg)
                upper=fleet.econ.hours*3600/max(sum(w*x for w,x in zip(weights,fleet.p.decode_device)),
                                              sum(w*x for w,x in zip(weights,fleet.p.decode_occupied)))
                for load in ('light','medium','heavy'):
                    for share in m.config()['shares']:
                        demand=c.inputs.get('service.profiles.'+load)*share
                        def at(n):
                            r=m.prefill_only(fleet.evaluate(50,demand,n));r['boxes']=n
                            return r
                        fixed={str(n):at(n) for n in (1,2,4)}
                        if demand>upper:
                            minimum=dict(person_month=None,nodes=None,boxes=None,feasible=False,status='client_decode_capacity_shortfall',client_capacity_day=upper)
                        else:
                            low=fleet25.storage(fleet.server,fleet.depth,50,1,case,4)['storage_min_nodes']
                            minimum=dict(person_month=None,boxes=None,status='no_prefill_only_certificate_through4T')
                            for n in range(low,max(low,200)+1):
                                r=at(n)
                                if r['feasible']:minimum=r;break
                        fixed['minimum']=minimum
                        own=normalize(econ.own('pro6000_fp8',50,demand,'bought'))
                        own.update(econ.utilization('pro6000_fp8',50,demand,own,'own'))
                        for policy,h in fixed.items():
                            for basis in ('owned','new'):
                                q=common(meta,'qwen','pro6000_fp8',client,basis,'bought',load,share)
                                row=row_for(q,50,demand,h,own,m.capital(c.inputs.get('hardware.clients.'+client+'.purchase_price'),c.inputs,basis))
                                row.update(fleet_policy=policy,storage_case=case['name'],restore_slowdown=speed,
                                    proxy_basis=case['basis']+'; '+cfg['arrival_basis']+'; '+cfg['queue_basis'],
                                    mean_client_ttft_s=h.get('mean_ttft_s'),actual_mean_queue_s=h.get('actual_mean_queue_s'),
                                    charged_mean_queue_s=h.get('charged_mean_queue_s'),read_s_offload=h.get('read_s_offload'),
                                    write_s_offload=h.get('write_s_offload'),storage_shortfall_copies=h.get('storage_shortfall_copies'),
                                    copies_per_node=h.get('copies_per_node'),copy_bytes=h.get('copy_bytes'),
                                    comparison_basis='R25 fixed1/2/4/first-certified sensitivity at team50 ONLY; prefill-only admission added; own reference inherited sufficient retention, not paired storage optimization; GLM two-GPU replicas out of this PRO-only queue contract')
                                tables['fleet_variants'].append(row)
        print('fleet variants',meta['profile'],client,flush=True)


def moe_rows():
    sv=m.GlmServer(e23.Server('b300_fp8'));a=sv.a;u=m.Ultra()
    rows=[]
    for depth in (16000,64000,164000,256000,512000,1000000):
        for requested in (1,8,32,128,1000000):
            g=sv.decode(depth,requested);q=e23.Server('b300_fp8').decode(depth,requested if requested<=32 else min(requested,sv.slots(depth)))
            k=g['batch'];shared,routed=m.expert_partition(a['total'],a['active'],a['experts'],a['topk'])
            union=a['experts']*(1-(1-a['topk']/a['experts'])**k)
            rows.append(dict(depth=depth,requested_streams=requested,glm_resident_limit=sv.slots(depth),glm_batch=k,
                glm_gain=g['gain'],qwen_batch=q['batch'],qwen_gain=q['gain'],glm_vs_qwen_gain=g['gain']/q['gain'],
                glm_aggregate_tok_s=g['aggregate_tok_s'],glm_active_parameters=a['active'],glm_total_parameters=a['total'],
                experts=a['experts'],topk=a['topk'],expected_unique_experts=union,
                expert_read_amortization=k*a['topk']/union,glm_server_kv_bytes_token=a['server_kv'],glm_client_kv_bytes_token=a['client_kv'],
                glm_wire_state_bytes=a['wire_state'],glm_client_projected_single_tok_s=u.decode(depth,1),
                ultra_basis='EXTRAPOLATED M5 Ultra256 from measured M5 Max single Qwen,2x inferred bandwidth, unmeasured GLM kernels',
                basis='MODELLED architecture; equal independent expert routing and full MLA KV read (sparse-index/cache optimizations unmodelled); two B300 GLM vs one B300 dense replica; no GLM/B300 decode measurement, no communication'))
    return rows


def calculate(resume=None,checkpoint=None):
    c=r23.context();cfg=s.config();cfg['servers']={k:cfg['servers'][k]for k in ('pro6000_fp8','b300_fp8')}
    cfg['reservation_depth']=249000;empty={k:[] for k in ('middle_cost','mixed_scheme','crossings','fleet_variants','cloud_reference','cloud_affordability','moe_decode','class_map','pending_inputs')}
    tables=resume['tables'] if resume else empty
    done=set(resume['done']) if resume else set()
    def save(stage):
        done.add(stage)
        if checkpoint:checkpoint(dict(tables=tables,done=sorted(done)))
    for meta,calls in source_profiles(c):
        servers={k:e23.Server(k)for k in cfg['servers']}
        econ=e23.Economics(c,calls,servers,copy.deepcopy(cfg))
        for key in servers:
            stage=meta['profile']+':'+key
            if stage not in done:
                sweep(c,meta,calls,econ,key,('m5max64','m5max'),tables);save(stage)
        stage=meta['profile']+':fleet'
        if stage not in done:
            fleet_variants(c,meta,calls,econ,tables);save(stage)
        # Do not retain complete prior profile caches unnecessarily.
        for slowdown in m.config()['glm_prefill_slowdowns']:
            stage=meta['profile']+':glm:'+str(slowdown)
            if stage in done:continue
            sv=m.GlmServer(servers['b300_fp8'],slowdown);ge=m.GlmEconomics(c,calls,sv,copy.deepcopy(cfg))
            sweep(c,meta,calls,ge,sv.key,('ultra256','ultra512'),tables,True);save(stage)
        print('profile finished',meta['profile'],flush=True)
    for billing in ('bought','rented'):
        for retention in ('weights_only_floor','all_resident_sessions'):
            series=[]
            for team in range(1,501):
                row=m.cloud_capacity(team,c.inputs,billing,retention=retention);series.append(row['person_month'])
                if team in SAMPLES:tables['cloud_reference'].append(dict(billing=billing,team=team,**row,
                    model='Qwen3.8-2.4T-A95B FP8',parameters=2.4e12,active_parameters=95e9,
                    basis='CAPACITY COST ONLY; no cloud-class service throughput measurement or replica scaling; multi-node TP/expert communication unmeasured;262144 context,90%HBM,8GB workspace/GPU; no task-success claim'))
            wins=[x<=1000 for x in series]
            intervals=fleet25.intervals(wins)
            tables['cloud_affordability'].append(dict(billing=billing,retention_basis=retention,
                criterion='capacity cost <=1000 USD/person-month; declared budget, not successful-work cost or service certification',
                first_affordable=next((i+1 for i,v in enumerate(wins)if v),None),affordable_team_intervals=json.dumps(intervals),
                team50_person_month=series[49],service_cost_pending=True,scan_max=500))
    tables['moe_decode']=moe_rows()
    tables['class_map']=[
        dict(model_class='cloud',model='Qwen3.8-2.4T-A95B FP8',inside_contour='multi-node internal cluster',hybrid_applies=False,client='none; weights alone exceed512GB',basis='model-card2.4T/95B;2.4TB FP8 weights; at least two8xB300 weight-capacity nodes, service pending'),
        dict(model_class='middle dense',model='Qwen3.8-27B',inside_contour='own vLLM PRO/B300 or prefill-only hybrid',hybrid_applies=True,client='M5 Max64/128GB owned/new',basis='PRI31 measured64GB;128GB same-SoC portability; bf16 transport; finite client decode capacity'),
        dict(model_class='middle MoE',model='GLM-5.3-Flash',inside_contour='two-B300/replica own cluster or projected prefill-only hybrid',hybrid_applies=True,client='EXTRAPOLATED M5 Ultra256/512GB owned/new',basis='all GLM/Ultra performance UNMEASURED, client Q4/GLM KV layout unqualified; scenario applicability, no runtime certification')]
    tables['pending_inputs']=[dict(input=x,status='pending; never a measured result',effect=y)for x,y in [
        ('GLM Studio prefill/decode','all Ultra/GLM timings and crossings conditional on Max-to-Ultra and model portability'),
        ('GLM B300 prefill/decode','failed rental; Qwen FLOP portability x1/x2 and expert-union bandwidth projection only'),
        ('GLM slot/import/transport quality','MLA layout derived, linear state estimated; bf16 wire and Qwen import/bridge reuse unqualified'),
        ('2.4T multi-node throughput and storage','cloud reference and common large cost are capacity-cost floors, extra service/storage unknown'),
        ('task success share','s20/50/100 input scenario; no equal-quality or completed-work price claim'),
        ('Ultra performance','2x measured M5 Max compute and inferred bandwidth extrapolation, no Studio benchmark'),
        ('Studio purchase cost','sourced US reported list-price proxy; actual tax/availability/quote pending'),
        ('joint raw-call trace','aggregate fitted/reconstructed shapes; no observed token/work coverage or peak scheduler qualification')]]
    return tables
