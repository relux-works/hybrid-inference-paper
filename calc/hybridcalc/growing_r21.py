"""Growing200k/1M tasks on R20 costs; all GLM performance is estimated."""
import copy
import hashlib
import math
from pathlib import Path

from .inputs import ROOT, InputGap
from . import deep_r21 as d, measurements_r21 as r
from . import measurements_r20 as old, measurements_r16 as r16
from . import measurements_r19 as r19, server_economics_r20 as s


def trace(agent,limit):
    if limit not in (200000,1000000):raise InputGap('run21.growing','target must be200k or1M')
    calls=[];depth=0
    while depth<limit:
        key='<50k'if depth<50000 else'50-100k'if depth<100000 else'100-200k'if depth<200000 else'200k+'
        n=min(agent['new_in_by_depth'][key]['mean'],limit-depth)
        o=min(agent['output_per_call']['mean'],limit-depth-n)
        if n<=0:raise InputGap('run21.growing','positive input increment required')
        calls.append((depth,n,o,agent['gap_seconds']['p50']))
        depth+=n+o
    return calls


class GlmServer:
    """A two-B300 FP8 replica, priced as four replicas per eight-GPU box."""
    key='glm_two_b300';engine='vllm';weights=328e9;kv=5984;state=152600000
    def __init__(self,qwen,inputs):
        self.qwen=qwen;self.inputs=inputs;self.info=dict(host='b300',hourly_usd=76)
        self.free=2*288e9-self.weights-2*8e9
    def session_bytes(self,depth):return self.kv*depth+self.state
    def slots(self,depth):
        value=math.floor(self.free/self.session_bytes(depth))
        if value<1:raise InputGap('run21.growing','complete GLM session exceeds two-GPU capacity')
        return value
    def flop_ratio(self,depth):return (35213909504+22528*depth+1441792*min(depth,8192))/(54e9+393216*depth)
    def cached(self,depth,n,bridge='none'):return self.qwen.cached(depth,n,bridge)*self.flop_ratio(depth)
    def cold(self,depth):return self.qwen.cold(depth)*self.flop_ratio(depth)
    def decode(self,depth,streams=32,measurements=None):return r.glm_batch(depth,streams,self.inputs)


class GlmPrepared(old.Prepared):
    def __init__(self,calls,server,context):
        self.calls=calls;self.context=context
        self.profiles={x['key']:x for x in r19.links(context.inputs)}
        self.own=[];self.pre=[];self.shadow=[];self.output=[];self.wire=[];self.imports=[];self.rebuild=[]
        self.decode_device=[];self.decode_occupied=[];self.wait_weight=[]
        importer=r16.ClientImport()
        # Integral of the architecture FLOP law anchors the unmeasured
        # Studio cold1M=57min estimate; it is not a measured delta curve.
        D=1000000;cap=8192
        integral=35213909504*D+22528*D**2/2+1441792*(cap*D-cap**2/2)
        coefficient=57*60/integral
        for depth,n,o,tool in calls:
            server.slots(depth+n+o)
            flops=35213909504+22528*(depth+n/2)+1441792*min(depth+n/2,cap)
            self.own.append(n*flops*coefficient)
            self.pre.append(server.cached(depth,n,'measured_envelope'))
            base=server.cached(depth,n)
            self.shadow.append(base*(n+o)/n);self.output.append(base*o/n)
            self.wire.append(n*5984+152600000);self.imports.append(importer.at_depth(n,depth))
            self.rebuild.append(server.cold(depth))
            slots=math.floor((.9*256e9-181.4e9-4e9)/(5984*(depth+n+o)+152600000))
            k=min(4,slots)
            if k<1:raise InputGap('run21.growing','complete GLM client session does not fit256GB')
            union=288*(1-(1-8/288)**k)
            traffic=4.6125e9+4.75875e9*union/8+k*(5984*(depth+n)+152600000)
            per_stream=.4*819.2e9/traffic
            self.decode_device.append(o/(k*per_stream))
            self.decode_occupied.append((o/per_stream+tool)/k);self.wait_weight.append(1/k)


class Economics(old.Economics):
    def __init__(self,context,calls,servers,cfg,model):
        super().__init__(context,calls,servers,cfg,{})
        self.model=model;self.ready={}
        for key,server in servers.items():
            if model=='glm':
                for billing in ('bought','rented'):
                    month,gpus=self.units[key,billing];self.units[key,billing]=(month,4)
                self.ready[key]=GlmPrepared(calls,server,context)
            else:self.ready[key]=r.Prepared(calls,server,'m3max',context,'measured_envelope',[])

    @old.capacity_result('hybrid')
    def hybrid(self,key,team,demand,basis,billing,link):
        r19.integer(team,'team');s.r18.positive(demand,'demand')
        if basis not in ('owned','new'):raise InputGap('run21.growing','owned/new basis required')
        server=self.servers[key];prepared=self.ready[key];month,gpus=self.units[key,billing]
        boxes=self.storage_boxes(server,team,gpus)
        while True:
            spill,host=self.retention(server,team,boxes,gpus);stat=prepared.stats(spill,link)
            served=min(demand,stat['client_capacity_day']);overflow=demand-served
            full=self.fleet_stats(server,team,boxes,gpus)
            overflow_gpu=full['fleet_s_call']*full['active_gpus']+spill*self.cold[key]
            work=served*stat['gpu_s_call']+overflow*overflow_gpu
            needed=max(1,math.ceil(team*work/(self.hours*3600*self.load*full['active_gpus'])*boxes))
            if needed>boxes and boxes*gpus>=team*self.concurrency and spill==0:
                raise InputGap('run21.growing','finite team concurrency cannot serve growing hybrid demand')
            if needed<=boxes:break
            boxes=needed
        if self.model=='glm':purchase,power=8000,.25
        else:purchase,power=self.inputs.get('hardware.clients.m3max.purchase_price'),self.inputs.get('hardware.clients.m3max.power')
        device=0 if basis=='owned'else purchase*(1-self.inputs.get('economics.client_residual'))/(12*self.inputs.get('owners.years'))
        energy=power*self.hours*self.days*self.inputs.get('prices.energy_client');front=self.inputs.get('owners.front_month')
        storage=host/1e9*self.inputs.get('hosting.tiers.NVMe.price')if billing=='rented'else 0
        return dict(person_month=boxes*month/team+storage/team+device+energy+front,boxes=boxes,unit_month=month,
            device_month=device,client_energy_month=energy,front_month=front,server_person_month=boxes*month/team,storage_person_month=storage/team,
            served_day=served,server_decode_overflow_day=overflow,spill_share=spill,offload_share=stat['offload_share'],
            client_capacity_day=stat['client_capacity_day'],prefill_gpu_s_day=served*stat['gpu_s_call'],decode_overflow_gpu_s_day=overflow*overflow_gpu,pending_s_offload=stat['pending_s_offload'])


