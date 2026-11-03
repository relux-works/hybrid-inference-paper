"""Offline archive custody and admitted run-13 measurement reductions."""
import hashlib
import json
import math
import tarfile
from pathlib import Path, PurePosixPath
from .inputs import InputGap, ROOT


def verified_archive(path, expected):
    """Validate everything before returning any payload; never extract tar paths."""
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
        raise InputGap('measurements.archive', 'archive sha256 mismatch')
    with tarfile.open(path) as archive:
        members = {}
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if member.name.startswith('/') or '..' in parts or member.issym() or member.islnk():
                raise InputGap('measurements.archive', 'unsafe archive member')
            if member.isfile():
                if member.name in members:
                    raise InputGap('measurements.archive', 'duplicate archive member')
                members[member.name] = archive.extractfile(member).read()
        manifest = json.loads(members['results/MANIFEST.json'])
        payload = {'results/MANIFEST.json': members['results/MANIFEST.json']}
        for name, info in manifest['files'].items():
            key = 'results/' + name
            if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:
                raise InputGap('measurements.archive', 'unsafe manifest member')
            content = members.get(key)
            if content is None or len(content) != info['bytes'] or hashlib.sha256(content).hexdigest() != info['sha256']:
                raise InputGap('measurements.archive', 'manifest mismatch: ' + name)
            payload[key] = content
        # AppleDouble metadata is transport-only and never an admitted payload.
        extra = set(members) - set(payload)
        if any(not PurePosixPath(n).name.startswith('._') for n in extra):
            raise InputGap('measurements.archive', 'unmanifested payload')
        return manifest, payload


def package(key):
    config = json.loads((Path(__file__).parent/'data/run13-measurements.json').read_text())[key]
    root = ROOT/config['directory']
    manifest, payload = verified_archive(root/config['archive'], config['sha256'])
    # Imported files must remain identical to the verified archive.
    for name, content in payload.items():
        if (root/name).read_bytes() != content:
            raise InputGap('measurements.'+key, 'imported payload differs: '+name)
    return manifest, payload


def record_packages(inputs):
    config = json.loads((Path(__file__).parent/'data/run13-measurements.json').read_text())
    for key, info in config.items():
        manifest, _ = package(key)
        for name in (info['archive'], 'results/MANIFEST.json'):
            path = str(Path(info['directory'])/name)
            inputs.files[path] = dict(path=path,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                                     provenance=dict(kind='measured',package=manifest['kit']+' '+manifest['kit_version'],sha256=info['sha256']))


def rows(content):
    return [json.loads(s) for s in content.splitlines()]


def matching(payload, fragment, suffix='.jsonl'):
    names = [n for n in payload if fragment in n and n.endswith(suffix)]
    if len(names) != 1:
        raise InputGap('measurements', 'expected one payload: '+fragment)
    return rows(payload[names[0]])


def no_swap(review, phase):
    p = review['phase_summary'][phase]
    if (p['samples'] <= 0 or p['max_swap_used_bytes'] != 0 or
            p['swapins_counter_delta_sum'] != 0 or p['swapouts_counter_delta_sum'] != 0 or
            p['sampler_error_samples'] != 0):
        raise InputGap('measurements.m5', 'swap-affected or unqualified phase: '+phase)


def vllm_rates(document):
    """TTFT includes request/first-token overhead; processed and useful rates differ."""
    out = []
    for row in document['B']:
        # Kit wraps each cached probe with its depth/delta coordinates.
        probe = row['measurement']
        depth, delta = row['depth'], row['delta']
        cached = probe['cached_tokens']
        ttft = probe['ttft_s']
        processed = depth+delta-cached
        if not (type(ttft) in (int,float) and math.isfinite(ttft) and ttft > 0 and
                0 <= cached <= depth and cached % 784 == 0 and processed > 0):
            raise InputGap('measurements.vllm', 'invalid cached-delta observation')
        out.append(dict(depth=depth, delta=delta, cached=cached, processed=processed,
                        ttft_s=ttft, processed_tok_s=processed/ttft, delta_tok_s=delta/ttft))
    if not out:
        raise InputGap('measurements.vllm', 'missing cached-delta observations')
    return out


def cold_fit(document):
    """OLS TTFT=a*N+b*N*N/2, matching the kit cold-fit objective."""
    points = [(r['length']/2, r['ttft_s']/r['length']) for r in document['A']]
    if len(points) < 4 or any(r.get('cached_tokens') != 0 or r['ttft_s'] <= 0 for r in document['A']):
        raise InputGap('measurements.vllm', 'positive uncached cold observations required')
    xx = sum(r['length']**2 for r in document['A'])
    xy = sum(r['length']**3/2 for r in document['A'])
    yy = sum(r['length']**4/4 for r in document['A'])
    xt = sum(r['length']*r['ttft_s'] for r in document['A'])
    yt = sum(r['length']**2/2*r['ttft_s'] for r in document['A'])
    det = xx*yy-xy*xy
    a,b = (xt*yy-yt*xy)/det, (yt*xx-xt*xy)/det
    if a <= 0 or b < 0:
        raise InputGap('measurements.vllm', 'invalid cold fit')
    return a,b


