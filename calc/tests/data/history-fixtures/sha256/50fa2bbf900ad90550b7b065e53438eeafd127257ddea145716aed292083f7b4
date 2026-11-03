"""Remote ownership, deeper client memory and a hypothetical drain-safe idle pool."""
import math
from .inputs import InputGap


def schedule(users,calls_day,open_share,seconds,auto,hours,days,calendar,load):
    """Fixed total work: interactive in operator windows, automatic uniformly 24/7."""
    if days!=int(days):
        raise InputGap('owners.days','guaranteed-window schedule needs integer active days')
    if calendar<days*24:
        raise InputGap('economics.hours_month','active days exceed the declared calendar month')
    work=users*calls_day*open_share*days*seconds/3600
    peak=work*((1-auto)/(hours*days)+auto/calendar)
    units=max(1,math.ceil(peak/load))
    return {'work':work,'units':units,'peak':peak,'warm_hours':hours*days if auto==0 else calendar,
            'calendar_utilization':work/(units*calendar),'window_utilization':peak/units}


def idle_windows(auto,hours,days,calendar,drain,job_limit,restore):
    if days!=int(days):
        raise InputGap('owners.days','guaranteed-window schedule needs integer active days')
    if calendar<days*24:
        raise InputGap('economics.hours_month','active days exceed the declared calendar month')
    handback=math.fsum((job_limit,restore))
    if drain<handback and not math.isclose(drain,handback,rel_tol=0,abs_tol=math.ulp(handback)):
        raise InputGap('operations.drain_hours','drain guard is shorter than tenant job plus owner restoration bound; zero-fallback drain cannot be guaranteed')
    if auto>0:
        return {'idle':0.0,'eligible':0.0,'drain':0.0,'windows':0}  # Continuous reserved owner work leaves no guaranteed idle window.
    night=24-hours
    lengths=[night]*(int(days)-1)+[night+calendar-days*24]
    eligible=sum(max(0,length-drain) for length in lengths)
    draining=sum(min(drain,length) for length in lengths if length>drain)
    return {'idle':sum(lengths),'eligible':eligible,'drain':draining,'windows':sum(length>drain for length in lengths)}


def months(net_capex,rent,opex,credit,path):
    saving=rent-opex+credit
    if saving<=0:
        raise InputGap(path,'buying never recovers net capex at these operating costs and rental/pool prices')
    return net_capex/saving


