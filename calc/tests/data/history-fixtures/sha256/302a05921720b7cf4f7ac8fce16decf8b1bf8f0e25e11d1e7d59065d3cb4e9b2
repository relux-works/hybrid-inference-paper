"""Break-even token prices on the unchanged Run14 routing and storage budgets."""
import copy
import json
import math

from .inputs import InputGap


def monthly_cost(price, million_tokens, fixed):
    if any(not math.isfinite(x) or x < 0 for x in (price,million_tokens,fixed)):
        raise InputGap('r14.prefill_price','finite nonnegative price, token volume and fixed cost required')
    return fixed+price*million_tokens


def price_threshold(target, million_tokens, components, storage_gb_month):
    """Price is only prefill compute; migration and every other budget stay fixed."""
    if not math.isfinite(target) or target < 0 or not math.isfinite(storage_gb_month) or storage_gb_month <= 0:
        raise InputGap('r14.prefill_price','nonnegative API target and positive retained GB-month required')
    if 'storage' not in components or any(not math.isfinite(v) or v<0 for v in components.values()):
        raise InputGap('r14.prefill_price','storage component and finite nonnegative component prices required')
    fixed=sum(components.values())
    monthly_cost(0,million_tokens,fixed)
    if million_tokens <= 0:
        raise InputGap('r14.prefill_price','no client-served prefilled tokens; token-price threshold undefined')
    nonstorage=fixed-components['storage']
    needed=(target-nonstorage)/storage_gb_month
    if fixed <= target:
        threshold=(target-fixed)/million_tokens
        return dict(price=threshold,verdict='break-even',required_storage_price=needed,
                    blocker='none at zero prefill price',zero_price_cost=fixed)
    largest=max((value,key) for key,value in components.items() if key!='storage')[1]
    blocker=('storage at its current price' if nonstorage <= target else
             'non-storage floor exceeds API; largest component: '+largest)
    return dict(price='no break-even',verdict='no break-even',
                required_storage_price=needed if needed>=0 else 'no nonnegative storage price',
                blocker=blocker,zero_price_cost=fixed)


def active_storage_price(effective,retention,active_fraction,inactive_nvme):
    """RAM-price ceiling when only RAM changes and inactive NVMe stays priced."""
    if isinstance(effective,str):return 'no nonnegative active-tier storage price'
    if retention=='ram_month':return effective
    if not 0<active_fraction<=1:
        raise InputGap('r14.prefill_price','positive active fraction at most one required')
    price=(effective-(1-active_fraction)*inactive_nvme)/active_fraction
    return price if price>=0 else 'no nonnegative active-tier price at fixed inactive NVMe'


def rental_cost_per_mtoken(seconds_token,hourly,load):
    if (not math.isfinite(seconds_token) or seconds_token<=0 or not math.isfinite(hourly) or hourly<0 or
            not math.isfinite(load) or not 0<load<=1):
        raise InputGap('r14.prefill_price','positive measured seconds/token and load; nonnegative rental price required')
    return seconds_token*1e6*hourly/3600/load


def require_option(options,key):
    if key not in options:
        raise InputGap('measurements.prefill_price','missing measured server option: '+key)
    return options[key]


def client_budget(inputs,key):
    """Reuse declared whole-device budgets; never invent free missing power."""
    if key in ('strix','spark'):
        # These tab:clients entries previously carried capacity only. The
        # existing GLM family budget declares the same physical nodes' price
        # and power; retain its conservative per-node allocation, including
        # the Strix NIC/cabling slice, rather than claiming a new measurement.
        p='hardware.glm_family.'+key+'2';nodes=inputs.get(p+'.nodes')
        return dict(power=inputs.get(p+'.power')/nodes,purchase=inputs.get(p+'.price')/nodes,credit=0,
                    basis='estimate: existing '+key+'2 whole-device budget divided by nodes; Strix includes NIC allocation; no laptop credit')
    p='hardware.clients.'+key
    return dict(power=inputs.get(p+'.power'),purchase=inputs.get(p+'.purchase_price'),credit=inputs.get(p+'.premium_credit'),
                basis='existing single-client power and purchase/premium-credit budget')


