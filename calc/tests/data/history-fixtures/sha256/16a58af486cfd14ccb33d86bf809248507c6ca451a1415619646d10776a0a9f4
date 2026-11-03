"""Run14 archive-backed parallel anchors; historical consumers remain frozen."""
import hashlib
import json
import math
from pathlib import Path

from .inputs import InputGap, ROOT
from .measurements_r13 import verified_archive, rows, cold_fit


def package(key):
    config = json.loads((Path(__file__).parent/'data/run14-measurements.json').read_text())
    if key not in config:
        raise InputGap('measurements.'+key, 'missing measured inputs')
    info = config[key]
    try:
        return verified_archive(ROOT/info['directory']/info['archive'], info['sha256'])
    except OSError as exc:
        raise InputGap('measurements.'+key, 'missing measured inputs') from exc


def record_packages(inputs):
    config = json.loads((Path(__file__).parent/'data/run14-measurements.json').read_text())
    for key, info in config.items():
        manifest, payload = package(key)
        path = str(Path(info['directory'])/info['archive'])
        provenance = dict(kind='measured', package=manifest['kit']+' '+manifest['kit_version'], sha256=info['sha256'])
        inputs.files[path] = dict(path=path, sha256=info['sha256'], provenance=provenance)
        for name, content in payload.items():
            source = path+'::'+name
            inputs.files[source] = dict(path=source, sha256=hashlib.sha256(content).hexdigest(), provenance=provenance)
    from .run14_r5 import evidence
    info=evidence()['cuda_pr9']
    for path in ('calc/hybridcalc/data/run14-r5.json',info['path']):
        digest=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
        inputs.files[path]=dict(path=path,sha256=digest,provenance=dict(kind='measured',package='Owner r5 FACTS snapshot / PR9 CUDA imports; assumptions labelled in data',sha256=digest))


def one_file(payload, fragment, suffix='.jsonl'):
    names = [name for name in payload if fragment in name and name.endswith(suffix)]
    if len(names) != 1:
        raise InputGap('measurements', 'expected one payload: '+fragment)
    return names[0], payload[names[0]]


def aggregate_round(row):
    """The sweep times n-1 decode intervals, excluding the first generated token."""
    requests = row.get('requests', [])
    if (row.get('valid') is not True or row.get('errors') or not row.get('restore_reused') or
            len(requests) != row['streams'] or
            any(r.get('predicted_n', 0) <= 1 or r.get('predicted_ms', 0) <= 0 for r in requests)):
        raise InputGap('measurements.parallel', 'invalid or unrestored parallel observation')
    return sum(r['predicted_n']-1 for r in requests)/(max(r['predicted_ms'] for r in requests)/1000)


