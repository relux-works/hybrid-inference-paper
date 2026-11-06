"""Discrete CUDA clients and one ephemeral Qwen rental-task scenario."""
import hashlib
import json
import math
from pathlib import Path

from .inputs import InputGap, ROOT
from .measurements_r13 import verified_archive, rows
from .measurements_r14 import one_file, raw_table
from . import measurements_r16 as r16, measurements_r17 as r17

CONFIG=Path(__file__).parent/'data/run18-measurements.json'


def config():
    return json.loads(CONFIG.read_text())


def package(key, cfg=None):
    info=(cfg or config())['sources'][key]
    digest=info['sha256']
    if not (digest.startswith(info['facts_prefix']) and digest.endswith(info['facts_suffix'])):
        raise InputGap('run18.custody','FACTS checksum discrepancy requires source correction: '+key)
    return verified_archive(ROOT/info['path'],digest)


def positive(value,name,zero=False):
    r16.nonnegative(value,name)
    if not zero and value==0:raise InputGap('run18.'+name,'positive value required')
    return value


def normal_priority(manifest,payload):
    if manifest.get('normal_priority') is not True or manifest.get('priority_override_used') is not False:
        raise InputGap('run18.priority','recorded normal priority without override required')
    _,b=one_file(payload,'OPERATOR-READINESS','.json');record=json.loads(b)
    samples=record.get('samples',[]);servers=[s for r in samples for s in r.get('servers',[])]
    if (record.get('normal_priority') is not True or record.get('override_used') is not False or not servers or
        any(r.get('platform')!='Linux' or r.get('violations') or r.get('normal_priority') is not True or r.get('override_used') is not False for r in samples) or
        any(s.get('nice')!=0 or s.get('scheduling_class')!='TS' or s.get('errors') for s in servers)):
        raise InputGap('run18.priority','Linux TS nice0 server evidence required')


def interpolate(points,depth):
    if depth<=points[0][0]:return points[0][1]
    if depth>points[-1][0]:raise InputGap('run18.coverage','depth beyond measured rate coverage')
    for (a,x),(b,y) in zip(points,points[1:]):
        if depth<=b:return x+(y-x)*(depth-a)/(b-a)


