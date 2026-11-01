"""Four R7 charts: measured spans, explicit import, decode what-ifs and config formulas."""
import math
from .inputs import InputGap
from .metrics import field,nonempty
from .paper import throughput
from .paper_tables import Context,end_memory,measured_rate,supported
from .performance import flop,payload,transfer
from .session_hosting import route


def integrate_span(function,start,tokens,step):
    if start<0 or tokens<0 or step<=0:raise InputGap('r7.integration_step','nonnegative span and positive integration step required')
    total=0.0;end=start+tokens
    while start<end:
        width=min(step,end-start);total+=width*function(start+width/2);start+=width
    return total


def import_time(size,bandwidth,efficiency,copies,fixed):
    return copies*size/(bandwidth*efficiency)+fixed


def hybrid_time(server,wire,import_s,last_token):return server+wire+import_s+last_token


def scale_guard(scale,efficiency,path):
    if scale*efficiency>1:
        raise InputGap(path,'requested decode scale exceeds raw bandwidth bound at unchanged Q4/q8_0 byte traffic; capacity not physically computable')
    return scale


def arch_geometry(full,sliding,q8):
    if sliding['layers'] and any(sliding[k]<=0 for k in ('kv_heads','dim')):
        raise InputGap('r7.arch.models.sliding.window','active sliding layers require positive KV heads and dimensions')
    return (full['layers']*full['kv_heads']*full['dim']*full['kv_copies']*q8,
            sliding['layers']*sliding['kv_heads']*sliding['dim']*2*q8)


def arch_flops(parameters,full,sliding,depth):
    if sliding['layers'] and any(sliding[k]<=0 for k in ('q_heads','dim','window')):
        raise InputGap('r7.arch.models.sliding.window','active sliding layers require positive query heads, dimension and window')
    return (2*parameters+4*full['layers']*depth*full['q_heads']*full['dim']+
            4*sliding['layers']*min(depth,sliding['window'])*sliding['q_heads']*sliding['dim'])


def arch_window(layers,window):
    if layers and window<=0:raise InputGap('r7.arch.models.sliding.window','active sliding layers require a positive window')
    return window


def arch_delta(geometry,window,state,portion):
    return portion*geometry[0]+min(portion,window)*geometry[1]+state


