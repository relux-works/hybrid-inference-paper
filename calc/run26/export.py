"""Disk-guarded run26 summaries and frozen-parent/source manifest."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from run26 import engine, model as m
from run25.export import csv_bytes
OUT=ROOT/'calc/out/run26'
REPORT=ROOT/'calc/ENGINE-REPORT-R26-261105.md'


def write(path,raw,checks):
    before=shutil.disk_usage(ROOT).free
    df_before=subprocess.check_output(['df','-BG',str(ROOT)],text=True)
    if before-len(raw)-1048576<m.config()['free_floor_bytes']:
        raise RuntimeError('disk floor: refusing write '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.r26-tmp')
    temp.write_bytes(raw);temp.replace(path)
    after=shutil.disk_usage(ROOT).free;df_after=subprocess.check_output(['df','-BG',str(ROOT)],text=True)
    checks.append(dict(path=str(path.relative_to(ROOT)),bytes=len(raw),free_before=before,free_after=after,df_before=df_before,df_after=df_after))
    print('write',path.relative_to(ROOT),len(raw),before,after,flush=True)
    if after<m.config()['free_floor_bytes']:raise RuntimeError('disk floor crossed; stopping')


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()


import history_evidence as history


def frozen():
    """Retain original parent evidence and require each explicit paper migration."""
    parent=m.config()['parent']
    names=history.verify_engine_parent(parent)
    return dict(parent=parent,parent_files=len(names),historical_output_files=sum(n.startswith('calc/out/')for n in names),all_parent_bytes_identical=True)


def words(row, exposure):
    prefix='Conditional UNMEASURED GLM/M5 Ultra extrapolation' if row['model']=='glm' else 'Qwen measured-anchor scenario'
    link=row['link'];s=float(row['share']);profile=row['profile']
    servers={'pro6000_fp8':'RTX PRO6000 vLLM FP8 default KV','b300_fp8':'eight-B300 node vLLM FP8 default KV','glm_two_b300':'eight-B300 node, four two-B300 GLM replicas'}
    clients={'m5max64':'M5 Max64GB PRI31','m5max':'M5 Max128GB same-SoC portability','ultra256':'M5 Ultra Studio256GB EXTRAPOLATED','ultra512':'M5 Ultra Studio512GB EXTRAPOLATED'}
    calls=float(exposure['requested_middle_calls_day']);monthly=float(exposure['middle_calls_person_month'])
    return (f"{prefix}: {servers[row['server']]}, {row['billing']} dedicated calendar billing, {link}, "
        f"{clients[row['client']]} client {row['client_basis']}, s={s:g} of tasks assigned to this middle model inside the contour, "
        f"cache allowance not applicable (internal inference), {row['load']} load ({row['intensity']}; {calls:g} middle calls/person-day, {monthly:g} middle calls/person-month), "
        f"{profile}: {row['selected_shapes']}/{row['source_shapes']} ({100*float(row['shape_fraction']):.2f}%) fitted/reconstructed call shapes inside the measured ladder, "
        f"normalized per person-month (full log mix unsupported), {row['statement']}; "
        f"prefill-only hybrid vs same-model own cluster, scan1..500; new-client capital included where client_basis=new; "
        f"s<1 requires the remaining tasks on an internal large model whose identical common cost cancels; "
        f"GLM prefill slowdown={row['glm_prefill_slowdown'] or 'not applicable'}; s is an input scenario, not equal-quality task evidence.")


def paper_tables(tables):
    selected=[r for r in tables['crossings'] if r['share']==1 and r['billing']=='bought' and
              (r['model']=='qwen' and r['server']=='pro6000_fp8' or r['model']=='glm' and r['glm_prefill_slowdown']==1)]
    return dict(middle_crossings=selected,
        team50=[r for r in tables['middle_cost'] if r['team']==50 and r['billing']=='bought' and r['share']==1 and
                (r['model']=='qwen' and r['server']=='pro6000_fp8' or r['model']=='glm' and r['glm_prefill_slowdown']==1)],
        words_ready=[dict(r,sentence=words(r,next(x for x in tables['middle_cost'] if x['team']==50 and all(x[k]==r[k] for k in ('profile','model','server','client','client_basis','billing','load','share','glm_prefill_slowdown')))))for r in selected],class_map=tables['class_map'],pending_inputs=tables['pending_inputs'])


def report(tables):
    lines=['# Engine run26 — closed contour: hybrid against internal inference','',
        'Parent: run25 `ec28e37c58f49e7109178d1c23334c4c7e0aad38`, Muse r5x9 review pending at start. Run24 `ca7f228a` was accepted. This separate run adds files only; every parent-tracked byte, including run24/run25, is frozen. No inference, native builds, model downloads or pushes. Public source/price pages only.','',
        '## Section8: Closed contour («Закрытый контур»)','',
        'The organization first chooses the model class. Cloud-class2.4T FP8 belongs on an internal multi-node cluster and cannot be offered to the hybrid512GB client. The dense27B middle class can use measured M5 Max64 clients (128GB is same-SoC portability); the320B MoE can be investigated on an EXTRAPOLATED Ultra256/512. The own cluster does both phases; the primary hybrid server does prefill only. All generation exceeding client capacity REFUSES, rather than quietly migrating to the server. Buying a client is charged in full amortization; owned capital is sunk. Own-cluster rows price server hardware only; ordinary terminal/common organizational costs are outside both alternatives.','',
        'At s=1 every model call is internal. At s=.2/.5, the remaining80%/50% is on an INTERNAL large model, whose common cost C is identical in both alternatives. Htotal=Hmiddle+C; Ototal=Omiddle+C; the difference and strict crossings cancel C exactly. The numerical common C shown is a capacity-cost FLOOR, not a service price. Additional large-model service, communication, storage and quality costs are pending, identical symbolic additions in both alternatives. Historical s=.2 with80% to a cloud API was not a closed contour. A task share is an input scenario, not evidence that the middle model solves that share at equal quality. Call price is not price of completed work.','',
        '## Sources and explicit projections','',
        '[Qwen model card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B) specifies2.4T total/95B active,92 layers and512 routed experts/top10+shared. [GLM model card](https://huggingface.co/zai-org/GLM-5.3-Flash) specifies320B/18B; its [config](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/main/config.json) supplies288 routed/top8, one shared,45 layers (34 linear/11 sparse),512-dimensional MLA latent,2048 sparse index cap,1048576 context. Captures/source hashes are in `calc/run26/data/source-index.json`. No model weights were fetched.','',
        '[Apple specifications](https://www.apple.com/mac-studio/specs/) confirm an M5 Ultra with256/512GB and1.2TB/s. [Macworld’s Apple-list-price report](https://www.macworld.com/article/3271691/the-mac-studio-with-512gb-of-ram-is-shipping-and-it-costs-new-car-money.html) gives US$10,799/22,299 for256/512GB,36CPU/80GPU,1TB. These are sourced purchase-cost proxies before tax, not quotes. The official store capture lists the chip/configuration; its static price bootstrap does not expose the configured memory surcharge. MacRumors HTTP403 is recorded, not claimed as a successful second fetch. The obsolete$8,000 Studio estimate is not used.','',
        'Every Ultra timing is UNMEASURED: measure-derived effective M5 Max bandwidth at the same depth = Qwen single-stream tok/s ×(18,973,870,432B weights +34,816B/token×depth +156,893,184B recurrent state), then multiply by2. Divide by the GLM active/expert-union+per-session state traffic. Prefill = measured Max Qwen elapsed time × GLM/Qwen FLOP proxy /2. This is the owner-authorized two-die scaling assumption, not an Ultra benchmark or a claim of perfect observed scaling. GLM B300 prefill = measured Qwen single-B300 elapsed time × FLOP ratio /2; x2 slower sensitivity applies to both GLM alternatives. No GLM kernel, collective, Studio decode/prefill, bridge or B300 prefill measurement exists; rental failed to start. Legacy Studio57min/1M is not a timing anchor.','',
        'GLM FLOP proxy =2×18B +4×11×64×256×min(depth,2048) +4×34×64×128²; Qwen54B+393216×depth. FLOP portability omits routing/indexer/collective overhead. The expert weight partition solves total=A+R and active=A+R×8/288; it is not the older inconsistent shared/routed constants. Q4 residency181.4GB and FP8 allocation328GB are inherited sizing estimates. Client q8_0 MLA =11×512×34/32=5984B/token; server bf16 MLA11264B/token. Estimated fp32 linear+conv state152,633,344B, hypothetical bf16 transport76,316,672B. These layouts, sparse-KV read behavior, conversion and GLM bf16 quality are unmeasured; Qwen’s accepted bf16 quality does not qualify GLM. Whole MLA KV is charged per generated token conservatively, so sparse gather optimization is an open bound.','',
        'GLM twoB300/replica, four replicas/eightGPU paid node, ideal summed2×8TB/s×70% bandwidth, no collective overhead. Native fleet model caps decode at32 streams/replica and finite4×team concurrency, includes tool pauses, retained-copy residency and nonresident cold-rebuild proxy; no new restore measurement is claimed. Qwen PRO decode uses run23 measured surface, B300 decode remains modelled. Measured PR16 Qwen bridge envelope and run16 Mac import are reused for GLM only as UNMEASURED portability. Bought link125MB/s/1ms office; rental112.5MB/s/400ms engine WAN estimate,730h/month, inherited egress/storage. A rented node represents an internal contour only under an approved trust-boundary assumption.','',
        'Coverage: combined10885/39904=27.28%, Claude554/1000=55.40%, shares of fitted/reconstructed CALL SHAPES inside Qwen’s measured ladder, normalized to full declared intensities per person-month, not a quarter of tokens/work. Profiles are aggregate reconstructions, not raw chronological traces. For GLM the same shapes ensure comparison consistency, not measured GLM coverage. Light/medium typical200/800 calls/day, heavy2500/day is the owner’s intensity,21days/month,8h/day. No second Mac.','',
        '## s=100% bought dedicated: crossings through500 and team50','',
        'Costs below USD/person-month; × means no finite prefill-only certificate. Each cost includes its dedicated service occupancy in parentheses. Inherited fleets are sufficient, not globally minimal. Conditional projections are not measured results.','',
        '| Profile | Model/client | Client capital | Load | Sustained from | Team50 hybrid (occupancy) | Team50 own (occupancy) |','|---|---|---|---|---:|---:|---:|']
    paper=paper_tables(tables)
    for r in paper['middle_crossings']:
        sample=next(x for x in paper['team50']if all(x[k]==r[k]for k in ('profile','model','client','client_basis','load','server')))
        def cell(price,util):return f'{price:.2f} ({util:.1%})' if m.finite(price) and m.finite(util) else '×'
        lines.append(f"| {r['profile']} | {r['model']} {r['client']} | {r['client_basis']} | {r['load']} | {r['sustained_from'] or 'none'} | {cell(sample['hybrid_person_month'],sample['hybrid_service_utilization'])} | {cell(sample['own_person_month'],sample['own_service_utilization'])} |")
    lines+=['','`crossings.csv` also gives first wins, exact finite/winning team intervals, both bought/rented, Qwen PRO and B300, both profiles, s=.2/.5/1, both client memories/capital bases and GLM prefill x1/x2. A first integer-fleet step win is not a sustained crossing. `mixed_scheme.csv` gives identical common-large columns, middle difference and conditional capacity-floor totals for teams1/3/5/10/20/50/100/500.','',
        '## Run25 fleet sensitivity','',
        'The PRO queue/storage contract applies to Qwen, not automatically to a two-GPU GLM replica. `fleet_variants.csv` recomputes team50 with64/128GB vectors, owned/new clients, s=.2/.5/1, light/medium/heavy, fixed1/2/4 and first-certified minimum through4T; original900GB NVMe, expanded3.6TB NVMe,3.6TB warmRAM and x2 slower proxies. Every server restore remains UNMEASURED:7GB/s NVMe read/write,50GB/s warm RAM/PCIe; capacities/prices and independent Poisson/M/G/1 mean queue are exactly run25 declarations, including extra$400/$10k capex. Mean queue≤5s and occupancy≤70%, no p95 or peak guarantee. Checkpoint read/write, pending replay, wire/import and local-prefill fallback change TTFT and routing; each is exported. Primary rows additionally refuse server generation overflow. Thus old run25 heavy generation-fallback results cannot be quoted as a prefill-only win. Minimum is within the declared grid, not a runtime optimum. Own reference here retains the inherited own policy, explicitly not paired optimized storage.','',
        '## Cloud-class reference: capacity cost, service pending','',
        'One8×B300 node has2.304TB raw HBM. At90% allocation and8GB workspace/GPU,2.4TB FP8 weights need at least two nodes. The weight-only cost floor omits session storage and task throughput. A separate all-resident-copy scenario holds4copies/person at262144 depth in HBM:23 full layers×2K/V×4heads×256×2B=94208B/token plus estimated69 linear-layer state. Its larger fleet is a declared residency alternative, not a minimum that precludes off-GPU storage. Multi-node interconnect, quantization extras and effective throughput remain pending. No cloud-class hybrid is feasible.','',
        '| Billing | Retention | Team50 capacity cost/person-month | First within declared $1000 budget |','|---|---|---:|---:|']
    for r in tables['cloud_affordability']:
        lines.append(f"| {r['billing']} | {r['retention_basis']} | {r['team50_person_month']:.2f} | {r['first_affordable'] or 'none through500'} |")
    lines+=['','The$1000/person-month threshold is a declared affordability criterion for the hardware capacity floor only. It certifies neither serving the requested load nor price/quality parity with the middle model. It is not an API comparison.','',
        '## MoE hypothesis: compute the bound, do not presume a cost victory','',
        'For E=288, top8, batch B, expected expert union is E[1−(1−8/E)^B]. Single-client decode reads its active experts; batch traffic reads the union plus every session’s own KV/state. `moe_decode.csv` compares the resulting gain with dense Qwen at16k/64k/164k/256k/512k/1M, including large-batch resident limits. Less KV raises the GLM batch cap; weak expert overlap delays weight sharing. Uniform independent routing, full-KV reads, ideal sharding and no communication make this a model, not measured server scaling. Economic verdict must be conditional on both client purchase and GLM portability; smaller KV alone is insufficient.','',
        '## Gates and remaining inputs','',
        'New rules have named negatives with positive controls. Source hashes, all parent files, report and compact outputs are audited. No supplied attack-surface table (brief gap). Runtime GLM/Ultra, cloud-class service, raw-log correlations, parity of completed tasks and trust-boundary certification remain outside the measured contract. See `pending_inputs.csv` and `calc/run26/UNRESOLVED_QUESTIONS.md`. Validation receipts are published separately; no unrun gate is asserted here.']
    return '\n'.join(lines)+'\n'


def refresh_manifest(checks=None):
    sources=sorted([p for p in (ROOT/'calc/run26').rglob('*') if p.is_file()]+list((ROOT/'calc/tests').glob('test_run26*.py')))
    files=sorted([p for p in OUT.rglob('*')if p.is_file() and p.name!='manifest.json']+[REPORT])
    validation=ROOT/'calc/R26-VALIDATION-261105.json'
    if validation.exists():files.append(validation)
    doc=dict(parent=m.config()['parent'],frozen=frozen(),sources={str(p.relative_to(ROOT)):digest(p)for p in sources},
             files={str(p.relative_to(ROOT)):digest(p)for p in files},csv_bytes=sum(p.stat().st_size for p in files if p.suffix=='.csv'))
    if doc['csv_bytes']>=m.config()['output_limit_bytes']:raise AssertionError('summary CSVs >=50MB')
    write(OUT/'manifest.json',(json.dumps(doc,indent=2)+'\n').encode(),checks if checks is not None else [])
    return doc


def audit():
    doc=json.loads((OUT/'manifest.json').read_text())
    current={name:digest(ROOT/name)for name in doc['sources']}
    if history.accepted_identity('397432dd',current)!=doc['sources']:raise AssertionError('original source identity changed')
    for name,value in doc['files'].items():
        if digest(ROOT/name)!=value:raise AssertionError('manifest hash mismatch '+name)
    if frozen()!=doc['frozen']:raise AssertionError('parent manifest mismatch')
    if doc['csv_bytes']>=50_000_000:raise AssertionError('too much CSV')
    for p in OUT.rglob('*.csv'):
        for r in csv.DictReader(p.open()):
            if 'rtx5090' in r.get('server','').lower():raise AssertionError('excluded5090 server')
            if r.get('model')=='glm' and 'rate_basis'in r and 'UNMEASURED'not in r['rate_basis']:raise AssertionError('unlabelled GLM projection')
            if r.get('hybrid_status')=='feasible_prefill_only' and float(r.get('server_decode_overflow_day') or 0)>1e-9:raise AssertionError('hybrid generation overflow')
    return dict(status='pass',**doc['frozen'],csv_bytes=doc['csv_bytes'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--audit-only',action='store_true');parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    if args.audit_only:print(json.dumps(audit()));return
    if args.refresh:refresh_manifest();print(json.dumps(audit()));return
    frozen();checks=[]
    # Checkpoint only completed stages, bound to every parent byte and all new
    # mathematical sources/data. A resource retry never reuses a foreign model.
    signature=hashlib.sha256(''.join(digest(p)for p in sorted((ROOT/'calc/run26').rglob('*'))if p.is_file() and p.name not in ('export.py','finish.py','README.md','UNRESOLVED_QUESTIONS.md')).encode()).hexdigest()
    cache=Path(os.environ.get('TMPDIR',ROOT/'.temp/hybrid-e-r21b-261105/tmp')).parent/'calculation-checkpoint.json'
    cached=json.loads(cache.read_text())if cache.exists()else None
    resume=cached['state']if cached and cached.get('signature')==signature else None
    def checkpoint(state):
        write(cache,(json.dumps(dict(signature=signature,state=state),allow_nan=False,separators=(',',':'))+'\n').encode(),checks)
    tables=engine.calculate(resume,checkpoint)
    for name,rows in tables.items():write(OUT/(name+'.csv'),csv_bytes(rows),checks)
    for name,rows in paper_tables(tables).items():write(OUT/'paper'/(name+'.csv'),csv_bytes(rows),checks)
    write(REPORT,report(tables).encode(),checks)
    write(OUT/'write-audit.json',(json.dumps(checks,indent=2)+'\n').encode(),[])
    refresh_manifest();print(json.dumps(audit()))

if __name__=='__main__':main()
