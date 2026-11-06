"""Run23 report publication; numerical exports and historical artifacts immutable."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'calc'))
from run23.export import OUT,verify as verify_engine
from run23 import changes

REPORT=ROOT/'calc/ENGINE-REPORT-R23-261104.md'
QUOTES=ROOT/'calc/ENGINE-REPORT-QUOTES-R23-261104.csv'
VALIDATION=ROOT/'calc/R23-VALIDATION-261104.json'
MANIFEST=ROOT/'calc/R23-REPORT-MANIFEST-261104.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build(directory=OUT):
    cache={};records=[]
    def rows(name,old=False):
        key=name,old
        if key not in cache:
            path=(changes.OLD if old else directory)/name
            cache[key]=list(csv.DictReader(io.StringIO(path.read_text())))
        return cache[key]
    def match(name,old=False,**conditions):
        found=[(i,r)for i,r in enumerate(rows(name,old))if all(r.get(k)==str(v)for k,v in conditions.items())]
        assert len(found)==1,(name,conditions,len(found))
        return found[0]
    def q(name,index,column,fmt=None,old=False):
        raw=rows(name,old)[index][column];rendered=raw
        if raw=='nan':rendered='capacity refusal'
        elif raw=='':rendered='—'
        elif fmt is not None:rendered=fmt(float(raw))
        elif column in ('sentence','short_sentence'):rendered=raw.rstrip()
        records.append(dict(site='report quote '+str(len(records)+1),source='calc/out/'+('run22/'if old else'run23/')+name,
            row=index,column=column,source_value=raw,rendered=rendered))
        return rendered
    money=lambda x:format(x,'.2f')
    three=lambda x:format(x,'.3f')
    pct=lambda x:format(100*x,'.2f')+'%'
    lines=['# Engine run23 — the night’s measured inputs', '',
        'Base: accepted run22 `9053089eb54fcbdf1e39efba9e5fc6b9de42d1b0` (Muse r5x4 ACCEPT). Historical run13–22 exports and their generators remain byte-identical. This successor retains bf16 transport by default, f32 control/resident state, dedicated bought/rented primary economics, the API cache/window bounds and the same workload shapes.', '',
        'The r5x4 notes are carried forward: M3 Max threshold results are explicitly named; economics clients remain M5 Max, not the owner’s M3; zero-prefill-offload crossings disclose local work plus residency/overflow rather than claim an offload gain. Bought-server assumptions are restated below. The old brief’s idleness example is superseded by the measured-basis tables, not reused as a target.', '',
        '## Direct Mac measurements and their gate', '',
        'Owner’s **M3 Max 128 GB, normal priority**, kit 1.6.12 step 56, model internal, slots/references on an **external LaCie SSD**, **warm/no purge**. Each shape has one excluded warm-up and three timed rounds; prefill medians exclude restore. Decode is 255 steps after the seed. These are native measurements, not end-to-end hybrid TTFT.', '',
        'The first attempt at 524288 refused at raw-logit bound 1.0 (max difference 1.08298), before any decode/delta/1040000 child. The later accepted timing run used bound 4.0; it was raised after that refusal and is **not calibrated**. At 524288 max KL/mean KL=0.0017539/0.00032912, top1=64/64; at 1040000=0.0021309/0.00032571, top1=63/64 and max raw difference 3.01402. All 30 native children stayed inside the pageout guard; swapouts 0. Neither attempt is hidden.', '',
        '| Actual depth | Delta | Prefill s, restore excluded | First-probe restore s | Timed warm restore median s | Decode tok/s | Status |',
        '|---:|---:|---:|---:|---:|---:|---|']
    for i,r in enumerate(rows('mac_direct_measurements.csv')):
        lines.append('| '+' | '.join([q('mac_direct_measurements.csv',i,k,three if k.endswith('_s')or k=='decode_tok_s'else None)for k in ('depth','delta','prefill_s','restore_first_s','restore_warm_s','decode_tok_s','measurement_status')])+' |')
    lines+=['', 'At 524288 the later 18.4 GB restores benefit from OS caching; at 1040000 the 36.4 GB file does not remain cached beside wired model/KV. “First” is not a purged cold measurement. The 1040000+10000 shape stays refused: 1050000 exceeds 1048576. FACTS is the accepted source for the rounded Mac medians; the strict archive (1069117 B, abbreviated SHA 90723f8c…be43) remains with the incident lane, and this checkout does not claim full archive re-verification.', '',
        '## M3 Max million-context routing', '',
        'Qwen, Delta 690, B300 FP8 with FP8 KV, historical home Wi-Fi 5.19 MB/s, RTT 126 ms. The main rows use the measured 1040000 local prefill and timed warm full-slot restore. As instructed, the restore is charged **once per offload as a conservative recovery proxy**, while wire bytes remain the modelled bf16/f32 delta payload. This is **not a measured delta import or a measured complete hybrid path**. B300 prefill and its deep bridge envelope remain extrapolated. The 1000000 comparison explicitly uses the 1040000 observation as a proxy; the direct observation is never renamed a measured 1000000 turn.', '',
        'Recovery uses the supplied restore-before-decode median for each delta shape; per-delta restore medians are not available in this checkout. This is a charged recovery proxy, not a measured delta import. The Delta690 headline is accompanied by the measured Delta2000 case and the Delta10000 context refusal.', '',
        '| Scenario depth / delta / local basis | Transport | Actual Mac observation depth | Local prefill s | Recovery charged s | Threshold MB/s | Offload |',
        '|---|---|---:|---:|---:|---:|---|']
    for depth,delta,variant in ((1040000,690,'direct measured'),(1040000,2000,'direct measured'),(1040000,10000,'direct measured'),(1000000,690,'measured1.04M'),(1000000,690,'analyst')):
        for transport in ('bf16','f32'):
            found=[(i,r)for i,r in enumerate(rows('link_thresholds.csv'))if r['model']=='qwen'and r['server']=='b300_fp8_kv'and r['client']=='m3max'and r['depth']==str(depth)and r['delta']==str(delta)and r['transport']==transport and float(r['bytes_s'])==5190000 and r['rate_basis'].startswith(variant)]
            assert len(found)==1,(depth,transport,variant)
            i,r=found[0]
            lines.append('| '+str(depth)+' / '+str(delta)+' / '+('earlier 120s sensitivity'if variant=='analyst'else'context refusal'if delta==10000 else'direct'if depth==1040000 else'explicit 1.04M proxy')+' | '+transport+' | '+q('link_thresholds.csv',i,'measurement_depth')+' | '+q('link_thresholds.csv',i,'local_prefill_s',three)+' | '+q('link_thresholds.csv',i,'recovery_s',three)+' | '+q('link_thresholds.csv',i,'threshold_MB_s',three)+' | '+q('link_thresholds.csv',i,'offload')+' |')
    lines+=['', '| Link profile at actual 1040000 / Delta690 | MB/s | RTT s | bf16 remote s / offload | f32 remote s / offload |', '|---|---:|---:|---:|---:|']
    for link in ('historical_home_wifi','historical_5g','today_wifi','today_wan','fullslot_e2e'):
        conditions=dict(model='qwen',server='b300_fp8_kv',client='m3max',depth=1040000,delta=690,link=link,primary=True)
        bi,_=match('link_thresholds.csv',**conditions,transport='bf16')
        fi,_=match('link_thresholds.csv',**conditions,transport='f32')
        lines.append('| '+link+' | '+q('link_thresholds.csv',bi,'bytes_s',lambda x:format(x/1e6,'.2f'))+' | '+q('link_thresholds.csv',bi,'rtt_s',three)+' | '+q('link_thresholds.csv',bi,'remote_s',three)+' / '+q('link_thresholds.csv',bi,'offload')+' | '+q('link_thresholds.csv',fi,'remote_s',three)+' / '+q('link_thresholds.csv',fi,'offload')+' |')
    lines+=['', 'The analyst’s earlier 120s local turn remains a sensitivity beside the measured basis, using the same newly charged recovery. At 512k, first versus timed-warm restores have separate routing rows. All measured-link profiles and both transport arms are exported. M5 Max deep local/import estimates remain explicitly estimated; no M3 measurement is ported into M5 economics. The normal-priority M3 decode 1.6638 tok/s replaces the earlier background-priority 1.67 in the ceiling comparison; the actual measurement depth stays 1040000.', '',
        '## PRO6000 vLLM decode now drives the economics', '',
        'Kit 1.6.11 `cd85a194`, Muse r7at ACCEPT; private independent contexts, 256 generated tokens, three-round medians over the common decode interval. Timing granularity is SSE chunk receipt with exact token IDs in each chunk. The local GPU archive SHA256 8a58f122af021136721e720232a6cc4c081ed3674391bdf13714e6d63d24efe0 was verified. Raw-source hashes, round aggregates and capacity searches are retained in the compact receipt.', '',
        '| Actual depth | Streams | Largest resident | Aggregate tok/s | Gain |', '|---:|---:|---:|---:|---:|---:|']
    for i,r in enumerate(rows('server_decode_measured.csv')):
        lines.append('| '+' | '.join(q('server_decode_measured.csv',i,k,three if k in ('aggregate_tok_s','gain')else None)for k in ('depth','streams','resident_limit','aggregate_tok_s','gain'))+' |')
    lines+=['', 'Exact observed depth/count points return the measured value. Other batches interpolate seconds per sequence-token. Between depths the same fraction of the admitted resident batch is used, with linear service-time interpolation. Capacity interpolates reciprocal resident count (space/session), rounds down, and is also bounded by physical memory. Those intermediate points are assumptions calibrated to measurements, not additional measurements. Unlike run22’s lone 16k point, the surface applies automatically to every supported workload shape. Below 16384 / above 256000 remain modelled; B300 decode remains modelled because its rental failed to start at 2026-11-04 00:36Z.', '',
        '**PRO vLLM at 1M is impossible:** default KV required 61.97 GiB versus 56.62 GiB available; FP8 KV is unavailable on SM 12.0. Routing rows have no finite remote time/threshold; decode rows are capacity refusals. The historical llama.cpp Q4/q8 slot builder remains artifact-construction context only, explicitly not a feasible current vLLM 1M server scenario.', '',
        'Bridge component medians are exported as context: the source is loopback with a CUDA client. There is no separate non-overlapping export/conversion term, and its CUDA import cannot replace Metal recovery. The reviewed aggregate bridge envelope is retained; phases are not added twice.', '',
        '## Dedicated PRO6000 costs and fleet changes', '',
        'Selection: bought PRO6000 vLLM FP8, office 125 MB/s RTT 1 ms assumed; owned PRI31 M5 Max 64 GB, s=20%, bf16; owner 98.1% aggregate cache allowance (1.9% misses billed, provider behaviour unverified). Economics compare the same selected measured call shapes, normalized per person-month; this is the open-model cost component, not the full unconditioned source workload. Light/medium are typical; heavy 2500 calls/day is the owner’s intensity.', '',
        'Inherited cost assumptions, not new price observations: bought PRO box capex $30000, 20% residual over 4 years, 2% annual support; 0.9 kW x PUE 1.3 x730h x office load 0.5 x $0.15/kWh, no office colo, giving $614.0575/box-month. Rental remains the engine’s $2.20/h x730=$1606/month, WAN 112.5 MB/s RTT 400 ms, egress $5/decimal TB and separate storage. Owned client energy $2.52/month plus $5 front; buying an M5 Max 64 instead adds $69.05/month. Fleets are sufficient, not proved minimal. Service utilization includes allocated-GPU tool/concurrency occupancy, not hardware SM telemetry.', '',
        '| Profile / load, 50 people | Own cluster old $ / new $ | Own boxes old / new | Own service/calendar old to new | Hybrid new $ | Hybrid service / calendar | Median API / hybrid old / new |',
        '|---|---:|---:|---:|---:|---:|---:|']
    common=dict(scope_tier='measured_ladder',transport='bf16',share=.2,client='m5max64',basis='owned',server='pro6000_fp8',billing='bought')
    for profile in ('existing_combined','claude_deep'):
        for load in ('light','medium','heavy'):
            args=dict(common,profile=profile,load=load,team=50)
            ni,n=match('main_economics.csv',**args);oi,o=match('main_economics.csv',True,**args)
            mi,_=match('dedicated_multiples.csv',**args);mo,_=match('dedicated_multiples.csv',True,**args)
            lines.append('| '+profile+' / '+load+' | '+q('main_economics.csv',oi,'own_cluster_person_month',money,True)+' / '+q('main_economics.csv',ni,'own_cluster_person_month',money)+' | '+q('main_economics.csv',oi,'own_cluster_boxes',None,True)+' / '+q('main_economics.csv',ni,'own_cluster_boxes')+' | '+q('main_economics.csv',oi,'own_service_utilization',pct,True)+' / '+q('main_economics.csv',oi,'own_calendar_utilization',pct,True)+' → '+q('main_economics.csv',ni,'own_service_utilization',pct)+' / '+q('main_economics.csv',ni,'own_calendar_utilization',pct)+' | '+q('main_economics.csv',ni,'person_month',money)+' | '+q('main_economics.csv',ni,'service_utilization',pct)+' / '+q('main_economics.csv',ni,'calendar_utilization',pct)+' | '+q('dedicated_multiples.csv',mo,'api_median_over_hybrid',three,True)+' / '+q('dedicated_multiples.csv',mi,'api_median_over_hybrid',three)+' |')
    lines+=['', 'The Claude measured-shape rows with zero prefill offload price local client work plus residency/any generation overflow. Their crossings are not evidence of an offload gain. The sentence forms state that explicitly. API admission, workload profiles and measured-shape coverage exports are byte-identical to run22. Coverage means the share of calls whose shapes lie inside the measured ladder, normalized to the row’s calls/person-month; it is not a fraction of total work. Physical-envelope fractions use deep estimates. No provider cache measurement has arrived; no-cache, owner 98.1% and measured/pending remain separate.', '',
        '| Heavy sensitivity: generation on own PRO server, 50 people | Old $/person-month | New $/person-month | Old service/calendar | New service/calendar |', '|---|---:|---:|---:|---:|']
    for ni,n in enumerate(rows('heavy_sensitivity.csv')):
        oi,o=match('heavy_sensitivity.csv',True,profile=n['profile'])
        lines.append('| '+n['profile']+' | '+q('heavy_sensitivity.csv',oi,'move_generation_person_month',money,True)+' | '+q('heavy_sensitivity.csv',ni,'move_generation_person_month',money)+' | '+q('heavy_sensitivity.csv',oi,'service_utilization',pct,True)+' / '+q('heavy_sensitivity.csv',oi,'calendar_utilization',pct,True)+' | '+q('heavy_sensitivity.csv',ni,'service_utilization',pct)+' / '+q('heavy_sensitivity.csv',ni,'calendar_utilization',pct)+' |')
    lines+=['', 'All small-team/share/load/billing/client rows and shared-provider bounds are exported. The shared resident-work allocation remains a supplementary utilization limit; it is not substituted for a dedicated comparator. Night agents may raise utilization. The withdrawn universal heavy-load claim was lost after recalculation on vLLM; it held only for the owner-excluded 5090 hybrid, not because of a second Mac.', '',
        '## Words-ready conclusions', '', 'These are generated short forms; each has its canonical, row-bound counterpart in the paper exports. Cache allowance, link, billing, client, s, load, coverage, transport and measured/modelled decode basis travel with every sentence.', '']
    for profile in ('existing_combined','claude_deep'):
        for load in ('light','medium','heavy'):
            for ref in ('own_cluster','api_median_owner_981','api_cheapest_owner_981'):
                i,r=match('paper/team_break_even.csv',**dict(common,profile=profile,load=load,reference=ref))
                lines.append('- '+q('paper/team_break_even.csv',i,'short_sentence'))
    i,r=match('paper/team_break_even.csv',**dict(common,profile='claude_deep',load='light',billing='rented',reference='own_cluster'))
    lines+=['', 'The measured-shape rental crossing changes; the zero-prefill-offload condition is material:', '', '- '+q('paper/team_break_even.csv',i,'short_sentence')]
    lines+=['', '## Changed against run22: every abstract-bound coordinate', '',
        'The table below includes unchanged numbers too. It covers every numeric coordinate quoted by the accepted run22 report, its prose local/recovery/decode inputs, primary fleet counts and sustained crossing statements. Full semantic row keys, both row indices, exact unrounded values, absolute/percentage deltas and reasons are in `abstract_bound_changes.csv`. These audit addresses are not standalone paper quotations; use the condition-complete sentences above. Every common-coordinate numeric/verdict change across the full matrices is separately in `changed_against_run22.csv`; added/removed rows are counted in `change_summary.csv`.', '',
        '| Table: old row to new row / column | Old | New | Why |', '|---|---|---|---|']
    for i,r in enumerate(rows('abstract_bound_changes.csv')):
        label=r['table']+':'+r['old_row']+'→'+r['new_row']+' / '+r['column']
        lines.append('| '+label+' | '+q('abstract_bound_changes.csv',i,'old')+' | '+q('abstract_bound_changes.csv',i,'new')+' | '+q('abstract_bound_changes.csv',i,'why')+' |')
    lines+=['', '## Validation and limits', '']
    if VALIDATION.exists():
        v=json.loads(VALIDATION.read_text());lines+=[v['summary'],'', '| Mutant | Bound established | Named failing test |','|---|---|---|']
        for m in v['mutants']:lines.append('| '+m['name']+' | '+m['bound']+' | `'+m['test']+'` |')
        lines+=['',v['attempts'],'',v['resources']]
    else:lines+=['Validation pending; this draft is not a review handoff.']
    lines+=['', 'No new GPU/Mac run, model download or native build was performed. Unmeasured B300 decode/deep prefill, deeper PRO decode, delta-import portability, workload reconstruction/correlations and shared-provider assumptions remain open. Raw/cold LaCie performance and an end-to-end bf16 hybrid at 1M are not established by these measurements. Original R16b and Glimmer/Gemma PRI31 interfaces remain intact. No attack-surface table was supplied (brief gap); new measurements/API cache certification and a proof of minimal fleets are out of contract.']
    return '\n'.join(lines)+'\n',records


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit-only',action='store_true');args=parser.parse_args()
    verify_engine();text,records=build()
    if not args.audit_only:
        REPORT.write_text(text)
        with QUOTES.open('w',newline='')as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');writer.writeheader();writer.writerows(records)
        MANIFEST.write_text(json.dumps(dict(policy_sha256=sha(Path(__file__)),test_sha256=sha(ROOT/'calc/tests/test_r23_report.py'),
            numerical_manifest_sha256=sha(OUT/'r23_manifest.json'),files={str(p.relative_to(ROOT)):sha(p)for p in (REPORT,QUOTES,VALIDATION)if p.exists()}),indent=2,sort_keys=True)+'\n')
    assert REPORT.read_text()==text,'stale or changed report quotation'
    assert list(csv.DictReader(io.StringIO(QUOTES.read_text())))==[{k:str(v)for k,v in r.items()}for r in records],'missing/changed report quote'
    m=json.loads(MANIFEST.read_text())
    assert set(m['files'])=={str(p.relative_to(ROOT))for p in (REPORT,QUOTES,VALIDATION)if p.exists()},'report manifest file set'
    assert m['policy_sha256']==sha(Path(__file__))and m['test_sha256']==sha(ROOT/'calc/tests/test_r23_report.py'),'stale report policy/test'
    assert m['numerical_manifest_sha256']==sha(OUT/'r23_manifest.json'),'changed numerical producer'
    assert all(sha(ROOT/p)==h for p,h in m['files'].items()),'changed report payload'
    print('report quotes',len(records),'exit0')


if __name__=='__main__':main()