class R7:
    def __init__(self,scenario,inputs):
        self.c=Context(scenario,inputs);self.g=self.c.g;self.model=self.c.model('qwen27');self.clients={};self.arrays={}
        self.server=self.c.server(scenario['summary_option'],self.model)
        def q4(quant):
            if quant!='Q4':raise InputGap('owners.client_quant','R7 timings/reference require Qwen Q4; use a separate scenario for other formats')
            return quant
        self.q4=self.add('q4',['owners.client_quant'],q4)
        def compute(rate,gpus):
            if gpus!=1:raise InputGap(self.server['prefix']+'.gpus','R7 requires one B300 GPU, not a fleet')
            return rate
        self.compute=self.add('compute',[self.server['compute'],self.server['prefix']+'.gpus'],compute)
    def add(self,name,refs,fn):return self.c.add('r7.'+name,refs,fn)
    def label(self,name,value):return self.c.label('r7.'+name,value)
    def positions(self,path):return self.c.positions(path)
    def state(self,key):
        n='state.'+key
        if n not in self.c.cache:self.c.cache[n]=self.add(n,[self.c.state,'r7.states.'+key+'.factor'],lambda s,f:s*f)
        return self.c.cache[n]
    def link(self,name,bandwidth):return self.add(name,[bandwidth,'r7.goodput','r7.latency'],lambda b,g,l:dict(bandwidth=b,goodput=g,latency=l))
    def client(self,key,state):
        n=key+'.'+state
        if n in self.clients:return self.clients[n]
        p='hardware.clients.'+key;m=self.model;s=self.state(state)
        local=self.c.local_rate(key,m)
        memory=self.add(n+'.memory',[p+'.memory','owners.client_reserve',m['weights'],self.c.kv,s,self.q4],lambda mem,r,w,kv,s,q:lambda d:max(0,math.floor((mem-r-w)/(d*kv+s))))
        def decoder(w,kv,s,b,cal,passes,doc,q4):
            gain=field(doc,'parallel.normalized_decode_interval_gain','measurements.normalized');anchor=field(doc,'parallel.frozen_v11_row.streams','measurements.normalized')
            return measured_rate(w,kv,s,b,cal[0],gain,anchor,passes)
        rate=self.add(n+'.rate',[m['weights'],self.c.kv,s,p+'.bandwidth',self.c.cal,'analysis.decode_state_passes',self.c.normalized,self.q4],decoder)
        self.clients[n]=dict(prefix=p,local=local,memory=memory,rate=rate,state=s)
        return self.clients[n]
    def import_node(self,name,size,client):
        return self.add(name,[size,client['prefix']+'.bandwidth','r7.import_efficiency','r7.import_copies','r7.import_fixed_s'],import_time)
    def span(self,name,depth,portion,state):
        client=self.client('m3max',state);m=self.model
        def admit(d,n,limit):
            if d+n>limit:raise InputGap('r7.context_limit','span exceeds measured client context limit')
            return d+n
        final=self.add(name+'.final',[depth,portion,'r7.context_limit'],admit)
        def fit(d,mem):
            if mem(d)<1:raise InputGap('hardware.clients.m3max.memory','Q4 weights + full q8_0 context/state + reserve do not fit')
            return d
        client_final=self.add(name+'.client_fit',[final,client['memory']],fit)
        def server_fit(d,free,kv,state):
            if d*kv+state>free:raise InputGap(self.server['prefix']+'.memory','Q4 weights + full context/state + workspace do not fit server')
            return d
        server_final=self.add(name+'.server_fit',[final,self.server['free'],self.c.kv,client['state']],server_fit)
        one=self.add(name+'.one',[depth,portion],lambda d,n:[(d,n,0,0)])
        migration=self.c.hosting.vector('r7.'+name,one,self.c.kv,client['state'])
        reload_s=self.add(name+'.reload',[migration],lambda rows:rows[0][0])
        local=self.add(name+'.local',[depth,portion,client['local'],'r7.integration_step',client_final],lambda d,n,r,step,ready:integrate_span(lambda x:1/r(x),d,n,step))
        server=self.add(name+'.server',[depth,portion,m['flop'],self.compute,'r7.integration_step',server_final],lambda d,n,m,c,step,ready:integrate_span(lambda x:flop(m,x)/c,d,n,step))
        size=self.add(name+'.payload',[portion,self.c.kv,client['state']],payload)
        imp=self.import_node(name+'.import',size,client)
        last=self.add(name+'.last',[client['rate'],client_final,'r7.last_token_tokens'],lambda r,d,n:n/r(1,d))
        return dict(reload=reload_s,local=local,server=server,size=size,import_s=imp,last=last,state=client['state'],final=final)


def timing_tables(r):
    for oneshot in (False,True):
        rows=[];id='oneshot_ingest' if oneshot else 'turn_speedup'
        for state in r.c.scenario['state_keys']:
            depths=[r.label(id+'.'+state+'.zero',0)] if oneshot else r.positions('r7.turn.depths')
            for i,depth in enumerate(depths):
                for j,portion in enumerate(r.positions('r7.oneshot.contexts' if oneshot else 'r7.turn.portions')):
                    name=id+'.'+state+'.'+str(i)+'.'+str(j);span=r.span(name,depth,portion,state)
                    for z,bw in enumerate(r.positions('r7.links')):
                        n=name+'.'+str(z);link=r.link(n+'.link',bw)
                        wire=r.add(n+'.transfer',[portion,r.c.kv,span['state'],link],transfer)
                        total=r.add(n+'.total',[span['server'],wire,span['import_s'],span['last'],span['reload']],lambda s,w,i,l,reload:hybrid_time(s+reload,w,i,l))
                        row={'state_format':r.label(n+'.format',state),'state_basis':'r7.states.'+state+'.basis','client':'hardware.clients.m3max.label','server':r.server['label'],'server_precision':r.c.precision_label,'quant':r.q4,
                             'kv_bytes_token':r.c.kv,'state_bytes':span['state'],'link_mbit':r.add(n+'.mbit',[bw],lambda b:b/1e6),'payload_bytes':span['size'],
                             'server_compute':r.compute,'server_reload_s':span['reload'],'server_prefill_s':span['server'],'transfer_s':wire,'import_s':span['import_s'],'last_token_s':span['last'],
                             'speedup':r.add(n+'.speedup',[span['local'],total],lambda local,remote:local/remote)}
                        if oneshot:row.update(start_depth=depth,context=portion,local_s=span['local'],hybrid_ttft_s=total)
                        else:row.update(depth=depth,portion=portion,local_prefill_s=span['local'],hybrid_s=total)
                        rows.append(row)
        text={'state_format','state_basis','client','server','server_precision','quant'}
        units={k:'text' if k in text else 'token' if k in ('start_depth','context','depth','portion') else 'B/token' if k=='kv_bytes_token' else 'B' if k in ('state_bytes','payload_bytes') else 'Mbit/s' if k=='link_mbit' else 'FLOP/s' if k=='server_compute' else '1' if k=='speedup' else 's' for k in rows[0]}
        r.c.table(id,'One-shot full-context ingestion and hybrid first-token time' if oneshot else 'Large single turns: integrated local prefill against full hybrid cost',units,rows)


