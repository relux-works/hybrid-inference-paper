"""RC4 bf16 defaults, dedicated primary basis and explicitly pending evidence."""
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
from . import api, interfaces, measurements as m, economics as e, sentences


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


def threshold_rows(c,servers,pending):
    out=[]; importer=r16.ClientImport()
    profiles=links(c)
    for key,server in servers.items():
        for client in ('m3max','m5max64'):
            for transport in ('bf16','f32'):
                for depth in (32000,64000,100000,1000000):
                    for n in ((690,) if depth==1000000 else (512,2343,10000)):
                        for variant in (('measured_anchor_flop_extension','analyst_120s_at_1M') if depth==1000000 else ('measured_ladder_interpolation',)):
                            local=120*n/690 if variant=='analyst_120s_at_1M' else e.mac_prefill(c,client,depth,n)
                            imp=importer.at_depth(n,depth)
                            pre=server.cached(depth,n,'measured_envelope')
                            size=m.wire(n,transport)
                            try:
                                slots=server.slots(depth+n)
                            except InputGap:
                                slots=0
                            for link in profiles:
                                budget=local-pre-imp-link['rtt_s']
                                remote=pre+imp+link['rtt_s']+size/link['bytes_s']
                                out.append(dict(model='qwen',server=key,client=client,transport=transport,depth=depth,delta=n,
                                    link=link['key'],bytes_s=link['bytes_s'],rtt_s=link['rtt_s'],wire_bytes=size,state_bytes=m.state_bytes(transport),
                                    local_prefill_s=local,server_prefill_s=pre,import_s=imp,transfer_s=size/link['bytes_s'],
                                    remote_s=remote,budget_s=budget,threshold_MB_s=size/budget/1e6 if budget>0 and slots else '',
                                    offload=bool(slots and remote<local),resident_slots=slots,
                                    verdict='capacity refusal' if not slots else 'never: nonpositive budget' if budget<=0 else 'finite threshold',
                                    rate_basis=variant+'; Qwen M3 PRI31 measured anchors / M5 kit1.6.7 normal-priority anchors,1M FLOP-efficiency extension estimated; Mac import depth slope extrapolated at1M, bf16 same import seconds assumption; direct1.04M delta/import/logits/decode CSV pending',
                                    link_basis=link['basis']))
    # SWA has no recurrent state: bf16/f32 transport is not a model distinction.
    geometry=r17.geometry('glimmer30'); gpu=r17.Surface('glimmer30','server')
    for client in ('m3max','m5max64'):
        mac=m.Mac('glimmer',client)
        for depth in (32000,64000,100000):
            for n in (512,2343,10000):
                local=mac.prefill(depth,n); pre=n/gpu.for_delta(depth,n); imp=importer.at_depth(n,depth)
                size=r17.offload_bytes(geometry,n,depth)
                for link in profiles:
                    budget=local-pre-imp-link['rtt_s']
                    out.append(dict(model='glimmer',server='llama_pro6000',client=client,transport='no_recurrent_state',depth=depth,delta=n,
                        link=link['key'],bytes_s=link['bytes_s'],rtt_s=link['rtt_s'],wire_bytes=size,state_bytes=0,
                        local_prefill_s=local,server_prefill_s=pre,import_s=imp,transfer_s=size/link['bytes_s'],
                        remote_s=pre+imp+link['rtt_s']+size/link['bytes_s'],budget_s=budget,threshold_MB_s=size/budget/1e6 if budget>0 else '',
                        offload=budget>size/link['bytes_s'],resident_slots='',verdict='finite threshold' if budget>0 else 'never: nonpositive budget',
                        rate_basis=mac.basis+'; SWA reuses Qwen Mac import fit as unmeasured portability assumption; ideal final window transport, no new hybrid measurement',link_basis=link['basis']))
    return out


def full_resync(c):
    rows=[]
    for depth,prefill,restore,slot in ((524288,518.29,1.83,18425185848),(1040000,1813.77,3.14,36394654776)):
        for link in (links(c) if c else deep.config()['links']):
            for transport in ('bf16','f32'):
                size=slot-(m.F32-m.BF16 if transport=='bf16' else 0)
                rows.append(dict(server='llama_pro6000',depth=depth,transport=transport,wire_bytes=size,
                    measured_f32_slot_bytes=slot,rebuild_s=prefill,server_restore_s=restore,link=link['key'],bytes_s=link['bytes_s'],
                    transfer_s=size/link['bytes_s'],rebuild_and_transfer_s=prefill+size/link['bytes_s']+link['rtt_s'],
                    basis='measured sequential cold rebuild on PRO6000 ServerEdition llama.cpp;1M total518.29+1295.48=1813.77s; server restore is on GPU host, NOT Mac import; '+
                    ('bf16 wire estimate assumes lossless container conversion except recurrent tensor cast; full-slot bf16 encoding unmeasured' if transport=='bf16' else 'f32 control: actual serialized slot bytes; full-slot framing retained')+
                    '; vLLM full-resync latency not measured; no transfer protocol throughput claim'))
    return rows


