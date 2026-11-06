"""Run20 admission, measured vLLM TTFT and capacity-bounded decode contracts."""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from .inputs import InputGap,ROOT
from . import measurements_r13 as r13,measurements_r14 as r14,measurements_r16 as r16,measurements_r18 as r18,measurements_r19 as r19

CONFIG=Path(__file__).parent/'data/run20-economics.json'
SNAPSHOT=ROOT/'calc/prices-2026-10-29/qwen_qwen3.8-27b.json'
EVIDENCE=ROOT/'data/measurements/run20-2026-11-03/evidence.json'


def config():return json.loads(CONFIG.read_text())


def fraction(x,name):
    r16.nonnegative(x,name)
    if x>1:raise InputGap('run20.'+name,'fraction must be within zero and one')
    return x


def admission(row,context):
    reasons=[]
    if row.get('context_length',0)<context:reasons.append('context_below_'+str(context))
    pricing=row.get('pricing',{})
    if not (row.get('supports_implicit_caching') is True or 'input_cache_write'in pricing):reasons.append('caching_not_declared')
    if 'input_cache_read'not in pricing:reasons.append('cache_read_price_missing')
    availability=[row[k] for k in ('uptime_last_5m','uptime_last_30m','uptime_last_1d')if row.get(k)is not None]
    if any(not isinstance(x,(int,float))or not math.isfinite(x)or x<95 or x>100 for x in availability):reasons.append('recorded_availability_below_95_or_invalid')
    for k in ('prompt','completion','input_cache_read','input_cache_write'):
        if k in pricing:
            try:v=float(pricing[k])
            except (TypeError,ValueError):v=-1
            if not math.isfinite(v)or v<0:reasons.append('invalid_'+k+'_price')
        elif k in ('prompt','completion'):reasons.append(k+'_price_missing')
    return reasons


def cache_measurements(document,known):
    if set(document)!={'measurements'}:raise InputGap('run20.cache','cache interface requires measurements only')
    out={}
    for r in document['measurements']:
        key=(r.get('tag'),r.get('profile'))
        if key in out or r.get('tag')not in known or r.get('profile')not in ('main','million'):
            raise InputGap('run20.cache','duplicate or unknown provider/profile')
        if r.get('model')!='qwen/qwen3.8-27b' or not r.get('observed_at') or not r.get('source'):
            raise InputGap('run20.cache','dated same-model source required')
        total=r19.integer(r.get('input_tokens'),'input_tokens');hit=r19.integer(r.get('cached_tokens'),'cached_tokens',True)
        if hit>total:raise InputGap('run20.cache','cached tokens exceed input tokens')
        out[key]=hit/total
    return out


def api_cost(row,means,hit):
    """Expected aggregate token billing; observed98.1% is a scenario, not per-call cache mechanics."""
    fraction(hit,'cache_hit');d,n,o=means;p=row['pricing'];inp=d+n
    miss=float(p.get('input_cache_write',p['prompt']))
    return inp*(hit*float(p['input_cache_read'])+(1-hit)*miss)+o*float(p['completion'])