def sensitivity_table(r):
    rows=[];m=r.model
    anchor=r.add('sensitivity.anchor',[r.c.normalized],lambda d:field(d,'parallel.frozen_v11_row.depth','measurements.normalized'))
    gain=r.add('sensitivity.gain',[r.c.normalized],lambda d:field(d,'parallel.normalized_decode_interval_gain','measurements.normalized'))
    for key in r.c.scenario['decode_clients']:
        for state in r.c.scenario['state_keys']:
            cl=r.client(key,state);p=cl['prefix'];name='sensitivity.'+key+'.'+state
            idx=r.add(name+'.eligible',[r.c.valid,cl['memory']],supported)
            calls=r.add(name+'.calls',[r.c.valid,idx],lambda rows,idx:nonempty([rows[i] for i in idx]))
            def choose(wanted,memory,doc):
                cap=field(doc,'parallel.frozen_v11_row.streams','measurements.normalized');depth=field(doc,'parallel.frozen_v11_row.depth','measurements.normalized')
                if wanted>cap:raise InputGap('paper_tables.streams','R7 retains measured four-stream gain; stream count exceeds anchor')
                k=min(wanted,memory(depth))
                if k<1:raise InputGap(p+'.memory','no complete client stream fits the measured anchor')
                return k
            streams=r.add(name+'.streams',['paper_tables.streams',cl['memory'],r.c.normalized],choose)
            bounded=r.add(name+'.end_memory',[calls,cl['memory']],end_memory)
            migration=r.c.hosting.vector(name,calls,r.c.kv,cl['state'])
            localsteps=r.add(name+'.localsteps',[calls,cl['local']],lambda rows,rate:[(n/rate(d),n/rate(d),0,False) for d,n,o,t in rows])
            fraction=r.add(name+'.fit_share',[idx,r.c.valid],lambda idx,all:len(idx)/len(nonempty(all)))
            minimum=r.add(name+'.min_streams',[calls,cl['memory'],streams],lambda rows,mem,k:min(min(k,mem(d+n+o)) for d,n,o,t in rows))
            maximum=r.add(name+'.max_streams',[calls,cl['memory'],streams],lambda rows,mem,k:max(min(k,mem(d+n+o)) for d,n,o,t in rows))
            for i,scale in enumerate(r.positions('r7.decode.scales')):
                pre=name+'.'+str(i)
                valid=r.add(pre+'.physical',[scale,r.c.cal],lambda s,cal,path=scale:scale_guard(s,cal[0],path))
                rate=r.add(pre+'.rate',[cl['rate'],scale],lambda base,s:lambda k,d:base(k,d)*s)
                ready=r.add(pre+'.ready_rate',[rate,valid],lambda fn,v:fn)
                single=r.add(pre+'.single',[rate,anchor],lambda rate,d:rate(1,d))
                aggregate=r.add(pre+'.four',[rate,anchor],lambda rate,d:rate(4,d)*4)
                localcap=r.add(pre+'.local',[calls,localsteps,streams,bounded,ready,'paper_tables.hours'],throughput)
                for j,bw in enumerate(r.positions('r7.decode.links')):
                    n=pre+'.'+str(j);link=r.link(n+'.link',bw)
                    def steps(rows,local,rate,model,compute,free,kv,state,link,bandwidth,eff,copies,fixed,last,migration):
                        own=[];remote_times=[];shadow=[];outputs=[];wires=[];foreground=[]
                        for (d,delta,o,t),(reload_s,spill) in zip(rows,migration):
                            if (d+delta+o)*kv+state>free:raise InputGap(r.server['prefix']+'.memory','complete context does not fit B300 replica')
                            local_s=delta/local(d)
                            imp=import_time(payload(delta,kv,state),bandwidth,eff,copies,fixed);evaluation=last/rate(1,d+delta)
                            remote=hybrid_time(reload_s+delta*flop(model,d)/compute,transfer(delta,kv,state,link),imp,evaluation)
                            own.append(local_s);remote_times.append(remote);shadow.append((delta+o)*flop(model,d)/compute);outputs.append(o*flop(model,d)/compute);wires.append(payload(delta,kv,state));foreground.append(imp+evaluation)
                        return route(own,remote_times,shadow,outputs,wires,foreground,migration.catch_up)
                    policy=r.add(n+'.policy',[calls,cl['local'],ready,m['flop'],r.compute,r.server['free'],r.c.kv,cl['state'],link,p+'.bandwidth','r7.import_efficiency','r7.import_copies','r7.import_fixed_s','r7.last_token_tokens',migration],steps)
                    cap=r.add(n+'.hybrid',[calls,policy,streams,bounded,ready,'paper_tables.hours'],throughput)
                    local=r.add(n+'.local_sessions',[localcap,'workload.chunk_calls'],lambda n,c:n/c)
                    hybrid=r.add(n+'.hybrid_sessions',[cap,'workload.chunk_calls'],lambda n,c:n/c)
                    rows.append(dict(client=p+'.label',client_basis=r.label(n+'.client_basis','measured M3 anchors; estimated depth throughput' if key=='m3max' else 'estimated M5 bandwidth/compute portability'),fit_share=fraction,hours='paper_tables.hours',chunk_calls='workload.chunk_calls',min_streams=minimum,max_streams=maximum,state_format=r.label(n+'.format',state),state_basis='r7.states.'+state+'.basis',state_bytes=cl['state'],kv_bytes_token=r.c.kv,
                                     decode_scale=scale,decode_basis=r.add(n+'.basis',[scale],lambda s:'measured M3 anchor; portability/depth/state are estimated' if s==1 else 'hypothetical engine improvement; not measured'),
                                     link_mbit=r.add(n+'.mbit',[bw],lambda b:b/1e6),streams=streams,anchor_gain=gain,single_tok_s_32k=single,four_aggregate_tok_s_32k=aggregate,
                                     local_sessions_day=local,hybrid_sessions_day=hybrid,gain=r.add(n+'.gain',[hybrid,local],lambda h,l:h/l)))
    units={k:'text' if k in ('client','client_basis','state_format','state_basis','decode_basis') else 'B' if k=='state_bytes' else 'B/token' if k=='kv_bytes_token' else 'Mbit/s' if k=='link_mbit' else 'h/day' if k=='hours' else 'call/session group' if k=='chunk_calls' else 'stream' if k in ('streams','min_streams','max_streams') else 'token/s' if k.endswith('32k') else 'session/day (supported mix)' if k.endswith('sessions_day') else '1' for k in rows[0]}
    r.c.table('decode_sensitivity','Real-call-mix sensitivity to hypothetical decode improvements; unchanged four-stream gain',units,rows)