class Client:
    """Measured one-slot surface; memory admission is separate from rate coverage."""
    def __init__(self,key,cfg=None,evidence=None):
        cfg=cfg or config();self.key=key;self.info=cfg['clients'][key]
        self.card=self.info['card'];self.model=self.info['model'];self.cap=self.info['context_limit']
        expected_cap=99328 if key=='rtx3090_qwen27' else 262144 if self.model=='qwen27' else 131072
        if self.cap!=expected_cap:raise InputGap('run18.capacity','measured context limit cannot be enlarged')
        manifest,payload=evidence if evidence is not None else package(self.info['source'],cfg)
        normal_priority(manifest,payload)
        reference=r17.package(self.model+'_server')[0]
        if (manifest.get('kit_version')!='1.6.7' or manifest.get('llama_cpp_commit')!='dde879bc4f954b809892fd0d660515f42536394a' or
            manifest.get('model_sha256')!=reference['model_sha256']):
            raise InputGap('run18.rates','same measured model weights and kit/build required')
        self.payload=payload
        label='q27b' if self.model=='qwen27' else self.model
        self.source,b=one_file(payload,'-'+label+'-q4km-');records=rows(b)
        self.records=records;self.depths=self.info['depths']
        expected_depths=([16000,50000,86000] if key=='rtx3090_qwen27' else
                         [16000,50000,100000,150000,200000,249000] if self.model=='qwen27' else [16000,50000,100000,118000])
        if self.depths!=expected_depths:raise InputGap('run18.rates','complete measured ladder required')
        meta=[r for r in records if r['kind']=='meta'];server=[r for r in records if r['kind']=='server']
        if (len(meta)!=1 or self.card.replace('rtx','rtx-') not in meta[0].get('label','') or
            len(server)!=1 or server[0].get('n_ctx')!=self.cap or server[0].get('total_slots')!=1 or
            server[0].get('build')!='b12032-dde879bc4'):
            raise InputGap('run18.rates','device/model/context/build evidence mismatch')
        self.turns=[r for r in records if r['kind']=='turn']
        expected={(d,n) for d in self.depths for n in r16.DELTAS}
        if len(self.turns)!=len(expected) or {(r['level'],r['delta']) for r in self.turns}!=expected:
            raise InputGap('run18.rates','complete distinct delta grid required')
        for r in self.turns:
            if (r.get('truncated') is not False or r.get('gen_tokens_exact') is not True or r.get('reread') is not False or
                r.get('cache_reused') is not True or r.get('predicted_n')!=128 or
                r.get('prompt_n') not in (r['delta'],r['delta']+1) or
                r.get('depth')!=r['level']+{512:0,2000:640,10000:2768}[r['delta']]):
                raise InputGap('run18.rates','exact cached delta/framing observations required')
            for k in ('prompt_ms','predicted_ms'):positive(r.get(k),k)
            self.admit(r['depth'],r['prompt_n'],r['predicted_n'])
        self.rates={n:sorted((r['level'],r['prompt_n']*1000/r['prompt_ms']) for r in self.turns if r['delta']==n) for n in r16.DELTAS}
        self.decode_points=[(d,sum(r['predicted_n']*1000/r['predicted_ms'] for r in self.turns if r['level']==d)/3) for d in self.depths]
        segments=[r for r in records if r['kind']=='segment']
        if len(segments)!=len(self.depths) or [r['depth'] for r in segments]!=self.depths:
            raise InputGap('run18.rates','complete cold segment grid required')
        for i,r in enumerate(segments):
            if (r['depth_from']!=(0 if i==0 else self.depths[i-1]+12896) or
                r['prompt_n'] not in (r['depth']-r['depth_from'],r['depth']-r['depth_from']+1) or
                r.get('truncated') is not False or r.get('gen_tokens_exact') is not True or
                r.get('reread') is not False or r.get('cache_reused') is not True):
                raise InputGap('run18.rates','cold fill/probe boundaries disagree')
            positive(r['prompt_ms'],'cold_prompt_ms')
        self.cold_points=[((r['depth_from']+r['depth'])/2,r['prompt_n']*1000/r['prompt_ms']) for r in segments]
        self.parallel=self.parallel_points(payload,label)

    def admit(self,depth,delta=0,output=0):
        for name,v in (('depth',depth),('delta',delta),('output',output)):positive(v,name,True)
        if depth+delta+output>self.cap:
            raise InputGap('run18.capacity','session exceeds hard context capacity '+str(self.cap))

    def for_delta(self,depth,delta):
        self.admit(depth,delta)
        if depth>self.depths[-1]:raise InputGap('run18.coverage','depth beyond measured rate coverage')
        n=min(10000,max(512,delta))
        return interpolate([(k,interpolate(self.rates[k],depth)) for k in r16.DELTAS],n)

    def decode(self,depth):
        self.admit(depth)
        return interpolate(self.decode_points,depth)

    def cold_seconds(self,depth):
        self.admit(depth)
        if depth>self.depths[-1]:raise InputGap('run18.coverage','cold depth beyond measured coverage')
        # Last measured segment's marginal rate holds to its measured endpoint;
        # no extrapolation beyond the ladder endpoint is admitted.
        points=[(0,self.cold_points[0][1])]+self.cold_points+[(self.depths[-1],self.cold_points[-1][1])]
        seconds=0
        for (a,x),(b,y) in zip(points,points[1:]):
            width=min(depth,b)-a
            if width<=0:break
            slope=(y-x)/(b-a)
            seconds+=width/x if slope==0 else math.log1p(slope*width/x)/slope
            if depth<=b:break
        return seconds

    def parallel_points(self,payload,label):
        out=[]
        for name,b in payload.items():
            if not name.endswith('.jsonl'):continue
            records=rows(b)
            if '-'+label+'-par' in name:
                servers=[r for r in records if r['kind']=='server'];ps=[r for r in records if r['kind']=='parallel']
                if len(servers)!=1 or len(ps)!=1:raise InputGap('run18.parallel','single32k parallel/control row required')
                r=ps[0];s=servers[0];count=r['streams']
                if count!=s['total_slots'] or r['depth']!=32000 or s['n_ctx']<r['depth']+128:
                    raise InputGap('run18.parallel','32k server shape mismatch')
                for n,rate in ((1,r['single_decode_tok_s']),(count,r['aggregate_decode_tok_s'])):
                    positive(rate,'parallel_rate')
                    out.append(dict(client=self.key,model=self.model,depth=r['depth'],streams=n,server_np=s['total_slots'],
                        n_ctx_slot=s['n_ctx'],aggregate_tok_s=rate,source=name,
                        protocol='step50 reported n/elapsed aggregate; single control; one round; no cooled-median claim'))
            elif name.startswith('results/parallel-depth-') and '-'+label+'-' in name:
                meta=[r for r in records if r['kind']=='meta'];rs=[r for r in records if r['kind']=='round']
                if len(meta)!=1 or not rs:raise InputGap('run18.parallel','complete parallel round metadata required')
                m=meta[0]
                if (m.get('rounds')!=1 or m.get('cooldown_s')!=0 or len(rs)!=len(m['streams']) or
                    {r['streams'] for r in rs}!=set(m['streams'])):
                    raise InputGap('run18.parallel','complete one-round count grid required')
                for r in rs:
                    count=r['streams'];req=r['requests']
                    if (r.get('valid') is not True or r.get('errors') or r.get('restore_reused') is not True or
                        r['depth']!=m['depth']+16 or len(req)!=count or r['server_np']!=m['server_np'] or
                        r['n_ctx_slot']!=m['n_ctx_slot'] or count>r['server_np'] or r['depth']+128>r['n_ctx_slot']):
                        raise InputGap('run18.parallel','valid restored count/shape/capacity required')
                    for q in req:
                        if q.get('prompt_n')!=16 or q.get('predicted_n')!=128:raise InputGap('run18.parallel','exact generated interval count required')
                        positive(q['predicted_ms'],'parallel_predicted_ms')
                    rate=sum(q['predicted_n']-1 for q in req)/max(q['predicted_ms']/1000 for q in req)
                    if abs(rate-r['aggregate_tok_s'])>.00051:raise InputGap('run18.parallel','aggregate interval mismatch')
                    out.append(dict(client=self.key,model=self.model,depth=r['depth'],streams=count,server_np=r['server_np'],
                        n_ctx_slot=r['n_ctx_slot'],aggregate_tok_s=rate,source=name,
                        protocol='step55 n-1 decode intervals; one restored round; zero cooldown; not R16 cooled medians'))
        counts={(r['depth'],r['streams'],r['server_np']) for r in out}
        first_np=2 if self.key=='rtx3090_qwen27' else 4
        expected={(32000,n,first_np) for n in (1,first_np)}
        if self.model=='glimmer30':
            np=8 if self.card=='rtx3090' else 16
            expected|={(65552,n,np) for n in (1,2,4,8) if n<=np}
            if np==16:expected.add((65552,16,16))
        elif self.card=='rtx3090':expected.add((65552,1,1))
        else:
            expected|={(65552,n,4) for n in (1,2,4)}|{(131088,n,2) for n in (1,2)}|{(260016,1,1)}
        if counts!=expected or len(counts)!=len(out):
            raise InputGap('run18.parallel','complete distinct parallel shape grid required')
        return sorted(out,key=lambda r:(r['depth'],r['streams']))

    def parallel_at(self,streams,depth,server_np):
        self.admit(depth)
        if type(streams) is not int or streams<1:raise InputGap('run18.parallel','positive integer stream count required')
        matches=[r for r in self.parallel if (r['streams'],r['depth'],r['server_np'])==(streams,depth,server_np)]
        if len(matches)!=1:raise InputGap('run18.parallel','unmeasured count/depth/server shape')
        return matches[0]


