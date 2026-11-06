"""Impossibility-only API admission and separate cache/window scenarios."""
import json

from hybridcalc.inputs import InputGap
from hybridcalc import server_economics_r20 as s
from . import interfaces as i

MODEL = 'qwen/qwen3.8-27b'


def providers():
    return json.loads(s.SNAPSHOT.read_text())['data']['endpoints']


def admission(row, needed, availability):
    # Cache observations never participate in admission.
    reasons = []
    if row.get('context_length',0) < needed:
        reasons.append('context_below_'+str(needed))
    p = row.get('pricing',{})
    if row.get('supports_implicit_caching') is not True and 'input_cache_write' not in p:
        reasons.append('caching_not_declared')
    if availability is not None and availability < 95:
        reasons.append('common_window_availability_below_95')
    return reasons


def baseline(means, profile, needed, scope, cache=None, availability=None, window=None, scenarios=None):
    if sum(means)>needed:
        raise InputGap('run22.api_context','input and generated answer must fit the stated API context')
    cache = {} if cache is None else cache
    availability = {} if availability is None else availability
    result = []; selected = {}
    scenarios = scenarios or ('snapshot_1d','analyst_72h_with_alibaba','analyst_72h_without_alibaba')
    for scenario in scenarios:
        candidates = {name:[] for name in ('no_cache','owner_981','measured')}
        for row in providers():
            tag = row['tag']; key = (MODEL,tag)
            if scenario == 'snapshot_1d':
                uptime = row.get('uptime_last_1d')
                basis = 'OpenRouter2026-10-29 snapshot; last1d window for ALL providers; exact window endpoints not retained; other windows unused'
            elif scenario == 'measured_common_window':
                if window is None:
                    raise InputGap('run22.availability','measured common-window scenario requires CSV window')
                uptime = availability.get(key)
                basis = 'measured common window '+window[0].isoformat()+' to '+window[1].isoformat()+'; absent provider observations unverified, no snapshot backfill'
            elif scenario in ('analyst_72h_with_alibaba','analyst_72h_without_alibaba'):
                uptime = {'phala':86.0,'alibaba':96.0}.get(tag)
                basis = 'owner-supplied analyst72h check2026-11-03; Phala86%, Alibaba96%; exact endpoints and other provider observations missing, unverified; no snapshot backfill'
            else:
                raise InputGap('run22.availability','unknown common-window scenario')
            reasons = admission(row,needed,uptime)
            if scenario == 'analyst_72h_without_alibaba' and tag == 'alibaba':
                reasons.append('explicit_without_Alibaba_sensitivity')
            for point, hit in (('no_cache',0.0),('owner_981',0.981),('measured',cache.get((MODEL,tag,profile)))):
                price_complete='input_cache_read' in row['pricing']
                cost = s.api_cost(row,means,hit) if hit is not None and not reasons and price_complete else None
                item = dict(profile=profile,context_needed=needed,availability_scenario=scenario,provider=tag,
                    admitted=not reasons,reasons='; '.join(reasons) or 'no impossibility established',
                    pricing_status='complete' if price_complete else 'tariff missing; admitted provider unpriceable, not excluded',
                    availability_percent=uptime if uptime is not None else '',availability_basis=basis,
                    cache_point=point,cache_hit_fraction=hit if hit is not None else '',
                    cache_basis='provider measurement pending; no invented rate' if hit is None else 'no-cache bound' if point=='no_cache' else 'owner98.1% aggregate allowance, not provider verification' if point=='owner_981' else 'measured repeated-series cached input token fraction; low hit rate priced, never excluded',
                    effective_usd_per_1000_calls=cost*1000 if cost is not None else '',
                    mean_input_tokens=means[0]+means[1],mean_output_tokens=means[2],
                    prompt_usd_million=float(row['pricing']['prompt'])*1e6,output_usd_million=float(row['pricing']['completion'])*1e6,
                    cache_read_usd_million=float(row['pricing']['input_cache_read'])*1e6 if 'input_cache_read' in row['pricing'] else '',
                    miss_usd_million=float(row['pricing'].get('input_cache_write',row['pricing']['prompt']))*1e6,
                    role='excluded' if reasons else 'pending' if hit is None else 'admitted',workload_scope=scope,
                    extension_basis='hybrid model-card YaRN factor4 above262144; API extension method unknown, identical YaRN not established')
                result.append(item)
                if cost is not None:
                    candidates[point].append((cost,tag,item))
        for point, values in candidates.items():
            values.sort(key=lambda x:(x[0],x[1]))
            priceable=sum(1 for row in result if row['availability_scenario']==scenario and row['cache_point']=='measured' and row['admitted'] and row['pricing_status']=='complete')
            if point=='measured' and len(values)!=priceable:
                # Partial observations price their providers but cannot establish
                # the cheapest/median over a still-unmeasured admitted cohort.
                continue
            if values:
                low, median = values[0],values[len(values)//2]
                low[2]['role'] = 'cheapest'
                median[2]['role'] = 'cheapest_and_median' if low is median else 'median'
                selected[scenario,point] = dict(cheapest=low[0],median=median[0],cheapest_provider=low[1],median_provider=median[1],
                    cheapest_hit=low[2]['cache_hit_fraction'],median_hit=median[2]['cache_hit_fraction'],count=len(values))
    return result, selected


def pending_inputs(servers):
    known = {(MODEL,row['tag']) for row in providers()}
    cache = i.cache_rows(i.rows('provider_cache'),known)
    availability,window = i.availability_rows(i.rows('provider_availability'),known)
    decode = i.server_rows(i.rows('server_decode'),servers,'decode')
    prefill = i.server_rows(i.rows('server_prefill'),servers,'prefill')
    mac = i.mac_rows(i.rows('mac_million'))
    return dict(cache=cache,availability=availability,window=window,decode=decode,prefill=prefill,mac=mac)