def api_baselines(calls,cfg):
    owner=json.loads(EVIDENCE.read_text())['owner_cache'];content=(ROOT/owner['path']).read_bytes()
    if hashlib.sha256(content).hexdigest()!=owner['sha256'] or cfg['owner_cache_fraction']!=owner['hit_fraction']:
        raise InputGap('run20.cache','owner cache fraction must match hash-checked NOTES evidence')
    rows=json.loads(SNAPSHOT.read_text())['data']['endpoints'];known={r['tag']for r in rows}
    measured=cache_measurements(cfg['provider_cache_hits'],known)
    means=tuple(sum(r[i] for r in calls)/len(calls)for i in range(3))
    out=[];selected={}
    for profile,limit in (('main',262144),('million',1000000)):
        # Million prices compare one million input tokens and the same mean output.
        m=means if profile=='main' else (1000000-means[2],0,means[2]);candidates=[]
        for row in rows:
            reasons=admission(row,limit);h=measured.get((row['tag'],profile),cfg['owner_cache_fraction'])
            price=api_cost(row,m,h)if not reasons else None
            record=dict(profile=profile,provider=row['provider_name'],tag=row['tag'],context_limit=row['context_length'],
                admitted=not reasons,reasons='; '.join(reasons)or'passes snapshot criteria',
                availability_basis='minimum of every recorded5m/30m/1d window'if any(row.get(k)is not None for k in ('uptime_last_5m','uptime_last_30m','uptime_last_1d'))else'not recorded; unverified',
                cache_hit_fraction=h,cache_basis='measured provider token fraction'if(row['tag'],profile)in measured else'owner commercial aggregate98.1% scenario; provider cache behaviour unverified',
                effective_usd_per_1000_calls=price*1000 if price is not None else alarm('API excluded by admission'),
                prompt_usd_million=float(row['pricing']['prompt'])*1e6,output_usd_million=float(row['pricing']['completion'])*1e6,
                cache_read_usd_million=float(row['pricing']['input_cache_read'])*1e6 if 'input_cache_read' in row['pricing'] else alarm('cache read price not declared'),
                mean_input_tokens=m[0]+m[1],mean_output_tokens=m[2],role='excluded'if reasons else'admitted')
            out.append(record)
            if price is not None:candidates.append((price,row['tag'],record))
        if not candidates:raise InputGap('run20.api','no admitted provider for '+profile)
        candidates.sort(key=lambda x:(x[0],x[1]));cheap=candidates[0];median=candidates[len(candidates)//2]
        cheap[2]['role']='cheapest';median[2]['role']='median'if median is not cheap else'cheapest_and_median'
        selected[profile]=dict(cheapest=cheap[0],median=median[0],cheapest_tag=cheap[1],median_tag=median[1],count=len(candidates))
    return out,selected


def alarm(reason):return {'alarm':[dict(input='run20',reason=reason)]}


def bridge_evidence():
    info=json.loads(EVIDENCE.read_text());out={}
    for key in ('pro6000','b300'):
        p=ROOT/info[key]['path'];content=p.read_bytes()
        if hashlib.sha256(content).hexdigest()!=info[key]['sha256']:raise InputGap('run20.bridge','bridge source SHA256 mismatch')
        records=[json.loads(l)for l in content.splitlines()]
        chunks=[c for r in records if r.get('stage')=='call'and r.get('path')=='offload'for c in r['chunks']]
        if not chunks or any(c.get('status')not in ('imported','staged')or c['n1']<=c['n0']or c['server_prefill_ms']<=0 for c in chunks):
            raise InputGap('run20.bridge','successful measured bridge chunks required')
        if any(r['chunks'][-1]['status']!='imported' or r['remote_applied']!=sum(c['n1']-c['n0'] for c in r['chunks']) for r in records if r.get('stage')=='call' and r.get('path')=='offload'):
            raise InputGap('run20.bridge','staged chunks require successful terminal import and exact applied count')
        out[key]=dict(seconds_token=sum(c['server_prefill_ms']/1000 for c in chunks)/sum(c['n1']-c['n0']for c in chunks),
            chunks=len(chunks),tokens=sum(c['n1']-c['n0']for c in chunks),source=info[key]['path'])
    return out


class Server:
    def __init__(self,key,cfg=None):
        self.cfg=cfg or config();self.key=key;self.info=self.cfg['servers'][key]
        r18.positive(self.cfg['bandwidth_efficiency'],'bandwidth_efficiency')
        self.engine=self.info['engine'];self.weights=self.info['weights_bytes'];self.kv=self.info['kv_bytes_token'];self.state=r19.STATE
        for k in ('weights_bytes','kv_bytes_token','memory_bytes','bandwidth_bytes_s','workspace_bytes'):r18.positive(self.info[k],k)
        self.free=self.info['memory_bytes']-self.weights-self.info['workspace_bytes']
        self.depth_limit=249000;self.old=None
        if self.engine=='vllm':
            if self.info['host']=='pro6000'and self.info['variant']!='fp8-default':raise InputGap('run20.server','PRO6000 FP8 KV did not start')
            docs=(r14.B300Measurements().vllm if self.info['host']=='b300'else json.loads(next(v for k,v in r13.package('phase_a')[1].items()if k.endswith('/vllm.json'))))
            doc=next(d for d in docs if d['name']==self.info['variant'])
            self.a,self.b=r13.cold_fit(doc)
            raw=r14.b300_vllm_rates(doc)if self.info['host']=='b300'else r13.vllm_rates(doc)
            self.points={n:sorted((r['depth'],r['ttft_s'])for r in raw if r['delta']==n)for n in (2000,10000)}
            if any(len(v)!=4 for v in self.points.values()):raise InputGap('run20.server','complete cached delta ladder required')
            self.bridge=bridge_evidence()[self.info['host']]
        elif self.engine=='llama_cpp':
            if key=='llama_b300':self.old=r14.B300Measurements()
            else:self.old=r19.Node(self.info['host'])
        else:raise InputGap('run20.server','unknown engine')

    def session_bytes(self,depth):
        r16.nonnegative(depth,'depth');return depth*self.kv+self.state

    def slots(self,depth):
        result=math.floor(self.free/self.session_bytes(depth))
        if result<1:raise InputGap('run20.capacity','one complete session does not fit a GPU replica')
        return result

    def cached(self,depth,delta,bridge='none'):
        for k,v in (('depth',depth),('delta',delta)):r16.nonnegative(v,k)
        if depth>self.depth_limit or delta>10000:raise InputGap('run20.prefill','outside measured depth/delta envelope')
        if bridge not in ('none','measured_envelope'):raise InputGap('run20.bridge','unknown bridge assumption')
        if self.engine=='vllm':
            y={n:r18.interpolate(ps,depth)for n,ps in self.points.items()}
            # Linear elapsed-time interpolation; shallow endpoint hold and
            # delta<2000 extension are assumptions, never extra measured anchors.
            seconds=y[2000]+(delta-2000)*(y[10000]-y[2000])/8000
            if seconds<=0:raise InputGap('run20.prefill','nonpositive cached TTFT extension')
            if bridge=='measured_envelope':seconds=max(seconds,delta*self.bridge['seconds_token'])
            return seconds
        if isinstance(self.old,r19.Node):return delta/self.old.rate(depth,max(512,delta))
        return delta*(self.old.a+self.old.b*depth)

    def cold(self,depth):
        r16.nonnegative(depth,'depth')
        if depth>self.depth_limit:raise InputGap('run20.prefill','cold rebuild outside measured depth envelope')
        if self.engine=='vllm':return self.a*depth+self.b*depth**2/2
        if isinstance(self.old,r19.Node):return self.old.swap_seconds(depth,'NVMe')
        return self.old.a*depth+self.old.b*depth**2/2

    def decode(self,depth,streams=32,measurements=None):
        """Bandwidth ceiling model; every stream reads its complete KV per token."""
        r19.integer(streams,'streams');k=min(streams,self.slots(depth))
        passes=self.cfg['state_passes'];r18.positive(passes,'state_passes')
        traffic=self.kv*depth+passes*self.state
        bw=self.info['bandwidth_bytes_s']*fraction(self.cfg['bandwidth_efficiency'],'bandwidth_efficiency')
        single=bw/(self.weights+traffic);aggregate=k*bw/(self.weights+k*traffic)
        basis='modelled bandwidth; depth-aware KV and memory limit; not vLLM decode measurement'
        if measurements:
            anchors=[r for r in measurements if r['server']==self.key and r['streams']==k]
            if anchors:
                if not min(r['depth']for r in anchors)<=depth<=max(r['depth']for r in anchors):
                    raise InputGap('run20.decode','measured decode curve cannot extrapolate depth')
                aggregate=r18.interpolate(sorted((r['depth'],r['aggregate_tok_s'])for r in anchors),depth)
                # Gain remains a model quantity unless the same depth has a single-stream observation.
                ones=[r for r in measurements if r['server']==self.key and r['streams']==1]
                if not ones:raise InputGap('run20.decode','measured single-stream curve required for gain')
                single=r18.interpolate(sorted((r['depth'],r['aggregate_tok_s'])for r in ones),depth)
                basis='measured aggregate curve; interpolation within observed depth; no external extrapolation'
        return dict(batch=k,single_tok_s=single,aggregate_tok_s=aggregate,gain=aggregate/single,basis=basis)


def decode_measurements(document,servers):
    if set(document)!={'measurements'}:raise InputGap('run20.decode','decode interface requires measurements only')
    seen=set();out=[]
    for r in document['measurements']:
        key=(r.get('server'),r.get('streams'),r.get('depth'))
        if key in seen or key[0]not in servers or key[1]not in (1,8,32)or key[2]not in (16000,64000,164000):
            raise InputGap('run20.decode','duplicate or unsupported server/streams/depth')
        seen.add(key);r18.positive(r.get('aggregate_tok_s'),'aggregate_tok_s')
        if not r.get('source')or not r.get('observed_at')or r.get('engine')!='vllm':raise InputGap('run20.decode','dated vLLM source required')
        if servers[key[0]].engine!='vllm'or servers[key[0]].slots(key[2])<key[1]:raise InputGap('run20.decode','measured stream count exceeds resident capacity or wrong engine')
        out.append(r)
    # Sparse measured curves are valid only with single-stream references
    # spanning every supplied parallel depth; impossible grid cells stay absent.
    for key in {r['server']for r in out}:
        ones=[r['depth'] for r in out if r['server']==key and r['streams']==1]
        if not ones:raise InputGap('run20.decode','measured single-stream curve required for gain')
        if any(not min(ones)<=r['depth']<=max(ones) for r in out if r['server']==key):
            raise InputGap('run20.decode','single-stream reference does not span parallel observations')
    return out


def unit_month(server,inputs,billing):
    h=server.info['host'];gpus=8 if h=='b300'else 1
    if billing=='bought':
        if h=='rtx5090':capex,month=r19.unit_month(r19.Node('rtx5090'),inputs,r19.config())
        else:
            p='owners.options.'+('b300_node'if h=='b300'else'office6000')
            capex=inputs.get(p+'.capex');power=inputs.get(p+'.power')
            month=capex*(1-inputs.get('owners.residual'))/(12*inputs.get('owners.years'))
            month+=capex*inputs.get('owners.office_support'if h!='b300'else'economics.support')/12
            month+=power*inputs.get('economics.pue')*inputs.get('economics.hours_month')*inputs.get('owners.office_load'if h!='b300'else'owners.load')*inputs.get('prices.energy_client'if h!='b300'else'prices.energy_dc')
            if h=='b300':month+=power*inputs.get('prices.colo')
        return month,gpus
    if billing=='rented':return server.info['hourly_usd']*730,gpus
    raise InputGap('run20.billing','bought or calendar rented node required')
