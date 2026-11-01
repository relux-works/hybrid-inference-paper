"""Canonical paper metrics: each output cell has explicit, independently evaluated dependencies."""
import math
from . import economics as ec
from . import glm
from .analysis_graph import (FLOP_FIELDS, calls_graph, curve_data, decode_calibration,
                             mean_field, mean_flops, slot_data)
from .inputs import InputGap
from .metrics import Graph, field, nonempty
from .performance import Curve, dense_decode, flop, memory_streams, payload, roofline_prefill, transfer


def combine(*parts):
    return dict(item for part in parts for item in part.items())


def matching(calls, memory):
    return [call for call in nonempty(calls) if memory(call[0] + call[1]) >= 1]


def policy(calls, model, server_eff, link, local_rate, cloud):
    rows=[]
    for depth,delta,output,tool in nonempty(calls):
        remote=transfer(delta,model['kv'],model['wire_state'],link)+delta*flop(model,depth)/server_eff
        local=None if cloud else delta/local_rate(depth)
        offload=cloud or remote<local
        rows.append((remote if offload else local, 0 if offload else local,
                     payload(delta,model['kv'],model['wire_state']) if offload else 0,offload))
    return rows


def throughput(calls, steps, streams, memory, rate, hours):
    if streams<1:
        raise InputGap('hardware.client.memory','no decode stream fits')
    device=occupied=0.0
    for (depth,delta,output,tool),(wait,local,wire,offload) in zip(nonempty(calls),steps):
        k=min(streams,memory(depth+delta))
        if k<1:
            raise InputGap('hardware.client.memory','no decode stream fits this call')
        r=rate(k,depth+delta)
        device+=local+output/(k*r)
        occupied+=(wait+output/r+tool)/k
    bound=max(device,occupied)/len(calls)
    if bound<=0:
        raise InputGap('workload','zero service time; throughput is undefined')
    return hours*3600/bound


def choose_streams(km,cap,floor,rate,depth):
    if km<1:
        raise InputGap('hardware.client.memory','model does not fit at capacity_depth')
    eligible=[k for k in range(1,min(km,cap)+1) if rate(k,depth)>=floor]
    return (max(eligible),True) if eligible else (1,False)


def device_price(price,basis,baseline):
    if basis=='owned': return 0
    if basis=='laptop_premium': return max(0,price-baseline)
    if basis=='full': return price
    raise InputGap('hardware.client.cost_basis','unknown device cost_basis '+str(basis))


