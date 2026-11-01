"""Warm prefill service sizing: engine-derived workload, precision and explicit billing."""
import math
from .analysis_graph import FLOP_FIELDS, calls_graph, mean_flops
from .inputs import InputGap
from .metrics import Graph, nonempty
from .performance import flop, payload, transfer


def download_per_call(calls,model,settings):
    """The declared calc8 admission policy, independent of the subsequently compared GPU SKU."""
    link={key:settings[key] for key in ('bandwidth','goodput','latency')}
    total=0.0
    for depth,delta,output,tool in nonempty(calls):
        local=delta*flop(model,depth)/settings['client_compute']
        remote=delta*flop(model,depth)/settings['decision_server_compute']+transfer(delta,settings['wire_kv'],settings['wire_state'],link)
        if remote<local:
            total+=payload(delta,settings['wire_kv'],settings['wire_state'])
    return total/len(calls)


def cached_api_cost(calls,tariff,chunk):
    """Preserve calc8's cache-write convention and 116-call group boundaries explicitly."""
    total=0.0
    previous=0.0
    for index,(depth,delta,output,tool) in enumerate(nonempty(calls)):
        if index%chunk==0: previous=0.0
        total+=depth*tariff['cache_read']+(delta+previous)*tariff['cache_write']+output*tariff['output']
        previous=output
    return total/len(calls)/1e6


def checked_peak(precision, rate):
    if rate<=0:
        raise InputGap('service.precision','NVFP4 requires engine-dependent Blackwell FP4 support; unavailable for this option')
    return rate


