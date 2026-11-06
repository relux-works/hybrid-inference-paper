"""Compact run25 tables with same-profile, same-server dedicated comparisons."""
import copy
import csv
import gzip
import json
import math
from pathlib import Path

from run23 import engine as previous, economics as e
from hybridcalc import deep_r21 as deep, server_economics_r20 as s, measurements_r20 as old
from . import model

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    with (ROOT/path).open(newline='') as f:
        return list(csv.DictReader(f))


def number(value):
    return value if isinstance(value,(int,float)) and math.isfinite(value) else None


def compare(costs, refs):
    valid = [number(a) is not None and number(b) is not None for a,b in zip(costs,refs)]
    wins = [v and a < b for a,b,v in zip(costs,refs,valid)]
    crossing = old.break_even([a if v else None for a,v in zip(costs,valid)],refs)
    return dict(sustained_from=crossing['from_people'] if isinstance(crossing['from_people'],int) else '',
                first_win=next((i+1 for i,x in enumerate(wins) if x),''),
                feasible_team_intervals=json.dumps(model.intervals(valid),separators=(',',':')),
                cheaper_team_intervals=json.dumps(model.intervals(wins),separators=(',',':')),
                statement=crossing['statement'],scan_max=len(costs))


class Weighted(e.Economics):
    """Identical own-cluster formula with explicit profile weights in each mean."""
    def __init__(self,*args,weights,**kwargs):
        self.weights = weights
        super().__init__(*args,**kwargs)
        self.cold = {k:sum(w*sv.cold(d) for w,(d,n,o,t) in zip(weights,self.calls)) for k,sv in self.servers.items()}

    def fleet_stats(self,server,team,boxes,gpus):
        # Populate accepted per-call measured decode vectors, then weight them.
        original = super().fleet_stats(server,team,boxes,gpus)
        active = original['active_gpus']; offered = min(int(team*self.concurrency),32*active)
        key = ('weighted',server.key,active,offered)
        if key not in self.fleet_cache:
            total = dec_total = 0.; minimum = 32; max_total = 0
            for weight,(pre,o,tool,slots,rates) in zip(self.weights,self.decode_vectors[server.key]):
                streams = min(offered,active*slots); lo,extra = divmod(streams,active)
                aggregate = (active-extra)*rates[lo]+(extra*rates[lo+1] if extra else 0)
                total += weight*max(pre/active+o/aggregate,(pre+o/(aggregate/streams)+tool)/streams)
                dec_total += weight*o/aggregate
                minimum = min(minimum,lo); max_total = max(max_total,streams)
            self.fleet_cache[key] = dict(fleet_s_call=total,decode_fleet_s_call=dec_total,active_gpus=active,batch_min=minimum,total_streams=max_total)
        return self.fleet_cache[key]


def setup():
    c = previous.context(); stats = deep.checked_stats(); cfg = s.config()
    servers = {'pro6000_fp8':e.Server('pro6000_fp8',cfg)}
    profiles = [('existing_combined',c.g.resolve(c.valid).value),
                ('claude_deep',deep.reconstruct(stats['agents']['claude']))]
    prepared = []; coverage = []
    for profile,calls in profiles:
        indices = [i for i,(d,n,o,t) in enumerate(calls) if 16000 <= d and d+n+o <= 249000 and 512 <= n <= 10000]
        selected = [calls[i] for i in indices]
        billed = old.billing_calls(calls,indices,c.inputs.get('workload.chunk_calls'))
        targets = [sum(x[j] for x in calls)/len(calls) for j in (1,2)]
        baseline = [1/len(selected)]*len(selected)
        fitted = model.reweight(selected,targets)
        for weighting,weights in [('accepted_shapes',baseline),('full_delta_output_mix',fitted)]:
            pcfg = copy.deepcopy(cfg); pcfg['reservation_depth'] = 249000
            econ = Weighted(c,selected,servers,pcfg,weights=weights)
            effective = 1/sum(w*w for w in weights)
            meta = dict(profile=profile,weighting=weighting,scope_tier='measured_ladder',transport='bf16',
                        client='M5 Max64 PRI31 already owned',server='PRO6000 vLLM FP8 default KV',share_call_shapes=len(selected)/len(calls),
                        selected_shapes=len(selected),profile_shapes=len(calls),effective_shapes=effective,
                        weighted_api_mean_input=sum(w*(x[0]+x[1]) for w,x in zip(weights,billed)),
                        weighted_api_mean_output=sum(w*x[2] for w,x in zip(weights,billed)),
                        coverage_basis='fitted/reconstructed call-shape quadrature, not observed per-call log rows; normalized to declared calls/person-month; full workload unsupported')
            prepared.append((meta,econ,weights))
        sums = {j:sum(x[j] for x in calls) for j in (0,1,2)}
        row = dict(profile=profile,source='owner aggregate package; accepted fitted/reconstructed profiles',
                   shapes=len(calls),subset_shapes=len(selected),fitted_call_shape_share=len(selected)/len(calls),
                   observed_log_call_share='',observed_log_input_token_share='',observed_log_output_token_share='',observed_log_work_share='',
                   fitted_input_token_share=sum(x[0]+x[1] for x in selected)/(sums[0]+sums[1]),
                   fitted_new_token_share=sum(x[1] for x in selected)/sums[1],
                   fitted_output_token_share=sum(x[2] for x in selected)/sums[2],
                   full_mean_input=(sums[0]+sums[1])/len(calls),subset_mean_input=sum(x[0]+x[1] for x in selected)/len(selected),
                   full_mean_new=targets[0],full_mean_output=targets[1],
                   source_gap=model.config()['source_gap'])
        # Only measured anchors exist; tails use the accepted Mac depth/delta
        # extension. Clamp out-of-context shapes visibly for a work-only proxy.
        mac = c.measured_m5.mac; total_pre = total_dec = sub_pre = sub_dec = 0.; clipped = 0
        selected_set = set(indices)
        for i,(d,n,o,t) in enumerate(calls):
            dd = min(d,mac.limit-1); nn = min(max(n,0),mac.limit-dd)
            if dd != d or nn != n or d+o > mac.limit:
                clipped += 1
            pre = mac.prefill(dd,nn)
            dec = o/mac.decode(1,min(d+n,mac.limit))
            total_pre += pre; total_dec += dec
            if i in selected_set:
                sub_pre += pre; sub_dec += dec
        row.update(fitted_prefill_seconds_share=sub_pre/total_pre,fitted_decode_seconds_share=sub_dec/total_dec,
                   fitted_work_seconds_share=(sub_pre+sub_dec)/(total_pre+total_dec),work_clipped_shapes=clipped,
                   work_proxy='M5 PRI31 prefill seconds + single-stream decode seconds, no tool gaps; accepted measured anchors with explicit depth/delta extrapolation outside ladder; out-of-context shapes clamped only for proxy, not admitted; not observed work')
        coverage.append(row)
    return c,prepared,coverage


