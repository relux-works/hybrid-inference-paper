"""Closed-perimeter integer fleets, Studio occupancy and bounds-only decode charts."""
import math
from .analysis_graph import mean_flops
from .glm import step_bytes
from .inputs import InputGap
from .metrics import field,nonempty
from .paper import policy,throughput
from .paper_tables import Context,api_vector,end_memory,growing_calls
from .performance import flop
from .session_hosting import policy_with_reload


def fleet_units(seconds,hours,load):
    """Whole owned units, including the smallest viable idle/warm fleet."""
    return max(1,math.ceil(seconds/(hours*3600*load)))


def route_counts(requested,fraction,capacity):
    served=min(requested*fraction,capacity)
    return served,requested-served


def wait_stats(steps):
    waits=sorted(x[0] for x in nonempty(steps))
    return sum(waits)/len(waits),waits[max(0,math.ceil(.9*len(waits))-1)]


def pool_work(requested,all_seconds,served,eligible_seconds,shadow):
    turbo=requested*all_seconds-served*eligible_seconds
    if turbo < -1e-7:raise InputGap('workload','routed turbo work is negative; inconsistent eligible call accounting')
    return max(0,turbo)+served*shadow


def routed_wait(requested,served,client_wait,all_wait,eligible_wait):
    return (served*client_wait+requested*all_wait-served*eligible_wait)/requested


def shared_demand(team,sharing,capacity,requested):
    studios=math.ceil(team/sharing)
    total=studios*capacity if requested is None else team*requested
    served=min(total,studios*capacity)
    return studios,total,served,total-served


def decode_bound(streams,bandwidth,weights,depth,kv,state,passes):
    return streams*bandwidth/(weights+streams*(depth*kv+passes*state))