def calculate(scenario,inputs):
    g=Graph(inputs)
    add=g.add
    dense=scenario['kind']=='paper'
    model_path='models.'+scenario['model']
    server_path='hardware.servers.'+scenario['server']
    link_path='hardware.links.'+scenario['link']
    bundle=lambda name,prefix,fields:g.bundle(name,prefix,fields)
    calls,valid=calls_graph(g)
    mean_depth=mean_field(g,'mean.depth',valid,0)
    g.table('Sampled call mix (sessions are normalization groups)',
            {'calls':'call','calls_per_session':'call/session','mean_depth':'token','mean_new':'token/call','mean_output':'token/call'},
            [{'calls':add('call.count',[calls],len),'calls_per_session':'workload.chunk_calls','mean_depth':mean_depth,
              'mean_new':mean_field(g,'mean.new',valid,1),'mean_output':mean_field(g,'mean.output',valid,2)}])
    dates=g.measurement('dates')
    date_columns={'snapshot':'text','first':'UTC','last':'UTC','status':'text','calls':'call','contexts':'context'}
    date_fields={'snapshot':'dataset','first':'agents.all.call_time.first_utc','last':'agents.all.call_time.last_utc',
                 'status':'agents.all.call_time.status','calls':'agents.all.calls','contexts':'agents.all.contexts'}
    def date_value(document,path,key):
        value=field(document,path,'measurements.dates')
        if key in ('calls','contexts'):
            if type(value) is not int or value<0:
                raise InputGap('measurements.dates','invalid measured count '+path)
            return inputs.measured_value('dates',path,value,'call' if key=='calls' else 'context')
        if not isinstance(value,str) or not value:
            raise InputGap('measurements.dates','invalid measured metadata '+path)
        return value
    g.table('Separate call-date snapshot (not the call-mix denominator)',date_columns,
            [{key:add('dates.'+key,[dates],lambda data,p=path,k=key:date_value(data,p,k)) for key,path in date_fields.items()}])
    fmodel=bundle('model.flop',model_path,FLOP_FIELDS)
    if dense:
        depth_data=g.measurement('depth',json_lines=True)
        points=add('prefill.points',[depth_data],lambda data:curve_data(data,None,inputs).curve)
        curve=add('prefill.curve',[points,fmodel],lambda points,m:Curve(m,points))
        slot=add('slot.fit',[depth_data],lambda rows:slot_data(rows,inputs))
        state=add('slot.fixed',[slot],lambda pair:pair[1])
        # A failed package produces a visible placeholder row rather than dropping the table.
        outcome=g.resolve(points)
        indices=range(len(outcome.value)) if not outcome.alarms else range(1)
        refs=[]
        for index in indices:
            x=add('curve.depth.'+str(index),[points],lambda c,i=index:c[i][0])
            y=add('curve.rate.'+str(index),[points],lambda c,i=index:c[i][1])
            refs.append({'depth':x,'rate':y,'effective_compute':add('curve.compute.'+str(index),[x,y,fmodel],lambda depth,rate,m:rate*flop(m,depth))})
        g.table('M3 Max measured prefill calibration',{'depth':'token','rate':'token/s','effective_compute':'FLOP/s'},refs)
        normalized=g.measurement('normalized')
        calibration=add('decode.calibration',[normalized,model_path+'.weights',model_path+'.kv','hardware.clients.m3max.bandwidth','analysis.decode_state_passes',state],
                        lambda document,w,kv,bw,passes,s:decode_calibration(document,w,kv,bw,passes,s,inputs))
    else:
        state=model_path+'.state'
    kv=model_path+'.kv'
    wire_state=state if dense else model_path+'.wire_state'
    wire_model=add('model.wire',[fmodel,kv,wire_state],lambda m,k,s:combine(m,dict(kv=k,wire_state=s)))
    server_eff=add('server.effective',[server_path+'.peak',server_path+'.mfu'],lambda peak,mfu:peak*mfu)
    link=bundle('wan',link_path,('bandwidth','goodput','latency'))
    energy=add('unit.energy',[server_path+'.power','economics.pue','economics.hours_month','economics.load','prices.energy_dc'],lambda p,pue,h,load,price:p*pue*12*h*load*price)
    colo=add('unit.colo',[server_path+'.power','prices.colo'],lambda p,price:p*price*12)
    support=add('unit.support',[server_path+'.capex','economics.support'],lambda capex,rate:capex*rate)
    opex=add('unit.opex',[energy,colo,support],lambda *values:sum(values))
    month=add('unit.month',[server_path+'.capex','economics.server_residual','economics.years',opex],lambda capex,residual,years,opex:capex*(1-residual)/(12*years)+opex/12)
    def utilization(days,hours,regions,month_hours,peak):
        result=days*hours*regions/(month_hours*peak)
        if result>1: raise InputGap('economics.regions','regional utilization exceeds 1')
        return result
    util=add('owned.utilization',['economics.days_month','economics.hours_day','economics.regions','economics.hours_month','economics.peak'],utilization)
    owned_price=add('owned.gpu_s',[month,server_path+'.gpus','economics.hours_month',util],lambda cost,n,h,u:cost/(n*h*3600*u))
    rent_price=add('rental.gpu_s',['prices.rental_gpu_hour','economics.rental_utilization'],lambda price,u:price/(3600*u))
    own_model_fields=['server_weights','server_batch','server_stream_rate','server_bandwidth_efficiency'] if dense else ['server_batch','server_stream_rate','server_bandwidth_efficiency','experts','active_experts','server_shared_bytes','server_routed_bytes','decode_kv_slope','decode_fixed']
    own_extra=bundle('model.server_decode',model_path,own_model_fields)
    own_model=add('model.own',[fmodel,kv,state,own_extra],lambda m,k,s,extra:combine(m,extra,dict(kv=k,state=s)))
    own_server=bundle('server.resources',server_path,('peak','mfu','bandwidth','memory','reserved'))
    def own_parts(rows,m,srv,passes):
        if srv['reserved']>=srv['memory']:
            raise InputGap(server_path+'.reserved','reserved memory must be less than total memory')
        if not dense and m['active_experts']>m['experts']:
            raise InputGap(model_path+'.active_experts','active experts exceed expert count')
        step=(lambda k,depth,server=False:m['server_weights']+k*(depth*m['kv']+passes*m['state'])) if dense else (lambda k,depth,server=False:glm.step_bytes(m,k,depth,passes,server))
        decode={'step':step,'batch':m['server_batch'],'stream_rate':m['server_stream_rate'],'efficiency':m['server_bandwidth_efficiency']}
        return sum(ec.own_gpu_seconds(nonempty(rows),m,srv,decode,passes))
    own=add('own.gpu_seconds',[valid,own_model,own_server,'analysis.decode_state_passes'],own_parts)
    shadow_flop=add('shadow.flop',[valid,fmodel],mean_flops)
    shadow=add('shadow.seconds',[shadow_flop,server_eff],lambda f,eff:f/eff)
    def amount(name,seconds,price): return add(name,[seconds,price],lambda seconds,price:seconds*price)
    def scale(name,value,factor):return add(name,[value],lambda x:x*factor)
    def session(name,value):return add(name,[value,'workload.chunk_calls'],lambda x,n:x*n)
    own_cost=amount('own.cost',own,owned_price)
    operations=[]
    for name,seconds,price in [('Owned all-server',own,owned_price),('Rented all-server',own,rent_price),('Owned shadow prefill',shadow,owned_price),('Rented shadow prefill',shadow,rent_price)]:
        value=amount('operations.'+name,seconds,price)
        operations.append({'variant':g.constant('variant.'+name,name),'per_1000_calls':scale('operations.1000.'+name,value,1000),'per_session':session('operations.session.'+name,value)})
    g.table('Prefill and all-server operating alternatives (GPU only)',{'variant':'text','per_1000_calls':'USD','per_session':'USD'},operations)
    apis={};api_rows=[]
    for api_key in scenario['api_keys']:
        p='prices.apis.'+api_key
        tariff=bundle('api.tariff.'+api_key,p,('input','output','cache_read'))
        cost=add('api.cost.'+api_key,[valid,tariff],ec.api_cost)
        apis[api_key]=(tariff,cost)
        api_rows.append({'provider':p+'.label','per_1000_calls':scale('api.1000.'+api_key,cost,1000),'per_session':session('api.session.'+api_key,cost)})
    api_rows.append({'provider':g.constant('own.label','Own B300 cluster (demand-priced)'),
                     'per_1000_calls':scale('own.1000',own_cost,1000),'per_session':session('own.session',own_cost)})
    g.table('API and own cluster on the full sampled mix',{'provider':'text','per_1000_calls':'USD','per_session':'USD'},api_rows)
    client_refs=[];client_nodes={}
    for key in scenario['client_keys'] if dense else scenario['family_keys']:
        prefix=('hardware.clients.' if dense else 'hardware.glm_family.')+key
        node=lambda name,req,fn,k=key:add('client.'+k+'.'+name,req,fn)
        memory_model=node('memory_model',[model_path+'.weights',kv,state],lambda w,k,s:dict(weights=w,kv=k,state=s))
        if dense:
            memory=node('memory',[memory_model,prefix+'.memory','economics.usable_memory','economics.runtime_buffer'],lambda m,mem,u,b:lambda depth:memory_streams(m,dict(memory=mem),depth,u,b))
            rate=node('rate',[memory_model,prefix+'.bandwidth',calibration,'analysis.decode_state_passes','analysis.decode_calibration_scale'],lambda m,bw,cal,passes,scale:lambda k,depth:dense_decode(m,dict(bandwidth=bw),k,depth,cal[0],cal[1],passes)*scale)
            local=node('local',[fmodel,curve,prefix+'.prefill_scale',prefix+'.bandwidth',model_path+'.weights',model_path+'.prefill_batch',kv,'analysis.prefill_calibration_scale'],
                       lambda m,c,pf,bw,w,batch,kv,scale:lambda depth:1/roofline_prefill(m,depth,flop(m,depth)*c.rate(depth)*pf*scale,bw,w/batch+kv))
            basis=g.resolve(prefix+'.cost_basis')
            if not basis.alarms and basis.value=='laptop_premium':
                price=node('price',[prefix+'.price',prefix+'.cost_basis','economics.baseline_laptop'],device_price)
            else:
                def declared_price(value,basis,p=prefix):
                    if basis not in ('owned','full'):
                        raise InputGap(p+'.cost_basis','unknown device cost basis '+str(basis))
                    if basis=='owned' and value!=0:
                        raise InputGap(p+'.price','owned incremental price must be explicitly zero')
                    return value
                price=node('price',[prefix+'.price',prefix+'.cost_basis'],declared_price)
            inter=g.constant('client.'+key+'.inter',0)
            link_label=g.constant('client.'+key+'.link','single machine')
        else:
            memdev=bundle('client.'+key+'.memdev',prefix,('nodes','memory_per_node','buffer_per_node'))
            memory=node('memory',[memory_model,memdev,'economics.usable_memory'],lambda m,d,u:lambda depth:glm.capacity(m,d,depth,u))
            decode_fields=('experts','active_experts','shared_bytes','routed_bytes','decode_kv_slope','decode_fixed')
            dm=bundle('client.'+key+'.decode_model',model_path,decode_fields)
            decoder=node('decoder',[dm,state],lambda m,s:combine(m,dict(state=s)))
            dev=bundle('client.'+key+'.decoder_device',prefix,('nodes','bandwidth_per_node','efficiency','split'))
            # Topology is data; a missing topology is an alarm rather than an assumed single-node device.
            topology=g.resolve(prefix+'.nodes')
            if not topology.alarms and topology.value==1:
                ilink=g.constant('client.'+key+'.interlink',None)
                link_label=g.constant('client.'+key+'.link','none')
            else:
                comm=bundle('client.'+key+'.communication_model',model_path,('hidden_width','activation_bytes','boundary_messages'))
                decoder=node('distributed_decoder',[decoder,comm],combine)
                label=g.resolve(prefix+'.link')
                if label.alarms:
                    ilink=node('interlink',[prefix+'.link'],lambda x:x)
                else:
                    ilink=bundle('client.'+key+'.interlink','hardware.links.'+label.value,('bandwidth','goodput','latency'))
                link_label=node('link_label',[ilink],lambda link:'{} Gbit/s pipeline'.format(link['bandwidth']/1e9))
            def make_rate(m,d,passes,link,p=prefix):
                if m['active_experts']>m['experts']:
                    raise InputGap(model_path+'.active_experts','active experts exceed expert count')
                if d['split']!=('none' if d['nodes']==1 else 'pipeline'):
                    raise InputGap(p+'.split','only the declared pipeline split is modeled')
                return lambda k,depth:glm.decode_rate(m,d,k,depth,passes,link)[0]
            rate=node('rate',[decoder,dev,'analysis.decode_state_passes',ilink],make_rate)
            local=g.constant('client.'+key+'.local',None)
            price=prefix+'.price'
        km=node('memory_sessions',[memory,'analysis.capacity_depth'],lambda fn,depth:fn(depth))
        chosen=node('chosen',[km,'analysis.stream_cap','economics.decode_floor',rate,'analysis.rate_depth'],choose_streams)
        k=node('streams',[chosen],lambda pair:pair[0])
        floor=node('floor',[chosen],lambda pair:str(pair[1]))
        tok_s=node('tok_s',[rate,k,'analysis.rate_depth'],lambda fn,k,depth:fn(k,depth))
        if not dense:
            if not topology.alarms and topology.value==1:
                inter=node('inter',[prefix+'.nodes'],lambda nodes:0)
            else:
                inter=node('inter',[decoder,dev,k,ilink],glm.communication)
        matched=node('matched',[valid,memory],matching)
        fit=node('fit',[matched,valid],lambda subset,all:len(subset)/len(all))
        def require_supported(rows,p=prefix):
            if not rows: raise InputGap(p+'.memory','no sampled call fits device memory')
            return rows
        matched=node('matched_nonempty',[matched],require_supported)
        status=node('status',[fit],lambda share:'full mix' if share==1 else 'supported subset only')
        steps=node('policy',[matched,wire_model,server_eff,link,local],lambda rows,m,eff,link,local:policy(rows,m,eff,link,local,not dense))
        offload=node('offload',[steps],lambda rows:sum(row[3] for row in rows)/len(nonempty(rows)))
        bytes_call=node('bytes',[steps],lambda rows:sum(row[2] for row in rows)/len(nonempty(rows)))
        cap=node('throughput',[matched,steps,k,memory,rate,'economics.hours_day'],throughput)
        cap_session=node('capacity_session',[cap,'workload.chunk_calls'],lambda calls,n:calls/n)
        flops=node('shadow_flop',[matched,fmodel],mean_flops)
        seconds=node('server_seconds',[flops,server_eff],lambda f,eff:f/eff)
        srv=amount('client.'+key+'.server_cost',seconds,owned_price)
        rental=amount('client.'+key+'.rental_cost',seconds,rent_price)
        egress=node('egress',[bytes_call,'prices.egress'],lambda byte,price:byte/1e12*price)
        amort=node('amort',[price,'economics.client_residual','economics.years','economics.days_month',cap],lambda price,res,y,d,cap:price*(1-res)/(y*12*d*cap))
        electricity=node('electricity',[prefix+'.power','economics.hours_day','prices.energy_client',cap],lambda power,h,price,cap:power*h*price/cap)
        depth=mean_field(g,'client.'+key+'.depth',matched,0)
        storage=node('storage',[depth,kv,state,'economics.active_sessions','prices.dram','economics.parked_sessions','economics.storage_redundancy','prices.nvme','economics.years','economics.days_month','economics.calls_day'],
                     lambda L,kv,state,active,dram,parked,redundancy,nvme,y,d,calls:((L*kv+state)*active/1e9*dram+(L*kv+state)*parked/1e12*redundancy*nvme)/(y*12*d*calls))
        total=node('total',[srv,egress,amort,electricity,storage],lambda *values:sum(values))
        rental_total=node('rental_total',[rental,egress,amort,electricity,storage],lambda *values:sum(values))
        api=node('api',[matched,apis[scenario['api_keys'][0]][0]],ec.api_cost)
        own_secs=node('own_seconds',[matched,own_model,own_server,'analysis.decode_state_passes'],own_parts)
        own_cost_subset=amount('client.'+key+'.own_cost',own_secs,owned_price)
        row={'device':prefix+'.label','status':status,'memory_sessions':km,'streams':k,'tok_s_stream':tok_s,'meets_floor':floor,
             'session_capacity':cap_session,'fit_share':fit,'offload_share':offload,'per_1000_calls':scale('client.'+key+'.1000',total,1000),
             'per_session':session('client.'+key+'.session',total),'link':link_label,
             'inter_node_ms_step':scale('client.'+key+'.inter_ms',inter,1000)}
        for col,value in [('api_session',api),('own_session',own_cost_subset),('server_session',srv),('egress_session',egress),('device_session',amort),('energy_session',electricity),('storage_session',storage),('rental_session',rental_total)]:
            row[col]=session('client.'+key+'.'+col,value)
        client_refs.append(row)
        client_nodes[key]=dict(cap=cap,fit=fit,seconds=seconds,egress=egress,amort=amort,electricity=electricity,storage=storage)
    g.table("Decode hardware (costs use each row's supported calls; API/own use the same subset)",
            {'device':'text','status':'text','memory_sessions':'session at capacity_depth','streams':'stream','tok_s_stream':'token/s at rate_depth',
             'meets_floor':'bool','session_capacity':'session/working day','fit_share':'1','offload_share':'1','per_1000_calls':'USD','per_session':'USD',
             'api_session':'USD','own_session':'USD','server_session':'USD','egress_session':'USD','device_session':'USD','energy_session':'USD',
             'storage_session':'USD','rental_session':'USD','link':'text','inter_node_ms_step':'ms'},client_refs)
    build_fleets(g,scenario,client_nodes,own,opex,month,apis[scenario['api_keys'][0]][1],server_path)
    if dense: build_edge(g,inputs,fmodel,server_eff,link)
    return g.result(scenario['name'],[
        'Costs, hardware scaling and multi-node GLM behavior are estimates; prices are dated offline snapshots.',
        'Missing/invalid inputs raise cell alarms. No numeric substitute is used. Legacy complete-data wrappers are unchanged.',
        'full04 call mix and full05 partial call dates are separate snapshots. Sessions are normalization groups.',
        'Output alone is generated and billed; reasoning is informational. workload.reasoning_extra_fraction=1 is an explicit reasoning-on-top upper bound.',
        'GLM pairs use balanced sequential pipeline shards; capacity adds, bandwidth does not. No split runtime was tested.'])