class ParallelAnchors:
    """Measured lookup with an explicitly supplied Run13 depth law outside it."""
    def __init__(self, normalized, depth_law=None):
        self.depth_law = depth_law
        p = normalized['parallel']
        frozen = p['frozen_v11_row']
        self.points = [dict(depth=frozen['depth'], streams=k,
                            aggregate_tok_s=p['baseline_native_decode_tok_s']*gain,
                            source='data/measurements/ivmbp-2026-10-30/qwen27b-bench/normalized-results.json :: parallel.frozen_v11_row',
                            condition='frozen measured 32k interval anchor', conservative=False)
                       for k, gain in ((1, 1), (frozen['streams'], p['normalized_decode_interval_gain']))]
        mac = package('mac')[1]
        control = package('control')[1]
        for payload, fragment, condition, only in (
                (mac, '-depth64k-', 'step55; after fill; q8_0 KV; FA on', None),
                (control, '-maxctx131k-', 'restored-context control; preferred at 128k; q8_0 KV; FA on', None),
                (mac, '-depth128k-', 'after a long prefill, lower bound', {12}),
                (mac, '-maxctx260k-', 'step56; restored context; q8_0 KV; FA on', None),
                (mac, '-maxctx1040k-', 'step56; restored context; YaRN scale4; original context262144', None)):
            name, content = one_file(payload, fragment)
            for row in rows(content):
                if row.get('kind') == 'round' and (only is None or row['streams'] in only):
                    self.points.append(dict(depth=row['depth'], streams=row['streams'],
                                            aggregate_tok_s=aggregate_round(row), source=name,
                                            condition=condition, conservative=only is not None))
        self.points.sort(key=lambda p: (p['streams'], p['depth']))

    def measured_lookup(self, streams, depth):
        if type(streams) is not int or streams < 1 or not math.isfinite(depth) or depth < 0:
            raise InputGap('measurements.parallel', 'positive integer streams and finite nonnegative depth required')
        points = [p for p in self.points if p['streams'] == streams]
        if not points:
            raise InputGap('measurements.parallel', 'unmeasured stream count: '+str(streams))
        if depth > points[-1]['depth']:
            raise InputGap('measurements.parallel', 'depth exceeds deepest measured anchor for {} streams: {} > {}'.format(streams, depth, points[-1]['depth']))
        if depth <= points[0]['depth']:
            p = points[0]
            return dict(aggregate_tok_s=p['aggregate_tok_s'], conservative=depth < p['depth'] or p['conservative'],
                        sources=p['source'], condition=p['condition'])
        for a, b in zip(points, points[1:]):
            if depth <= b['depth']:
                fraction = (depth-a['depth'])/(b['depth']-a['depth'])
                return dict(aggregate_tok_s=a['aggregate_tok_s']+fraction*(b['aggregate_tok_s']-a['aggregate_tok_s']),
                            conservative=b['conservative'] or (a['conservative'] and fraction < 1),
                            sources=b['source'] if fraction == 1 else a['source']+'; '+b['source'],
                            condition=b['condition'] if fraction == 1 else a['condition']+'; '+b['condition'])

    def lookup(self, streams, depth):
        if type(streams) is not int or streams < 1 or not math.isfinite(depth) or depth < 0:
            raise InputGap('measurements.parallel', 'positive integer streams and finite nonnegative depth required')
        counts = sorted({p['streams'] for p in self.points})
        if streams > counts[-1]:
            raise InputGap('measurements.parallel', 'stream count above largest measured count')
        count = max(k for k in counts if k <= streams)
        points = [p for p in self.points if p['streams'] == count]
        modelled = depth > points[-1]['depth']
        if modelled:
            if self.depth_law is None:
                raise InputGap('measurements.parallel', 'Run13 depth law unavailable')
            anchor = points[-1]
            probe = self.measured_lookup(count, anchor['depth'])
            probe['aggregate_tok_s'] *= self.depth_law(count, depth)/self.depth_law(count, anchor['depth'])
            probe['condition'] += '; modelled beyond measured depth'
        else:
            probe = self.measured_lookup(count, depth)
        zones = dict(shallow=depth < points[0]['depth'], depth_modelled=modelled,
                     count_conservative=count != streams,
                     measured_lower_bound=probe['conservative'] and depth >= points[0]['depth'])
        zones['measured'] = not any(zones.values())
        probe.update(zones=zones, measured_streams=count,
                     conservative=probe['conservative'] or count != streams)
        if count != streams:
            probe['condition'] += '; conservative nearest lower measured count'
        return probe

    def decode(self, streams, depth):
        return self.lookup(streams, depth)['aggregate_tok_s']/streams


def day_bounds(calls, steps, streams, memory, decoder, hours, measured_only=False):
    """Same two throughput bounds as paper.throughput, exposing their components."""
    device = occupied = agent = 0.0
    admitted = []
    conservative = False
    zones = {key: [0, 0.0] for key in ('measured','shallow','depth_modelled','count_conservative','measured_lower_bound')}
    decode_total = 0.0
    for (d, n, o, tool), (wait, local, wire, offload) in zip(calls, steps):
        k = min(streams, memory(d+n))
        if k < 1:
            raise InputGap('hardware.client.memory', 'no decode stream fits this call')
        probe = decoder.lookup(k, d+n)
        if measured_only:
            decoder.measured_lookup(k, d+n)
        r = probe['aggregate_tok_s']/k
        conservative = conservative or probe['conservative']
        admitted.append(k)
        decode_total += o/(k*r)
        for key, flagged in probe['zones'].items():
            if flagged:
                zones[key][0] += 1
                zones[key][1] += o/(k*r)
        device += local+o/(k*r)
        agent += wait+o/r+tool
        occupied += (wait+o/r+tool)/k
    count = len(calls)
    if not count or max(device, occupied) <= 0:
        raise InputGap('workload', 'positive service time required')
    return dict(calls_day=hours*3600/(max(device, occupied)/count),
                binding='device' if device >= occupied else 'agent cycle',
                mean_agent_s=agent/count, device_s=device/count, cycle_s=occupied/count,
                min_streams=min(admitted), max_streams=max(admitted), conservative=conservative,
                zones={key:dict(calls=count_/count, decode_time=seconds/decode_total if decode_total else 0.0)
                       for key,(count_,seconds) in zones.items()})


