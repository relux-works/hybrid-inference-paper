"""Report-only publication stage; numerical run22 payloads are never rewritten."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'calc'))
from run22.export import OUT,verify as verify_engine

REPORT=ROOT/'calc/ENGINE-REPORT-R22-261103.md'
QUOTES=ROOT/'calc/ENGINE-REPORT-QUOTES-R22-261103.csv'
VALIDATION=ROOT/'calc/R22-VALIDATION-261103.json'
MANIFEST=ROOT/'calc/R22-REPORT-MANIFEST-261103.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    records=[]
    cache={}
    def rows(name):
        if name not in cache:
            cache[name]=list(csv.DictReader(io.StringIO((OUT/name).read_text())))
        return cache[name]
    def match(name,**conditions):
        found=[(index,row)for index,row in enumerate(rows(name)) if all(row.get(k)==str(v)for k,v in conditions.items())]
        assert len(found)==1,(name,conditions,len(found))
        return found[0]
    def value(name,index,column,fmt=None):
        raw=rows(name)[index][column]
        rendered=raw if fmt is None else fmt(float(raw))
        old='<new RC4 quotation>';old_source='';old_row=''
        current=rows(name)[index]
        if name=='link_thresholds.csv' and current.get('depth')=='1000000':
            previous=ROOT/'calc/out/run21/million_link_thresholds.csv'
            for oi,prior in enumerate(csv.DictReader(io.StringIO(previous.read_text()))):
                variant=current['rate_basis'].split(';')[0]
                if all(prior.get(key)==current.get(key) for key in ('server','client','depth','delta','link')) and prior['rate_basis'].startswith(variant) and column in prior:
                    old=prior[column];old_source=str(previous.relative_to(ROOT));old_row=oi;break
        records.append(dict(site='report quotation'+str(len(records)+1),source='calc/out/run22/'+name,row=index,column=column,
            source_value=raw,old=old,old_source=old_source,old_row=old_row,
            comparison='run21 f32 basis to run22 stated transport/rate arm' if old_source else 'new run22 publication',new=rendered))
        return rendered
    money=lambda x:format(x,'.2f')
    pct=lambda x:format(100*x,'.2f')+'%'
    three=lambda x:format(x,'.3f')
    lines=['# Engine run22 — RC4 bounds and accepted measurements', '',
        'Base: `b6316e8a12c47526c9815cc08ebc6de78eec162b`, independently accepted by Muse r5x3. No findings remained. Run22 adopts its generated, humanized short-form advice; the canonical and short quotations share row-bound validators. Runs13–21 and their generators are unchanged.', '',
        'The headline basis is a dedicated team server, bought in the office or rented for 730 calendar hours/month. Shared resident work is a supplementary provider/full-utilization limit. The authors operate a shared prefill service, so its allocation is not the headline. Costs below are the open-model component per person-month, with the stated client/front costs; all alternatives use the same selected call shapes.', '',
        '## bf16 default and measured quality', '',
        'Qwen transports 78,446,592 recurrent bytes by default; 156,893,184 bytes remains the adjacent f32 control. Resident state remains f32: capacity and decode traffic do not halve. Measured f32 Mac import seconds are reused in both transport arms; bf16 import acceleration is not assumed.', '',
        'The accepted KL study gives bf16 minus local −0.000298 nats, 95% interval [−0.001076,+0.000390], against the client’s own 0.054253 nats. The interval contains zero; this is not a universal equivalence claim. The archived paired RULER analyses report:', '',
        '| Arm | Equal paired scores | Changed answers against local |', '|---|---:|---:|']
    for index,row in enumerate(rows('quality_evidence.csv')):
        if row['evidence'].startswith('bf16 RULER'):
            lines.append('| '+row['evidence']+' | '+value('quality_evidence.csv',index,'value')+'/390 | '+value('quality_evidence.csv',index,'answer_changes')+' |')
    lines+=['','The RULER block arrived in FACTS during this run; primary analyses are now source-bound in `calc/run22/data/`. Equality of scores does not mean answer identity or 100% accuracy. These homogeneous CUDA results do not close the heterogeneous vLLM-to-Metal calibration item.', '',
        '## 1M routing: anchored primary value, 120-second sensitivity', '',
        'At 1M, Δ690, B300 FP8 with FP8 KV and the measured historical 5.19 MB/s home Wi-Fi profile:', '',
        '| Transport / local basis | Wire MB | Transfer s | Threshold MB/s | Offload |', '|---|---:|---:|---:|---|']
    for fmt in ('bf16','f32'):
        for variant in ('measured_anchor','analyst'):
            found=[(index,row) for index,row in enumerate(rows('link_thresholds.csv')) if row['model']=='qwen' and row['server']=='b300_fp8_kv' and row['client']=='m3max' and row['depth']=='1000000' and row['transport']==fmt and float(row['bytes_s'])==5190000 and row['rate_basis'].startswith(variant)]
            index,row=found[0]
            lines.append('| '+fmt+' / '+('anchored extension'if variant=='measured_anchor'else'120s estimate')+' | '+value('link_thresholds.csv',index,'wire_bytes',lambda x:format(x/1e6,'.3f'))+' | '+value('link_thresholds.csv',index,'transfer_s',three)+' | '+value('link_thresholds.csv',index,'threshold_MB_s',three)+' | '+value('link_thresholds.csv',index,'offload')+' |')
    lines+=['', 'The primary local delta time is a FLOP-efficiency extension of measured M3 PRI31 anchors, not a direct 1M measurement. The original f32 anchored threshold 5.283 MB/s survives; only transport changes its bf16 counterpart. Both the local 1M rate and the Mac import-depth slope remain estimates. The analyst 120s local turn is separate. PRO6000 default-KV 1M capacity refuses; B300 variants are capacity-checked.', '',
        'All office/WAN/Wi-Fi rows, including 0.798/2.805 MB/s today, 5.19/9.75 MB/s historically and 5.18 MB/s end-to-end slot acquisition, are in `link_thresholds.csv`. The 5.18 MB/s observation included hashing/assembly, not pure wire throughput. Direct restored 1.04M Δ690/2000/10000 observations have their own pending table and CSV interface; they are never renamed measured 1M rates. A slot restore is never substituted for delta import.', '',
        '## Coverage is about call shapes', '',
        '| Profile / selected envelope | Measured-shape calls / source calls | Selected calls / source calls |', '|---|---:|---:|']
    for index,row in enumerate(rows('workload_coverage.csv')):
        lines.append('| '+row['profile']+' / '+row['scope_tier']+' | '+value('workload_coverage.csv',index,'measured_shape_calls')+'/'+value('workload_coverage.csv',index,'source_calls')+' ('+value('workload_coverage.csv',index,'measured_shape_fraction',pct)+') | '+value('workload_coverage.csv',index,'selected_calls')+'/'+row['source_calls']+' ('+value('workload_coverage.csv',index,'selected_fraction',pct)+') |')
    lines+=['', 'Measured coverage means the share of calls whose depth/delta/end shapes lie inside the common measured ladder, normalized to each stated calls/person-month. It is not a share of the total workload or token mass. The combined measured subset retains the same 10,885/39,904 call shapes as R20; the explicit 16k lower bound excludes none of them. Physical-envelope fractions include extrapolated deep rates and must not be called measured coverage. Neither table prices the full unconditioned source mix.', '',
        'The original seeded combined workload is unchanged. The Claude profile remains a quantile/mean reconstruction with conditional mean deltas and independently permuted output/pause ranks, not raw replay. Published Claude pauses are median 8.1 s / p90 60.6 s; the combined p90 is 34.8 s. The active 300 s gap cap and lost correlations remain assumptions.', '',
        '## Dedicated PRO6000 small teams — primary selection', '',
        'Bought office PRO6000 vLLM FP8, 125 MB/s and 1 ms assumed; owned M5 Max 64 GB at recorded PRI31; s=20%; bf16; owner 98.1% cache allowance with 1.9% billed misses. Combined measured-shape subset 10,885/39,904 (27.28%), normalized separately per demanded person-month. Light/medium are typical; heavy 2500 calls/day is the owner’s own intensity.', '',
        '| Load | People | Hybrid $/person-month | Service occupancy | Calendar occupancy | Same-server own cluster $/person-month | Own-cluster service / calendar occupancy |', '|---|---:|---:|---:|---:|---:|---:|']
    common=dict(profile='existing_combined',scope_tier='measured_ladder',transport='bf16',share=.2,client='m5max64',basis='owned',server='pro6000_fp8',billing='bought')
    for load in ('light','medium','heavy'):
        for team in (3,5,10,20):
            index,row=match('small_team_cost.csv',**common,load=load,team=team)
            lines.append('| '+load+' | '+str(team)+' | '+value('small_team_cost.csv',index,'person_month',money)+' | '+value('small_team_cost.csv',index,'service_utilization',pct)+' | '+value('small_team_cost.csv',index,'calendar_utilization',pct)+' | '+value('small_team_cost.csv',index,'own_cluster_person_month',money)+' | '+value('small_team_cost.csv',index,'own_service_utilization',pct)+' / '+value('small_team_cost.csv',index,'own_calendar_utilization',pct)+' |')
    lines+=['', 'Service occupancy divides modelled allocated-GPU work by installed 8h/day GPU time; calendar occupancy uses 730h/month. Decode’s tool/concurrency bound is included, so neither is hardware SM utilization. Hybrid integer fleets are sufficient, not proved minimal. Every dedicated cost row carries utilization, including the own-cluster comparator. Rented nodes pay the full calendar, office nodes the whole bought chassis. Rented hybrid egress uses the retained USD per decimal TB tariff; office egress is zero.', '',
        '## Price of idleness and conditional multiples', '',
        '| Profile / load, team50 | Dedicated cost | Service / calendar occupancy | Median API / dedicated hybrid | Shared-work cost | Median API / shared hybrid |', '|---|---:|---:|---:|---:|---:|']
    for profile in ('existing_combined','claude_deep'):
        for load in ('light','medium','heavy'):
            args=dict(common,profile=profile,load=load,team=50)
            di,dr=match('dedicated_multiples.csv',**args)
            shared=dict(common,profile=profile,load=load,billing='shared_work');si,sr=match('shared_multiples.csv',**shared)
            lines.append('| '+profile+' / '+load+' | '+value('dedicated_multiples.csv',di,'person_month',money)+' | '+value('dedicated_multiples.csv',di,'service_utilization',pct)+' / '+value('dedicated_multiples.csv',di,'calendar_utilization',pct)+' | '+value('dedicated_multiples.csv',di,'api_median_over_hybrid',three)+' | '+value('shared_multiples.csv',si,'person_month',money)+' | '+value('shared_multiples.csv',si,'api_median_over_hybrid',three)+' |')
    lines+=['', 'The dedicated office link is 125 MB/s / 1 ms; the shared provider limit uses engine WAN 112.5 MB/s / 400 ms. `idleness.csv` additionally aligns both sides to the office link and shows the dedicated-minus-shared cost difference against 70%-allocation and 100%-utilization limits. That contrast also changes bought versus rental tariffs, residency, storage and pooled batching: it is not a pure causal measurement of idle cost. Paying the full idle calendar/chassis is explicit. Night agents on autopilot can raise utilization, but their sustained demand is an assumption.', '',
        '## API bounds, no cache verdict', '',
        'Admission excludes context impossibility, no declared cache, or availability below 95% in the chosen common window. Low/zero measured cache hit rates are priced, never excluded. Missing tariff data makes an admitted endpoint unpriceable, not impossible. The exploratory Chutes three-call probe is not an input; series warm-up includes a first miss.', '',
        '| Main measured-shape API point | Cheapest admitted provider | $/1000 calls | Median admitted provider | $/1000 calls |', '|---|---|---:|---|---:|']
    for point in ('no_cache','owner_981'):
        chosen={}
        for role in ('cheapest','median'):
            candidates=[(idx,r)for idx,r in enumerate(rows('api_admission.csv'))if r['profile']=='existing_combined' and r['scope_tier']=='measured_ladder' and r['availability_scenario']=='snapshot_1d' and r['cache_point']==point and r['role']in(role,'cheapest_and_median')]
            chosen[role]=candidates[0]
        a,ar=chosen['cheapest'];b,br=chosen['median']
        lines.append('| '+point+' | '+value('api_admission.csv',a,'provider')+' | '+value('api_admission.csv',a,'effective_usd_per_1000_calls',three)+' | '+value('api_admission.csv',b,'provider')+' | '+value('api_admission.csv',b,'effective_usd_per_1000_calls',three)+' |')
    lines+=['| Measured cache rate | Pending | Pending | Pending | Pending |', '',
        'No-cache means zero cached input tokens; misses use declared cache-write or base-input tariffs, including Alibaba’s explicit write tariff. The 98.1% point is the hash-bound owner commercial aggregate, not a Chutes/provider measurement. API input billing preserves previous generated output at the original call-group boundaries before subsetting. Partial cache observations price individual endpoints but cannot establish the cheapest/median over an incompletely measured cohort.', '',
        'Availability uses the snapshot’s last1d field uniformly, rather than a minimum over 5m/30m/1d. Exact snapshot interval endpoints were not retained. A measured common-window CSV replaces this comparison cohort; no snapshot backfill is mixed into its missing provider observations.', '',
        '| 1M owner 98.1% allowance / availability cohort | Cheapest | $/1000 calls | Median | $/1000 calls |', '|---|---|---:|---|---:|']
    for scenario in ('snapshot_1d','analyst_72h_with_alibaba','analyst_72h_without_alibaba'):
        chosen={}
        for role in ('cheapest','median'):
            chosen[role]=next((idx,r)for idx,r in enumerate(rows('api_admission.csv'))if r['profile']=='million' and r['availability_scenario']==scenario and r['cache_point']=='owner_981' and r['role']in(role,'cheapest_and_median'))
        a,ar=chosen['cheapest'];b,br=chosen['median']
        lines.append('| '+scenario+' | '+value('api_admission.csv',a,'provider')+' | '+value('api_admission.csv',a,'effective_usd_per_1000_calls',three)+' | '+value('api_admission.csv',b,'provider')+' | '+value('api_admission.csv',b,'effective_usd_per_1000_calls',three)+' |')
    lines+=['', 'The fixed 1M API task reserves 690 new and 762 generated tokens inside its advertised 1,000,000 total window, as R21 did; mean billed input is 999,238 tokens. The owner-reported analyst 72h scenario has Phala 86% and Alibaba 96%; other providers and exact endpoints are unverified. Snapshot last1d Alibaba is 87.464%, so the window changes admission. The separate without-Alibaba cohort is an explicit sensitivity, not an additional impossibility rule. Hybrid Qwen uses model-card YaRN factor 4; API extension methods are unknown, and identical YaRN is not claimed. Historical GLM/Ultra projections remain unmeasured; this run does not promote them to new measurements.', '',
        '## Words-ready conclusions', '',
        'The following are generated short forms, with the canonical row in the same table. Own-cluster crossings compare the same server/engine/billing; no claim substitutes an expensive cluster for a cheaper one without naming that basis. All crosses are sustained strict improvements through 500 scanned people, not the first favourable fleet step.', '']
    for billing in ('bought','rented'):
        for load in ('light','medium','heavy'):
            for reference in ('own_cluster','api_median_owner_981','api_cheapest_owner_981'):
                args=dict(common,billing=billing,load=load,reference=reference)
                index,row=match('paper/team_break_even.csv',**args)
                lines.append('- '+value('paper/team_break_even.csv',index,'short_sentence'))
    lines+=['', 'The old “heavy is cheaper at any team size” claim was withdrawn because the own cluster was recalculated on vLLM; under vLLM prices it held only for a 5090 hybrid, which the owner excluded. A second Mac is not the explanation. `heavy_sensitivity.csv` gives one alternative: move generation to the team’s own vLLM server, using its matched own-cluster cost/occupancy bound. Heavy 2500 calls/day is the owner’s intensity; light and medium are typical.', '',
        '## Accepted Mac measurements and resync', '',
        'The new M5 Max 64 GB kit 1.6.7 archives match full SHA256s 1d0d04a372d56ef553565292d12ae10dd58357fad71d53f9f7ccd28e0d44704c and 89211edd6348d026724769bc0de46933f582856b6c36bf33a04d4454b2709f9f. Recorded server samples are PRI31 / nice 0, with no overrides. Readiness arrays contain 35 Qwen and 30 Glimmer samples, versus 36/31 in FACTS; the archived counts govern. M5 Max 128 GB uses the 64 GB same-SoC curves as a labelled portability estimate.', '',
        'Qwen’s measured best batching gains are 2.715/2.024/1.284 at 32768/65536/131072; Glimmer’s 3.236/2.660/2.363 at 32768/65536/129024. Raw depth-specific ladders, 260k Qwen 1/2-stream decode, 129k Glimmer and agent-loop medians/tails are published in `client_measurements.csv`. Agent-loop 8h call counts are projections of those small measured rounds, not a substitute for the economics’ differently shaped workload. Pure parallel decode and agent-loop scheduling are separate protocols. Server decode is measured only at 16384 on the PRO6000; deeper points and the B300 remain modelled until their CSV data arrive.', '',
        '## Accepted PRO 6000 server decode point', '',
        'The accepted kit 1.6.9 observation is at the actual depth of 16,384 tokens, with default KV. Values below are three-round medians of the common decode interval, using private prefixes and salts per session. The measured resident limit is 39 sessions; 40 did not fit. This limit applies at the observed depth. Deeper points remain modelled pending kit 1.6.11; the separate model grid at 16,000 tokens is not relabelled as measured.', '',
        '| Streams | Aggregate tok/s | Gain against one stream |', '|---|---:|---:|']
    for index,row in enumerate(rows('server_decode_measured.csv')):
        lines.append('| '+value('server_decode_measured.csv',index,'streams')+' | '+value('server_decode_measured.csv',index,'aggregate_tok_s',lambda x:format(x,'.2f'))+' | '+value('server_decode_measured.csv',index,'gain',lambda x:format(x,'.2f'))+' |')
    lines+=['', 'The measured point enters through `server_decode.csv`, with its retained receipt and source SHA256. Own-cluster economics use it only where depth and stream count are supported. Continuous workload depths elsewhere retain the bandwidth model; this one anchor does not make the whole cost table measured.', '',
        'M3 Max Glimmer now uses the accepted PRI31 FACTS transcription, including actual successive-turn start offsets; the incident archive is still unavailable on this host. Its rounded values are not claimed archive-verified. SWA reuses the Qwen Mac import-cost fit as an unmeasured portability assumption.', '',
        'The PRO6000 ServerEdition llama.cpp cold fill to 1,040,000 was 518.29+1295.48=1813.77 s (30.2 min), with a measured f32 slot 36,394,654,776 bytes. `full_resync.csv` uses these values. The bf16 full-slot payload is a labelled casting/container estimate; server restore 3.14 s is not Mac import. This does not become a measured vLLM cold rebuild. The M3 Max 1M bandwidth ceiling remains 7.415 tok/s against 1.67 at 1.04M measured at background priority; the gap is open.', '',
        '## Interfaces and limits', '',
        'The provenance CSV carries the accepted PRO 6000 default-KV point at 16,384 tokens. Interfaces remain open for deeper/B300 decode, 512k/1M prefill, provider cache/availability, and restored-slot Mac prefill/import/logits/decode. Empty cells mean pending, never zero. The R16b and Glimmer/Gemma PRI31 JSON interfaces remain unchanged. No 5090 server rows enter paper exports; the historical 5090 client remains supported. The complete commands and CSV contracts are in `calc/run22/README.md`.', '',
        'No new GPU/Mac measurements, downloads or native builds were run. Hardware service rates beyond measured ladders, uniform session retention/miss modelling, deep Mac import, and vLLM decode traffic/efficiency remain assumptions. Physical-extension and shared-provider rows bound applicability rather than establish deployable service offers. No supplied attack-surface table was present (brief gap); out of contract are new measurements, API cache/availability certification and heterogeneous quality calibration.', '',
        '## Validation', '']
    if VALIDATION.exists():
        v=json.loads(VALIDATION.read_text())
        lines += [v['summary'],'', 'Six process-local narrowing faults were killed by named assertion failures; controls passed. Expected-red mutant exits are 1, never labelled green:', '',
            '| Mutant | Gate narrowed to | Named failing test |', '|---|---|---|']
        for r in v['mutants']:
            lines.append('| '+r['name']+' | '+r['bound']+' | `'+r['test']+'` |')
        lines+=['', 'No surviving mutants. Report-only publication adds this report, a coordinate/rendering ledger and a separate manifest; numerical CSV payloads remain the exact exporter output. The main quote ledger covers sentence surfaces and declared quantitative/cost columns; this report ledger additionally covers every quoted API/cost/coverage coordinate. Both are verified against source cells.', '', v['attempts'], '', v['resources']]
    else:
        lines+=['Validation receipts pending; this draft is not a review handoff.']
    return '\n'.join(lines)+'\n',records


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit-only',action='store_true');args=parser.parse_args()
    verify_engine()
    text,records=build()
    if not args.audit_only:
        REPORT.write_text(text)
        with QUOTES.open('w',newline='')as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');writer.writeheader();writer.writerows(records)
        content=dict(policy=str(Path(__file__).relative_to(ROOT)),policy_sha256=sha(Path(__file__)),
            test_sha256=sha(ROOT/'calc/tests/test_r22_report.py'),
            numeric_manifest_sha256=sha(OUT/'r22_manifest.json'),files={str(p.relative_to(ROOT)):sha(p)for p in (REPORT,QUOTES,VALIDATION) if p.exists()})
        MANIFEST.write_text(json.dumps(content,indent=2,sort_keys=True)+'\n')
    assert REPORT.read_text()==text,'stale or changed report quotation'
    assert list(csv.DictReader(io.StringIO(QUOTES.read_text())))==[{k:str(v)for k,v in row.items()}for row in records],'missing/changed report quote'
    manifest=json.loads(MANIFEST.read_text())
    assert manifest['policy_sha256']==sha(Path(__file__)),'stale report policy'
    assert manifest['test_sha256']==sha(ROOT/'calc/tests/test_r22_report.py'),'stale report test'
    assert manifest['numeric_manifest_sha256']==sha(OUT/'r22_manifest.json'),'changed numerical producer'
    assert all(sha(ROOT/name)==digest for name,digest in manifest['files'].items()),'changed report payload'
    print('report quotes',len(records),'exit0')


if __name__=='__main__':main()