def build_fleets(g,scenario,clients,own,opex,month,api,server_path):
    add=g.add
    client=clients[scenario['fleet_client']]
    def full_mix(share):
        if share<1:raise InputGap('hardware.fleet_client.memory','fleet client cannot support the full sampled mix')
        return share
    full=add('fleet.fullmix',[client['fit']],full_mix)
    grid_paths=g.positions('analysis.team_grid')
    rows=[]
    for index,n in enumerate(grid_paths):
        node=lambda name,req,fn,i=index:add('fleet.'+str(i)+'.'+name,req,fn)
        def units(people,seconds,regions,calls,hours,peak,gpus):
            return max(1,math.ceil(people/regions*calls*seconds/(hours*3600)*peak/gpus))
        shared=['economics.regions','economics.calls_day','economics.hours_day','economics.peak',server_path+'.gpus']
        no=node('own_units',[n,own]+shared,units)
        nh=node('hybrid_units',[n,client['seconds']]+shared,units)
        calls_month=node('calls_month',[n,'economics.calls_day','economics.days_month'],lambda n,calls,days:n*calls*days)
        boxes=node('boxes',[n,'economics.calls_day',client['cap'],full],lambda n,calls,cap,fit:math.ceil(n*calls/cap))
        client_scale=node('client_scale',[boxes,client['cap'],n,'economics.calls_day'],lambda boxes,cap,n,calls:boxes*cap/(n*calls))
        own_price=node('own_price',[no,month,calls_month],lambda n,month,calls:n*month/calls*1000)
        hyb_price=node('hybrid_price',[nh,month,calls_month,client['egress'],client['storage'],client['amort'],client['electricity'],client_scale,full],
                       lambda n,month,calls,egress,storage,amort,energy,scale,fit:(n*month/calls+egress+storage+(amort+energy)*scale)*1000)
        rows.append({'people':n,'decode_boxes':boxes,'own_units':no,'hybrid_units':nh,
                     'own_capex':node('own_capex',[no,server_path+'.capex'],lambda n,price:n*price),
                     'hybrid_capex':node('hybrid_capex',[nh,server_path+'.capex'],lambda n,price:n*price),
                     'own_opex_year':node('own_opex',[no,opex],lambda n,opex:n*opex),
                     'hybrid_opex_year':node('hybrid_opex',[nh,opex],lambda n,opex:n*opex),
                     'own_per_1000':own_price,'hybrid_per_1000':hyb_price,'api_per_1000':node('api',[api],lambda cost:cost*1000)})
    g.table('Integer B300 fleets ({}; declared regions)'.format(scenario['fleet_client']),
            {'people':'person','decode_boxes':'pooled client box/pair','own_units':'node','hybrid_units':'node','own_capex':'USD','hybrid_capex':'USD',
             'own_opex_year':'USD/year','hybrid_opex_year':'USD/year','own_per_1000':'USD','hybrid_per_1000':'USD','api_per_1000':'USD'},rows)
    crossing=[]
    for a,b in [('own_per_1000','api_per_1000'),('hybrid_per_1000','api_per_1000'),('own_per_1000','hybrid_per_1000')]:
        deps=[row[key] for row in rows for key in ('people',a,b)]
        def first(*values):
            records=[{'people':values[i],'a':values[i+1],'b':values[i+2]} for i in range(0,len(values),3)]
            result=ec.first_stays(records,'a','b')
            return 'no crossover on this grid' if result is None else result
        crossing.append({'comparison':g.constant('comparison.'+a+'.'+b,a+' <= '+b),'from_people':add('crossing.'+a+'.'+b,deps,first)})
    g.table('Team-size equilibrium (finite grid, no interpolation)',{'comparison':'text','from_people':'person or no crossover'},crossing)


