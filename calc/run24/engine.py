"""Measured API overlays; all hardware costs and routing remain accepted run23."""
import csv,math,re
from pathlib import Path
from . import api,inputs,curves,sentences
from hybridcalc.measurements_r20 import break_even

ROOT=Path(__file__).resolve().parents[2]
FIELDS=('profile','scope_tier','transport','load','share','client','basis','server','billing','full_calls_day','intensity_basis','workload_scope','rate_basis')
WINDOW_BASIS='measured common window '+api.WINDOW+' for attempted endpoints, >=95%; snapshot last1d retained only for never-attempted endpoints, missing availability unverified'


def read(name):
    with (ROOT/'calc/out/run23'/name).open(newline='')as f:return list(csv.DictReader(f))


def identity(row):return tuple(str(row[k])for k in curves.KEYS+('basis',))


def normalized_base(old,rank,model):
    row={k:old[k]for k in FIELDS};row['share']=float(row['share']);row['full_calls_day']=float(row['full_calls_day'])
    row.update(api_model=model,cadence=rank['cadence'],cache_point='measured',api_role=rank['role'],api_provider=rank['provider'],
        api_hit_fraction=rank['cache_hit_fraction'],api_warm_calls=rank['warm_calls'],api_sample_basis=rank['sample_basis'],api_usd_per_1000_calls=rank['usd_per_1000_calls'],cohort_size=rank['cohort_size'],
        complete_admitted_cohort=rank['complete_admitted_cohort'],
        comparison_kind='same-model Qwen comparison'if model==inputs.QWEN else'GLM API price reference versus Qwen hybrid, different models; no quality/performance equivalence claim',
        cache_basis='measured '+str(rank['cache_hit_fraction'])+' cached-input fraction for '+rank['provider'] if rank['provider']else'measured point unavailable; no rate invented',
        api_window_basis=WINDOW_BASIS)
    return row


def cohort(rank):
    return ('PRICEABLE measured cohort '+str(rank['cohort_size'])+'/'+str(rank['admitted_count'])+' admitted endpoints at this cadence; '+
        'not a global cheapest/median over unmeasured endpoints')


def capital_costs():
    result={}
    for row in read('main_economics.csv')+read('small_team_cost.csv'):
        if row['basis']!='new'or row['device_month']in ('','nan'):continue
        value=float(row['device_month']);key=row['client']
        assert key not in result or result[key]==value,'inconsistent client capital control'
        result[key]=value
    assert set(result)=={'m5max64','m5max'}
    return result


