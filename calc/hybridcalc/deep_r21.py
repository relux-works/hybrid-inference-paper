"""Explicit run21 aggregate reconstruction and long-context sensitivities.

No deep prefill/decode prediction in this module is a new measurement.
"""
import copy
import csv
import hashlib
import io
import json
import math
from functools import lru_cache
from pathlib import Path

from .inputs import ROOT, InputGap
from . import measurements_r16 as r16, measurements_r18 as r18
from . import measurements_r19 as r19, server_economics_r20 as s

CONFIG = Path(__file__).parent/'data/run21-deep.json'
STATS = ROOT/'data/measurements/ivmbp-2026-10-30/stats.json'
LIMIT = 1000000
SERVERS = ('pro6000_fp8', 'b300_fp8', 'b300_fp8_kv')


def config():
    return json.loads(CONFIG.read_text())


def checked_stats(cfg=None):
    cfg = cfg or config()
    content = STATS.read_bytes()
    if hashlib.sha256(content).hexdigest() != cfg['stats_sha256']:
        raise InputGap('run21.stats', 'aggregate source SHA256 mismatch')
    return json.loads(content)


def quantile(points, p):
    return r18.interpolate(points, p)


def reconstruct(agent, count=1000, pause_cap=300):
    """Mean-calibrated quantile quadrature and permuted output/gap ranks.

    This recovers published marginals approximately, never original calls or
    correlations. Tail endpoints and the conditional mean delta are estimates.
    """
    r19.integer(count, 'quadrature_count')
    r18.positive(pause_cap,'active_gap_cap_s')
    if count < 100:
        raise InputGap('run21.profile', 'at least100 quadrature points required')
    depth = agent['depth_per_call']
    bins=agent['new_in_by_depth'];total=sum(x['n']for x in bins.values());cumulative=0
    dp = [(0, 0)] + [(p, depth['p'+str(int(p*100))]) for p in (.1,.25,.5,.75,.9,.99)] + [(1, LIMIT)]
    for key,bound in (('<50k',50000),('50-100k',100000),('100-200k',200000)):
        cumulative+=bins[key]['n'];dp.append((cumulative/total,bound))
    dp.sort()
    def fitted(points,mean):
        def value(p,power):
            for (a,x),(b,y)in zip(points,points[1:]):
                if p<=b:return x+(y-x)*((p-a)/(b-a))**power
            return points[-1][1]
        lo,hi=.01,100
        low_mean=sum(value((i+.5)/count,hi)for i in range(count))/count
        high_mean=sum(value((i+.5)/count,lo)for i in range(count))/count
        if not low_mean<=mean<=high_mean:
            raise InputGap('run21.profile','aggregate mean incompatible with declared quantile reconstruction')
        for _ in range(50):
            power=(lo+hi)/2;actual=sum(value((i+.5)/count,power)for i in range(count))/count
            if actual>mean:lo=power
            else:hi=power
        return [value((i+.5)/count,(lo+hi)/2)for i in range(count)]
    depths=fitted(dp,depth['mean'])
    def ranks(field):
        q = agent[field]
        # End tail capped at ten times p99; absent raw maximum stays unknown.
        ps = [(0,0)] + [(p,q['p'+str(int(p*100))]) for p in (.1,.25,.5,.75,.9,.99)] + [(1,10*q['p99'])]
        return fitted(ps,q['mean'])
    outputs=ranks('output_per_call');pauses=ranks('gap_seconds')
    calls = []
    for i in range(count):
        d = depths[i]
        key = '<50k' if d<50000 else '50-100k' if d<100000 else '100-200k' if d<200000 else '200k+'
        n = agent['new_in_by_depth'][key]['mean']
        o = outputs[(i*137)%count]
        # Long idle gaps cannot all be charged as active tool work. This
        # explicit300s cap is a scenario assumption, not a measured tool cap.
        pause = min(pause_cap,pauses[(i*313)%count])
        calls.append((d,n,o,pause))
    return calls


def profile_rows(stats):
    out = []
    for name,key in (('existing_combined','all'),('claude_deep','claude')):
        a=stats['agents'][key]
        for metric in ('depth_per_call','new_in_per_call','output_per_call','gap_seconds'):
            for statistic,value in a[metric].items():
                out.append(dict(profile=name,metric=metric,statistic=statistic,value=value,
                    value_unit='call'if statistic=='n'else's'if metric=='gap_seconds'else'token',
                    basis='published aggregate; pause quantiles cannot be recomputed from raw calls absent from package'))
        bins=a['new_in_by_depth']
        out.append(dict(profile=name,metric='depth_at_least_200k',statistic='fraction_of_delta_observed_calls',
            value=bins['200k+']['n']/sum(v['n']for v in bins.values()),value_unit='1',
            basis='recomputed depth-bin count ratio; delta-observed denominator differs from all calls'))
    return out


