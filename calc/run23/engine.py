"""Run23 successor: night measurements replace labelled estimates."""
import copy
import hashlib
import json
import math

from hybridcalc.engine import load
from hybridcalc.paper_tables import Context
from hybridcalc.inputs import InputGap
from hybridcalc import deep_r21 as deep, measurements_r21 as r21
from hybridcalc import measurements_r20 as old, server_economics_r20 as s
from hybridcalc import measurements_r16 as r16, measurements_r17 as r17
from run22 import api, interfaces, measurements as m
from run22 import engine as previous, economics as old_e
from . import economics as e, inputs as night, routing, sentences


def links(c):
    from hybridcalc import measurements_r19 as r19
    out={x['key']:x for x in deep.config()['links']}
    for row in r19.links(c.inputs):
        out.setdefault(row['key'],row)
    return list(out.values())


def context():
    _,inputs=load('deep-economics-r21')
    spec,_=load('paper-tables-r17')
    c=Context(spec,inputs)
    # Set before any client graph resolves, so measured decoded curves replace
    # the old owner-reported-priority family throughout this run alone.
    c.measured_m5=e.M5Rates()
    return c


def threshold_rows(context,servers,pending):
    return routing.threshold_rows(context,servers,pending)


def full_resync(context):
    rows=previous.full_resync(context)
    for row in rows:
        row.update(server='historical_llama_pro6000_slot_builder',engine='llama.cpp Q4_K_M/q8_0',
            feasible_server_scenario=False,current_vllm_admission=False,
            capacity_basis='historical slot-artifact construction only; PRO vLLM default KV at1M is impossible,61.97GiB >56.62GiB; FP8 KV unavailable')
    return rows


def _base(profile,tier,transport,load,share,client,basis,key,billing,scope,c,api_window):
    return dict(profile=profile,scope_tier=tier,transport=transport,load=load,share=share,client=client,basis=basis,server=key,billing=billing,
        full_calls_day=c.inputs.get('service.profiles.'+load),intensity_basis=e.intensity(load),workload_scope=scope,
        cache_basis='98.1% aggregate allowance with1.9% billed misses, provider cache unverified',
        api_window_basis=api_window,
        rate_basis='M5 Max64 PRI31 ladder/parallel;128GB same-SoC portability; measured delta/depth interpolation, tails estimated; vLLM prefill measured<=249k, deeper extrapolated; PRO decode measured surface 16384–256000 with seconds interpolation and reciprocal residency, beyond modelled; B300 decode modelled after failed rental; bf16 import seconds reused from f32 for economics clients; resident state remains f32; M3 direct deep observations are not M5 economics measurements')


