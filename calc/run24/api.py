"""Endpoint admission and cadence-specific prices on the accepted final study."""
import csv,json,math
from pathlib import Path
from . import inputs
from run22 import api as old_api
from hybridcalc import deep_r21 as deep,server_economics_r20 as tariff

ROOT=Path(__file__).resolve().parents[2]
WINDOW='2026-11-03T14:39:44.389926+00:00 to 2026-11-04T07:22:22.114713+00:00'
CADENCE_TEXT={'v1_long_pause':'v1 multi-depth long pauses, including recorded late gaps; not the core8s/35s cadence',
    'amendment_core':'amendment core short-gap cadence, including labelled resumed cells; not a pure8s/35s TTL result',
    'amendment_long':'separate amendment long-pause substudy; no valid price sample'}


def inventory(study):
    result={}
    for row in old_api.providers():
        result[inputs.QWEN,row['tag']]=dict(row,context_basis='2026-10-29 endpoint snapshot',snapshot_tag=row['tag'])
    for provider in study['doc']['providers']:
        key=inputs.native_key(provider)
        if key not in result:
            assert key[0]in (inputs.QWEN,inputs.GLM),'unmapped model'
            floor=1000000 if key[0]==inputs.GLM else 262144
            # The accepted study selected GLM inventory for declared1M context
            # and declared cache. Do not invent a more precise upper limit.
            result[key]=dict(tag=key[1],provider_name=provider['provider_name'],context_length=floor,
                context_basis='final-study selected inventory certifies declared context>='+str(floor)+' and declared cache; exact limit not retained',
                supports_implicit_caching=True,pricing={},snapshot_tag='')
        # The accepted study inventory independently declares cache support;
        # older GLM snapshot summaries omitted that field, rather than denying it.
        result[key]['supports_implicit_caching']=True
        result[key]['cache_declaration_basis']='accepted final-study selected inventory; context/no-declared-cache candidates were excluded before tests'
    return result


def admission(row,needed,measured_percent=None):
    # Low cache hits and thin samples are price/uncertainty conditions only.
    reasons=old_api.admission(row,needed,measured_percent)
    if row.get('context_basis','').startswith('final-study selected inventory') and needed>row['context_length']:
        reasons=[r for r in reasons if not r.startswith('context_below_')]
    return reasons


def context_verified(row,needed):
    return row['context_length']>=needed


def availability(key,row,study):
    if key in study['availability']:
        return study['availability'][key],'whole test window '+WINDOW+'; all attempts including seeds/timeouts; request-sampled, not continuous uptime','measured_whole_window'
    value=row.get('uptime_last_1d')
    label='2026-10-29 Qwen snapshot last1d retained'if key[0]==inputs.QWEN else'GLM snapshot uptime not retained; old research-note tariffs alone do not qualify a provider'
    return value,label+'; endpoint never attempted; '+('availability missing/unverified'if value is None else'exact snapshot window endpoints unavailable'),'snapshot_unattempted'


def profile_shapes():
    with (ROOT/'calc/out/run23/api_admission.csv').open(newline='')as f:rows=list(csv.DictReader(f))
    result={}
    for row in rows:
        identity=(row['profile'],row['scope_tier'])
        result.setdefault(identity,dict(profile=row['profile'],scope_tier=row['scope_tier'],context_needed=int(row['context_needed']),
            mean_input_tokens=float(row['mean_input_tokens']),mean_output_tokens=float(row['mean_output_tokens']),workload_scope=row['workload_scope']))
    return list(result.values())


def prices(study=None):
    study=inputs.load()if study is None else study;out=[]
    for shape in profile_shapes():
        profile=shape['profile']
        for cadence in ('v1_long_pause','amendment_core'):
            for (model,tag),row in inventory(study).items():
                key=(model,tag,profile,cadence);observation=study['cache'].get(key)
                uptime,basis,source=availability((model,tag),row,study)
                reasons=admission(row,shape['context_needed'],uptime)
                p=study['prices'].get(key,row.get('pricing',{}));complete=all(k in p for k in ('prompt','completion','input_cache_read'))
                for point,hit in (('no_cache',0.),('owner_981',.981),('measured',observation['hit']if observation else None)):
                    cost=tariff.api_cost(dict(pricing=p),(shape['mean_input_tokens'],0,shape['mean_output_tokens']),hit)*1000 if hit is not None and not reasons and complete and context_verified(row,shape['context_needed']) else ''
                    out.append(dict(shape,model=model,provider=tag,provider_name=row.get('provider_name',tag),cadence=cadence,cadence_basis=CADENCE_TEXT[cadence],
                        cache_point=point,cache_hit_fraction=hit if hit is not None else '',admitted=not reasons,reasons='; '.join(reasons)or'no impossibility established',
                        availability_percent=uptime if uptime is not None else '',availability_basis=basis,availability_source=source,
                        context_requirement_verified=context_verified(row,shape['context_needed']),context_limit=row['context_length']if row['snapshot_tag']else'',context_certified_minimum=row['context_length']if not row['snapshot_tag']else'',context_basis=row['context_basis'],cache_declaration_basis=row.get('cache_declaration_basis','retained snapshot declaration fields'),
                        effective_usd_per_1000_calls=cost,study_usd_per_1000=observation['study_usd_per_1000']if observation else '',
                        study_depth_mix=observation['study_depth_mix']if observation else '',warm_calls=observation['warm_calls']if observation else '',
                        sample_basis=observation['sample_basis']if observation else'cache measurement unavailable, including unattempted endpoints; no hit rate invented',
                        continuation_flagged_warm_calls=observation['continuation_flagged_warm_calls']if observation else '',
                        interrupted_cell_warm_calls=observation['interrupted_cell_warm_calls']if observation else '',
                        pricing_basis=('run22 aggregate-token tariff formula on identical paper call-shape means; transfer of cadence token-hit fraction across depth mixes is an assumption; '+
                            ('mean same-cohort live tariffs'if key in study['prices']else'retained Qwen snapshot tariffs where present, no GLM research-note tariff fallback; no same-cadence study tariff')+
                            '; study USD/1000 retained separately: source depth mix,1065 new input/512 output and conservative write-surcharge convention'),
                        cache_basis='no cache, all input billed'if point=='no_cache'else'98.1% owner aggregate allowance, not per-provider cache verification'if point=='owner_981'else'measured final-study aggregate token fraction; zero hits priced, thin points disclosed; no Chutes smoke or seed inference',
                        extension_basis='hybrid model-card YaRN factor4 when needed; API extension method unknown, identical YaRN not established',
                        price_status='excluded'if reasons else'priceable'if cost!=''else'unknown, not excluded for missing cache measurement or tariff'))
    return out