def agents_table(c, ceiling=None):
    """Never silently drop unmeasured calls from the full supported-memory mix."""
    from .paper_tables import end_memory
    result = []
    for mbit in (1000, 300):
        name = 'agents.link.'+str(mbit)
        if name not in c.cache:
            c.cache[name] = c.label(name, mbit*1e6)
        link = c.cache[name]
        cl = c.client('m3max', link, 'agents'+str(mbit))
        calls = c.g.resolve(cl['matched']).value
        local_steps = c.g.resolve(cl['local_steps']).value
        hybrid_steps = c.g.resolve(cl['steps']).value
        if any(v is None for v in (calls, local_steps, hybrid_steps)):
            raise InputGap('client_agents_day', 'upstream policy unavailable')
        indices = [i for i, (d,n,o,t) in enumerate(calls) if ceiling is None or d+n <= ceiling]
        subset = [calls[i] for i in indices]
        mem = end_memory(subset, c.g.resolve(cl['memory']).value)
        for agents in (1, 2, 4, 6, 8, 12, 16):
            row = dict(client='M3 Max 128 GB', link_mbit=mbit, agents=agents,
                       calls=len(subset), depth_ceiling='full mix' if ceiling is None else str(ceiling))
            try:
                local = day_bounds(subset, [local_steps[i] for i in indices], agents, mem, c.parallel, c.inputs.get('paper_tables.hours'), ceiling is not None)
                hybrid = day_bounds(subset, [hybrid_steps[i] for i in indices], agents, mem, c.parallel, c.inputs.get('paper_tables.hours'), ceiling is not None)
                chunk = c.inputs.get('workload.chunk_calls')
                row.update(local_sessions_day=local['calls_day']/chunk, hybrid_sessions_day=hybrid['calls_day']/chunk,
                           gain=hybrid['calls_day']/local['calls_day'], local_bound=local['binding'], hybrid_bound=hybrid['binding'],
                           local_agent_s=local['mean_agent_s'], hybrid_agent_s=hybrid['mean_agent_s'],
                           admitted_streams='{}..{}'.format(local['min_streams'],local['max_streams']),
                           coverage='; '.join(key for key,v in local['zones'].items() if v['calls']))
                for key,value in local['zones'].items():
                    row[key+'_call_share']=value['calls']
                    row[key+'_decode_time_share']=value['decode_time']
            except InputGap as exc:
                alarm = dict(alarm=[exc.alarm()])
                row.update({key: alarm for key in ('local_sessions_day','hybrid_sessions_day','gain','local_bound','hybrid_bound','local_agent_s','hybrid_agent_s')})
                counts = [min(agents, mem(d+n)) for d,n,o,t in subset]
                row.update(admitted_streams='{}..{}'.format(min(counts),max(counts)), coverage='gap: '+exc.reason)
                for key in ('measured','shallow','depth_modelled','count_conservative','measured_lower_bound'):
                    for metric in ('call_share','decode_time_share'):row[key+'_'+metric]=alarm
            result.append(row)
    return result


def raw_table(result, key, records, units):
    alarms = [a for row in records for value in row.values() if isinstance(value,dict) and 'alarm' in value for a in value['alarm']]
    result['tables'].append(dict(id=key, name=key, columns=units, rows=records, alarms=alarms))
    from .metrics import unique
    result['alarms'] = unique(result['alarms']+alarms)
    result['computed_metrics'] += sum(type(v) in (int,float) for row in records for v in row.values())


def append_parallel_tables(result, c):
    from .run14_r5 import append_checks
    append_checks(result,c)
    raw_table(result, 'parallel_anchors', c.parallel.points,
              dict(depth='token',streams='stream',aggregate_tok_s='token/s',source='text',condition='text',conservative='bool'))
    units = dict(client='text',link_mbit='Mbit/s',agents='agent',calls='call',depth_ceiling='text',
                 local_sessions_day='session/day',hybrid_sessions_day='session/day',gain='1',local_bound='text',hybrid_bound='text',
                 local_agent_s='s/call including tool time',hybrid_agent_s='s/call including tool time',admitted_streams='text',coverage='text')
    units.update({key+'_'+metric:'1' for key in ('measured','shallow','depth_modelled','count_conservative','measured_lower_bound')
                  for metric in ('call_share','decode_time_share')})
    raw_table(result, 'client_agents_day', agents_table(c), units)
    raw_table(result, 'client_agents_day_bounded', agents_table(c,65552)+agents_table(c,131088), units)