def tables(g,scenario,model_nodes,option_nodes,weight,fit_sessions):
    add=lambda name,refs,fn:g.add('operations.'+name,refs,fn)
    label=lambda name,value:g.constant('operations.'+name,value)
    teams=g.positions('operations.teams');depths=g.positions('operations.depths');memories=g.positions('owners.memories')
    fit_rows=[]
    for key in scenario['fit_models']:
        p='owners.models.'+key
        for quant in ('Q3','Q4'):
            for ssd in ((False,True) if key=='flashnext' else (False,)):
                nm='reach.'+key+'.'+quant+'.'+str(ssd)
                w=weight(key,quant,nm+'.weight',ssd)
                for i,memory in enumerate(memories):
                    base=nm+'.'+str(i)
                    def maximum(m,r,w,k,s,path=memory):
                        if m-r-w<s:
                            raise InputGap(path,'weights + recurrent state + OS/app reserve do not fit even at depth zero')
                        return math.floor((m-r-w-s)/k)
                    reach=add(base+'.max',[memory,'owners.client_reserve',w,p+'.kv',p+'.state'],maximum)
                    limit='operations.context_limits.'+key
                    supported=add(base+'.supported',[reach,limit],min)
                    row={'model':p+'.label','quant':label(base+'.quant',quant),'placement':label(base+'.placement','n-gram on SSD' if ssd else 'all weights in RAM'),
                         'memory':memory,'weights':w,'kv_per_token':p+'.kv','state':p+'.state','reserve':'owners.client_reserve','memory_depth':reach,'supported_depth':supported}
                    for j,depth in enumerate(depths):
                        def fit(m,r,w,k,s,d,limit,path=memory,lp=limit):
                            if d>limit:raise InputGap(lp,'requested depth exceeds declared model envelope')
                            return fit_sessions(m,r,w,k,s,d,path)
                        row['depth_'+str(j)]=depth
                        row['sessions_'+str(j)]=add(base+'.sessions.'+str(j),[memory,'owners.client_reserve',w,p+'.kv',p+'.state',depth,limit],fit)
                    fit_rows.append(row)
    cols={'model':'text','quant':'format','placement':'text','memory':'B','weights':'B','kv_per_token':'B/token','state':'B','reserve':'B','memory_depth':'token, raw memory bound','supported_depth':'token, clipped to declared envelope'}
    for j in range(len(depths)):cols.update({'depth_'+str(j):'token','sessions_'+str(j):'resident session'})
    g.table('Deep client reach and sessions (256k, 500k, 1M)',cols,fit_rows)
    # Office boxes are a large-company option only. Policy failures are visible metrics.
    m=model_nodes('qwen27');rows=[]
    for key in scenario['operations_options']:
        o=option_nodes(m,key);p=o['prefix']
        location=g.resolve(p+'.location')
        for i,team in enumerate(teams):
            for mode,auto in [('operator','operations.reference_share'),('autopilot','operations.autopilot_share')]:
                nm=key+'.'+str(i)+'.'+mode
                def eligible(n,bound,location):
                    if location=='office' and n<=bound:
                        raise InputGap('operations.small_team_max','office boxes are reserved for larger companies; remote teams up to this size use colocation')
                    return True
                admitted=add(nm+'.admitted',[team,'operations.small_team_max',p+'.location'],eligible)
                settings=add(nm+'.schedule',[team,'owners.calls_day','owners.shares.0',o['seconds'],auto,'owners.hours','owners.days','economics.hours_month','owners.load',admitted],
                             lambda *v:schedule(*v[:-1]))
                def part(field):return add(nm+'.'+field,[settings],lambda cfg,k=field:cfg[k])
                units=part('units');work=part('work');util=part('calendar_utilization');winutil=part('window_utilization');warm=part('warm_hours')
                windows=add(nm+'.idle',[auto,'owners.hours','owners.days','economics.hours_month','operations.drain_hours','operations.job_limit_hours','operations.owner_restore_hours'],idle_windows)
                def idle_capacity(auto,hours,days,calendar):
                    if days!=int(days):raise InputGap('owners.days','guaranteed-window schedule needs integer active days')
                    if calendar<days*24:raise InputGap('economics.hours_month','active days exceed the declared calendar month')
                    return calendar-hours*days if auto==0 else 0.0
                idle=add(nm+'.idle_hours',[auto,'owners.hours','owners.days','economics.hours_month'],idle_capacity)
                eligible_hours=add(nm+'.eligible_hours',[windows],lambda w:w['eligible'])
                sold=add(nm+'.sold',[eligible_hours,'operations.pool_fill',units,p+'.gpus'],lambda h,fill,n,k:h*fill*n*k)
                drain_gpu=add(nm+'.drain_gpu',[windows,'operations.pool_fill',units,p+'.gpus'],lambda w,fill,n,k:(w['drain'] if fill>0 else 0)*n*k)
                gpu_used=add(nm+'.owner_gpu_hours',[work,p+'.gpus'],lambda h,n:h*n)
                rent=add(nm+'.rent',[units,warm,o['hourly']],lambda n,h,p:n*h*p)
                # Linear power estimate charges idle baseline plus incremental owner/pool activity.
                energy_price='prices.energy_client' if not location.alarms and location.value=='office' else 'prices.energy_dc'
                ownenergy=add(nm+'.energy',[units,p+'.power','economics.pue',energy_price,'operations.idle_power_fraction','economics.hours_month',work],
                              lambda n,p,pue,price,idle,calendar,work:p*pue*price*(n*calendar*idle+(1-idle)*work))
                opex=add(nm+'.opex',[ownenergy,units,o['colo'],o['support']],lambda energy,n,colo,support:energy+n*(colo+support))
                net=add(nm+'.net',[units,o['capex'],'owners.residual'],lambda n,p,r:n*p*(1-r))
                dep=add(nm+'.depreciation',[net,'owners.years'],lambda net,y:net/(12*y))
                owncost=add(nm+'.owncost',[dep,opex],lambda d,o:d+o)
                revenue=add(nm+'.revenue',[sold,'operations.pool_price'],lambda h,p:h*p)
                poolenergy=add(nm+'.pool_energy',[sold,drain_gpu,p+'.power',p+'.gpus','economics.pue',energy_price,'operations.idle_power_fraction'],
                               lambda sold,drain,p,k,pue,price,idle:(sold+drain)*p/k*pue*price*(1-idle))
                credit=add(nm+'.credit',[revenue,poolenergy],lambda rev,cost:rev-cost)
                effective=add(nm+'.effective',[owncost,credit],lambda cost,credit:cost-credit)
                def perused(cost,h):
                    if h<=0:raise InputGap('owners.shares.0','no owner-used GPU hours; effective cost per used hour undefined')
                    return cost/h
                costh=add(nm+'.costh',[owncost,gpu_used],perused)
                costhpool=add(nm+'.costhpool',[effective,gpu_used],perused)
                buy=add(nm+'.buy',[net,rent,opex],lambda cap,r,op,p=o['hourly']:months(cap,r,op,0,p))
                buypool=add(nm+'.buypool',[net,rent,opex,credit],lambda cap,r,op,c:months(cap,r,op,c,'operations.pool_price'))
                # Mathematical disjointness under the stated bounded-job schedule; not a deployed runtime claim.
                conflicts=add(nm+'.conflicts',[windows,settings],lambda windows,s:0)
                rows.append({'team':team,'option':o['label'],'mode':label(nm+'.mode',mode),'autopilot_share':auto,'units':units,'owner_gpu_hours':gpu_used,
                             'calendar_utilization':util,'peak_window_load':winutil,'warm_hours':warm,'owner_idle_hours_per_unit':idle,'eligible_pool_hours_per_unit':eligible_hours,
                             'sold_pool_gpu_hours':sold,'drain_gpu_hours_bound':drain_gpu,'rent_month':rent,'own_opex_month':opex,'own_month':owncost,
                             'pool_revenue':revenue,'pool_incremental_energy':poolenergy,'pool_net_credit':credit,'own_with_pool_month':effective,
                             'cost_per_owner_gpu_hour':costh,'cost_per_owner_gpu_hour_pool':costhpool,'buy_months':buy,'buy_months_pool':buypool,'owner_conflict_hours':conflicts})
    g.table('Colocation, autopilot and hypothetical idle pool (estimate; pool does not exist)',
            {'team':'person','option':'text','mode':'text','autopilot_share':'1','units':'server unit','owner_gpu_hours':'GPU-h/month',
             'calendar_utilization':'1','peak_window_load':'1','warm_hours':'h/unit/month','owner_idle_hours_per_unit':'h/month',
             'eligible_pool_hours_per_unit':'h/month','sold_pool_gpu_hours':'GPU-h/month','drain_gpu_hours_bound':'GPU-h/month bound',
             'rent_month':'USD/month','own_opex_month':'USD/month','own_month':'USD/month','pool_revenue':'USD/month','pool_incremental_energy':'USD/month',
             'pool_net_credit':'USD/month','own_with_pool_month':'USD/month','cost_per_owner_gpu_hour':'USD/owner-used GPU-h',
             'cost_per_owner_gpu_hour_pool':'USD/owner-used GPU-h','buy_months':'month','buy_months_pool':'month','owner_conflict_hours':'h (analytical schedule)'},rows)