def prefilled_token_mean(calls):
    if not calls or any(not math.isfinite(n) or not math.isfinite(o) or n<0 or o<0 for d,n,o,t in calls):
        raise InputGap('r14.prefill_price','nonempty calls with nonnegative delta/output required')
    # All client-served delta and generated tokens reach the server once;
    # the already-prefilled prefix is storage/reload, not new prefill work.
    return sum(n+o for d,n,o,t in calls)/len(calls)


def server_options(c):
    from .measurements_r13 import package,matching,cold_fit
    from .server_prefill import fit
    payload=package('phase_a')[1]
    a,b,_=fit(matching(payload,'-q27b-q4km-'))
    options=dict(llamacpp_pro6000=dict(a=a,b=b,hourly=c.inputs.get('owners.options.rtx6000.hourly'),
                 label='measured llama.cpp PRO6000 run13 base; bulk fit',server_only=0,max_depth=249000))
    docs=json.loads(next(v for n,v in payload.items() if n.endswith('/vllm.json')))
    document=next((d for d in docs if d['name']=='fp8-default' and d.get('A')),None)
    if document is None:raise InputGap('measurements.prefill_price','missing measured server option: vllm_pro6000')
    a,b=cold_fit(document)
    options['vllm_pro6000']=dict(a=a,b=b,hourly=c.inputs.get('owners.options.rtx6000.hourly'),
        label='measured vLLM FP8 PRO6000; server-only; cold marginal fit',server_only=1,max_depth=max(r['length'] for r in document['A']))
    for key,name in (('vllm_b300_auto','fp8-default'),('vllm_b300_fp8kv','fp8-kv')):
        document=next((d for d in c.b300.vllm if d['name']==name and d.get('A')),None)
        if document is None:raise InputGap('measurements.prefill_price','missing measured server option: '+key)
        a,b=cold_fit(document)
        options[key]=dict(a=a,b=b,hourly=c.inputs.get('owners.options.b300.hourly'),
            label='measured vLLM FP8 B300 '+name+'; server-only; cold marginal fit',server_only=1,max_depth=max(r['length'] for r in document['A']))
    return options