class B300Measurements:
    """Measured kit1.6.5 envelope; missing data never falls back to peak scaling."""
    def __init__(self):
        from .server_prefill import fit
        manifest, payload = package('b300')
        if manifest['kit_version'] != '1.6.5':
            raise InputGap('measurements.b300','expected measured kit1.6.5 inputs')
        self.source, content = one_file(payload, '-q27b-q4km-')
        self.rows = rows(content)
        self.a, self.b, self.bulk = fit(self.rows)
        self.decode_curve = [(r['depth']+r['prompt_n'],r['predicted_n']/(r['predicted_ms']/1000))
                             for r in self.rows if r.get('kind')=='turn' and r['delta']==2000]
        if len(self.decode_curve) != 6:
            raise InputGap('measurements.b300','missing measured decode inputs')
        self.tuning_source, content = one_file(payload,'sweep-status','.json')
        self.tuning = json.loads(content)
        self.vllm_source, content = one_file(payload,'/vllm.json','.json')
        self.vllm = [d for d in json.loads(content) if d.get('name') in ('fp8-default','fp8-kv','fp8-large-batch')]
        if {d['name'] for d in self.vllm} != {'fp8-default','fp8-kv','fp8-large-batch'}:
            raise InputGap('measurements.b300','missing measured FP8 inputs')

    def compute(self, model, precision):
        from .performance import flop
        if precision != 'Q4':
            raise InputGap('owners.server_precision','B300 measured llama.cpp inputs require Q4/q8_0')
        return lambda d:flop(model,d)/(self.a+self.b*d)

    def decode(self, depth):
        from .performance import Curve
        model=dict(base_flop=54e9,attention_slope=393216,sparse_slope=0,sparse_cap=0,context_limit=2e6)
        return Curve(model,self.decode_curve).rate(depth)


