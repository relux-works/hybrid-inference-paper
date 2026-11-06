"""Run16 priority-qualified anchors, prototype import and finite link validation."""
import gzip
import copy
import ast
import hashlib
import json
import math
from pathlib import Path

from .inputs import InputGap, ROOT
from .measurements_r13 import rows, verified_archive
from .measurements_r14 import ParallelAnchors as Lookup, one_file, raw_table
from .measurements_r15 import ParallelAnchors as Interim, cooled_points
from .performance import Curve

CONFIG = Path(__file__).parent/'data/run16-measurements.json'
MODEL = dict(base_flop=54e9, attention_slope=393216, sparse_slope=0,
             sparse_cap=0, context_limit=2e6)
DEPTHS = (16000, 50000, 100000, 150000, 200000, 249000)
DELTAS = (512, 2000, 10000)


def config():
    return json.loads(CONFIG.read_text())


def checked(info):
    content = (ROOT/info['path']).read_bytes()
    if hashlib.sha256(content).hexdigest() != info['sha256']:
        raise InputGap('measurements.run16', 'source sha256 mismatch: '+info['path'])
    return content


def package(key, cfg=None):
    info = (cfg or config())[key]
    checked(info)
    return verified_archive(ROOT/info['path'], info['sha256'])


def normal_priority(manifest, payload):
    if manifest.get('normal_priority') is not True or manifest.get('priority_override_used') is not False:
        raise InputGap('measurements.priority', 'recorded normal priority without override required')
    name, content = one_file(payload, 'OPERATOR-READINESS', '.json')
    record = json.loads(content)
    servers = [s for sample in record.get('samples', []) for s in sample.get('servers', [])]
    if (record.get('normal_priority') is not True or record.get('override_used') is not False or
            not servers or any(s.get('pri') != 31 or s.get('errors') for s in servers) or
            any(s.get('violations') or s.get('normal_priority') is not True for s in record['samples'])):
        raise InputGap('measurements.priority', 'PRI31 server samples required')