def _base(profile,tier,transport,load,share,client,basis,key,billing,scope,c,api_window):
    return dict(profile=profile,scope_tier=tier,transport=transport,load=load,share=share,client=client,basis=basis,server=key,billing=billing,
        full_calls_day=c.inputs.get('service.profiles.'+load),intensity_basis=e.intensity(load),workload_scope=scope,
        cache_basis='98.1% aggregate allowance with1.9% billed misses, provider cache unverified',
        api_window_basis=api_window,
        rate_basis='M5 Max64 kit1.6.7 PRI31 ladder/parallel;128GB same-SoC portability; measured delta/depth interpolation, tails estimated; server vLLM prefill measured<=249k, deeper extrapolated; server decode measured only at observed depth/count pairs, deeper modelled; bf16 import seconds reused from f32; resident state remains f32')


def calculate(scan_max=500, tiers=('measured_ladder','physical_extended')):
    c=context(); cfg=deep.config(); stats=deep.checked_stats(cfg)
    original=c.g.resolve(c.valid).value
    base_cfg=s.config(); base_cfg['servers']={k:base_cfg['servers'][k] for k in deep.SERVERS}
    preliminary={k:e.Server(k,base_cfg) for k in deep.SERVERS}
    pending=api.pending_inputs(preliminary)
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
                raise InputGap('run22.workload','empty selected same-mix envelope')
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
                                    samples={}
                                    for team in range(1,scan_max+1):
                                        h=econ.hybrid(key,team,demand,client,'owned',billing,'measured_envelope')
                                        own=econ.own(key,team,demand,billing)
                                        own_series.append(own['person_month'])
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
                                            b=dict(base,reference=reference,**old.break_even(series[basis],values))
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
        measured.append(dict(observation,**{k:v for k,v in result.items() if k not in observation}))
        # Preserve the modelled16000 grid and the exact measured16384 coordinate;
        # never round the latter down or extend it to64k/deeper.
        if observation['depth'] not in (16000,64000,164000,512000,1000000) or observation['streams'] not in (1,8,32):
            table['decode_scaling'].append(dict(server=server.key,model='qwen',depth=observation['depth'],
                requested_streams=observation['streams'],**result,context_basis=deep.extension_basis('qwen','server'),session_bytes=server.session_bytes(observation['depth'])))
    table['server_decode_measured']=measured
    table['decode_ceiling']=[dict(client='m3max',depth=1000000,ceiling_tok_s=deep.mac_ceiling(1000000),measured_decode_tok_s=1.67,
        measured_depth=1040000,priority='background_priority_interim',basis='memory bandwidth ceiling; PRI31 Mac1M decode CSV pending; gap remains open')]
    for client in ('m3max','m5max64','m5max'):
        for delta in (690,2000,10000):
            row=pending['mac'].get((client,1040000,delta),{})
            table['direct_mac_pending'].append(dict(client=client,depth=1040000,delta=delta,prefill_s=row.get('prefill_s',''),import_s=row.get('import_s',''),
                decode_tok_s=row.get('decode_tok_s',''),logits_kl=row.get('logits_kl',''),source=row.get('source','pending'),
                import_kind=row.get('import_kind',''),transport=row.get('transport',''),
                basis='direct restored1.04M slot measurement; no substitution from analyst120s or1M FLOP extrapolation'))
            if isinstance(row.get('prefill_s'),(int,float)):
                for server_key,server in servers.items():
                    # A direct1.04M sample remains at its own depth; never relabel
                    # it as a measured1M turn. Delta10000 may exceed the configured
                    # server envelope and is then explicitly capacity-refused.
                    fits=1040000+delta<=1048576
                    try:
                        slots=server.slots(1040000+delta) if fits else 0
                    except InputGap:
                        slots=0
                    pre=server.cached(1040000,delta,'measured_envelope') if fits else 0
                    for transport in ('bf16','f32'):
                        imp=row.get('import_s')
                        measured_import=isinstance(imp,(int,float)) and row.get('import_kind')=='delta_import' and row.get('transport')==transport
                        import_basis='measured direct '+transport+' delta import' if measured_import else 'Mac delta-import depth-fit extrapolation; matching direct import pending (slot restore not substituted)'
                        if not measured_import:
                            imp=r16.ClientImport().at_depth(delta,1040000)
                        for link in cfg['links']:
                            budget=row['prefill_s']-pre-imp-link['rtt_s'];size=m.wire(delta,transport)
                            table['link_thresholds'].append(dict(model='qwen',server=server_key,client=client,transport=transport,depth=1040000,delta=delta,
                                link=link['key'],bytes_s=link['bytes_s'],rtt_s=link['rtt_s'],wire_bytes=size,state_bytes=m.state_bytes(transport),
                                local_prefill_s=row['prefill_s'],server_prefill_s=pre if fits else '',import_s=imp,transfer_s=size/link['bytes_s'],
                                remote_s=pre+imp+link['rtt_s']+size/link['bytes_s'] if slots else '',budget_s=budget if slots else '',
                                threshold_MB_s=size/budget/1e6 if budget>0 and slots else '',offload=bool(slots and budget>size/link['bytes_s']),resident_slots=slots,
                                verdict='capacity refusal' if not slots else 'never: nonpositive budget' if budget<=0 else 'finite threshold',
                                rate_basis='direct restored1.04M Mac PRI31 prefill; '+import_basis+'; transport import-seconds reuse assumption',link_basis=link['basis']))
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