def perimeter_table(c):
    m=c.model('qwen27');servers={};rows=[]
    for key in c.scenario['perimeter_options']:
        srv=c.server(key,m);n='r6.perimeter.server.'+key
        month=c.unit_month(n+'.month',srv,'owners.residual')
        seconds=c.own_seconds(n+'.all_seconds',c.valid,m,srv)
        servers[key]=(srv,month,seconds)
    link=c.g.bundle('pt.r6.perimeter.link','hardware.links.wan',('bandwidth','goodput','latency'))
    wire=c.add('r6.perimeter.wire',[m['flop'],'owners.models.qwen27.kv',m['state']],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
    profiles={}
    for profile in c.scenario['traffic_profiles']:
        profiles[profile]=c.add('r6.perimeter.profile.'+profile,['service.profiles.'+profile,'r6.perimeter.share'],lambda n,s:n*s)
    for pi,team in enumerate(c.positions('paper_tables.teams')):
        for profile,requested in profiles.items():
            n='r6.perimeter.'+str(pi)+'.'+profile
            zero=c.label(n+'.zero',0);none=c.label(n+'.none','not applicable')
            # Policy selection is distinct from physical sizing, so gaps in policy cannot corrupt costs.
            def eligible(t,bound,overlap,policy,key):
                if overlap>bound:raise InputGap('r6.perimeter.overlap_min','overlap starts above the small-host upper bound')
                return int(t>=overlap if key=='b300_node' else t<=bound)
            own={};elig={}
            for key,(srv,month,seconds) in servers.items():
                k=n+'.'+key
                elig[key]=c.add(k+'.eligible',[team,'r6.perimeter.small_team_max','r6.perimeter.overlap_min','r6.perimeter.policy'],lambda t,b,o,p,key=key:eligible(t,b,o,p,key))
                units=c.add(k+'.units',[team,requested,seconds,'owners.hours','owners.load'],lambda t,n,s,h,l:fleet_units(t*n*s,h,l))
                cost=c.add(k+'.cost',[units,month,team],lambda units,p,t:units*p/t)
                call=c.add(k+'.call',[cost,requested,'owners.days'],lambda p,n,d:p/(n*d))
                own[key]=(units,cost,call)
            choice=c.add(n+'.choice',sum(([elig[k],own[k][1]] for k in servers),[]),
                         lambda *v,keys=tuple(servers):min((v[2*i+1],key) for i,key in enumerate(keys) if v[2*i])[1])
            for key,(srv,month,seconds) in servers.items():
                units,cost,call=own[key];k=n+'.all.'+key
                server_wait=c.add(k+'.wait',[c.valid,m['flop'],srv['compute'],'hardware.links.wan.latency'],lambda calls,fm,compute,latency:sum(n*flop(fm,d)/compute+latency for d,n,o,t in nonempty(calls))/len(calls))
                selected=c.add(k+'.selected',[choice],lambda selected,key=key:int(selected==key))
                rows.append(dict(profile=c.label(k+'.profile',profile),team=team,route=c.label(k+'.route','all server'),client=none,basis=c.label(k+'.basis','server only'),server=srv['label'],
                                 share='r6.perimeter.share',case=c.label(k+'.case','closed perimeter; all calls open'),office_policy='r6.perimeter.policy',server_precision=c.precision_label,client_quant=none,eligible=elig[key],selected=selected,
                                 requested_day=requested,client_served_day=zero,turbo_day=requested,unserved_day=zero,external_calls_day=zero,client_served_share=zero,client_capacity_day=zero,
                                 streams=zero,min_streams=zero,max_streams=zero,p90_scope=c.label(k+'.p90_scope','all calls'),prefill_mean_s=server_wait,prefill_p90_s=c.add(k+'.p90',[c.valid,m['flop'],srv['compute'],'hardware.links.wan.latency'],lambda calls,fm,compute,latency:wait_stats([(n*flop(fm,d)/compute+latency,) for d,n,o,t in calls])[1]),
                                 units=units,unit_month=month,fleet_person_month=cost,all_server_call=call,prefill_reference_month=zero,turbo_reference_month=cost,fleet_adjustment_month=zero,
                                 device_month=zero,client_energy_month=zero,front_month=zero,hosting_storage_month=zero,person_month=cost))
            for client in c.scenario['economics_clients']:
                cl=c.client(client,'hardware.links.wan.bandwidth','r6');p='hardware.clients.'+client
                cn='r6.perimeter.client.'+client
                if cn not in c.cache:
                    fraction=c.add(cn+'.fraction',[cl['indices'],c.valid],lambda idx,all:len(idx)/len(nonempty(all)))
                    energy=c.add(cn+'.energy',[p+'.power','owners.hours','owners.days','prices.energy_client'],lambda p,h,d,e:p*h*d*e)
                    localsteps=c.add(cn+'.localsteps',[cl['matched'],cl['local']],lambda rows,rate:[(n/rate(d),n/rate(d),0,False) for d,n,o,t in rows])
                    localwait=c.add(cn+'.localwait',[localsteps],wait_stats)
                    bounded=c.add(cn+'.local_end_memory',[cl['matched'],cl['memory']],end_memory)
                    localcap=c.add(cn+'.localcap',[cl['matched'],localsteps,cl['streams'],bounded,cl['decoder'],'owners.hours'],throughput)
                    device=c.add(cn+'.device',[p+'.purchase_price',p+'.premium_credit','owners.residual','owners.years'],lambda p,b,r,y:max(0,p-b)*(1-r)/(12*y))
                    candidates={}
                    for key,(srv,month,seconds) in servers.items():
                        pre=cn+'.'+key
                        migration=c.hosting.vector(pre,cl['matched'],m['kv'],m['state'])
                        def admission(calls,model,compute,link,rate,free,state,migration,path=srv['prefix']+'.memory'):
                            if any((d+n+o)*model['kv']+state>free for d,n,o,t in calls):raise InputGap(path,'full context does not fit the owned prefill replica')
                            return policy_with_reload(calls,model,compute,link,rate,migration)
                        steps=c.add(pre+'.steps',[cl['matched'],wire,srv['compute'],link,cl['local'],srv['free'],m['state'],migration],admission)
                        bounded=c.add(pre+'.end_memory',[cl['matched'],cl['memory']],end_memory)
                        capacity=c.add(pre+'.capacity',[cl['matched'],steps,cl['streams'],bounded,cl['decoder'],'owners.hours'],throughput)
                        # Every client-served input AND output maintains the server copy, including local-only portions.
                        shadow=c.add(pre+'.shadow',[cl['matched'],m['flop'],srv['total_compute']],lambda rows,fm,compute:mean_flops(rows,fm)/compute)
                        hosting=c.hosting.summary(pre+'.hosting',cl['matched'],m['kv'],m['state'],steps,'owners.hours')
                        migration_work=c.add(pre+'.migration_work',[hosting['seconds'],srv['prefix']+'.gpus'],lambda s,g:s/g)
                        shadow=c.add(pre+'.shadow_hosting',[shadow,migration_work],lambda a,b:a+b)
                        eligible_s=c.own_seconds(pre+'.eligible_seconds',cl['matched'],m,srv)
                        wait=c.add(pre+'.wait',[steps],wait_stats)
                        all_wait=c.add(pre+'.turbo_all_wait',[c.valid,m['flop'],srv['compute'],'hardware.links.wan.latency'],lambda rows,fm,compute,latency:sum(n*flop(fm,d)/compute+latency for d,n,o,t in nonempty(rows))/len(rows))
                        eligible_wait=c.add(pre+'.turbo_eligible_wait',[cl['matched'],m['flop'],srv['compute'],'hardware.links.wan.latency'],lambda rows,fm,compute,latency:sum(n*flop(fm,d)/compute+latency for d,n,o,t in rows)/len(rows))
                        candidates[key]=(capacity,shadow,eligible_s,wait,all_wait,eligible_wait,hosting)
                    c.cache[cn]=(fraction,energy,localwait,device,candidates,localcap)
                fraction,energy,localwait,premium,candidates,localcap=c.cache[cn]
                for basis in ('owned','premium'):
                    k=n+'.'+client+'.'+basis
                    device=premium if basis=='premium' else zero
                    localserved=c.add(k+'.localserved',[requested,fraction,localcap],lambda n,f,cap:route_counts(n,f,cap)[0])
                    unserved=c.add(k+'.unserved',[requested,localserved],lambda n,s:n-s)
                    cost=c.add(k+'.localcost',[device,energy,'r6.perimeter.local_front_month'],lambda *v:sum(v))
                    base=dict(profile=c.label(k+'.profile',profile),team=team,client=p+'.label',basis=c.label(k+'.basis','Mac already owned' if basis=='owned' else 'Mac premium bought'),share='r6.perimeter.share',case=c.label(k+'.case','closed perimeter; all calls open'),
                              office_policy='r6.perimeter.policy',server_precision=c.precision_label,client_quant='owners.client_quant',requested_day=requested,external_calls_day=zero,streams=cl['streams'],min_streams=cl['min_streams'],max_streams=cl['max_streams'],device_month=device,client_energy_month=energy)
                    rows.append(dict(base,route=c.label(k+'.route','Macs only'),server=none,eligible=c.label(k+'.eligible',1),selected=c.label(k+'.selected',1),client_served_day=localserved,turbo_day=zero,unserved_day=unserved,
                                     client_served_share=c.add(k+'.share',[localserved,requested],lambda s,n:s/n),client_capacity_day=localcap,p90_scope=c.label(k+'.p90_scope','client-served subset'),prefill_mean_s=c.add(k+'.mean',[localwait],lambda w:w[0]),prefill_p90_s=c.add(k+'.p90',[localwait],lambda w:w[1]),
                                     units=zero,unit_month=zero,fleet_person_month=zero,all_server_call=zero,prefill_reference_month=zero,turbo_reference_month=zero,fleet_adjustment_month=zero,front_month='r6.perimeter.local_front_month',hosting_storage_month=zero,person_month=cost))
                    hybrid={}
                    for key,(srv,month,seconds) in servers.items():
                        pre=k+'.hybrid.'+key;capacity,shadow,eligible_s,wait,all_wait,eligible_wait,hosting=candidates[key]
                        served=c.add(pre+'.served',[requested,fraction,capacity],lambda n,f,cap:route_counts(n,f,cap)[0])
                        turbo=c.add(pre+'.turbo',[requested,served],lambda n,s:n-s)
                        work=c.add(pre+'.work',[requested,seconds,served,eligible_s,shadow],pool_work)
                        tail=c.add(pre+'.tail',[served,hosting['flush_seconds'],'hosting.sessions_per_person',srv['prefix']+'.gpus'],lambda n,s,c,g:min(n,c)*s/g if n else 0.0)
                        work=c.add(pre+'.work_with_tail',[work,tail],lambda a,b:a+b)
                        units=c.add(pre+'.units',[team,work,'owners.hours','owners.load'],lambda t,s,h,l:fleet_units(t*s,h,l))
                        fleet=c.add(pre+'.fleet',[units,month,team],lambda units,p,t:units*p/t)
                        preunits=c.add(pre+'.prefillunits',[team,served,shadow,tail,'owners.hours','owners.load'],lambda t,n,s,tail,h,l:fleet_units(t*(n*s+tail),h,l))
                        preref=c.add(pre+'.prefillref',[preunits,month,team],lambda units,p,t:units*p/t)
                        turboref=c.add(pre+'.turboref',[turbo,'owners.days',own[key][2]],lambda n,d,p:n*d*p)
                        adjustment=c.add(pre+'.adjustment',[fleet,preref,turboref],lambda actual,pre,turbo:actual-pre-turbo)
                        storage=c.add(pre+'.storage',[served,hosting['storage']],lambda n,p:p if n>0 else 0)
                        total=c.add(pre+'.total',[fleet,device,energy,'owners.front_month',storage],lambda *v:sum(v))
                        client_wait=c.add(pre+'.client_wait',[wait],lambda w:w[0])
                        mean=c.add(pre+'.mean',[requested,served,client_wait,all_wait,eligible_wait],routed_wait)
                        hybrid[key]=dict(base,route=c.label(pre+'.route','hybrid'),server=srv['label'],eligible=elig[key],client_served_day=served,turbo_day=turbo,unserved_day=zero,
                                         client_served_share=c.add(pre+'.share',[served,requested],lambda s,n:s/n),client_capacity_day=capacity,p90_scope=c.label(pre+'.p90_scope','client-served subset'),prefill_mean_s=mean,
                                         prefill_p90_s=c.add(pre+'.p90',[wait],lambda w:w[1]),units=units,unit_month=month,fleet_person_month=fleet,all_server_call=own[key][2],prefill_reference_month=preref,turbo_reference_month=turboref,fleet_adjustment_month=adjustment,
                                         front_month='owners.front_month',hosting_storage_month=storage,person_month=total)
                    hc=c.add(k+'.choice',sum(([elig[key],hybrid[key]['person_month']] for key in servers),[]),lambda *v,keys=tuple(servers):min((v[2*i+1],key) for i,key in enumerate(keys) if v[2*i])[1])
                    for key,row in hybrid.items():
                        row['selected']=c.add(k+'.select.'+key,[hc],lambda choice,key=key:int(choice==key));rows.append(row)
    text={'profile','route','client','basis','server','case','office_policy','p90_scope','server_precision','client_quant'}
    units={k:'text' if k in text else 'person' if k=='team' else 'call/day' if k.endswith('_day') else '1' if k in ('share','eligible','selected','client_served_share') else 'stream' if k.endswith('streams') else 's/call' if k.endswith('_s') else 'server unit' if k=='units' else 'USD/unit-month' if k=='unit_month' else 'USD/call' if k=='all_server_call' else 'USD/person-month' for k in rows[0]}
    c.table('perimeter_cost','Closed perimeter: local, integer all-server and hybrid/turbo fleets',units,rows)
    for profile in profiles:
        c.table('perimeter_cost_'+profile,'Closed perimeter / '+profile,units,[r for r in rows if c.g.resolve(r['profile']).value==profile])


def utilization_table(c):
    """Same physical GLM session as R5; demand and purchased Studio count vary."""
    m=c.model('glm');p='hardware.clients.'+c.scenario['glm_client'];n='r6.util'
    server=c.server(c.scenario['cluster_option'],m);month=c.unit_month(n+'.unitmonth',server,'owners.residual');local=c.local_rate(c.scenario['glm_client'],m)
    memory=c.add(n+'.memory',[p+'.memory','owners.client_reserve',m['weights'],m['kv'],m['state']],lambda mem,r,w,k,s:lambda d:max(0,math.floor((mem-r-w)/(k*d+s))))
    decoder=c.g.bundle('pt.'+n+'.decoder','models.glm',('experts','active_experts','shared_bytes','routed_bytes','decode_kv_slope','decode_fixed'))
    decoder=c.add(n+'.quant',[decoder,c.client_bpp,'owners.formats.Q4',m['state']],lambda d,b,q,s:dict(d,shared_bytes=d['shared_bytes']*b/q,routed_bytes=d['routed_bytes']*b/q,state=s))
    def decode(d,b,e,passes):
        if d['active_experts']>d['experts']:raise InputGap('models.glm.active_experts','active experts exceed total experts')
        return lambda k,depth:b*e/step_bytes(d,k,depth,passes)
    rate=c.add(n+'.rate',[decoder,p+'.bandwidth','hardware.glm_family.m5ultra.efficiency','analysis.decode_state_passes'],decode)
    wire=c.add(n+'.wire',[m['flop'],m['kv'],'models.glm.wire_state'],lambda fm,k,s:dict(fm,kv=k,wire_state=s))
    link=c.g.bundle('pt.'+n+'.link','hardware.links.wan',('bandwidth','goodput','latency'))
    studio=c.add(n+'.studio',[p+'.purchase_price','economics.client_residual','owners.years',p+'.power','paper_tables.hours','owners.days','prices.energy_client'],lambda price,r,y,p,h,d,e:price*(1-r)/(12*y)+p*h*d*e)
    rows=[]
    for j,depth in enumerate(c.positions('r6.utilization.contexts')):
        pre=n+'.'+str(j)
        calls=c.add(pre+'.calls',[c.valid,'paper_tables.glm.start_depth',depth,'models.glm.context_limit'],growing_calls)
        def fit(memory,depth):
            fit=memory(depth)
            if fit<1:raise InputGap(p+'.memory','GLM weights + KV/state + reserve do not fit a complete session')
            return fit
        sessions=c.add(pre+'.fit',[memory,depth],fit);streams=c.add(pre+'.streams',[sessions,'paper_tables.glm.streams'],min)
        migration=c.hosting.vector(pre,calls,m['kv'],m['state'])
        def admission(rows,wire,compute,link,local,free,state,migration):
            if any((d+n+o)*wire['kv']+state>free for d,n,o,t in rows):raise InputGap(server['prefix']+'.memory','GLM context does not fit server replica')
            return policy_with_reload(rows,wire,compute,link,local,migration)
        steps=c.add(pre+'.steps',[calls,wire,server['compute'],link,local,server['free'],m['state'],migration],admission)
        bounded=c.add(pre+'.end_memory',[calls,memory],end_memory)
        cap=c.add(pre+'.capcalls',[calls,steps,streams,bounded,rate,'paper_tables.hours'],throughput)
        cap=c.add(pre+'.capacity',[cap,calls],lambda cap,rows:cap/len(rows))
        api=c.add(pre+'.api',[calls,m['api']['glm'][0]],lambda calls,tariff:sum(api_vector(calls,tariff,len(calls))))
        own_s=c.own_seconds(pre+'.ownseconds',calls,m,server,per_call=False)
        shadow=c.add(pre+'.shadow',[calls,m['flop'],server['total_compute']],lambda calls,m,compute:mean_flops(calls,m)*len(calls)/compute)
        hosting=c.hosting.summary(pre+'.hosting',calls,m['kv'],m['state'],steps)
        migration_s=c.add(pre+'.migration_work',[hosting['seconds'],calls,server['prefix']+'.gpus'],lambda s,rows,g:s*len(rows)/g)
        shadow=c.add(pre+'.shadow_hosting',[shadow,migration_s],lambda a,b:a+b)
        egress=c.add(pre+'.egress',[steps,'prices.egress'],lambda steps,p:sum(x[2] for x in steps)*p/1e12)
        for i,team in enumerate(c.positions('r6.utilization.teams')):
            for u,sharing in enumerate(c.positions('r6.utilization.users_per_studio')):
                for z,demand in enumerate(c.positions('r6.utilization.sessions_day')+[None]):
                    nm=pre+'.'+str(i)+'.'+str(u)+'.'+str(z)
                    refs=[team,sharing,cap]+([demand] if demand is not None else [])
                    budget=c.add(nm+'.budget',refs,lambda t,u,c,*d:shared_demand(t,u,c,d[0] if d else None))
                    studios=c.add(nm+'.studios',[budget],lambda x:x[0]);requested=c.add(nm+'.requested',[budget],lambda x:x[1]);served=c.add(nm+'.served',[budget],lambda x:x[2]);spill=c.add(nm+'.spill',[budget],lambda x:x[3])
                    monthly=c.add(nm+'.monthly',[requested,'owners.days'],lambda n,d:n*d)
                    ownunits=c.add(nm+'.ownunits',[requested,own_s,'paper_tables.hours','owners.load'],lambda n,s,h,l:fleet_units(n*s,h,l))
                    tail=c.add(nm+'.tail',[served,team,hosting['flush_seconds'],'hosting.sessions_per_person',server['prefix']+'.gpus'],lambda s,t,io,n,g:t*min(s/t,n)*io/g if s else 0.0)
                    hyunits=c.add(nm+'.hyunits',[served,shadow,tail,'paper_tables.hours','owners.load'],lambda n,s,tail,h,l:fleet_units(n*s+tail,h,l))
                    owncost=c.add(nm+'.owncost',[ownunits,month,monthly],lambda n,p,d:n*p/d)
                    macpart=c.add(nm+'.macpart',[studios,studio,monthly],lambda n,p,d:n*p/d)
                    base=c.add(nm+'.base',[hyunits,month,studios,studio,team,'owners.front_month',served,egress,'owners.days',monthly,hosting['storage']],lambda units,p,macs,mac,team,front,served,e,days,total,storage:(units*p+macs*mac+team*(front+storage)+served*e*days)/total)
                    overflow=c.add(nm+'.overflow',[spill,api,requested],lambda o,p,n:o*p/n)
                    total=c.add(nm+'.total',[base,overflow],lambda b,o:b+o)
                    rows.append(dict(team=team,context=depth,client=p+'.label',users_per_studio=sharing,studios=studios,demand_mode=c.label(nm+'.mode','capacity' if demand is None else 'fixed'),
                                     requested_user_day=c.add(nm+'.user',[requested,team],lambda n,t:n/t),requested_team_day=requested,served_team_day=served,overflow_team_day=spill,
                                     capacity_studio_day=cap,utilization=c.add(nm+'.utilization',[served,studios,cap],lambda s,n,c:s/(n*c)),sessions_fit=sessions,streams=streams,
                                     studio_month=studio,studio_session=macpart,api_session=api,own_cluster_session=owncost,hybrid_base_session=base,overflow_api_session=overflow,hybrid_session=total,own_units=ownunits,hybrid_units=hyunits))
    units={k:'text' if k in ('client','demand_mode') else 'person' if k=='team' else 'token' if k=='context' else 'person/device' if k=='users_per_studio' else 'device' if k=='studios' else '1' if k=='utilization' else 'session/day' if k.endswith('_day') else 'stream' if k=='streams' else 'resident session' if k=='sessions_fit' else 'server unit' if k.endswith('_units') else 'USD/device-month' if k=='studio_month' else 'USD/requested session' for k in rows[0]}
    c.table('glm_utilization','GLM Studio utilization: fixed demand and one aggregate capacity per shared device',units,rows)


def decode_table(c):
    rows=[];prefix='r6.decode';m=c.model('qwen27')
    weights=c.add(prefix+'.weights',['owners.models.qwen27.weights_q4','r6.decode.client_quant'],lambda w,q:w)
    for client in c.scenario['decode_clients']:
        p='hardware.clients.'+client
        for i,memory in enumerate(c.positions(prefix+'.memories')):
            for j,depth in enumerate(c.positions(prefix+'.depths')):
                for k,streams in enumerate(c.positions(prefix+'.streams')):
                    n=prefix+'.'+client+'.'+str(i)+'.'+str(j)+'.'+str(k)
                    fits=c.add(n+'.fits',[memory,'owners.client_reserve',weights,streams,depth,c.kv,c.state],lambda mem,r,w,k,d,kv,s:int(w+r+k*(d*kv+s)<=mem))
                    bound=c.add(n+'.bound',[streams,p+'.bandwidth',weights,depth,'owners.models.qwen27.kv',c.state,prefix+'.state_passes'],decode_bound)
                    def usable(fits,bound,path=memory):
                        if not fits:raise InputGap(path,'K complete Q4/q8_0 sessions plus reserve do not fit; bandwidth bound is theoretical only')
                        return bound
                    actual=c.add(n+'.usable',[fits,bound],usable)
                    rows.append(dict(kind=c.label(n+'.kind','bandwidth bound'),client=c.label(n+'.client','M3 Max' if client=='m3max' else 'M5 Max'),memory=memory,depth=depth,streams=streams,quant='r6.decode.client_quant',kv_quant=c.label(n+'.kv_quant','q8_0'),
                                     bandwidth=p+'.bandwidth',weights=weights,reserve='owners.client_reserve',wire_kv='owners.models.qwen27.kv',resident_kv=c.kv,state=c.state,state_passes=prefix+'.state_passes',fits=fits,bandwidth_bound_aggregate=bound,aggregate_tok_s=actual))
    # Anchor coordinates and rates are read from the hash-checked package, not recreated as model parameters.
    for kind in ('single','parallel'):
        n=prefix+'.anchor.'+kind
        def anchor(doc,kind=kind):
            return field(doc,'parallel.frozen_v11_row','measurements.normalized')
        row=c.add(n+'.row',[c.normalized],anchor)
        depth=c.add(n+'.depth',[row],lambda r:field(r,'depth','measurements.normalized'))
        # Single rows have no stream field; a single stream is an identity, not a fitted input.
        streams=c.label(n+'.streams',1) if kind=='single' else c.add(n+'.streams',[row],lambda r:field(r,'streams','measurements.normalized'))
        rate=c.add(n+'.rate',[c.normalized],lambda d,kind=kind:field(d,'parallel.baseline_native_decode_tok_s' if kind=='single' else 'parallel.normalized_max_decode_interval_aggregate_tok_s','measurements.normalized'))
        bound=c.add(n+'.bound',[streams,'hardware.clients.m3max.bandwidth',weights,depth,'owners.models.qwen27.kv',c.state,prefix+'.state_passes'],decode_bound)
        fits=c.add(n+'.fits',['hardware.clients.m3max.memory','owners.client_reserve',weights,streams,depth,c.kv,c.state],lambda mem,r,w,k,d,kv,s:int(w+r+k*(d*kv+s)<=mem))
        rows.append(dict(kind=c.label(n+'.kind','measured'),client=c.label(n+'.client','M3 Max'),memory='hardware.clients.m3max.memory',depth=depth,streams=streams,quant='r6.decode.client_quant',kv_quant=c.label(n+'.kv_quant','q8_0'),
                         bandwidth='hardware.clients.m3max.bandwidth',weights=weights,reserve='owners.client_reserve',wire_kv='owners.models.qwen27.kv',resident_kv=c.kv,state=c.state,state_passes=prefix+'.state_passes',fits=fits,bandwidth_bound_aggregate=bound,aggregate_tok_s=rate))
    units={k:'text' if k in ('kind','client','quant','kv_quant') else 'B' if k in ('memory','weights','reserve','state') else 'B/s' if k=='bandwidth' else 'B/token' if k in ('wire_kv','resident_kv') else 'token' if k=='depth' else 'stream' if k=='streams' else '1' if k in ('fits','state_passes') else 'token/s aggregate' for k in rows[0]}
    c.table('decode_scaling','Qwen27 Q4/q8_0 decode: raw bandwidth bounds and separate measured 32k anchors',units,rows)


def calculate(scenario,inputs):
    c=Context(scenario,inputs)
    perimeter_table(c);utilization_table(c);decode_table(c)
    result=c.g.result(scenario['name'],[
        'Perimeter share=100% is a real closed-perimeter requirement. No API, outside prefill, rental or external egress enters perimeter costs. Existing link bandwidth/goodput/latency represent the organization-controlled path; transport encryption, compatible state export and rack facilities are assumed.',
        'Own-rack RTX PRO 6000 hosts explicitly override the usual small-team office exclusion. Small hosts are eligible through 100 users; B300 is eligible from the declared overlap. All candidates remain visible; selected marks the cheapest eligible integer fleet for that route/client/basis, not just the smallest GPU count.',
        'All-server sizing charges input-only prefill and one decode with resident-context occupancy, Q4 weights per independent GPU replica and target load. Hybrid eventually shadows every client-served input/output token once, whether locally read or offloaded, and adds append-only migration plus one deferred tail catch-up per active session-day and the selected retention storage; it combines this shadow and turbo work in the same integer pool. Turbo reference uses full all-server USD/call; signed fleet adjustment reconciles sharing/rounding with actual owned hardware cost.',
        'Local-only unserved calls are explicit. Hybrid routes all unsupported or capacity-excess calls to owned server decode. Client-served requests are a uniform thinning of eligible empirical calls, not a priority scheduler; wait means include the declared internal-path RTT for server routes and exclude queue delay. Hybrid p90 is the client-served subset, mean covers client and turbo; all-server p90 covers all calls.',
        'Client capacities retain R5 measured 32k single/four-stream interpolation with estimated depth/device scaling. Local prefill scales the hash-checked M3 curve by compute ratio, with the memory roofline. These capacities are estimates, not new measurements.',
        'GLM growing sessions and Studio price retain R5 assumptions; studios=ceil(team/users_per_Studio). Capacity mode saturates the actual integer Studio fleet. Fixed loads beyond capacity are GLM-API-priced as in R5; this separate table is not the closed-perimeter scenario. USD/session denominators are all requested sessions.',
        'Decode bound rows use K*BW/(weights+K*(depth*serialized_q8_KV+2*state)), without any measured-efficiency multiplier. Resident fit uses the measured 34844 B/token slot slope and one fixed-state allocation, plus the 12 GB reserve. A nonfit rate alarms; the raw theoretical bound remains numeric. Measured rows are only the two hash-checked 32k M3 anchors; no new K/depth efficiency is projected.'
    ])
    result['export_namespace']=scenario['export_namespace']
    return result
