"""Owner economics: explicit DAG inputs, quantization, finite fleets and client caps.

Quantized weights and tensor arithmetic are separate contracts. Arithmetic below is
an analytical capacity model, not an assertion that a serving engine supports it.
"""
import math
import statistics
from .analysis_graph import FLOP_FIELDS, calls_graph, curve_data, mean_flops
from .inputs import InputGap
from .metrics import Graph, field, nonempty
from .paper import policy, throughput
from .performance import flop
from .service import cached_api_cost, download_per_call


def fit_sessions(memory, reserve, weights, kv, state, context, path):
    available=memory-reserve-weights
    per_session=kv*context+state
    count=math.floor(available/per_session)
    if count<1:
        raise InputGap(path,'model does not fit: weights + KV + recurrent state + OS/app reserve exceed memory')
    return count


def selected(g,name,path,prefix):
    """Read only the chosen format, retaining a missing/invalid selector as a root alarm."""
    value=g.resolve(path)
    refs=[path] if value.alarms else [path,prefix+'.'+value.value]
    return g.add(name,refs,lambda *args:args[-1])


def anchor_rates(document,depth,inputs):
    rows=field(document,'depth.rows','measurements.normalized')
    matches=[r for r in rows if field(r,'depth','measurements.normalized')==depth]
    if len(matches)!=1:
        raise InputGap('owners.anchor_depth','no unique measured decode group at this depth')
    rates=[field(t,'server_decode_tok_s','measurements.normalized') for t in field(matches[0],'turns','measurements.normalized')]
    if not rates or any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in rates):
        raise InputGap('measurements.normalized','invalid native decode anchor')
    for i,value in enumerate(rates):inputs.measured_value('normalized','depth.anchor.'+str(i),value,'token/s')
    return min(rates),statistics.mean(rates),max(rates)


def parameter_ratio(active,total,path):
    if active>total:
        raise InputGap(path,'active parameters exceed total parameters')
    return active/total


def crossover(net_capex,rental,opex,path):
    if rental<=opex:
        raise InputGap(path,'buying never recovers net capex at this load: rent is no greater than ownership opex')
    return net_capex/(rental-opex)


