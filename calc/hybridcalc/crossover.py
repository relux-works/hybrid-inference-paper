"""One-assumption attribution of calc5 versus the reviewed r3, independent of legacy printing."""
import math
from .analysis_graph import FLOP_FIELDS,calls_graph
from .inputs import InputError,InputGap
from .metrics import Graph,nonempty
from .performance import flop

FIELDS=('calls_per_session','depth','delta','output','tool','output_context','tool_context','prefill','shadow','previous_output')
UNIT_FIELDS=('gpus','compute','bandwidth','kv_free','capex','opex','batch','stream_rate')
CONFIG=('server_moments','api_moments','server_calls','api_calls','weight','kv','state','resid_state','shadow','hours','peak','grid','fleet','geometry','tariff')


def moments(calls,model,chunk):
    rows=nonempty(calls);n=len(rows)
    functions={'depth':lambda d,x,o,t:d,'delta':lambda d,x,o,t:x,'output':lambda d,x,o,t:o,'tool':lambda d,x,o,t:t,
               'output_context':lambda d,x,o,t:o*(d+x),'tool_context':lambda d,x,o,t:t*(d+x),
               'prefill':lambda d,x,o,t:x*flop(model,d),'shadow':lambda d,x,o,t:o*flop(model,d)}
    result={key:sum(fn(*row) for row in rows)/n for key,fn in functions.items()}
    result['calls_per_session']=chunk
    result['previous_output']=sum(rows[i-1][2] for i in range(n) if i%chunk)/n
    return result


def unit_seconds(m,u,weight,kv,state,resid_state,shadow,geometry,memory,workspace,passes):
    pre=(m['prefill']+shadow*m['shadow'])/(u['compute']*u['gpus'])
    decode=(m['output']*(weight/u['batch']+passes*state)+kv*m['output_context'])/(u['bandwidth']*u['gpus'])
    free=u['kv_free']*u['gpus'] if geometry=='replicas' else (memory-weight-workspace)*u['gpus'] if geometry=='replicas_quantized' else memory*u['gpus']-weight-workspace
    if free<=0:raise InputGap('owners.workspace','no free HBM for resident sessions')
    resident=(kv*(m['output_context']/u['stream_rate']+m['tool_context'])+
              resid_state*state*(m['output']/u['stream_rate']+m['tool']))/free
    return pre+decode+resident


def fleet_function(times,monthly,server_calls,hours,peak,fleet,office_max,mixed_max):
    if fleet not in ('rule_a','b300'):raise InputGap('bridge.base.fleet','unknown fleet rule '+str(fleet))
    if mixed_max<office_max:raise InputGap('bridge.mixed_max','mixed-fleet boundary is below office-only boundary')
    def own(n,share):
        keys=('b300',) if fleet=='b300' else (('rtx1','rtx4') if n<=office_max else ('rtx1','rtx4','rtx8','b300') if n<=mixed_max else ('rtx8','b300'))
        return min(max(1,math.ceil(n*server_calls*share*times[k]/(hours*3600)*peak))*monthly[k]/n for k in keys)
    return own


def crossovers(own,api_month,grid,shares):
    grid=sorted(set(grid))
    if not grid:raise InputGap('bridge.legacy_grid','empty team grid')
    if len(shares)!=3:raise InputGap('owners.shares','bridge needs three comparison shares, matching its three labelled columns')
    result={}
    for key,share in zip(('s20','s50','s100'),shares):
        hit=None
        for n in grid:hit=(n if hit is None else hit) if own(n,share)<=api_month*share else None
        result[key]=hit if hit is not None else 'none through '+str(grid[-1])
    return result


def api_month(m,tariff,calls,days):
    return (m['depth']*tariff['cache_read']+(m['delta']+m['previous_output'])*tariff['cache_write']+m['output']*tariff['output'])/1e6*calls*days


