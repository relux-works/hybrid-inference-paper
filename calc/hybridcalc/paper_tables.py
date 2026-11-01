"""Paper charts on hash-checked measurements, explicit routing and whole-demand costs."""
import copy
import math
from .analysis_graph import FLOP_FIELDS,calls_graph,curve_data,decode_calibration,slot_data,mean_flops
from .glm import step_bytes
from .inputs import InputGap
from .metrics import Graph,nonempty,unique
from .ownership import fit_sessions,selected
from .paper import policy,throughput
from .performance import flop,payload,roofline_prefill,transfer
from .session_hosting import Hosting,policy_with_reload


def api_vector(calls,tariff,chunk):
    """Keep original normalization-group cache boundaries when routing only some calls."""
    previous=0;out=[]
    for i,(d,n,o,t) in enumerate(nonempty(calls)):
        if i%chunk==0:previous=0
        out.append((d*tariff['cache_read']+(n+previous)*tariff['cache_write']+o*tariff['output'])/1e6)
        previous=o
    return out


def growing_calls(calls,start,end,limit):
    rows=nonempty(calls)
    if not 0<=start<end<=limit:raise InputGap('paper_tables.glm.contexts','context must increase from start within the model limit')
    if not any(n+o>0 for d,n,o,t in rows):raise InputGap('workload','growing session needs positive delta/output progress')
    result=[];depth=start;index=0
    while depth<end:
        _,n,o,t=rows[index%len(rows)];index+=1
        n=min(n,end-depth);o=min(o,end-depth-n)
        if n+o<=0:continue
        result.append((depth,n,o,t));depth+=n+o
    return result


def integrate(function,tokens,step):
    if tokens<0 or step<=0:raise InputGap('paper_tables.glm.integration_step','positive integration step and nonnegative depth required')
    total=0;start=0
    while start<tokens:
        width=min(step,tokens-start);total+=width*function(start+width/2);start+=width
    return total


def measured_rate(weights,kv,state,bandwidth,efficiency,gain,anchor_streams,passes):
    """Measured aggregate interpolation, capped by calibrated bandwidth; k is <= anchor."""
    exponent=math.log(gain)/math.log(anchor_streams)
    if not 0<=exponent<=1:raise InputGap('measurements.normalized','parallel gain must lie between one and the measured stream count')
    def rate(k,depth):
        traffic=kv*depth+passes*state
        single=bandwidth*efficiency/(weights+traffic)
        aggregate=min(single*k**exponent,bandwidth*efficiency*k/(weights+k*traffic))
        return aggregate/k
    return rate


def supported(calls,memory):return [i for i,(d,n,o,t) in enumerate(nonempty(calls)) if memory(d+n+o)>=1]


def end_memory(calls,memory):
    """Admit simultaneous streams against KV after this call's output growth."""
    limits={}
    for d,n,o,t in calls:
        depth=d+n;k=memory(d+n+o)
        limits[depth]=min(k,limits[depth]) if depth in limits else k
    return lambda depth:limits[depth]


def overflow_cost(requested,served,indices,prices,days):
    if not prices:raise InputGap('workload.sample_calls','empty API cost vector')
    eligible=set(indices);offered=requested*len(indices)/len(prices)
    if served>offered+1e-9:raise InputGap('paper_tables','served calls exceed eligible demand')
    probability=served/offered if offered>0 else 0
    return requested*days*sum(p*(1-probability if i in eligible else 1) for i,p in enumerate(prices))/len(prices)


def offload_stats(calls,local,model,compute,link,migration):
    steps=policy_with_reload(calls,model,compute,link,local,migration)
    saving=[max(0,n/local(d)-step[0]) if step[3] else 0.0 for (d,n,o,t),step in zip(calls,steps)]
    wins=sum(x>0 for x in saving)
    return {'share':wins/len(saving),'saved':sum(saving)/len(saving),'wins':wins,'total':sum(saving)}


