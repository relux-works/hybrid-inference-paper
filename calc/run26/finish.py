"""Publish compact quoted coordinates and the conditional MoE verdict after export."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from run26 import export, model as m


def read(name):
    with (export.OUT/name).open()as f:return list(csv.DictReader(f))


def num(v):
    if v in ('',None):return None
    return float(v)


def quotes():
    result=[]
    for i,r in enumerate(read('paper/middle_crossings.csv'),1):
        for col in ('sustained_from','team50_hybrid','team50_own'):
            result.append(dict(source='paper/middle_crossings.csv',row=i,column=col,value=r[col],
                coordinate='|'.join(r[k]for k in ('profile','model','server','client','client_basis','load','share','billing')),
                claim_basis=r['rate_basis']+'; '+r['coverage']+'; '+r['link']+'; prefill-only, own same-model; sufficient fleet'))
    for name,cols in [('cloud_affordability.csv',('first_affordable','team50_person_month')),('moe_decode.csv',('glm_gain','qwen_gain','expert_read_amortization'))]:
        for i,r in enumerate(read(name),1):
            if name=='moe_decode.csv' and r['requested_streams']!='32':continue
            for col in cols:result.append(dict(source=name,row=i,column=col,value=r[col],coordinate=json.dumps({k:v for k,v in r.items()if k in ('billing','retention_basis','depth','requested_streams')},sort_keys=True),claim_basis=r.get('basis',r.get('criterion',''))))
    for i,r in enumerate(read('middle_cost.csv'),1):
        if r['team']=='50' and r['share']=='1.0' and r['billing']=='bought' and (r['model']=='qwen' or r['glm_prefill_slowdown']=='1'):
            for col in ('own_over_hybrid','offload_share','client_capacity_day'):
                result.append(dict(source='middle_cost.csv',row=i,column=col,value=r[col],
                    coordinate='|'.join(r[k]for k in ('profile','model','server','client','client_basis','load','share','billing')),
                    claim_basis=r['rate_basis']+'; '+r['coverage']+'; '+r['link']))
    return result


def verify_quotes():
    for q in read('quotes.csv'):
        rows=read(q['source']);r=rows[int(q['row'])-1]
        if r[q['column']]!=q['value']:raise AssertionError('quote coordinate mismatch '+q['coordinate'])
    return len(read('quotes.csv'))


def moe_verdict():
    cc=read('crossings.csv');out=[]
    for profile in ('existing_combined','claude_deep'):
        for load in ('light','medium','heavy'):
            for basis in ('owned','new'):
                q=next(r for r in cc if all(r[k]==v for k,v in dict(profile=profile,load=load,client_basis=basis,share='1.0',billing='bought',server='b300_fp8',client='m5max64').items()))
                for client in ('ultra256','ultra512'):
                    g=next(r for r in cc if all(r[k]==v for k,v in dict(profile=profile,load=load,client_basis=basis,share='1.0',billing='bought',server='glm_two_b300',client=client,glm_prefill_slowdown='1').items()))
                    support=bool(g['sustained_from']) and (not q['sustained_from'] or int(g['sustained_from'])<int(q['sustained_from']))
                    out.append(dict(profile=profile,load=load,client_basis=basis,glm_client=client,qwen_client='m5max64',
                        qwen_b300_sustained_from=q['sustained_from'],glm_two_b300_sustained_from=g['sustained_from'],
                        conditional_support=support,glm_first_win=g['first_win'],glm_winning_intervals=g['cheaper_team_intervals'],
                        basis='UNMEASURED GLM/Ultra projection; bought8-B300 paid-node control, fourGLM vs eightQwen replicas/node, same calls/s1,128/256/512 memory distinctions explicit; x1prefill; no universal or completed-task claim'))
    return out


def supplement():
    lines=['','## Numerical MoE result and ownership limits','',
        'At the same requested32 streams, the modelled server gains are:','',
        '| Depth | GLM two-B300 gain | Dense Qwen one-B300 gain | Expert-read amortization |','|---:|---:|---:|---:|']
    for r in read('moe_decode.csv'):
        if r['requested_streams']=='32':lines.append(f"| {r['depth']} | {float(r['glm_gain']):.3f} | {float(r['qwen_gain']):.3f} | {float(r['expert_read_amortization']):.3f} |")
    lines+=['','The expert-read amortization is B×topk/expected_union; it can remain small when dense weights share once across the entire batch. Smaller MLA KV raises the resident batch limit but does not give dense-style weight sharing. This mechanism supports testing the MoE hypothesis, not presuming its economic answer.','',
        'For a hardware-matched paid eight-B300 node comparison, team50 s=1 bought, combined measured-shape profile:','',
        '| Model/client | Client basis | Light own/hybrid | Medium own/hybrid | Heavy own/hybrid |','|---|---|---:|---:|---:|']
    costs=read('middle_cost.csv');ratios=[]
    for client in ('m5max64','m5max','ultra256','ultra512'):
        for basis in ('owned','new'):
            rr=[r for r in costs if r['team']=='50' and r['profile']=='existing_combined' and r['share']=='1.0' and r['billing']=='bought' and r['client']==client and r['client_basis']==basis and r['server']in ('b300_fp8','glm_two_b300') and r['glm_prefill_slowdown']in ('','1')]
            values=[next(r for r in rr if r['load']==load)['own_over_hybrid']for load in ('light','medium','heavy')]
            ratios.append((client,basis,values))
            lines.append('| '+client+' | '+basis+' | '+' | '.join(f'{float(v):.3f}'if v else 'capacity shortfall'for v in values)+' |')
    lines+=['','Conditional engine verdict: on the bought B300-node control, owned GLM/Ultra clients have a sustained medium/heavy crossing where Qwen/Max does not; light and newly purchased Studio clients do not establish a sustained advantage through500 in the combined profile. This is conditional cost support for decode on the client, not an empirical GLM result. The GLM team50 policy selects zero prefill offloads: it is projected local compute plus paid retention, and does not demonstrate a prefill-offload speed benefit. `moe_verdict.csv` gives both profiles and both Studio memories. Qwen on PRO is a different and cheaper hardware option, so this is not a general economic superiority claim.','',
        'Values above1 favor the hybrid. GLM rows remain UNMEASURED Ultra/GLM projections (prefill x1; x2 is in root outputs), and client purchase can reverse a win. The table reports the hypothesis conditionally by load and ownership; it establishes no universal MoE advantage or completed-task parity. Qwen PRO remains the dedicated paper headline; this same-B300 control isolates part of the hardware-price confound.','',
        '## Mixed scheme and fleet boundaries','',
        'All s=.2/.5 crossings in `crossings.csv` are legitimate closed-contour segment comparisons ONLY when the remainder runs internally at the identical common cost. `mixed_scheme.csv` has both copies of C and symbolic-pending cost labels. The numerical two-node weight floor is not a measured large-model service bill. The middle-model delta, not the capacity-floor total, is the reliable algebraic comparison.','',
        'Fleet-size variants in this run are team50 sensitivities, not fresh integer-team crossings under every storage policy. Run25’s legacy crossing tables remain frozen with their explicit server-generation fallback; they cannot substitute for the new prefill-only crossings. Full1..500 primary crossings are recomputed for the inherited dedicated policy. No GLM fleet-queue extension is claimed from the PRO-only run25 contract.','',
        'Compact `quotes.csv` binds each printed crossing/team50 cost, cloud affordability coordinate and32-stream MoE gain to an exact CSV cell; it is not a full quote dump.']
    lines+=['','## Zero-offload boundary at team50','',
        'A paid retained-copy fleet with zero offload is a local-compute/retention scenario, not evidence of faster hybrid prefill. The costs remain charged. The routing shares below prevent interpreting a zero-offload win as an offload-speed benefit.','',
        '| Profile | Model/client, owned | Load | Prefill offload share | Client capacity/day |','|---|---|---|---:|---:|']
    for r in costs:
        if r['team']=='50' and r['share']=='1.0' and r['billing']=='bought' and r['client_basis']=='owned' and (r['model']=='qwen' and r['server']=='pro6000_fp8' or r['model']=='glm' and r['glm_prefill_slowdown']=='1'):
            value=f"{float(r['offload_share']):.2%}" if r['hybrid_status']=='feasible_prefill_only' and r['offload_share'] else r['hybrid_status']
            cap=f"{float(r['client_capacity_day']):.1f}" if r['client_capacity_day'] else 'undefined'
            lines.append(f"| {r['profile']} | {r['model']}/{r['client']} | {r['load']} | {value} | {cap} |")
    return '\n'.join(lines)+'\n'


def capital_metadata(checks):
    changes=[]
    for path in sorted(export.OUT.rglob('*.csv')):
        if path.name in ('quotes.csv','publication-metadata-fixes.csv'):continue
        with path.open()as f:rr=list(csv.DictReader(f))
        if not rr or 'client_capital_month'not in rr[0]:continue
        original=json.dumps([{k:v for k,v in r.items()if k!='client_capital_month'}for r in rr],sort_keys=True)
        edited=False
        for i,r in enumerate(rr,1):
            if r['client_basis']=='owned'and r['client_capital_month']=='':
                changes.append(dict(source=str(path.relative_to(export.OUT)),row=i,column='client_capital_month',old='',new='0.0',reason='owned capital is zero even when total service price refuses'))
                r['client_capital_month']='0.0';edited=True
        after=json.dumps([{k:v for k,v in r.items()if k!='client_capital_month'}for r in rr],sort_keys=True)
        if original!=after:raise AssertionError('capital metadata changed another cell')
        if edited:export.write(path,export.csv_bytes(rr),checks)
    if changes:export.write(export.OUT/'publication-metadata-fixes.csv',export.csv_bytes(changes),checks)
    return changes


def mixed_scope(checks):
    rows=read('mixed_scheme.csv')
    for r in rows:r['middle_ratio_basis']='middle segment only; not total internal cost ratio'
    export.write(export.OUT/'mixed_scheme.csv',export.csv_bytes(rows),checks)


def verify_mixed():
    rows=read('mixed_scheme.csv')
    for r in rows:
        if r.get('middle_ratio_basis')!='middle segment only; not total internal cost ratio':
            raise AssertionError('mixed ratio scope missing or total-cost claim')
        if r['hybrid_person_month'] and r['own_person_month']:
            if abs(float(r['own_over_hybrid'])-float(r['own_person_month'])/float(r['hybrid_person_month']))>1e-10:
                raise AssertionError('mixed middle ratio differs from segment costs')
    return len(rows)


def refresh_words(checks):
    cc=read('paper/middle_crossings.csv');costs=read('middle_cost.csv')
    keys=('profile','model','server','client','client_basis','billing','load','share','glm_prefill_slowdown')
    exposure={tuple(r[k]for k in keys):r for r in costs if r['team']=='50'}
    rows=[dict(r,sentence=export.words(r,exposure[tuple(r[k]for k in keys)]))for r in cc]
    export.write(export.OUT/'paper/words_ready.csv',export.csv_bytes(rows),checks)


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--audit-only':
        print(json.dumps(dict(export.audit(),quoted_coordinates=verify_quotes(),mixed_scope_rows=verify_mixed())));return
    checks=[];capital_metadata(checks);mixed_scope(checks);refresh_words(checks);marker='\n## Numerical MoE result and ownership limits\n'
    report=export.REPORT.read_text().split(marker)[0].replace('Muse r5x9 review pending at start.','Muse r5x9 ACCEPT; review arrived during this run.')
    export.write(export.OUT/'moe_verdict.csv',export.csv_bytes(moe_verdict()),checks)
    export.write(export.REPORT,(report+supplement()).encode(),checks)
    export.write(export.OUT/'quotes.csv',export.csv_bytes(quotes()),checks)
    export.write(export.OUT/'publication-write-audit.json',(json.dumps(checks,indent=2)+'\n').encode(),[])
    export.refresh_manifest();print(json.dumps(dict(export.audit(),quoted_coordinates=verify_quotes(),mixed_scope_rows=verify_mixed())))

if __name__=='__main__':main()