def build_edge(g,inputs,fmodel,server_eff,link):
    rows=[]
    for key,prefix in g.mapping('edge'):
        if key is None:
            rows.append({column:prefix for column in ('device','fits','prompt','local_prefill','hybrid_ttft','decode_bound')})
            continue
        node=lambda name,req,fn,k=key:g.add('edge.'+k+'.'+name,req,fn)
        payload_bytes=node('payload',[prefix+'.prompt',prefix+'.kv',prefix+'.state'],payload)
        fits=node('fits',[prefix+'.weights',payload_bytes,'economics.runtime_buffer',prefix+'.memory','economics.usable_memory'],lambda w,state,buffers,m,u:w+state+buffers<=m*u)
        def require_fit(value,p=prefix):
            if not value: raise InputGap(p+'.memory','model and prompt do not fit')
            return value
        fit=node('fit_required',[fits],require_fit)
        work=node('flops',[prefix+'.base_flop',prefix+'.attention_slope',prefix+'.prompt'],lambda base,slope,n:base*n+slope*n*n/2)
        local=node('local',[work,prefix+'.compute',prefix+'.thermal',payload_bytes,prefix+'.bandwidth',fit],lambda work,compute,thermal,bytes,bw,fit:max(work/(compute*thermal),bytes/bw))
        remote=node('remote',[work,server_eff,prefix+'.prompt',prefix+'.kv',prefix+'.state',link,fit],lambda work,eff,n,kv,state,link,fit:work/eff+transfer(n,kv,state,link))
        decode=node('decode',[prefix+'.bandwidth',prefix+'.weights',prefix+'.prompt',prefix+'.kv','analysis.decode_state_passes',prefix+'.state',fit],lambda bw,w,n,kv,passes,state,fit:bw/(w+n*kv+passes*state))
        rows.append({'device':prefix+'.label','fits':node('fits_label',[fits],str),'prompt':prefix+'.prompt','local_prefill':local,'hybrid_ttft':remote,'decode_bound':decode})
    g.table('Edge one-shot ingestion (analytic bounds)',{'device':'text','fits':'bool','prompt':'token','local_prefill':'s','hybrid_ttft':'s','decode_bound':'token/s'},rows)