def calculate(scenario,inputs):
    g=Graph(inputs);add=g.add
    calls,valid=calls_graph(g)
    fm=g.bundle('bridge.model','models.qwen27',FLOP_FIELDS)
    add('bridge.measured',[valid,fm,'workload.chunk_calls'],moments)
    for name in ('server','api'):g.bundle('bridge.legacy_'+name,'bridge.moments.'+name,FIELDS)
    for name in ('legacy_server','legacy_api'):
        add('bridge.'+name+'_calls',['@bridge.'+name,'bridge.sessions_day'],lambda m,s:m['calls_per_session']*s)
    add('bridge.q4_weight',['owners.models.qwen27.parameters','owners.formats.Q4'],lambda p,b:p*b)
    add('bridge.r3_peak',['owners.load'],lambda load:1/load)
    g.bundle('bridge.legacy_tariff','bridge.tariff',('cache_read','cache_write','output'))
    g.bundle('bridge.current_tariff','prices.apis.qwen_median',('cache_read','cache_write','output'))
    for name,path in [('legacy_grid','bridge.legacy_grid'),('r3_grid','owners.teams')]:
        paths=g.positions(path);add('bridge.'+name,paths,lambda *values:list(values))
    def integers(lo,hi):
        if hi<lo:raise InputGap('bridge.max_team','maximum team is below minimum team')
        return list(range(lo,hi+1))
    add('bridge.integer_grid',['bridge.min_team','bridge.max_team'],integers)
    def dereference(name,path,policy=False):
        outcome=g.resolve(path)
        if outcome.alarms or policy:return add(name,[path],lambda value:value)
        target=outcome.value
        if not isinstance(target,str) or target.startswith('@') and target not in g.nodes:
            def invalid(value):raise InputGap(path,'unknown input/metric reference '+str(value))
            return add(name,[path],invalid)
        return add(name,[path,target],lambda ref,value:value)
    config={k:dereference('bridge.base.'+k,'bridge.base.'+k,k in ('fleet','geometry')) for k in CONFIG}
    try:steps=inputs.locate('bridge.steps')
    except InputError:steps=None
    columns={'step':'one changed assumption','s20':'person, 20%','s50':'person, 50%','s100':'person, academic 100%',
             'own_500_s100':'USD/person-month, academic100','api_s100':'USD/person-month, academic100','unit_s_call':'B300-node s/call'}
    if not isinstance(steps,list) or not steps:
        def invalid(value):raise InputGap('bridge.steps','expected nonempty ordered steps')
        alarm=add('bridge.bad_steps',['bridge.steps'],invalid)
        g.table('calc5 to r3 step by step',columns,[{key:alarm for key in columns}]);return g.result(scenario['name'])
    rows=[]
    for i,step in enumerate(steps):
        path='bridge.steps.'+str(i)
        if not isinstance(step,dict) or not isinstance(step.get('changes'),dict):
            def invalid(value,p=path):raise InputGap(p,'step requires label and changes record')
            alarm=add('bridge.bad_step.'+str(i),[path],invalid);rows.append({key:alarm for key in columns});continue
        unknown=[key for key in step['changes'] if key not in config]
        if unknown:
            bad_path=path+'.changes.'+unknown[0]
            def invalid(value,p=bad_path):raise InputGap(p,'unknown assumption; later states cannot be reconstructed')
            alarm=add('bridge.unknown_step.'+str(i),[bad_path],invalid)
            rows.append({key:(path+'.label' if key=='step' else alarm) for key in columns})
            config={key:alarm for key in CONFIG}
            continue
        for key in step['changes']:
            config[key]=dereference('bridge.step.'+str(i)+'.'+key,path+'.changes.'+key,key in ('fleet','geometry'))
        fleet_outcome=g.resolve(config['fleet']);geometry=g.resolve(config['geometry'])
        keys=('b300',) if not fleet_outcome.alarms and fleet_outcome.value=='b300' else ('b300','rtx8','rtx4','rtx1')
        times=[];costs=[]
        replicas=not geometry.alarms and geometry.value=='replicas'
        for key in keys:
            name='bridge.row.'+str(i)+'.'+key;p='bridge.units.'+key
            hw_fields=('gpus','compute','bandwidth','batch','stream_rate')+(('kv_free',) if replicas else ())
            hw=g.bundle(name+'.hardware',p,hw_fields)
            refs=[config['server_moments'],hw,config['weight'],config['kv'],config['state'],config['resid_state'],config['shadow'],config['geometry']]
            if not replicas:refs+=['owners.options.b300_node.memory','owners.workspace']
            refs+=['analysis.decode_state_passes']
            def seconds(*v,replicas=replicas):
                if v[7] not in ('replicas','pooled','replicas_quantized'):
                    raise InputGap('bridge.base.geometry','unknown HBM geometry '+str(v[7]))
                return unit_seconds(*v[:8],None,None,v[8]) if replicas else unit_seconds(*v)
            times.append(add(name+'.seconds',refs,seconds))
            costs.append(add(name+'.month',[p+'.capex',p+'.opex','owners.years','owners.residual'],lambda cap,op,y,r:cap*(1-r)/(y*12)+op))
        time_map=add('bridge.times.'+str(i),times,lambda *v,keys=keys:dict(zip(keys,v)))
        cost_map=add('bridge.costs.'+str(i),costs,lambda *v,keys=keys:dict(zip(keys,v)))
        own=add('bridge.own.'+str(i),[time_map,cost_map,config['server_calls'],config['hours'],config['peak'],config['fleet'],'bridge.office_max','bridge.mixed_max'],fleet_function)
        api=add('bridge.api.'+str(i),[config['api_moments'],config['tariff'],config['api_calls'],'owners.days'],api_month)
        result=add('bridge.crossovers.'+str(i),[own,api,config['grid'],'owners.shares'],crossovers)
        row={'step':path+'.label','own_500_s100':add('bridge.probe.'+str(i),[own,'bridge.probe_team','owners.shares.2'],lambda f,n,s:f(n,s)),
             'api_s100':api,'unit_s_call':times[0]}
        for key in ('s20','s50','s100'):
            row[key]=add('bridge.row.'+str(i)+'.'+key,[result],lambda data,k=key:data[k])
        rows.append(row)
    g.table('calc5 to r3 step by step',columns,rows)
    return g.result(scenario['name'],[
        'Ordered one-assumption bridge; no claim that the order-independent effects add linearly across integer fleet thresholds.',
        'Legacy already uses FP8, not BF16. Mac purchase basis and unchanged median tariff have no effect on own-cluster/API crossover.',
        'Both finite grids and integer sweeps are bounded above by the supplied maximum; a sparse-grid crossover is not a guarantee at omitted team sizes.',
        'Frozen calc5 outputs remain unchanged. The paper correction removes output shadow-prefill only from all-server demand; hybrid prefill still shadows all generated tokens.'])
