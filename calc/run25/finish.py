"""Compact changed-crossing ledger and source-bound final audit."""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from run25 import export, engine, model, publication


def key(row):
    return tuple(row[k] for k in ('profile','share','load','billing'))


def load(name):
    return engine.read('calc/out/run25/'+name+'.csv')


def audit_rows(rows):
    """Semantic gate operates on published rows, including resource refusals."""
    for row in rows:
        if row['status']=='feasible':
            assert row['feasible']=='True', 'feasible marker differs'
            assert int(row['storage_capacity_copies']) >= int(row['retained_copies']), 'declared storage shortfall'
            assert int(row['storage_shortfall_copies'])==0, 'declared storage shortfall'
            assert float(row['actual_mean_queue_s']) <= float(row['charged_mean_queue_s'])+1e-12, 'latency budget below collision queue'
            assert float(row['charged_mean_queue_s'])<=model.config()['max_mean_queue_s'], 'latency bound exceeded'
            assert float(row['service_utilization'])<=model.config()['max_service_occupancy'], 'compute budget exceeded'
            assert float(row['person_month'])>0, 'zero cost forbidden'
        else:
            assert row['person_month']=='' and row['feasible']=='False', 'refused fleet has finite price'


def audit():
    export.audit()
    doc = json.loads((export.OUT/'manifest.json').read_text())
    current={path:export.sha((ROOT/path).read_bytes())for path in doc['sources']}
    assert export.history.accepted_identity('ec28e37c',current)==doc['sources'], 'original source identity changed'
    audit_rows(load('fleet_summary'))
    closed = load('closed_contour')
    assert len(closed)==24
    assert {r['share'] for r in closed}=={'0.2','1.0'}
    assert all('80%' in r['contour'] and 'not a closed contour' in r['contour'] for r in closed if r['share']=='0.2')
    assert all('in-house' in r['contour'] for r in closed if r['share']=='1.0')
    coverage = load('coverage')
    assert all(r['observed_log_work_share']=='' and r['observed_log_input_token_share']=='' for r in coverage)
    assert 'UNMEASURED' in model.config()['arrival_basis']
    print('source, published storage/queue rejection, closed-contour and finite-coverage audits exit0')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--audit-only',action='store_true'); args = parser.parse_args()
    if args.audit_only:
        return audit()
    export.audit(); rows = load('crossings'); bases = {key(r):r for r in load('closed_contour')}
    ranks = engine.api_refs(); before = {}; deltas = []
    for row in rows:
        k = key(row)
        reference = row['reference']
        if reference=='own_cluster':
            base = bases[k]; old_statement=base['statement']; old_from=base['sustained_from']
        else:
            identity = k+(reference,row['cache_point'],row['cadence'])
            if identity not in before:
                rank = next(r for r in ranks if r['profile']==row['profile'] and r['role']==reference.removeprefix('api_') and r['cache_point']==row['cache_point'] and r['cadence']==row['cadence'])
                price = float(rank['usd_per_1000_calls']) if rank['usd_per_1000_calls']!='' else None
                monthly = float(row['monthly_calls']); value = price*monthly/1000 if price is not None else None
                curve = engine.series_control(row['profile'],row['load'],float(row['share']),row['billing'])
                control = engine.compare(curve,[value]*500)
                if value is None:
                    control.update(statement='unknown: no qualified measured point',sustained_from='')
                before[identity] = control
            old_statement=before[identity]['statement']; old_from=before[identity]['sustained_from']
            base=before[identity]
        fields = ('profile','weighting','share','load','billing','link','storage_case','restore_slowdown','fleet_policy','reference','cache_point','cadence',
                  'statement','sustained_from','first_win','feasible_team_intervals','cheaper_team_intervals')
        deltas.append(dict({f:row[f] for f in fields},baseline_statement=old_statement,baseline_sustained_from=old_from,
                           baseline_first_win=base['first_win'],baseline_feasible_team_intervals=base['feasible_team_intervals'],
                           baseline_cheaper_team_intervals=base['cheaper_team_intervals'],
                           changed=any(str(row[f])!=str(base[f]) for f in ('statement','first_win','feasible_team_intervals','cheaper_team_intervals')),
                           comparison_basis='accepted run24 inherited fleet versus new declared fleet policy; token-mix rows additionally change workload weights and API price means'))
    checks = []; payload = export.csv_bytes(deltas)
    total_before = sum(p.stat().st_size for p in export.OUT.glob('*.csv') if p.name!='changed_crossings.csv')
    assert total_before+len(payload)<model.config()['output_limit_bytes'], 'compact CSV budget exceeded before write'
    path = export.OUT/'changed_crossings.csv'; export.write(path,payload,checks)
    tables={name:load(name) for name in ('fleet_summary','comparisons','crossings','closed_contour','coverage','storage_by_depth','coverage_sensitivity')}
    original={name:[dict(row) for row in tables[name]] for name in ('fleet_summary','comparisons','closed_contour','coverage_sensitivity')}
    tables=publication.enrich(tables)
    preserved={}
    for name,oldrows in original.items():
        before=[];after=[]
        for oldrow,newrow in zip(oldrows,tables[name]):
            for field,value in oldrow.items():
                if field=='contour':continue
                before.append((field,value));after.append((field,newrow[field]))
        assert before==after, 'publication refresh changed a calculation cell'
        preserved[name]=dict(cells=len(before),sha256=export.sha(json.dumps(before,separators=(',',':')).encode()))
    metadata_payloads={}
    for name in ('fleet_summary','comparisons','closed_contour','coverage_sensitivity'):
        target=export.OUT/(name+'.csv');metadata_payloads[target]=export.csv_bytes(tables[name])
        export.write(target,metadata_payloads[target],checks)
    summaries = tables['fleet_summary']; text = export.report({name:publication.typed(values) for name,values in tables.items()})
    # Publication-only clarification; office numerical calculations are unchanged.
    text = text.replace('Rental rows rent the GPU but own this incremental storage, whose physical attachment is an unmeasured portability assumption.',
        'The NEW fleet policy is bought-office only; rental rows in the closed-contour control retain the accepted run24 engine and egress accounting. The new office proxy refuses rental billing.')
    text += '\n## Changed crossings and the latency price\n\n'
    text += 'At the accepted light-load routing, prefill83.2663 GPU-seconds/person-day ×50=4163.3 GPU-seconds/day. One node has28800×70%=20160 service-seconds/day: this work alone fits one node. That is a diagnostic holding routing fixed, not a claim the original900GB one-node retention policy fits. Failed sensitivity rows mean no fleet certified under the declared storage/mean-delay/occupancy/concurrency rules, not measured physical impossibility.\n\n'
    text += 'Sensitivity service occupancy reserves the node during IO, wire and equivalent GPU work; it is not GPU-busy utilization and differs in scope from the accepted3.61% GPU-service diagnostic. Calendar occupancy uses the same node-reservation scope.\n\n'
    text += 'Rented all-open-model rows assume the dedicated rental is approved inside the team trust boundary; this removes external model APIs but does not establish a physical office perimeter or provider privacy assurance. Bought-office rows are the closed-contour headline.\n\n'
    text += 'All rows below use accepted fitted call shapes, bf16, owned M5Max64 PRI31 and bought PRO6000 vLLM over office125MB/s RTT1ms; expanded3.6TB NVMe,7GB/s full read/write and declared$400/node capex upgrade. Minimum fleet is certified against the declared Poisson/random-node mean-queue model (≤5s,≤70% service occupancy), not a measured scheduler. Copy retention is4/person; fractions cover call shapes normalized per person-month, not full work. API rows use their stated cadence/cache point; core measured Qwen remains unknown.\n\n'
    text += '| Profile | s | Load | Reference | Cache/cadence | Accepted sustained crossing | Sensitivity sustained crossing | First feasible win |\n|---|---:|---|---|---|---|---|---:|\n'
    for r in deltas:
        if not (r['weighting']=='accepted_shapes' and r['billing']=='bought' and r['storage_case']=='expanded_nvme' and r['restore_slowdown']=='1' and r['fleet_policy']=='minimum'):
            continue
        if r['reference']!='own_cluster' and not (r['cache_point']=='measured' and r['cadence']=='v1_long_pause'):
            continue
        text += '| {} | {} | {} | {} | {}/{} | {} | {} | {} |\n'.format(r['profile'],r['share'],r['load'],r['reference'],r['cache_point'],r['cadence'],r['baseline_statement'],r['statement'],r['first_win'])
    text += '\n| Profile | s | Load | Nodes | Client-served mean TTFT s | All-call mean TTFT proxy s | Accepted client mean TTFT s | Offload mean TTFT s | Restore read/write s per offload | Charged/model queue s | Offload share | Service occupancy |\n|---|---:|---|---:|---:|---:|---:|---:|---|---|---:|---:|\n'
    for r in summaries:
        if not (r['weighting']=='accepted_shapes' and r['billing']=='bought' and r['storage_case']=='expanded_nvme' and r['restore_slowdown']=='1' and r['fleet_policy']=='minimum'):
            continue
        def fmt(k):
            return f'{float(r[k]):.3f}' if r.get(k,'')!='' else 'unknown'
        text += '| {} | {} | {} | {} | {} | {} | {} | {} | {}/{} | {}/{} | {} | {} |\n'.format(r['profile'],r['share'],r['load'],r['nodes'],fmt('mean_ttft_s'),fmt('mean_all_call_ttft_s'),fmt('baseline_mean_ttft_s'),fmt('mean_offload_ttft_s'),fmt('read_s_offload'),fmt('write_s_offload'),fmt('charged_mean_queue_s'),fmt('actual_mean_queue_s'),fmt('offload_share'),fmt('service_utilization'))
    text += '\nThe changed ledger includes all declared bought-office fixed/minimum fleets. The inherited rented control is separate. A fixed fleet that exhausts storage before500 people has only finite feasible/winning intervals; its sustained crossing is correctly absent. No result proves the full raw-log workload has the same crossing. Material changes under delta/output reweighting are shown above; a surviving crossing can coexist with zero prefill offload and therefore cannot be quoted as an offload performance benefit.\n'
    paired = load('paired_retention')
    text += '\n## Paired retention fairness control\n\nThe main ratios use the accepted own-cluster comparator, which retains its original storage/rebuild policy. To expose that asymmetry, this additional control optimizes BOTH hybrid and own cluster with the SAME expanded3.6TB NVMe,7GB/s read/write,$400 extra-capex proxy and ≤5s mean queue/≤70% occupancy. Own cluster keeps the accepted server-only price boundary; hybrid includes$2.52 Mac energy+$5 front. These are sufficient certified model fleets, not runtime latency measurements or proven global optima. Only this primary1× storage proxy is paired; other proxies remain sensitivities against the accepted comparator.\n\n'
    text += '| Profile | s | Load | Hybrid nodes at50 | Own nodes at50 | Hybrid $ / occupancy at50 | Own $ / occupancy at50 | Sustained win vs paired own through500 |\n|---|---:|---|---:|---:|---:|---:|---|\n'
    for r in paired:
        if r['weighting']=='accepted_shapes' and r['billing']=='bought' and r['fleet_policy']=='minimum':
            def priced(kind):
                value=r[kind+'_person_month50'];util=r[kind+'_service_utilization50']
                return f'{float(value):.3f} / {float(util):.2%}' if value!='' else r[kind+'_status']
            text += '| {} | {} | {} | {} | {} | {} | {} | {} |\n'.format(r['profile'],r['share'],r['load'],r['hybrid_nodes50'],r['own_nodes50'],priced('hybrid'),priced('own'),r['statement'])
    export.write(export.REPORT,text.encode(),checks)
    doc = json.loads((export.OUT/'manifest.json').read_text())
    doc['files'][str(path.relative_to(ROOT))] = export.sha(payload)
    doc['files'][str(export.REPORT.relative_to(ROOT))] = export.sha(text.encode())
    for target,value in metadata_payloads.items():
        doc['files'][str(target.relative_to(ROOT))]=export.sha(value)
    doc['files']['calc/out/run25/paired_retention.csv'] = export.sha((export.OUT/'paired_retention.csv').read_bytes())
    doc['sources'] = {str(p.relative_to(ROOT)):export.sha(p.read_bytes()) for p in sorted((ROOT/'calc/run25').glob('*')) if p.is_file()}
    for p in sorted((ROOT/'calc/tests').glob('test_run25*.py')):
        doc['sources'][str(p.relative_to(ROOT))] = export.sha(p.read_bytes())
    doc['disk_writes'] += checks
    doc['publication_calculation_cells_preserved']=preserved
    doc['disk_writes'] += json.loads((ROOT/'.temp/hybrid-e-r20-261105/paired-disk-writes.json').read_text())
    doc['csv_bytes'] = sum((ROOT/p).stat().st_size for p in doc['files'] if p.endswith('.csv'))
    assert doc['csv_bytes']<model.config()['output_limit_bytes']
    export.write(export.OUT/'manifest.json',(json.dumps(doc,indent=2,sort_keys=True,allow_nan=False)+'\n').encode(),[])
    audit()


if __name__=='__main__':
    main()