def cuda_depth_fit():
    """Joint OLS of verified PR9 import seconds against delta and prefix depth.

    The intercept is refitted with both predictors, so it cannot retain the
    depth already absorbed in the old marginal CUDA intercept. Full-slot file
    timings do not identify this endpoint's recovery component separately.
    """
    from .run14_r5 import cuda_import_rows
    points=cuda_import_rows()
    values=[]
    for row in points:
        n=positive(row.get('remote_applied'),'cuda_delta',True)
        d=positive(row.get('depth_before'),'cuda_depth',True)
        t=positive(row.get('import_ms'),'cuda_import_ms')/1000
        values.append((n,d,t))
    means=[sum(p[i] for p in values)/len(values) for i in range(3)]
    centered=[tuple(v-m for v,m in zip(p,means)) for p in values]
    nn=sum(n*n for n,d,t in centered);dd=sum(d*d for n,d,t in centered)
    nd=sum(n*d for n,d,t in centered)
    nt=sum(n*t for n,d,t in centered);dt=sum(d*t for n,d,t in centered)
    determinant=nn*dd-nd*nd
    if determinant<=0:
        raise InputGap('run18.cuda_import','independent delta and depth observations required')
    token=(nt*dd-dt*nd)/determinant
    depth=(dt*nn-nt*nd)/determinant
    fixed=means[2]-token*means[0]-depth*means[1]
    if fixed<=0 or token<=0 or depth<0:
        raise InputGap('run18.cuda_import','positive intercept/token and nonnegative CUDA depth fit required')
    return fixed,token,depth