class Context:
    def __init__(self,scenario,inputs):
        self.scenario=scenario;self.inputs=inputs;self.g=Graph(inputs);self.cache={};self.arrays={};self.hosting=Hosting(self)
        self.calls,self.valid=calls_graph(self.g)
        self.depth=self.g.measurement('depth',json_lines=True);self.normalized=self.g.measurement('normalized')
        self.fm=self.g.bundle('pt.base_model','models.qwen27',FLOP_FIELDS)
        self.curve=self.add('curve',[self.depth,self.fm],lambda rows,m:curve_data(rows,m,inputs))
        self.slot=self.add('slot',[self.depth],lambda rows:slot_data(rows,inputs))
        self.kv=self.add('slot.kv',[self.slot],lambda pair:pair[0]);self.state=self.add('slot.state',[self.slot],lambda pair:pair[1])
        self.client_bpp=selected(self.g,'pt.client_bpp','owners.client_quant','owners.formats')
        self.server_bpp=selected(self.g,'pt.server_bpp','owners.server_precision','owners.formats')
        self.precision_label=self.add('precision_label',['owners.server_precision'],lambda p:'BF16 (academic reference)' if p=='BF16' else p)
        self.cal=self.add('decode_cal',[self.normalized,'owners.models.qwen27.weights_q4',self.kv,'hardware.clients.m3max.bandwidth','analysis.decode_state_passes',self.state],
                          lambda doc,w,k,b,p,s:decode_calibration(doc,w,k,b,p,s,inputs))
    def add(self,name,refs,fn):return self.g.add('pt.'+name,refs,fn)
    def label(self,name,value):return self.g.constant('pt.'+name,value)
    def positions(self,path):
        if path not in self.arrays:self.arrays[path]=self.g.positions(path)
        return self.arrays[path]
    def table(self,id,name,columns,rows):
        t=self.g.table(name,columns,rows);t['id']=id;return t
    def model(self,key):
        cache='model.'+key
        if cache in self.cache:return self.cache[cache]
        p='owners.models.'+key
        weights=self.add(cache+'.weights',[p+'.weights_q4',self.client_bpp,'owners.formats.Q4'],lambda w,b,q:w*b/q)
        m={'key':key,'label':p+'.label','flop':self.g.bundle('pt.'+cache+'.flop','models.'+key,FLOP_FIELDS),'weights':weights,
           'kv':self.kv if key=='qwen27' else p+'.kv','state':self.state if key=='qwen27' else p+'.state',
           'parameters':p+'.parameters','server_weights':self.add(cache+'.server_weights',[p+'.parameters',self.server_bpp],lambda n,b:n*b)}
        m['api']={}
        for api in (('qwen_median','qwen_cheap') if key=='qwen27' else ('glm',)):
            tariff=self.g.bundle('pt.'+cache+'.tariff.'+api,'prices.apis.'+api,('cache_read','cache_write','output'))
            m['api'][api]=(tariff,self.add(cache+'.api.'+api,[self.valid,tariff,'workload.chunk_calls'],api_vector))
        self.cache[cache]=m;return m
    def server(self,key,model):
        cache='server.'+model['key']+'.'+key
        if cache in self.cache:return self.cache[cache]
        p='owners.options.'+key
        fields=('memory','gpus','bandwidth','shard_efficiency')
        h=self.g.bundle('pt.'+cache+'.hardware',p,fields)
        precision=self.g.resolve('owners.server_precision')
        field='bf16_peak' if not precision.alarms and precision.value=='BF16' else 'fp4_peak' if not precision.alarms and precision.value=='NVFP4' else 'fp8_peak'
        def peak(fmt,rate,mfu):
            if rate<=0:raise InputGap(p+'.'+field,'selected precision unavailable; NVFP4 needs engine-supported Blackwell FP4')
            return rate*mfu
        compute=self.add(cache+'.compute',['owners.server_precision',p+'.'+field,'service.mfu'],peak)
        def free(h,w,workspace):
            # The paper fleet uses independent replicas. Never credit one copy pooled over all GPUs.
            available=h['memory']-w-workspace
            if available<=0:raise InputGap(p+'.memory','server weights plus workspace do not fit one GPU replica')
            return available
        free=self.add(cache+'.free',[h,model['server_weights'],'owners.workspace'],free)
        ready=self.add(cache+'.ready',[compute,free,p+'.gpus',p+'.shard_efficiency'],lambda c,f,g,s:c*g*s)
        location=self.g.resolve(p+'.location')
        ep='prices.energy_client' if not location.alarms and location.value=='office' else 'prices.energy_dc'
        duty='owners.office_load' if not location.alarms and location.value=='office' else 'owners.load'
        cp='owners.office_colo' if not location.alarms and location.value=='office' else 'prices.colo'
        sp='owners.office_support' if not location.alarms and location.value=='office' else 'economics.support'
        energy=self.add(cache+'.energy',[p+'.location',p+'.power','economics.pue','economics.hours_month',duty,ep],lambda loc,p,pue,h,l,e:p*pue*h*l*e)
        refs=[p+'.location',p+'.power',cp]
        if key in self.scenario['colocated_keys']:
            colo=self.add(cache+'.colo',refs+[p+'.colo_min_month'],lambda loc,p,c,m:max(p*c,m))
        else:colo=self.add(cache+'.colo',refs,lambda loc,p,c:p*c)
        support=self.add(cache+'.support',[p+'.location',p+'.capex',sp],lambda loc,p,s:p*s/12)
        opex=self.add(cache+'.opex',[energy,colo,support],lambda *v:sum(v))
        value={'prefix':p,'hardware':h,'compute':compute,'total_compute':ready,'free':free,'opex':opex,'colo':colo,'label':p+'.label','hourly':p+'.hourly','capex':p+'.capex','model':model}
        self.cache[cache]=value;return value
    def unit_month(self,name,server,residual):
        return self.add(name,[server['capex'],residual,'owners.years',server['opex']],lambda cap,r,y,op:cap*(1-r)/(12*y)+op)
    def own_seconds(self,name,calls,m,server,per_call=True):
        if m['key']=='qwen27':
            decoder=self.add(name+'.decoder',[m['server_weights']],lambda w:dict(weights=w))
        else:
            dm=self.g.bundle('pt.'+name+'.glm_decoder','models.glm',('experts','active_experts','shared_bytes','routed_bytes','decode_kv_slope','decode_fixed'))
            decoder=self.add(name+'.decoder',[dm,self.server_bpp,'owners.formats.Q4',m['state']],lambda d,b,q,s:dict(d,shared_bytes=d['shared_bytes']*b/q,routed_bytes=d['routed_bytes']*b/q,state=s))
        def seconds(rows,fm,decoder,kv,state,h,compute,free,batch,rate,eff,passes):
            nonempty(rows)
            if m['key']=='glm' and decoder['active_experts']>decoder['experts']:raise InputGap('models.glm.active_experts','active experts exceed total experts')
            pre=mean_flops(rows,fm,shadow=False)/compute/h['gpus']/h['shard_efficiency']
            decode=res=0
            for d,n,o,t in rows:
                if (d+n+o)*kv+state>free:raise InputGap(server['prefix']+'.memory','one full session KV/state does not fit alongside the server replica')
                traffic=decoder['weights']/batch+(d+n)*kv+passes*state if m['key']=='qwen27' else step_bytes(decoder,batch,d+n,passes)/batch
                decode+=o*traffic/(h['bandwidth']*eff*h['gpus']*h['shard_efficiency'])
                res+=((d+n)*kv+state)*(o/rate+t)/(free*h['gpus'])
            value=pre+(decode+res)/len(rows)
            return value if per_call else value*len(rows)
        return self.add(name,[calls,m['flop'],decoder,m['kv'],m['state'],server['hardware'],server['compute'],server['free'],'owners.server_batch','owners.server_stream_rate','owners.server_bw_efficiency','analysis.decode_state_passes'],seconds)
    def local_rate(self,key,m):
        p='hardware.clients.'+key;name='local.'+m['key']+'.'+key
        if name in self.cache:return self.cache[name]
        refs=[self.curve,self.fm,m['flop'],p+'.compute','hardware.clients.m3max.compute',p+'.bandwidth',m['weights'],m['kv'],'models.qwen27.prefill_batch']
        if m['key']=='glm':refs+=['paper_tables.glm.moe_prefill_efficiency']
        def rate(curve,base,model,compute,anchor,bw,w,kv,batch,*factor):
            scale=compute/anchor*(factor[0] if factor else 1)
            return lambda d:1/roofline_prefill(model,d,curve.rate(d)*flop(base,d)*scale,bw,w/batch+kv)
        self.cache[name]=self.add(name,refs,rate)
        return self.cache[name]
    def client(self,key,link,tag):
        cache='client.'+key+'.'+tag
        if cache in self.cache:return self.cache[cache]
        p='hardware.clients.'+key;m=self.model('qwen27')
        # Per-call memory admission, not a global cap chosen from the deepest outlier.
        memory=self.add(cache+'.memory',[p+'.memory','owners.client_reserve',m['weights'],m['kv'],m['state']],lambda mem,r,w,kv,s:lambda d:max(0,math.floor((mem-r-w)/(d*kv+s))))
        def choose(wanted,cal,memory,doc):
            from .metrics import field
            measured=field(doc,'parallel.frozen_v11_row.streams','measurements.normalized')
            depth=field(doc,'parallel.frozen_v11_row.depth','measurements.normalized')
            if wanted>measured:raise InputGap('paper_tables.streams','stream count exceeds measured parallel anchor; no unmeasured extrapolation')
            k=min(wanted,memory(depth))
            if k<1:raise InputGap(p+'.memory','client model/state does not fit even one anchor stream')
            return k
        streams=self.add(cache+'.streams',['paper_tables.streams',self.cal,memory,self.normalized],choose)
        def decoder_fn(w,k,s,b,cal,passes,doc,law):
            from .metrics import field
            gain=field(doc,'parallel.normalized_decode_interval_gain','measurements.normalized')
            anchor=field(doc,'parallel.frozen_v11_row.streams','measurements.normalized')
            return measured_rate(w,k,s,b,cal[0],gain,anchor,passes)
        decoder=self.add(cache+'.rate',[m['weights'],m['kv'],m['state'],p+'.bandwidth',self.cal,'analysis.decode_state_passes',self.normalized,'paper_tables.decode_scaling'],decoder_fn)
        local=self.local_rate(key,m)
        srv=self.server(self.scenario['summary_option'],m)
        # Client eligibility is independent of server prices/admission.
        eligibility=self.add(cache+'.eligible',[self.valid,memory],supported)
        matched=self.add(cache+'.matched',[self.valid,eligibility],lambda rows,idx:nonempty([rows[i] for i in idx]))
        model=self.add(cache+'.wire',[m['flop'],'owners.models.qwen27.kv',m['state']],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
        wire=self.add(cache+'.link',[link,'hardware.links.wan.goodput','hardware.links.wan.latency'],lambda b,g,l:dict(bandwidth=b,goodput=g,latency=l))
        migration=self.hosting.vector(cache,matched,m['kv'],m['state'])
        def hybrid_steps(rows,m,c,l,r,free,state,migration):
            if any((d+n+o)*m['kv']+state>free for d,n,o,t in rows):raise InputGap(srv['prefix']+'.memory','full context does not fit the server replica; hybrid admission unavailable')
            return policy_with_reload(rows,m,c,l,r,migration)
        steps=self.add(cache+'.steps',[matched,model,srv['compute'],wire,local,srv['free'],m['state'],migration],hybrid_steps)
        local_steps=self.add(cache+'.local_steps',[matched,local],lambda rows,r:[(n/r(d),n/r(d),0,False) for d,n,o,t in rows])
        bounded=self.add(cache+'.end_memory',[matched,memory],end_memory)
        cap=self.add(cache+'.capacity',[matched,steps,streams,bounded,decoder,'paper_tables.hours'],throughput)
        localcap=self.add(cache+'.local_capacity',[matched,local_steps,streams,bounded,decoder,'paper_tables.hours'],throughput)
        downloads=self.add(cache+'.downloads',[steps],lambda s:sum(x[2] for x in nonempty(s))/len(s))
        work=self.add(cache+'.work',[matched,m['flop']],mean_flops)
        hosting=self.hosting.summary(cache+'.budget',matched,m['kv'],m['state'],steps)
        anchor=self.add(cache+'.anchor',[self.normalized],lambda doc:doc['parallel']['frozen_v11_row']['depth'])
        perstream=self.add(cache+'.perstream',[decoder,streams,anchor],lambda f,n,d:f(n,d))
        single=self.add(cache+'.single',[decoder,anchor],lambda f,d:f(1,d))
        gain=self.add(cache+'.gain',[perstream,streams,single],lambda r,k,s:r*k/s)
        minstreams=self.add(cache+'.min_streams',[matched,memory,streams],lambda rows,mem,k:min(min(k,mem(d+n+o)) for d,n,o,t in rows))
        maxstreams=self.add(cache+'.max_streams',[matched,memory,streams],lambda rows,mem,k:max(min(k,mem(d+n+o)) for d,n,o,t in rows))
        value=dict(hosting=hosting,steps=steps,min_streams=minstreams,max_streams=maxstreams,model=m,server=srv,indices=eligibility,matched=matched,capacity=cap,local_capacity=localcap,streams=streams,downloads=downloads,work=work,rate=perstream,single=single,gain=gain,local=local,memory=memory,decoder=decoder)
        self.cache[cache]=value;return value


def person_tables(c):
    m=c.model('qwen27');cluster=c.server(c.scenario['cluster_option'],m)
    own_s=c.own_seconds('person.own_seconds',c.valid,m,cluster)
    month=c.unit_month('person.cluster_month',cluster,'owners.residual')
    for share_key in c.scenario['share_keys']:
        share='paper_tables.shares.'+share_key;rows=[]
        for key in c.scenario['economics_clients']:
            cl=c.client(key,'hardware.links.wan.bandwidth','base');p='hardware.clients.'+key;name='person.'+share_key+'.'+key
            requested=c.add(name+'.requested',['owners.calls_day',share],lambda n,s:n*s)
            fraction=c.add(name+'.fit_share',[cl['indices'],c.valid],lambda idx,rows:len(idx)/len(nonempty(rows)))
            served=c.add(name+'.served',[requested,fraction,cl['capacity']],lambda n,f,cap:min(n*f,cap))
            overflow=c.add(name+'.overflow',[requested,served],lambda n,s:n-s)
            compute=c.add(name+'.compute',[served,cl['work'],cl['server']['total_compute'],cl['server']['hourly'],'owners.load','owners.days'],lambda n,f,compute,p,l,d:n*f/compute*p/3600/l*d)
            migration_day=c.hosting.daily(name,cl['hosting'],served)
            migration=c.add(name+'.migration',[migration_day,cl['server']['prefix']+'.gpus',cl['server']['hourly'],'owners.load','owners.days'],lambda s,g,p,l,d:s/g*p/3600/l*d)
            promotion=c.hosting.promotion(name,cl['hosting'])
            pending_calls=c.add(name+'.pending_calls',[cl['steps']],lambda steps:steps.pending_calls)
            pending_compute=c.add(name+'.pending_compute',[cl['steps']],lambda steps:steps.pending_seconds)
            flush_day=c.add(name+'.flush_day',[served,cl['hosting']['flush_seconds'],'hosting.sessions_per_person'],lambda n,s,k:min(n,k)*s if n else 0.0)
            reloads=c.add(name+'.reloads',[served,cl['hosting']['share'],'hosting.sessions_per_person','hosting.catch_up'],lambda n,p,k,mode:n if mode=='per_call' else n*p+min(n,k))
            storage=c.add(name+'.storage',[served,cl['hosting']['storage']],lambda n,p:p if n>0 else 0)
            hosting=c.add(name+'.hosting',[migration,storage],lambda a,b:a+b)
            gpu=c.add(name+'.gpu',[compute,hosting],lambda a,b:a+b)
            compute_call=c.add(name+'.compute_call',[cl['work'],cl['server']['total_compute'],cl['server']['hourly'],'owners.load'],lambda f,c,p,l:f/c*p/3600/l)
            hosting_call=c.add(name+'.hosting_call',[hosting,served,'owners.days'],lambda p,n,d:p/(n*d) if n else 0)
            egress=c.add(name+'.egress',[served,cl['downloads'],'owners.days','prices.egress'],lambda n,b,d,p:n*b*d/1e12*p)
            energy=c.add(name+'.energy',[p+'.power','paper_tables.hours','owners.days','prices.energy_client'],lambda p,h,d,e:p*h*d*e)
            apis={};extra={}
            for api,col in [('qwen_median','median'),('qwen_cheap','cheapest')]:
                prices=m['api'][api][1]
                apis[col]=c.add(name+'.api.'+col,[requested,prices,'owners.days'],lambda n,p,d:n*sum(p)/len(p)*d)
                extra[col]=c.add(name+'.overflow.'+col,[requested,served,cl['indices'],prices,'owners.days'],overflow_cost)
            for basis in ('owned','premium'):
                n=name+'.'+basis
                device=c.add(n+'.device',[p+'.purchase_price',p+'.premium_credit','economics.client_residual','owners.years'],lambda p,b,r,y:max(0,p-b)*(1-r)/(12*y)) if basis=='premium' else c.label(n+'.device',0)
                base=c.add(n+'.base',[gpu,egress,energy,device,'owners.front_month'],lambda *v:sum(v))
                hm=c.add(n+'.median',[base,extra['median']],lambda b,e:b+e);hc=c.add(n+'.cheap',[base,extra['cheapest']],lambda b,e:b+e)
                for i,team in enumerate(c.positions('paper_tables.teams')):
                    nn=n+'.'+str(i)
                    boxes=c.add(nn+'.boxes',[team,requested,own_s,'paper_tables.hours','owners.load'],lambda t,n,s,h,l:max(1,math.ceil(t*n*s/(h*3600*l))))
                    own=c.add(nn+'.own',[boxes,month,team],lambda n,p,t:n*p/t)
                    rows.append({'team':team,'client':p+'.label','basis':c.label(nn+'.basis','Mac already owned' if basis=='owned' else 'Mac premium bought'),
                                 'server_precision':c.precision_label,'client_quant':'owners.client_quant','share':share,'bound':c.add(nn+'.bound',[share],lambda s:'academic bound' if s==1 else 'decision case'),'streams':cl['streams'],'min_streams':cl['min_streams'],'max_streams':cl['max_streams'],
                                 'requested_day':requested,'fit_share':fraction,'capacity_day':cl['capacity'],'served_day':served,'overflow_day':overflow,
                                 'compute_month':compute,'hosting_month':hosting,'storage_month':storage,'migration_month':migration,'compute_per_call':compute_call,'hosting_per_call':hosting_call,'reload_offloaded_s':cl['hosting']['offload_reload'],'reload_background_s':cl['hosting']['background_reload'],'spill_s':cl['hosting']['spill'],'promotion_s_day':promotion,'terminal_flush_s_day':flush_day,'reloads_day':reloads,'offload_share':cl['hosting']['share'],'pending_calls_per_offload':pending_calls,'pending_compute_s_per_offload':pending_compute,'gpu_month':gpu,'egress_month':egress,'device_month':device,'energy_month':energy,'front_month':'owners.front_month',
                                 'hybrid_without_overflow':base,'overflow_median':extra['median'],'overflow_cheapest':extra['cheapest'],
                                 'hybrid_median':hm,'hybrid_cheapest':hc,'own_cluster':own,'api_median':apis['median'],'api_cheapest':apis['cheapest'],'cluster_units':boxes})
        cols={k:('text' if k in ('client','basis','bound','server_precision','client_quant') else '1' if k in ('share','fit_share') else 'stream' if k in ('streams','min_streams','max_streams') else 'person' if k=='team' else 'call/day' if k.endswith('_day') and k not in ('promotion_s_day','terminal_flush_s_day','reloads_day') else '8-GPU node' if k=='cluster_units' else 'USD/served call' if k.endswith('_per_call') else 's/day' if k in ('promotion_s_day','terminal_flush_s_day') else 'reload/day' if k=='reloads_day' else '1' if k in ('offload_share','pending_calls_per_offload') else 's/offloaded call' if k=='pending_compute_s_per_offload' else 's/served call' if k.endswith('_s') else 'USD/person-month') for k in rows[0]}
        c.table('person_cost_'+share_key,'Per-person cost / '+share_key+' (all requested calls, explicit overflow)',cols,rows)


def remote_table(c):
    m=c.model('qwen27');rows=[]
    for key in c.scenario['rental_options']+c.scenario['owned_options']:
        srv=c.server(key,m);p=srv['prefix'];name='remote.'+key
        offered=c.add(name+'.offered',['owners.calls_day','paper_tables.sizing_share'],lambda n,s:n*s)
        idx=c.add(name+'.fit',[c.valid,srv['free'],m['kv'],m['state']],lambda calls,free,kv,s:[i for i,(d,n,o,t) in enumerate(nonempty(calls)) if (d+n+o)*kv+s<=free])
        subset=c.add(name+'.subset',[c.valid,idx],lambda calls,idx:nonempty([calls[i] for i in idx]))
        fraction=c.add(name+'.fraction',[idx,c.valid],lambda idx,rows:len(idx)/len(rows))
        served=c.add(name+'.served',[offered,fraction],lambda n,f:n*f)
        work=c.add(name+'.work',[subset,m['flop']],mean_flops)
        compute_seconds=c.add(name+'.compute_seconds',[work,srv['total_compute']],lambda w,r:w/r)
        no_offload=c.add(name+'.not_foreground',[subset],lambda rows:[(0,0,0,False) for _ in rows])
        hosting=c.hosting.summary(name,subset,m['kv'],m['state'],no_offload)
        migration_day=c.hosting.daily(name,hosting,served)
        migration_seconds=c.add(name+'.migration_seconds',[migration_day,served,srv['prefix']+'.gpus'],lambda s,n,g:s/n/g if n else 0.0)
        seconds=c.add(name+'.seconds',[compute_seconds,migration_seconds],lambda a,b:a+b)
        fallback=c.add(name+'.fallback',[offered,served,idx,m['api']['qwen_median'][1],'owners.days'],overflow_cost)
        for i,team in enumerate(c.positions('owners.small_teams')):
            for j,residual in enumerate(c.positions('owners.residuals')):
                unit=c.unit_month(name+'.month.'+str(i)+'.'+str(j),srv,residual)
                for k,hours in enumerate(c.positions('owners.windows')):
                    n=name+'.'+str(i)+'.'+str(j)+'.'+str(k)
                    def policy_ok(team,location,bound):
                        if location=='office' and team<=bound:raise InputGap('operations.small_team_max','office boxes are reserved for large companies; small remote teams use colocation')
                        return True
                    admitted=c.add(n+'.admitted',[team,p+'.location','operations.small_team_max'],policy_ok)
                    boxes=c.add(n+'.units',[team,served,seconds,hours,'owners.load',admitted],lambda n,c,s,h,l,a:max(1,math.ceil(n*c*s/(h*3600*l))))
                    window_storage=c.hosting.storage(n,hosting['bytes'],hours)
                    storage=c.add(n+'.storage',[team,window_storage],lambda t,p:t*p)
                    owned=c.add(n+'.own',[boxes,unit,team,fallback,storage],lambda n,p,t,f,s:n*p+t*f+s)
                    rent=c.add(n+'.rent',[boxes,p+'.hourly',hours,'owners.days',team,fallback,storage],lambda n,p,h,d,t,f,s:n*p*h*d+t*f+s)
                    selected_cost=rent if key in c.scenario['rental_options'] else owned
                    colo=c.add(n+'.colo',[boxes,srv['colo']],lambda n,p:n*p)
                    rows.append({'team':team,'option':srv['label'],'deployment':p+'.location','mode':c.label(n+'.mode','hourly rental' if key in c.scenario['rental_options'] else 'owned'),
                                 'server_precision':c.precision_label,'share':'paper_tables.sizing_share','hours':hours,'residual':residual,'fit_share':fraction,'offered_calls_day':offered,'server_calls_day':served,
                                 'units':boxes,'compute_gpu_s_call':compute_seconds,'migration_gpu_s_call':migration_seconds,'hosting_storage_month':storage,'colo_month':colo,'overflow_api_user_month':fallback,'owned_month':owned,'rent_month':rent,'monthly_cost':selected_cost,
                                 'per_user_month':c.add(n+'.user',[selected_cost,team],lambda p,n:p/n),'buy_beats_rent':c.add(n+'.wins',[owned,rent],lambda o,r:int(o<r))})
    cols={k:'text' if k in ('option','deployment','mode','server_precision') else 'person' if k=='team' else 'h/day' if k=='hours' else '1' if k in ('share','residual','fit_share','buy_beats_rent') else 'server unit' if k=='units' else 'call/user/day' if k.endswith('_day') else 's/call' if k.endswith('_s_call') else 'USD/user-month' if k in ('per_user_month','overflow_api_user_month') else 'USD/team-month' for k in rows[0]}
    c.table('remote_rent_buy','Remote prefill rent or buy (whole warm windows, residual grid; office restricted)',cols,rows)


def client_table(c):
    rows=[]
    for key in c.scenario['capacity_clients']:
        p='hardware.clients.'+key
        for i,link in enumerate(c.positions('paper_tables.links')):
            cl=c.client(key,link,'link'+str(i));n='sessions.'+key+'.'+str(i)
            local=c.add(n+'.local',[cl['local_capacity'],'workload.chunk_calls'],lambda cap,k:cap/k)
            hybrid=c.add(n+'.hybrid',[cl['capacity'],'workload.chunk_calls'],lambda cap,k:cap/k)
            rows.append({'client':p+'.label','link_mbit':c.add(n+'.mbit',[link],lambda b:b/1e6),'hours':'paper_tables.hours','streams':cl['streams'],'min_streams':cl['min_streams'],'max_streams':cl['max_streams'],
                         'bandwidth':p+'.bandwidth','compute':p+'.compute','prefill_compute_scale':c.add(n+'.scale',[p+'.compute','hardware.clients.m3max.compute'],lambda b,a:b/a),
                         'fit_share':c.add(n+'.fraction',[cl['indices'],c.valid],lambda idx,rows:len(idx)/len(rows)),
                         'single_tok_s_32k':cl['single'],'tok_s_stream_32k':cl['rate'],'aggregate_gain_32k':cl['gain'],
                         'local_sessions_day':local,'hybrid_sessions_day':hybrid,'gain':c.add(n+'.gain',[hybrid,local],lambda h,l:h/l)})
    cols={k:'text' if k=='client' else 'Mbit/s' if k=='link_mbit' else 'h/day' if k=='hours' else 'stream' if k in ('streams','min_streams','max_streams') else 'B/s' if k=='bandwidth' else 'FLOP/s' if k=='compute' else 'token/s' if 'tok_s' in k else 'session/day (supported mix)' if k.endswith('sessions_day') else '1' for k in rows[0]}
    c.table('client_sessions_day','Client sessions per eight-hour day (measured prefill/parallel anchor, scaled estimates)',cols,rows)


def offload_table(c):
    m=c.model('qwen27');srv=c.server(c.scenario['cluster_option'],m);local=c.local_rate(c.scenario['reference_client'],m);rows=[]
    for i,bits in enumerate(c.positions('paper_tables.state_bits')):
        def state(s,b):
            if b not in (16,32):raise InputGap('paper_tables.state_bits','supported state formats are 16 or 32 bits')
            return s*b/32
        sx=c.add('offload.state.'+str(i),[m['state'],bits],state)
        wire=c.add('offload.model.'+str(i),[m['flop'],'owners.models.qwen27.kv',sx],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
        migration=c.hosting.vector('offload.'+str(i),c.valid,m['kv'],m['state'])
        for j,link in enumerate(c.positions('paper_tables.offload_links')):
            n='offload.'+str(i)+'.'+str(j)
            l=c.add(n+'.link',[link,'paper_tables.offload_goodput','hardware.links.wan.latency'],lambda b,g,t:dict(bandwidth=b,goodput=g,latency=t))
            result=c.add(n+'.result',[c.valid,local,wire,srv['compute'],l,migration],offload_stats)
            def conditional(r):
                if not r['wins']:raise InputGap('paper_tables.offload_links','no calls benefit; conditional saving undefined')
                return r['total']/r['wins']
            rows.append({'state_bits':bits,'state_bytes':sx,'link_mbit':c.add(n+'.mbit',[link],lambda b:b/1e6),'share_calls':c.add(n+'.share',[result],lambda r:r['share']),
                         'saved_seconds_call':c.add(n+'.saved',[result],lambda r:r['saved']),'saved_seconds_offloaded':c.add(n+'.conditional',[result],conditional)})
    c.table('offload_by_link','Offload by link (calc9 D line-rate convention; state conversion estimated)',{'state_bits':'bit','state_bytes':'B','link_mbit':'Mbit/s','share_calls':'1','saved_seconds_call':'s/all calls','saved_seconds_offloaded':'s/offloaded call'},rows)


def traffic_table(c):
    cl=c.client(c.scenario['traffic_client'],'hardware.links.wan.bandwidth','base');rows=[]
    for profile in c.scenario['traffic_profiles']:
        name='traffic.'+profile;calls='service.profiles.'+profile
        fraction=c.add(name+'.fit',[cl['indices'],c.valid],lambda idx,rows:len(idx)/len(rows))
        served=c.add(name+'.served',[calls,fraction,cl['capacity']],lambda n,f,cap:min(n*f,cap))
        offered=c.add(name+'.offered',[calls,fraction,cl['downloads'],'owners.days'],lambda n,f,b,d:n*f*b*d/1e12)
        actual=c.add(name+'.actual',[served,cl['downloads'],'owners.days'],lambda n,b,d:n*b*d/1e12)
        row={'profile':c.label(name+'.label',profile),'client':'hardware.clients.'+c.scenario['traffic_client']+'.label','streams':cl['streams'],'calls_day':calls,'served_day':served,
             'overflow_day':c.add(name+'.overflow',[calls,served],lambda n,s:n-s),'bytes_per_served_call':cl['downloads'],'offered_tb_month':offered,'hybrid_tb_month':actual}
        for i,price in enumerate(c.positions('paper_tables.egress_prices')):
            row['price_'+str(i)]=price;row['egress_'+str(i)]=c.add(name+'.egress.'+str(i),[actual,price],lambda tb,p:tb*p)
            row['offered_egress_'+str(i)]=c.add(name+'.offered_egress.'+str(i),[offered,price],lambda tb,p:tb*p)
        rows.append(row)
    cols={k:'text' if k in ('profile','client') else 'stream' if k in ('streams','min_streams','max_streams') else 'call/day' if k.endswith('_day') else 'B/call' if k=='bytes_per_served_call' else 'TB/month' if k.endswith('tb_month') else 'USD/TB' if k.startswith('price_') else 'USD/month' for k in rows[0]}
    c.table('traffic_user_month','Traffic per user-month (offered demand and Mac-capped hybrid)',cols,rows)


def glm_table(c):
    m=c.model('glm');key=c.scenario['glm_client'];p='hardware.clients.'+key
    server=c.server(c.scenario['cluster_option'],m);month=c.unit_month('long.unit_month',server,'owners.residual')
    local=c.local_rate(key,m)
    memory=c.add('long.memory',[p+'.memory','owners.client_reserve',m['weights'],m['kv'],m['state']],lambda mem,r,w,k,s:lambda d:max(0,math.floor((mem-r-w)/(k*d+s))))
    decoder=c.g.bundle('pt.long.decoder','models.glm',('experts','active_experts','shared_bytes','routed_bytes','decode_kv_slope','decode_fixed'))
    decoder=c.add('long.decoder_quant',[decoder,c.client_bpp,'owners.formats.Q4',m['state']],lambda d,b,q,s:dict(d,shared_bytes=d['shared_bytes']*b/q,routed_bytes=d['routed_bytes']*b/q,state=s))
    def rate_fn(d,b,e,passes):
        if d['active_experts']>d['experts']:raise InputGap('models.glm.active_experts','active experts exceed total experts')
        return lambda k,depth:b*e/step_bytes(d,k,depth,passes)
    rate=c.add('long.rate',[decoder,p+'.bandwidth','hardware.glm_family.m5ultra.efficiency','analysis.decode_state_passes'],rate_fn)
    wire=c.add('long.wire',[m['flop'],m['kv'],'models.glm.wire_state'],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
    link=c.g.bundle('pt.long.link','hardware.links.wan',('bandwidth','goodput','latency'))
    api=m['api']['glm'][0]
    ingest=c.add('long.ingest_local',[local,'paper_tables.glm.ingest_tokens','paper_tables.glm.integration_step'],lambda rate,n,step:integrate(lambda d:1/rate(d),n,step))
    def ingest_remote(fm,compute,wire,link,n,step,free):
        if n*wire['kv']+wire['wire_state']>free:raise InputGap(server['prefix']+'.memory','cold-ingest KV does not fit server replica')
        return integrate(lambda d:flop(fm,d),n,step)/compute+transfer(n,wire['kv'],wire['wire_state'],link)
    remote=c.add('long.ingest_remote',[m['flop'],server['compute'],wire,link,'paper_tables.glm.ingest_tokens','paper_tables.glm.integration_step',server['free']],ingest_remote)
    def studio_price(price,residual,years,power,hours,days,energy):return price*(1-residual)/(12*years)+power*hours*days*energy
    studio=c.add('long.studio',[p+'.purchase_price','economics.client_residual','owners.years',p+'.power','paper_tables.hours','owners.days','prices.energy_client'],studio_price)
    rows=[]
    for j,depth in enumerate(c.positions('paper_tables.glm.contexts')):
        n='long.'+str(j)
        calls=c.add(n+'.calls',[c.valid,'paper_tables.glm.start_depth',depth,'models.glm.context_limit'],growing_calls)
        final=c.add(n+'.final',[calls],lambda rows:rows[-1][0]+rows[-1][1]+rows[-1][2])
        def fit(fn,d):
            k=fn(d)
            if k<1:raise InputGap(p+'.memory','GLM weights + KV/state + reserve do not fit a complete session')
            return k
        sessions=c.add(n+'.fit',[memory,depth],fit)
        streams=c.add(n+'.streams',[sessions,'paper_tables.glm.streams'],min)
        decode=c.add(n+'.tok_s',[rate,streams,depth],lambda fn,k,d:fn(k,d))
        migration=c.hosting.vector(n,calls,m['kv'],m['state'])
        def admission(rows,fm,compute,l,r,free,state,migration):
            if any((d+n+o)*fm['kv']+state>free for d,n,o,t in rows):raise InputGap(server['prefix']+'.memory','GLM context does not fit server replica')
            return policy_with_reload(rows,fm,compute,l,r,migration)
        steps=c.add(n+'.policy',[calls,wire,server['compute'],link,local,server['free'],m['state'],migration],admission)
        local_steps=c.add(n+'.local_steps',[calls,local],lambda rows,r:[(x/r(d),x/r(d),0,False) for d,x,o,t in rows])
        bounded=c.add(n+'.end_memory',[calls,memory],end_memory)
        capacity=c.add(n+'.capacity_calls',[calls,steps,streams,bounded,rate,'paper_tables.hours'],throughput)
        capacity=c.add(n+'.capacity',[capacity,calls],lambda cap,rows:cap/len(rows))
        localcap=c.add(n+'.local_capacity',[calls,local_steps,streams,bounded,rate,'paper_tables.hours'],throughput)
        localcap=c.add(n+'.local_sessions',[localcap,calls],lambda cap,rows:cap/len(rows))
        served=c.add(n+'.served',['paper_tables.glm.sessions_day',capacity],min)
        overflow=c.add(n+'.overflow',['paper_tables.glm.sessions_day',served],lambda n,s:n-s)
        api_session=c.add(n+'.api',[calls,api],lambda rows,p:sum(api_vector(rows,p,len(rows))))
        own_s=c.own_seconds(n+'.own_seconds',calls,m,server,per_call=False)
        shadow=c.add(n+'.shadow',[calls,m['flop'],server['total_compute']],lambda rows,m,compute:mean_flops(rows,m)*len(rows)/compute)
        hosting=c.hosting.summary(n+'.hosting',calls,m['kv'],m['state'],steps)
        migration_s=c.add(n+'.migration_seconds',[hosting['seconds'],calls,server['prefix']+'.gpus'],lambda s,rows,g:s*len(rows)/g)
        shadow=c.add(n+'.with_hosting',[shadow,migration_s],lambda a,b:a+b)
        downloads=c.add(n+'.downloads',[steps],lambda rows:sum(x[2] for x in rows))
        egress=c.add(n+'.egress',[downloads,'prices.egress'],lambda b,p:b/1e12*p)
        for i,team in enumerate(c.positions('paper_tables.teams')):
            nm=n+'.team.'+str(i)
            def units(n,d,s,h,load):return max(1,math.ceil(n*d*s/(h*3600*load)))
            ownunits=c.add(nm+'.own_units',[team,'paper_tables.glm.sessions_day',own_s,'paper_tables.hours','owners.load'],units)
            calls_day=c.add(nm+'.calls_day',[served,calls],lambda sessions,rows:sessions*len(rows))
            migration_day=c.hosting.daily(nm,hosting,calls_day,served)
            compute_shadow=c.add(nm+'.compute_shadow',[calls,m['flop'],server['total_compute']],lambda rows,m,c:mean_flops(rows,m)*len(rows)/c)
            daily_shadow=c.add(nm+'.daily_shadow',[served,compute_shadow,migration_day,server['prefix']+'.gpus'],lambda s,w,io,g:s*w+io/g)
            hyunits=c.add(nm+'.hybrid_units',[team,daily_shadow,'paper_tables.hours','owners.load'],lambda t,w,h,l:max(1,math.ceil(t*w/(h*3600*l))))
            monthly=c.add(nm+'.month_sessions',[team,'paper_tables.glm.sessions_day','owners.days'],lambda n,s,d:n*s*d)
            owncost=c.add(nm+'.own',[ownunits,month,monthly],lambda n,p,s:n*p/s)
            without=c.add(nm+'.hybrid_base',[hyunits,month,team,studio,served,egress,'owners.front_month','owners.days',monthly,hosting['storage']],lambda units,p,n,mac,s,e,front,d,sessions,storage:(units*p+n*(mac+front+storage+s*e*d))/sessions)
            spill=c.add(nm+'.spill',[team,overflow,api_session,'owners.days',monthly],lambda n,o,p,d,s:n*o*p*d/s)
            hybrid=c.add(nm+'.hybrid',[without,spill],lambda base,spill:base+spill)
            rows.append({'context':depth,'final_depth':final,'team':team,'client':p+'.label','server_precision':c.precision_label,'client_quant':'owners.client_quant',
                         'calls_session':c.add(nm+'.call_count',[calls],len),'sessions_fit':sessions,'streams':streams,'decode_tok_s_stream':decode,
                         'local_sessions_day':localcap,'hybrid_capacity_sessions_day':capacity,'requested_sessions_day':'paper_tables.glm.sessions_day','served_sessions_day':served,'overflow_sessions_day':overflow,
                         'api_session':api_session,'own_cluster_session':owncost,'hybrid_without_overflow_session':without,'overflow_api_session':spill,'hybrid_session':hybrid,
                         'own_units':ownunits,'hybrid_units':hyunits,'studio_month':studio,'download_bytes_session':downloads,
                         'ingest_1m_local_s':ingest,'ingest_1m_server_s':remote})
    cols={k:'text' if k in ('client','server_precision','client_quant') else 'token' if k in ('context','final_depth') else 'person' if k=='team' else 'stream' if k in ('streams','min_streams','max_streams') else 'token/s' if k=='decode_tok_s_stream' else 'call/session' if k=='calls_session' else 'resident session' if k=='sessions_fit' else 'session/day' if k.endswith('_day') else 'server unit' if k.endswith('_units') else 's' if k.endswith('_s') else 'B/session' if k=='download_bytes_session' else 'USD/month' if k=='studio_month' else 'USD/requested session' for k in rows[0]}
    c.table('glm_long_sessions','GLM growing sessions 200k to 1M (purchased Studio and owned cluster; overflow costed)',cols,rows)


def deep_fit_table(c):
    rows=[]
    for key in c.scenario['fit_models']:
        m=c.model(key);p='owners.models.'+key
        for quant in ('Q4','Q3'):
            for ssd in ((False,True) if key=='flashnext' else (False,)):
                n='deep.'+key+'.'+quant+'.'+str(ssd)
                w=c.add(n+'.weights',[p+'.weights_q4','owners.formats.'+quant,'owners.formats.Q4'],lambda w,b,q:w*b/q)
                if ssd:
                    def without_ngram(w,ngram,b,total,p=p):
                        if ngram>total or w-ngram*b<=0:raise InputGap(p+'.ngram','invalid resident n-gram subtraction')
                        return w-ngram*b
                    w=c.add(n+'.ssd',[w,p+'.ngram','owners.formats.'+quant,p+'.parameters'],without_ngram)
                for i,memory in enumerate(c.positions('owners.memories')):
                    nm=n+'.'+str(i)
                    def maximum(mem,r,w,k,s,path=memory):
                        if mem-r-w<s:raise InputGap(path,'model weights + state + reserve do not fit even at depth zero')
                        return math.floor((mem-r-w-s)/k)
                    reach=c.add(nm+'.reach',[memory,'owners.client_reserve',w,m['kv'],m['state']],maximum)
                    supported_depth=c.add(nm+'.supported',[reach,'operations.context_limits.'+key],min)
                    row={'model':p+'.label','quant':c.label(nm+'.quant',quant),'placement':c.label(nm+'.placement','n-gram on SSD' if ssd else 'all weights in RAM'),
                         'memory':memory,'weights':w,'kv_per_token':m['kv'],'state_bytes':m['state'],'reserve':'owners.client_reserve','memory_depth':reach,'supported_depth':supported_depth}
                    for j,depth in enumerate(c.positions('operations.depths')):
                        def fit(mem,r,w,k,s,d,limit,path=memory,lp='operations.context_limits.'+key):
                            if d>limit:raise InputGap(lp,'depth exceeds declared model envelope')
                            return fit_sessions(mem,r,w,k,s,d,path)
                        suffix=('256k','500k','1m')[j] if j<3 else str(j)
                        row['depth_'+suffix]=depth
                        row['sessions_'+suffix]=c.add(nm+'.fit.'+suffix,[memory,'owners.client_reserve',w,m['kv'],m['state'],depth,'operations.context_limits.'+key],fit)
                    rows.append(row)
    cols={k:'text' if k in ('model','quant','placement') else 'token' if k.endswith('depth') or k.startswith('depth_') else 'B/token' if k=='kv_per_token' else 'resident session' if k.startswith('sessions_') else 'B' for k in rows[0]}
    c.table('client_fit_deep','Deep client fit (complete sessions, measured 27B affine slot geometry)',cols,rows)


def historical_crossover(inputs):
    """A separately named r4 reference; current paper client overrides must not rewrite history."""
    from .engine import load
    from .crossover import calculate
    scenario,reference=load('crossover-bridge')
    result=calculate(scenario,reference);table=result['tables'][0]
    try:selection=inputs.locate('paper_tables.crossover_steps')
    except ValueError:selection=None
    rows=[];dependencies={};alarms=[]
    if not isinstance(selection,list) or not selection:
        selection=[{'step':None,'paper_uses':'unavailable selection'}]
    for i,item in enumerate(selection):
        source=next((j for j,r in enumerate(table['rows']) if r['step']==item.get('step')),None) if isinstance(item,dict) else None
        if source is None or not isinstance(item.get('paper_uses'),str) or not item['paper_uses']:
            alarm={'input':'paper_tables.crossover_steps','reason':'unknown/missing crossover reference step'}
            row={k:{'alarm':[alarm]} for k in ('assumption','s20','s50','academic_s100','paper_uses')};alarms.append(alarm)
        else:
            row={'assumption':table['rows'][source]['step'],'paper_uses':item['paper_uses']}
            for dest,col in [('s20','s20'),('s50','s50'),('academic_s100','s100')]:
                value=copy.deepcopy(table['rows'][source][col])
                if isinstance(value,dict):
                    for a in value['alarm']:a['input']='r4_reference.'+a['input'];alarms.extend(value['alarm'])
                row[dest]=value
                d=copy.deepcopy(table['dependencies'][str(source)+'.'+col])
                d['inputs']=['r4_reference.'+x for x in d['inputs']];d['requires']=['r4_reference.'+x for x in d['requires']]
                dependencies[str(i)+'.'+dest]=d
        for col in ('assumption','s20','s50','academic_s100','paper_uses'):
            dependencies.setdefault(str(i)+'.'+col,{'requires':['paper_tables.crossover_steps'],'inputs':['paper_tables.crossover_steps']})
        rows.append(row)
    for path,quantity in reference.used.items():inputs.used['r4_reference.'+path]=quantity
    for name,record in reference.files.items():inputs.files['r4_reference.'+name]=dict(record,scope='r4_reference')
    return {'id':'crossover_explanation','name':'Crossover explanation (unchanged r4 reference, 20%/50%/academic100%)',
            'columns':{'assumption':'text','s20':'person','s50':'person','academic_s100':'person','paper_uses':'text'},'rows':rows,'dependencies':dependencies,'alarms':unique(alarms)}


def calculate(scenario,inputs):
    c=Context(scenario,inputs)
    person_tables(c);remote_table(c);client_table(c);offload_table(c);traffic_table(c);glm_table(c);deep_fit_table(c)
    result=c.g.result(scenario['name'],[
        'Full04 measured marginal mix, seeded normalization groups: original session chronology is unavailable. Generated tokens use output_per_call alone; reasoning is informational. Use workload.reasoning_extra_fraction=1 only for the reasoning-on-top upper bound (run10 accounting). Codex/Claude evidence is in workload provenance; Muse is treated the same way unverified.',
        'Dense decode interpolates the hash-checked 32k M3 single/4-stream anchor (1.665015 aggregate interval gain), capped by calibrated memory bandwidth. The depth extrapolation is estimated and aggregate capacity is monotone in available streams. Other clients scale decode by bandwidth. Streams may fall below the requested four where per-call memory limits them; unsupported calls go to API.',
        'Local prefill = measured M3 curve at the same depth times compute/14 TFLOP/s, with a memory roofline. Equal FLOP efficiency across devices is estimated; M4 compute and replacement price are unmeasured estimates. Extrapolation beyond the last measured midpoint keeps FLOP efficiency constant.',
        'Each person-cost row charges all requested open calls, partitions the actual per-call API vector without resetting cache boundaries, and exposes both median and cheapest overflow totals. Remaining closed-model calls are a common excluded cost.',
        'Hybrid server compute and cold-tier migration are a shared rental service at target load; explicit incremental session-storage budget is charged per person. All client-served input/output tokens are eventually shadowed once. R9 appends only new KV, overwrites recurrent state and reserves the selected per-call/deferred catch-up plus daily-tail I/O; retention uses the selected window-weighted or month-long policy. Background promotion is not GPU time. Client purchase/energy/front are separate. Mac premium credits a baseline laptop only on laptop rows; Studios are extra devices. Own all-server uses integer B300 replica fleets and charges input prefill plus one output decode, no redundant output shadow.',
        'Remote rent/buy sizes a dedicated full-shadow pool including cold reload/spill and per-person session storage for all offered open calls before client caps; server-context overflow is priced at the median API. Warm rent pays the full 10h/24h windows. Buy flag compares four-year residual-adjusted monthly costs, not cash payback. Energy duty retains the stated historical budget.',
        'Client day capacities normalize supported measured calls into workload.chunk_calls groups. fit_share and per-call memory limitations are explicit; these are throughput estimates, not wall-clock latency measurements.',
        'Offload-by-link follows calc9 D raw line-rate goodput=1 and serialized KV bytes, adding the declared cold-prefix reload; its legacy output remains frozen.  client economics uses its separately declared WAN goodput. State16 transfer is estimated and does not establish cross-engine state equivalence.',
        'Traffic shows offered and client-capped volumes separately. Egress prices apply to decimal TB; API overflow has no hybrid-download charge.',
        'GLM growing sessions replay measured delta/output/tool increments from zero to the selected context, clipping the last call. Two sessions/day is an explicit demand estimate; all excess is API-priced. Studio and server hardware are bought with residual assumptions. GLM compute/parallel decode remain estimates, not M3 measurements.',
        'GLM cold ingest integrates the depth-dependent prefill model, then transfers KV/state once from one B300 replica. Client fit is memory geometry, not performance qualification at one million tokens.',
        'Crossover explanation is an independent historical r4 reference, sources/dependencies prefixed r4_reference. Current client/input overrides do not rewrite that reference. Its thresholds are bounded at 20000 and are not recalculated claims about the new client rows.'
    ])
    reference=historical_crossover(inputs);result['tables'].insert(3,reference)
    result['alarms']=unique(result['alarms']+reference['alarms'])
    result['computed_metrics']+=sum(type(v) in (int,float) for row in reference['rows'] for v in row.values())
    return result