def calculate(scenario,inputs):
    g=Graph(inputs)
    add=g.add
    label=lambda name,value:g.constant(name,value)
    def node(name,refs,fn):return add('owners.'+name,refs,fn)
    def bundle(name,path,fields):return g.bundle('owners.'+name,path,fields)
    calls,valid=calls_graph(g)
    measured=g.measurement('normalized')
    depth_rows=g.measurement('depth',json_lines=True)
    anchor=node('anchor',[measured,'owners.anchor_depth'],lambda d,x:anchor_rates(d,x,inputs))
    mean_anchor=node('anchor.mean',[anchor],lambda r:r[1])
    dense_model=bundle('qwen.flop','models.qwen27',FLOP_FIELDS)
    curve=node('curve',[depth_rows,dense_model],lambda rows,m:curve_data(rows,m,inputs))
    precision_label=node('precision_label',['owners.server_precision'],lambda p:'BF16 (academic reference)' if p=='BF16' else p)
    client_bpp=selected(g,'owners.client_bpp','owners.client_quant','owners.formats')
    server_bpp=selected(g,'owners.server_bpp','owners.server_precision','owners.formats')
    # Hardware/quant selectors determine graph topology, never substitute a physical default.
    precision=g.resolve('owners.server_precision')
    peak_field=None if precision.alarms else ('bf16_peak' if precision.value=='BF16' else 'fp4_peak' if precision.value=='NVFP4' else 'fp8_peak')
    def weight(model,quant,name,ssd=False):
        prefix='owners.models.'+model
        bpp='owners.formats.'+quant if quant else client_bpp
        refs=[prefix+'.weights_q4',bpp,'owners.formats.Q4']
        result=node(name,refs,lambda w,b,ref:w*b/ref)
        if ssd:
            def without_ngram(w,p,b,total):
                if p>total or w-p*b<=0:
                    raise InputGap(prefix+'.ngram','n-gram table leaves no positive resident model weights or exceeds total parameters')
                return w-p*b
            result=node(name+'.ssd',[result,prefix+'.ngram',bpp,prefix+'.parameters'],without_ngram)
        return result
    model_cache={}
    def model_nodes(key):
        if key in model_cache:return model_cache[key]
        p='owners.models.'+key
        mf=bundle(key+'.flop','models.'+key,FLOP_FIELDS)
        work=node(key+'.flops',[valid,mf],mean_flops)
        prefill=node(key+'.prefill_only',[valid,mf],lambda calls,m:mean_flops(calls,m,shadow=False))
        cw=weight(key,None,key+'.client_weights')
        sw=node(key+'.server_weights',[p+'.parameters',server_bpp],lambda n,b:n*b)
        # Q4 client weights are actual GGUF estimates. For dense decode traffic use full
        # weights; MoE traffic uses active/total ratio (expert union under batching below).
        active_ratio=node(key+'.active_ratio',[p+'.active_parameters',p+'.parameters'],lambda a,n:parameter_ratio(a,n,p+'.active_parameters'))
        maxdepth=node(key+'.maxdepth',[valid],lambda rows:max(d+n for d,n,o,t in rows))
        memory='owners.glm_client_memory' if key=='glm' else 'owners.client_memory'
        price='owners.glm_client_price' if key=='glm' else 'owners.client_price'
        fit=node(key+'.client_fit',[memory,'owners.client_reserve',cw,p+'.kv',p+'.state',maxdepth],
                 lambda m,r,w,k,s,d:fit_sessions(m,r,w,k,s,d,memory))
        sessions=node(key+'.sessions',[fit,'owners.parallel_agents'],min)
        # Owner's 0.30-0.37 efficiency coordinate is calibrated to measured native
        # tok/s. It must not be confused with efficiency computed using GGUF bytes.
        reftraffic=node(key+'.reftraffic',['owners.models.qwen27.weights_q4','owners.models.qwen27.kv','owners.models.qwen27.state','owners.anchor_depth','analysis.decode_state_passes'],lambda w,k,s,d,passes:w+k*d+passes*s)
        correction=node(key+'.correction',[mean_anchor,reftraffic,'owners.anchor_bandwidth','owners.anchor_efficiency'],lambda r,t,b,e:r*t/(b*e))
        def rate_fn(w,active_ratio,k,s,b,e,correction,passes):
            # Independent expert routing reads the union across simultaneous agents.
            # Dense models (active=total) share one weight read, as before.
            return lambda streams,depth:b*e*correction/(w*(1-(1-active_ratio)**streams)+streams*(k*depth+passes*s))
        rate=node(key+'.rate',[cw,active_ratio,p+'.kv',p+'.state','owners.client_bandwidth','owners.client_efficiency',correction,'analysis.decode_state_passes'],rate_fn)
        per_stream=node(key+'.rate_report',[rate,sessions,'owners.anchor_depth'],lambda rate,k,d:rate(k,d))
        # FLOP-scaled measured prefill curve is an explicit model estimate for GLM.
        local=node(key+'.local',[curve,dense_model,mf,'owners.client_prefill_scale','owners.formats.Q4',client_bpp],
                   lambda curve,base,m,scale,q4,q:lambda d:curve.rate(d)*flop(base,d)/flop(m,d)*scale*q4/q)
        wire=bundle(key+'.wire','hardware.links.wan',('bandwidth','goodput','latency'))
        # The shared service uses the same B300 admission reference for every SKU.
        compute=node(key+'.reference_compute',['service.transfer.decision_server_compute'],lambda x:x)
        wm=node(key+'.wiremodel',[mf,p+'.kv',p+'.state'],lambda m,k,s:dict(m,kv=k,wire_state=s))
        steps=node(key+'.policy',[valid,wm,compute,wire,local],lambda calls,m,c,l,r:policy(calls,m,c,l,r,False))
        capacity=node(key+'.capacity',[valid,steps,sessions,fit,rate,'owners.hours'],
                      lambda calls,steps,k,fit,rate,h:throughput(calls,steps,k,lambda d:fit,rate,h))
        # Pinned calc8 policy gives the same wire reference for Qwen as service sizing.
        transfer_settings=bundle(key+'.reference_wire','service.transfer',('wire_kv','wire_state','client_compute','decision_server_compute','bandwidth','goodput','latency'))
        if key=='qwen27':
            downloads=node(key+'.downloads',[valid,mf,transfer_settings],download_per_call)
        else:
            downloads=node(key+'.downloads',[steps],lambda rows:sum(x[2] for x in rows)/len(rows))
        api_key='glm' if key=='glm' else 'qwen_median'
        tariff=bundle(key+'.api_tariff','prices.apis.'+api_key,('output','cache_read','cache_write'))
        api=node(key+'.api',[valid,tariff,'workload.chunk_calls'],cached_api_cost)
        cheap_tariff=bundle(key+'.cheap_tariff','prices.apis.qwen_cheap',('output','cache_read','cache_write'))
        cheap=node(key+'.cheap',[valid,cheap_tariff,'workload.chunk_calls'],cached_api_cost) if key=='qwen27' else api
        state={'key':key,'label':p+'.label','flop':work,'prefill':prefill,'model':mf,'cw':cw,'sw':sw,
               'fit':fit,'sessions':sessions,'rate':per_stream,'capacity':capacity,'downloads':downloads,
               'api':api,'cheap':cheap,'price':price,'maxdepth':maxdepth}
        model_cache[key]=state
        return state
    option_cache={}
    def option_nodes(model,key):
        cachekey=(model['key'],key)
        if cachekey in option_cache:return option_cache[cachekey]
        mp='owners.models.'+model['key'];p='owners.options.'+key;name=model['key']+'.'+key
        def op(n,refs,fn):return node(name+'.'+n,refs,fn)
        def peak(precision,rate):
            if rate<=0:raise InputGap(p+'.'+peak_field,'NVFP4 FP4 unavailable on this GPU; Blackwell and engine support required')
            return rate
        pk=op('peak',['owners.server_precision',p+'.'+peak_field],peak) if peak_field else op('peak',['owners.server_precision'],lambda p:p)
        compute=op('compute',[pk,p+'.gpus','service.mfu',p+'.shard_efficiency'],lambda rate,n,mfu,shard:rate*n*mfu*shard)
        seconds=op('seconds',[model['flop'],compute],lambda work,rate:work/rate)
        pooled_mem=op('memory',[p+'.memory',p+'.gpus'],lambda m,n:m*n)
        copies=p+'.gpus' if scenario.get('replicated_dense') and model['key']=='qwen27' else label('copies.'+name,1)
        def free_memory(memory,weights,workspace,copies):
            if copies*(weights+workspace)>=memory:
                raise InputGap(p+'.memory','server model does not fit: {:.1f} GB weights + {:.1f} GB workspace >= {:.1f} GB pooled GPU memory (balanced sharding)'.format(copies*weights/1e9,copies*workspace/1e9,memory/1e9))
            return memory-copies*(weights+workspace)
        free=op('free',[pooled_mem,model['sw'],'owners.workspace',copies],free_memory)
        feasible=op('seconds_fit',[seconds,free],lambda s,free:s)
        def own_time(calls,pre,weights,parameters,active,kv,state,batch,bw,eff,gpus,shard,free,rate,passes):
            parameter_ratio(active,parameters,mp+'.active_parameters')
            # Prefill already contains output-token shadow work, matching service baseline.
            # Expert union assumes independent routing; dense is its active=total limit.
            union=parameters*(1-(1-active/parameters)**batch)
            step=weights*union/parameters/batch
            dec=sum(o*(step+(d+n)*kv+passes*state)/(bw*eff*gpus*shard) for d,n,o,t in calls)/len(calls)
            residence=sum(((d+n)*kv+state)*(o/rate+t)/free for d,n,o,t in calls)/len(calls)
            return pre+dec+residence
        own_pre=op('own_prefill',[model['prefill'],compute],lambda work,rate:work/rate) if scenario.get('correct_all_server_prefill') else seconds
        own=op('own_seconds',[valid,own_pre,model['sw'],mp+'.parameters',mp+'.active_parameters',mp+'.kv',mp+'.state','owners.server_batch',p+'.bandwidth','owners.server_bw_efficiency',p+'.gpus',p+'.shard_efficiency',free,'owners.server_stream_rate','analysis.decode_state_passes'],own_time)
        # Calendar operating costs do not acquire a discount merely because the
        # daily rental window is shorter. Office and datacenter rates are explicit.
        location=g.resolve(p+'.location')
        energy_price='prices.energy_client' if not location.alarms and location.value=='office' else 'prices.energy_dc'
        energy_load='owners.office_load' if not location.alarms and location.value=='office' else 'owners.load'
        colo_price='owners.office_colo' if not location.alarms and location.value=='office' else 'prices.colo'
        support_rate='owners.office_support' if not location.alarms and location.value=='office' else 'economics.support'
        energy=op('energy',[p+'.location',p+'.power','economics.pue','economics.hours_month',energy_load,energy_price],lambda loc,p,pue,h,l,price:p*pue*h*l*price)
        colo=op('colo',[p+'.location',p+'.power',colo_price,p+'.colo_min_month'],lambda loc,p,price,minimum:max(p*price,minimum)) if key in scenario.get('colocated_keys',[]) else op('colo',[p+'.location',p+'.power',colo_price],lambda loc,p,price:p*price)
        support=op('support',[p+'.capex',support_rate,p+'.location'],lambda capex,s,location:capex*s/12)
        opex=op('opex',[energy,colo,support],lambda *args:sum(args))
        result={'prefix':p,'label':p+'.label','seconds':feasible,'own_seconds':own,'opex':opex,'capex':p+'.capex','hourly':p+'.hourly','free':free,'colo':colo,'support':support}
        option_cache[cachekey]=result
        return result
    dense=model_nodes('qwen27')
    summary=option_nodes(dense,scenario['summary_option'])
    cluster=option_nodes(dense,scenario['cluster_option'])
    owned_hybrid=option_nodes(dense,scenario['owned_hybrid_option'])
    teams=g.positions('owners.teams');shares=g.positions('owners.shares');residuals=g.positions('owners.residuals');windows=g.positions('owners.windows')
    # Register each array shape once, including its failed-shape placeholder.
    # Reusing it across models/options prevents duplicate nodes when an entire catalogue is missing.
    memories=g.positions('owners.memories');contexts=g.positions('owners.contexts');small_teams=g.positions('owners.small_teams')
    def counts(name,team,demand,seconds,hours):
        return node(name,[team,demand,seconds,hours,'owners.load'],lambda n,d,s,h,l:max(1,math.ceil(n*d*s/(h*3600*l))))
    def unit_month(name,option,residual):
        return node(name,[option['capex'],residual,'owners.years',option['opex']],lambda cap,r,y,op:cap*(1-r)/(y*12)+op)
    def ratio(price,baseline,path):
        if baseline<=0:raise InputGap(path,'zero API baseline: price ratio undefined')
        return price/baseline
    def volume(name,model,share):
        requested=node(name+'.requested',['owners.calls_day',share],lambda d,s:d*s)
        served=node(name+'.served',[requested,model['capacity']],min)
        excess=node(name+'.excess',[requested,served],lambda r,s:r-s)
        return requested,served,excess
    def client_month(name,model,residual,fraction):
        return node(name,[model['price'],residual,'owners.years',fraction,'owners.client_power','owners.hours','owners.days','prices.energy_client'],
                    lambda price,r,years,f,p,h,d,e:price*(1-r)/12/years*f+p*h*d*e)
    rows=[];res_rows=[];break_rows=[];capacity_rows=[];cross_rows=[];share_totals=[]
    full=label('full_fraction',1)
    for i,share in enumerate(shares):
        name='share.'+str(i);requested,served,excess=volume(name,dense,share)
        bound=node(name+'.bound',[share],lambda s:'academic bound' if s==1 else 'decision case')
        capacity_rows.append({'share':share,'bound':bound,'requested_day':requested,'served_day':served,'excess_day':excess,'capacity_day':dense['capacity'],
                              'sessions':dense['sessions'],'tok_s_stream':dense['rate'],'quant':'owners.client_quant','prefill_scale':'owners.client_prefill_scale'})
        egress=node(name+'.egress',[served,dense['downloads'],'owners.days','prices.egress'],lambda s,b,d,p:s*b*d/1e12*p)
        fallback=node(name+'.fallback',[excess,dense['cheap'],'owners.days'],lambda e,c,d:e*c*d)
        median_fallback=node(name+'.fallback_median',[excess,dense['api'],'owners.days'],lambda e,c,d:e*c*d)
        apimed=node(name+'.apimed',[requested,dense['api'],'owners.days'],lambda n,p,d:n*p*d)
        apicheap=node(name+'.apicheap',[requested,dense['cheap'],'owners.days'],lambda n,p,d:n*p*d)
        pooled=node(name+'.pooled',[served,summary['seconds'],'owners.days',summary['hourly'],'owners.load'],lambda s,t,d,p,l:s*t*d*p/3600/l)
        cm=client_month(name+'.client_month',dense,'owners.residual','owners.client_cost_fraction')
        hybrid=node(name+'.hybrid',[pooled,egress,fallback,cm,'owners.front_month'],lambda *v:sum(v))
        hybrid_median=node(name+'.hybrid_median',[pooled,egress,median_fallback,cm,'owners.front_month'],lambda *v:sum(v))
        one_residual=unit_month(name+'.cluster_month',cluster,'owners.residual')
        share_totals.append(dict(requested=requested,unit=one_residual,api_median_user=apimed,api_cheapest_user=apicheap))
        for j,team in enumerate(teams):
            nm=name+'.team.'+str(j)
            boxes=counts(nm+'.cluster_boxes',team,requested,cluster['own_seconds'],'owners.hours')
            own=node(nm+'.cluster_user',[boxes,one_residual,team],lambda b,c,n:b*c/n)
            rows.append({'team':team,'share':share,'bound':bound,'server_precision':precision_label,'hybrid_user':hybrid,'own_cluster_user':own,'api_median_user':apimed,'api_cheapest_user':apicheap,
                         'cluster_boxes':boxes,'capacity_day':dense['capacity'],'served_day':served,'excess_day':excess,
                         'overflow_median_user':median_fallback,'overflow_cheapest_user':fallback,'hybrid_median_user':hybrid_median,'hybrid_cheapest_user':hybrid})
            for a,sres in enumerate(residuals):
                for b,cres in enumerate(residuals):
                    rm=nm+'.res.'+str(a)+'.'+str(b)
                    ownhybridboxes=counts(rm+'.boxes',team,served,owned_hybrid['seconds'],'owners.hours')
                    unit=unit_month(rm+'.unit',owned_hybrid,sres)
                    mac=client_month(rm+'.mac',dense,cres,full)
                    h=node(rm+'.hybrid',[ownhybridboxes,unit,team,mac,egress,fallback,'owners.front_month'],lambda boxes,u,n,*other:boxes*u/n+sum(other))
                    def savings(price,api,path):
                        if api<=0:raise InputGap(path,'zero API baseline: relative savings undefined')
                        return 1-price/api
                    res_rows.append({'team':team,'share':share,'bound':bound,'server':owned_hybrid['label'],'server_residual':sres,'client_residual':cres,'hybrid_user':h,
                                     'api_median_user':apimed,'api_cheapest_user':apicheap,'savings_median':node(rm+'.save_median',[h,apimed],lambda h,a:savings(h,a,'prices.apis.qwen_median')),
                                     'savings_cheapest':node(rm+'.save_cheap',[h,apicheap],lambda h,a:savings(h,a,'prices.apis.qwen_cheap'))})
        gpu1000=node(name+'.gpu1000',[summary['seconds'],summary['hourly'],'owners.load'],lambda t,p,l:t*p/3600/l*1000)
        eg1000=node(name+'.eg1000',[dense['downloads'],'prices.egress'],lambda b,p:b*p/1e12*1000)
        def front1000(front,served,days,path=share):
            if served<=0:raise InputGap(path,'zero served calls: front allocation per call undefined')
            return front/(served*days)*1000
        fr1000=node(name+'.fr1000',['owners.front_month',served,'owners.days'],front1000)
        def selling(gpu,eg,front,margin):
            if margin>=1:raise InputGap('owners.margin','target margin must be less than 1')
            return (gpu+eg+front)/(1-margin)
        price=node(name+'.selling',[gpu1000,eg1000,fr1000,'owners.margin'],selling)
        for benchmark in scenario['benchmark_keys']:
            bp='owners.benchmarks.'+benchmark
            break_rows.append({'share':share,'bound':bound,'gpu_1000':gpu1000,'egress_1000':eg1000,'front_1000':fr1000,'margin':'owners.margin','price_1000':price,
                               'api':label(name+'.bench.'+str(benchmark),benchmark),'api_1000':bp,'price_over_api':node(name+'.ratio.'+str(benchmark),[price,bp],lambda p,a,path=bp:ratio(p,a,path))})
    # Table rows are resolved only after construction; share-independent shapes stay intact under a gap.
    g.table('Paper summary (USD/person-month; existing Mac incremental hybrid, owned all-server)',
            {'team':'person','share':'1','bound':'text','server_precision':'format','hybrid_user':'USD/person/month','own_cluster_user':'USD/person/month','api_median_user':'USD/person/month','api_cheapest_user':'USD/person/month','cluster_boxes':'8-GPU node','capacity_day':'call/day','served_day':'call/day','excess_day':'call/day','overflow_median_user':'USD/person/month','overflow_cheapest_user':'USD/person/month','hybrid_median_user':'USD/person/month','hybrid_cheapest_user':'USD/person/month'},rows)
    g.table('Client capacity cap (decode + local prefill + stream occupation)',
            {'share':'1','bound':'text','requested_day':'call/day','served_day':'call/day','excess_day':'call/day','capacity_day':'call/day','sessions':'stream','tok_s_stream':'token/s','quant':'format','prefill_scale':'1'},capacity_rows)
    g.table('Owned residual grid (full new Macs and integer owned prefill boxes)',
            {'team':'person','share':'1','bound':'text','server':'text','server_residual':'1','client_residual':'1','hybrid_user':'USD/person/month','api_median_user':'USD/person/month','api_cheapest_user':'USD/person/month','savings_median':'1','savings_cheapest':'1'},res_rows)
    # First sustained crossover on the supplied finite grid; never extrapolate a "500" target.
    for i,share in enumerate(shares):
        subset=[r for r in rows if r['share']==share]
        def first(*pairs):
            hit=None
            for n,c,a in sorted(pairs,key=lambda row:row[0]):
                hit=(n if hit is None else hit) if c<=a else None
            return 'none on supplied grid' if hit is None else hit
        for api in ('api_median_user','api_cheapest_user'):
            refs=[x for r in subset for x in (r['team'],r['own_cluster_user'],r[api])]
            if scenario.get('integer_equilibrium'):
                def exact(demand,seconds,unit,hours,load,api_month,grid):
                    if not grid:raise InputGap('owners.teams','empty team grid leaves no integer sweep bound')
                    maximum=max(grid);last=0
                    for n in range(1,maximum+1):
                        cost=max(1,math.ceil(n*demand*seconds/(hours*3600*load)))*unit/n
                        if cost>api_month:last=n
                    return last+1 if last<maximum else 'none through '+str(maximum)
                st=share_totals[i]
                value=node('crossover.'+str(i)+'.'+api,[st['requested'],cluster['own_seconds'],st['unit'],'owners.hours','owners.load',st[api],'owners.teams'],exact)
            else:
                value=node('crossover.'+str(i)+'.'+api,refs,lambda *args:first(*[args[j:j+3] for j in range(0,len(args),3)]))
            cross_rows.append({'share':share,'bound':node('crossbound.'+str(i)+api,[share],lambda s:'academic bound' if s==1 else 'decision case'),
                               'api':label('crossapi.'+str(i)+api,api),'first_sustained_team':value})
    g.table('Derived own-cluster equilibrium (every integer through maximum displayed team)' if scenario.get('integer_equilibrium') else 'Derived own-cluster equilibrium (first sustained point on this grid)',{'share':'1','bound':'text','api':'text','first_sustained_team':'person or no crossover'},cross_rows)
    g.table('Break-even selling price (pooled prefill service, excludes client hardware and API overflow)',
            {'share':'1','bound':'text','gpu_1000':'USD/1000call','egress_1000':'USD/1000call','front_1000':'USD/1000call','margin':'1','price_1000':'USD/1000call','api':'text','api_1000':'USD/1000call','price_over_api':'1'},break_rows)
    fit_rows=[]
    for key in scenario['fit_models']:
        model_path='owners.models.'+key
        for quant in ('Q3','Q4'):
            for ssd in ((False,True) if key=='flashnext' else (False,)):
                mode='ngram on SSD' if ssd else 'all weights in RAM'
                w=weight(key,quant,'fit.'+key+quant+str(ssd),ssd)
                for i,memory in enumerate(memories):
                    for j,context in enumerate(contexts):
                        nm='fit.'+key+quant+str(ssd)+'.'+str(i)+'.'+str(j)
                        kv=node(nm+'.kv',[model_path+'.kv',context],lambda k,d:k*d)
                        required=node(nm+'.required',[w,kv,model_path+'.state','owners.client_reserve'],lambda *v:sum(v))
                        sessions=node(nm+'.sessions',[memory,'owners.client_reserve',w,model_path+'.kv',model_path+'.state',context],
                                      lambda m,r,w,k,s,c,p=memory:fit_sessions(m,r,w,k,s,c,p))
                        fit_rows.append({'model':model_path+'.label','quant':label(nm+'.quant',quant),'placement':label(nm+'.mode',mode),'memory':memory,'context':context,
                                         'weights':w,'kv':kv,'state':model_path+'.state','reserve':'owners.client_reserve','required':required,'sessions':sessions,
                                         'ssd_latency':node(nm+'.ssd_latency',['owners.ssd_token_latency'],lambda t:t) if ssd else label(nm+'.ssd_latency',0),
                                         'parameters':model_path+'.parameters','active_parameters':model_path+'.active_parameters'})
    g.table('Client fit (decimal bytes; non-fit is an alarm, not zero usable sessions)',
            {'model':'text','quant':'format','placement':'text','memory':'B','context':'token','weights':'B','kv':'B','state':'B','reserve':'B','required':'B','sessions':'session','ssd_latency':'s/token','parameters':'parameter','active_parameters':'parameter'},fit_rows)
    small=[];buy=[]
    option_keys=scenario['option_keys']
    for mk in scenario['small_models']:
        m=model_nodes(mk)
        for ok in option_keys:
            o=option_nodes(m,ok)
            for i,team in enumerate(small_teams):
                nm='small.'+mk+'.'+ok+'.'+str(i)
                # Small-team demand is the first production share (20% by default).
                request,served,excess=volume(nm,m,shares[0])
                units=counts(nm+'.units',team,served,o['seconds'],'owners.hours')
                rent=node(nm+'.rent',[units,o['hourly'],'owners.hours','owners.days'],lambda n,p,h,d:n*p*h*d)
                ownunit=unit_month(nm+'.unit',o,'owners.residual')
                own=node(nm+'.own',[units,ownunit],lambda n,c:n*c)
                loc=g.resolve(o['prefix']+'.location')
                cost=own if ok in scenario.get('colocated_keys',[]) or not loc.alarms and loc.value=='office' else node(nm+'.rent_checked',[rent,o['prefix']+'.location'],lambda r,loc:r)
                monthly_calls=node(nm+'.calls',[team,served,'owners.days'],lambda n,s,d:n*s*d)
                def session_cost(cost,calls,chunk):
                    if calls<=0:raise InputGap('owners.shares','zero served calls: session cost undefined')
                    return cost/calls*chunk
                egress=node(nm+'.egress',[monthly_calls,m['downloads'],'prices.egress'],lambda c,b,p:c*b/1e12*p)
                mac=client_month(nm+'.mac',m,'owners.residual',full)
                total=node(nm+'.total',[cost,egress,mac,team,'owners.front_month'],lambda gpu,eg,mac,n,front:gpu+eg+n*(mac+front))
                small.append({'team':team,'share':shares[0],'model':m['label'],'option':o['label'],'precision':precision_label,'weight_bytes':m['sw'],'units':units,
                              'sessions_mac':m['fit'],'active_streams':m['sessions'],'tok_s_stream':m['rate'],'served_day':served,'excess_day':excess,
                              'cost_session':node(nm+'.session',[total,monthly_calls,'workload.chunk_calls'],session_cost),
                              'api_session':node(nm+'.api',[m['api'],'workload.chunk_calls'],lambda c,k:c*k),
                              'own_cluster_session':node(nm+'.all_server',[team,request,o['own_seconds'],'owners.hours','owners.load',ownunit,'owners.days','workload.chunk_calls'],
                                                       lambda n,d,s,h,l,u,days,k:max(1,math.ceil(n*d*s/(h*3600*l)))*u/(n*d*days)*k)})
    # Buy/rent sensitivity uses the Qwen model, all team sizes and both windows.
    for ok in option_keys:
        o=option_nodes(dense,ok)
        for i,team in enumerate(teams):
            for si,share in enumerate(shares):
                req,served,excess=volume('buyvolume.'+ok+'.'+str(i)+'.'+str(si),dense,share)
                for j,hours in enumerate(windows):
                    nm='buy.'+ok+'.'+str(i)+'.'+str(si)+'.'+str(j)
                    # Capacity follows the client work window, not a global server window;
                    # global teams reuse the server, each Mac retains its owners.hours day.
                    units=counts(nm+'.units',team,served,o['seconds'],hours)
                    rental=node(nm+'.rent',[units,o['hourly'],hours,'owners.days'],lambda n,p,h,d:n*p*h*d)
                    op=node(nm+'.op',[units,o['opex']],lambda n,c:n*c)
                    for k,residual in enumerate(residuals):
                        rn=nm+'.res.'+str(k)
                        net=node(rn+'.net',[units,o['capex'],residual],lambda n,p,r:n*p*(1-r))
                        months=node(rn+'.months',[net,rental,op],lambda c,r,o,p=o['hourly']:crossover(c,r,o,p))
                        buy.append({'team':team,'share':share,'bound':node(rn+'.bound',[share],lambda s:'academic bound' if s==1 else 'decision case'),
                                    'option':o['label'],'hours_day':hours,'residual':residual,'units':units,'net_capex':net,'rent_month':rental,'own_opex_month':op,
                                    'months_to_buy':months,'buy_by_horizon':node(rn+'.beats',[net,rental,op,'owners.years'],lambda cap,r,op,y:cap+12*y*op<12*y*r)})
    g.table('Small teams (dedicated warm prefill rental or office ownership; full Studio cost)',
            {'team':'person','share':'1','model':'text','option':'text','precision':'format','weight_bytes':'B','units':'unit','sessions_mac':'resident session','active_streams':'stream','tok_s_stream':'token/s',
             'served_day':'call/day','excess_day':'call/day','cost_session':'USD/session','api_session':'USD/session','own_cluster_session':'USD/session'},small)
    g.table('Buy versus rent (dedicated integer warm pool; fixed daily demand)',
            {'team':'person','share':'1','bound':'text','option':'text','hours_day':'h/day','residual':'1','units':'unit','net_capex':'USD','rent_month':'USD/month','own_opex_month':'USD/month',
             'months_to_buy':'month','buy_by_horizon':'bool'},buy)
    raw_eff=node('raw_eff',[mean_anchor,'owners.models.qwen27.weights_q4','owners.models.qwen27.kv','owners.models.qwen27.state','owners.anchor_depth','owners.anchor_bandwidth','analysis.decode_state_passes'],lambda r,w,k,s,d,b,passes:r*(w+k*d+passes*s)/b)
    g.table('Measured decode anchor (efficiency coordinate versus GGUF-byte roofline)',
            {'depth':'token','min':'token/s','mean':'token/s','max':'token/s','coordinate':'1','raw_byte_efficiency':'1'},
            [{'depth':'owners.anchor_depth','min':node('anchor.min',[anchor],lambda r:r[0]),'mean':mean_anchor,'max':node('anchor.max',[anchor],lambda r:r[2]),
              'coordinate':'owners.anchor_efficiency','raw_byte_efficiency':raw_eff}])
    if scenario.get('operations'):
        from .operations import tables
        tables(g,scenario,model_nodes,option_nodes,weight,fit_sessions)
    return g.result(scenario['name'],[
        'All figures use the supplied offline snapshots; no live tariff verification. Currency USD unless stated. API comparisons charge the same open calls; remaining closed-model calls are a common excluded cost.',
        'Summary hybrid buys fractional capacity from a shared rental service at target load; it does not reserve a minimum GPU per team. Dedicated warm rentals and full new Macs are shown separately. Client capacity overflow goes to the same-model cheapest API.',
        'Q4/Q6/Q8/FP8 weights use INT8/FP8 tensor throughput at the stated MFU. NVFP4 requires Blackwell FP4 and is engine-dependent. BF16 overrides are academic only. No quality or state-interchange equivalence is proven.',
        'Multi-GPU options assume balanced model sharding with explicit shard_efficiency; topology, kernel and tensor-parallel communication are not runtime-qualified. H200 pair is not two independent replicas.',
        ('Paper all-server demand prefills only new input; generated output is charged once through decode. Dense models reserve a separate weights/workspace copy per GPU. Hybrid still shadows output.' if scenario.get('correct_all_server_prefill') else 'Historical r3 all-server demand includes redundant output shadow-prefill; retained as a reviewed reference, not the corrected paper estimate.'),
        'Own-cluster demand sums prefill, batched decode and resident-state occupation with no overlap credit. owners-paper checks every integer team through the largest displayed team; the r3 reference retains its sparse-grid definition.',
        'Client fit reserves OS/apps before allocating complete KV+recurrent-state sessions. Flash-Next SSD placement removes the 51B n-gram table from RAM and reports an explicit unmeasured lookup latency; it is not a throughput qualification.',
        'Owner 30-37% decode efficiency is a calibrated coordinate. Using actual GGUF bytes yields a different raw bandwidth fraction, shown explicitly beside the native measured 7.48-8.82 tok/s anchor.',
        'Client parallelism is capped by memory at the largest sampled context. Prefill uses the measured M3 curve with FLOP scaling for GLM; MoE active-parameter traffic is an estimate. All calls remain in the API denominator; none are silently discarded.',
        'Buy crossover = net capex/(monthly rental minus ownership operating cost); assumes stationary tariff, occupancy and horizon residual without discounting. A nonpositive saving raises an alarm, not an infinite crossover.',
        'Fit failures in the requested laptop/model grid are expected alarms. The strict CLI intentionally returns 1 for the full owners-economics grid.'])
