"""Run17 architecture arithmetic; SWA transport/import remain explicit estimates."""
import hashlib
import json
from pathlib import Path

from .inputs import InputGap, ROOT
from .measurements_r13 import verified_archive, rows
from .measurements_r14 import one_file
from . import measurements_r16 as r16

CONFIG = Path(__file__).parent/'data/run17-measurements.json'
MODELS = ('qwen27', 'glimmer30', 'gemma31')
DEPTHS = (32000, 64000, 100000)
DELTAS = (512, 2343, 10000)


def config():
    return json.loads(CONFIG.read_text())


def package(key, cfg=None):
    info = (cfg or config())['sources'][key]
    return verified_archive(ROOT/info['path'], info['sha256'])


def geometry(model, payload=None):
    payload = package(model+'_server')[1] if payload is None else payload
    g = json.loads(payload['results/model-geometry.json'])
    expected = {'qwen27': (34816, 0, 0, 156893184, 262144),
                'glimmer30': (7072, 21216, 2048, 0, 131072),
                'gemma31': (43520, 435200, 1024, 0, 262144)}[model]
    keys = ('kv_bytes_per_token', 'window_bytes_per_token', 'sliding_window',
            'recurrent_tensor_bytes', 'native_context')
    if g.get('model') != model or tuple(g.get(k) for k in keys) != expected:
        raise InputGap('run17.geometry', 'model geometry disagrees with measured contract')
    if g['sliding_window_bytes'] != g['window_bytes_per_token']*g['sliding_window']:
        raise InputGap('run17.geometry', 'window byte product mismatch')
    return g


def offload_bytes(g, delta, depth, state_format='f32'):
    """Final-range full-attention KV plus complete live window and recurrent tensors.

    Protocol framing and slot bookkeeping are excluded. Native context counts
    prefix+delta; this estimates one ideal final import, not chunked transport.
    """
    for k,v in (('delta',delta),('depth',depth)):
        r16.nonnegative(v,k)
        if int(v) != v:
            raise InputGap('run17.geometry', 'integer token coordinates required')
    if depth+delta > g['native_context']:
        raise InputGap('run17.geometry', 'native context exceeded')
    if state_format not in ('f32','bf16') or (state_format=='bf16' and g['model']!='qwen27'):
        raise InputGap('run17.geometry', 'unsupported state format')
    state = g['recurrent_tensor_bytes']/(2 if state_format=='bf16' else 1)
    return int(delta*g['kv_bytes_per_token'] +
               min(depth+delta,g['sliding_window'])*g['window_bytes_per_token'] + state)


def geometry_rows(model, payload=None):
    payload = package(model+'_server')[1] if payload is None else payload
    g = geometry(model,payload)
    if model=='qwen27':
        return []
    _,content = one_file(payload,'delta-geometry-', '.json')
    d = json.loads(content)
    # Full sequence serialization has 16 B/position of token/cache metadata.
    # Its fixed metadata is distinct from allocated slot_fixed_bytes and wire.
    metadata_fixed = {'glimmer30':25900, 'gemma31':13804}[model]
    samples = d.get('samples',[])
    if (d.get('status')!='measured' or d.get('skipped') or
            [r['depth'] for r in samples] != [16000,40000,64000] or
            d.get('bytes_per_token')!=g['kv_bytes_per_token']+16 or
            d.get('fixed_bytes')!=g['sliding_window_bytes']+metadata_fixed):
        raise InputGap('run17.geometry', 'complete sequence-save geometry required')
    result=[]
    for sample in samples:
        depth=sample['depth']; tensors=offload_bytes(g,depth,0)
        predicted=tensors+16*depth+metadata_fixed
        if predicted!=sample['bytes']:
            raise InputGap('run17.geometry','sequence-save byte reconciliation failed')
        result.append(dict(model=model,depth=depth,full_kv_bytes_token=g['kv_bytes_per_token'],
            window_bytes_position=g['window_bytes_per_token'],window_positions=g['sliding_window'],
            window_bytes=g['sliding_window_bytes'],recurrent_bytes=g['recurrent_tensor_bytes'],
            estimated_tensor_bytes=tensors,sequence_metadata_bytes=16*depth+metadata_fixed,
            predicted_sequence_bytes=predicted,measured_sequence_bytes=sample['bytes'],residual_bytes=0,
            allocated_slot_fixed_bytes=g['slot_fixed_bytes'],
            basis='Full sequence save reconciliation; not measured prototype delta transport'))
    return result