def nonnegative(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise InputGap('measurements.run16.'+name, 'finite nonnegative value required')
    return value


class SingleStream:
    """Nominal-depth delta surface; cold fills have a separate segment curve."""
    def __init__(self, manifest=None, payload=None):
        if manifest is None:
            manifest, payload = package('m3')
        normal_priority(manifest, payload)
        self.source, content = one_file(payload, '-q27b-q4km-')
        self.records = rows(content)
        segments = [r for r in self.records if r['kind']=='segment']
        turns = [r for r in self.records if r['kind']=='turn']
        expected = {(d,n) for d in DEPTHS for n in DELTAS}
        if (len(segments)!=6 or {r['level'] for r in segments}!=set(DEPTHS) or
                len(turns)!=18 or {(r['level'],r['delta']) for r in turns}!=expected):
            raise InputGap('measurements.m3_single', 'complete six-depth three-delta grid required')
        for r in segments+turns:
            if (r.get('truncated') is not False or r.get('gen_tokens_exact') is not True or
                    r.get('reread') is not False or r.get('cache_reused') is not True or
                    any(type(r.get(k)) not in (int,float) or not math.isfinite(r[k]) or r[k]<=0
                        for k in ('prompt_n','prompt_ms','predicted_n','predicted_ms'))):
                raise InputGap('measurements.m3_single', 'exact positive reused observations required')
        if any(r['prompt_n'] not in (r['delta'],r['delta']+1) or r['predicted_n']!=128 or
               r['depth']!=r['level']+{512:0,2000:640,10000:2768}[r['delta']] for r in turns):
            raise InputGap('measurements.m3_single', 'delta/framing/actual-depth mismatch')
        segments.sort(key=lambda r:r['depth'])
        if any(r['depth_from']!=(0 if a==0 else a+12896) or r['depth']!=b or
               r['prompt_n'] not in (b-r['depth_from'],b-r['depth_from']+1)
               for r,a,b in zip(segments,(0,)+DEPTHS[:-1],DEPTHS)):
            raise InputGap('measurements.m3_single', 'cold segment/probe boundary mismatch')
        self.cold_curve = Curve(MODEL, [((r['depth_from']+r['depth'])/2,r['prompt_n']*1000/r['prompt_ms']) for r in segments])
        self.curves = {n:Curve(MODEL, sorted((r['level'],r['prompt_n']*1000/r['prompt_ms']) for r in turns if r['delta']==n)) for n in DELTAS}
        # FACTS' per-depth decode is the arithmetic mean of all three turn
        # rates, each using the kit's n / elapsed convention (not n-1).
        self.decode_points = [(d,sum(r['predicted_n']*1000/r['predicted_ms'] for r in turns if r['level']==d)/3) for d in DEPTHS]

    def __call__(self, depth):
        return self.for_delta(depth, 2000)

    def cold(self, depth):
        return self.cold_curve.rate(depth)

    def for_delta(self, depth, delta):
        nonnegative(depth,'depth');nonnegative(delta,'delta')
        if delta<=DELTAS[0]:
            return self.curves[DELTAS[0]].rate(depth)
        if delta>=DELTAS[-1]:
            return self.curves[DELTAS[-1]].rate(depth)
        for a,b in zip(DELTAS,DELTAS[1:]):
            if delta<=b:
                fraction=(delta-a)/(b-a)
                return self.curves[a].rate(depth)*(1-fraction)+self.curves[b].rate(depth)*fraction


def sweep(info, manifest, payload):
    if info['priority_basis']=='recorded_normal_priority_PRI31':
        normal_priority(manifest,payload)
    result=[]
    for grid in info['grids']:
        _,content=one_file(payload,grid['fragment'])
        metadata=[r for r in rows(content) if r['kind']=='meta']
        if (len(metadata)!=1 or metadata[0].get('cooldown_s')!=300 or metadata[0].get('rounds')!=3 or
                metadata[0].get('system',{}).get('machdep.cpu.brand_string')!=info['expected_device']):
            raise InputGap('measurements.parallel','cooled300s three-round device-qualified protocol required')
        result.extend(cooled_points(payload,grid['fragment'],grid['depth'],grid['server_np'],tuple(grid['counts'])))
    if not result or len({(p['streams'],p['depth']) for p in result})!=len(result):
        raise InputGap('measurements.parallel','nonempty distinct sweep grid required')
    for p in result:
        p.update(priority_basis=info['priority_basis'],background_priority_interim=info.get('background_priority_interim',False))
    return sorted(result,key=lambda p:(p['streams'],p['depth']))


class M3Anchors(Lookup):
    """Single anchors are PRI31; all remaining interim rates keep qualification."""
    def __init__(self, normalized, depth_law, single, cfg=None):
        cfg=cfg or config();info=cfg['m3_parallel'];self.depth_law=depth_law
        self.historical=[];self.shape_sensitivity=[]
        if info['mode']=='r15_interim':
            if info['background_priority_interim'] is not True or info['priority_basis']!='historical_background_priority_throttled':
                raise InputGap('measurements.priority','background sweep cannot claim final normal priority')
            old=Interim(normalized,depth_law)
            self.points=[dict(p,priority_basis=info['priority_basis'],background_priority_interim=True) for p in old.points if p['streams']>1]
            self.historical=[dict(p) for p in old.historical]+[dict(p) for p in old.points if p['streams']==1]
            self.shape_sensitivity=old.shape_sensitivity
        elif info['mode']=='verified_sweep':
            if info['priority_basis']!='recorded_normal_priority_PRI31' or info['background_priority_interim'] is not False:
                raise InputGap('measurements.priority','replacement sweep must record normal priority')
            manifest,payload=package('m3_parallel',cfg)
            self.points=[p for p in sweep(info,manifest,payload) if p['streams']>1]
        else:
            raise InputGap('measurements.parallel','unknown parallel admission mode')
        for p in self.historical:
            p.update(priority_basis='historical_background_priority_throttled',background_priority_interim=True,
                     sensitivity='historical; measured at background priority and throttled; excluded from canonical single anchors')
        for d,rate in single.decode_points:
            self.points.append(dict(depth=d,streams=1,aggregate_tok_s=rate,source=single.source,
                condition='PRI31 recorded; mean of three single-turn decode rates; nominal depth',conservative=False,
                server_np=1,rounds=3,round_aggregate_tok_s='mean across delta probes; not cooled rounds',
                payload_sha256=hashlib.sha256(package('m3')[1][single.source]).hexdigest(),
                priority_basis='recorded_normal_priority_PRI31',background_priority_interim=False))
        self.points.sort(key=lambda p:(p['streams'],p['depth']))
        self.priority_info=info

    def lookup(self,streams,depth):
        result=super().lookup(streams,depth)
        result['background_priority_interim']=self.priority_info['background_priority_interim'] if streams>1 else False
        result['priority_basis']=self.priority_info['priority_basis'] if streams>1 else 'recorded_normal_priority_PRI31'
        return result


class M5Anchors(Lookup):
    def __init__(self):
        info=config()['m5'];manifest,payload=package('m5')
        self.points=sweep(info,manifest,payload)
        self.depth_law=lambda k,d:1/(18973870432/k+34816*d+2*157000000)
        self.control=cooled_points(payload,'-scale131072-np4-control-np4-',131088,4,(4,))[0]


def configure_context(c):
    c.r16_single=SingleStream()
    c.curve=c.label('r16.cold_curve',c.r16_single.cold_curve)
    c.state=c.label('r16.fixed_state',config()['wire']['f32_state_bytes'])
    c.parallel=M3Anchors(c.inputs.measured_json('normalized'),c.m3_depth_law,c.r16_single)
    doc=copy.deepcopy(c.inputs.measured_json('normalized'))
    p=doc['parallel'];d=32784
    single=c.parallel.decode(1,d);aggregate=4*c.parallel.decode(4,d)
    p.update(baseline_native_decode_tok_s=single,normalized_max_decode_interval_aggregate_tok_s=aggregate,
             normalized_decode_interval_gain=aggregate/single)
    p['frozen_v11_row'].update(depth=d,streams=4)
    c.normalized=c.label('r16.decode_reference',doc)
    def calibration(w,kv,bw,passes,state):
        traffic=d*kv+passes*state
        efficiency=single*(w+traffic)/bw
        ideal_gain=4*(w+traffic)/(w+4*traffic)
        return efficiency,math.log(ideal_gain/(aggregate/single))/math.log(4)
    c.cal=c.add('r16.decode_cal',['owners.models.qwen27.weights_q4',c.kv,'hardware.clients.m3max.bandwidth','analysis.decode_state_passes',c.state],calibration)
    c.r16_m5=M5Anchors()
    c.measured_m5.decode=c.r16_m5.decode


def depth_fit(points=None):
    ps=points if points is not None else config()['import']['depth_points']
    if len(ps)<3 or len({p[0] for p in ps})!=len(ps):
        raise InputGap('measurements.import','distinct depth probes required')
    for x,y in ps:
        nonnegative(x,'depth');nonnegative(y,'import_s')
    mx=sum(p[0] for p in ps)/len(ps);my=sum(p[1] for p in ps)/len(ps)
    slope=sum((x-mx)*(y-my) for x,y in ps)/sum((x-mx)**2 for x,y in ps)
    intercept=my-slope*mx
    if slope<=0:
        raise InputGap('measurements.import','positive measured depth slope required')
    residual=sum((y-intercept-slope*x)**2 for x,y in ps)
    return intercept,slope,1-residual/sum((y-my)**2 for x,y in ps)


class ClientImport:
    def __init__(self,variant='prototype_depth'):
        if variant not in ('prototype_depth','bounded_undo'):
            raise InputGap('measurements.import','unknown import variant')
        self.variant=variant;self.record=config()['import'];intercept,self.slope,_=depth_fit()
        # The old1.498 intercept is from a marginal fit with varying depths.
        # Fit the depth probes conditionally at their fixed539-token delta;
        # keeping that marginal intercept would count its depth cost twice.
        self.fixed_s=intercept-self.record['probe_tokens']*self.record['seconds_token']
        nonnegative(self.fixed_s,'conditional_import_intercept')

    def __call__(self,tokens):
        raise InputGap('measurements.import.depth','conditioning depth required')

    def at_depth(self,tokens,depth):
        nonnegative(tokens,'delta');nonnegative(depth,'depth')
        return self.fixed_s+tokens*self.record['seconds_token']+(self.slope*depth if self.variant=='prototype_depth' else 0.0)


def link_threshold(local_s, server_s, import_s, wire_bytes, rtt_s):
    for k,v in (('local_s',local_s),('server_s',server_s),('import_s',import_s),('wire_bytes',wire_bytes),('rtt_s',rtt_s)):
        nonnegative(v,k)
    budget=local_s-server_s-import_s-rtt_s
    if budget<=0:
        raise InputGap('downstream','no finite downstream rate can beat local prefill')
    if wire_bytes==0:
        raise InputGap('wire_bytes','offload must carry state and delta')
    return wire_bytes/budget


def record_sources(inputs):
    cfg=config()
    for key,info in cfg.items():
        if not isinstance(info,dict) or 'path' not in info:
            continue
        content=checked(info)
        inputs.files[info['path']]=dict(path=info['path'],sha256=info['sha256'],provenance=dict(kind='measured',package='Run16 '+key,sha256=info['sha256']))
        if key in ('m3','m5','m3_parallel') and info['path'].endswith('.tar.gz'):
            for name,data in package(key,cfg)[1].items():
                path=info['path']+'::'+name
                inputs.files[path]=dict(path=path,sha256=hashlib.sha256(data).hexdigest(),provenance=dict(kind='measured',package='Run16 '+key,sha256=info['sha256']))
    name=str(CONFIG.relative_to(ROOT));inputs.files[name]=dict(path=name,sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest())


def source_json(key):
    return json.loads(gzip.decompress(checked(config()[key])))


def add_table(result,key,records):
    if not records:
        return
    columns={k:('bool' if isinstance(v,bool) else 'text' if isinstance(v,str) else
                'MB/s' if k.endswith('_mb_s') else 's' if k.endswith('_s') else
                'token/s' if k.endswith('_tok_s') else 'B' if k.endswith('_bytes') else
                'token' if k in ('depth','actual_depth','delta','prompt_n') else
                's/token' if k=='depth_slope_s_token' else '1') for k,v in records[0].items()}
    raw_table(result,key,records,columns)


def threshold_rows(single,server):
    w=config()['wire'];result=[]
    for depth in (100000,140000,200000):
        for delta in (512,2343,10000):
            for fmt in ('f32','bf16'):
                state=w[fmt+'_state_bytes'];size=state+delta*w['kv_bytes_token']
                for variant in ('prototype_depth','bounded_undo'):
                    local=delta/single.for_delta(depth,delta);remote=delta*(server.a+server.b*depth)
                    imp=ClientImport(variant).at_depth(delta,depth)
                    threshold=link_threshold(local,remote,imp,size,w['threshold_rtt_s'])
                    result.append(dict(depth=depth,delta=delta,state_format=fmt,state_bytes=state,delta_bytes=delta*w['kv_bytes_token'],
                        wire_bytes=size,import_variant=variant,local_prefill_s=local,server_prefill_s=remote,import_s=imp,
                        rtt_s=w['threshold_rtt_s'],break_even_downstream_mb_s=threshold/1e6,
                        offload_at_wifi_5_19_mb_s=5.19e6>threshold,offload_at_5g_9_75_mb_s=9.75e6>threshold,
                        depth_import_extrapolated=depth>max(p[0] for p in config()['import']['depth_points']),
                        server_basis='measured B300 Q4 bulk-turn OLS',
                        basis='ideal single offload; delta plus one fixed state; decimal MB; no catch-up/extra framing'))
    return result


def instrumentation_residual(timing,instrument,hybrid,component):
    if timing['trace_sha256']!=instrument['trace_sha256']:
        raise InputGap('measurements.instrumentation','trace identity mismatch')
    captures=[r for r in instrument['node_snapshot_capture_events'] if r['arm']=='hybrid' and r['turn']==hybrid['turn']]
    captured=sum(r['duration_seconds'] for r in captures)
    if (not captures or any(r.get('inside_call_ttft') is not True or r['status']!='ok' for r in captures) or
            len(captures)!=component['snapshot_capture_count'] or
            abs(captured-component['snapshot_download_seconds_sum'])>1e-6 or
            abs(component['ttft_seconds']-hybrid['ttft_seconds'])>1e-6 or
            not 0<captured<hybrid['ttft_seconds']):
        raise InputGap('measurements.instrumentation','unique synchronous capture accounting required')
    return hybrid['ttft_seconds']-captured


def validation_rows(single,server):
    timing=source_json('TIMING-EXTRACT.json.gz');instrument=source_json('INSTRUMENTATION-TIMING-EXTRACT.json.gz')
    result=[];link=timing['measured_link'];w=config()['wire']
    from .paper_tables import integrate
    for component in instrument['base_and_offload_call_components']:
        turn=component['turn']
        hybrid=next(r for r in timing['calls'] if r['turn']==turn and r['arm']=='hybrid')
        local=next(r for r in timing['calls'] if r['turn']==turn and r['arm']=='local')
        depth=hybrid['depth_before'];delta=hybrid['new_tokens']
        residual=instrumentation_residual(timing,instrument,hybrid,component)
        for variant in ('prototype_depth','bounded_undo'):
            predicted_local=delta/single.for_delta(depth,delta) if turn else integrate(lambda d:1/single.cold(d),delta,512)
            server_s=delta*(server.a+server.b*(depth if turn else delta/2))
            imp=ClientImport(variant).at_depth(delta,depth)
            ideal_wire=delta*w['kv_bytes_token']+w['f32_state_bytes']
            # Measured-wire replay is explicitly conditional on observed wire
            # and catch-up. The ideal one-state calculation remains separate.
            ideal=server_s+ideal_wire/link['downstream_bytes_per_second']+link['warm_rtt_seconds']+imp
            conditioned=server_s+hybrid['wire_bytes']/link['downstream_bytes_per_second']+link['warm_rtt_seconds']+imp+hybrid['catchup_seconds']
            result.append(dict(turn=turn,depth=depth,delta=delta,import_variant=variant,
                predicted_local_prefill_s=predicted_local,measured_local_ttft_s=local['ttft_seconds'],
                predicted_ideal_offload_s=ideal,predicted_measured_wire_catchup_s=conditioned,
                measured_ttft_s=hybrid['ttft_seconds'],instrumentation_capture_s=component['snapshot_download_seconds_sum'],
                measured_residual_s=residual,ideal_wire_bytes=ideal_wire,measured_wire_bytes=hybrid['wire_bytes'],
                predicted_import_s=imp,measured_import_s=hybrid['import_seconds'],predicted_server_s=server_s,
                measured_server_s=component['server_prefill_seconds'],measured_catchup_s=hybrid['catchup_seconds'],
                prediction_minus_residual_s=conditioned-residual,measured_gain=local['ttft_seconds']/residual,
                basis='arithmetic residual only; not production TTFT; fidelity/checkpoint unmeasured; Run13 PRO6000 workstation bulk-fit portability to Server Edition is estimated; base measured wire includes ten staged chunks'))
    return result


def preflight_rows(single,server):
    wifi=source_json('PREFLIGHT-ROUTE-PLAN.json.gz');five=source_json('5g-PREFLIGHT-ROUTE-PLAN.json.gz')
    timing=source_json('TIMING-EXTRACT.json.gz');w=config()['wire'];result=[]
    tree=ast.parse(checked(config()['policy_source']))
    policy=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Policy')
    constants={n.target.id:ast.literal_eval(n.value) for n in policy.body
               if isinstance(n,ast.AnnAssign) and n.target.id in ('eta','margin','hysteresis')}
    entry_fraction=1-constants['margin']-constants['hysteresis']
    for source,rate in ((wifi,wifi['actual_measured_downstream_bytes_s']),(five,timing['measured_link']['downstream_bytes_per_second'])):
        turn=next(r for r in source['routes']['rows'] if r['turn']==7)
        # Reproduce the old policy threshold from its two recorded link plans.
        # Difference cancels compute/import/RTT: T = C + B/downstream.
        a=next(r for r in wifi['routes']['rows'] if r['turn']==7)
        b=next(r for r in five['routes']['rows'] if r['turn']==7)
        wa=wifi['actual_measured_downstream_bytes_s'];fb=timing['measured_link']['downstream_bytes_per_second']
        rtt_a=wifi['actual_measured_warm_rtt_s'];rtt_b=timing['measured_link']['warm_rtt_seconds']
        inferred_bytes=(a['offload_seconds']-b['offload_seconds']-rtt_a+rtt_b)/(1/wa-1/fb)
        fixed=a['offload_seconds']-inferred_bytes/wa-rtt_a
        rtt=rtt_a if source is wifi else rtt_b
        entry_mb_s=inferred_bytes/(entry_fraction*turn['local_seconds']-fixed-rtt)/1e6
        replay={}
        for variant in ('prototype_depth','bounded_undo'):
            count=0
            for route in source['routes']['rows']:
                if route['outage']:continue
                call=next(r for r in timing['calls'] if r['turn']==route['turn'] and r['arm']=='hybrid')
                d=call['depth_before'];n=call['new_tokens']
                offload=n*(server.a+server.b*d)+(w['f32_state_bytes']+n*w['kv_bytes_token'])/rate+rtt+ClientImport(variant).at_depth(n,d)
                count+=offload<n/single.for_delta(d,n)
            replay[variant]=count
        result.append(dict(link='Wi-Fi' if source is wifi else '5G',downstream_mb_s=rate/1e6,
            recorded_policy_local_s=turn['local_seconds'],recorded_policy_offload_s=turn['offload_seconds'],
            recorded_connected_offloads=sum(r['offload'] for r in source['routes']['rows'] if not r['outage']),
            policy_two_plan_inferred_wire_bytes=inferred_bytes,policy_fixed_nontransfer_s=fixed,
            policy_break_even_mb_s=inferred_bytes/(turn['local_seconds']-fixed-rtt)/1e6,
            policy_entry_local_fraction=entry_fraction,policy_goodput=constants['eta'],policy_entry_threshold_mb_s=entry_mb_s,
            facts_reported_entry_threshold_mb_s=8.45,reported_threshold_reproduced=abs(entry_mb_s-8.45)<.005,
            pri31_prototype_connected_offloads=replay['prototype_depth'],pri31_bounded_undo_connected_offloads=replay['bounded_undo'],
            basis='old background-rate policy; two-plan inference cancels shared nontransfer cost and distinct RTTs; fca0fe31 margin0.1+hysteresis0.05 requires remote<0.85local for entry and reproduces FACTS8.45; new PRI31 replay uses PRO6000 fit and ideal one-state economic break-even without prototype eta/margins/catch-up'))
    return result


def append_evidence(result,c):
    single=c.r16_single
    turns=[]
    for r in single.records:
        if r['kind']=='turn':
            turns.append(dict(depth=r['level'],actual_depth=r['depth'],delta=r['delta'],prompt_n=r['prompt_n'],
                prefill_tok_s=r['prompt_n']*1000/r['prompt_ms'],decode_tok_s=r['predicted_n']*1000/r['predicted_ms'],
                canonical_depth_decode_tok_s=dict(single.decode_points)[r['level']],priority_basis='recorded_normal_priority_PRI31',
                background_priority_interim=False,source=single.source))
    add_table(result,'m3_pri31_depth',turns)
    history=[]
    for r in rows(c.inputs.measured('depth')):
        if r['kind']=='segment':
            history.append(dict(depth=r['depth'],depth_from=r['depth_from'],prefill_tok_s=r['prefill_tok_s'],
                priority_basis='historical_background_priority_throttled',background_priority_interim=True,
                basis='kit1.6.0 c21284cd; measured at background priority and throttled; historical only'))
    add_table(result,'historical_m3_prefill',history)
    add_table(result,'m5_cooled_parallel',c.r16_m5.points)
    control=dict(c.r16_m5.control,priority_basis=config()['m5']['priority_basis'],basis='same np4 configuration run-to-run sensitivity only')
    add_table(result,'m5_np4_control_sensitivity',[control])
    intercept,slope,r2=depth_fit();rec=config()['import'];probes=[]
    for depth,seconds in rec['depth_points']:
        probes.append(dict(depth=depth,delta=rec['probe_tokens'],measured_import_s=seconds,
            depth_only_ols_s=intercept+slope*depth,prototype_fitted_s=ClientImport().at_depth(rec['probe_tokens'],depth),
            bounded_undo_s=ClientImport('bounded_undo').at_depth(rec['probe_tokens'],depth),
            original_depth_blind_s=rec['fixed_s']+rec['probe_tokens']*rec['seconds_token'],
            conditional_fixed_s=ClientImport().fixed_s,retained_seconds_token=rec['seconds_token'],
            depth_slope_s_token=slope,depth_only_intercept_s=intercept,depth_only_r2=r2,supplied_token_fit_r2=rec['fit_r2'],
            basis=rec['depth_model']+' '+rec['bounded_undo']))
    add_table(result,'import_depth_fit',probes)
    add_table(result,'state_link_threshold',threshold_rows(single,c.b300))
    from .server_prefill import fit
    from .measurements_r13 import matching, package as r13_package
    a,b,_=fit(matching(r13_package('phase_a')[1],'-q27b-q4km-'))
    server=type('ServerFit',(),dict(a=a,b=b))()
    add_table(result,'growing_5g_validation',validation_rows(single,server))
    add_table(result,'measured_preflight_check',preflight_rows(single,server))


def finalize(result,scenario,inputs):
    """Qualify every inherited mixed table conservatively at table granularity."""
    interim=config()['m3_parallel']['background_priority_interim']
    for table in result['tables']:
        # These tables precede the priority discovery; retain dated numbers as
        # historical diagnostics rather than describing them as canonical.
        if table['id']=='client_import_sensitivity':
            table['name']+=' / historical background-priority diagnostics'
        table['columns'].update(background_priority_interim='bool',capacity_status='text')
        if table['id'] in ('parallel_anchors','parallel_historical_sensitivity','parallel_server_shape_sensitivity','m5_family_rates'):
            table['columns']['priority_basis']='text'
        independent=table['id'] in ('m3_pri31_depth','m5_cooled_parallel','m5_np4_control_sensitivity','import_depth_fit',
                                   'state_link_threshold','growing_5g_validation','measured_preflight_check')
        for row in table['rows']:
            row.setdefault('background_priority_interim',False if independent else interim)
            if 'priority_basis' in table['columns']:
                row.setdefault('priority_basis',config()['m5']['priority_basis'] if table['id']=='m5_family_rates' else config()['m3_parallel']['priority_basis'])
            row['capacity_status']='not a final agents/day claim' if independent else ('interim; normal-priority M3 parallel remeasurement pending' if interim else 'qualified by recorded PRI31 parallel sweep; model limits still apply')
    result['notes']=[n for n in result.get('notes',[]) if not n.startswith(('Run14 r5:','Run15 supersedes','Local prefill =','Architecture f32 rows reproduce','Exactly four R7 tables.'))]
    parallel_note='M3 parallel remains explicitly interim.' if interim else 'M3 parallel uses the data-supplied recorded PRI31 sweep.'
    result['notes'].append('Run16: M3 single-stream PRI31 step40 supersedes historical background-priority throttled anchors. Decode is mean of three n/elapsed probes per nominal depth; prefill uses nominal-depth curves at delta512/2000/10000, linear rate interpolation between deltas, endpoint holds outside them, FLOP-law extrapolation beyond249k. Cold ingestion integrates PRI31 segment midpoints. '+parallel_note+' Table-level flags conservatively qualify every inherited mixed table, including its independent cells. M5 cooled sweep uses np16/8/4, owner-reported normal priority, not recorded; interpolation and beyond-depth laws are estimates. Import fits intercept and depth slope to the four fixed539-token probes, retaining48.7us/token from the old weak marginal fit as an assumption; it recenters the marginal1.498s intercept instead of counting its depth cost twice. Bounded undo removes the fitted depth term; unimplemented sensitivity. Other Apple import portability is an estimate. f32 state157MB, bf1678.5MB; bf16 bridge unqualified. Architecture comparison uses the new M3 delta surface at its configured reference depth/portion, Qwen state157MB and config q8_0 KV34816 B/token; the old attached-script numerical reproduction remains historical. This note supersedes inherited state/rate descriptions. Growing-session numbers subtract synchronous snapshot downloads arithmetically, not measured production TTFT; checkpoint/fidelity unmeasured.')
    record_sources(inputs)