class MeasuredM5:
    """Q4/q8_0 rates; depth interpolation and explicitly bounded stream coverage."""
    def __init__(self):
        _, payload = package('m5')
        review = json.loads(payload['results/measurement-review.json'])
        for phase in ('40-run-depth', '50-run-parallel', '55-run-scaling'):
            no_swap(review, phase)
        self.depth = matching(payload, '-q27b-q4km-')
        self.parallel = matching(payload, '-q27b-par4-')
        self.scaling = [r for n,c in payload.items() if 'parallel-depth-' in n and n.endswith('.jsonl') for r in rows(c) if r['kind']=='round']
        from .server_prefill import fit
        self.a,self.b,points = fit(self.depth)
        self.prefill_curve = [(d, 2/sum(p['seconds_token'] for p in points if p['depth']==d)) for d in sorted({p['depth'] for p in points})]
        turns = [r for r in self.depth if r.get('kind')=='turn' and r['delta']==2000]
        self.decode_curve = [(r['depth']+r['prompt_n'],r['predicted_n']/(r['predicted_ms']/1000)) for r in turns]
        if len(self.decode_curve)!=6 or any(not r['gen_tokens_exact'] or r['truncated'] for r in turns):
            raise InputGap('measurements.m5','invalid decode observations')

    def prefill(self, depth):
        from .performance import Curve
        model = dict(base_flop=54e9,attention_slope=393216,sparse_slope=0,sparse_cap=0,context_limit=2e6)
        return Curve(model,self.prefill_curve).rate(depth)

    def decode(self, streams, depth):
        from .performance import Curve
        if not 1 <= streams <= 4:
            raise InputGap('measurements.m5','decode stream count outside common measured 1..4 range')
        if streams==3:
            # Three streams were not measured; interpolate aggregate throughput
            # between the adjacent admitted two/four-stream controls.
            return (2*self.decode(2,depth)+4*self.decode(4,depth))/6
        model = dict(base_flop=54e9,attention_slope=393216,sparse_slope=0,sparse_cap=0,context_limit=2e6)
        parallel = next(r for r in self.parallel if r['kind']=='parallel')
        anchors = list(self.decode_curve) if streams==1 else []
        if streams in (1,4):
            anchors.append((32000,parallel['single_decode_tok_s'] if streams==1 else parallel['aggregate_decode_tok_s']/4))
        for d in (65536,131072):
            rounds=[r for r in self.scaling if r['valid'] and not r['errors'] and r['streams']==streams and abs(r['depth']-d)<=16]
            if len(rounds)!=1:
                raise InputGap('measurements.m5','missing scaling anchor')
            r=rounds[0]
            aggregate=sum(q['predicted_n'] for q in r['requests'])/(max(q['predicted_ms'] for q in r['requests'])/1000)
            anchors.append((d,aggregate/streams))
        return Curve(model,sorted(anchors)).rate(depth)