def extension_basis(model, side):
    if model == 'qwen' and side in ('client','server'):
        return 'model-card YaRN factor4; hybrid client/server configuration requirement; quality unqualified'
    if side == 'api':
        return 'provider context-extension method unknown; same YaRN not established'
    if model == 'glm':
        return 'native1048576 NoPE; architecture estimate, no YaRN required'
    raise InputGap('run21.yarn','unknown model or side')


class Server(s.Server):
    """vLLM measured through249k; explicit positive elapsed-time extrapolation."""
    def __init__(self,key,cfg=None):
        if key not in SERVERS:
            raise InputGap('run21.server','owner excludes5090 servers; PRO6000/B300 only')
        super().__init__(key,cfg)

    def cached(self,depth,delta,bridge='none'):
        for key,value in (('depth',depth),('delta',delta)):
            r16.nonnegative(value,key)
        if depth+delta>1048576:
            raise InputGap('run21.context','YaRN analysis envelope exceeded')
        if delta==0:return 0.0
        if delta>10000:
            total=0
            while delta>0:
                n=min(10000,delta);total+=self.cached(depth,n,bridge);depth+=n;delta-=n
            return total
        if depth<=249000:
            return super().cached(depth,delta,bridge)
        if bridge not in ('none','measured_envelope'):
            raise InputGap('run21.bridge','unknown bridge assumption')
        # Extend the last measured depth sec/token slope, never negative.
        def at(d):
            y={n:r18.interpolate(ps,d)for n,ps in self.points.items()}
            return y[2000]+(delta-2000)*(y[10000]-y[2000])/8000
        a,b=131072,249000
        seconds=at(b)+max(0,(at(b)-at(a))/(b-a))*(depth-b)
        if bridge=='measured_envelope':seconds=max(seconds,delta*self.bridge['seconds_token'])
        if seconds<=0:raise InputGap('run21.prefill','nonpositive elapsed-time extrapolation')
        return seconds

    def cold(self,depth):
        r16.nonnegative(depth,'depth')
        if depth>1048576:raise InputGap('run21.context','cold rebuild exceeds YaRN envelope')
        return self.a*depth+self.b*depth**2/2


def decode_measurements(document,servers):
    """Data-only sparse vLLM1/8/32-stream observations, including512k/1M."""
    if set(document)!={'measurements'}:
        raise InputGap('run21.decode','measurements-only interface required')
    seen=set();out=[]
    for row in document['measurements']:
        r19.integer(row.get('streams'),'streams')
        r19.integer(row.get('depth'),'depth')
        key=(row.get('server'),row.get('streams'),row.get('depth'))
        if key in seen or key[0]not in servers or key[1]not in (1,8,32) or key[2]not in (16000,64000,164000,512000,1000000):
            raise InputGap('run21.decode','duplicate or unsupported server/streams/depth')
        if row.get('engine')!='vllm' or not row.get('source') or not row.get('observed_at'):
            raise InputGap('run21.decode','dated vLLM source required')
        r18.positive(row.get('aggregate_tok_s'),'aggregate_tok_s')
        if servers[key[0]].slots(key[2])<key[1]:
            raise InputGap('run21.decode','measured streams exceed resident capacity')
        if key[2]>262144 and row.get('extension')!='yarn_factor4':
            raise InputGap('run21.decode','deep Qwen measurement requires recorded YaRN factor4')
        seen.add(key);out.append(row)
    for row in out:
        ones=[x['depth']for x in out if x['server']==row['server'] and x['streams']==1]
        if not ones or not min(ones)<=row['depth']<=max(ones):
            raise InputGap('run21.decode','single-stream reference must span parallel observations')
    return out


def provider_measurements(document,known):
    if set(document)!={'measurements'}:
        raise InputGap('run21.cache','measurements-only interface required')
    out={}
    for row in document['measurements']:
        key=(row.get('model'),row.get('tag'),row.get('profile'))
        if key in out or key[:2]not in known or key[2]not in ('existing_combined','claude_deep','million'):
            raise InputGap('run21.cache','duplicate or unknown model/provider/profile')
        if not row.get('source')or not row.get('observed_at'):
            raise InputGap('run21.cache','dated provider cache evidence required')
        total=r19.integer(row.get('input_tokens'),'input_tokens')
        cached=r19.integer(row.get('cached_tokens'),'cached_tokens',True)
        if cached>total:raise InputGap('run21.cache','cached tokens exceed input tokens')
        out[key]=cached/total
    return out