def b300_vllm_rates(document):
    """Useful and processed rates retain measured cache-block geometry per KV."""
    output=[]
    for row in document['B']:
        probe=row['measurement'];depth=row['depth'];delta=row['delta']
        block=row['cache_block_tokens'];cached=probe['cached_tokens'];ttft=probe['ttft_s']
        if (type(block) is not int or block <= 0 or not 0 <= cached <= depth or cached % block or
                cached != (depth//block)*block or not math.isfinite(ttft) or ttft <= 0):
            raise InputGap('measurements.b300.vllm','invalid measured cached-delta inputs')
        output.append(dict(depth=depth,delta=delta,cached=cached,processed=depth+delta-cached,
                           cache_block_tokens=block,ttft_s=ttft,processed_tok_s=(depth+delta-cached)/ttft,delta_tok_s=delta/ttft))
    if not output:
        raise InputGap('measurements.b300.vllm','missing measured cached-delta inputs')
    return output


def append_hardware_tables(result,c):
    import copy
    from .paper_tables import Context, client_table
    # Keep the old M3-based M5 family as an explicitly named sensitivity,
    # using the same new server and workload rather than mixing runs.
    scenario=dict(c.scenario,m5_m3_sensitivity=True)
    scenario['capacity_clients']=['m5max','ultra96','ultra256']
    sensitivity=Context(scenario,copy.deepcopy(c.inputs))
    client_table(sensitivity)
    table=sensitivity.g.result('M3-based sensitivity')['tables'][0]
    for row in table['rows']:
        row['basis']='old M3-based compute/bandwidth estimate; sensitivity only'
    raw_table(result,'client_m5_m3_sensitivity',table['rows'],dict(table['columns'],basis='text'))
    rates=[]
    for key in ('m5max64','m5max','ultra96','ultra256'):
        model=c.model('qwen27');local=c.g.resolve(c.local_rate(key,model)).value
        client=c.client(key,'hardware.links.wan.bandwidth','hardware-rates')
        decoder=c.g.resolve(client['decoder']).value
        for depth in (16000,32000,50000,65536,100000,131072,150000,200000,249000):
            rates.append(dict(client=key,depth=depth,prefill_tok_s=local(depth),single_tok_s=decoder(1,depth),
                              aggregate4_tok_s=4*decoder(4,depth),
                              basis='measured M5 Max SoC' if key.startswith('m5max') else 'estimate scaled from measured M5 Max compute/bandwidth'))
    raw_table(result,'m5_family_rates',rates,dict(client='text',depth='token',prefill_tok_s='token/s',single_tok_s='token/s',aggregate4_tok_s='token/s',basis='text'))
    append_b300_tables(result,c.b300)
    segments=[]
    for client,rows_ in (('M3 Max',rows(c.inputs.measured('depth'))),('M5 Max',c.measured_m5.depth)):
        for r in rows_:
            if r['kind']=='segment':
                segments.append(dict(client=client,depth_from=r['depth_from'],depth=r['depth'],prefill_tok_s=r['prefill_tok_s']))
    raw_table(result,'client_prefill_segments',segments,dict(client='text',depth_from='token',depth='token',prefill_tok_s='token/s'))
    latency_examples(result,c)


def latency_examples(result,c):
    """Prefill wait examples, excluding decode/tool time, with explicit coordinates."""
    from .paper_tables import integrate
    from .performance import transfer
    local=c.g.resolve(c.local_rate('m3max',c.model('qwen27'))).value
    wire=dict(bandwidth=1e9,goodput=c.inputs.get('hardware.links.wan.goodput'),latency=c.inputs.get('hardware.links.wan.latency'))
    kv=c.inputs.get('owners.models.qwen27.kv');state=c.g.resolve(c.state).value
    records=[]
    for kind,depth,delta in (('per-call',16000,2000),('per-call',131072,2000),('per-call',249000,2000),
                             ('large tool output',131072,10000),('large tool output',249000,10000),
                             ('first fill',131072,131072),('first fill',249000,249000)):
        if kind=='first fill':
            ls=integrate(lambda d:1/local(d),delta,512)
            server=c.b300.a*delta+c.b300.b*delta*delta/2
        else:
            ls=delta/local(depth)
            server=delta*(c.b300.a+c.b300.b*depth)
        imp=c.client_import()(delta)
        remote=server+transfer(delta,kv,state,wire)+imp
        records.append(dict(kind=kind,depth=0 if kind=='first fill' else depth,delta=delta,link_mbit=1000,
                            local_prefill_s=ls,server_prefill_s=server,transfer_s=remote-server-imp,import_s=imp,
                            hybrid_wait_s=min(ls,remote),prefill_wait_gain=ls/min(ls,remote)))
    raw_table(result,'latency_examples',records,dict(kind='text',depth='token',delta='token',link_mbit='Mbit/s',local_prefill_s='s',server_prefill_s='s',transfer_s='s',import_s='s',hybrid_wait_s='s',prefill_wait_gain='1'))


def append_b300_tables(result,b):
    raw_table(result,'b300_bulk',[dict(p,rate=1/p['seconds_token'],fitted_rate=1/(b.a+b.b*p['depth']),source=b.source) for p in b.bulk],
              dict(depth='token',actual_depth='token',delta='token',seconds_token='s/token',rate='token/s',fitted_rate='token/s',source='text'))
    decoded=[dict(depth=d,decode_tok_s=r,source=b.source) for d,r in b.decode_curve]
    raw_table(result,'b300_decode',decoded,dict(depth='token',decode_tok_s='token/s',source='text'))
    raw_table(result,'b300_tuning',[dict(tuning_status=b.tuning['status'],reason=b.tuning['reason'],
              pinned_commit=b.tuning['pinned_commit'],new_commit=b.tuning['new_commit'],source=b.tuning_source)],
              dict(tuning_status='text',reason='text',pinned_commit='text',new_commit='text',source='text'))
    cold=[];cached=[]
    label='server-only rate; hybrid transfer through the vLLM bridge is in qualification'
    for doc in b.vllm:
        a,slope=cold_fit(doc)
        for r in doc['A']:
            n=r['length']
            cold.append(dict(option=doc['name'],kv=doc['kv'],depth=n,repetition=r['repetition'],ttft_s=r['ttft_s'],
                             fitted_s=a*n+slope*n*n/2,a=a,b=slope,rate=n/r['ttft_s'],server_only=1,client_bridge=0,qualification=label))
        for r in b300_vllm_rates(doc):
            cached.append(dict(option=doc['name'],kv=doc['kv'],**r,server_only=1,client_bridge=0,qualification=label))
    raw_table(result,'b300_vllm_cold',cold,dict(option='text',kv='text',depth='token',repetition='index',ttft_s='s',fitted_s='s',a='s/token',b='s/token/depth-token',rate='token/s',server_only='bool',client_bridge='bool',qualification='text'))
    raw_table(result,'b300_vllm_cached',cached,dict(option='text',kv='text',depth='token',delta='token',cached='token',processed='token',cache_block_tokens='token',ttft_s='s',processed_tok_s='token/s',delta_tok_s='token/s',server_only='bool',client_bridge='bool',qualification='text'))


def calculate(scenario,inputs):
    """Server-only options in the same raw/fit form as run13."""
    from .measurements_r13 import calculate as previous
    result=previous(scenario,inputs)
    result["notes"][0]="PRO 6000 run13 server-only controls are retained. B300 FP8 both KV settings are measured; NVFP4 is excluded. M5 step57 remains excluded for swap."
    append_b300_tables(result,B300Measurements())
    return result