def calculate(scenario, inputs):
    from .server_prefill import fit
    tables=[]
    def table(key, records, units):
        tables.append(dict(id=key,name=key,columns=units,rows=records))
    curves=[];fits=[];agreement=[];packages={k:package(k) for k in ('phase_a','off','on','m5')}
    points={}
    for key in ('phase_a','off','on'):
        raw=matching(packages[key][1],'-q27b-q4km-');a,b,pts=fit(raw);points[key]=pts
        fits.append(dict(case=key,a=a,b=b,max_residual=max(abs((a+b*p['depth'])/p['seconds_token']-1) for p in pts)))
        for p in pts:
            d=p['depth'];f=54e9+393216*d;peak=inputs.get('hardware.servers.rtx1.peak')
            curves.append(dict(case=key,depth=d,actual_depth=p['actual_depth'],delta=p['delta'],seconds_token=p['seconds_token'],fitted_seconds_token=a+b*d,rate=1/p['seconds_token'],fp8_fraction=f/(a+b*d)/peak))
    for p,q in zip(points['phase_a'],points['off']):
        if (p['depth'],p['delta'])!=(q['depth'],q['delta']):raise InputGap('measurements.gpu_server','mismatched reproduction coordinates')
        ratio=p['seconds_token']/q['seconds_token']
        if abs(ratio-1)>=.01:raise InputGap('measurements.gpu_server','phase A/off disagreement exceeds 1%')
        agreement.append(dict(depth=p['depth'],delta=p['delta'],relative_difference=ratio-1))
    earlier=rows(inputs.measured('gpu_server'))
    a,b,pts=fit(earlier);fits.append(dict(case='earlier run',a=a,b=b,max_residual=max(abs((a+b*p['depth'])/p['seconds_token']-1) for p in pts)))
    table('server_fits',fits,dict(case='text',a='s/token',b='s/token/depth-token',max_residual='fraction'))
    table('server_bulk',curves,dict(case='text',depth='token',actual_depth='token',delta='token',seconds_token='s/token',fitted_seconds_token='s/token',rate='token/s',fp8_fraction='fraction of dense FP8 peak'))
    table('server_reproduction',agreement,dict(depth='token',delta='token',relative_difference='fraction'))
    vllm=json.loads(next(c for n,c in packages['phase_a'][1].items() if n.endswith('/vllm.json')))
    cold=[];cached=[]
    for doc in vllm:
        if 'A' not in doc:continue
        a,b=cold_fit(doc)
        for r in doc['A']:
            n=r['length'];prediction=a*n+b*n*n/2
            cold.append(dict(option=doc['name'],depth=n,repetition=r['repetition'],ttft_s=r['ttft_s'],fitted_s=prediction,a=a,b=b,rate=n/r['ttft_s'],server_only=1,client_bridge=0))
        for r in vllm_rates(doc):cached.append(dict(option=doc['name'],**r,server_only=1,client_bridge=0))
    table('vllm_cold',cold,dict(option='text',depth='token',repetition='index',ttft_s='s',fitted_s='s',a='s/token',b='s/token/depth-token',rate='token/s',server_only='bool',client_bridge='bool'))
    table('vllm_cached',cached,dict(option='text',depth='token',delta='token',cached='token',processed='token',ttft_s='s',processed_tok_s='token/s',delta_tok_s='token/s',server_only='bool',client_bridge='bool'))
    client=MeasuredM5();rates=[]
    for label,raw in [('M3 Max 128 GB',rows(inputs.measured('depth'))),('M5 Max 64 GB',client.depth)]:
        for r in raw:
            if r['kind']!='turn':continue
            rates.append(dict(client=label,phase='40-run-depth' if label.startswith('M5') else 'historical-depth',depth=r['level'],actual_depth=r['depth'],delta=r['delta'],prefill_tok_s=r['prompt_n']/(r['prompt_ms']/1000),decode_tok_s=r['predicted_n']/(r['predicted_ms']/1000)))
    table('client_depth',rates,dict(client='text',phase='text',depth='token',actual_depth='token',delta='token',prefill_tok_s='token/s',decode_tok_s='token/s'))
    parallel=[]
    for r in client.parallel:
        if r['kind']=='parallel':
            parallel.append(dict(client='M5 Max 64 GB',phase='50-run-parallel',depth=r['depth'],streams=r['streams'],wall_tok_s=4*128/r['wall_s'],reported_tok_s=r['aggregate_decode_tok_s'],decode_interval_tok_s=r['aggregate_decode_tok_s'],single_tok_s=r['single_decode_tok_s']))
    for r in client.scaling:
        if not r['valid'] or r['errors']:raise InputGap('measurements.m5','invalid scaling round')
        parallel.append(dict(client='M5 Max 64 GB',phase='55-run-scaling',depth=r['depth'],streams=r['streams'],wall_tok_s=sum(q['predicted_n'] for q in r['requests'])/r['wall_s'],reported_tok_s=r['aggregate_tok_s'],decode_interval_tok_s=sum(q['predicted_n'] for q in r['requests'])/(max(q['predicted_ms'] for q in r['requests'])/1000),single_tok_s=128/(r['requests'][0]['predicted_ms']/1000) if r['streams']==1 else 0))
    table('client_parallel',parallel,dict(client='text',phase='text',depth='token',streams='stream',wall_tok_s='token/s',reported_tok_s='token/s (kit counter convention)',decode_interval_tok_s='token/s',single_tok_s='token/s (0 means not a single-stream row)'))
    return dict(scenario=scenario['name'],tables=tables,export_namespace=scenario['export_namespace'],alarms=[],computed_metrics=sum(len(t['rows']) for t in tables),notes=['All vLLM rows are server-only; no client state bridge. Methods A and B include TTFT overhead; B reports processed tokens and useful delta separately. fp8-kv and NVFP4 startup failures remain unsupported. M5 step57 excluded for measured swap; sampled telemetry cannot exclude all contention. decode_interval_tok_s uses predicted_n/predicted_ms; step55 reported_tok_s instead counts predicted_n-1 timed steps. Step50 preserves its rounded summary because per-request timings were not archived.'])