def calculate():
    study=inputs.load();prices=api.prices(study);rankings=api.ranked(prices)
    lookup={tuple(r[k]for k in ('model','profile','scope_tier','cadence','cache_point','role')):r for r in rankings}
    table=dict(api_prices=prices,api_rankings=rankings,api_native_study=api.native_prices(study),million_measured=api.million(study),
        measured_crossings=[],measured_multiples=[],shared_measured_crossings=[],api_cadence_subsets=api.cadence_subsets(study))
    samples={identity(r):r for r in read('main_economics.csv')if r['team']=='50'}
    oldcross={identity(r)+(r['reference'],):r for r in read('team_break_even.csv')}
    cached=curves.load();capital_by_client=capital_costs()
    for curve in cached['curves']:
        for basis in ('owned','new'):
            base=dict(curve,basis=basis);sample=samples[identity(base)]
            capital=capital_by_client[curve['client']]if basis=='new'else 0;costs=[p+capital if p is not None else None for p in curve['prices']]
            monthly=float(re.search(r'normalized to ([0-9.]+) calls/person-month',sample['workload_scope'])[1])
            for model in (inputs.QWEN,inputs.GLM):
                for cadence in ('v1_long_pause','amendment_core'):
                    for role in ('cheapest','median'):
                        rank=lookup[model,curve['profile'],curve['scope_tier'],cadence,'measured',role]
                        row=normalized_base(sample,rank,model);price=rank['usd_per_1000_calls'];ref=price*monthly/1000 if price!=''else''
                        if ref=='':
                            result=dict(from_people='',statement='crossing unknown: no qualified measured provider',any_counterexample='',scan_max=500)
                        else:
                            result=break_even(costs,[ref]*500)
                            if isinstance(result['from_people'],dict):result['from_people']=''
                        old=oldcross[identity(base)+('api_'+role+'_owner_981',)]
                        row.update(result,offload_share_min=curve['offload_share_min']if curve['offload_share_min']is not None else'',
                            offload_share_max=curve['offload_share_max']if curve['offload_share_max']is not None else'',
                            historical_owner_981_statement=old['statement'],historical_control_cache_point='owner_981, snapshot1d; a different cache/admission/cohort basis, not a causal cache-only delta',
                            changed_from_historical_control=result['statement']!=old['statement'],api_person_month=ref)
                        claim=row['statement']+' versus measured '+role+' API '+rank['provider']+'; '+cohort(rank)
                        row['sentence'],row['short_sentence']=sentences.make(row,claim)
                        table['measured_crossings'].append(row)
                        mult=normalized_base(sample,rank,model)
                        cost=costs[49]
                        mult.update(team=50,person_month=cost if cost is not None else'',service_utilization=sample['service_utilization'],calendar_utilization=sample['calendar_utilization'],
                            api_person_month=ref,api_over_hybrid=ref/cost if isinstance(ref,(int,float))and cost is not None else'',
                            offload_share=sample['offload_share'],pricing_basis=sample['pricing_basis'],monthly_calls=monthly)
                        if cost is None:claim='capacity alarm: no finite hybrid cost; '+cohort(rank)
                        else:
                            claim='team50 dedicated hybrid ${:.2f}/person-month; service utilization {:.2%}, calendar occupancy {:.2%}; '.format(cost,float(sample['service_utilization']),float(sample['calendar_utilization']))
                            claim+=('API/hybrid {:.3f} measured {}({})'.format(mult['api_over_hybrid'],role,rank['provider'])if mult['api_over_hybrid']!=''else'API/hybrid unknown: no qualified measured provider')+'; '+cohort(rank)
                        mult['sentence'],mult['short_sentence']=sentences.make(mult,claim);table['measured_multiples'].append(mult)
    for old in read('shared_multiples.csv'):
        monthly=float(re.search(r'normalized to ([0-9.]+) calls/person-month',old['workload_scope'])[1]);cost=float(old['person_month'])
        for model in (inputs.QWEN,inputs.GLM):
            for cadence in ('v1_long_pause','amendment_core'):
                for role in ('cheapest','median'):
                    rank=lookup[model,old['profile'],old['scope_tier'],cadence,'measured',role]
                    row=normalized_base(old,rank,model);ref=rank['usd_per_1000_calls'];monthly_api=ref*monthly/1000 if ref!=''else''
                    statement='shared comparison unknown: no qualified measured provider'if monthly_api==''else'shared resident-work limit cheaper for every team size1..500'if cost<monthly_api else'no shared-limit improvement at any team size1..500'
                    row.update(person_month=cost,api_person_month=monthly_api,api_over_hybrid=monthly_api/cost if monthly_api!=''else'',
                        from_people='',shared_from_team=1 if monthly_api!=''and cost<monthly_api else'',statement=statement,scan_max=500,
                        service_utilization=old['service_utilization'],calendar_utilization=old['calendar_utilization'],offload_share=old['offload_share'],
                        shared_basis='continuously shared resident-work/provider allocation; constant per-person price, not a dedicated fleet crossing or a provider offer',
                        full_utilization_person_month=old['full_utilization_person_month'])
                    claim='shared-work hybrid ${:.2f}/person-month; '.format(cost)
                    claim+=('API/hybrid {:.3f} measured {}({}); '.format(row['api_over_hybrid'],role,rank['provider'])if monthly_api!=''else'API/hybrid unknown; ')+statement+'; '+cohort(rank)
                    row['sentence'],row['short_sentence']=sentences.make(row,claim);table['shared_measured_crossings'].append(row)
    return table