class Surface:
    """Bounded bilinear rates at nominal depths and requested deltas."""
    def __init__(self, model, role, cfg=None, evidence=None):
        cfg=cfg or config();self.model=model
        info=cfg['mac'][model] if role=='mac' else None
        key=info['source'] if info else model+'_server'
        manifest,payload = evidence if evidence is not None else package(key,cfg)
        self.interim=False
        if info:
            if info['mode']=='verified_pri31':
                if info['background_priority_interim'] is not False or info['priority_basis']!='recorded_normal_priority_PRI31':
                    raise InputGap('run17.priority','replacement must record PRI31')
                r16.normal_priority(manifest,payload)
            elif info['mode']=='background_interim':
                if info['background_priority_interim'] is not True or info['priority_basis']!='historical_background_priority_throttled':
                    raise InputGap('run17.priority','background rates cannot claim final')
                self.interim=True
            else:
                raise InputGap('run17.priority','unknown Mac admission mode')
        model_label='q27b' if model=='qwen27' else model
        self.source,content=one_file(payload,'-'+model_label+'-')
        records=rows(content);self.records=records;self.turns=[r for r in records if r['kind']=='turn']
        self.depths=(16000,50000,100000,118000) if model=='glimmer30' else r16.DEPTHS
        meta=[r for r in records if r['kind']=='meta']
        if (len(meta)!=1 or '-'+model_label+'-' not in meta[0].get('label','') or
                (role=='mac' and meta[0].get('machdep.cpu.brand_string')!='Apple M3 Max')):
            raise InputGap('run17.rates','model identity mismatch')
        expected={(d,n) for d in self.depths for n in r16.DELTAS}
        if len(self.turns)!=len(expected) or {(r['level'],r['delta']) for r in self.turns}!=expected:
            raise InputGap('run17.rates','complete depth/delta grid required')
        for r in self.turns:
            if (r.get('reread') is not False or r.get('cache_reused') is not True or
                r.get('truncated') is not False or r.get('gen_tokens_exact') is not True or
                r.get('prompt_n') not in (r['delta'],r['delta']+1) or r.get('predicted_n')!=128 or
                r.get('depth')!=r['level']+{512:0,2000:640,10000:2768}[r['delta']]):
                raise InputGap('run17.rates','exact reused delta/framing required')
            for k in ('prompt_ms','predicted_ms'):
                r16.nonnegative(r.get(k),k)
                if r[k]==0:raise InputGap('run17.rates','positive timings required')
        self.rates={(r['level'],r['delta']):r['prompt_n']*1000/r['prompt_ms'] for r in self.turns}

    def for_delta(self, depth, delta):
        r16.nonnegative(depth,'depth');r16.nonnegative(delta,'delta')
        if not self.depths[0]<=depth<=self.depths[-1] or not 512<=delta<=10000:
            raise InputGap('run17.rates','outside measured depth/delta grid')
        def interp(xs,x,fn):
            for a,b in zip(xs,xs[1:]):
                if a<=x<=b:return fn(a)+(fn(b)-fn(a))*(x-a)/(b-a)
        return interp(self.depths,depth,lambda d:interp(r16.DELTAS,delta,lambda n:self.rates[d,n]))


def threshold_rows(cfg=None):
    cfg=cfg or config();out=[];qwen=r16.SingleStream();rtt=r16.config()['wire']['threshold_rtt_s']
    for model in MODELS:
        g=geometry(model);server=Surface(model,'server',cfg)
        local=qwen if model=='qwen27' else Surface(model,'mac',cfg)
        for fmt in (('f32','bf16') if model=='qwen27' else ('f32',)):
            for depth in DEPTHS:
                for delta in DELTAS:
                    size=offload_bytes(g,delta,depth,fmt)
                    ls=delta/local.for_delta(depth,delta);ss=delta/server.for_delta(depth,delta)
                    imp=r16.ClientImport().at_depth(delta,depth)
                    threshold=r16.link_threshold(ls,ss,imp,size,rtt)
                    out.append(dict(model=model,state_format=fmt,depth=depth,delta=delta,wire_bytes=size,
                        local_prefill_s=ls,server_prefill_s=ss,import_s=imp,rtt_s=rtt,
                        break_even_downstream_mb_s=threshold/1e6,break_even_downstream_mbit_s=threshold*8/1e6,
                        background_priority_interim=getattr(local,'interim',False),
                        state_quality='pending measured quality of dev-a r38' if fmt=='bf16' else 'f32 reference',
                        import_assumption=cfg['import_assumption'] if model!='qwen27' else 'run16 prototype_depth',
                        basis='ideal tensor payload; measured kit1.6.5 PRO6000 rates; bilinear nominal-depth rates; no framing/catch-up'))
    return out


def extrapolation_rows():
    qwen=r16.SingleStream();server=Surface('qwen27','server');depth=100000;delta=2343
    ls=delta/qwen.for_delta(depth,delta);ss=delta/server.for_delta(depth,delta)
    imp=r16.ClientImport().at_depth(delta,depth);rtt=r16.config()['wire']['threshold_rtt_s']
    return [dict(fixed_mb=s,kv_kib_token=k,depth=depth,delta=delta,wire_bytes=s*1e6+k*1024*delta,
        local_prefill_s=ls,server_prefill_s=ss,import_s=imp,rtt_s=rtt,
        break_even_downstream_mb_s=r16.link_threshold(ls,ss,imp,s*1e6+k*1024*delta,rtt)/1e6,
        basis='architecture extrapolation at Qwen rates and unchanged Qwen import time; not a model claim; MB decimal; KiB binary')
        for s in (0,10,50,78.5,157) for k in (2,7,34)]