def calculate():
    from .engine import load
    from .paper_tables import Context
    spec,inputs=load('deep-economics-r21');context_spec,_=load('paper-tables-r17');context=Context(context_spec,inputs)
    cfg=s.config();cfg['server_decode']={'measurements':[]};stats=d.checked_stats();config=d.config()
    rows=[];traces=[];apis=[]
    for profile,agent in (('existing_combined',stats['agents']['all']),('claude_deep',stats['agents']['claude'])):
        for limit in (200000,1000000):
            calls=trace(agent,limit);N=len(calls)
            cfg['reservation_depth']=limit
            price_rows,api=d.api_baselines(calls,'million',config,limit)
            for row in price_rows:apis.append(dict(row,growing_profile=profile,target_depth=limit))
            for model in ('qwen','glm'):
                if model=='qwen':servers={key:d.Server(key)for key in ('b300_fp8','b300_fp8_kv')}
                else:servers={'glm_two_b300':GlmServer(d.Server('b300_fp8'),inputs)}
                econ=Economics(context,calls,servers,cfg,model)
                for key,server in servers.items():
                    traces.append(dict(profile=profile,model=model,server=key,target_depth=limit,calls=N,
                        new_tokens=sum(x[1]for x in calls),output_tokens=sum(x[2]for x in calls),
                        end_depth=calls[-1][0]+calls[-1][1]+calls[-1][2],
                        client_prefill_s=sum(econ.ready[key].own),
                        basis='synthetic growing mean-delta/mean-output task, not raw log replay; same task for hybrid/API/cluster'))
                    for team in (5,50,500):
                        for tasks_day in (1,2,4):
                            demand=tasks_day*N
                            for basis in ('owned','new'):
                                for billing in ('bought','rented'):
                                    own=econ.own(key,team,demand,billing)
                                    for link in ('office_gigabit','measured_wifi_wan'):
                                        h=econ.hybrid(key,team,demand,basis,billing,link)
                                        cheap=api[model]['cheapest'];median=api[model]['median']
                                        cheap_month=cheap*demand*econ.days if isinstance(cheap,(int,float))else cheap
                                        median_month=median*demand*econ.days if isinstance(median,(int,float))else median
                                        rows.append(dict(profile=profile,model=model,server=key,target_depth=limit,team=team,tasks_day=tasks_day,
                                            calls_per_task=N,client_basis=basis,billing=billing,link=link,**h,
                                            usd_per_task=old.ratio(h['person_month'],tasks_day*econ.days),
                                            own_cluster_person_month=own['person_month'],own_cluster_boxes=own['boxes'],
                                            api_cheapest_person_month=cheap_month,api_median_person_month=median_month,
                                            median_over_hybrid=old.ratio(median_month,h['person_month']),
                                            basis='same synthetic growing task; R20 integer node/residency/finite-team bounds; hybrid fleet sufficient not minimal; GLM all rates and Qwen deep prefill/decode/import projections unmeasured/mixed priority; YaRN4 on hybrid Qwen, API extension unknown; no persistence guarantee'))
    result=dict(scenario='million-growth-r21',tables=[],sources=inputs.used,files=inputs.files,alarms=[],computed_metrics=0,export_namespace='growth21',notes=[
        'Growing-to200k and1M tasks supplement stationary1M calls. Conditional mean input by depth, mean output, median pause; no observed correlations or real sessions.',
        'GLM328GB FP8 uses twoB300 GPUs per replica/four replicas per eightGPU node. Prefill is Qwen wall-time times FLOP ratio; communication omitted. Studio cold1M57min,819.2GB/s*40%,8000USD/250W are unmeasured estimates. GLM wire statef32=152.6MB.',
        'Qwen M3 client decode carries inherited measured/interpolated mixed-priority anchors;1.04M1.67tok/s is background priority. Default B300 andFP8KV prefill beyond249k extrapolated. GLM no admitted API until endpoint metadata arrives.'])
    for name,data in (('growing_task_economics',rows),('growing_trace_summary',traces),('growing_api_admission',apis)):
        r16.add_table(result,name,data)
        for key in result['tables'][-1]['columns']:
            value=next((x[key]for x in data if not isinstance(x[key],dict)),None)
            result['tables'][-1]['columns'][key]='USD/task'if key=='usd_per_task'else r.unit(key,value)
    old.r18_sources(inputs)
    for path in (Path(__file__),d.CONFIG,d.STATS):
        name=str(path.relative_to(ROOT));inputs.files[name]=dict(path=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    return result