def rows(c):
    from .engine import load
    from .paper_tables import Context,overflow_cost
    options=server_options(c)
    # Prices are conditional on today's routing and capacities. They do not
    # optimize routing again when a hypothetical provider changes its tariff.
    _,policy_inputs=load('paper-tables-conservative-r14')
    cautious_inputs=copy.deepcopy(c.inputs)
    for key in ('catch_up','retention'):
        cautious_inputs.data['hosting'][key]=copy.deepcopy(policy_inputs.locate('hosting.'+key))
    cautious_inputs.files.update(policy_inputs.files)
    cautious=Context(c.scenario,cautious_inputs)
    result=[]
    for policy,cc in (('default',c),('cautious',cautious)):
        g=cc.g;i=cc.inputs;m=cc.model('qwen27');all_calls=g.resolve(cc.valid).value
        days=i.get('owners.days');hours=i.get('paper_tables.hours');load_=i.get('owners.load')
        retention=i.get('hosting.retention');active=hours*days/i.get('economics.hours_month')
        inactive_nvme=i.get('hosting.tiers.NVMe.price')
        tariff={key:g.resolve(m['api'][key][1]).value for key in ('qwen_cheap','qwen_median')}
        for client in c.scenario['capacity_clients']:
            cl=cc.client(client,'hardware.links.wan.bandwidth','prefill-price');p='hardware.clients.'+client
            budget=client_budget(i,client)
            calls=g.resolve(cl['matched']).value;indices=g.resolve(cl['indices']).value
            capacity=g.resolve(cl['capacity']).value;fit_share=len(calls)/len(all_calls)
            token_mean=prefilled_token_mean(calls)
            tokens=token_mean*len(calls)
            rates={};modelled={}
            for key in ('llamacpp_pro6000','vllm_pro6000','vllm_b300_auto','vllm_b300_fp8kv'):
                option=require_option(options,key)
                seconds_token=sum((n+o)*(option['a']+option['b']*d) for d,n,o,t in calls)/tokens
                rates[key]=rental_cost_per_mtoken(seconds_token,option['hourly'],load_)
                modelled[key]=sum(n+o for d,n,o,t in calls if d>option['max_depth'])/tokens
            gb_month=g.resolve(cl['hosting']['bytes']).value/1e9*i.get('hosting.sessions_per_person')*i.get('hosting.month_fraction')
            for share_key in c.scenario['share_keys']:
                share=i.get('paper_tables.shares.'+share_key);requested=i.get('owners.calls_day')*share
                served=min(requested*fit_share,capacity);million=served*days*token_mean/1e6
                storage=g.resolve(cl['hosting']['storage']).value if served else 0
                download=g.resolve(cl['downloads']).value
                transfer=served*days*download/1e12*i.get('prices.egress')
                energy=budget['power']*hours*days*i.get('prices.energy_client')
                migration_ref=cc.hosting.daily('prefill-price.'+client+'.'+share_key,cl['hosting'],cc.label('prefill-price.'+client+'.'+share_key+'.served',served))
                migration=g.resolve(migration_ref).value/i.get(cl['server']['prefix']+'.gpus')*i.get(cl['server']['hourly'])/3600/load_*days
                for basis in ('owned','premium'):
                    device=0 if basis=='owned' else max(0,budget['purchase']-budget['credit'])*(1-i.get('economics.client_residual'))/(12*i.get('owners.years'))
                    for target,label in (('qwen_cheap','cheapest API'),('qwen_median','median API')):
                        api=requested*days*sum(tariff[target])/len(all_calls)
                        overflow=overflow_cost(requested,served,indices,tariff[target],days)
                        components=dict(storage=storage,transfer=transfer,client_power=energy,client_device=device,
                                        service_front=i.get('owners.front_month'),migration=migration,overflow_api=overflow)
                        solved=price_threshold(api,million,components,gb_month)
                        row=dict(client=i.locate(p+'.label'),client_budget_basis=budget['basis'],storage_policy=policy,share=share,basis=basis,target=label,
                            requested_calls_day=requested,served_calls_day=served,fit_share=fit_share,prefilled_mtokens_month=million,
                            api_month=api,zero_prefill_price_month=solved['zero_price_cost'],price_usd_mtoken=solved['price'],verdict=solved['verdict'],
                            storage_month=storage,storage_gb_month=gb_month,storage_effective_usd_gb_month=storage/gb_month,
                            required_storage_usd_gb_month_at_zero_prefill=solved['required_storage_price'],blocker=solved['blocker'],
                            required_active_storage_usd_gb_month_at_fixed_NVMe=active_storage_price(solved['required_storage_price'],retention,active,inactive_nvme),
                            inactive_storage_floor_usd_gb_month=0 if retention=='ram_month' else (1-active)*inactive_nvme,
                            transfer_month=transfer,client_power_month=energy,client_device_month=device,
                            front_month=components['service_front'],migration_month=migration,overflow_api_month=overflow,
                            rate_basis='n+o weighted marginal measured fits; >deepest measured depth estimated; tariff held at target load; routing fixed')
                        for key in rates:
                            row[key+'_usd_mtoken']=rates[key]
                            row[key+'_hourly']=options[key]['hourly']
                            row[key+'_basis']=options[key]['label']
                            row[key+'_server_only']=options[key]['server_only']
                            row[key+'_modelled_token_share']=modelled[key]
                        result.append(row)
        c.inputs.used.update({k:v for k,v in i.used.items() if not k.startswith('hosting.')})
        c.inputs.files.update(i.files)
    return result


def append_table(result,c):
    from .measurements_r14 import raw_table
    records=rows(c)
    def unit(k,v):
        return ('USD/MTok prefilled' if k.endswith('_usd_mtoken') else
                'USD/GB-month' if 'usd_gb_month' in k else 'text' if isinstance(v,str) else
                'USD/GPU-hour' if k.endswith('_hourly') else
                'GB-month' if k=='storage_gb_month' else 'MTok/month' if k=='prefilled_mtokens_month' else
                'call/day' if k.endswith('_day') else 'USD/person-month' if k.endswith('_month') else '1')
    raw_table(result,'breakeven_prefill_price',records,{k:unit(k,v) for k,v in records[0].items()})