def architecture_table(r):
    configs={};rows=[]
    for key in r.c.scenario['arch_models']:
        p='r7.arch.models.'+key
        full=r.g.bundle('pt.r7.arch.'+key+'.full',p+'.full',('layers','dim','q_heads'))
        sliding=r.g.bundle('pt.r7.arch.'+key+'.sliding',p+'.sliding',('layers','dim','q_heads','window'))
        kv_full=r.g.bundle('pt.r7.arch.'+key+'.kv_full',p+'.full',('layers','kv_heads','dim','kv_copies'))
        kv_sliding=r.g.bundle('pt.r7.arch.'+key+'.kv_sliding',p+'.sliding',('layers','kv_heads','dim'))
        window=r.add('arch.'+key+'.window',[p+'.sliding.layers',p+'.sliding.window'],arch_window)
        geometry=r.add('arch.'+key+'.geometry',[kv_full,kv_sliding,'r7.arch.q8_factor'],arch_geometry)
        flops=r.add('arch.'+key+'.flops',[p+'.parameters',full,sliding,'r7.arch.reference_depth'],arch_flops)
        configs[key]=(p,full,sliding,geometry,flops,window)
    def reference(rows,end,q4):
        matches=[row for row in rows if field(row,'kind','measurements.depth')=='segment' and field(row,'depth','measurements.depth')==end]
        if len(matches)!=1:raise InputGap('r7.arch.reference_segment_end','expected one matching measured segment')
        rate=field(matches[0],'prefill_tok_s','measurements.depth')
        if type(rate) not in (float,int) or not math.isfinite(rate) or rate<=0:raise InputGap('measurements.depth','positive finite architecture reference rate required')
        return r.c.inputs.measured_value('depth','architecture.reference_prefill_tok_s',rate,'token/s')
    ref_rate=r.add('arch.reference_rate',[r.c.depth,'r7.arch.reference_segment_end',r.q4],reference)
    for key,(p,full,sliding,geometry,flops,window) in configs.items():
        for state in r.c.scenario['state_keys']:
            n='arch.'+key+'.'+state
            fixed=r.add(n+'.state',[p+'.state','r7.states.'+state+'.factor'],lambda s,f:s*f)
            small=r.add(n+'.small',[geometry,window,fixed,'r7.arch.portion'],arch_delta)
            large=r.add(n+'.large',[geometry,window,fixed,'r7.arch.large_portion'],arch_delta)
            local=r.add(n+'.local',['r7.arch.portion',ref_rate,configs['qwen27'][4],flops],lambda n,rate,ref,f:n/(rate*ref/f))
            other=r.add(n+'.other_flops',[p+'.parameters',full,sliding,'r7.arch.comparison_depth'],arch_flops)
            def second(n,rate,ref,f,depth,limit,path=p+'.context'):
                if depth>limit:raise InputGap(path,'attached script uses None: comparison depth exceeds configured context')
                return round(n/(rate*ref/f),1)
            optional=r.add(n+'.second',['r7.arch.portion',ref_rate,configs['qwen27'][4],other,'r7.arch.comparison_depth',p+'.context'],second)
            links=r.positions('r7.arch.links')
            row=dict(model=p+'.label',kind=p+'.kind',state_format=r.label(n+'.format',state),state_basis=('r7.states.'+state+'.basis') if key=='qwen27' else r.label(n+'.state_basis','no recurrent state; window KV remains q8_0'),context=p+'.context',portion_tokens='r7.arch.portion',large_portion_tokens='r7.arch.large_portion',reference_depth='r7.arch.reference_depth',comparison_depth='r7.arch.comparison_depth',full_layers=p+'.full.layers',
                     kv_full_bytes_token=r.add(n+'.kv',[geometry],lambda g:round(g[0])),swa_bytes_token=r.add(n+'.swa',[geometry],lambda g:round(g[1])),swa_window=p+'.sliding.window',
                     fixed_mb=r.add(n+'.fixed',[fixed,window,geometry],lambda s,w,g:round((s+w*g[1])/1e6,1)),
                     delta_1k_mb=r.add(n+'.smallmb',[small],lambda b:round(b/1e6,1)),delta_10k_mb=r.add(n+'.largemb',[large],lambda b:round(b/1e6,1)),
                     transfer_1k_300mbit_s=r.add(n+'.transfer',[small,'r7.arch.transfer_bandwidth'],lambda b,bw:round(b/(bw/8),1)),
                     gflop_token_131k=r.add(n+'.gflops',[flops],lambda f:round(f/1e9)),client_prefill_1k_131k_s=r.add(n+'.rounded_local',[local],lambda t:round(t,1)),
                     client_prefill_1k_262k_s=optional,within_context_131k=r.add(n+'.supported',['r7.arch.reference_depth',p+'.context'],lambda d,c:int(d<=c)),
                     transfer_link_mbit=r.add(n+'.transfer_link',['r7.arch.transfer_bandwidth'],lambda b:b/1e6),kv_basis=r.label(n+'.kv_basis','config q8_0 layout; timing tables use measured slot slope'),reference_rate_tok_s=ref_rate)
            for j,bw in enumerate(links):
                column=('saving_1k_131k_100mbit_s','saving_1k_131k_300mbit_s','saving_1k_131k_1000mbit_s')[j] if j<3 else 'saving_link_'+str(j)+'_s'
                row[column]=r.add(n+'.saving.'+str(j),[local,small,bw],lambda t,b,bw:round(t-b/(bw/8),1))
                row['saving_link_'+str(j)+'_mbit']=r.add(n+'.link.'+str(j),[bw],lambda b:b/1e6)
            rows.append(row)
    units={k:'text' if k in ('model','kind','state_format','state_basis','kv_basis') else 'token' if k in ('context','swa_window','portion_tokens','large_portion_tokens','reference_depth','comparison_depth') else 'layer' if k=='full_layers' else 'B/token' if k.endswith('bytes_token') else 'MB' if k.endswith('_mb') else 'GFLOP/token' if k=='gflop_token_131k' else '1' if k=='within_context_131k' else 'token/s' if k=='reference_rate_tok_s' else 'Mbit/s' if k.endswith('_mbit') else 's' for k in rows[0]}
    r.c.table('arch_compare','Attached architecture formulas: exact f32 reproduction and estimated bf16 recurrent state',units,rows)