def ranked(rows):
    selected={};groups={}
    for row in rows:
        key=tuple(row[k]for k in ('model','profile','scope_tier','cadence','cache_point'))
        groups.setdefault(key,[]).append(row)
    for key,group in sorted(groups.items()):
        values=sorted([r for r in group if r['admitted']is True and r['effective_usd_per_1000_calls']!=''],key=lambda r:(r['effective_usd_per_1000_calls'],r['provider']))
        complete=sum(r['admitted']is True for r in group)==len(values)
        for role,index in (('cheapest',0),('median',len(values)//2)):
            row=values[index]if values else None
            selected[key+(role,)]=dict(model=key[0],profile=key[1],scope_tier=key[2],cadence=key[3],cache_point=key[4],role=role,
                provider=row['provider']if row else'',usd_per_1000_calls=row['effective_usd_per_1000_calls']if row else'',cache_hit_fraction=row['cache_hit_fraction']if row else'',warm_calls=row['warm_calls']if row else'',sample_basis=row['sample_basis']if row else'no qualified price point',
                cohort_size=len(values),admitted_count=sum(r['admitted']is True for r in group),complete_admitted_cohort=complete,
                ranking_basis='rank among admitted PRICEABLE endpoints at this cadence/point; measured cohort is partial, not the global API minimum; upper-middle provider median as in run22',
                availability_basis='whole-window observed admission for attempted endpoints, snapshot last1d only for never-attempted endpoints; missing availability unverified',
                verdict='qualified price point'if row else'no qualified measured provider'if key[4]=='measured'else'no priceable admitted provider')
    return list(selected.values())


def native_prices(study):
    out=[]
    for record in inputs.read('provider_cache'):
        if record['profile']!='existing_combined':continue
        key=(record['model'],record['tag']);row=inventory(study)[key];up,basis,src=availability(key,row,study)
        reasons=admission(row,262144 if key[0]==inputs.QWEN else 1000000,up)
        out.append(dict(record,cache_hit_fraction=float(record['cached_tokens'])/float(record['input_tokens']),admitted=not reasons,
            reasons='; '.join(reasons)or'no impossibility established',availability_percent=up if up is not None else'',availability_basis=basis,
            price_basis='source study measured depth mix; normalized1065 new input/512 output, conservative cache-write surcharge; not paper-workload means or raw16-token bill'))
    return out


def million(study):
    out=[]
    for model,variants in study['doc']['million_token_comparison'].items():
        for variant,r in variants.items():
            actual=[p for p in study['doc']['providers']if p['provider']in r['priced_providers']]
            assert all(p['whole_window_availability']['rate']>=.95 for p in actual),'under95 provider in pooled1M'
            values=[p['million']['effective_usd_per_1000_measured_depth_mix']for p in actual]
            value=sum(values)/len(values)if values else ''
            assert (not values and r['mean_effective_usd_per_1000']is None)or math.isclose(value,r['mean_effective_usd_per_1000'],rel_tol=0,abs_tol=1e-10)
            out.append(dict(model=model,variant=variant,cadence='pooled_v1_and_amendment_core',cache_point='measured',
                usd_per_1000_calls=value,qualified_providers=len(actual),provider_identities=json.dumps(r['priced_providers'],separators=(',',':')),
                basis='equal provider weights, final-study1M depth mix and1065 new/512 output projection; separate long/probe substudy excluded; API YaRN unknown',
                verdict='qualified pooled mean'if values else'no qualified measured provider; snapshot references remain historical labelled controls'))
    return out


def cadence_subsets(study):
    out=[]
    for provider in study['doc']['providers']:
        model,tag=inputs.native_key(provider)
        for (phase,cohort),cadence in inputs.CADENCES.items():
            value=provider['phases'].get(phase,{}).get(cohort)
            if not value:continue
            for subset,metric in value.get('cadence_subsets',{}).items():
                if metric:
                    out.append(dict(model=model,provider=tag,cadence=cadence,subset=subset,warm_calls=metric['accepted'],
                        cache_hit_fraction=metric['token_hit_rate']if metric['token_hit_rate']is not None else'',
                        study_usd_per_1000=metric['effective_usd_per_1000_measured_depth_mix']if metric['effective_usd_per_1000_measured_depth_mix']is not None else'',
                        basis='final analysis cadence subset; descriptive source depth mix, not a silently substituted primary cache point or a target-TTL proof'))
    return out