def calculate(scenario,inputs):
    g=Graph(inputs)
    add=g.add
    calls,valid=calls_graph(g)
    precision_label=add('service.precision_label',['service.precision'],lambda p:'BF16 (academic reference)' if p=='BF16' else p)
    model=g.bundle('service.flop_model','models.'+scenario['model'],FLOP_FIELDS)
    flops=add('service.flops_call',[valid,model],mean_flops)
    reference=g.bundle('service.transfer','service.transfer',('wire_kv','wire_state','client_compute','decision_server_compute','bandwidth','goodput','latency'))
    downloads=add('service.bytes_call',[valid,model,reference],download_per_call)
    g.table('Service reference (derived calc8 call mix, not hard-coded FLOPs or bytes)',
            {'calls':'call','prefill_flop':'FLOP/call','download_bytes':'B/call','precision':'server format','mfu':'1'},
            [{'calls':add('service.call_count',[calls],len),'prefill_flop':flops,'download_bytes':downloads,
              'precision':precision_label,'mfu':'service.mfu'}])
    per_api={}
    for key in scenario['api_keys']:
        tariff=g.bundle('service.tariff.'+key,'prices.apis.'+key,('output','cache_read','cache_write'))
        per_api[key]=add('service.api.'+key,[valid,tariff,'workload.chunk_calls'],cached_api_cost)
    precision=g.resolve('service.precision')
    if not precision.alarms:
        peak_field='bf16_peak' if precision.value=='BF16' else ('fp4_peak' if precision.value=='NVFP4' else 'fp8_peak')
        bytes_param='service.bytes_per_parameter.'+precision.value
        weights=add('service.weight_bytes',['service.precision','service.server_parameters',bytes_param],lambda precision,n,bytes:n*bytes)
    else:
        peak_field=None
        weights=add('service.weight_bytes',['service.precision'],lambda p:p)
    profiles=g.mapping('service.profiles')
    user_paths=g.positions('service.users')
    api_rows=[];gpu_rows=[]
    for profile,profile_path in profiles:
        for index,n in enumerate(user_paths):
            cohort='service.'+str(profile)+'.'+str(index)
            node=lambda name,req,fn,p=cohort:add(p+'.'+name,req,fn)
            monthly_calls=node('calls_month',[n,profile_path,'service.active_days'],lambda n,calls,days:n*calls*days)
            tb=node('tb',[monthly_calls,downloads],lambda calls,bytes:calls*bytes/1e12)
            label=g.constant(cohort+'.profile',profile) if profile is not None else profile_path
            for key in scenario['api_keys']:
                cost=node('api_month.'+key,[monthly_calls,per_api[key]],lambda calls,cost:calls*cost)
                api_rows.append({'profile':label,'users':n,'api':'prices.apis.'+key+'.label',
                                 'per_1000_calls':node('api_1000.'+key,[per_api[key]],lambda c:c*1000),
                                 'month':cost,'per_user_month':node('api_user.'+key,[cost,n],lambda cost,n:cost/n)})
            for option in scenario['option_keys']:
                prefix='service.options.'+option
                rownode=lambda name,req,fn,p=cohort,o=option:add(p+'.'+o+'.'+name,req,fn)
                peak=rownode('peak',['service.precision',prefix+'.'+peak_field],checked_peak) if peak_field else rownode('peak',['service.precision'],lambda p:p)
                seconds=rownode('seconds',[flops,peak,'service.mfu'],lambda work,peak,mfu:work/(peak*mfu))
                def memory_check(weights,buffers,memory,p=prefix):
                    if weights+buffers>memory:
                        raise InputGap(p+'.memory','{:.0f} GB server weights plus {:.0f} GB workspace exceed {:.0f} GB; unsupported single-GPU placement (no sharding assumed)'.format(weights/1e9,buffers/1e9,memory/1e9))
                    return True
                feasible=rownode('feasible',[weights,'service.workspace',prefix+'.memory'],memory_check)
                gpu_count=rownode('gpus',[n,profile_path,seconds,'service.active_hours','service.target_load',feasible],
                                  lambda n,calls,seconds,hours,load,fit:max(1,math.ceil(n*calls*seconds/(hours*3600*load))))
                mode=g.resolve(prefix+'.billing')
                if not mode.alarms and mode.value=='window':
                    recurring=rownode('recurring',[gpu_count,prefix+'.hourly_usd','service.active_hours','service.active_days',prefix+'.billing_quantum'],
                                      lambda n,price,hours,days,quantum:n*price*math.ceil(hours*3600/quantum)*quantum/3600*days)
                    setup=rownode('setup',[gpu_count,prefix+'.setup_usd'],lambda n,price:n*price)
                    gpu_month=rownode('gpu_month',[recurring,setup,'service.setup_months'],lambda monthly,setup,months:monthly+setup/months)
                elif not mode.alarms and mode.value=='monthly':
                    recurring=rownode('recurring',[gpu_count,prefix+'.monthly_eur','service.fx_usd_eur'],lambda n,price,fx:n*price*fx)
                    setup=rownode('setup',[gpu_count,prefix+'.setup_eur','service.fx_usd_eur'],lambda n,price,fx:n*price*fx)
                    gpu_month=rownode('gpu_month',[recurring,setup,'service.setup_months'],lambda monthly,setup,months:monthly+setup/months)
                else:
                    def bad_billing(mode,p=prefix):raise InputGap(p+'.billing','unknown billing mode '+str(mode))
                    recurring=rownode('recurring',[prefix+'.billing'],bad_billing)
                    setup=recurring;gpu_month=recurring
                egress=rownode('egress',[tb,'service.egress_price'],lambda tb,price:tb*price)
                total=rownode('total',[gpu_month,egress],lambda gpu,egress:gpu+egress)
                row={'profile':label,'users':n,'calls_day':profile_path,'option':prefix+'.label','precision':precision_label,
                     'gpu_s_call':seconds,'gpus':gpu_count,'tb_month':tb,'recurring_month':recurring,'setup_upfront':setup,'gpu_month':gpu_month,
                     'egress_selected':egress,'total_month':total,'per_user_month':rownode('per_user',[total,n],lambda total,n:total/n),
                     'first_month':rownode('first_month',[recurring,setup,egress],lambda monthly,setup,egress:monthly+setup+egress)}
                for j,key in enumerate(('egress_0','egress_5','egress_50')):
                    row[key]=rownode(key,[tb,'service.egress_prices.'+str(j)],lambda tb,price:tb*price)
                for key in scenario['api_keys']:
                    row[key+'_user_month']=rownode(key+'_user_month',[monthly_calls,per_api[key],n],lambda calls,cost,n:calls*cost/n)
                gpu_rows.append(row)
    g.table('Service API comparison (same calls and historical cache-write convention)',
            {'profile':'text','users':'person','api':'text','per_1000_calls':'USD','month':'USD','per_user_month':'USD'},api_rows)
    columns={'profile':'text','users':'person','calls_day':'call/user/day','option':'text','precision':'format','gpu_s_call':'GPU-s/call',
             'gpus':'GPU','tb_month':'TB/month','recurring_month':'USD/month','setup_upfront':'USD one time','gpu_month':'USD/month incl amortized setup',
             'egress_0':'USD/month','egress_5':'USD/month','egress_50':'USD/month','egress_selected':'USD/month',
             'total_month':'USD/month','per_user_month':'USD/user/month','first_month':'USD cash'}
    columns.update({key+'_user_month':'USD/user/month API' for key in scenario['api_keys']})
    g.table('Service GPU sizing (integer warm pool; full active-window billing)',columns,gpu_rows)
    return g.result(scenario['name'],[
        'All prices are the supplied offline 2026-10-30 research snapshot, excluding tax; no network revalidation.',
        'GPU count = max(1, ceil(users*calls_day*GPU_s_call/(active_hours*3600*target_load))). MFU is separate from load.',
        'Per-second options are a warm pool billed for its entire active window, including integer headroom. No per-inference-only or scale-to-zero discount is assumed.',
        'Monthly reservation is paid for the whole month. Setup is shown upfront, amortized over the explicit setup_months input, and included once in first-month cash.',
        'Weights/workspace admission is a lower bound; KV residency, cold starts, queueing, storage/CPU extras and state conversion correctness are not runtime-qualified here.',
        'Q4/Q6/Q8/FP8 server weights use INT8/FP8 tensor throughput; NVFP4 uses Blackwell FP4 and is engine-dependent. MFU absorbs dequantization overhead. BF16 is an academic reference only; no state/quality equivalence is established.',
        'Generated tokens use output alone; the informational reasoning subset is not added. Explicit fraction=1 recovers the historical calc8 upper bound; 116-call cache-write grouping remains synthetic.'])