def api_baselines(calls,profile,cfg,context):
    owner=json.loads(s.EVIDENCE.read_text())['owner_cache']
    if (cfg['owner_cache_fraction']!=owner['hit_fraction'] or
        hashlib.sha256((ROOT/owner['path']).read_bytes()).hexdigest()!=owner['sha256']):
        raise InputGap('run21.cache','owner allowance must match source-bound NOTES evidence')
    qwen=json.loads(s.SNAPSHOT.read_text())['data']['endpoints']
    glm=cfg['glm_endpoints']['endpoints']
    known={(r['model_id'],r['tag'])for r in qwen+glm}
    measured=provider_measurements(cfg['provider_cache_hits'],known)
    means=tuple(sum(r[i]for r in calls)/len(calls)for i in range(3))
    rows=[];selected={}
    for model,providers in (('qwen',qwen),('glm',glm)):
        admitted=[]
        for row in providers:
            reasons=s.admission(row,context)
            # Respect declared context inclusive of the generated answer and
            # max_prompt_tokens when a snapshot records a stricter input cap.
            if max(d+n+o for d,n,o,t in calls)>row['context_length']:reasons.append('call_total_exceeds_context')
            if row.get('max_prompt_tokens') and max(d+n for d,n,o,t in calls)>row['max_prompt_tokens']:
                reasons.append('call_input_exceeds_max_prompt')
            key=(row['model_id'],row['tag'],profile)
            hit=measured.get(key,cfg['owner_cache_fraction'])
            price=s.api_cost(row,means,hit)if not reasons else s.alarm('API excluded: '+'; '.join(reasons))
            rec=dict(profile=profile,model=model,provider=row['provider_name'],tag=row['tag'],admitted=not reasons,
                reasons='; '.join(reasons)or'passes recorded snapshot criteria',context_limit=row['context_length'],
                usd_per_1000_calls=price*1000 if isinstance(price,(int,float))else price,
                mean_input_tokens=means[0]+means[1],mean_output_tokens=means[2],
                cache_hit_fraction=hit,cache_basis='measured provider token fraction'if key in measured else'owner98.1% allowance; per-provider cache unverified',
                availability_basis='minimum recorded windows; missing windows unverified',extension_basis=extension_basis(model,'api'),role='excluded'if reasons else'admitted')
            rows.append(rec)
            if not reasons:admitted.append((price,row['tag'],rec))
        admitted.sort(key=lambda x:(x[0],x[1]))
        if admitted:
            cheap,median=admitted[0],admitted[len(admitted)//2]
            cheap[2]['role']='cheapest';median[2]['role']='median'if median!=cheap else'cheapest_and_median'
            selected[model]=dict(cheapest=cheap[0],median=median[0],count=len(admitted))
        else:selected[model]=dict(cheapest=s.alarm('no admitted '+model+' endpoint'),median=s.alarm('no admitted '+model+' endpoint'),count=0)
    return rows,selected


def rental_basis(old):
    return r19.rental_basis(old)


def corrected_r19():
    # Successor view preserves every numeric cell and immutable historical CSV.
    path=ROOT/'calc/out/run19/rented_prefill_node.csv'
    rows=list(csv.DictReader(io.StringIO(path.read_text())))
    for row in rows:
        row['basis']=rental_basis(row['basis'])
        row.pop('status');row.pop('alarm_inputs')
    return rows


def mac_prefill(context,client,depth,delta,variant='measured_anchor_flop_extension'):
    if variant=='analyst_120s_at_1M':
        return delta/690*120
    if variant!='measured_anchor_flop_extension':
        raise InputGap('run21.mac','unlabelled Mac prefill extrapolation forbidden')
    if client=='m3max':return delta/m3_surface().for_delta(depth,delta)
    # Last measured nominal depth is249k. Hold FLOP efficiency, not rate.
    anchor=249000;rate=context.measured_m5.prefill(min(depth,anchor))
    if depth>anchor:rate*=(54e9+393216*anchor)/(54e9+393216*depth)
    return delta/rate


@lru_cache(maxsize=1)
def m3_surface():
    return r16.SingleStream()


def mac_ceiling(depth,bandwidth=400e9,weights=18.97e9,kv=34816,state=156893184):
    for key,value in (('depth',depth),('bandwidth',bandwidth),('weights',weights),('kv',kv)):
        r18.positive(value,key)
    return bandwidth/(weights+kv*depth+state)
