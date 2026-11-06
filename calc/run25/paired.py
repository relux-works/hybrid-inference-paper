"""Fairness control: optimize the own cluster's retention under the same proxy."""
import math
from . import model, engine


def own_at(fleet,team,demand,nodes):
    cap = model.storage(fleet.server,fleet.depth,team,nodes,fleet.case,fleet.econ.sessions)
    if not cap['feasible']:
        return dict(status='storage_shortfall',person_month='',nodes=nodes,feasible=False)
    active,(first,second) = fleet.overflow(team,nodes)
    rho,queue = model.mg1(team*demand/(fleet.econ.hours*3600),first,second,active)
    if rho>fleet.cfg['max_service_occupancy'] or queue>fleet.cfg['max_mean_queue_s']:
        return dict(status='latency_or_compute_shortfall',person_month='',nodes=nodes,feasible=False)
    # Same accepted own-cluster price boundary: server only; no Mac/front charge.
    unit,_ = fleet.econ.units['pro6000_fp8',fleet.billing]
    inputs=fleet.econ.inputs;extra=fleet.case['extra_capex_usd']
    uplift=extra*(1-inputs.get('owners.residual'))/(12*inputs.get('owners.years'))+extra*inputs.get('owners.office_support')/12
    return dict(status='feasible',person_month=nodes*(unit+uplift)/team,nodes=nodes,feasible=True,
                service_utilization=rho,mean_queue_s=queue,
                basis='same off-GPU restore/write proxy; accepted equivalent depth-batched server work; server-only price boundary')


def own_minimum(fleet,team,demand):
    low=model.storage(fleet.server,fleet.depth,team,1,fleet.case,fleet.econ.sessions)['storage_min_nodes']
    if low is None:
        return dict(status='storage_shortfall',person_month='',nodes='',feasible=False)
    for nodes in range(low,max(low,4*team)+1):
        row=own_at(fleet,team,demand,nodes)
        if row['feasible']:
            return row
    return dict(status='finite_concurrency_shortfall',person_month='',nodes='',feasible=False)


def calculate():
    # One primary proxy suffices to reveal asymmetric-retention effects; the
    # complete tables still compare every sensitivity with the accepted cluster.
    c,prepared,_=engine.setup();cfg=model.config();case=next(x for x in cfg['storage_cases'] if x['name']=='expanded_nvme')
    rows=[]
    for meta,econ,weights in prepared:
        for billing in ('bought',):
            fleet=model.Fleet(econ,weights,case,1,billing,cfg)
            for share in cfg['shares']:
                for load in ('light','medium','heavy'):
                    demand=c.inputs.get('service.profiles.'+load)*share
                    prices={str(n):[] for n in cfg['fleets']};prices['minimum']=[];own=[];samples={}
                    for team in range(1,501):
                        baseline=own_minimum(fleet,team,demand);own.append(engine.number(baseline['person_month']))
                        for policy in prices:
                            result=fleet.minimum(team,demand) if policy=='minimum' else fleet.evaluate(team,demand,int(policy))
                            prices[policy].append(engine.number(result['person_month']))
                            if team==50:samples[policy]=(baseline,result)
                    for policy,series in prices.items():
                        a,b=samples[policy]
                        rows.append(dict(meta,billing=billing,link='office125MB/s RTT1ms' if billing=='bought' else 'engine WAN112.5MB/s RTT400ms estimated',
                            share=share,load=load,fleet_policy=policy,storage_case=case['name'],restore_slowdown=1,
                            proxy_basis=case['basis'],**engine.compare(series,own),
                            own_person_month50=a['person_month'],own_nodes50=a['nodes'],own_status=a['status'],
                            hybrid_person_month50=b['person_month'],hybrid_nodes50=b['nodes'],hybrid_status=b['status'],
                            own_service_utilization50=a.get('service_utilization',''),own_mean_queue_s50=a.get('mean_queue_s',''),
                            hybrid_service_utilization50=b.get('service_utilization',''),hybrid_calendar_utilization50=b.get('calendar_utilization',''),
                            own_over_hybrid50=a['person_month']/b['person_month'] if engine.number(a['person_month']) is not None and engine.number(b['person_month']) is not None else '',
                            comparison_basis='both architectures use the same expanded off-GPU retention/IO/queue proxy; own price server-only, hybrid includes client energy/front as accepted'))
                    print('paired retention',meta['profile'],meta['weighting'],billing,share,load,flush=True)
    return rows