def cuda_import(delta,depth,model,*,depth_basis='cuda_pr9'):
    """CUDA-only joint fit; portability to these cards and SWA is estimated."""
    positive(delta,'delta',True);positive(depth,'depth',True)
    if depth_basis!='cuda_pr9':
        raise InputGap('run18.cuda_import','CUDA depth evidence required; Mac slope forbidden')
    if model not in ('qwen27','glimmer30'):
        raise InputGap('run18.cuda_import','unqualified model portability')
    fixed,token,slope=cuda_depth_fit()
    return fixed+token*delta+slope*depth


def threshold_rows(clients):
    result=[];rtt=r16.config()['wire']['threshold_rtt_s']
    for client in clients:
        server=r17.Surface(client.model,'server');geometry=r17.geometry(client.model)
        for fmt in (('f32','bf16') if client.model=='qwen27' else ('f32',)):
            for depth in r17.DEPTHS:
                for delta in r17.DELTAS:
                    row=dict(client=client.key,model=client.model,state_format=fmt,depth=depth,delta=delta,
                        context_limit=client.cap,wire_bytes=r17.offload_bytes(geometry,delta,depth,fmt),
                        local_prefill_s=0,server_prefill_s=delta/server.for_delta(depth,delta),
                        import_s=cuda_import(delta,depth,client.model),rtt_s=rtt,budget_s=0,
                        break_even_downstream_mb_s=0,break_even_downstream_mbit_s=0,threshold_status='',
                        background_priority_interim=False,
                        import_assumption='cuda_pr9_joint_delta_depth_portability; full-slot file timings diagnostic only; not measured on3090/5090; SWA portability unmeasured',
                        state_quality='pending measured quality of dev-a r38' if fmt=='bf16' else 'f32 reference')
                    try:local=delta/client.for_delta(depth,delta)
                    except InputGap as exc:
                        if exc.path not in ('run18.capacity','run18.coverage'):raise
                        row['threshold_status']='capacity_refused' if exc.path=='run18.capacity' else 'unmeasured_rate'
                        alarm={'alarm':[exc.alarm()]}
                        for k in ('local_prefill_s','budget_s','break_even_downstream_mb_s','break_even_downstream_mbit_s'):row[k]=alarm
                    else:
                        row['local_prefill_s']=local;budget=local-row['server_prefill_s']-row['import_s']-rtt
                        row['budget_s']=budget
                        if budget<=0:
                            row['threshold_status']='never_pays_nonpositive_budget'
                            alarm={'alarm':[dict(input='downstream',reason='no finite downstream rate can beat local prefill')]}
                            row['break_even_downstream_mb_s']=alarm;row['break_even_downstream_mbit_s']=alarm
                        else:
                            speed=row['wire_bytes']/budget
                            row.update(threshold_status='finite_threshold',break_even_downstream_mb_s=speed/1e6,break_even_downstream_mbit_s=speed*8/1e6)
                    result.append(row)
    return result


def rental_bill(calls,per_call_s,cold_s,fetch_s,hourly,task_calls,billing):
    """Each independent rental loses both model and session; partial tasks pay too."""
    for k,v in (('calls',calls),('per_call_s',per_call_s),('cold_s',cold_s),('fetch_s',fetch_s),('hourly',hourly),('task_calls',task_calls)):
        positive(v,k,k in ('calls','per_call_s','cold_s','hourly'))
    if type(calls) is not int or type(task_calls) is not int:raise InputGap('run18.rental','integer call/task counts required')
    if billing not in ('ceil_hour_assumption','prorated_hourly_quote'):raise InputGap('run18.rental','unknown billing rule')
    full,remainder=divmod(calls,task_calls)
    def charge(n):
        seconds=fetch_s+cold_s+n*per_call_s
        return (math.ceil(seconds/3600) if billing=='ceil_hour_assumption' else seconds/3600)*hourly
    return full*charge(task_calls)+(charge(remainder) if remainder else 0)