def api_refs():
    return [r for r in read('calc/out/run24/api_rankings.csv') if r['model']=='qwen/qwen3.8-27b' and r['scope_tier']=='measured_ladder']


def series_control(profile,load,share,billing):
    doc = json.loads(gzip.decompress((ROOT/'calc/run24/data/cost-curves.json.gz').read_bytes()))
    return next(x['prices'] for x in doc['curves'] if all(str(x[k])==str(v) for k,v in
        dict(profile=profile,scope_tier='measured_ladder',transport='bf16',load=load,share=share,client='m5max64',server='pro6000_fp8',billing=billing).items()))


def calculate(scan_max=None):
    cfg = model.config(); scan_max = scan_max or cfg['scan_max']
    c, prepared, coverage = setup(); refs = api_refs()
    tables = {k:[] for k in ('fleet_summary','comparisons','crossings','closed_contour','coverage','storage_by_depth','coverage_sensitivity')}
    tables['coverage'] = coverage
    controls = read('calc/out/run23/main_economics.csv')
    for meta,econ,weights in prepared:
        profile = meta['profile']; server = econ.servers['pro6000_fp8']; selected = econ.calls
        ranks = [r for r in refs if r['profile']==profile]
        if meta['weighting']!='accepted_shapes':
            ranks = reweighted_api(ranks,meta['weighted_api_mean_input'],meta['weighted_api_mean_output'])
        if meta['weighting']=='accepted_shapes':
            for depth in (16000,32000,64000,100000,164000,249000):
                tables['storage_by_depth'].append(dict(profile=profile,depth=depth,server_copy_bytes=server.session_bytes(depth),
                    client_copy_bytes=depth*34816+156893184,wire_state_bytes=78446592,
                    basis='server bf16-default KV65536B/token + f32 resident recurrent state; client q8_0 KV34816; bf16 transport is not half the full slot'))
        for share in cfg['shares']:
            for load in ('light','medium','heavy'):
                demand = c.inputs.get('service.profiles.'+load)*share; monthly = demand*econ.days
                for billing in ('bought','rented'):
                    common = dict(meta,share=share,load=load,billing=billing,requested_day=demand,monthly_calls=monthly,
                        link='office125MB/s RTT1ms' if billing=='bought' else 'engine WAN112.5MB/s RTT400ms estimated',
                        contour='all calls open model in-house, no external model' if share==1 else 'open-model segment20%; remaining80% sent to stronger cloud model, not a closed contour',
                        intensity='owner2500calls/day atypical' if load=='heavy' else 'typical '+load)
                    own = [econ.own('pro6000_fp8',team,demand,billing) for team in range(1,scan_max+1)]
                    own_costs = [number(x['person_month']) for x in own]
                    canonical = series_control(profile,load,share,billing)
                    if meta['weighting']=='accepted_shapes':
                        crossing = compare(canonical[:scan_max],own_costs)
                        sample = next(r for r in controls if all(r[k]==str(v) for k,v in dict(profile=profile,scope_tier='measured_ladder',transport='bf16',load=load,share=share,client='m5max64',basis='owned',server='pro6000_fp8',billing=billing,team=50).items()))
                        tables['closed_contour'].append(dict(common,**crossing,team50_hybrid=canonical[49],team50_own_cluster=own_costs[49],
                            team50_hybrid_nodes=sample['boxes'],team50_offload_share=sample['offload_share'],
                            basis='accepted run24 inherited sufficient fleet, storage900GB/node; same PRO/billing own vLLM cluster; no queue terms in this control'))
                    # New fleet policy is scoped to the bought-office question.
                    # Rented rows above are exact accepted controls, including
                    # their existing egress accounting; no new rental economics.
                    if billing != 'bought':
                        continue
                    for case in cfg['storage_cases']:
                        for speed in cfg['speed_factors']:
                            fleet = model.Fleet(econ,weights,case,speed,billing,cfg)
                            family = dict(common,storage_case=case['name'],restore_slowdown=speed,proxy_basis=case['basis'])
                            series = {str(n):[] for n in cfg['fleets']}; series['minimum'] = []
                            minimum = []; samples = {}
                            for team in range(1,scan_max+1):
                                best = fleet.minimum(team,demand); minimum.append(best)
                                for policy in series:
                                    row = best if policy=='minimum' else fleet.evaluate(team,demand,int(policy))
                                    series[policy].append(number(row['person_month']))
                                    if team==cfg['team']:
                                        samples[policy] = row
                            for policy,costs in series.items():
                                row = samples[policy]; own50 = own_costs[49]
                                summary = dict(family,fleet_policy=policy,**row,own_cluster_person_month=own50 if own50 is not None else '',
                                    own_over_hybrid=own50/row['person_month'] if own50 is not None and number(row['person_month']) is not None else '',
                                    baseline_mean_ttft_s=econ.prepared['pro6000_fp8','m5max64','measured_envelope'].stats(.94,'office_gigabit' if billing=='bought' else 'engine_wan')['prefill_wait_s_call'],
                                    baseline_hybrid_person_month=canonical[49] if meta['weighting']=='accepted_shapes' else '')
                                tables['fleet_summary'].append(summary)
                                tables['crossings'].append(dict(family,fleet_policy=policy,reference='own_cluster',cache_point='not applicable',cadence='not applicable',**compare(costs,own_costs)))
                                for rank in ranks:
                                    price = float(rank['usd_per_1000_calls']) if rank['usd_per_1000_calls']!='' else None
                                    ref = monthly*price/1000 if price is not None else None
                                    info = dict(family,fleet_policy=policy,reference='api_'+rank['role'],cache_point=rank['cache_point'],cadence=rank['cadence'],
                                        provider=rank['provider'],warm_calls=rank['warm_calls'],cohort_size=rank['cohort_size'],
                                        api_basis='accepted run24 per-cadence admitted PRICEABLE Qwen cohort, no global cheapest claim; aggregate-token cache fraction portability assumed')
                                    tables['comparisons'].append(dict(info,team=50,hybrid_person_month=row['person_month'],api_person_month=ref if ref is not None else '',
                                        api_over_hybrid=ref/row['person_month'] if ref is not None and number(row['person_month']) is not None else '',status=row['status']))
                                    cross = compare(costs,[ref]*scan_max)
                                    if ref is None:
                                        cross.update(statement='unknown: no qualified measured point',sustained_from='',first_win='')
                                    tables['crossings'].append(dict(info,**cross))
                            if meta['weighting']=='full_delta_output_mix':
                                tables['coverage_sensitivity'].append(dict(family,**compare(series['minimum'],own_costs),
                                    minimum_nodes_team50=minimum[49]['nodes'],person_month_team50=minimum[49]['person_month'],
                                    target_new=sum(w*x[1] for w,x in zip(weights,selected)),
                                    target_output=sum(w*x[2] for w,x in zip(weights,selected)),
                                    weighted_mean_input=sum(w*(x[0]+x[1]) for w,x in zip(weights,selected)),
                                    reweight_basis='maximum entropy weights match full fitted-profile mean new/output tokens; full input-depth/correlation mix not identified, no full-workload claim'))
                print('run25',profile,meta['weighting'],share,load,flush=True)
    return tables


def reweighted_api(ranks,mean_input,mean_output):
    # Recompute provider tariffs first, then rerank: provider identity can change.
    from run24 import api as current_api, inputs as current_inputs
    base = current_api.prices(current_inputs.load())
    profile = ranks[0]['profile']; filtered = []
    # Recover input/output marginal tariffs by exact independent perturbations.
    study = current_inputs.load()
    for row in base:
        if row['profile']!=profile or row['scope_tier']!='measured_ladder':
            continue
        key = (row['model'],row['provider'],profile,row['cadence'])
        inv = current_api.inventory(study)[row['model'],row['provider']]
        p = study['prices'].get(key,inv.get('pricing',{})); row = dict(row)
        if row['effective_usd_per_1000_calls']!='':
            hit = float(row['cache_hit_fraction'])
            row['effective_usd_per_1000_calls'] = s.api_cost(dict(pricing=p),(mean_input,0,mean_output),hit)*1000
        filtered.append(row)
    return [r for r in current_api.ranked(filtered) if r['model']=='qwen/qwen3.8-27b']