def sensitivity_rows():
    out=[];g=geometry('qwen27')
    for depth in DEPTHS:
        for delta in DELTAS:
            for fmt in ('f32','bf16'):
                size=offload_bytes(g,delta,depth,fmt)
                for speed in (5.19,9.75,125):
                    out.append(dict(depth=depth,delta=delta,state_format=fmt,wire_bytes=size,
                        downstream_mb_s=speed,transfer_s=size/(speed*1e6),egress_usd_per_gb=0.02,
                        egress_usd=size/1e9*.02,
                        state_quality='pending measured quality of dev-a r38' if fmt=='bf16' else 'f32 reference',
                        basis='per ideal offload; decimal GB; transfer excludes RTT/import; illustrative egress tariff'))
    return out


def rate_rows():
    result=[]
    for model in MODELS:
        for role in (('server',) if model=='qwen27' else ('server','mac')):
            surface=Surface(model,role)
            for r in surface.turns:
                result.append(dict(model=model,role=role,depth=r['level'],actual_depth=r['depth'],delta=r['delta'],
                    prompt_n=r['prompt_n'],prefill_tok_s=r['prompt_n']*1000/r['prompt_ms'],
                    decode_tok_s=r['predicted_n']*1000/r['predicted_ms'],
                    background_priority_interim=surface.interim,source=surface.source,
                    basis='raw kit nominal-depth delta probes; decode n/elapsed; no rereads'))
    return result


def record_sources(inputs):
    for key,info in config()['sources'].items():
        _,payload=package(key)
        inputs.files[info['path']]=dict(info,provenance=dict(kind='measured',package='Run17 '+key))
        for n,b in payload.items():
            path=info['path']+'::'+n
            inputs.files[path]=dict(path=path,sha256=hashlib.sha256(b).hexdigest())
    name=str(CONFIG.relative_to(ROOT))
    inputs.files[name]=dict(path=name,sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest())


def calculate(scenario,inputs):
    result=dict(scenario=scenario['name'],tables=[],sources=[],files=[],alarms=[],notes=[],computed_metrics=0,export_namespace='r17_architecture')
    for key,data in (('sliding_geometry',sum((geometry_rows(m) for m in MODELS),[])),
                     ('architecture_link_threshold',threshold_rows()),
                     ('architecture_extrapolation',extrapolation_rows()),
                     ('bf16_transfer_egress',sensitivity_rows()),('measured_model_rates',rate_rows())):
        r16.add_table(result,key,data)
    units={'fixed_mb':'MB (1000000 B)','kv_kib_token':'KiB/token (1024 B/KiB)',
           'full_kv_bytes_token':'B/token','window_bytes_position':'B/position','window_positions':'position',
           'allocated_slot_fixed_bytes':'B','break_even_downstream_mbit_s':'Mbit/s',
           'egress_usd':'USD','egress_usd_per_gb':'USD/GB (1000000000 B)'}
    for table in result['tables']:
        table['columns'].update({k:v for k,v in units.items() if k in table['columns']})
    record_sources(inputs)
    return result


def configure_context(c):
    # R16b remains selected by the original run16 data-only interface.
    if config()['qwen_state_bytes']!=156893184:
        raise InputGap('run17.state','exact measured recurrent tensor bytes required')
    fmt=c.scenario.get('wire_state_format','f32')
    if fmt not in ('f32','bf16'):raise InputGap('run17.state','unknown wire state format')
    c.wire_state=c.label('r17.wire_state',config()['qwen_state_bytes']/(2 if fmt=='bf16' else 1))


def finalize(result,scenario,inputs):
    fmt=scenario.get('wire_state_format','f32')
    # Preserve the resident f32 footprint, decode and import assumptions in both
    # scenarios. Only wire state changes; routing/volume/cost are recomputed.
    for table in result['tables']:
        table['columns'].update(wire_state_format='text',state_quality='text')
        for row in table['rows']:
            row.update(wire_state_format=fmt,state_quality='pending measured quality of dev-a r38' if fmt=='bf16' else 'f32 reference')
    result['notes'].append('Run17 economics sensitivity: exact recurrent tensors156893184 B; bf16 wire half78446592 B pending measured quality of dev-a r38. Resident state/decode/import unchanged. R16 economics server portfolio retained for a paired comparison; architecture thresholds separately use kit1.6.5 PRO6000 rates. Inherited R16 rounded157/78.5MB diagnostic tables are historical controls, not Run17 geometry.')
    record_sources(inputs)
