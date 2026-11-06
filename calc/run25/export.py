"""Bounded new artifacts only, with disk pre/post checks and frozen-parent audit."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'calc'))
from run25 import engine, model

OUT = ROOT/'calc/out/run25'
REPORT = ROOT/'calc/ENGINE-REPORT-R25-261105.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


import history_evidence as history


def frozen():
    """Retain original parent evidence and require each explicit paper migration."""
    parent=model.config()['parent']
    names=history.verify_engine_parent(parent)
    return dict(parent=parent,parent_tracked_files=len(names),historical_output_files=sum(n.startswith('calc/out/')for n in names),all_parent_bytes_identical=True)


def write(path,raw,checks):
    floor = model.config()['free_floor_bytes']; path.parent.mkdir(parents=True,exist_ok=True)
    before = shutil.disk_usage(ROOT).free
    # Leave room for the entire new artifact, plus metadata. No shared cleanup.
    if before-len(raw)-1024*1024 < floor:
        raise RuntimeError('disk floor: refusing output write '+str(path))
    df_before = subprocess.check_output(['df','-BG',str(ROOT)],text=True)
    temporary = path.with_name(path.name+'.r25-tmp')
    with temporary.open('wb') as f:
        f.write(raw)
    temporary.replace(path)
    after = shutil.disk_usage(ROOT).free
    df_after = subprocess.check_output(['df','-BG',str(ROOT)],text=True)
    checks.append(dict(path=str(path.relative_to(ROOT)),bytes=len(raw),free_before=before,free_after=after,df_before=df_before,df_after=df_after))
    if after < floor:
        raise RuntimeError('disk floor crossed during output write; stopping')


def csv_bytes(rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    f = io.StringIO(newline=''); writer = csv.DictWriter(f,fields,lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k:('' if v is None else v) for k,v in row.items()})
    return f.getvalue().encode()


def report(tables):
    out = ['# Engine run25 — dedicated fleets, closed contour and coverage',
        '', 'Parent: accepted run24 `ca7f228a` (Muse r5x6 ACCEPT). Separate sensitivity; every accepted parent-tracked byte, including run24, stays unchanged. No GPU/CPU inference, downloads or API requests.',
        '', '## Why the accepted fleet has four nodes',
        '', 'The lower bound is retained-session STORAGE, not peak concurrency: `calc/hybridcalc/measurements_r20.py:99` (`storage_boxes`), called before compute sizing at `:181` (`hybrid`). Run23 uses this inherited code through `calc/run22/economics.py:108`. The249k reservation comes from `calc/hybridcalc/measurements_r21.py:77` and `calc/run23/engine.py:96`.',
        '', 'PRO default KV is65,536B/token and recurrent resident state156,893,184B: a249,000-token copy is16,475,357,184B. Of96GB VRAM,27GB weights and8GB workspace leave61GB, admitting3 reserved GPU copies (measured decode surface also caps residency). Per-node900GB NVMe holds floor(900e9/16,475,357,184)=54 copies. Four sessions/person ×50people=200 copies; ceil(200/(54+3))=4 nodes. At4 nodes12/200 copies are resident, giving94% expected misses. The subsequent compute test does not add a light-load node. Claudedeep still pays for200 copies even when routing offloads zero calls.',
        '', 'The accepted $56.6446/person-month =4×$614.0575/50+$2.52 client energy+$5 front. Light service occupancy3.61399% is an allocated-service model output, not a measured GPU-utilization trace. The accepted fleet is sufficient; minimality across alternative retention policies was never established.',
        '', '## Explicit unmeasured proxies and admission',
        '', 'All sensitivity checkpoints live OFF GPU. Every catch-up reads a full server-format copy, replays the existing expected pending work, and writes a full updated checkpoint. Client bf16 wire remains78,446,592B recurrent state plus34,816B/delta token; it does not halve the server checkpoint. No cold-prefix rebuild is charged in addition to restore. State serialization/conversion metadata overhead beyond byte IO is assumed zero, unmeasured; ×2 IO sensitivity does not calibrate that overhead. No runtime vLLM slot-restore implementation is claimed.',
        '', 'Inherited NVMe:900GB usable/node,256GB host RAM declared but no cache credited. Expanded NVMe:3.6TB usable/node,256GB RAM, extra$400 capex/node. Warm RAM:3.6TB usable RAM/node,900GB NVMe not counted for warm capacity, extra$10,000 capex/node; volatile, no cold persistence guarantee. Expansion prices are declared scenarios, not sourced offers or hardware recommendations. They use the accepted residual/depreciation/support formula. The NEW fleet policy is bought-office only; rental rows in the closed-contour control retain the accepted run24 engine and egress accounting. The new office proxy refuses rental billing.',
        '', 'NVMe read/write7GB/s uses the existing declared tier bandwidth; RAM50GB/s is min(100GB/s RAM,50GB/s PCIe). Both are UNMEASURED server restore proxies, with×2 slower read AND write. The actual Mac/LaCie reference (`calc/run23/data/MAC-FACTS.md`) is18.425GB/20.523s first and2.965s warm at524k;36.4GB/about40.5s at1.04M, warm/no purge. Those timings are context, not server measurements or server conversion calibration.',
        '', 'Accepted routing treats calls as exchangeable Bernoulli opportunities (`calc/hybridcalc/session_hosting.py:15`); no ordered arrival process was delivered. Here independent homogeneous Poisson arrivals are an UNMEASURED proxy at accepted calls/day over8h, randomly split across nodes. Per-node M/G/1 mean delay is λE[S²]/(2(1−ρ)); collisions are charged. Restore, catch-up, response wire and checkpoint write reserve the node sequentially. Overflow generation uses the accepted depth-dependent measured PRO batch surface/finite4T concurrency as equivalent service work; that queue surrogate does not reproduce the real batching scheduler or its latency distribution. Tool/session occupancy is retained in the equivalent overflow work.',
        '', 'For each fleet we test queue budgets0,.05,.1,.25,.5,1,2,3,4,5seconds, rerun the greatest-stable offload policy with restore+charged queue+pending catch-up, and recompute client capacity/overflow and service moments. A row is certified only if actual modelled mean queue ≤charged budget and service occupancy≤70%. Minimum means the first integer fleet certified on this declared queue grid, not a hardware/runtime optimum. Storage/latency/compute shortfalls have no finite cost or ratio. Mean TTFT covers local and offloaded client-served calls; the offload mean includes client import, link and pending. Overflow uses a workload proxy, so its request TTFT and latency tails remain unqualified. No peak-arrival or p95 guarantee is inferred.',
        '', 'When the offload queue cannot certify, the policy explicitly tries LOCAL PREFILL, retaining all required copies and charging any generation exceeding Mac capacity to the server. This can make a smaller fleet feasible with zero prefill offload; it is a retention/local-compute alternative, not an offload speedup. Overflow also catches up the deferred local journal. With no offloads, expected local replay work per overflow refresh is capped by the full existing-prefix cold-work bound; with positive offload share the existing offload-only pending bound is also charged to overflow conservatively. Full-depth copy bytes reserve an upper bound for an older checkpoint; no fresh checkpoint or free replay is invented.',
        '', 'The overflow TTFT column is an UNMEASURED surrogate: mean restore+cached prefill+journal+charged node queue+link RTT, with no client state import. The all-call TTFT combines this with client-served TTFT by their actual served/overflow counts. It is not a measured batching scheduler latency. The latency table keeps the client-only and all-call means separate.',
        '', '## Team50 fleet costs and latency',
        '', 'All following prices are per person-month, owned M5 Max64 PRI31, bf16-default transport, bought PRO vLLM node over office125MB/s, RTT1ms. Light/medium are typical; heavy2500calls/day is the owner’s intensity. s=.2 prices only the open-model segment (80% still goes to a stronger cloud model); s=1 sends every model call in-house. These are normalized selected-shape scenarios, never full-log performance claims.',
        '', 'Cost cells show USD/person-month and node service occupancy together. Shortfall cells have no finite cost.',
        '', '| Profile | s | Restore proxy | Fleet | Light $ / occupancy | Medium $ / occupancy | Heavy $ / occupancy | Heavy nodes if minimum |',
        '|---|---:|---|---|---:|---:|---:|---:|']
    rows = [r for r in tables['fleet_summary'] if r['weighting']=='accepted_shapes' and r['billing']=='bought']
    def amount(row):
        return f"{row['person_month']:.3f} / {row['service_utilization']:.2%}" if isinstance(row['person_month'],(int,float)) else row['status']
    for profile in ('existing_combined','claude_deep'):
        for share in (.2,1.):
            for case in ('inherited_nvme','expanded_nvme','all_ram_warm'):
                for slow in (1,2):
                    for policy in ('1','2','4','minimum'):
                        group = {r['load']:r for r in rows if r['profile']==profile and r['share']==share and r['storage_case']==case and r['restore_slowdown']==slow and r['fleet_policy']==policy}
                        out.append('| {} | {} | {} ×{} | {} | {} | {} | {} | {} |'.format(profile,share,case,slow,policy,*(amount(group[x]) for x in ('light','medium','heavy')),group['heavy']['nodes'] if policy=='minimum' else ''))
    out += ['', '## Closed contour on the accepted dedicated basis', '',
        's=20% thresholds describe a segment: the other80% goes to a stronger cloud model. They cannot substantiate an all-in-house closed contour. Only s=100% rows below make every call open-model/in-house. Own cluster uses the same PRO6000 engine and billing as its hybrid alternative. This is the inherited no-queue fleet control; the alternative off-GPU policies and mean delays are separate in `crossings.csv`.', '',
        '| Profile | s | Billing / link | Load | Hybrid $ / service occupancy at50 | Own $ / service occupancy at50 | Sustained hybrid win through500 |',
        '|---|---:|---|---|---:|---:|---|']
    for r in tables['closed_contour']:
        def priced(key,utilkey):
            value=r[key];util=r.get(utilkey,'')
            return f'{value:.3f} / {util:.2%}' if isinstance(value,(int,float)) and isinstance(util,(int,float)) else 'capacity shortfall' if not isinstance(value,(int,float)) else str(value)+' / pending publication metadata'
        out.append('| {} | {} | {} / {} | {} | {} | {} | {} |'.format(r['profile'],r['share'],r['billing'],r['link'],r['load'],priced('team50_hybrid','team50_service_utilization'),priced('team50_own_cluster','team50_own_service_utilization'),r['statement']))
    out += ['', '## Coverage and representativeness', '',
        'The owner package explicitly excludes raw per-call CSV, transcripts and timestamps (`data/measurements/ivmbp-2026-10-30/README.md`, `REPORT.md`). Exact joint observed subset input/output/work shares cannot be recomputed from marginal aggregates. The accepted10,885/39,904(27.28%) is a share of fitted CALL SHAPES, normalized to declared intensity, not a measured share of total work or tokens. Claudedeep is a1000-point aggregate reconstruction. Blank observed-share columns mean unknown; fitted estimates below are not promoted to measured log fractions.', '',
        '| Fitted profile | Shape share | Full-input token share | New-token share | Output-token share | Prefill seconds share | Decode seconds share | Work seconds share |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in tables['coverage']:
        out.append('| {} | {} |'.format(r['profile'],' | '.join(f'{r[k]:.2%}' for k in ('fitted_call_shape_share','fitted_input_token_share','fitted_new_token_share','fitted_output_token_share','fitted_prefill_seconds_share','fitted_decode_seconds_share','fitted_work_seconds_share'))))
    out += ['', 'Work proxy =M5 measured-anchor prefill seconds +single-stream decode seconds, excluding tool pauses. Outside the measured ladder it uses the accepted depth/delta extrapolation, so the full-profile denominator is modelled. No exact measured-only full-work fraction is available. The code records any context clipping; clipped shapes are never admitted as valid hardware requests.', '',
        'The representativeness sensitivity reweights the measured shapes by maximum entropy to match the FULL FITTED profile’s mean NEW and OUTPUT tokens, reprices each API provider and reranks it, and recalculates hybrid/own-server work using the same weights. It preserves the measured shape envelope, but does not recover deep input-context distributions, correlations or real arrivals. The deep full mean input exceeds the measured subset’s attainable range; it cannot be fixed by honest in-envelope reweighting. Results are conditional stress tests, not a full-log correction.', '',
        '| Profile | s | Load | Expanded NVMe speed | Accepted-shape minimum win vs own | Reweighted minimum win vs own | Reweighted $ at50 | Reweighted offload at50 |',
        '|---|---:|---|---:|---|---|---:|---:|']
    for r in tables['crossings']:
        if not (r['reference']=='own_cluster' and r['billing']=='bought' and r['weighting']=='full_delta_output_mix' and r['storage_case']=='expanded_nvme' and r['restore_slowdown']==1 and r['fleet_policy']=='minimum'):
            continue
        before = next(x for x in tables['crossings'] if all(x[k]==r[k] for k in ('profile','share','load','billing','reference','storage_case','restore_slowdown','fleet_policy')) and x['weighting']=='accepted_shapes')
        row = next(x for x in tables['fleet_summary'] if all(x[k]==r[k] for k in ('profile','share','load','billing','weighting','storage_case','restore_slowdown','fleet_policy')))
        cost=f"{row['person_month']:.3f} / {row['service_utilization']:.2%}" if isinstance(row['person_month'],(int,float)) else row['status']
        out.append('| {} | {} | {} | 1 | {} | {} | {} | {} |'.format(r['profile'],r['share'],r['load'],before['statement'],r['statement'],cost,row.get('offload_share','')))
    out += ['', '## Reading the compact outputs', '',
        '`fleet_summary.csv` carries capacity, shortfalls, charged/actual mean queue, restore/read/write, TTFT, utilization, offload and client/overflow capacity. `comparisons.csv` reports own/API ratios at50 for BOTH v1-long-pause and amendment-core cadence, no-cache/owner98.1%/measured points; Qwen core measured remains unknown. Thin final-study points remain descriptive, especially the one-warm-call Qwen v1 cheapest point. `crossings.csv` scans every integer1..500: fixed fleets can win on intervals then fail storage, so first win is not mislabelled a sustained crossing. Every case includes1/2/4 nodes and the first certified minimum. `closed_contour.csv` preserves the accepted fleet control at both shares. Coverage, reweighting and per-depth full-copy sizes are separate small CSVs. No full quote dump is generated.', '',
        'API references retain the accepted run24 whole-window admission, cadence and aggregate-token price formula, including unknown core measured Qwen. Reweighted API prices assume the same cache fractions and live tariffs transfer to the altered token mix. Comparisons of the open-model segment do not price the stronger-cloud remainder. The API is only a reference for closed-contour teams, which cannot use it.', '',
        'Dedicated paid storage is retained even for zero offloads; such rows may be cheaper solely because fewer boxes retain copies. They do not demonstrate useful prefill offload. Light-load one-node costs require the declared expanded capacity; one inherited900GB node REFUSES. The warm3.6TB RAM configuration and its capex are hypothetical. Failure of the assumed runtime checkpoint restore/serialization, hardware attachment, arrivals or latency policy invalidates that sensitivity, without changing accepted run24.', '',
        'Validation receipts and source/file hashes are in `calc/out/run25/manifest.json`; executable paired negatives cover storage/latency rejection, queue instability, checkpoint writeback, pending catch-up, token reweighting, refusal-sensitive crossings and unchanged uniform-weight own-cluster controls. No independent run25 acceptance is claimed.']
    return '\n'.join(out)+'\n'


def audit():
    frozen_result = frozen()
    doc = json.loads((OUT/'manifest.json').read_text())
    assert doc['frozen']==frozen_result
    total = 0
    for name,digest in doc['files'].items():
        assert sha((ROOT/name).read_bytes())==digest,name
        if name.endswith('.csv'):
            total += (ROOT/name).stat().st_size
    assert total < model.config()['output_limit_bytes']
    rows = engine.read('calc/out/run25/fleet_summary.csv')
    for row in rows:
        if row['status']=='feasible':
            assert float(row['person_month'])>0 and row['feasible']=='True'
            assert int(row['storage_shortfall_copies'])==0
            assert float(row['actual_mean_queue_s']) <= float(row['charged_mean_queue_s'])+1e-12
            assert float(row['charged_mean_queue_s'])<=model.config()['max_mean_queue_s']
            assert float(row['service_utilization'])<=model.config()['max_service_occupancy']
        else:
            assert row['person_month']=='' and row['feasible']=='False'
    assert {'accepted_shapes','full_delta_output_mix'}=={r['weighting'] for r in rows}
    print(json.dumps(dict(frozen_result,csv_bytes=total,files=len(doc['files']),summary_rows=len(rows))))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--audit-only',action='store_true'); args = parser.parse_args()
    if args.audit_only:
        return audit()
    before = frozen(); checks = []; tables = engine.calculate()
    payloads = {OUT/(k+'.csv'):csv_bytes(v) for k,v in tables.items()}
    assert sum(len(x) for x in payloads.values())<model.config()['output_limit_bytes']
    payloads[REPORT] = report(tables).encode()
    for path,data in payloads.items():
        write(path,data,checks)
    assert frozen()==before
    sources = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted((ROOT/'calc/run25').glob('*')) if p.is_file()}
    sources['calc/tests/test_run25.py'] = sha((ROOT/'calc/tests/test_run25.py').read_bytes())
    doc = dict(frozen=before,sources=sources,files={str(p.relative_to(ROOT)):sha(v) for p,v in payloads.items()},
        csv_bytes=sum(len(v) for p,v in payloads.items() if p.suffix=='.csv'),disk_writes=checks,
        provenance=dict(config='calc/run25/config.json',stats='data/measurements/ivmbp-2026-10-30/stats.json',
                        log_limits='data/measurements/ivmbp-2026-10-30/REPORT.md',restore_context='calc/run23/data/MAC-FACTS.md'),
        gates='see calc/R25-VALIDATION-261105.json for actual standalone test receipts; producer output alone is not independent acceptance')
    write(OUT/'manifest.json',(json.dumps(doc,indent=2,sort_keys=True,allow_nan=False)+'\n').encode(),checks)
    audit()


if __name__=='__main__':
    main()