def economics(inputs,scenario,clients):
    """A common measured-capacity subset; full-distribution infeasibility explicit."""
    from .engine import load
    from .paper_tables import Context,person_tables
    spec,_=load('paper-tables-r17');c=Context(spec,inputs)
    calls=c.g.resolve(c.valid)
    if calls.alarms:raise InputGap('run18.workload',str(calls.alarms))
    calls=calls.value;qwen=[p for p in clients if p.model=='qwen27']
    def eligible(p,row):
        d,n,o,t=row
        return d+n+o<=min(p.cap,p.depths[-1])
    common=[r for r in calls if all(eligible(p,r) for p in qwen)]
    if not common:raise InputGap('run18.workload','no common measured-capacity calls')
    # The same conditional call distribution is fed to every alternative.
    c.valid=c.label('r18.common_workload',common)
    c.scenario=dict(spec,economics_clients=['m3max'],share_keys=['academic_s100'])
    person_tables(c)
    comparison=c.g.result(scenario['name'])
    row=next(r for r in comparison['tables'][0]['rows'] if r['client'].startswith('M3') and r['team']==5 and r['basis']=='Mac already owned')
    cfg=config()['rental'];task=cfg['calls_per_rental'];month_calls=round(inputs.get('owners.calls_day')*inputs.get('owners.days'))
    out=[]
    for p in qwen:
        per_call=sum(n/p.for_delta(d,n)+o/p.decode(d+n)+t for d,n,o,t in common)/len(common)
        cold=sum(p.cold_seconds(d) for d,n,o,t in common)/len(common)
        price=cfg['prices'][p.card]
        for price_case in ('search_low','rented','search_high'):
            hourly=price[price_case]
            for billing in ('ceil_hour_assumption','prorated_hourly_quote'):
                cost1000=rental_bill(1000,per_call,cold,price['download_s'],hourly,task,billing)
                costmonth=rental_bill(month_calls,per_call,cold,price['download_s'],hourly,task,billing)
                out.append(dict(client=p.key,model=p.model,workload='common_measured_capacity_subset',
                    coverage_call_share=len(common)/len(calls),device_capacity_share=sum(d+n+o<=p.cap for d,n,o,t in calls)/len(calls),
                    device_measured_coverage_share=sum(eligible(p,r) for r in calls)/len(calls),
                    context_limit=p.cap,rate_depth_limit=p.depths[-1],calls_per_rental=task,price_case=price_case,
                    observed_hourly_usd=hourly,price_basis=cfg['price_basis'],observed_date=cfg['observed_date'],billing=billing,
                    fetch_s_per_rental=price['download_s'],cold_prefill_s_per_rental=cold,warm_call_s=per_call,
                    full_task_wall_s=price['download_s']+cold+task*per_call,
                    rentals_per_1000_calls=math.ceil(1000/task),calls_person_month=month_calls,rentals_person_month=math.ceil(month_calls/task),
                    rented_usd_per_1000_calls=cost1000,rented_usd_person_month=costmonth,
                    rented_wall_hours_person_month=rental_bill(month_calls,per_call,cold,price['download_s'],1,task,'prorated_hourly_quote'),
                    rented_billed_hours_person_month=rental_bill(month_calls,per_call,cold,price['download_s'],1,task,billing),
                    api_cheapest_usd_per_1000_calls=row['api_cheapest']/month_calls*1000,
                    api_cheapest_usd_person_month=row['api_cheapest'],api_median_usd_per_1000_calls=row['api_median']/month_calls*1000,
                    api_median_usd_person_month=row['api_median'],hybrid_usd_per_1000_calls=row['hybrid_cheapest']/month_calls*1000,
                    hybrid_usd_person_month=row['hybrid_cheapest'],own_server_usd_per_1000_calls=row['own_cluster']/month_calls*1000,
                    own_server_usd_person_month=row['own_cluster'],
                    background_priority_interim=r16.config()['m3_parallel']['background_priority_interim'],
                    persistence='none across rentals; fresh model fetch and cold prefix every rental',
                    comparator_basis='Qwen; same conditional fitted call mix; hybrid M3 already owned plus API overflow; own B300 five-person allocation; not same hardware or API model-identity claim; M3 parallel qualification follows R16b data'))
    coverage=[]
    for p in clients:
        fits=sum(d+n+o<=p.cap for d,n,o,t in calls)
        measured=sum(eligible(p,r) for r in calls)
        coverage.append(dict(client=p.key,model=p.model,context_limit=p.cap,rate_depth_limit=p.depths[-1],
            full_workload_supported=fits==len(calls),capacity_fit_calls=fits,rate_covered_calls=measured,total_calls=len(calls),
            capacity_share=fits/len(calls),measured_share=measured/len(calls),
            full_workload_rental_cost={'alarm':[dict(input='run18.capacity',reason='full fitted workload exceeds hard client capacity; no fully-local quote')]},
            basis='No API fallback or context truncation in the rented-machine scenario; Glimmer model fetch time not supplied; rental price comparison uses Qwen'))
    return out,coverage