def calculate(scenario,inputs):
    r=R7(scenario,inputs);timing_tables(r);sensitivity_table(r);architecture_table(r)
    result=r.g.result(scenario['name'],[
        'Exactly four R7 tables. Timings use measured Qwen27 Q4 M3 marginal segment curve with roofline and measured resident q8_0 slot slope34844 B/token; statef32 is fitted156894784 B, bf16 half is estimated. Cross-device/state/depth speed portability is estimated.',
        'Hybrid timing is serial existing-prefix reload (zero for cold empty-prefix ingest), B300 prefill, line-rate delta/full-state transfer including explicit RTT, import and one final-depth decode-equivalent client evaluation. No overlap or cold model loading. Import assumes one copy at10% nominal client bandwidth, explicit fixed overhead0; filesystem slot restore is not a delta-import measurement.',
        'Large turns and one-shot loads integrate from start to final depth. Server uses one B300 at existing quantized effective compute, including its stated MFU. All client/server contexts undergo memory admission. Local spans use declared midpoint integration; beyond the last measured midpoint FLOP efficiency is held constant.',
        'Decode sensitivity uses supported real-mix calls normalized into workload.chunk_calls groups in an8h day, R5 marginal per-call prefill convention, measured four-stream gain, R7 remote import/evaluation and the selected R9 pending-catch-up critical path. Sensitivity retains the existing engine1M context modelling envelope beyond the262k benchmark limit, with fit_share and actual stream ranges explicit. Scale>1 is hypothetical. A requested rate beyond raw unchanged-traffic memory bandwidth alarms capacity; no speedup is silently clipped.',
        'Architecture f32 rows reproduce every numeric field of the owner-attached script, using config q8_0 KV34816 for Qwen rather than measured slot34844. The41.2 tok/s approximate131k reference is read from the segment with actual midpoint131448. Its 27.8B FLOP estimate differs from the existing engine27B envelope. Savings intentionally omit server/import/evaluation as the script does.',
        'Architecture131k results are labelled extrapolations when outside model context (Qwen3). Unsupported262k fields are alarms where the script wrote None. Bf16 rows halve only recurrent state; sliding-window KV remains q8_0. Config URLs identify owner-supplied offline config transcriptions, not a new network verification.'
    ])
    result['export_namespace']=scenario['export_namespace'];return result
