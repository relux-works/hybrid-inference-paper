"""Review accounting sensitivity and three explicitly estimated paper examples."""
import copy
import math
from .analysis_graph import mean_flops
from .inputs import Inputs,InputGap
from .metrics import unique
from .paper_tables import Context,person_tables
from .paper_tables_r7 import R7,integrate_span,arch_geometry,arch_flops,arch_delta
from .performance import flop,payload,transfer
from .session_hosting import policy_with_reload


def people_table(c):
    m=c.model('qwen27');rows=[]
    work=c.add('people.work',[c.valid,m['flop']],mean_flops)
    for key in c.scenario['prefill_options']:
        s=c.server(key,m);p=s['prefix']
        def one(rate,gpus,free):
            if gpus!=1:raise InputGap(p+'.gpus','people-per-GPU chart requires a single GPU')
            return rate
        compute=c.add('people.'+key+'.compute',[s['compute'],p+'.gpus',s['free']],one)
        # Complete end-of-call context must fit a replica before any capacity is quoted.
        def fit(rows,free,kv,state):
            if any((d+n+o)*kv+state>free for d,n,o,t in rows):raise InputGap(p+'.memory','sample session exceeds one GPU replica memory')
            return True
        ready=c.add('people.'+key+'.fit',[c.valid,s['free'],m['kv'],m['state']],fit)
        seconds=c.add('people.'+key+'.seconds',[work,compute,ready],lambda f,c,ready:f/c)
        local=c.local_rate(c.scenario['people_reference_client'],m)
        wire=c.add('people.'+key+'.wire',[m['flop'],m['kv'],m['state']],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
        link=c.g.bundle('pt.people.'+key+'.link','hardware.links.wan',('bandwidth','goodput','latency'))
        migration=c.hosting.vector('people.'+key,c.valid,m['kv'],m['state'])
        steps=c.add('people.'+key+'.steps',[c.valid,wire,compute,link,local,migration],policy_with_reload)
        host=c.hosting.summary('people.'+key+'.budget',c.valid,m['kv'],m['state'],steps)
        for j,share in enumerate(c.positions('r8.shares')):
            n='people.'+key+'.'+str(j)
            demand=c.add(n+'.demand',['service.profiles.heavy',share],lambda calls,s:calls*s)
            budget=c.add(n+'.window',['paper_tables.hours','owners.load'],lambda h,l:h*3600*l)
            daily=c.hosting.daily(n,host,demand)
            migration_call=c.add(n+'.migration_call',[daily,demand],lambda io,calls:io/calls)
            row=dict(gpu=s['label'],server_precision=c.precision_label,share=share,hours='paper_tables.hours',load='owners.load',calls_user_day=demand,
                     shadow_gpu_s_call=seconds,migration_gpu_s_call=migration_call,storage_user_month=host['storage'],
                     people_compute_only=c.add(n+'.compute_only',[budget,demand,seconds],lambda b,n,s:math.floor(b/n/s)),
                     people_with_hosting=c.add(n+'.hosting',[budget,demand,seconds,daily],lambda b,n,s,io:math.floor(b/(n*s+io))))
            rows.append(row)
    c.table('people_per_gpu','Heavy users per single GPU: all-call input/output shadow, with and without cold-tier migration',
            {k:'text' if k in ('gpu','server_precision') else 'person' if k.startswith('people_') else 's/call' if k.endswith('s_call') else 'USD/person-month' if k=='storage_user_month' else 'call/person/day' if k=='calls_user_day' else 'h/day' if k=='hours' else '1' for k in rows[0]},rows)


def transcript_table(r):
    c=r.c;rows=[];m=r.model
    for key in c.scenario['transcript_clients']:
        cl=r.client(key,'f32');p=cl['prefix'];n='transcript.'+key
        reserve='r8.transcript.air_reserve' if key=='m5air32' else 'owners.client_reserve'
        final=r.add(n+'.final',['r8.transcript.tokens','r8.transcript.summary'],lambda n,o:n+o)
        def fit(d,limit,mem,res,w,kv,state):
            if d>limit:raise InputGap('r7.context_limit','transcript and summary exceed context limit')
            if w+d*kv+state+res>mem:raise InputGap(p+'.memory','transcript + summary + Q4 weights + reserve do not fit')
            return d
        admitted=r.add(n+'.fit',[final,'r7.context_limit',p+'.memory',reserve,m['weights'],c.kv,c.state],fit)
        def server_fit(d,free,kv,state):
            if d*kv+state>free:raise InputGap(r.server['prefix']+'.memory','transcript does not fit one server replica')
            return d
        server_ok=r.add(n+'.server_fit',[final,r.server['free'],c.kv,c.state],server_fit)
        local=r.add(n+'.local',['r8.transcript.tokens',cl['local'],'r7.integration_step',admitted],lambda n,rate,step,ok:integrate_span(lambda d:1/rate(d),0,n,step))
        server=r.add(n+'.server',['r8.transcript.tokens',m['flop'],r.compute,'r7.integration_step',server_ok],lambda n,m,c,step,ok:integrate_span(lambda d:flop(m,d)/c,0,n,step))
        size=r.add(n+'.size',['r8.transcript.tokens',c.kv,c.state],payload)
        imp=r.import_node(n+'.import',size,cl)
        last=r.add(n+'.last',[cl['rate'],'r8.transcript.tokens','r7.last_token_tokens',admitted],lambda rate,d,n,ok:n/rate(1,d))
        decode=r.add(n+'.decode',['r8.transcript.tokens','r8.transcript.summary',cl['rate'],'r7.integration_step',admitted],lambda d,n,rate,step,ok:integrate_span(lambda x:1/rate(1,x),d,n,step))
        apis={}
        for api in ('qwen_median','qwen_cheap'):
            apis[api]=r.add(n+'.api.'+api,['r8.transcript.tokens','r8.transcript.summary',m['api'][api][0]],lambda n,o,p:(n*p['cache_write']+o*p['output'])/1e6)
        for j,bw in enumerate(r.positions('r8.transcript.links')):
            nn=n+'.'+str(j);link=r.link(nn+'.link',bw)
            wire=r.add(nn+'.wire',['r8.transcript.tokens',c.kv,c.state,link],transfer)
            total=r.add(nn+'.ttft',[server,wire,imp,last],lambda *v:sum(v))
            rows.append(dict(client=p+'.label',basis=r.label(nn+'.basis','M3 measured curve/anchor; compute and bandwidth portability estimated; Air uses explicit 8 GB appliance reserve' if key!='m3max' else 'measured M3 prefill curve and decode anchor; depth scaling estimated'),
                             transcript_tokens='r8.transcript.tokens',summary_tokens='r8.transcript.summary',reserve_bytes=reserve,
                             link_mbit=r.add(nn+'.mbit',[bw],lambda b:b/1e6),local_ttft_s=local,server_prefill_s=server,transfer_s=wire,import_s=imp,last_token_s=last,hybrid_ttft_s=total,summary_decode_s=decode,
                             local_total_s=r.add(nn+'.local_total',[local,decode],lambda a,b:a+b),hybrid_total_s=r.add(nn+'.hybrid_total',[total,decode],lambda a,b:a+b),
                             api_median=apis['qwen_median'],api_cheapest=apis['qwen_cheap']))
    c.table('transcript_example','Cold 70k transcript and one 3k summary; one stream, no double-counted reasoning',
            {k:'text' if k in ('client','basis') else 'token' if k.endswith('_tokens') else 'B' if k=='reserve_bytes' else 'Mbit/s' if k=='link_mbit' else 'USD/session' if k.startswith('api_') else 's' for k in rows[0]},rows)


def recurrent_bits(bits,path):
    if bits not in (16,32):raise InputGap(path,'supported recurrent formats are32 or16 bits')
    return bits


def intensity_table(r):
    c=r.c;rows=[]
    for key in c.scenario['intensity_models']:
        name='intensity.'+key
        if key in ('qwen27','flashnext','glm'):
            m=c.model(key);limit='models.'+key+'.context_limit';label=m['label']
            fixed=m['state'] if key!='flashnext' else r.add(name+'.f32',[m['state']],lambda s:s*2)
            def geometry(d,m,limit,path=limit):
                if d>limit:raise InputGap(path,'depth exceeds configured context; ratio not computable')
                return flop(m,d)
            nodes=[r.add(name+'.flop.'+str(i),[d,m['flop'],limit],geometry) for i,d in enumerate(r.positions('r8.depths'))]
            basis='engine architecture estimate; measured Qwen slot geometry; Flash native bf16 is expanded to f32 for the32-bit row'
            full=sliding=geom=None
        else:
            p='r7.arch.models.'+key;label=p+'.label';limit=p+'.context';fixed=p+'.state'
            full=c.g.bundle('pt.'+name+'.full',p+'.full',('layers','kv_heads','dim','q_heads','kv_copies'))
            sliding=c.g.bundle('pt.'+name+'.sliding',p+'.sliding',('layers','kv_heads','dim','q_heads','window'))
            geom=r.add(name+'.geometry',[full,sliding,'r7.arch.q8_factor'],arch_geometry)
            def geometry(d,params,f,s,limit,path=limit):
                if d>limit:raise InputGap(path,'depth exceeds published config context; ratio not computable')
                return arch_flops(params,f,s,d)
            nodes=[r.add(name+'.flop.'+str(i),[d,p+'.parameters',full,sliding,limit],geometry) for i,d in enumerate(r.positions('r8.depths'))]
            basis='published config q8_0 geometry; window delta uses min(portion,window); no recurrent state'
        for z,bits in enumerate(r.positions('r9.state_bits')):
            bits=r.add(name+'.bits.'+str(z),[bits],lambda b,path=bits:recurrent_bits(b,path))
            def state(size,b,path=bits):
                if b not in (16,32):raise InputGap(path,'supported recurrent formats are32 or16 bits')
                return size*b/32
            sx=r.add(name+'.state.'+str(z),[fixed,bits],state)
            for j,portion in enumerate(['r8.portion','r9.large_portion']):
                n=name+'.'+str(z)+'.'+str(j)
                if key in ('qwen27','flashnext','glm'):size=r.add(n+'.size',[portion,m['kv'],sx],payload)
                else:size=r.add(n+'.size',[geom,p+'.sliding.window',sx,portion],arch_delta)
                for i,depth in enumerate(r.positions('r8.depths')):
                    nn=n+'.'+str(i)
                    perbyte=r.add(nn+'.perbyte',[nodes[i],size,portion],lambda f,b,n:f/(b/n))
                    for client in c.scenario['intensity_clients']:
                        cp='hardware.clients.'+client
                        for k,bw in enumerate(r.positions('r8.links')):
                            prefix=nn+'.'+client+'.'+str(k)
                            machine=r.add(prefix+'.machine',[cp+'.compute',bw],lambda f,b:f/(b/8))
                            ratio=r.add(prefix+'.ratio',[perbyte,machine],lambda a,b:a/b)
                            rows.append(dict(model=label,basis=r.label(prefix+'.basis',basis),state_bits=bits,state_bytes=sx,
                                             state_basis=r.add(prefix+'.state_basis',[bits],lambda b:'f32 geometry; measured only for Qwen27' if b==32 else 'estimated bf16 recurrent representation; KV stays q8_0'),
                                             client=cp+'.label',depth=depth,context_limit=limit,portion_tokens=portion,delta_bytes=size,flop_new_token=nodes[i],model_flop_byte=perbyte,client_peak_flop_s=cp+'.compute',
                                             link_mbit=r.add(prefix+'.mbit',[bw],lambda b:b/1e6),client_flop_byte=machine,ratio=ratio,beats_ideal_local=r.add(prefix+'.wins',[ratio],lambda x:int(x>1))))
    c.table('flop_per_byte','Arithmetic intensity:1k/10k portions and f32/estimated bf16 recurrent state; ideal local bound',
            {k:'text' if k in ('model','basis','client','state_basis') else 'bit' if k=='state_bits' else 'token' if k in ('depth','context_limit','portion_tokens') else 'B' if k in ('delta_bytes','state_bytes') else 'FLOP/token' if k=='flop_new_token' else 'FLOP/B' if k in ('model_flop_byte','client_flop_byte') else 'FLOP/s' if k=='client_peak_flop_s' else 'Mbit/s' if k=='link_mbit' else '1' for k in rows[0]},rows)


def output_sensitivity(c):
    """Separate declared scopes prevent cross-contamination of the two workload policies."""
    from .engine import load
    rows=[];dependencies={};alarms=[];columns=None
    for i,path in enumerate(c.positions('r8.output_fractions')):
        fraction=c.g.resolve(path);path=sorted(c.g.roots(path))[0];team=c.g.resolve('r8.sensitivity_team')
        scenario,_=load('paper-tables');scenario.update(economics_clients=['m3max','m5max64'],share_keys=['s20','s50'])
        data=copy.deepcopy(c.inputs.data)
        data.setdefault('workload',{})['reasoning_extra_fraction']=copy.deepcopy(c.inputs.locate(path)) if not fraction.alarms else None
        data.setdefault('paper_tables',{})['teams']=[copy.deepcopy(c.inputs.locate('r8.sensitivity_team')) if not team.alarms else None]
        child=Inputs(data,tolerant=True);child.unavailable=copy.deepcopy(c.inputs.unavailable)
        context=Context(scenario,child);person_tables(context);result=context.g.result(scenario['name'])
        scope='output_sensitivity_'+str(i)+'.'
        for t in result['tables']:
            for j,row in enumerate(t['rows']):
                index=len(rows);out={'accounting_case':('base_output' if fraction.value==0 else 'reasoning_on_top_upper_bound') if not fraction.alarms else {'alarm':list(fraction.alarms)},'reasoning_extra_fraction':fraction.value if not fraction.alarms else {'alarm':list(fraction.alarms)}}
                out.update(copy.deepcopy(row));rows.append(out)
                for col,value in out.items():
                    if col in ('reasoning_extra_fraction','accounting_case'):d={'inputs':sorted(c.g.roots(path)),'requires':[path]}
                    else:
                        def remap(x):
                            return path if x=='workload.reasoning_extra_fraction' else 'r8.sensitivity_team' if x=='paper_tables.teams.0' else scope+x
                        d=copy.deepcopy(t['dependencies'][str(j)+'.'+col]);d={k:[remap(x) for x in v] for k,v in d.items()}
                    dependencies[str(index)+'.'+col]=d
                    if isinstance(value,dict) and 'alarm' in value:
                        if col in ('reasoning_extra_fraction','accounting_case'):
                            alarms.extend(value['alarm']);continue
                        value['alarm']=[dict(a,input=path if a['input']=='workload.reasoning_extra_fraction' else 'r8.sensitivity_team' if a['input']=='paper_tables.teams.0' else scope+a['input']) for a in value['alarm']]
                        alarms.extend(value['alarm'])
                columns={'accounting_case':'text','reasoning_extra_fraction':'1',**t['columns']}
        for p,q in child.used.items():c.inputs.used[scope+p]=q
        for p,q in child.files.items():c.inputs.files[scope+p]=dict(q,scope=scope)
    return dict(id='reasoning_on_top_sensitivity',name='Output-only base versus reasoning-on-top upper bound; same measured input mix',columns=columns,rows=rows,dependencies=dependencies,alarms=unique(alarms))


def calculate(scenario,inputs):
    r=R7(scenario,inputs);people_table(r.c);transcript_table(r);intensity_table(r)
    result=r.c.g.result(scenario['name'],[
        'Every client-served input/output token is eventually prefilled once on the server. R9 uses append-only KV spill plus recurrent overwrite. The selected catch-up policy places pending work on offload or shadows per call, with an explicit daily-tail budget. Selected retention uses active-window tiered storage or month-long RAM; promotion is background I/O. All hosting budgets are estimates, not quotes or measurements.',
        'People/GPU is an uncapped offered-demand bound at 70% in 8h. It is not a per-Mac capacity claim. Integer people are rounded down; RAM pool costs remain separate from GPU time.',
        'Transcript timings integrate the measured M3 curve, scaled by compute for M5. Summary uses one measured-calibrated stream with estimated depth/bandwidth scaling. Air is an unmeasured dedicated appliance with an explicit 8GB reserve; 12GB raises a fit alarm.',
        'Arithmetic intensity is a necessary compute/transfer comparison, not end-to-end speedup: server time, import and ideal-engine memory limits are excluded. Unsupported configured contexts alarm; Qwen 1M is an estimated extension, not measured quality validation.',
        'Output alone is the base (reasoning_extra_fraction=0). Reasoning is an informational subset for verified Codex/Claude usage; Muse follows that convention unverified. Fraction=1 is a labelled reasoning-on-top upper bound in a separate source/dependency scope, retaining run10 accounting.'
    ])
    t=output_sensitivity(r.c);result['tables'].insert(0,t)
    result['alarms']=unique(result['alarms']+t['alarms'])
    result['computed_metrics']+=sum(type(v) in (int,float) for row in t['rows'] for v in row.values())
    result['export_namespace']=scenario['export_namespace']
    return result