def record_sources(inputs):
    cfg=config()
    facts=cfg['facts'];b=(ROOT/facts['path']).read_bytes()
    if hashlib.sha256(b).hexdigest()!=facts['sha256']:raise InputGap('run18.facts','FACTS snapshot digest mismatch')
    inputs.files[facts['path']]=facts
    for key,info in cfg['sources'].items():
        _,payload=package(key,cfg)
        provenance=dict(kind='measured',package='GPU kit1.6.7 '+key,sha256=info['sha256'])
        inputs.files[info['path']]=dict(path=info['path'],sha256=info['sha256'],provenance=provenance)
        for name,b in payload.items():
            path=info['path']+'::'+name
            inputs.files[path]=dict(path=path,sha256=hashlib.sha256(b).hexdigest(),provenance=provenance)
    path=str(CONFIG.relative_to(ROOT));inputs.files[path]=dict(path=path,sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest())
    from .run14_r5 import cuda_import_rows,evidence
    cuda_import_rows() # Verify the exact bytes used by the joint fit before recording custody.
    info=evidence()['cuda_pr9'];inputs.files[info['path']]=dict(info,provenance=dict(kind='measured',package='PR9 CUDA joint delta/depth import fit'))
    r16.record_sources(inputs);r17.record_sources(inputs)


def calculate(scenario,inputs):
    clients=[Client(key) for key in config()['clients']]
    result=dict(scenario=scenario['name'],tables=[],alarms=[],computed_metrics=0,notes=[],export_namespace='r18')
    probes=[]
    for p in clients:
        for r in p.turns:
            probes.append(dict(client=p.key,model=p.model,depth=r['level'],actual_depth=r['depth'],delta=r['delta'],
                context_limit=p.cap,prefill_tok_s=r['prompt_n']*1000/r['prompt_ms'],
                decode_tok_s=r['predicted_n']*1000/r['predicted_ms'],depth_decode_mean_tok_s=dict(p.decode_points)[r['level']],
                source=p.source,priority_basis='recorded Linux TS nice0; kit1.6.7'))
    rental,coverage=economics(inputs,scenario,clients)
    for key,data in (('gpu_client_rates',probes),('gpu_client_parallel',sum((p.parallel for p in clients),[])),
                     ('gpu_link_threshold',threshold_rows(clients)),('rented_machine_comparator',rental),('gpu_capacity_coverage',coverage)):
        r16.add_table(result,key,data)
    for table in result['tables']:
        for key in table['columns']:
            if 'usd_per_1000_calls' in key:table['columns'][key]='USD/1000 calls'
            elif 'usd_person_month' in key:table['columns'][key]='USD/person-month'
            elif key=='observed_hourly_usd':table['columns'][key]='USD/hour'
            elif key.endswith('hours_person_month'):table['columns'][key]='GPU-machine hours/person-month'
            elif key in ('context_limit','rate_depth_limit','n_ctx_slot'):table['columns'][key]='token'
            elif key in ('capacity_fit_calls','rate_covered_calls','total_calls','calls_person_month'):table['columns'][key]='call'
            elif key=='calls_per_rental':table['columns'][key]='call/rental'
    result['notes'].append('Run18: GPU context caps are hard; rate coverage is separately bounded by measured ladders. Shallow depths and deltas outside512..10000 hold nearest endpoint as an estimate. Parallel rows preserve np/context/protocol; no unmeasured shapes. Threshold import uses the joint PR9 CUDA delta/depth fit, unmeasured on these cards/SWA. Native full-slot file save/restore timings cannot separately identify imported-delta recovery, so remain diagnostics; no Mac slope or additional slot cost is composed with the fit. Rental scenario uses Qwen, fresh fetch and cold prefix per task, no persistence; observed offers are dated observations, not market rates. Hour rounding is an assumption, not asserted Vast billing. The full fitted workload exceeds these cards; costs condition all alternatives on the same common measured-capacity subset, without truncation or API fallback in the rental. R16b and SWA Mac PRI31 input interfaces remain unchanged.')
    record_sources(inputs)
    return result
