"""Closed-contour contracts and explicitly unmeasured GLM/Ultra projections."""
import copy
import functools
import json
import math
from pathlib import Path

from hybridcalc.inputs import InputGap
from hybridcalc import measurements_r20 as old, measurements_r19 as r19
from hybridcalc import measurements_r16 as r16, server_economics_r20 as s
from run22.measurements import Mac

DATA=Path(__file__).parent


@functools.lru_cache(maxsize=1)
def config():
    return json.loads((DATA/'config.json').read_text())


def finite(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def hybrid_admission(kind,weight_bytes,memory_bytes,session_bytes=0,reserve_bytes=4e9):
    """The requested cloud FP8 model cannot be smuggled into a client scenario."""
    if any(not finite(x) or x<0 for x in (weight_bytes,memory_bytes,session_bytes,reserve_bytes)):
        raise InputGap('run26.client','invalid memory quantity')
    if kind=='cloud' or weight_bytes+session_bytes+reserve_bytes>.9*memory_bytes:
        raise InputGap('run26.client','model does not fit client; cloud-class hybrid inapplicable')
    if kind!='middle':
        raise InputGap('run26.client','unknown model class')
    return True


def prefill_only(row):
    """Preserve refusal: server generation is a separate architecture sensitivity."""
    result=dict(row)
    if not finite(row.get('person_month')):
        result.update(person_month=None,status=row.get('status','capacity_shortfall'),feasible=False)
    elif row.get('server_decode_overflow_day',0)>1e-9:
        result.update(person_month=None,status='client_decode_capacity_shortfall',feasible=False)
    else:
        result.update(status='feasible_prefill_only',feasible=True)
    return result


def capital(price,inputs,basis):
    if basis not in ('owned','new'):
        raise InputGap('run26.client','owned or new client basis required')
    return 0. if basis=='owned' else price*(1-inputs.get('economics.client_residual'))/(12*inputs.get('owners.years'))


def expert_partition(total,active,experts,topk):
    """Solve Ptotal=A+R and Pactive=A+R*k/E, with uniform equal experts."""
    if not(0<topk<experts and total*topk/experts<active<total):
        raise InputGap('run26.experts','inconsistent active/total parameters or routing')
    shared=(active-total*topk/experts)/(1-topk/experts)
    return shared,total-shared


def expert_traffic(batch,depth,weight_bytes,total,active,experts,topk,kv,state):
    r19.integer(batch,'batch');r16.nonnegative(depth,'depth')
    shared,routed=expert_partition(total,active,experts,topk)
    union=experts*(-math.expm1(batch*math.log1p(-topk/experts)))
    return weight_bytes*(shared+routed*union/experts)/total+batch*(kv*depth+state)


@functools.lru_cache(maxsize=1)
def architecture():
    cfg=config();c=json.loads((DATA/'data/glm-config.json').read_text())['text_config']
    linear=c['linear_attn_config'];L=len(linear['kda_layers']);A=len(linear['full_attn_layers'])
    # Layout estimates, NOT measured slot geometry. MLA latent only, q8_0 scale overhead.
    state=L*(linear['num_heads']*linear['head_dim']**2*4+
             3*linear['num_heads']*linear['head_dim']*(linear['short_conv_kernel_size']-1)*4)
    return dict(total=cfg['glm_total_parameters'],active=cfg['glm_active_parameters'],
                experts=c['n_routed_experts'],topk=c['num_experts_per_tok'],
                layers=c['num_hidden_layers'],linear_layers=L,full_layers=A,
                latent=c['kv_lora_rank'],client_kv=A*c['kv_lora_rank']*34/32,
                server_kv=A*c['kv_lora_rank']*2,state=state,wire_state=state/2,
                context=c['max_position_embeddings'],heads=c['num_attention_heads'],
                head_dim=c['qk_head_dim'],sparse_cap=c['index_topk'])


def glm_flops(depth):
    a=architecture()
    # Explicit portability proxy: active matmuls + bounded sparse attention + recurrent matrices.
    return 2*a['active']+4*a['full_layers']*a['heads']*a['head_dim']*min(depth,a['sparse_cap'])+4*a['linear_layers']*64*128**2


def qwen_flops(depth):
    return 54e9+393216*depth


class GlmServer:
    """Two B300 per replica; four complete replicas per paid eight-GPU node."""
    key='glm_two_b300';engine='vllm'
    def __init__(self,qwen,slowdown=1,cfg=None):
        self.cfg=cfg or config();self.a=architecture();self.qwen=qwen;self.slowdown=slowdown
        if slowdown not in self.cfg['glm_prefill_slowdowns']:
            raise InputGap('run26.prefill','declared unmeasured prefill sensitivity required')
        self.weights=self.cfg['glm_server_weights_bytes'];self.kv=self.a['server_kv'];self.state=self.a['state']
        self.free=2*288e9-self.weights-2*8e9
        self.info=dict(host='b300',hourly_usd=76)
    def session_bytes(self,depth):
        return self.kv*depth+self.state
    def slots(self,depth):
        n=math.floor(self.free/self.session_bytes(depth))
        if n<1:raise InputGap('run26.server','complete GLM session does not fit two B300')
        return n
    def cached(self,depth,n,bridge='none'):
        if n<0 or depth<0 or depth+n>self.a['context']:
            raise InputGap('run26.context','GLM context envelope exceeded')
        # Optimistic equal compute efficiency/two-GPU sum; x2 slowdown exposes portability.
        return self.qwen.cached(depth,n,bridge)*glm_flops(depth+n/2)/qwen_flops(depth+n/2)/2*self.slowdown
    def cold(self,depth):
        # Constant-at-end FLOP ratio proxy; not a measured rebuild or a bound.
        return self.qwen.cold(depth)*glm_flops(depth)/qwen_flops(depth)/2*self.slowdown
    def decode(self,depth,streams=32,measurements=None):
        k=min(streams,self.slots(depth));a=self.a
        def traffic(b):
            return expert_traffic(b,depth,self.weights,a['total'],a['active'],a['experts'],a['topk'],self.kv,self.state)
        bw=2*8e12*self.cfg['glm_server_bandwidth_efficiency']
        single=bw/traffic(1);agg=k*bw/traffic(k)
        return dict(batch=k,single_tok_s=single,aggregate_tok_s=agg,gain=agg/single,
                    basis='UNMEASURED uniform expert union, full per-session MLA KV; ideal two-B300 bandwidth sum, communication omitted')


class Ultra:
    """All GLM timings are extrapolated from recorded-PRI31 M5 Max Qwen."""
    def __init__(self,memory=256e9,cfg=None):
        self.cfg=cfg or config();self.a=architecture();self.mac=Mac('qwen','m5max64');self.memory=memory
        self.weights=self.cfg['glm_client_weights_bytes']
    def slots(self,depth):
        hybrid_admission('middle',self.weights,self.memory,
                         self.a['client_kv']*depth+self.a['state'],self.cfg['client_reserve_bytes'])
        return math.floor((self.cfg['client_usable_fraction']*self.memory-self.weights-self.cfg['client_reserve_bytes'])/
                          (self.a['client_kv']*depth+self.a['state']))
    def prefill(self,depth,n):
        return self.mac.prefill(depth,n)*glm_flops(depth+n/2)/qwen_flops(depth+n/2)/self.cfg['ultra_compute_scale']
    def decode(self,depth,streams=1):
        k=min(streams,self.slots(depth));a=self.a
        # Effective bandwidth inferred from measured Max single stream, then doubled.
        effective=self.mac.decode(1,depth)*(18973870432+34816*depth+156893184)
        traffic=expert_traffic(k,depth,self.weights,a['total'],a['active'],a['experts'],a['topk'],a['client_kv'],a['state'])
        return effective*self.cfg['ultra_bandwidth_scale']/traffic # per stream, not aggregate


class GlmPrepared(old.Prepared):
    def __init__(self,calls,server,client,context):
        self.calls=calls;self.context=context;self.client=client;self.server=server
        self.profiles={x['key']:x for x in r19.links(context.inputs)}
        fields=('own','pre','shadow','output','wire','imports','rebuild','decode_device','decode_occupied','wait_weight')
        for name in fields:setattr(self,name,[])
        u=Ultra(256e9 if client=='ultra256' else 512e9);importer=r16.ClientImport();a=server.a
        for d,n,o,t in calls:
            server.slots(d+n+o);k=min(4,u.slots(d+n+o));rate=u.decode(d+n,k)
            self.own.append(u.prefill(d,n));self.pre.append(server.cached(d,n,'measured_envelope'))
            base=server.cached(d,n);self.shadow.append(base*(n+o)/n);self.output.append(base*o/n)
            self.wire.append(n*a['client_kv']+a['wire_state'])
            self.imports.append(importer.at_depth(n,d));self.rebuild.append(server.cold(d))
            self.decode_device.append(o/(k*rate));self.decode_occupied.append((o/rate+t)/k);self.wait_weight.append(1/k)


class GlmEconomics(old.Economics):
    def __init__(self,context,calls,server,cfg):
        super().__init__(context,calls,{server.key:server},cfg,{})
        for billing in ('bought','rented'):
            month,_=self.units[server.key,billing];self.units[server.key,billing]=month,4
        for client in ('ultra256','ultra512'):
            self.prepared[server.key,client,'measured_envelope']=GlmPrepared(calls,server,client,context)

    @functools.lru_cache(maxsize=None)
    def hybrid(self,team,demand,client,basis,billing):
        key='glm_two_b300';sv=self.servers[key];p=self.prepared[key,client,'measured_envelope']
        month,replicas=self.units[key,billing];boxes=self.storage_boxes(sv,team,replicas)
        link='office_gigabit' if billing=='bought' else 'engine_wan'
        # Storage floor and monotonically sufficient prefill-only fleet; no generation fallback.
        while True:
            spill,host=self.retention(sv,team,boxes,replicas);stat=p.stats(spill,link)
            if demand>stat['client_capacity_day']+1e-9:
                # Better residency might cure prefill waits; test all-resident upper certificate.
                if spill and demand<=p.stats(0,link)['client_capacity_day']:
                    boxes=max(boxes+1,math.ceil(team*self.sessions/(sv.slots(self.cfg['reservation_depth'])*replicas)))
                    continue
                return dict(person_month=None,boxes=boxes,status='client_decode_capacity_shortfall',feasible=False,
                            client_capacity_day=stat['client_capacity_day'],server_decode_overflow_day=0)
            work=demand*stat['gpu_s_call'];needed=max(1,math.ceil(team*work/(self.hours*3600*self.load*replicas)))
            if needed<=boxes:break
            boxes=needed
        cfg=config();device=capital(cfg['studio_price_proxy_usd'][client],self.inputs,basis)
        energy=cfg['ultra_power_kw']*self.hours*self.days*self.inputs.get('prices.energy_client')
        store=host/1e9*self.inputs.get('hosting.tiers.NVMe.price')/team if billing=='rented' else 0
        egress=demand*self.days*stat['wire_bytes_call']/1e12*self.inputs.get('prices.egress') if billing=='rented' else 0
        rho=team*work/(boxes*replicas*self.hours*3600)
        return dict(person_month=boxes*month/team+device+energy+self.inputs.get('owners.front_month')+store+egress,
                    boxes=boxes,status='feasible_prefill_only',feasible=True,service_utilization=rho,
                    calendar_utilization=rho*self.hours*self.days/730,device_month=device,
                    client_capacity_day=stat['client_capacity_day'],server_decode_overflow_day=0,
                    offload_share=stat['offload_share'],spill_share=spill)


def cloud_capacity(team,inputs,billing,share=1,retention="weights_only_floor"):
    """Capacity floor only: no 2.4T throughput or task completion inferred."""
    cfg=config()
    if not 0<=share<=1:raise InputGap('run26.cloud','share outside [0,1]')
    if share==0:return dict(nodes=0,person_month=0.,status='no_large_tasks')
    # Model card:23 full layers, K/V4heads x256 at bf16; recurrent69 layers.
    kv=23*2*4*256*2
    state=69*128*128*128*4
    copies=math.ceil(team*cfg['large_retained_sessions_per_person']*share)
    session=cfg['large_context']*kv+state
    unit_hbm=cfg['large_hbm_bytes_per_gpu']*8*cfg['large_residency_fraction']
    workspace=8*cfg['large_workspace_bytes_per_gpu']
    if retention not in ('weights_only_floor','all_resident_sessions'):
        raise InputGap('run26.cloud','unknown retention basis')
    nodes=math.ceil((cfg['large_fp8_weight_bytes']+(copies*session if retention=='all_resident_sessions' else 0))/(unit_hbm-workspace))
    from run23.economics import Server
    month,_=s.unit_month(Server('b300_fp8'),inputs,billing)
    return dict(nodes=nodes,person_month=nodes*month/team,unit_node_month=month,
                copies=copies,copy_bytes=session,kv_bytes_token=kv,state_bytes=state,
                hbm_node_bytes=cfg['large_hbm_bytes_per_gpu']*8,
                status='capacity_cost_floor_service_pending',retention_basis=retention,
                service_cost_pending=True,storage_cost_pending=retention=='weights_only_floor')


def mixed(middle_hybrid,middle_own,common):
    """Exact same common part; never treat 80% internal large-model calls as free."""
    if not finite(common) or common<0:raise InputGap('run26.mixed','invalid common cost')
    h=middle_hybrid+common if finite(middle_hybrid) else None
    o=middle_own+common if finite(middle_own) else None
    return dict(common_large_person_month=common,hybrid_common_large_person_month=common,
                own_common_large_person_month=common,total_hybrid_floor_person_month=h,
                total_own_floor_person_month=o,
                difference_person_month=middle_hybrid-middle_own if finite(middle_hybrid) and finite(middle_own) else None)