def calculate(scan_max=500, tiers=('measured_ladder','physical_extended')):
    c=context(); cfg=deep.config(); stats=deep.checked_stats(cfg)
    original=c.g.resolve(c.valid).value
    base_cfg=s.config(); base_cfg['servers']={k:base_cfg['servers'][k] for k in deep.SERVERS}
    preliminary={k:old_e.Server(k,base_cfg) for k in deep.SERVERS}
    pending=night.pending_inputs(preliminary)
    api_scenario='measured_common_window' if pending['window'] is not None else 'snapshot_1d'
    api_window=('measured common window '+pending['window'][0].isoformat()+' to '+pending['window'][1].isoformat()+', >=95%; unobserved providers unverified' if pending['window'] else
        'OpenRouter2026-10-29 last1d for every provider, >=95%; exact window endpoints unretained')
    servers={k:e.Server(k,base_cfg,pending['prefill'],pending['decode']) for k in deep.SERVERS}
    table={name:[] for name in ('small_team_cost','main_economics','team_break_even','dedicated_multiples','shared_multiples','idleness','api_admission','workload_coverage','heavy_sensitivity','direct_mac_pending')}
    profiles=(('existing_combined',original),('claude_deep',deep.reconstruct(stats['agents']['claude'],cfg['quadrature_points'],cfg['active_gap_cap_s'])))
    for profile,calls in profiles:
        true_measured=[i for i,(depth,n,o,t) in enumerate(calls) if 16000<=depth and depth+n+o<=249000 and 512<=n<=10000]
        for tier in tiers:
            max_end=min(deep.LIMIT,min((server.free-server.state)/server.kv for server in servers.values()))
            indices=true_measured if tier=='measured_ladder' else [i for i,(depth,n,o,t) in enumerate(calls) if depth+n+o<=max_end]
            selected=[calls[i] for i in indices]
            if not selected:
                raise InputGap('run23.workload','empty selected same-mix envelope')
            table['workload_coverage'].append(dict(profile=profile,scope_tier=tier,source_calls=len(calls),selected_calls=len(selected),
                measured_shape_calls=len(true_measured),measured_shape_fraction=len(true_measured)/len(calls),selected_fraction=len(selected)/len(calls),
                original_profile_sha256=hashlib.sha256(json.dumps(calls,separators=(',',':')).encode()).hexdigest(),
                basis='coverage counts CALL SHAPES, never share of total workload/tokens; Claude is aggregate reconstruction, not raw-call replay; physical_extended coverage is not measured-ladder coverage'))
            billed=old.billing_calls(calls,indices,c.inputs.get('workload.chunk_calls'))
            means=tuple(sum(x[i] for x in billed)/len(billed) for i in range(3))
            limit=max(262144 if tier=='measured_ladder' else 1000000,math.ceil(max(depth+n+o for depth,n,o,t in billed)))
            scenarios=['snapshot_1d']
            if pending['window'] is not None:
                scenarios.append('measured_common_window')
            scope=e.coverage(calls,indices,true_measured,profile,1,tier)
            apis,api_refs=api.baseline(means,profile,limit,scope,pending['cache'],pending['availability'],pending['window'],scenarios)
            # These are per1,000-call means; costs below explicitly normalize the
            # exact same call shapes to each demanded person-month separately.
            for row in apis:
                row['scope_tier']=tier
                row['workload_scope']=scope.replace('normalized to 1 calls/person-month','API unit normalized to1000 calls; monthly rows scale the same shapes to their stated calls/person-month')
            table['api_admission']+=apis
            pcfg=copy.deepcopy(base_cfg)
            pcfg['reservation_depth']=r21.profile_reservation(selected,249000 if tier=='measured_ladder' else cfg['reservation_depth'],servers)
            reuse=None
            for transport in ('bf16','f32'):
                econ=e.Economics(c,selected,servers,pcfg,transport,pending['decode'],reuse)
                reuse=econ
                for load in ('light','medium','heavy'):
                    for share in (.2,.5,1.0):
                        demand=c.inputs.get('service.profiles.'+load)*share; monthly=demand*econ.days
                        scope=e.coverage(calls,indices,true_measured,profile,monthly,tier)
                        for client in ('m5max64','m5max'):
                            for key in deep.SERVERS:
                                for billing in ('bought','rented'):
                                    # New-client cost is an additive capital term;
                                    # the routing/fleet is otherwise identical.
                                    series={basis:[] for basis in ('owned','new')}
                                    own_series=[]
                                    offload_family=[]
                                    samples={}
                                    for team in range(1,scan_max+1):
                                        h=econ.hybrid(key,team,demand,client,'owned',billing,'measured_envelope')
                                        own=econ.own(key,team,demand,billing)
                                        own_series.append(own['person_month'])
                                        offload_family.append(h.get('offload_share'))
                                        for basis in ('owned','new'):
                                            if basis=='owned':
                                                item=h
                                            else:
                                                item=dict(h)
                                                p='hardware.clients.'+client
                                                purchase=c.inputs.get(p+'.purchase_price')*(1-c.inputs.get('economics.client_residual'))/(12*c.inputs.get('owners.years'))
                                                if isinstance(item['person_month'],(int,float)):
                                                    item['person_month']+=purchase; item['device_month']=purchase
                                            series[basis].append(item['person_month'])
                                            if team in (3,5,10,20,50,500):
                                                base=_base(profile,tier,transport,load,share,client,basis,key,billing,scope,c,api_window)
                                                util=econ.utilization(key,team,demand,item,'hybrid')
                                                own_util=econ.utilization(key,team,demand,own,'own')
                                                row=dict(base,team=team,**item,**util,
                                                    own_cluster_person_month=own['person_month'],own_cluster_boxes=own['boxes'],own_cluster_server=key,
                                                    own_cluster_basis='same server hardware/engine and bought/rented billing, identical call shapes',
                                                    own_service_utilization=own_util['service_utilization'],own_calendar_utilization=own_util['calendar_utilization'],
                                                    usd_per_1000_calls=old.ratio(item['person_month'],monthly/1000),
                                                    pricing_basis='PRIMARY dedicated calendar-billed team node; full chassis amortization or730h rent; unused capacity paid; no5090 server',
                                                    resident_state_bytes=m.F32,wire_state_bytes=m.state_bytes(transport))
                                                for point in ('no_cache','owner_981','measured'):
                                                    comparison=api_refs.get((api_scenario,point))
                                                    for role in ('cheapest','median'):
                                                        row['api_'+role+'_'+point+'_person_month']=comparison[role]*monthly if comparison else ''
                                                table['small_team_cost' if team in (3,5,10,20) else 'main_economics'].append(row)
                                                samples[basis,team]=row
                                    for basis in ('owned','new'):
                                        base=_base(profile,tier,transport,load,share,client,basis,key,billing,scope,c,api_window)
                                        refs={'own_cluster':own_series}
                                        for point in ('no_cache','owner_981','measured'):
                                            choice=api_refs.get((api_scenario,point))
                                            if choice:
                                                for role in ('cheapest','median'):
                                                    refs['api_'+role+'_'+point]=[choice[role]*monthly]*scan_max
                                        # Large physical-envelope sweeps are a
                                        # sensitivity; retain per-profile crossings.
                                        for reference,values in refs.items():
                                            point='no_cache' if reference.endswith('_no_cache') else 'owner_981' if reference.endswith('_owner_981') else 'measured' if reference.endswith('_measured') else 'owner_981'
                                            b=dict(base,reference=reference,**old.break_even(series[basis],values),
                                                offload_share_min=min((p for p in offload_family if isinstance(p,(int,float))),default=''),
                                                offload_share_max=max((p for p in offload_family if isinstance(p,(int,float))),default=''))
                                            b['cache_basis']='no cache, all input billed' if point=='no_cache' else '98.1% aggregate allowance with1.9% billed misses, provider cache unverified' if point=='owner_981' else 'measured provider rate, no low-hit exclusion'
                                            if point=='measured':
                                                role='cheapest' if 'cheapest' in reference else 'median'
                                                choice=api_refs[api_scenario,point]
                                                b['cache_basis']='measured {}% cached input for {}, no low-hit exclusion'.format(100*choice[role+'_hit'],choice[role+'_provider'])
                                            if reference=='own_cluster':
                                                human='own vLLM cluster on the same server and billing basis'
                                                b['api_provider']='not applicable'
                                            else:
                                                role='cheapest' if 'cheapest' in reference else 'median'
                                                choice=api_refs[api_scenario,point]
                                                b['api_provider']=choice[role+'_provider']
                                                human=role+' admitted API ('+b['api_provider']+')'
                                            b['sentence']=sentences.sentence(b,b['statement']+' versus '+human)
                                            b['short_sentence']=sentences.short_sentence(b,b['statement']+' versus '+human)
                                            table['team_break_even'].append(b)
                                        for team in (50,500):
                                            if (basis,team) not in samples:
                                                continue
                                            h=samples[basis,team]
                                            choice=api_refs[api_scenario,'owner_981']
                                            if not isinstance(h['person_month'],(int,float)):
                                                claim='capacity alarm: no finite hybrid cost'
                                                median=cheapest=''
                                            else:
                                                median=choice['median']*monthly/h['person_month']; cheapest=choice['cheapest']*monthly/h['person_month']
                                                claim='team{} dedicated hybrid ${:.2f}/person-month, API/hybrid {:.3f} median({}) and {:.3f} cheapest({}), service utilization {:.2%}, calendar occupancy {:.2%}'.format(team,h['person_month'],median,choice['median_provider'],cheapest,choice['cheapest_provider'],h['service_utilization'],h['calendar_utilization'])
                                            row=dict(h,api_median_over_hybrid=median,api_cheapest_over_hybrid=cheapest,
                                                api_median_provider=choice['median_provider'],api_cheapest_provider=choice['cheapest_provider'],
                                                sentence=sentences.sentence(h,claim),short_sentence=sentences.short_sentence(h,claim))
                                            table['dedicated_multiples'].append(row)
                                # Shared rows are expressly supplementary limits.
                                for basis in ('owned','new'):
                                    base=_base(profile,tier,transport,load,share,client,basis,key,'shared_work',scope,c,api_window)
                                    sh=econ.shared(key,demand,client,basis)
                                    choice=api_refs[api_scenario,'owner_981']
                                    row=dict(base,**sh,team='provider pool',pricing_basis='SUPPLEMENTARY resident-work limit / shared prefill provider; no paid calendar idle fleet',
                                        api_median_provider=choice['median_provider'],api_cheapest_provider=choice['cheapest_provider'],
                                        api_median_over_hybrid=choice['median']*monthly/sh['person_month'],api_cheapest_over_hybrid=choice['cheapest']*monthly/sh['person_month'])
                                    claim='shared-work hybrid ${:.2f}/person-month; API/hybrid {:.3f} median({}) and {:.3f} cheapest({}); provider occupancy{:.0%};100% utilization lower bound ${:.2f}/person-month'.format(row['person_month'],row['api_median_over_hybrid'],row['api_median_provider'],row['api_cheapest_over_hybrid'],row['api_cheapest_provider'],row['service_utilization'],row['full_utilization_person_month'])
                                    row['sentence']=sentences.sentence(row,claim); row['short_sentence']=sentences.short_sentence(row,claim)
                                    table['shared_multiples'].append(row)
                                    if scan_max>=50:
                                        dedicated=econ.hybrid(key,50,demand,client,basis,'bought','measured_envelope')
                                        aligned=econ.shared(key,demand,client,basis,'office_gigabit')
                                        table['idleness'].append(dict(base,team=50,billing='bought',shared_billing='shared resident-work rental allocation',
                                            link='office125 MB/s RTT1 ms assumed for both sides',
                                            dedicated_person_month=dedicated['person_month'],shared_office_person_month=aligned['person_month'],
                                            full_utilization_office_person_month=aligned['full_utilization_person_month'],
                                            dedicated_minus_shared_limit=dedicated['person_month']-aligned['person_month'] if isinstance(dedicated['person_month'],(int,float)) else '',
                                            **econ.utilization(key,50,demand,dedicated,'hybrid'),
                                            basis_note='price of idleness comparison on same office125MB/s1ms; bought chassis vs prorated rental-work limit also differs in tariffs, residency misses, storage and batching; not a pure idle-only causal effect; night-agent autopilot may raise utilization'))
                print('prepared',profile,tier,transport,flush=True)
    # Cache and availability scenarios at1M, with and without Alibaba. No mixed
    # time-window admission, and no cheapest-cache verdict before provider tests.
    scope='million-token fixed-depth shape; normalized to1000 calls; not a sampled fraction of the workload'
    # Same fixed task as R21:690 new and762 generated tokens, with the answer
    # reserved inside the API's advertised1,000,000-token total window.
    million_api,_=api.baseline((1000000-690-762,690,762),'million',1000000,scope,pending['cache'],pending['availability'],pending['window'],
        ('snapshot_1d','analyst_72h_with_alibaba','analyst_72h_without_alibaba')+ (('measured_common_window',) if pending['window'] else ()))
    for row in million_api:
        row['scope_tier']='million_fixed_depth'
    table['api_admission']+=million_api
    table['link_thresholds']=threshold_rows(c,servers,pending)
    table['full_resync']=full_resync(c)
    table['client_measurements']=m.measurement_rows()
    table['workload_profiles']=deep.profile_rows(stats)
    table['decode_scaling']=r21.decode_table(servers,pending['decode'])
    measured=[]
    for observation in pending['decode']:
        server=servers[observation['server']]
        result=server.decode(observation['depth'],observation['streams'],pending['decode'])
        measured.append(dict(observation,**{k:v for k,v in result.items()if k not in observation}))
        if not any(r['server']==server.key and r['depth']==observation['depth'] and r['requested_streams']==observation['streams'] for r in table['decode_scaling']):
            table['decode_scaling'].append(dict(server=server.key,model='qwen',depth=observation['depth'],requested_streams=observation['streams'],
                **result,context_basis=deep.extension_basis('qwen','server'),session_bytes=server.session_bytes(observation['depth'])))
    table['server_decode_measured']=measured
    direct=night.mac_rows()
    table['mac_direct_measurements']=list(direct.values())
    table['bridge_timing_context']=night.bridge_rows()
    table['decode_ceiling']=[dict(client='m3max',depth=depth,ceiling_tok_s=deep.mac_ceiling(depth),measured_decode_tok_s=direct[actual,690]['decode_tok_s'],
        measured_depth=actual,priority='normal_priority',basis='M3 Max bandwidth ceiling versus normal-priority measured decode; warm/no purge external LaCie restore; actual measurement depth explicit')
        for depth,actual in ((1000000,1040000),(1040000,1040000),(524288,524288))]
    table['direct_mac_pending']=[dict(client=client,depth=1040000,delta=delta,**{k:v for k,v in pending['mac'].get((client,1040000,delta),{}).items()if k not in ('client','depth','delta')},
        basis='optional future measured delta import; distinct from the charged full-slot-recovery proxy; no invented observation')
        for client in ('m3max','m5max64','m5max')for delta in (690,2000,10000)]
    for profile in ('existing_combined','claude_deep'):
        source=next((r for r in table['main_economics'] if r['profile']==profile and r['scope_tier']=='measured_ladder' and r['transport']=='bf16' and r['load']=='heavy' and r['share']==.2 and r['client']=='m5max64' and r['basis']=='owned' and r['server']=='pro6000_fp8' and r['billing']=='bought' and r['team']==50),None)
        table['heavy_sensitivity'].append(dict(profile=profile,load='heavy',full_calls_day=2500,share=.2,client='m5max64',server='pro6000_fp8',transport='bf16',team=50,billing='bought',
            sensitivity='generation moved to the team own vLLM server',
            move_generation_person_month=source['own_cluster_person_month'] if source else '',
            service_utilization=source['own_service_utilization'] if source else '',calendar_utilization=source['own_calendar_utilization'] if source else '',
            workload_scope=source['workload_scope'] if source else 'preflight only',
            basis='single sensitivity only; existing main rows already charge capacity overflow to own server, moving all generation gives the own_cluster_person_month bound next to each dedicated cost; not a second Mac;2500/day is owner intensity, light/medium typical; Ultra-class client unmeasured, no invented price/performance'))
    table['quality_evidence']=m.quality_rows()
    table['policy']=[dict(key='primary_basis',value='dedicated bought or calendar-rented team server; shared resident-work/provider allocation is supplementary limit',
        reason='authors operate a shared prefill service, therefore shared allocation must not be the headline; night-agent autopilot can raise utilization'),
        dict(key='withdrawn_heavy_claim',value='not a universal any-team-size advantage',
        reason='own cluster recalculated on vLLM; under vLLM prices the old heavy-load claim held only for a5090 hybrid, which the owner excluded; not a second-Mac hardware explanation')]
    return table
